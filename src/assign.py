"""Etapas 5-7 (docs/01-metodo.md), pipeline mínimo da Fatia 5: classificação por
hipótese e verificação, H₀ e refinamento ponto-linha (`fit_point_line` da Fatia 2).

Espaços: imagem (px, u, v) e campo (m, X, Y); H sempre campo -> imagem.
Hipótese: 2 retas de cada família de paralelas (ponto de fuga) atribuídas a linhas
infinitas do modelo — Y constante (ao longo do comprimento) e X constante (ao longo
da largura) — respeitando a ordem na imagem; H pelo retângulo das 4 interseções.
"""
import itertools

import cv2
import numpy as np

from src.config import CFG
from src.geometry import point_segment_distance, project, project_segments
from src.homography import LINE_EQ, fit_point_line
from src.pitch_model import CORNERS, POLYLINES

A = CFG["assign"]
# linhas infinitas do modelo por família (as retas de cima das duas grandes áreas são a mesma reta)
Y_LINES = sorted({float(p[0, 1]) for k, p in POLYLINES.items() if k in LINE_EQ and p[0, 1] == p[-1, 1]})
X_LINES = sorted({float(p[0, 0]) for k, p in POLYLINES.items() if k in LINE_EQ and p[0, 0] == p[-1, 0]})
R180 = np.diag([-1.0, -1.0, 1.0])


def _hline(s):
    return np.cross([s[0], s[1], 1.0], [s[2], s[3], 1.0])


def _to_vp(segs, vp, tol_deg):
    """Segmentos (bool) cuja direção aponta para o ponto de fuga homogêneo vp."""
    d = segs[:, 2:] - segs[:, :2]
    if abs(vp[2]) > 1e-9 * np.linalg.norm(vp[:2]):
        to = vp[:2] / vp[2] - (segs[:, :2] + segs[:, 2:]) / 2
    else:
        to = np.tile(vp[:2], (len(segs), 1))                     # ponto de fuga no infinito
    cos = np.abs((d * to).sum(1)) / (np.linalg.norm(d, axis=1) * np.linalg.norm(to, axis=1) + 1e-12)
    return cos >= np.cos(np.deg2rad(tol_deg))


def _vp_refine(segs, idx, length):
    """Ponto de fuga (homogêneo) por mínimos quadrados das retas dos segmentos idx
    (normalizadas, peso = comprimento): menor vetor singular."""
    L = np.array([_hline(segs[i]) for i in idx])
    L = L / np.hypot(L[:, 0], L[:, 1])[:, None] * np.sqrt(length[idx])[:, None]
    return np.linalg.svd(L)[2][-1]


def families(segs, P=A):
    """Duas famílias de retas: (índices ao longo do comprimento, índices ao longo da
    largura). `family_mode`: "vp" — ponto de fuga por busca exaustiva em pares (peso =
    comprimento), com pelo menos `vp_min_segs` segmentos, reajustado por mínimos
    quadrados nos inliers e com os inliers recalculados; a família ao longo do
    comprimento é a mais horizontal. "angle" — ângulo com a horizontal <= `angle_split_deg`."""
    length = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
    if P["family_mode"] == "angle":
        ang = np.degrees(np.arctan2(np.abs(segs[:, 3] - segs[:, 1]), np.abs(segs[:, 2] - segs[:, 0])))
        return np.nonzero(ang <= P["angle_split_deg"])[0], np.nonzero(ang > P["angle_split_deg"])[0]
    rest, groups = np.arange(len(segs)), []
    for _ in range(2):
        best = (0.0, rest[:0])
        for i, j in itertools.combinations(rest, 2):
            vp = np.cross(_hline(segs[i]), _hline(segs[j]))
            if np.any(vp):
                inl = rest[_to_vp(segs[rest], vp, P["vp_tol_deg"])]
                if len(inl) >= P["vp_min_segs"] and length[inl].sum() > best[0]:
                    best = (length[inl].sum(), inl)
        if len(best[1]):
            inl = rest[_to_vp(segs[rest], _vp_refine(segs, best[1], length), P["vp_tol_deg"])]
            best = (0.0, inl if len(inl) >= P["vp_min_segs"] else best[1])
        else:
            best = (0.0, rest)
        groups.append(best[1])
        rest = np.setdiff1d(rest, best[1])
    horiz = [np.average(np.abs(segs[g, 3] - segs[g, 1]) / np.maximum(length[g], 1e-9), weights=length[g]) if len(g) else np.inf
             for g in groups]
    return (groups[0], groups[1]) if horiz[0] <= horiz[1] else (groups[1], groups[0])


