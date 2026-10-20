"""Métricas de registro (docs/01-metodo.md, Etapa 9). Homografias campo -> imagem.

Protocolo do AuxFlow (seção 4.2) para IoU, NPE e RE; LocSim contra o `bbox_pitch`;
acurácia contra as linhas anotadas com a contagem do código do SN-Calib
(`evaluate_camera.py`). Escolhas não ditas pelos artigos em docs/decisoes.md.
"""
import cv2
import numpy as np

from src_v2.config import CFG
from src_v2.geometry import point_segment_distance, project
from src_v2.pitch_model import CORNERS, HL, HW, POLYLINES
from src_v2.render import axis_mask, pitch_mask

E = CFG["eval"]
_X, _Y = np.meshgrid(np.arange(-HL, HL + 1e-9, E["grid_dx_m"]), np.arange(-HW, HW + 1e-9, E["grid_dy_m"]))
FIELD_GRID = np.c_[_X.ravel(), _Y.ravel()]   # campo, m: 2,5 m em X x 2 m em Y

# vista de cima do IoU_whole: campo + folga, `iou_px_per_m`
_PPM, _M = E["iou_px_per_m"], E["iou_margin_m"]
_T = np.array([[_PPM, 0, (HL + _M) * _PPM], [0, _PPM, (HW + _M) * _PPM], [0, 0, 1.0]])
_TOP = (int(round(2 * (HL + _M) * _PPM)) + 1, int(round(2 * (HW + _M) * _PPM)) + 1)
_FIELD_TOP = np.zeros(_TOP[::-1], np.uint8)
cv2.fillPoly(_FIELD_TOP, [np.round(CORNERS @ _T[:2, :2].T + _T[:2, 2]).astype(np.int32)], 1)


def _apply(H, pts):
    """Aplica H a pontos (N,2) e desomogeneíza, sem teste de lado da câmera."""
    p = np.c_[pts, np.ones(len(pts))] @ H.T
    return p[:, :2] / p[:, 2:]


def _back(H, uv):
    """Imagem (px) -> campo (m) por H⁻¹. `in_front`: o raio do pixel encontra o
    gramado à frente da câmera (mesma convenção de sinal de geometry.project)."""
    p = np.c_[uv, np.ones(len(uv))] @ np.linalg.inv(H).T
    with np.errstate(divide="ignore", invalid="ignore"):
        return p[:, :2] / p[:, 2:], p[:, 2] * np.sign(H[2, 2]) > 0


def _iou(a, b):
    union = (a | b).sum()
    return float((a & b).sum() / union) if union else np.nan


def iou_whole(H_est, H_gt):
    """IoU, na vista de cima, entre o molde e o molde levado por H_est⁻¹·H_gt."""
    M = _T @ np.linalg.inv(H_est) @ H_gt @ np.linalg.inv(_T)
    moved = cv2.warpPerspective(_FIELD_TOP, M, _TOP, flags=cv2.INTER_NEAREST)
    return _iou(_FIELD_TOP.astype(bool), moved.astype(bool))


def iou_part(H_est, H_gt, size):
    """IoU, no espaço da imagem (dentro do quadro), entre o molde reprojetado pela
    H_gt e pela H_est. Rasterizado na escala `iou_part_scale` do quadro."""
    k = E["iou_part_scale"]
    S = np.diag([k, k, 1.0])
    small = (int(round(size[0] * k)), int(round(size[1] * k)))
    return _iou(pitch_mask(S @ H_gt, small), pitch_mask(S @ H_est, small))


def npe_re(H_est, H_gt, size):
    """NPE = média de ‖H_est·X − H_gt·X‖ / altura; RE (m) = média de
    ‖H_est⁻¹(H_gt·X) − X‖. X = grade do campo cuja projeção pela H_gt cai dentro
    do quadro e à frente da câmera (escolha nossa; docs/decisoes.md)."""
    w, h = size
    uv, ok = project(H_gt, FIELD_GRID)
    vis = ok & (uv[:, 0] >= 0) & (uv[:, 0] < w) & (uv[:, 1] >= 0) & (uv[:, 1] < h)
    if not vis.any():
        return np.nan, np.nan
    X, uv = FIELD_GRID[vis], uv[vis]
    npe = np.linalg.norm(_apply(H_est, X) - uv, axis=1).mean() / h
    re = np.linalg.norm(_back(H_est, uv)[0] - X, axis=1).mean()
    return float(npe), float(re)


