"""T4 e T5(b) em cenas sintéticas: a vista central fecha a homografia?

Câmeras: (f, C, roll) reais, decompostas das H do detector dos jogos 2, 4, 5, 6 e 9 (d2_cameras.csv),
só as com C a <= 5 m da mediana do jogo; cada cena reaponta a câmera para um ponto perto do
círculo central e aceita a cena só se ela mostrar >= 50% do círculo, a linha do meio
e uma lateral cruzando a linha do meio dentro do quadro. Observações sintéticas com ruído
gaussiano isotrópico sigma (px, 1920x1080), 25% contíguos do círculo ocultados (jogadores).

Métodos (todos sem gabarito, só as observações):
  T4 fechada  : P1,P2 = linha do meio ∩ elipse, S = linha do meio ∩ lateral; projetividade 1D
                da linha do meio -> centro e ponto de fuga V_Y; polar de V_Y ∩ elipse -> (±9,15, 0); DLT com 6 pontos.
  T4 + refino : T4 fechada refinada por mínimos quadrados (Cauchy) nos resíduos no campo de todos os pontos observados.
  T5 2 pontos : C do jogo conhecido (com erro e), roll = 0; pan, tilt, f pelos 2 pontos P1, P2.
  T5 3 GL     : mesmo modelo, ajustado a todos os pontos observados (círculo, linha do meio, lateral).
Medida: NPE médio na grade 2,5 x 2 m visível (protocolo do projeto); "errada" = NPE > 0,05.
Uso: python -I t4_t5_sintetico.py <saída do d2> [n_cenas]"""
import csv
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).parent))
from camera import H_IMG, W, compose, npe, project, rot  # noqa: E402

R_C, HW = 9.15, 34.0
rng = np.random.default_rng(42)


# ---------- geometria projetiva das observações ----------
def fit_line(pts):
    c = pts.mean(0)
    d = np.linalg.svd(pts - c, full_matrices=False)[2][0]
    return np.cross([*c, 1.0], [*(c + d), 1.0])


def fit_conic(pts):
    """Elipse por ajuste direto (Fitzgibbon, forma de Halir-Flusser), pontos normalizados. Devolve a matriz 3x3."""
    m, s = pts.mean(0), pts.std()
    T = np.array([[1 / s, 0, -m[0] / s], [0, 1 / s, -m[1] / s], [0, 0, 1]])
    x, y = ((pts - m) / s).T
    D1 = np.c_[x * x, x * y, y * y]
    D2 = np.c_[x, y, np.ones_like(x)]
    S1, S2, S3 = D1.T @ D1, D1.T @ D2, D2.T @ D2
    Tm = -np.linalg.solve(S3, S2.T)
    M = S1 + S2 @ Tm
    M = np.array([M[2] / 2, -M[1], M[0] / 2])
    w, v = np.linalg.eig(M)
    v = np.real(v)
    cond = 4 * v[0] * v[2] - v[1] ** 2
    a1 = v[:, np.argmax(cond > 0)] if (cond > 0).any() else v[:, 0]
    a, b, c, d, e, f = np.r_[a1, Tm @ a1]
    Cn = np.array([[a, b / 2, d / 2], [b / 2, c, e / 2], [d / 2, e / 2, f]])
    return T.T @ Cn @ T


def line_conic(l, Cm):
    """Interseções (até 2) da reta l com a cônica Cm, como pontos da imagem."""
    a, b, c = l
    n2 = a * a + b * b
    p0 = np.array([W / 2, H_IMG / 2]) - (a * W / 2 + b * H_IMG / 2 + c) / n2 * np.array([a, b])
    d = np.array([-b, a]) / np.sqrt(n2)
    P, D = np.r_[p0, 1.0], np.r_[d, 0.0]
    A, B, Cq = D @ Cm @ D, 2 * D @ Cm @ P, P @ Cm @ P
    disc = B * B - 4 * A * Cq
    if disc < 0:
        return []
    return [p0 + t * d for t in ((-B - np.sqrt(disc)) / (2 * A), (-B + np.sqrt(disc)) / (2 * A))]


