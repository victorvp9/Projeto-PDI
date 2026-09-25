import dataclasses
import json

import numpy as np
import pytest

from src.config import CFG, path
from src.evaluate import image_grid_displacement
from src.homography import class_distances, fit_point_line
from src.io import gsr
from src.pitch_model import POLYLINES

CLIP = path("gsr") / "train" / "SNGS-070"
H_TRUE = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])  # campo -> imagem, 1280x720


def _person(u, v, w, cat=1):
    """Pessoa cuja base (u..u+w, v) na imagem é a projeção exata do bbox_pitch por H_TRUE."""
    base = np.array([[u, v, 1], [u + w / 2, v, 1], [u + w, v, 1]]) @ np.linalg.inv(H_TRUE).T
    XY = base[:, :2] / base[:, 2:]
    pitch = {f"{a}_{k}": XY[i, j] for i, k in enumerate(("bottom_left", "bottom_middle", "bottom_right"))
             for j, a in enumerate("xy")}
    return {"category_id": cat, "bbox_image": {"x": u, "y": v - 60, "w": w, "h": 60}, "bbox_pitch": pitch}


def _norm(H):
    return H / H[2, 2]


ANNS = [_person(100, 200, 20), _person(900, 250, 25), _person(400, 600, 40), _person(1100, 650, 45)]


def test_dlt_recovers_h():
    assert np.allclose(_norm(gsr.estimate_h_persons(ANNS)), H_TRUE, atol=1e-6)


def test_ball_and_null_pitch_ignored():
    ball = _person(500, 400, 10, cat=4)
    ball["bbox_pitch"] = {k: 1e3 for k in ball["bbox_pitch"]}  # bola "no ar", absurda
    null = _person(700, 300, 20) | {"bbox_pitch": None}
    H = gsr.estimate_h_persons(ANNS + [ball, null])
    assert np.array_equal(H, gsr.estimate_h_persons(ANNS))


def test_too_few_persons():
    assert gsr.estimate_h_persons(ANNS[:3]) is None


needs_clip = pytest.mark.skipif(not CLIP.exists(), reason="SNGS-070 ausente em data/")


@needs_clip
def test_polylines_cover_gsr_plane_classes():
    d = json.loads((CLIP / "Labels-GameState.json").read_text(encoding="utf-8"))
    names = next(c["lines"] for c in d["categories"] if c["name"] == "pitch")
    assert set(POLYLINES) == {n for n in names if not n.startswith("Goal")}


def _persons_err(s):
    """Erro contra as linhas da H pelas pessoas (definição da Fatia 1)."""
    d = class_distances(s.H_persons, gsr.inner_points(s.lines_uv, s.size))
    return float(np.median(np.concatenate(list(d.values())))) if d else np.nan


FATIA1_DUBIOUS_PX = 10   # limiar de "duvidoso" da definição da Fatia 1 (docs/decisoes.md)
MIN_CLASS_POINTS = 3     # classe deixada de fora precisa de pontos para medir o erro nela


@needs_clip
def test_sngs070_persons_reference_values():
    """H pelas pessoas contra as linhas: valores da Fatia 1 em docs/decisoes.md.
    Confere o mapeamento de classes e a leitura do JSON."""
    samples = gsr.load_clip(CLIP, fit="none")
    assert len(samples) == 750 and all(s.H_persons is not None for s in samples)
    err = np.array([_persons_err(s) for s in samples])
    assert abs(np.median(err) - 2.8) <= 0.3
    bad = {s.frame_idx for s, e in zip(samples, err) if e > FATIA1_DUBIOUS_PX}
    assert 5 <= len(bad) <= 10 and set(range(354, 360)) <= bad, sorted(bad)
    assert np.median(err[err <= FATIA1_DUBIOUS_PX]) <= 5