def locsim_distances(H_est, boxes_uv, persons_XY):
    """Distância (m) entre o centro da base da caixa (imagem) levado ao campo por
    H_est⁻¹ e o `bbox_pitch` (campo). Infinita se o raio não encontra o gramado."""
    base = np.c_[boxes_uv[:, 0] + boxes_uv[:, 2] / 2, boxes_uv[:, 1] + boxes_uv[:, 3]]
    XY, front = _back(H_est, base)
    d = np.linalg.norm(XY - persons_XY, axis=1)
    return np.where(front, d, np.inf)


def locsim(d, tau):
    """Similaridade de localização do GS-HOTA: exp(ln(0,05)·d²/τ²)."""
    return np.exp(np.log(0.05) * np.square(d) / tau ** 2)


def sncalib_accuracy(H_est, lines_uv, size, thresholds):
    """Acurácia contra as linhas anotadas, com a contagem do SN-Calib por classe.

    Em 960x540: classe anotada e projetada no quadro é TP se todos os seus pontos
    estão a menos de t px da polilinha projetada, senão FP; projetada e não
    anotada, FP; anotada e não projetada, FN. Acurácia = TP/(TP+FP+FN).
    Sem espelhamento (decisão de Victor). Traves fora dos dois lados.
    """
    W, Hh = E["sncalib_size"]
    w, h = size
    H = np.diag([W / w, Hh / h, 1.0]) @ H_est
    gt = {k: p / [w, h] * [W - 1, Hh - 1] for k, p in lines_uv.items()}   # como o scale_points deles
    proj = {}
    for k, poly in POLYLINES.items():
        uv, ok = project(H, poly)
        inside = ok & (uv[:, 0] >= 0) & (uv[:, 0] < W) & (uv[:, 1] >= 0) & (uv[:, 1] < Hh)
        if inside.any():
            keep = ok[:-1] & ok[1:] & (inside[:-1] | inside[1:])
            proj[k] = np.stack([uv[:-1][keep], uv[1:][keep]], axis=1)
    both = set(proj) & set(gt)
    n_fp, n_fn = len(set(proj) - set(gt)), len(set(gt) - set(proj))
    dmax = {k: point_segment_distance(gt[k], proj[k]).max() for k in both}
    out = []
    for t in thresholds:
        tp = sum(d < t for d in dmax.values())
        total = len(both) + n_fp + n_fn           # TP + FP(ruins) + FP(sobrando) + FN
        out.append(tp / total if total else 0.0)
    return out


def image_grid_displacement(H_a, H_b, size):
    """Deslocamento mediano (px) ‖H_b·H_a⁻¹·u − u‖ numa grade da imagem, só nos
    pontos que caem no campo, à frente da câmera, segundo H_a."""
    step = E["quality_grid_px"]
    w, h = size
    u, v = np.meshgrid(np.arange(step / 2, w, step), np.arange(step / 2, h, step))
    uv = np.c_[u.ravel(), v.ravel()]
    XY, front = _back(H_a, uv)
    on = front & (np.abs(XY[:, 0]) <= HL) & (np.abs(XY[:, 1]) <= HW)
    if not on.any():
        return np.nan
    return float(np.median(np.linalg.norm(_apply(H_b, XY[on]) - uv[on], axis=1)))


