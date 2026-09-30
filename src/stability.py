"""Estabilidade temporal na série estimada (docs/01-metodo.md, alteração da Fatia 7):
tremor (temporal.jitter) e deslize contra o movimento real da imagem, medido por ECC,
independente do Lucas–Kanade que o 6c usa para propagar. Espaço imagem (px).
"""
import cv2
import numpy as np

from src.config import CFG
from src.geometry import project

S = CFG["stability"]


def ecc_motion(gray0, gray1, mask1):
    """Homografia (imagem, px, resolução cheia) que leva o frame t-1 (gray0) ao t (gray1),
    por ECC numa versão reduzida a `ecc_scale`, só nos pixels de `mask1` (gramado de t).
    Devolve (W, convergiu, correlação); sem convergência, W é NaN."""
    s = S["ecc_scale"]
    g0 = cv2.resize(gray0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
    g1 = cv2.resize(gray1, (g0.shape[1], g0.shape[0]), interpolation=cv2.INTER_AREA).astype(np.float32)
    m = cv2.resize(mask1.astype(np.uint8), (g0.shape[1], g0.shape[0]), interpolation=cv2.INTER_NEAREST)
    crit = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, S["ecc_iters"], S["ecc_eps"])
    try:   # W leva coordenadas do modelo (g0) às da entrada (g1): o movimento t-1 -> t
        cc, W = cv2.findTransformECC(g0, g1, np.eye(3, dtype=np.float32), cv2.MOTION_HOMOGRAPHY, crit, m, S["ecc_gauss"])
    except cv2.error:
        return np.full((3, 3), np.nan), False, np.nan
    Sc = np.diag([s, s, 1.0])
    return np.linalg.inv(Sc) @ W.astype(float) @ Sc, True, float(cc)


def _apply(A, uv):
    q = np.c_[uv, np.ones(len(uv))] @ A.T
    return q[:, :2] / q[:, 2:]


def slip(Hs, motions, usable, size, grid):
    """Deslize por par (t-1, t), em px: mediana de ‖H_t·H_{t-1}⁻¹·u − W_t·u‖ nos pontos da
    grade do campo (m) visíveis em t-1 (projetados por H_{t-1} dentro da imagem). Só nos
    pares com H nos dois frames e `usable[t]` (ECC convergido, sem corte); NaN nos outros."""
    w, h = size
    out = np.full(len(Hs), np.nan)
    for t in range(1, len(Hs)):
        if not (usable[t] and np.isfinite(Hs[t - 1]).all() and np.isfinite(Hs[t]).all()):
            continue
        uv, front = project(Hs[t - 1], grid)
        ok = front & (uv[:, 0] >= 0) & (uv[:, 0] < w) & (uv[:, 1] >= 0) & (uv[:, 1] < h)
        if ok.any():
            p = uv[ok]
            out[t] = np.median(np.linalg.norm(_apply(Hs[t] @ np.linalg.inv(Hs[t - 1]), p) - _apply(motions[t], p), axis=1))
    return out
