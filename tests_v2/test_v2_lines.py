import cv2
import numpy as np
import pytest

from src_v2.config import CFG
from src_v2.evaluate import STRAIGHT, segment_counts, segment_gt
from src_v2.geometry import project
from src_v2.lines import fuse
from src_v2.pitch_model import POLYLINES
from src_v2.sweep_lines import pick_uniform


def test_pick_uniform_maps_global_index_to_item():
    # sorteando todos os pixels, cada item aparece com todos os seus índices (e o vazio, nenhum)
    counts = [("a", 3), ("b", 0), ("c", 5), ("d", 2)]
    picks = pick_uniform(counts, 10, np.random.default_rng(0))
    assert sorted(picks) == [("a", i) for i in range(3)] + [("c", i) for i in range(5)] + [("d", i) for i in range(2)]


H_IMG = 720
P = {**CFG["lines"], "fuse_theta_deg": 1.0, "fuse_d_frac": 3 / 720, "fuse_gap_frac": 0.1}   # td 3 px, G 72 px


def test_fuse_broken_noisy_line_becomes_one_segment():
    rng = np.random.default_rng(0)
    y = lambda u: 0.2 * u + 100
    pieces = [[u, y(u) + rng.normal(0, 0.3), u + 170, y(u + 170) + rng.normal(0, 0.3)] for u in range(100, 1100, 200)]
    out = fuse(np.array(pieces), P, H_IMG)                     # 5 pedaços, vãos de 30 px
    assert len(out) == 1
    assert sorted([out[0, 0], out[0, 2]]) == pytest.approx([100, 1070], abs=1)
    assert abs(out[0, 1] - y(out[0, 0])) < 1 and abs(out[0, 3] - y(out[0, 2])) < 1


def test_fuse_keeps_close_parallels_and_far_collinears():
    parallel = np.array([[100, 100, 600, 100], [100, 110, 600, 110.0]])     # 10 px > td
    collinear = np.array([[0, 100, 200, 100], [400, 100, 600, 100.0]])      # vão 200 px > G
    assert len(fuse(parallel, P, H_IMG)) == 2
    assert len(fuse(collinear, P, H_IMG)) == 2


def test_fuse_does_not_straighten_an_arc():
    # cordas de 5° de um arco de 60°, com tolerâncias largas o bastante para encadear
    t = np.linspace(0, np.pi / 3, 13)
    p = np.stack([640 + 300 * np.cos(t), 360 + 300 * np.sin(t)], 1)
    Q = {**P, "fuse_theta_deg": 6.0, "fuse_d_frac": 0.02}
    out = fuse(np.hstack([p[:-1], p[1:]]), Q, H_IMG)
    mid = (out[:, :2] + out[:, 2:]) / 2
    assert np.abs(np.hypot(mid[:, 0] - 640, mid[:, 1] - 360) - 300).max() < Q["fuse_d_frac"] * H_IMG


def _true_segments(H, size):
    """Retas do modelo projetadas e recortadas à imagem: segmentos exatos."""
    out = []
    for c in STRAIGHT:
        uv, ok = project(H, POLYLINES[c][[0, -1]])
        if ok.all():
            inside, p1, p2 = cv2.clipLine((0, 0, *size), tuple(np.round(uv[0]).astype(int)), tuple(np.round(uv[1]).astype(int)))
            if inside and np.hypot(p2[0] - p1[0], p2[1] - p1[1]) > 20:
                out.append([*p1, *p2])
    return np.array(out, float)


def test_segment_counts_on_exact_and_shifted_segments():
    # plano aberto do test_render (1280x720)
    H = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])
    size = (1280, 720)
    gt = segment_gt(H, size)
    segs = _true_segments(H, size)
    c, cls = segment_counts(segs, gt, 1.5)
    assert all(cls) and c["len_match"] == pytest.approx(c["len_total"])
    assert c["lines_det"] == c["lines_vis"] > 3 and c["axis_cov"] / c["axis_total"] > 0.99
    assert c["segs_match"] == c["classes_match"]            # um segmento por linha
    d = segs[:, 2:] - segs[:, :2]
    n = np.stack([-d[:, 1], d[:, 0]], 1) / np.hypot(d[:, 0], d[:, 1])[:, None]
    shifted = segs + 10 * np.hstack([n, n])                  # 10 px na normal de cada um
    assert segment_counts(shifted, gt, 1.5)[0]["len_match"] == 0


from src_v2.conics import detect_ellipses, dist_to_ellipse
from src_v2.evaluate import ellipse_gt
from src_v2.lines import detect_segments, shape_filter
from src_v2.render import lines_mask

H_WIDE = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])            # plano aberto do test_render, 1280x720
H_BROADCAST = np.array([[90.993262, -18.046952, 1006.07514],                 # H_gt do SNGS-070/101, 1920x1080
                        [-0.342962, 4.600815, 752.869136], [-0.000443, -0.018014, 1.0]])
# a máscara sintética é uma rede de linhas toda conexa, que o filtro de forma apagaria (docs/decisoes.md)
NO_FILTER = {**CFG["lines"], "shape_filter": False}


def _angle(d1, d2):
    return np.degrees(np.arccos(min(1.0, abs(d1 @ d2) / np.linalg.norm(d1) / np.linalg.norm(d2))))


def test_shape_filter_drops_blob_keeps_line():
    m = np.zeros((720, 1280), np.uint8)
    m[100:104, 100:600] = 1                                   # linha de 4 px
    cv2.circle(m, (900, 400), 15, 1, -1)                      # mancha compacta
    out = shape_filter(m.astype(bool), CFG["lines"])
    assert out[100:104, 100:600].all() and not out[385:416, 885:916].any()


def test_segments_wide_view_recover_each_line_once():
    # Etapa 3 sozinha: sem a remoção de cordas, que hoje pode levar uma reta junto com
    # uma elipse falsa (docs/decisoes.md); o círculo é pequeno demais para dar cordas
    size = (1280, 720)
    segs = detect_segments(lines_mask(H_WIDE, size), NO_FILTER)
    gt = segment_gt(H_WIDE, size)
    c, cls = segment_counts(segs, gt, 1.0)
    assert all(cls)                                           # nenhum segmento a mais
    assert c["segs_match"] == c["classes_match"]              # um segmento por linha
    long_lines = {k for k, g in gt[0].items() if len(g["axis"]) >= 2 * CFG["lines"]["hough_min_len_frac"] * size[1]}
    assert long_lines and long_lines <= set(cls)              # toda linha visível longa sai
    for s, k in zip(segs, cls):
        (a, b), _ = project(H_WIDE, POLYLINES[k][[0, -1]])
        assert _angle(s[2:] - s[:2], b - a) <= 1.0, k         # medido: <= 0,74° (segmento curto ao longe)


@pytest.mark.parametrize("H, size", [(H_WIDE, (1280, 720)), (H_BROADCAST, (1920, 1080))])
def test_pipeline_finds_the_center_circle(H, size):
    # o círculo central sai entre as elipses; hoje também sai uma segunda, falsa (docs/decisoes.md)
    marks = lines_mask(H, size)
    ells = detect_ellipses(marks, NO_FILTER, lines=detect_segments(marks, NO_FILTER))
    g = ellipse_gt(H, size)["Circle central"]
    p = np.round(g["pts"]).astype(int)
    best = min(np.median(dist_to_ellipse(E, marks.shape)[p[:, 1], p[:, 0]]) for E in ells)
    assert best <= CFG["lines"]["tol_frac"] * size[1]        # a tolerância de casamento; medido: 0 e 4 px
