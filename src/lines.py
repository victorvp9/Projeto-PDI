"""Etapa 3 (docs/01-metodo.md): segmentos de reta da máscara de marcações — Hough
probabilística e fusão de colineares. Espaço imagem (px); tamanhos em fração da
altura, parâmetros em CFG["lines"] (docs/03-plano.md, Fatia 4).
"""
import cv2
import numpy as np
from scipy.sparse.csgraph import connected_components

from src.config import CFG


def shape_filter(marks, P):
    """Tira os componentes (8-vizinhança) com alongamento < `shape_elong_min` (raiz da
    razão dos autovalores da covariância dos pixels; barra de 1 px: variância 1/12)."""
    n, lab = cv2.connectedComponents(marks.astype(np.uint8))
    v, u = np.nonzero(lab)
    k = lab[v, u]
    cnt = np.maximum(np.bincount(k, minlength=n), 1).astype(float)
    m = lambda x: np.bincount(k, x.astype(float), n) / cnt
    mu, mv = m(u), m(v)
    cuu, cvv, cuv = m(u * u) - mu ** 2, m(v * v) - mv ** 2, m(u * v) - mu * mv
    half, disc = (cuu + cvv) / 2, np.sqrt(np.maximum(((cuu - cvv) / 2) ** 2 + cuv ** 2, 0))
    # TODO(divida): uma rede de linhas toda conectada (máscara sintética) tem alongamento baixo e some;
    # poupar os componentes grandes custou F1 -0,008 no GSR train (docs/decisoes.md), então não entrou
    keep = np.sqrt(np.maximum(half + disc, 1 / 12) / np.maximum(half - disc, 1 / 12)) >= P["shape_elong_min"]
    keep[0] = False
    return keep[lab]


def hough(marks, P):
    """Segmentos (N, 4) = (u1, v1, u2, v2) da `HoughLinesP` sobre a máscara."""
    h = marks.shape[0]
    s = cv2.HoughLinesP(marks.astype(np.uint8), P["hough_rho_px"], np.deg2rad(P["hough_theta_deg"]),
                        max(1, int(round(P["hough_votes_frac"] * h))),
                        minLineLength=P["hough_min_len_frac"] * h, maxLineGap=P["hough_gap_frac"] * h)
    return np.zeros((0, 4)) if s is None else s.reshape(-1, 4).astype(float)


def _fit(pts, w):
    """Reta por mínimos quadrados totais, ponderada: (centro, direção unitária)."""
    c = (pts * w[:, None]).sum(0) / w.sum()
    return c, np.linalg.svd((pts - c) * np.sqrt(w)[:, None], full_matrices=False)[2][0]


def fuse(segs, P, h):
    """Fusão de colineares. Um par é compatível com diferença de ângulo <= `fuse_theta_deg`,
    os extremos de cada um a <= `fuse_d_frac`·h da reta do outro e vão ao longo da reta
    <= `fuse_gap_frac`·h. Grupos conexos (union-find) viram um segmento reajustado por
    mínimos quadrados totais nos extremos (peso = comprimento), extremos nas projeções
    extremas; o grupo só se funde se todos os extremos ficarem a <= td da reta ajustada
    (senão uma cadeia de cordas de um arco viraria uma reta). Repete até estabilizar."""
    cos_t, td, gap_max = np.cos(np.deg2rad(P["fuse_theta_deg"])), P["fuse_d_frac"] * h, P["fuse_gap_frac"] * h
    while len(segs) > 1:
        a, b = segs[:, :2], segs[:, 2:]
        length = np.maximum(np.hypot(*(b - a).T), 1e-9)
        d = (b - a) / length[:, None]
        nrm = np.stack([-d[:, 1], d[:, 0]], 1)
        rel = lambda p: p[None] - a[:, None]                           # [i, j] = p_j - a_i
        off = np.maximum(np.abs(np.einsum("ik,ijk->ij", nrm, rel(a))), np.abs(np.einsum("ik,ijk->ij", nrm, rel(b))))
        ta, tb = np.einsum("ik,ijk->ij", d, rel(a)), np.einsum("ik,ijk->ij", d, rel(b))
        gap = np.maximum(np.minimum(ta, tb) - length[:, None], -np.maximum(ta, tb))   # > 0: disjuntos na reta de i
        adj = (np.abs(d @ d.T) >= cos_t) & (off <= td) & (off.T <= td) & (gap <= gap_max) & (gap.T <= gap_max)
        np.fill_diagonal(adj, False)
        k, lab = connected_components(adj, directed=False)
        new, merged = [], False
        for g in range(k):
            idx = np.nonzero(lab == g)[0]
            if len(idx) > 1:
                pts = np.concatenate([a[idx], b[idx]])
                c, u = _fit(pts, np.tile(length[idx], 2))
                if np.abs((pts - c) @ np.array([-u[1], u[0]])).max() <= td:
                    t = (pts - c) @ u
                    new.append(np.r_[c + t.min() * u, c + t.max() * u])
                    merged = True
                    continue
            new.extend(segs[idx])
        segs = np.array(new)
        if not merged:
            break
    return segs


def detect_segments(marks, P=None):
    """Máscara de marcações (imagem, bool) -> segmentos (N, 4): filtro de forma
    (opcional), Hough e fusão (opcional)."""
    P = P or CFG["lines"]
    m = shape_filter(marks, P) if P["shape_filter"] else marks
    s = hough(m, P)
    return fuse(s, P, m.shape[0]) if P["fuse"] else s


def draw_segments(frame_bgr, segs):
    """Depuração: cada segmento numa cor, com os extremos marcados."""
    out = frame_bgr.copy()
    rng = np.random.default_rng(0)
    for s in np.round(segs).astype(int):
        color = tuple(int(x) for x in rng.integers(64, 256, 3))
        cv2.line(out, tuple(s[:2]), tuple(s[2:]), color, 2, cv2.LINE_AA)
        for p in (s[:2], s[2:]):
            cv2.circle(out, tuple(p), 4, color, 1, cv2.LINE_AA)
    return out
