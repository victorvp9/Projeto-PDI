"""v2, C (docs/decisoes.md, 2026-10-15): fusão das propagações direta e reversa entre âncoras."""
from types import SimpleNamespace

import numpy as np

from src_v2 import temporal as T
from src_v2.evaluate import FIELD_GRID

H0 = np.array([[12.0, 2.0, 960.0], [0.5, -6.0, 700.0], [0.0, 0.004, 1.0]])   # campo -> imagem, câmera de frente
SIZE = (1920, 1080)


def _shift(H, du):
    return np.array([[1, 0, du], [0, 1, 0], [0, 0, 1.0]]) @ H


def test_dlt_normalized_recovers_the_homography():
    from src_v2.geometry import project
    uv, ok = project(H0, FIELD_GRID)
    H = T.dlt_normalized(FIELD_GRID[ok], uv[ok])
    assert np.allclose(H, H0 / H0[2, 2], atol=1e-6)


def test_fuse_weights_and_disagreement():
    Hb = _shift(H0, 20.0)
    for wa, du in ((1.0, 0.0), (0.0, 20.0), (0.5, 10.0)):
        H, d = T.fuse(H0, Hb, wa, SIZE)
        assert np.allclose(H, _shift(H0, du) / H0[2, 2], atol=1e-6)
        assert np.isclose(d, 20.0 / SIZE[1])
    H, d = T.fuse(H0, H0, 0.3, SIZE)
    assert np.allclose(H, H0 / H0[2, 2], atol=1e-6) and d == 0.0


def test_fill_between_anchors_uses_both_sides(monkeypatch):
    """Entre as âncoras 0 e 10, a de 0 propaga H0 e a de 10, H0 deslocada de 30 px: o frame t fica
    com o deslocamento 30·t/10; nas pontas (depois da última âncora), só a propagação dela."""
    monkeypatch.setitem(T.T, "bidirectional", True)
    monkeypatch.setattr(T, "propagate", lambda cf, a, H, stop, step, lines=True, dbg=None: {u: H for u in range(a + step, stop, step)})
    H_anchor = np.full((15, 3, 3), np.nan)
    H_anchor[0], H_anchor[10] = H0, _shift(H0, 30.0)
    diag = {}
    Hs = T.fill_from_anchors(SimpleNamespace(size=SIZE), [0, 10], H_anchor, np.zeros(15, int), "flow", diag=diag)
    for t in range(1, 10):
        assert np.allclose(Hs[t], _shift(H0, 3.0 * t) / H0[2, 2], atol=1e-6)
        assert np.isclose(diag[t], 30.0 / SIZE[1])
    assert np.allclose(Hs[12], H_anchor[10]) and 12 not in diag
