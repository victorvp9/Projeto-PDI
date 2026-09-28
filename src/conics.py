"""Etapa 4 (docs/01-metodo.md): elipses — o círculo central e os arcos das grandes
áreas. Espaço imagem (px); tamanhos em fração da altura, parâmetros em CFG["lines"].

Ordem (decisão de Victor): as elipses são ajustadas sobre a máscara inteira, sem
tirar os pixels das cordas; depois, os segmentos de reta que são cordas de uma
elipse aceita ficam marcados com o id dela (uma corda que sobra vira reta falsa na
Fatia 5, mas apagá-la seria irreversível se a elipse for falsa).
Uma elipse é E = (cx, cy, A, B, θ): centro, semieixos A >= B e ângulo do eixo maior.
"""
import cv2
import numpy as np

from src.config import CFG
from src.lines import hough


def conic_ellipse(pts):
    """Elipse E pela cônica algébrica de mínimos quadrados (pontos normalizados), ou
    None se a cônica não for uma elipse real."""
    m, s = pts.mean(0), pts.std() + 1e-9
    x, y = ((pts - m) / s).T
    a, b, c, d, e, f = np.linalg.svd(np.stack([x * x, x * y, y * y, x, y, np.ones_like(x)], 1))[2][-1]
    if b * b - 4 * a * c >= 0:
        return None
    x0, y0 = np.linalg.solve([[2 * a, b], [b, 2 * c]], [-d, -e])
    f0 = a * x0 * x0 + b * x0 * y0 + c * y0 * y0 + d * x0 + e * y0 + f
    lam, vec = np.linalg.eigh([[a, b / 2], [b / 2, c]])
    ax2 = -f0 / lam
    if (ax2 <= 0).any():
        return None
    ax = np.sqrt(ax2) * s
    i = int(np.argmax(ax))
    return np.array([x0 * s + m[0], y0 * s + m[1], ax[i], ax[1 - i], np.arctan2(vec[1, i], vec[0, i])])


def from_cv(box):
    """RotatedRect do cv2.fitEllipse -> E."""
    (cx, cy), (w, h), ang = box
    t = np.deg2rad(ang)
    return np.array([cx, cy, w / 2, h / 2, t]) if w >= h else np.array([cx, cy, h / 2, w / 2, t + np.pi / 2])


def ellipse_points(E, step=1.0):
    """Pontos da elipse a cada ~`step` px (perímetro de Ramanujan)."""
    cx, cy, A, B, t = E
    n = int(min(np.ceil(np.pi * (3 * (A + B) - np.sqrt((3 * A + B) * (A + 3 * B))) / step), 20000))
    s = np.linspace(0, 2 * np.pi, max(n, 8), endpoint=False)
    x, y = A * np.cos(s), B * np.sin(s)
    return np.stack([cx + x * np.cos(t) - y * np.sin(t), cy + x * np.sin(t) + y * np.cos(t)], 1)


def _inside(pts, shape):
    h, w = shape
    return (pts[:, 0] >= 0) & (pts[:, 0] <= w - 1) & (pts[:, 1] >= 0) & (pts[:, 1] <= h - 1)


def ellipse_distance(E, pts):
    """Distância aproximada (Sampson, px) de pontos da imagem (N, 2) à elipse."""
    cx, cy, A, B, t = E
    dx, dy = pts[:, 0] - cx, pts[:, 1] - cy
    qx, qy = np.cos(t) * dx + np.sin(t) * dy, -np.sin(t) * dx + np.cos(t) * dy
    return np.abs((qx / A) ** 2 + (qy / B) ** 2 - 1) / np.maximum(2 * np.hypot(qx / A ** 2, qy / B ** 2), 1e-12)


def ellipse_inside(E, pts):
    """Pontos (N, 2) dentro da elipse (bool)."""
    cx, cy, A, B, t = E
    dx, dy = pts[:, 0] - cx, pts[:, 1] - cy
    qx, qy = np.cos(t) * dx + np.sin(t) * dy, -np.sin(t) * dx + np.cos(t) * dy
    return (qx / A) ** 2 + (qy / B) ** 2 <= 1


def support(E, dist_marks, tol):
    """(comprimento apoiado em px, fração apoiada) do perímetro dentro da imagem:
    pontos a <= tol de algum pixel da máscara."""
    p = ellipse_points(E)
    p = p[_inside(p, dist_marks.shape)]
    if not len(p):
        return 0.0, 0.0
    ok = dist_marks[np.round(p[:, 1]).astype(int), np.round(p[:, 0]).astype(int)] <= tol
    return float(ok.sum()), float(ok.mean())


def _seg_points(segs):
    n = np.ceil(np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])).astype(int) + 2
    sid = np.repeat(np.arange(len(segs)), n)
    t = np.concatenate([np.linspace(0, 1, k) for k in n])
    return segs[sid, :2] + t[:, None] * (segs[sid, 2:] - segs[sid, :2]), sid


