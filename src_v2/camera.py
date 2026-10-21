"""Câmera de transmissão a partir da homografia (campo -> imagem): focal, rotação e centro.

Pinhole com ponto principal no centro da imagem, sem skew e pixel quadrado (Citraro et al.,
2020, apêndice A). Na convenção do campo (X ao longo do comprimento, Y positivo em direção à
câmera principal), com r3 = r1 x r2 o eixo Z aponta para baixo: a câmera principal tem C_z < 0.
v2, B2 (docs/decisoes.md, 2026-10-21): o centro C de uma âncora longe do C do jogo denuncia um
encaixe errado do detector."""
import numpy as np


def decompose(H, size):
    """H (campo -> imagem) e tamanho (w, h) da imagem -> (f, R, C) no espaço do campo (m),
    ou None se a H não admite focal real (nenhuma câmera pinhole a produz)."""
    w, h = size
    Hp = np.array([[1, 0, -w / 2], [0, 1, -h / 2], [0, 0, 1.0]]) @ H
    Hp = Hp / np.linalg.norm(Hp)
    h1, h2 = Hp[:, 0], Hp[:, 1]
    # ortogonalidade e mesma norma de r1 e r2: duas equações lineares em 1/f², por mínimos quadrados
    a1, b1 = h1[0] * h2[0] + h1[1] * h2[1], h1[2] * h2[2]
    a2, b2 = h1[0] ** 2 + h1[1] ** 2 - h2[0] ** 2 - h2[1] ** 2, h1[2] ** 2 - h2[2] ** 2
    den = a1 ** 2 + a2 ** 2
    x = -(a1 * b1 + a2 * b2) / den if den > 0 else np.nan
    if not np.isfinite(x) or x <= 0:
        return None
    f = 1 / np.sqrt(x)
    M = np.diag([1 / f, 1 / f, 1.0]) @ Hp
    lam = 2 / (np.linalg.norm(M[:, 0]) + np.linalg.norm(M[:, 1]))
    if M[2, 2] * lam < 0:                              # o centro do campo fica à frente da câmera
        lam = -lam
    r1, r2, t = lam * M[:, 0], lam * M[:, 1], lam * M[:, 2]
    U, _, Vt = np.linalg.svd(np.c_[r1, r2, np.cross(r1, r2)])
    R = U @ Vt
    return f, R, -R.T @ t


def compose(f, R, C, size):
    """Inverso de decompose: (f, R, C) -> H (campo -> imagem), H[2,2] = 1."""
    w, h = size
    K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1.0]])
    t = -R @ C
    H = K @ np.c_[R[:, 0], R[:, 1], t]
    return H / H[2, 2]


def center(H, size):
    """Centro da câmera (m, campo) de H, ou None."""
    d = decompose(H, size)
    return None if d is None else d[2]
