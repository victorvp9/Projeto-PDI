import cv2
import numpy as np

from src.config import CFG
from src.evaluate import coverage_precision, lines_target, shadow_score
from src.render import lines_mask, render_synthetic
from src.segment import grass_mask, line_mask, params

SIZE = (1920, 1080)
# plano mais fechado, centro do campo: linhas de 0,12 m com 2,7 a 5,5 px
H_ZOOM = np.array([[30, -9.6, 960], [0, 24.6, 540], [0, -0.01, 1.0]])
P = {**params("gsr"), "width_ab": [3.5 / 1080, 0.0]}     # largura ~ a do H_ZOOM


def _shadow(img, frac=0.6):
    """Escurece a metade esquerda (V x frac): sombra atravessando o campo."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, : img.shape[1] // 2, 2] *= frac
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def test_grass_on_synthetic_with_and_without_shadow():
    img = render_synthetic(H_ZOOM, SIZE)
    full = np.ones(img.shape[:2], bool)
    for method in ("hsv", "lab_hue"):
        Q = {**P, "grass_method": method}
        assert (grass_mask(img, Q) & full).mean() >= 0.99, method
        # meia sombra: o "maior componente" não pode descartar a metade escura
        assert grass_mask(_shadow(img), Q).mean() >= 0.95, method


def test_lines_on_synthetic():
    img = render_synthetic(H_ZOOM, SIZE)
    target = lines_target(H_ZOOM, SIZE)
    for method in ("tophat", "filter"):
        Q = {**P, "line_method": method}
        pred = line_mask(img, np.ones(img.shape[:2], bool), Q)
        s = coverage_precision(pred, target, [1, 3], width_target=lines_mask(H_ZOOM, SIZE))
        assert s["cobertura@1"] >= 0.90 and s["precisao@3"] >= 0.95, (method, s)


def _texture(img, rng, sigma=6):
    """Textura de grama: ruído gaussiano em L; o sintético uniforme deixaria o Otsu
    separar a grama da franja suavizada das linhas."""
    return np.clip(img.astype(float) + rng.normal(0, sigma, img.shape[:2])[..., None], 0, 255).astype(np.uint8)


def test_shadow_score_separates_shadow_from_stripes():
    rng = np.random.default_rng(0)
    img = render_synthetic(H_ZOOM, SIZE)
    region = np.ones(img.shape[:2], bool)
    dl_flat, _, _ = shadow_score(_texture(img, rng), region)
    dl_sh, f_sh, w_sh = shadow_score(_texture(_shadow(img), rng), region)
    stripes = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    for i in range(0, SIZE[0], 2 * SIZE[0] // 24):              # 12 faixas de corte mais escuras
        stripes[:, i:i + SIZE[0] // 24, 2] *= 0.85
    dl_st, f_st, _ = shadow_score(_texture(cv2.cvtColor(stripes.astype(np.uint8), cv2.COLOR_HSV2BGR), rng), region)
    assert dl_flat < 15                         # textura sozinha: Otsu corta a unimodal no meio (~1,6 sigma)
    assert dl_sh > 2 * dl_st and f_sh >= 0.4    # meia sombra: região grande e bem mais escura
    assert w_sh >= CFG["shadow"]["f_light_min"]  # ... e um pedaço contínuo de sol
    assert f_st < CFG["shadow"]["f_dark_min"]   # faixas: bandas estreitas