def frame_metrics(H_est, s):
    """Métricas de um frame (Sample) para a predição H_est (campo -> imagem) ou None."""
    row = dict(clip=s.sequence_id, frame=s.frame_idx, image_id=s.image_id,
               has_gt=s.H_gt is not None, dubious=s.dubious, has_pred=H_est is not None,
               has_lines=bool(s.lines_uv))
    if H_est is None:
        return row
    for prefix, H_gt in (("", s.H_gt), ("auxflow_", getattr(s, "H_gt_auxflow", None))):
        if H_gt is not None:     # auxflow_: tabela à parte, "protocolo AuxFlow"
            row[f"{prefix}iou_whole"] = iou_whole(H_est, H_gt)
            row[f"{prefix}iou_part"] = iou_part(H_est, H_gt, s.size)
            row[f"{prefix}npe"], row[f"{prefix}re_m"] = npe_re(H_est, H_gt, s.size)
    if s.lines_uv:
        for t, acc in zip(E["sncalib_thresholds_px"], sncalib_accuracy(H_est, s.lines_uv, s.size, E["sncalib_thresholds_px"])):
            row[f"acc@{t}"] = acc
    if s.persons_XY is not None and len(s.persons_XY):
        row["locsim_d"] = locsim_distances(H_est, s.boxes_uv, s.persons_XY)
    return row


def summarize(rows):
    """Tabela: média e mediana de cada métrica, com e sem os duvidosos."""
    table = {}
    for label, keep in (("todos", lambda r: True), ("sem duvidosos", lambda r: not r["dubious"])):
        rs = [r for r in rows if keep(r)]
        gt = [r for r in rs if r["has_gt"]]
        pred_gt = [r for r in gt if r["has_pred"]]
        t = {"frames": len(rs), "frames com H_gt": len(gt),
             "cobertura": len(pred_gt) / len(gt) if gt else np.nan}
        for m in ("iou_whole", "iou_part", "npe", "re_m"):
            v = np.array([r[m] for r in pred_gt if m in r], float)
            t[m] = (np.nanmean(v), np.nanmedian(v)) if len(v) else (np.nan, np.nan)
        for m in ("iou_whole", "iou_part", "npe", "re_m"):   # protocolo AuxFlow: contra H_gt_auxflow
            v = np.array([r[f"auxflow_{m}"] for r in rs if f"auxflow_{m}" in r], float)
            if len(v):
                t[f"auxflow {m}"] = (np.nanmean(v), np.nanmedian(v))
        lines = [r for r in rs if r["has_lines"]]
        compl = np.mean([r["has_pred"] for r in lines]) if lines else np.nan
        for th in E["sncalib_thresholds_px"]:
            v = [r[f"acc@{th}"] for r in lines if r["has_pred"]]
            t[f"acc@{th}"] = compl * np.mean(v) if v else np.nan    # completude x acurácia média
        d = np.concatenate([r["locsim_d"] for r in rs if "locsim_d" in r] or [np.array([])])
        if len(d):
            t["locsim@5"] = (locsim(d, 5).mean(), np.median(locsim(d, 5)))
            t["locsim@2"] = (locsim(d, 2).mean(), np.median(locsim(d, 2)))
            t["mAP-locsim"] = np.mean([locsim(d, tau).mean() for tau in E["locsim_taus_m"]])
            t["locsim dist (m)"] = (np.mean(d[np.isfinite(d)]), np.median(d))
        n_all = sum(r.get("n_pessoas", 0) for r in rs)
        if n_all:                                 # penalizado: pessoa de frame sem H vale 0 (docs/01-metodo.md), inclusive se nenhum frame tem H
            t["locsim@5 penalizado"] = float(locsim(d, 5).sum() / n_all)
            t["mAP-locsim penalizado"] = float(np.mean([locsim(d, tau).sum() / n_all for tau in E["locsim_taus_m"]]))
        table[label] = t
    return table


# ============================ segmentação (Fatia 3) ===========================
ES = CFG["eval_segment"]


