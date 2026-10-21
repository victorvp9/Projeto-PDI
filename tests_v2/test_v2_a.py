"""v2, A: hipóteses da vista central em forma fechada (assign.central_view_homographies e
central_hypotheses), numa vista sintética da câmera principal."""
import numpy as np

from src_v2.assign import central_hypotheses, central_view_homographies, valid_orientation
from src_v2.camera import compose
from src_v2.conics import conic_ellipse
from src_v2.evaluate import image_grid_displacement
from src_v2.geometry import project

SIZE = (1920, 1080)


def _view(tilt=0.197, pan=0.0):
    """Câmera principal a (0, 50, -10) m, f = 3000 px, olhando para o círculo central."""
    cp, sp, ct, st = np.cos(pan), np.sin(pan), np.cos(tilt), np.sin(tilt)
    R = np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]]) @ np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0.0]]) \
        @ np.array([[cp, -sp, 0], [sp, cp, 0], [0, 0, 1]])
    return compose(3000.0, R, np.array([0.0, 50.0, -10.0]), SIZE)


def _segment(H, XY):
    uv, front = project(H, XY)
    ok = front & (uv[:, 0] >= 0) & (uv[:, 0] < SIZE[0]) & (uv[:, 1] >= 0) & (uv[:, 1] < SIZE[1])
    v = uv[ok]
    return np.r_[v[0], v[-1]]


def _scene(H):
    t = np.linspace(0, 2 * np.pi, 400, endpoint=False)
    E = conic_ellipse(project(H, 9.15 * np.c_[np.cos(t), np.sin(t)])[0])
    mid = _segment(H, np.c_[np.zeros(200), np.linspace(-34, 34, 200)])
    side = _segment(H, np.c_[np.linspace(-30, 30, 200), np.full(200, -34.0)])
    return E, mid, side


def _hline(s):
    return np.cross([*s[:2], 1.0], [*s[2:], 1.0])


def test_closed_form_recovers_the_central_view():
    for pan in (-0.1, 0.0, 0.12):
        H = _view(pan=pan)
        E, mid, side = _scene(H)
        Hs = central_view_homographies(E, _hline(mid), _hline(side), SIZE)
        assert Hs and all(valid_orientation(G, SIZE) for G in Hs)
        assert min(image_grid_displacement(G, H, SIZE) for G in Hs) < 0.5


def test_hypotheses_pick_middle_and_side_lines_among_distractors():
    H = _view()
    E, mid, side = _scene(H)
    distractor = np.array([100.0, 900.0, 300.0, 1000.0])      # reta curta perto do canto, fora do círculo
    Hs = central_hypotheses(np.stack([side, distractor, mid]), [E], SIZE)
    assert Hs and min(image_grid_displacement(G, H, SIZE) for G in Hs) < 0.5


def test_circle_and_middle_line_alone_give_no_hypothesis():
    H = _view()
    E, mid, _ = _scene(H)
    assert central_hypotheses(mid[None], [E], SIZE) == []
