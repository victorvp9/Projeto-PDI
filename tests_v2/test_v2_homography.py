import numpy as np

from src_v2.evaluate import image_grid_displacement
from src_v2.geometry import project
from src_v2.homography import fit_point_line
from src_v2.pitch_model import POLYLINES

SIZE = (1920, 1080)
# perspectiva realista em 1920x1080: u = 14X/w + 960, v = 14Y/w + 450, w = 1 - 0,01Y
H_TRUE = np.array([[14, -9.6, 960], [0, 9.5, 450], [0, -0.01, 1.0]])
# início perturbado: campo deslocado 1,5 m e girado 1 grau (~30-60 px na imagem)
_c, _s = np.cos(np.radians(1)), np.sin(np.radians(1))
H0 = H_TRUE @ np.array([[_c, -_s, 1.5], [_s, _c, -0.8], [0, 0, 1]])


def _annotate(H, classes, rng, every=6):
    """Pontos (imagem, px) sobre as polilinhas projetadas, só os dentro do quadro."""
    out = {}
    for k in classes:
        uv, ok = project(H, POLYLINES[k][::every])
        uv = uv[ok & (uv[:, 0] > 5) & (uv[:, 0] < SIZE[0] - 5) & (uv[:, 1] > 5) & (uv[:, 1] < SIZE[1] - 5)]
        if len(uv):
            out[k] = uv
    return out


def test_recovers_h_from_noisy_points_with_outliers():
    rng = np.random.default_rng(0)
    classes = [k for k in POLYLINES if not k.startswith("Side line bottom")]
    lines = _annotate(H_TRUE, classes, rng)
    for k in lines:
        lines[k] = lines[k] + rng.normal(0, 1.0, lines[k].shape)          # ruído de clique, 1 px
        bad = rng.random(len(lines[k])) < 0.10
        lines[k][bad] += rng.choice([-50, 50], size=(bad.sum(), 2))        # 10% de pontos ruins
    lines["Small rect. left main"] = lines.pop("Big rect. left main")      # uma classe trocada
    assert image_grid_displacement(H_TRUE, H0, SIZE) > 20                  # começa longe
    fit = fit_point_line(H0, lines, SIZE)
    assert fit.ok and fit.rank == 8
    # soft_l1 limita, mas não zera, a influência dos outliers: viés medido de 0,88 px
    # (média de 5 sementes) e 1,15 px nesta semente; o limite acompanha a perda escolhida
    assert image_grid_displacement(H_TRUE, fit.H, SIZE) < 1.5


def test_parallel_lines_only_is_rejected():
    lines = _annotate(H_TRUE, ["Side line top", "Big rect. left top"], None)
    fit = fit_point_line(H0, lines, SIZE)
    assert not fit.ok and fit.rank < 8


def test_too_few_points_is_not_tried():
    fit = fit_point_line(H0, {"Side line top": np.array([[100.0, 200], [300, 210]])}, SIZE)
    assert fit.H is None and not fit.ok