def t4_closed(Cm, l_mid, l_side):
    """Construção fechada do T4. Devolve H campo -> imagem ou None."""
    P = line_conic(l_mid, Cm)
    if len(P) < 2:
        return None
    P = sorted(P, key=lambda p: p[1])                     # o de cima (v menor) é o lado oposto: Y = -9,15
    S = np.cross(l_mid, l_side)
    if abs(S[2]) < 1e-12:
        return None
    S = S[:2] / S[2]
    Ys = -HW if S[1] < P[0][1] else HW                    # lateral acima dos dois pontos: a de cima (Y = -34)
    # projetividade 1D da linha do meio: s = (alpha Y + beta) / (gamma Y + 1)
    d = (P[1] - P[0]) / np.linalg.norm(P[1] - P[0])
    o = P[0]
    s = [0.0, float((P[1] - o) @ d), float((S - o) @ d)]
    Y = [-R_C, R_C, Ys]
    A = np.array([[y, 1, -si * y] for y, si in zip(Y, s)])
    alpha, beta, gamma = np.linalg.solve(A, s)
    center = o + beta * d
    VY = gamma * np.r_[o, 1.0] + alpha * np.r_[d, 0.0]    # Y -> infinito
    Q = line_conic(Cm @ VY, Cm)                           # polar de V_Y ∩ elipse = (±9,15, 0)
    if len(Q) < 2:
        return None
    Q = sorted(Q, key=lambda p: p[0])                     # o da esquerda é X = -9,15 (câmera principal: X para a direita)
    fld = np.float32([[0, -R_C], [0, R_C], [0, Ys], [0, 0], [-R_C, 0], [R_C, 0]])
    img = np.float32([P[0], P[1], S, center, Q[0], Q[1]])
    Hh, _ = cv2.findHomography(fld, img, 0)
    return Hh


def field_resid(H, obs):
    """Resíduos no campo (m) dos pontos observados levados por H^-1: raio - 9,15; X da linha do meio; Y - Ys da lateral."""
    Hi = np.linalg.inv(H)
    out = []
    for kind, pts, val in obs:
        q = np.c_[pts, np.ones(len(pts))] @ Hi.T
        xy = q[:, :2] / q[:, 2:]
        out.append(np.linalg.norm(xy, axis=1) - R_C if kind == "circ" else (xy[:, 0] if kind == "mid" else xy[:, 1] - val))
    return np.concatenate(out)


def t4_refine(H0, obs):
    g0 = (H0 / H0[2, 2]).ravel()[:8]
    r = least_squares(lambda g: field_resid(np.append(g, 1).reshape(3, 3), obs), g0, loss="cauchy", f_scale=0.5)
    return np.append(r.x, 1).reshape(3, 3)


def t5(Chat, obs_pts=None, obs=None):
    """PTZ com C fixo e roll 0: (pan, tilt, f) pelos pontos (campo, imagem) ou por todo o apoio (obs)."""
    def H_of(q):
        return compose(q[2], rot(q[0], q[1]), Chat)

    def res(q):
        if obs is not None:
            return field_resid(H_of(q), obs)
        uv, _ = project(H_of(q), obs_pts[0])
        return ((uv - obs_pts[1]) / 100).ravel()
    best = None
    for p0 in (-0.5, 0.0, 0.5):
        for t0 in (0.15, 0.35):
            for f0 in (2500, 5000):
                try:
                    r = least_squares(res, [p0, t0, f0], x_scale=[0.1, 0.1, 500], loss="cauchy" if obs is not None else "linear")
                except (ValueError, np.linalg.LinAlgError):
                    continue
                if best is None or r.cost < best.cost:
                    best = r
    return H_of(best.x)


# ---------- cenas ----------
def visible(uv, ok, m=0):
    return ok & (uv[:, 0] >= m) & (uv[:, 0] < W - m) & (uv[:, 1] >= m) & (uv[:, 1] < H_IMG - m)


CIRC = np.c_[R_C * np.cos(np.linspace(0, 2 * np.pi, 360, endpoint=False)), R_C * np.sin(np.linspace(0, 2 * np.pi, 360, endpoint=False))]
MID = np.c_[np.zeros(273), np.linspace(-HW, HW, 273)]
SIDES = {s: np.c_[np.linspace(-52.5, 52.5, 841), np.full(841, s)] for s in (-HW, HW)}


def aim(C, target, roll):
    """pan, tilt que põem `target` (campo, Z = 0) no centro da imagem."""
    from scipy.optimize import least_squares as ls
    r = ls(lambda q: (rot(q[0], q[1], roll) @ (np.r_[target, 0] - C))[:2], [0.0, 0.25])
    return r.x


