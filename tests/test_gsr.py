import json

import numpy as np
import pytest

from src.config import CFG, path
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
    assert np.allclose(_norm(gsr.estimate_h_gt(ANNS)), H_TRUE, atol=1e-6)


def test_ball_and_null_pitch_ignored():
    ball = _person(500, 400, 10, cat=4)
    ball["bbox_pitch"] = {k: 1e3 for k in ball["bbox_pitch"]}  # bola "no ar", absurda
    null = _person(700, 300, 20) | {"bbox_pitch": None}
    H = gsr.estimate_h_gt(ANNS + [ball, null])
    assert np.array_equal(H, gsr.estimate_h_gt(ANNS))


def test_too_few_persons():
    assert gsr.estimate_h_gt(ANNS[:3]) is None


needs_clip = pytest.mark.skipif(not CLIP.exists(), reason="SNGS-070 ausente em data/")


@needs_clip
def test_polylines_cover_gsr_plane_classes():
    d = json.loads((CLIP / "Labels-GameState.json").read_text(encoding="utf-8"))
    names = next(c["lines"] for c in d["categories"] if c["name"] == "pitch")
    assert set(POLYLINES) == {n for n in names if not n.startswith("Goal")}


@needs_clip
def test_sngs070_reference_values():
    """Valores de referência de docs/decisoes.md (frames numerados pelo arquivo)."""
    samples = gsr.load_clip(CLIP)
    assert len(samples) == 750 and all(s.H_gt is not None for s in samples)
    err = np.array([s.line_err for s in samples])
    assert abs(np.median(err) - 2.8) <= 0.3
    assert np.median([s.line_err for s in samples if not s.dubious]) <= 5
    dubious = {s.frame_idx for s in samples if s.dubious}
    assert 5 <= len(dubious) <= 10, sorted(dubious)
    assert set(range(354, 360)) <= dubious, sorted(dubious)
    assert CFG["gsr"]["dubious_median_px"] == 10


def test_label_fixes_whole_clip_and_range():
    assert gsr.fixed_label("SNGS-149", 5, "Circle right") == "Circle central"
    assert gsr.fixed_label("SNGS-070", 5, "Circle right") == "Circle right"      # clipe sem correção
    assert gsr.fixed_label("SNGS-149", 5, "Middle line") == "Middle line"        # classe sem correção
    assert gsr.fixed_label("SNGS-133", 100, "Big rect. right main") == "Big rect. right main"  # antes do trecho
    assert gsr.fixed_label("SNGS-133", 300, "Big rect. right main") == "Big rect. left main"


@pytest.mark.skipif(not (path("gsr") / "test" / "SNGS-149").exists(), reason="SNGS-149 ausente em data/")
def test_sngs149_circle_label_fixed():
    """Círculo central anotado como `Circle right`; corrigido na leitura (docs/decisoes.md)."""
    samples = gsr.load_clip(path("gsr") / "test" / "SNGS-149")
    assert not any("Circle right" in s.lines_uv for s in samples)
    assert np.nanmedian([s.line_err for s in samples]) < CFG["gsr"]["dubious_median_px"]  # era 1.815 px
