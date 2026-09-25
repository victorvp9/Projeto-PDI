"""Ajuste ponto-linha da homografia (campo -> imagem).

Minimiza, com perda robusta, a distância (px) de pontos da imagem às linhas do
modelo da classe deles projetadas pela H. Produz a H_gt do GSR a partir das
linhas anotadas (Fatia 2) e é o refinamento da Etapa 7 (Fatia 5).

O objetivo otimizado é uma versão lisa da distância às polilinhas: reta infinita
para as classes retas e distância de Sampson à cônica projetada do círculo
completo para os arcos. A distância a um segmento finito tem quina na ponta, e
anotadores clicam justamente nas pontas (cantos de área, fim de arco): o
Gauss-Newton se arrastava até o limite de avaliações. E o círculo como polilinha
quebrava a invariância das configurações degeneradas (círculo + uma reta), que
passavam no teste de condição. O resíduo reportado (aceite, "duvidoso")
continua sendo a distância às polilinhas (docs/decisoes.md).
"""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares

from src.config import CFG
from src.geometry import point_segment_distance, project_segments
from src.pitch_model import CENTER_CIRCLE_R, HL, HW, PENALTY_ARC_R, PENALTY_MARK_DIST, POLYLINES

F = CFG["fit"]
# normalização fixa do campo (m -> ~[-1, 1]); a da imagem depende do tamanho
N_FIELD = np.diag([1 / HL, 1 / HW, 1.0])

# geometria lisa do objetivo (campo): cônica (X-cx)² + Y² - r² = 0 do círculo completo
# para as classes circulares, reta homogênea para as demais
_CIRCLES = {"Circle central": (0.0, CENTER_CIRCLE_R),
            "Circle left": (-(HL - PENALTY_MARK_DIST), PENALTY_ARC_R),
            "Circle right": (HL - PENALTY_MARK_DIST, PENALTY_ARC_R)}
CONICS = {k: np.array([[1, 0, -cx], [0, 1, 0], [-cx, 0, cx * cx - r * r]]) for k, (cx, r) in _CIRCLES.items()}
LINE_EQ = {k: np.cross([*p[0], 1.0], [*p[-1], 1.0]) for k, p in POLYLINES.items() if k not in _CIRCLES}


def class_distances(H, lines_uv):
    """Classe -> distância (px) de cada ponto da imagem (K,2) à polilinha do modelo
    daquela classe projetada por H (campo -> imagem). Infinita se a polilinha
    inteira cai atrás da câmera."""
    return {k: point_segment_distance(p, project_segments(H, POLYLINES[k])) for k, p in lines_uv.items()}


def smooth_distances(H, lines_uv):
    """Distância (px) de cada ponto da imagem à reta infinita da sua classe, ou
    distância de Sampson à cônica do círculo completo, projetadas por H (campo ->
    imagem); concatenada na ordem do dict."""
    Hi = np.linalg.inv(H)
    out = []
    for k, p in lines_uv.items():
        q = np.c_[p, np.ones(len(p))]
        if k in LINE_EQ:
            l = Hi.T @ LINE_EQ[k]                  # reta na imagem: l = H^-T L
            out.append(np.abs(q @ l) / np.hypot(l[0], l[1]))
        else:
            Cq = q @ (Hi.T @ CONICS[k] @ Hi)       # cônica na imagem: C' = H^-T C H^-1
            out.append(np.abs((Cq * q).sum(axis=1)) / (2 * np.hypot(Cq[:, 0], Cq[:, 1])))
    return np.concatenate(out)


@dataclass
class Fit:
    H: np.ndarray | None   # campo -> imagem; None se nem tentou
    resid_px: float        # mediana da distância às polilinhas (px) na solução
    rank: int              # posto do jacobiano na solução
    cond: float            # condição do jacobiano (parâmetros normalizados)
    n_points: int
    ok: bool               # bem determinado e dentro dos limites do config
    cost: float = np.inf   # custo robusto na solução (compara ajustes de pontos de partida diferentes)


def _img_norm(size):
    w, h = size
    return np.array([[2 / w, 0, -1], [0, 2 / h, -1], [0, 0, 1.0]])


def fit_point_line(H0, lines_uv, size) -> Fit:
    """Ajusta H (campo -> imagem) aos pontos anotados (imagem, px) partindo de H0.

    Parâmetros: G = N_img · H · N_campo⁻¹ com G[2,2] = 1 (8 graus de liberdade),
    para que a condição do jacobiano meça a geometria e não a escala de H.
    Aceite: posto 8, condição <= max_cond e resíduo mediano <= max_resid_px.
    """
    n = sum(len(p) for p in lines_uv.values())
    if n < F["min_points"]:
        return Fit(None, np.nan, 0, np.inf, n, False)
    Ni = _img_norm(size)
    Ni_inv = np.linalg.inv(Ni)

    def H_of(g):
        return Ni_inv @ np.append(g, 1.0).reshape(3, 3) @ N_FIELD

    def resid(g):
        return np.minimum(smooth_distances(H_of(g), lines_uv), F["resid_cap_px"])

    G0 = Ni @ H0 @ np.linalg.inv(N_FIELD)
    r = least_squares(resid, (G0 / G0[2, 2]).ravel()[:8], loss=F["loss"], f_scale=F["f_scale_px"], x_scale="jac")
    s = np.linalg.svd(r.jac, compute_uv=False)
    # jacobiano por diferenças finitas: precisão relativa ~ sqrt(eps), então é essa a tolerância do posto
    rank = int((s > s[0] * np.sqrt(np.finfo(float).eps)).sum())
    cond = float(s[0] / s[-1]) if s[-1] > 0 else np.inf
    med = float(np.median(np.concatenate(list(class_distances(H_of(r.x), lines_uv).values()))))
    ok = rank == 8 and cond <= F["max_cond"] and med <= F["max_resid_px"]
    return Fit(H_of(r.x), med, rank, cond, n, ok, float(r.cost))