def make_scene(cams):
    for _ in range(200):
        f, C, roll = cams[rng.integers(len(cams))]
        f = f * rng.uniform(0.7, 1.3)
        pan, tilt = aim(C, rng.uniform(-8, 8, 2), roll)
        H = compose(f, rot(pan, tilt, roll), C)
        uv_c, ok_c = project(H, CIRC)
        vis_c = visible(uv_c, ok_c)
        uv_m, ok_m = project(H, MID)
        vis_m = visible(uv_m, ok_m)
        if vis_c.mean() < 0.5 or vis_m.sum() < 20:
            continue
        for s in (-HW, HW):
            uv_s, ok_s = project(H, SIDES[s])
            vis_s = visible(uv_s, ok_s)
            Suv, okS = project(H, np.array([[0.0, s]]))
            if vis_s.sum() >= 20 and visible(Suv, okS, 20)[0]:
                return H, (f, C, roll), (uv_c, vis_c), (uv_m, vis_m), (uv_s[vis_s], s)
    return None


def observe(scene, sigma):
    H, _, (uv_c, vis_c), (uv_m, vis_m), (uv_s, s) = scene
    idx = np.nonzero(vis_c)[0]
    k = len(idx) // 4
    start = rng.integers(len(idx))
    hide = set(idx[(start + np.arange(k)) % len(idx)])
    pc = uv_c[[i for i in idx if i not in hide]]
    noise = lambda p: p + rng.normal(0, sigma, p.shape)
    pc, pm, ps = noise(pc), noise(uv_m[vis_m]), noise(uv_s)
    return pc, pm, ps, s


cams = []
for r in csv.DictReader(open(Path(sys.argv[1]) / "d2_cameras.csv", encoding="utf-8")):
    if r["ok"] == "True" and r["jogo"] in ("2", "4", "5", "6", "9"):
        cams.append((r["jogo"], float(r["f"]), np.array([float(r["cx"]), float(r["cy"]), float(r["cz"])]), np.radians(float(r["roll"]))))
games = {g: np.median([c[2] for c in cams if c[0] == g], 0) for g in {c[0] for c in cams}}
cams = [(f, C, roll) for g, f, C, roll in cams if np.linalg.norm(C - games[g]) <= 5]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 300
scenes = [s for s in (make_scene(cams) for _ in range(N)) if s is not None]
print(f"câmeras-base: {len(cams)}; cenas centrais válidas: {len(scenes)} de {N}")

ERRS = (0, 0.5, 1, 2, 5)
methods = ["T4 fechada", "T4 + refino"] + [f"T5 {k}, e={e} m" for k in ("2 pontos", "3 GL") for e in ERRS]
print("\n| sigma (px) | método | NPE mediano | NPE p90 | fração NPE <= 0,01 | fração errada (NPE > 0,05) | falhas |")
print("|---|---|---|---|---|---|---|")
for sigma in (0.0, 1.0, 2.0, 4.0):
    res = {m: [] for m in methods}
    for sc in scenes:
        H, (f, C, roll), *_ = sc
        pc, pm, ps, s = observe(sc, sigma)
        obs = [("circ", pc, None), ("mid", pm, None), ("side", ps, s)]
        Cm, lm, lsd = fit_conic(pc), fit_line(pm), fit_line(ps)
        H4 = t4_closed(Cm, lm, lsd)
        res["T4 fechada"].append(np.inf if H4 is None else npe(H4, H))
        res["T4 + refino"].append(np.inf if H4 is None else npe(t4_refine(H4, obs), H))
        P = line_conic(lm, Cm)
        P = sorted(P, key=lambda p: p[1]) if len(P) == 2 else None
        for e in ERRS:
            dirn = rng.normal(size=3)
            Chat = C + e * dirn / np.linalg.norm(dirn)
            res[f"T5 2 pontos, e={e} m"].append(
                np.inf if P is None else npe(t5(Chat, obs_pts=(np.array([[0, -R_C], [0, R_C]]), np.array(P))), H))
            res[f"T5 3 GL, e={e} m"].append(npe(t5(Chat, obs=obs), H))
    for m in methods:
        a = np.array(res[m], float)
        fin = a[np.isfinite(a)]
        print(f"| {sigma:g} | {m} | {np.median(a):.4f} | {np.percentile(a, 90):.4f} | {np.mean(a <= 0.01):.2f} | {np.mean(a > 0.05):.2f} | {np.sum(~np.isfinite(a))} |")