def shadow_score(frame_bgr, region, dark_mask=False):
    """Bimodalidade do L* dentro do gramado (imagem, bool): limiar de Otsu separa
    duas classes; devolve (ΔL entre as médias, fração do gramado ocupada pelo maior
    componente conexo da classe escura, idem da classe clara), em fração do gramado.
    Sombra atravessando o campo = ΔL grande, região escura grande e um pedaço
    contínuo de sol; faixas de corte dão ΔL menor; campo todo na sombra dá classe
    clara só em pontos soltos.
    Com dark_mask=True, devolve também a máscara da classe escura (depuração)."""
    from src_v2.segment import green_hue
    frame_lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
    L = frame_lab[:, :, 0]
    # só grama pelo ângulo de matiz (sol e sombra juntos) e croma (sem linhas brancas)
    region = region & green_hue(frame_lab, CFG["shadow"]["hue_deg"], CFG["shadow"]["c_min"], where=region)
    vals = L[region]
    if len(vals) < 100:
        return (np.nan, np.nan, np.nan, None) if dark_mask else (np.nan, np.nan, np.nan)
    t, _ = cv2.threshold(vals.reshape(1, -1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    dark, light = vals[vals <= t], vals[vals > t]
    if not len(dark) or not len(light):
        return (0.0, 0.0, 0.0, None) if dark_mask else (0.0, 0.0, 0.0)
    dark_px = region & (L <= t)

    def biggest(m):
        n, _, stats, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
        return stats[1:, cv2.CC_STAT_AREA].max() / region.sum() if n > 1 else 0.0
    out = (float(light.mean() - dark.mean()), float(biggest(dark_px)), float(biggest(region & (L > t))))
    return (*out, dark_px) if dark_mask else out


def lines_target(H, size, region=None):
    """Alvo das marcações (imagem, bool): polilinhas do modelo desenhadas por H com
    1 px, fora de `border_px` da borda e, se dada, dentro de `region`."""
    t = axis_mask(H, size)
    b = ES["border_px"]
    t[:b], t[-b:], t[:, :b], t[:, -b:] = False, False, False, False
    return t & region if region is not None else t


def _dist_to(mask):
    """Distância (px) de cada pixel ao pixel verdadeiro mais próximo de `mask`."""
    if not mask.any():
        return np.full(mask.shape, np.inf, np.float32)
    return cv2.distanceTransform((~mask).astype(np.uint8), cv2.DIST_L2, 5)


def coverage_precision(pred, target, gammas, width_target=None):
    """Cobertura (eixo de 1 px `target` a <= γ da predição) e precisão (predição a <= γ
    de `width_target`, a linha com a largura projetada; sem ela, do eixo). Contra o
    eixo, a precisão puniria a própria largura da linha (até 8-10 px no GSR)."""
    d_pred = _dist_to(pred)
    d_target = _dist_to(target if width_target is None else width_target)
    out = {}
    for g in gammas:
        out[f"cobertura@{g}"] = float((d_pred[target] <= g).mean()) if target.any() else np.nan
        out[f"precisao@{g}"] = float((d_target[pred] <= g).mean()) if pred.any() else np.nan
    return out


def point_coverage(pred, pts, gamma):
    """Fração dos pontos (imagem, px) a <= γ de algum pixel da predição."""
    if not len(pts):
        return np.nan
    d = _dist_to(pred)
    u = np.clip(np.round(pts[:, 0]).astype(int), 0, pred.shape[1] - 1)
    v = np.clip(np.round(pts[:, 1]).astype(int), 0, pred.shape[0] - 1)
    return float((d[v, u] <= gamma).mean())


def field_grass_and_leak(grass, H_gt, size, step=4):
    """GSR: fração do campo projetado pela H_gt classificada como grama, e vazamento =
    fração da máscara (numa grade de `step` px) a mais de `leak_m` metros fora das
    linhas pela H_gt (ou acima do horizonte)."""
    field = pitch_mask(H_gt, size)
    frac = float((grass & field).sum() / field.sum()) if field.any() else np.nan
    v, u = np.nonzero(grass[::step, ::step])
    if not len(u):
        return frac, np.nan
    XY, front = _back(H_gt, np.c_[u * step, v * step].astype(float))
    out = np.hypot(np.maximum(np.abs(XY[:, 0]) - HL, 0), np.maximum(np.abs(XY[:, 1]) - HW, 0))
    return frac, float(np.mean(~front | (out > ES["leak_m"])))


def is_shadow(dL, f_dark, f_light):
    """Regra do subconjunto com sombra (docs/decisoes.md)."""
    S = CFG["shadow"]
    return bool(dL >= S["dL_min"] and f_dark >= S["f_dark_min"] and f_light >= S["f_light_min"])


def point_widths(H, lines_uv):
    """Largura projetada (px) de uma linha de 0,12 m em cada ponto (imagem) das
    classes: o ponto vai ao campo por H⁻¹ e mede-se |H(X + n·0,06) − H(X − n·0,06)|,
    com n a normal da classe (reta) ou radial (círculo). Só para análise."""
    from src_v2.homography import _CIRCLES, LINE_EQ
    from src_v2.pitch_model import LINE_WIDTH
    out = {}
    for k, p in lines_uv.items():
        XY, _ = _back(H, p)
        if k in LINE_EQ:
            n = np.tile(LINE_EQ[k][:2] / np.hypot(*LINE_EQ[k][:2]), (len(p), 1))
        else:
            n = XY - [_CIRCLES[k][0], 0.0]
            n /= np.linalg.norm(n, axis=1, keepdims=True)
        out[k] = np.linalg.norm(_apply(H, XY + n * LINE_WIDTH / 2) - _apply(H, XY - n * LINE_WIDTH / 2), axis=1)
    return out


# ======================= Etapa 3: segmentos de reta =======================
STRAIGHT = [k for k in POLYLINES if not k.startswith("Circle")]
CIRCLES = [k for k in POLYLINES if k.startswith("Circle")]


def segment_gt(H, size, region=None):
    """Gabarito das retas (imagem), por classe reta com eixo na imagem: mapa de
    distância ao eixo de 1 px inteiro, pixels do eixo visíveis (fora de `border_px`
    e, se dada, dentro de `region`) e se a linha conta como visível (eixo visível >=
    `visible_min_frac`·h). Mais o mapa de distância aos círculos (cordas de arco)."""
    w, h = size
    b = ES["border_px"]
    inner = np.zeros((h, w), bool)
    inner[b:-b, b:-b] = True
    if region is not None:
        inner &= region
    per_class = {}
    for c in STRAIGHT:
        ax = axis_mask(H, size, [c])
        if ax.any():
            v, u = np.nonzero(ax & inner)
            per_class[c] = dict(dist=_dist_to(ax), axis=np.stack([u, v], 1).astype(float),
                                visible=len(u) >= CFG["lines"]["visible_min_frac"] * h)
    return per_class, _dist_to(axis_mask(H, size, CIRCLES))


def _sample(segs):
    """Pontos a cada ~1 px ao longo dos segmentos (imagem) e o índice do segmento."""
    n = np.ceil(np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])).astype(int) + 2
    sid = np.repeat(np.arange(len(segs)), n)
    t = np.concatenate([np.linspace(0, 1, k) for k in n])
    return segs[sid, :2] + t[:, None] * (segs[sid, 2:] - segs[sid, :2]), sid


