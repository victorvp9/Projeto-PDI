import numpy as np

from src.config import CFG
from src.pitch_model import CORNERS, HL, HW, POLYLINES


def test_corner_flags():
    """Pega inversão de eixo: bandeirinhas em (±52.5, ±34)."""
    assert sorted(map(tuple, CORNERS)) == sorted((x, y) for x in (-52.5, 52.5) for y in (-34, 34))
    ends = {tuple(np.round(p[i], 9)) for k, p in POLYLINES.items() if k.startswith("Side line") for i in (0, -1)}
    assert ends == set(map(tuple, CORNERS))


def test_side_names_follow_axes():
    assert np.allclose(POLYLINES["Side line top"][:, 1], -HW)       # top = lado oposto à câmera
    assert np.allclose(POLYLINES["Side line left"][:, 0], -HL)
    assert (POLYLINES["Circle left"][:, 0] >= -36 - 1e-9).all()     # arco fora da grande área
    assert (POLYLINES["Circle right"][:, 0] <= 36 + 1e-9).all()


def test_polylines_dense_and_inside_pitch():
    step = CFG["pitch"]["sample_step_m"]
    assert len(POLYLINES) == 20
    for name, p in POLYLINES.items():
        assert len(p) > 2, name   # inclusive retas: 2 pontos quebram a projeção
        assert np.linalg.norm(np.diff(p, axis=0), axis=1).max() <= step + 1e-9, name
        assert (np.abs(p) <= [HL + 1e-9, HW + 1e-9]).all(), name