def valid_orientation(H, size):
    """Sem espelhamento (determinante do jacobiano campo -> imagem > 0, com o campo à
    frente) e com Y+ = lado da câmera: um ponto no pé da imagem volta ao campo com Y
    maior que um ponto a 80% da altura. Separa H de H·R180, que projetam as mesmas
    linhas (o modelo é simétrico por (X, Y) -> (−X, −Y))."""
    w, h = size
    Hi = np.linalg.inv(H)
    q = Hi @ np.array([[w / 2, h - 1, 1.0], [w / 2, 0.8 * h, 1.0]]).T
    if abs(q[2]).min() < 1e-12:
        return False
    X = (q[:2] / q[2]).T
    uv, front = project(H, X)
    if not front.all():
        return False
    e = 1e-3
    J = (np.stack([project(H, X[:1] + [e, 0])[0][0], project(H, X[:1] + [0, e])[0][0]]) - uv[0]) / e
    return np.linalg.det(J) > 0 and X[0, 1] > X[1, 1]


def _pairs(segs, idx, key, h, P):
    """Pares ordenados (a, b) dos `top_k` segmentos mais longos da família, com
    key(a) > key(b) e retas distintas (a >= pair_min_frac·h)."""
    length = np.hypot(segs[idx, 2] - segs[idx, 0], segs[idx, 3] - segs[idx, 1])
    top = idx[np.argsort(-length)[:P["top_k"]]]
    out = []
    for i, j in itertools.combinations(top, 2):
        ki, kj = key(segs[i]), key(segs[j])
        if np.isfinite(ki) and np.isfinite(kj) and abs(ki - kj) >= P["pair_min_frac"] * h:
            out.append((i, j) if ki > kj else (j, i))
    return out


def hypotheses(segs, size, P=A):
    """Homografias candidatas (campo -> imagem) de 2 retas ao longo do comprimento (a
    de baixo na imagem recebe o Y maior) e 2 ao longo da largura (a da direita recebe o
    X maior); só as com orientação válida. Devolve (lista de H, número tentado)."""
    w, h = size
    fx, fy = families(segs, P)
    v_at = lambda s: (lambda l: -(l[0] * w / 2 + l[2]) / l[1] if abs(l[1]) > 1e-9 else np.inf)(_hline(s))
    u_at = lambda s: (lambda l: -(l[1] * h / 2 + l[2]) / l[0] if abs(l[0]) > 1e-9 else np.inf)(_hline(s))
    out, tried = [], 0
    for (a, b), (c, d) in itertools.product(_pairs(segs, fx, v_at, h, P), _pairs(segs, fy, u_at, h, P)):
        la, lb, lc, ld = (_hline(segs[k]) for k in (a, b, c, d))
        q = np.array([np.cross(la, lc), np.cross(la, ld), np.cross(lb, lc), np.cross(lb, ld)])
        if np.abs(q[:, 2]).min() < 1e-9:
            continue
        img = (q[:, :2] / q[:, 2:]).astype(np.float32)
        # a: de baixo (Y maior), b: de cima; c: da direita (X maior), d: da esquerda
        for (Yb, Ya), (Xd, Xc) in itertools.product(itertools.combinations(Y_LINES, 2), itertools.combinations(X_LINES, 2)):
            tried += 1
            field = np.float32([[Xc, Ya], [Xd, Ya], [Xc, Yb], [Xd, Yb]])
            H = cv2.getPerspectiveTransform(field, img).astype(float)
            if valid_orientation(H, size):
                out.append(H)
    return out, tried


def _model_points(step):
    k = max(1, int(round(step / CFG["pitch"]["sample_step_m"])))
    pts = [p[::k] for p in POLYLINES.values()]
    nxt = np.concatenate([np.r_[np.arange(1, len(p)), len(p) - 2] + o for p, o in zip(pts, np.cumsum([0] + [len(p) for p in pts[:-1]]))])
    return np.concatenate(pts), nxt


MODEL, MODEL_NEXT = _model_points(A["score_step_m"])