def segment_counts(segs, gt, tol):
    """Casamento dos segmentos (N, 4) com o gabarito de `segment_gt` a `tol` px: o
    segmento casa com a classe reta em que >= `match_min` dos seus pontos estão a <= tol
    (a de maior fração); sem reta, e com os pontos sobre um círculo, é corda de arco.
    Devolve contagens somáveis entre frames e a classe de cada segmento (None: não casou).
    Precisão = len_match/len_total; recall por comprimento = axis_cov/axis_total;
    recall de linhas = lines_det/lines_vis; fragmentação = segs_match/classes_match."""
    per_class, dist_arc = gt
    out = dict(len_total=0.0, len_match=0.0, len_arc=0.0, axis_total=0, axis_cov=0,
               lines_vis=0, lines_det=0, segs_match=0, classes_match=0)
    cls = [None] * len(segs)
    if len(segs):
        m, names = CFG["lines"]["match_min"], list(per_class)
        pts, sid = _sample(segs)
        h, w = dist_arc.shape
        u = np.clip(np.round(pts[:, 0]).astype(int), 0, w - 1)
        v = np.clip(np.round(pts[:, 1]).astype(int), 0, h - 1)
        npts = np.bincount(sid, minlength=len(segs))
        frac = lambda dist: np.bincount(sid, dist[v, u] <= tol, len(segs)) / npts
        best, best_f = np.full(len(segs), -1), np.zeros(len(segs))
        for k, c in enumerate(names):
            f = frac(per_class[c]["dist"])
            up = (f >= m) & (f > best_f)
            best[up], best_f[up] = k, f[up]
        length = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
        arc = (best < 0) & (frac(dist_arc) >= m)
        out.update(len_total=float(length.sum()), len_match=float(length[best >= 0].sum()),
                   len_arc=float(length[arc].sum()), segs_match=int((best >= 0).sum()),
                   classes_match=len(set(best[best >= 0])))
        cls = [names[k] if k >= 0 else None for k in best]
    for c, g in per_class.items():
        if g["visible"]:
            mine = segs[[i for i, x in enumerate(cls) if x == c]]
            out["lines_vis"] += 1
            out["axis_total"] += len(g["axis"])
            if len(mine):
                out["lines_det"] += 1
                out["axis_cov"] += int((point_segment_distance(g["axis"], mine.reshape(-1, 2, 2)) <= tol).sum())
    return out, cls