@needs_clip
def test_sngs070_leave_one_class_out():
    """Em 1 frame a cada 10, para cada classe com pontos suficientes: ajuste pelas
    linhas SEM ela (partindo da H pelas pessoas) e erro NELA, contra o erro da H
    pelas pessoas na mesma classe. O ajuste tem de prever melhor a classe que não viu.
    A discordância linhas x pessoas na grade da imagem é só reportada (lado da câmera)."""
    held_fit, held_persons, dis = [], [], []
    for s in gsr.load_clip(CLIP, fit="none")[::10]:
        pts = gsr.inner_points(s.lines_uv, s.size)
        full = fit_point_line(s.H_persons, pts, s.size)
        if full.ok:
            dis.append(image_grid_displacement(full.H, s.H_persons, s.size))
        for k in [k for k, p in pts.items() if len(p) >= MIN_CLASS_POINTS]:
            fit = fit_point_line(s.H_persons, {c: p for c, p in pts.items() if c != k}, s.size)
            if fit.ok:
                held_fit.append(np.median(class_distances(fit.H, {k: pts[k]})[k]))
                held_persons.append(np.median(class_distances(s.H_persons, {k: pts[k]})[k]))
    print(f"\nSNGS-070, classe deixada de fora ({len(held_fit)} casos): mediana do erro nela "
          f"{np.median(held_fit):.2f} px pelo ajuste sem ela x {np.median(held_persons):.2f} px pelas pessoas")
    print(f"SNGS-070, discordância linhas x pessoas na grade: mediana {np.median(dis):.2f} px (reportada)")
    assert len(held_fit) >= 50 and np.median(held_fit) < np.median(held_persons)


@needs_clip
def test_chaining_recovers_fit_without_persons():
    """Sem as pessoas em 100-200, o encadeamento a partir do vizinho chega à mesma H."""
    samples = gsr.load_clip(CLIP, fit="none")[89:211]
    direct = gsr.fit_clip(samples)
    blind = [dataclasses.replace(s, H_persons=None) if 100 <= s.frame_idx <= 200 else s for s in samples]
    chained = gsr.fit_clip(blind)
    gap = [image_grid_displacement(a.H, b.H, s.size)
           for a, b, s in zip(direct, chained, samples) if 100 <= s.frame_idx <= 200]
    assert all(b.ok for b in chained) and max(gap) < 1.0, max(gap)


@pytest.mark.skipif(not (path("gsr") / "valid" / "SNGS-023").exists(), reason="SNGS-023 ausente em data/")
def test_sngs023_f230_fit_puts_center_circle_on_painted():
    """A H pelas pessoas põe o círculo central ~660 px longe do pintado/anotado; o
    ajuste pelas linhas o traz para cima dele (overlay em outputs/debug/)."""
    s = next(x for x in gsr.load_clip(path("gsr") / "valid" / "SNGS-023", fit="none") if x.frame_idx == 230)
    pts = gsr.inner_points(s.lines_uv, s.size)
    before = np.median(class_distances(s.H_persons, pts)["Circle central"])
    fit = fit_point_line(s.H_persons, pts, s.size)
    after = np.median(class_distances(fit.H, pts)["Circle central"])
    print(f"\nSNGS-023 f230, Circle central: {before:.0f} px pelas pessoas -> {after:.1f} px pelo ajuste")
    assert before > 100 and fit.ok and after <= 10


def test_label_fixes_whole_clip_and_range():
    assert gsr.fixed_label("SNGS-149", 5, "Circle right") == "Circle central"
    assert gsr.fixed_label("SNGS-149", 600, "Circle right") == "Circle right"    # arco verdadeiro em 583-750
    assert gsr.fixed_label("SNGS-070", 5, "Circle right") == "Circle right"      # clipe sem correção
    assert gsr.fixed_label("SNGS-149", 5, "Middle line") == "Middle line"        # classe sem correção
    assert gsr.fixed_label("SNGS-133", 100, "Big rect. right main") == "Big rect. right main"  # antes do trecho
    assert gsr.fixed_label("SNGS-133", 300, "Big rect. right main") == "Big rect. left main"
    assert gsr.fixed_label("SNGS-153", 500, "Middle line") is None                # congelada: descartada
    assert gsr.fixed_label("SNGS-153", 400, "Middle line") == "Middle line"


@pytest.mark.skipif(not (path("gsr") / "test" / "SNGS-149").exists(), reason="SNGS-149 ausente em data/")
def test_sngs149_circle_label_fixed():
    """Círculo central anotado como `Circle right` em 1-582; corrigido na leitura. Em
    583-750 o `Circle right` é o arco da grande área direita (docs/decisoes.md)."""
    samples = gsr.load_clip(path("gsr") / "test" / "SNGS-149", fit="none")
    assert not any("Circle right" in s.lines_uv for s in samples if s.frame_idx <= 582)
    assert all("Circle central" not in s.lines_uv for s in samples if s.frame_idx >= 583)
    assert np.nanmedian([_persons_err(s) for s in samples]) < FATIA1_DUBIOUS_PX  # era 1.815 px