def chords(segs, E, tol, pts=None):
    """Segmentos (bool) com mais de `chord_min` dos pontos a <= tol da elipse."""
    if not len(segs):
        return np.zeros(0, bool)
    p, sid = pts if pts is not None else _seg_points(segs)
    ok = ellipse_distance(E, p) <= tol
    return np.bincount(sid, ok, len(segs)) / np.bincount(sid, minlength=len(segs)) > CFG["lines"]["chord_min"]


def chord_fan(segs, mask):
    """Leque de direções (graus, módulo 180) das cordas: o menor arco que contém todas."""
    ang = np.sort(np.degrees(np.arctan2(segs[mask, 3] - segs[mask, 1], segs[mask, 2] - segs[mask, 0])) % 180)
    if len(ang) < 2:
        return 0.0
    gaps = np.diff(np.r_[ang, ang[0] + 180])
    return float(180 - gaps.max())


def dist_to_ellipse(E, shape):
    """Mapa de distância (px) à elipse desenhada com 1 px."""
    canvas = np.full(shape, 255, np.uint8)
    cv2.polylines(canvas, [np.round(ellipse_points(E)).astype(np.int32)], True, 0, 1)
    return cv2.distanceTransform(canvas, cv2.DIST_L2, 5)


def _plausible(E, h, P):
    return E is not None and E[3] >= P["ellipse_b_min_frac"] * h and E[2] <= P["ellipse_a_max_frac"] * h \
        and E[2] / E[3] <= P["ellipse_ratio_max"]


def _run(ok):
    """Índices (início, fim) da maior sequência circular de True em `ok`, aceitando
    buracos de até 5% do perímetro (a máscara falha sob jogadores)."""
    n = len(ok)
    idx = np.nonzero(ok)[0]
    if len(idx) < 2:
        return None
    gaps = np.diff(np.r_[idx, idx[0] + n])
    big = np.nonzero(gaps > max(1, 0.05 * n))[0]
    if not len(big):
        return idx[0], idx[0] + n - 1
    starts = (big + 1) % len(idx)
    lens = [(idx[big[(k + 1) % len(big)]] - idx[st]) % n for k, st in enumerate(starts)]
    k = int(np.argmax(lens))
    return idx[starts[k]], idx[starts[k]] + lens[k]


def _line_dist(p, seg):
    a, b = seg[:2], seg[2:]
    d = (b - a) / max(np.linalg.norm(b - a), 1e-9)
    return np.abs((p - a) @ np.array([-d[1], d[0]]))


def anchored(E, lines, dist_marks, tol, P):
    """Restrição geométrica (decisão de Victor), com os segmentos de reta detectados que
    não são cordas de E. Círculo central: uma reta cruza E perto do centro (ângulo com o
    eixo maior >= `anchor_cross_deg`, distância ao centro <= `anchor_center_b`·B).
    Arco da grande área: as duas pontas do trecho apoiado a <= `anchor_end_b`·B de uma
    mesma reta quase paralela ao eixo maior (<= `anchor_parallel_deg`), e o arco se
    afastando dela >= `anchor_bulge_b`·B. Limites folgados sobre o oráculo do GSR train."""
    if not len(lines):
        return False
    lines = lines[~chords(lines, E, tol)]
    major = np.array([np.cos(E[4]), np.sin(E[4])])
    d = lines[:, 2:] - lines[:, :2]
    ang = np.degrees(np.arccos(np.clip(np.abs(d @ major) / np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-9), 0, 1)))
    round_ = E[2] / E[3] < P["anchor_round_ratio"]           # quase redonda: o eixo maior não tem direção
    for seg, a in zip(lines, ang):
        if (round_ or a >= P["anchor_cross_deg"]) and _line_dist(E[None, :2], seg)[0] <= P["anchor_center_b"] * E[3]:
            return True
    p = ellipse_points(E)
    keep = _inside(p, dist_marks.shape)
    ok = np.zeros(len(p), bool)
    ok[keep] = dist_marks[np.round(p[keep, 1]).astype(int), np.round(p[keep, 0]).astype(int)] <= tol
    run = _run(ok)
    if run is None:
        return False
    arc = p[np.arange(run[0], run[1] + 1) % len(p)]
    for seg, a in zip(lines, ang):
        if a <= P["anchor_parallel_deg"] and _line_dist(arc[[0, -1]], seg).max() <= P["anchor_end_b"] * E[3] \
                and _line_dist(arc, seg).max() >= P["anchor_bulge_b"] * E[3]:
            return True
    return False


def _accept(E, pool, pts, dist, lines, h, P):
    """Apoio na máscara (comprimento >= `ellipse_arc_min_frac`·h, fração >=
    `ellipse_support_min`) e evidência de curvatura: >= `ellipse_chords_min` cordas no
    pool de segmentos, num leque de direções >= `ellipse_turn_min_deg`. Uma elipse
    encostada num canto de retas longas não tem cordas: só um trecho curto de cada
    reta fica perto dela. E a âncora geométrica (`anchored`)."""
    tol = P["ellipse_tol_frac"] * h
    if not _plausible(E, h, P):
        return None
    sup = support(E, dist, tol)
    if sup[0] < P["ellipse_arc_min_frac"] * h or sup[1] < P["ellipse_support_min"]:
        return None
    c = chords(pool, E, tol, pts)
    if c.sum() < P["ellipse_chords_min"] or chord_fan(pool, c) < P["ellipse_turn_min_deg"]:
        return None
    if not anchored(E, lines, dist, tol, P):
        return None
    return sup[0]


