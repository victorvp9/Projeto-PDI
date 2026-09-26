"""Métricas de registro (docs/01-metodo.md, Etapa 9). Homografias campo -> imagem.

Protocolo do AuxFlow (seção 4.2) para IoU, NPE e RE; LocSim contra o `bbox_pitch`;
acurácia contra as linhas anotadas com a contagem do código do SN-Calib
(`evaluate_camera.py`). Escolhas não ditas pelos artigos em docs/decisoes.md.
"""
import cv2
import numpy as np

from src.config import CFG
from src.geometry import point_segment_distance, project
from src.pitch_model import CORNERS, HL, HW, POLYLINES
from src.render import pitch_mask

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
        table[label] = t
    return table
