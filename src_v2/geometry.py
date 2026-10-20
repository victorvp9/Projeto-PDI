"""Projeção campo -> imagem e distância ponto-polilinha."""
import numpy as np


def project(H, XY):
    """Projeta pontos do campo (m, (N,2)) para a imagem (px) com H campo -> imagem.

    Devolve `uv` (N,2) e `in_front` (N,) — False para pontos atrás da câmera.
    O sinal de H é arbitrário; fixa-se supondo o centro do campo (0, 0) à frente
    da câmera, o que vale para a câmera principal (docs/decisoes.md).
    """
    p = np.c_[XY, np.ones(len(XY))] @ H.T
    with np.errstate(divide="ignore", invalid="ignore"):
        uv = p[:, :2] / p[:, 2:]
    return uv, p[:, 2] * np.sign(H[2, 2]) > 0


def project_segments(H, XY):
    """Polilinha do campo (m) -> segmentos na imagem (px), (K,2,2).

    Só entram segmentos entre amostras consecutivas ambas à frente da câmera;
    por isso a polilinha precisa vir amostrada densamente.
    """
    uv, ok = project(H, XY)
    keep = ok[:-1] & ok[1:]
    return np.stack([uv[:-1][keep], uv[1:][keep]], axis=1)


def point_segment_distance(pts, segs):
    """Menor distância (px) de cada ponto da imagem (N,2) aos segmentos (K,2,2).

    Sem segmentos, a distância é infinita.
    """
    if len(segs) == 0:
        return np.full(len(pts), np.inf)
    a, d = segs[:, 0], segs[:, 1] - segs[:, 0]                     # (K,2)
    ap = pts[:, None, :] - a[None]                                 # (N,K,2)
    t = np.clip((ap * d).sum(-1) / np.maximum((d * d).sum(-1), 1e-12), 0, 1)
    return np.linalg.norm(ap - t[..., None] * d, axis=-1).min(axis=1)