def _candidates(segs, h, P):
    """Elipses por trios de segmentos vizinhos (cada um com os `ellipse_neighbors` de
    ponto médio mais próximo, sem sobreposição): extremos e pontos médios dos três."""
    if len(segs) < 3:
        return []
    mid = (segs[:, :2] + segs[:, 2:]) / 2
    dist = np.hypot(*(mid[:, None] - mid[None]).transpose(2, 0, 1))
    # vizinhos que não se sobrepõem (pontos médios a >= meia soma dos comprimentos): o Hough
    # dá segmentos quase iguais na mesma corda (linha grossa), e trios num trecho curto do
    # arco dão um ajuste instável
    length = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
    dist[dist < (length[:, None] + length[None]) / 2] = np.inf
    near = np.argsort(dist, 1)[:, :P["ellipse_neighbors"]]
    seen, out = set(), []
    for i, nb in enumerate(near):
        for j in range(len(nb)):
            for k in range(j + 1, len(nb)):
                if np.isinf(dist[i, nb[j]]) or np.isinf(dist[i, nb[k]]):
                    continue
                tri = tuple(sorted((i, nb[j], nb[k])))
                if tri in seen:
                    continue
                seen.add(tri)
                s = segs[list(tri)]
                E = conic_ellipse(np.concatenate([s[:, :2], s[:, 2:], (s[:, :2] + s[:, 2:]) / 2]))
                if _plausible(E, h, P):
                    out.append(E)
    return out


def detect_ellipses(marks, P=None, lines=None):
    """Máscara de marcações (imagem, bool, sem o filtro de forma) -> elipses aceitas.
    Candidatas por trios de segmentos vizinhos do Hough; vence a de maior perímetro
    apoiado entre as aceitas por `_accept`; reajuste com cv2.fitEllipse nos pixels da
    máscara a <= τ dela (fica o reajuste se também for aceito). Até `ellipse_max`
    elipses; as cordas de cada aceita saem do pool de segmentos. `lines`: as retas da
    Etapa 3 (âncora geométrica); se None, são detectadas aqui."""
    from src.lines import detect_segments
    P = P or CFG["lines"]
    lines = detect_segments(marks, P) if lines is None else lines
    h = marks.shape[0]
    tol = P["ellipse_tol_frac"] * h
    dist = cv2.distanceTransform((~marks).astype(np.uint8), cv2.DIST_L2, 5)
    v, u = np.nonzero(marks)
    mpts = np.stack([u, v], 1).astype(float)
    # pool próprio: cordas curtas cobrem as pontas do círculo achatado; com o comprimento
    # mínimo das retas (0,06·h), o leque das cordas do círculo central fica em ~36° e o dos arcos em ~11°
    f = P["ellipse_hough_min_len_frac"]
    pool, accepted = hough(marks, {**P, "hough_min_len_frac": f, "hough_votes_frac": f}), []
    for _ in range(P["ellipse_max"]):
        if len(pool) < 3:
            break
        pts = _seg_points(pool)
        # uma segunda elipse com o centro dentro de uma aceita é a mesma, reencontrada com as cordas que sobraram
        cands = [E for E in _candidates(pool, h, P) if not any(ellipse_inside(A, E[None, :2])[0] for A in accepted)]
        scored = [(sc, E) for E in cands if (sc := _accept(E, pool, pts, dist, lines, h, P))]
        if not scored:
            break
        E = max(scored, key=lambda x: x[0])[1]
        inl = mpts[ellipse_distance(E, mpts) <= tol]
        if len(inl) >= 5:
            F = from_cv(cv2.fitEllipse(inl.astype(np.float32)))
            if _accept(F, pool, pts, dist, lines, h, P):
                E = F
        accepted.append(E)
        pool = pool[~chords(pool, E, tol, pts)]
    return accepted


def chord_ids(segs, ellipses, h, P=None):
    """Id (índice em `ellipses`) da elipse de que cada segmento é corda, ou -1 (imagem
    de altura h). As cordas são marcadas, não apagadas: 1/3 das elipses é falso, e
    apagar as cordas delas apagaria retas reais (decisão de Victor, docs/decisoes.md)."""
    P = P or CFG["lines"]
    ids = np.full(len(segs), -1)
    for k, E in enumerate(ellipses):
        if len(segs):
            ids[(ids < 0) & chords(segs, E, P["ellipse_tol_frac"] * h)] = k
    return ids


def detect(marks, P=None):
    """Etapas 3 e 4: (segmentos, elipses, id da elipse de que cada segmento é corda ou -1)."""
    from src.lines import detect_segments
    P = P or CFG["lines"]
    segs = detect_segments(marks, P)
    ells = detect_ellipses(marks, P, lines=segs)
    return segs, ells, chord_ids(segs, ells, marks.shape[0], P)