# ======================= Etapa 4: elipses =======================
def ellipse_gt(H, size):
    """Por classe de círculo (imagem): pontos da polilinha projetada dentro da imagem e
    se a classe conta como visível (>= metade da polilinha dentro da imagem)."""
    w, h = size
    out = {}
    for c in CIRCLES:
        uv, ok = project(H, POLYLINES[c])
        inside = ok & (uv[:, 0] >= 0) & (uv[:, 0] <= w - 1) & (uv[:, 1] >= 0) & (uv[:, 1] <= h - 1)
        if inside.any():
            out[c] = dict(pts=uv[inside], visible=inside.mean() >= 0.5)
    return out


def ellipse_counts(ellipses, egt, shape, tol):
    """Uma elipse casa com a classe de círculo cujos pontos dentro da imagem têm a menor
    distância mediana a ela, se essa mediana é <= tol (a lente deforma o círculo
    pintado: numa elipse certa, 20% dos pontos podem passar de tol). Também a regra
    dos segmentos (>= `match_min` dos pontos a <= tol), com o sufixo 80. Contagens
    somáveis: detectadas e casadas; visíveis e detectadas, à parte para o círculo
    central e para os arcos das grandes áreas."""
    from src_v2.conics import dist_to_ellipse
    keys = ("det_match", "det_central", "det_arco")
    out = dict(det=len(ellipses), vis_central=0, vis_arco=0, **{k: 0 for k in keys}, **{k + "80": 0 for k in keys})
    matched, matched80 = set(), set()
    for E in ellipses:
        d = dist_to_ellipse(E, shape)
        med, frac = {}, {}
        for c, g in egt.items():
            p = np.round(g["pts"]).astype(int)
            dd = d[p[:, 1], p[:, 0]]
            med[c], frac[c] = float(np.median(dd)), float((dd <= tol).mean())
        if med and min(med.values()) <= tol:
            out["det_match"] += 1
            matched.add(min(med, key=med.get))
        if frac and max(frac.values()) >= CFG["lines"]["match_min"]:
            out["det_match80"] += 1
            matched80.add(max(frac, key=frac.get))
    for c, g in egt.items():
        if g["visible"]:
            k = "central" if c == "Circle central" else "arco"
            out[f"vis_{k}"] += 1
            out[f"det_{k}"] += c in matched
            out[f"det_{k}80"] += c in matched80
    return out