def _clip_front(H, poly, rel=1e-6):
    """Polígono do campo (m) recortado ao semiplano à frente da câmera (o sinal de w é o
    do centro do campo, como em geometry.project)."""
    w = (np.c_[poly, np.ones(len(poly))] @ H[2]) * np.sign(H[2, 2] or 1.0)
    eps = rel * np.abs(w).max()
    out = []
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        if w[i] > eps:
            out.append(poly[i])
        if (w[i] > eps) != (w[j] > eps):
            out.append(poly[i] + (eps - w[i]) / (w[j] - w[i]) * (poly[j] - poly[i]))
    return np.array(out)


class Evidence:
    """O que a verificação consulta num frame: distância às marcas, gramado (inteiro e
    reduzido) e pontos dos segmentos detectados (sem as cordas) com o peso de cada um."""

    def __init__(self, marks, grass, segs, P=A):
        self.h, self.w = marks.shape
        self.dist = cv2.distanceTransform((~marks).astype(np.uint8), cv2.DIST_L2, 5)
        self.grass = grass
        f = P["iou_scale"]
        self.small = cv2.resize(grass.astype(np.uint8), (int(self.w * f), int(self.h * f)), interpolation=cv2.INTER_NEAREST)
        self.S = np.diag([f, f, 1.0])
        pts = [_sample(sg, P["seg_step_px"]) for sg in segs]
        self.pts = np.concatenate(pts) if pts else np.zeros((0, 2))
        self.pw = np.concatenate([np.full(len(q), np.hypot(sg[2] - sg[0], sg[3] - sg[1]) / len(q)) for q, sg in zip(pts, segs)]) if pts else np.zeros(0)
        sel = np.linspace(0, len(self.pts) - 1, min(len(self.pts), P["verify_max_pts"])).astype(int) if len(self.pts) else []
        self.pts, self.pw = self.pts[sel], self.pw[sel]          # passo fixo: a fração explicada não muda em média


LINES_COARSE = {k: POLYLINES[k][np.r_[np.arange(0, len(POLYLINES[k]) - 1, 20), len(POLYLINES[k]) - 1]] for k in LINE_EQ}


def field_iou(H, ev):
    """IoU entre o campo projetado por H e o gramado da Etapa 1, na resolução reduzida."""
    poly = _clip_front(H, CORNERS)
    if len(poly) < 3:
        return 0.0
    q = np.c_[poly, np.ones(len(poly))] @ (ev.S @ H).T
    uv = np.clip(q[:, :2] / q[:, 2:], -1e5, 1e5).astype(np.int32)
    canvas = np.zeros(ev.small.shape, np.uint8)
    cv2.fillPoly(canvas, [uv], 1)
    union = (canvas | ev.small).sum()
    return float((canvas & ev.small).sum() / union) if union else 0.0


def verify(H, ev, P=A):
    """Nota de uma hipótese: (imagem, modelo, IoU) e a soma, cada termo em [0, 1].
    Imagem: fração do comprimento dos segmentos detectados a <= score_tol de alguma reta
    do modelo projetada. Modelo: fração do comprimento projetado sobre o gramado que cai
    numa marca (cada ponto do modelo pesa o comprimento até o vizinho). IoU: campo
    projetado × gramado. Um campo encolhido no meio do quadro tem IoU baixo."""
    tol = P["score_tol_frac"] * ev.h
    iou = field_iou(H, ev)
    g = [project_segments(H, p) for p in LINES_COARSE.values()]
    g = np.concatenate([x for x in g if len(x)]) if any(len(x) for x in g) else np.zeros((0, 2, 2))
    img = float(ev.pw[point_segment_distance(ev.pts, g) <= tol].sum() / ev.pw.sum()) if len(ev.pts) and len(g) else 0.0
    uv, front = project(H, MODEL)
    wgt = np.minimum(np.linalg.norm(uv[MODEL_NEXT] - uv, axis=1), 0.05 * ev.h)
    ok = front & (uv[:, 0] >= 0) & (uv[:, 0] <= ev.w - 1) & (uv[:, 1] >= 0) & (uv[:, 1] <= ev.h - 1)
    u, v = np.round(uv[ok, 0]).astype(int), np.round(uv[ok, 1]).astype(int)
    in_grass = ev.grass[v, u]
    sup = (ev.dist[v, u] <= tol) & in_grass
    total = (wgt[ok] * in_grass).sum()
    mod = float((wgt[ok] * sup).sum() / total) if total > 0 else 0.0
    return img, mod, iou, img + mod + iou


