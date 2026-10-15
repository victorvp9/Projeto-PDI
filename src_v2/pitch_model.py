"""Modelo do campo, no espaço *campo*: metros, origem no centro do gramado, X ao
longo do comprimento, Y positivo em direção à câmera principal.

Valores das Regras do Jogo (IFAB, Lei 1). Os nomes das polilinhas são os do
SN-Calib, usados também pelo SoccerNet-GSR: `left` = X < 0, `top` = Y < 0 (lado
oposto à câmera), `main` = a linha paralela à linha de fundo, `Side line
left/right` = linhas de fundo, `Circle left/right` = arco da grande área, só a
parte fora dela. Traves e travessão (`Goal …`) ficam fora: não estão no plano.
"""
import numpy as np

from src_v2.config import CFG

LENGTH = 105.0              # comprimento
WIDTH = 68.0                # largura
LINE_WIDTH = 0.12           # largura máxima das marcações
CENTER_CIRCLE_R = 9.15
PENALTY_AREA_DEPTH = 16.5
PENALTY_AREA_WIDTH = 40.32
GOAL_AREA_DEPTH = 5.5
GOAL_AREA_WIDTH = 18.32
PENALTY_MARK_DIST = 11.0    # da linha de fundo
PENALTY_ARC_R = 9.15

HL, HW = LENGTH / 2, WIDTH / 2
CORNERS = np.array([[-HL, -HW], [HL, -HW], [HL, HW], [-HL, HW]])  # bandeirinhas


def _segment(p, q, step):
    """Reta de p a q (campo, m) amostrada com passo <= step."""
    n = int(np.ceil(np.hypot(q[0] - p[0], q[1] - p[1]) / step)) + 1
    return np.linspace(p, q, n)


def _arc(center, r, t0, t1, step):
    """Arco de círculo (campo, m) de t0 a t1 rad, amostrado com passo <= step."""
    t = np.linspace(t0, t1, int(np.ceil(r * abs(t1 - t0) / step)) + 1)
    return np.c_[center[0] + r * np.cos(t), center[1] + r * np.sin(t)]


def _build(step):
    lines = {
        "Side line top": ((-HL, -HW), (HL, -HW)),
        "Side line bottom": ((-HL, HW), (HL, HW)),
        "Side line left": ((-HL, -HW), (-HL, HW)),
        "Side line right": ((HL, -HW), (HL, HW)),
        "Middle line": ((0, -HW), (0, HW)),
    }
    for name, depth, half_w in (("Big rect.", PENALTY_AREA_DEPTH, PENALTY_AREA_WIDTH / 2),
                                ("Small rect.", GOAL_AREA_DEPTH, GOAL_AREA_WIDTH / 2)):
        for side, s in (("left", -1), ("right", 1)):
            x_goal, x_main = s * HL, s * (HL - depth)
            lines[f"{name} {side} top"] = ((x_goal, -half_w), (x_main, -half_w))
            lines[f"{name} {side} bottom"] = ((x_goal, half_w), (x_main, half_w))
            lines[f"{name} {side} main"] = ((x_main, -half_w), (x_main, half_w))
    polys = {k: _segment(p, q, step) for k, (p, q) in lines.items()}

    polys["Circle central"] = _arc((0, 0), CENTER_CIRCLE_R, 0, 2 * np.pi, step)  # fechado
    # arco da grande área: parte do círculo centrado na marca do pênalti fora da área
    a = np.arccos((PENALTY_AREA_DEPTH - PENALTY_MARK_DIST) / PENALTY_ARC_R)
    mark = HL - PENALTY_MARK_DIST
    polys["Circle left"] = _arc((-mark, 0), PENALTY_ARC_R, -a, a, step)
    polys["Circle right"] = _arc((mark, 0), PENALTY_ARC_R, np.pi - a, np.pi + a, step)
    return polys


POLYLINES: dict[str, np.ndarray] = _build(CFG["pitch"]["sample_step_m"])
