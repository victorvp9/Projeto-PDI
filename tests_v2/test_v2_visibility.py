import numpy as np

from src_v2.visibility import GRID, fov_polygon, frame_visibility

SIZE = (1280, 720)


def _top(scale=20.0, X0=0.0):
    """Vista de cima (campo -> imagem): `scale` px/m, o ponto (X0, 0) no centro da imagem."""
    return np.array([[scale, 0, SIZE[0] / 2 - scale * X0], [0, scale, SIZE[1] / 2], [0, 0, 1.0]])


def test_top_view_fov_is_the_image_rectangle():
    p = fov_polygon(_top(), SIZE)                      # 1280 x 720 px a 20 px/m = 64 x 36 m
    assert np.isclose(p.area, 64 * 36)
    assert np.allclose(p.bounds, (-32, -18, 32, 18))


def test_fov_is_clipped_at_the_horizon():
    """Vista inclinada com o horizonte dentro da imagem: o polígono é finito (recortado no
    campo mais a margem) e não inclui o que está atrás da câmera."""
    H = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.03, 1]])     # horizonte em v ~ 133 px
    p = fov_polygon(H, SIZE)
    assert 0 < p.area < np.inf and not p.is_empty
    assert p.bounds[1] > -34 - 5 - 1e-6                          # dentro do campo mais 5 m


def test_inversion_counts():
    players = [[0, 0], [20, 5], [40, 0]]                           # só o último fica fora da vista de 64 m
    same = frame_visibility(_top(), _top(), SIZE, players)
    assert same["vis_gt"] == 2 and same["sai"] == same["entra"] == same["grade_diff"] == 0
    shifted = frame_visibility(_top(X0=10), _top(), SIZE, players)  # estimativa 10 m à direita
    assert shifted["sai"] == 0 and shifted["entra"] == 1           # (40, 0) passa a "visível"
    X, Y = GRID[:, 0], GRID[:, 1]                                 # contains: a borda fica de fora
    in_gt = (np.abs(X) < 32) & (np.abs(Y) < 18)
    in_est = (np.abs(X - 10) < 32) & (np.abs(Y) < 18)
    assert shifted["grade_diff"] == int((in_gt != in_est).sum())
    missing = frame_visibility(None, _top(), SIZE, players)       # sem H: penalizada
    assert missing["sai"] == missing["vis_gt"] == 2 and missing["vis_est"] == 0
