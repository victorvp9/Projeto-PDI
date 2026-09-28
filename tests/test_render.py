import cv2
import numpy as np

from src.config import CFG
from src.geometry import project
from src.pitch_model import CORNERS
from src.render import pitch_mask, render_synthetic

SIZE = (1280, 720)
# perspectiva realista em 1280x720: u = 7X/w + 640, v = 7Y/w + 300, w = 1 - 0,01Y
# (lado distante encolhe ~2x; linha de 0,12 m fica com 0,6 a 1,3 px)
H = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])


def test_synthetic_corner_flags_are_bright():
    gray = cv2.cvtColor(render_synthetic(H, SIZE), cv2.COLOR_BGR2GRAY).astype(float)
    grass = cv2.cvtColor(np.uint8([[CFG["render"]["grass_bgr"]]]), cv2.COLOR_BGR2GRAY)[0, 0]
    uv, ok = project(H, CORNERS)
    assert ok.all()
    for u, v in np.round(uv).astype(int):
        # lado distante é sub-pixel e vira cinza: "bem mais claro que o verde", na vizinhança 3x3
        assert gray[v - 1:v + 2, u - 1:u + 2].max() > grass + 0.25 * (255 - grass), (u, v)
    assert gray[5, 5] == grass   # longe das linhas, verde puro


def test_pitch_mask_ignores_points_behind_camera():
    """Com o horizonte dentro do quadro, o céu não pode virar campo."""
    # u = 7X/w + 640, v = 7Y/w + 500, w = 1 - 0,05Y: o gramado com Y > 20 está atrás
    # da câmera, e seu espelho (w < 0) cairia nas linhas 0-160, ex. (640, 100) <- (0, 30.8)
    H_steep = np.array([[7, -32, 640], [0, -18, 500], [0, -0.05, 1]])
    uv, ok = project(H_steep, np.array([[0, 400 / 13]]))
    assert not ok[0] and np.allclose(uv[0], (640, 100))
    mask = pitch_mask(H_steep, SIZE)
    assert mask[500, 640]          # centro do campo
    assert not mask[:160].any()


def test_lines_mask_keeps_far_lines():
    """Plano aberto (H da WC14 196): longe, o warp da vista de cima pula ~19% do eixo
    das linhas; o lines_mask tem de cobrir o eixo de 1 px inteiro."""
    from src.render import axis_mask, lines_mask
    H_wide = np.array([[24.562785, -8.309995, 659.850943],
                       [-0.087259, -1.599212, 437.83858],
                       [-0.000312, -0.012699, 1.0]])
    axis = axis_mask(H_wide, SIZE)
    assert axis.sum() > 1000
    assert not (axis & ~lines_mask(H_wide, SIZE)).any()
