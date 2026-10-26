"""Câmera de broadcast <-> homografia (campo -> imagem), GSR 1920x1080.

Decomposição com ponto principal no centro, sem skew, pixel quadrado (Citraro et al.,
apêndice A). Convenção do campo do projeto: X ao longo do comprimento, Y positivo em
direção à câmera principal; com r3 = r1 x r2, Z aponta para baixo (câmera tem C_z < 0,
como C_main = (0, 55, -12) do BroadTrack)."""
import numpy as np

W, H_IMG = 1920, 1080
CX, CY = W / 2, H_IMG / 2
T_PP = np.array([[1, 0, -CX], [0, 1, -CY], [0, 0, 1.0]])


def decompose(H):
    """H campo -> imagem -> (f, R, C) ou None se a H não admite focal real."""
    Hp = T_PP @ H
    Hp = Hp / np.linalg.norm(Hp)
    h1, h2 = Hp[:, 0], Hp[:, 1]
    a1, b1 = h1[0] * h2[0] + h1[1] * h2[1], h1[2] * h2[2]
    a2, b2 = h1[0] ** 2 + h1[1] ** 2 - h2[0] ** 2 - h2[1] ** 2, h1[2] ** 2 - h2[2] ** 2
    x = -(a1 * b1 + a2 * b2) / (a1 ** 2 + a2 ** 2)      # 1/f² por mínimos quadrados nas duas restrições
    if not np.isfinite(x) or x <= 0:
        return None
    f = 1 / np.sqrt(x)
    M = np.diag([1 / f, 1 / f, 1.0]) @ Hp
    lam = 2 / (np.linalg.norm(M[:, 0]) + np.linalg.norm(M[:, 1]))
    if M[2, 2] * lam < 0:                               # centro do campo à frente da câmera
        lam = -lam
    r1, r2, t = lam * M[:, 0], lam * M[:, 1], lam * M[:, 2]
    U, _, Vt = np.linalg.svd(np.c_[r1, r2, np.cross(r1, r2)])
    R = U @ Vt
    return f, R, -R.T @ t


def compose(f, R, C):
    """(f, R, C) -> H campo -> imagem, normalizada H[2,2] = 1."""
    K = np.array([[f, 0, CX], [0, f, CY], [0, 0, 1.0]])
    t = -R @ C
    H = K @ np.c_[R[:, 0], R[:, 1], t]
    return H / H[2, 2]


R0 = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0.0]])    # olhando para -Y, horizontal, X à direita, Z para baixo


def rot(pan, tilt, roll=0.0):
    """Rotação mundo -> câmera: pan em torno da vertical, tilt para baixo, roll no eixo óptico (rad)."""
    cp, sp, ct, st, cr, sr = np.cos(pan), np.sin(pan), np.cos(tilt), np.sin(tilt), np.cos(roll), np.sin(roll)
    Rz = np.array([[cp, -sp, 0], [sp, cp, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]])
    Rr = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
    return Rr @ Rx @ R0 @ Rz


def angles(R):
    """Inverso de rot: (pan, tilt, roll) em rad."""
    from scipy.optimize import least_squares
    best = None
    for p0 in (-0.6, 0, 0.6):
        r = least_squares(lambda q: (rot(*q) - R).ravel(), [p0, 0.2, 0.0])
        if best is None or r.cost < best.cost:
            best = r
    return best.x


def project(H, XY):
    p = np.c_[XY, np.ones(len(XY))] @ H.T
    return p[:, :2] / p[:, 2:], p[:, 2] * np.sign(H[2, 2]) > 0


GRID = np.stack(np.meshgrid(np.arange(-52.5, 52.51, 2.5), np.arange(-34, 34.01, 2.0)), -1).reshape(-1, 2)


def npe(H_est, H_true):
    """NPE médio (fração da altura) na grade 2,5 x 2 m visível pela H verdadeira (protocolo do projeto)."""
    uv, ok = project(H_true, GRID)
    ok &= (uv[:, 0] >= 0) & (uv[:, 0] < W) & (uv[:, 1] >= 0) & (uv[:, 1] < H_IMG)
    if ok.sum() == 0:
        return np.nan
    ue, oke = project(H_est, GRID[ok])
    if not oke.all():
        return np.inf
    return float(np.mean(np.linalg.norm(ue - uv[ok], axis=1)) / H_IMG)


if __name__ == "__main__":                              # autoteste: compose/decompose e rot/angles são inversas
    rng = np.random.default_rng(0)
    for _ in range(200):
        C = np.array([rng.uniform(-10, 10), rng.uniform(40, 90), -rng.uniform(10, 40)])
        f = rng.uniform(1200, 9000)
        R = rot(rng.uniform(-0.8, 0.8), rng.uniform(0.1, 0.6), rng.uniform(-0.03, 0.03))
        Hs = compose(f, R, C)
        f2, R2, C2 = decompose(Hs * rng.choice([-1, 1]) * rng.uniform(0.1, 10))
        assert abs(f2 - f) / f < 1e-6 and np.allclose(R2, R, atol=1e-6) and np.allclose(C2, C, atol=1e-4), (f, f2, C, C2)
        assert np.allclose(angles(R2), angles(R), atol=1e-6)
    print("camera.py: autoteste ok")