def _sample(s, step):
    n = max(2, int(np.ceil(np.hypot(s[2] - s[0], s[3] - s[1]) / step)) + 1)
    return s[:2] + np.linspace(0, 1, n)[:, None] * (s[2:] - s[:2])


def classify(segs, H, h, P=A):
    """Classe reta de cada segmento pela H: a linha do modelo projetada com a menor
    distância mediana dos pontos do segmento, se <= band_frac·h; senão None."""
    proj = {k: project_segments(H, POLYLINES[k]) for k in LINE_EQ}
    out = []
    for s in segs:
        p = _sample(s, P["seg_step_px"])
        d = {k: np.median(point_segment_distance(p, g)) for k, g in proj.items() if len(g)}
        k = min(d, key=d.get) if d else None
        out.append(k if k is not None and d[k] <= P["band_frac"] * h else None)
    return out


def guided_points(H, marks, classes, P=A):
    """Classe -> pixels da máscara (imagem) a <= band_frac·h da polilinha da classe
    projetada por H, subamostrados para no máximo `guided_max_pts`."""
    h = marks.shape[0]
    t = 2 * int(round(P["band_frac"] * h)) + 1
    out = {}
    for k in classes:
        g = project_segments(H, POLYLINES[k])
        if not len(g):
            continue
        canvas = np.zeros(marks.shape, np.uint8)
        cv2.polylines(canvas, list(np.clip(g, -1e6, 1e6).astype(np.int32)), False, 1, t)
        v, u = np.nonzero(canvas.astype(bool) & marks)
        if len(u) >= 2:
            sel = np.linspace(0, len(u) - 1, min(len(u), P["guided_max_pts"])).astype(int)
            out[k] = np.stack([u[sel], v[sel]], 1).astype(float)
    return out


CIRCLES = [k for k in POLYLINES if k not in LINE_EQ]


def accept(terms, P=A):
    """Portão final: a H explica uma fração mínima das marcas (termo da imagem) e o campo
    projetado cobre o gramado (IoU). Barra H autoconsistente sobre as marcas erradas."""
    return terms[0] >= P["gate_img"] and terms[2] >= P["gate_iou"]


def estimate(marks, grass, segs, refine="segments", P=A):
    """Pipeline mínimo: hipóteses -> poda pelo IoU com o gramado -> verificação ->
    (refinamento) -> portão. `segs` sem as cordas marcadas. refine: None (só H₀),
    "segments" (pontos dos segmentos classificados + círculos guiados) ou "guided"
    (pixels da máscara em volta de todas as linhas). Devolve (H ou None, info)."""
    h, w = marks.shape
    size = (w, h)
    Hs, tried = hypotheses(segs, size, P) if len(segs) >= 4 else ([], 0)
    info = dict(hipoteses=tried, validas=len(Hs), ok=False)
    if not Hs:
        return None, info
    ev = Evidence(marks, grass, segs, P)
    Hs = [H for H in Hs if field_iou(H, ev) >= P["iou_prune"]]
    info["podadas"] = len(Hs)
    if not Hs:
        return None, info
    scores = [verify(H, ev, P)[3] for H in Hs]
    H = Hs[int(np.argmax(scores))]
    info["score"] = max(scores)
    fit_ok, lines_uv = True, {}
    if refine is not None:
        fit = None
        for _ in range(P["refine_iters"]):
            if refine == "segments":
                cls = classify(segs, H, h, P)
                lines_uv = {}
                for sg, k in zip(segs, cls):
                    if k:
                        lines_uv[k] = np.concatenate([lines_uv.get(k, np.zeros((0, 2))), _sample(sg, P["seg_step_px"])])
                lines_uv.update(guided_points(H, marks, CIRCLES, P))
            else:
                lines_uv = guided_points(H, marks, list(POLYLINES), P)
            fit = fit_point_line(H, lines_uv, size)
            if fit.H is None:
                break
            H = fit.H
        fit_ok = bool(fit is not None and fit.ok)
        info["resid_px"] = fit.resid_px if fit else np.nan
    terms = verify(H, ev, P)
    info.update(img=terms[0], mod=terms[1], iou=terms[2], fit_ok=fit_ok, ok=fit_ok and accept(terms, P))
    return (H if info["ok"] else None), info
