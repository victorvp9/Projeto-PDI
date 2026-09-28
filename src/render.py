"""Imagem sintética, máscara do campo projetado e overlay de depuração.

Imagem sintética e máscara saem de uma vista de cima do modelo deformada por
`warpPerspective`: a espessura das linhas fica correta em perspectiva e um canto
atrás da câmera não inverte o polígono (docs/03-plano.md, Fatia 1).
"""
import cv2
import numpy as np

from src.config import CFG
from src.geometry import project_segments
from src.pitch_model import CORNERS, HL, HW, LINE_WIDTH, POLYLINES

R = CFG["render"]
PPM, MARGIN = R["px_per_m"], R["margin_m"]
# campo (m) -> pixel da vista de cima
T = np.array([[PPM, 0, (HL + MARGIN) * PPM], [0, PPM, (HW + MARGIN) * PPM], [0, 0, 1.0]])
TOP_SIZE = (int(round(2 * (HL + MARGIN) * PPM)) + 1, int(round(2 * (HW + MARGIN) * PPM)) + 1)


def _to_top(XY):
    """Campo (m) -> pixel inteiro da vista de cima."""
    return np.round(XY @ T[:2, :2].T + T[:2, 2]).astype(np.int32)


def _in_front(H, size):
    """Máscara (imagem) dos pixels cujo raio encontra o gramado à frente da câmera."""
    w, h = size
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    p = np.linalg.inv(H)[2]
    return (p[0] * u + p[1] * v + p[2]) * np.sign(H[2, 2]) > 0


def _warp(top, H, size, flags, border):
    """Vista de cima -> imagem de tamanho `size` (w, h), com H campo -> imagem."""
    out = cv2.warpPerspective(top, H @ np.linalg.inv(T), size, flags=flags,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=border)
    out[~_in_front(H, size)] = border
    return out


def pitch_mask(H, size):
    """Máscara bool (imagem) da área do campo 105 x 68 m projetada por H."""
    top = np.zeros(TOP_SIZE[::-1], np.uint8)
    cv2.fillPoly(top, [_to_top(CORNERS)], 1)
    return _warp(top, H, size, cv2.INTER_NEAREST, 0).astype(bool)


def axis_mask(H, size):
    """Máscara bool (imagem) das polilinhas do modelo projetadas por H com 1 px."""
    w, h = size
    t = np.zeros((h, w), np.uint8)
    for poly in POLYLINES.values():
        segs = np.clip(project_segments(H, poly), -1e6, 1e6).astype(np.int32)
        cv2.polylines(t, list(segs), False, 1, 1)
    return t.astype(bool)


def lines_mask(H, size):
    """Máscara bool (imagem) das marcações com a largura projetada de 0,12 m: pixel
    tocado por qualquer fração de linha. Perto, a vista de cima deformada por H dá a
    largura; longe, um pixel da imagem cobre vários da vista de cima e o warp pula a
    linha (3,5% do eixo no WC14 train_val, até 20% num frame; docs/decisoes.md), e o
    eixo de 1 px projetado direto garante o pixel tocado."""
    top = np.zeros(TOP_SIZE[::-1], np.uint8)
    for poly in POLYLINES.values():
        cv2.polylines(top, [_to_top(poly)], False, 255, int(round(LINE_WIDTH * PPM)))
    return (_warp(top, H, size, cv2.INTER_LINEAR, 0) > 0) | axis_mask(H, size)


def render_synthetic(H, size):
    """Imagem BGR sintética (w, h): gramado uniforme e marcações de 0,12 m, vistas por H.

    Renderiza `supersample` vezes maior e reduz por média de área, para que linhas
    mais finas que um pixel fiquem cinza em vez de sumirem na amostragem.
    """
    grass, line = tuple(R["grass_bgr"]), tuple(R["line_bgr"])
    top = np.full((*TOP_SIZE[::-1], 3), grass, np.uint8)
    thick = int(round(LINE_WIDTH * PPM))
    for poly in POLYLINES.values():
        cv2.polylines(top, [_to_top(poly)], False, line, thick)
    k = R["supersample"]
    S = np.array([[k, 0, (k - 1) / 2], [0, k, (k - 1) / 2], [0, 0, 1.0]])  # centros de pixel alinhados
    big = _warp(top, S @ H, (size[0] * k, size[1] * k), cv2.INTER_LINEAR, grass)
    return cv2.resize(big, size, interpolation=cv2.INTER_AREA)


def draw_overlay(image, H, lines_uv=None):
    """Desenha sobre o frame (imagem, BGR) o modelo projetado por H e, se dados,
    os pontos das linhas anotadas (imagem, px)."""
    O = CFG["overlay"]
    out = image.copy()
    for poly in POLYLINES.values():
        # ponytail: pontos quase no horizonte explodem; corta em ±1e6 px para caber em int32
        segs = np.clip(project_segments(H, poly), -1e6, 1e6).astype(np.int32)
        cv2.polylines(out, list(segs), False, tuple(O["model_bgr"]), O["thickness_px"], cv2.LINE_AA)
    for pts in (lines_uv or {}).values():
        for u, v in np.round(pts).astype(int):
            cv2.circle(out, (u, v), 2 * O["thickness_px"], tuple(O["annotated_bgr"]), -1, cv2.LINE_AA)
    return out
