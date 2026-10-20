"""Taxa de inversão de visibilidade (docs/01-metodo.md, Fatia 7): o campo de visão do
frame levado ao gramado (campo, m) com shapely, comparado entre a H de gabarito e a
estimada, nos jogadores reais do GSR (unilateral) e numa grade do campo (bilateral).
"""
import cv2
import numpy as np
import shapely
from shapely.geometry import Polygon, box

from src_v2.config import CFG
from src_v2.pitch_model import HL, HW, POLYLINES

V = CFG["visibility"]
_EXTENT = box(-HL - V["margin_m"], -HW - V["margin_m"], HL + V["margin_m"], HW + V["margin_m"])


def _grid():
    """Grade de pontos de teste no campo (m), passo `grid_m`, só dentro do gramado."""
    X, Y = np.meshgrid(np.arange(-HL, HL + 1e-9, V["grid_m"]), np.arange(-HW, HW + 1e-9, V["grid_m"]))
    return np.c_[X.ravel(), Y.ravel()]


GRID = _grid()


def fov_polygon(H, size):
    """Polígono (campo, m) da região do gramado vista pelo frame de tamanho (w, h), com H
    campo -> imagem. O retângulo da imagem é recortado no semiplano à frente da câmera
    (com folga `horizon_rel` do horizonte) e os vértices vão ao campo por H⁻¹: desse lado
    do horizonte a homografia leva retas em retas, então o polígono é exato. Recortado no
    campo mais `margin_m`; vazio se nada da imagem cai à frente da câmera ou se H é None."""
    if H is None:
        return Polygon()
    w, h = size
    Hi = np.linalg.inv(H)
    rect = np.array([[0, 0], [w, 0], [w, h], [0, h]], float)
    s = (np.c_[rect, np.ones(4)] @ Hi[2]) * np.sign(H[2, 2])     # > 0: raio encontra o gramado à frente
    eps = V["horizon_rel"] * np.abs(s).max()
    pts = []
    for i in range(4):                                           # Sutherland–Hodgman contra s > eps
        j = (i + 1) % 4
        if s[i] > eps:
            pts.append(rect[i])
        if (s[i] > eps) != (s[j] > eps):
            pts.append(rect[i] + (eps - s[i]) / (s[j] - s[i]) * (rect[j] - rect[i]))
    if len(pts) < 3:
        return Polygon()
    q = np.c_[pts, np.ones(len(pts))] @ Hi.T
    return shapely.make_valid(Polygon(q[:, :2] / q[:, 2:])).intersection(_EXTENT)


def frame_visibility(H_est, H_gt, size, persons_XY):
    """Contagens de um frame: jogadores (campo, m) dentro do campo de visão do gabarito e
    da estimativa, e a grade do campo. Sem H estimada, o campo de visão estimado é vazio
    (versão penalizada: todo jogador visível conta como invertido)."""
    gt, est = fov_polygon(H_gt, size), fov_polygon(H_est, size)
    P = np.asarray(persons_XY, float).reshape(-1, 2)
    pg, pe = shapely.contains_xy(gt, P[:, 0], P[:, 1]), shapely.contains_xy(est, P[:, 0], P[:, 1])
    gg, ge = shapely.contains_xy(gt, GRID[:, 0], GRID[:, 1]), shapely.contains_xy(est, GRID[:, 0], GRID[:, 1])
    return dict(vis_gt=int(pg.sum()), vis_est=int(pe.sum()), sai=int((pg & ~pe).sum()), entra=int((~pg & pe).sum()),
                grade_diff=int((gg != ge).sum()), grade_uniao=int((gg | ge).sum()), fov_gt=gt, fov_est=est)


def summarize_visibility(rows):
    """Taxas de uma lista de frames (frame_visibility + has_pred): jogadores (principal,
    unilateral: visíveis no gabarito dados como fora), grade (fração em desacordo na
    união dos dois campos de visão) e o indicador na linha do Bassek (frames em que o
    registro deixa 0 jogadores visíveis com >= 1 no gabarito), penalizada e só cobertos."""
    out = {}
    for label, rs in (("penalizada", rows), ("só cobertos", [r for r in rows if r["has_pred"]])):
        n = sum(r["vis_gt"] for r in rs)
        u = sum(r["grade_uniao"] for r in rs)
        zero = [r for r in rs if r["vis_gt"] >= 1]
        out[label] = dict(jogadores=sum(r["sai"] for r in rs) / n if n else np.nan,
                          grade=sum(r["grade_diff"] for r in rs) / u if u else np.nan,
                          zero_visiveis=np.mean([r["vis_est"] == 0 for r in zero]) if zero else np.nan,
                          frames=len(rs))
    return out


def debug_top(frame_vis, persons_XY, path_out):
    """Depuração: vista de cima do campo com as linhas, o campo de visão do gabarito
    (verde) e o estimado (vermelho), e os jogadores (branco: visíveis nos dois; vermelho:
    visíveis no gabarito e dados como fora; azul: o contrário)."""
    ppm, m = V["debug_px_per_m"], V["margin_m"]
    to = lambda XY: np.round((np.asarray(XY) + [HL + m, HW + m]) * ppm).astype(np.int32)
    img = np.full((int(2 * (HW + m) * ppm), int(2 * (HL + m) * ppm), 3), (40, 90, 40), np.uint8)
    for poly in POLYLINES.values():
        cv2.polylines(img, [to(poly)], False, (200, 200, 200), 1, cv2.LINE_AA)
    for fov, color in ((frame_vis["fov_gt"], (0, 220, 0)), (frame_vis["fov_est"], (0, 0, 230))):
        for g in getattr(fov, "geoms", [fov]):
            if isinstance(g, Polygon) and not g.is_empty:
                cv2.polylines(img, [to(np.array(g.exterior.coords))], True, color, 2, cv2.LINE_AA)
    gt, est = frame_vis["fov_gt"], frame_vis["fov_est"]
    for X, Y in np.asarray(persons_XY, float).reshape(-1, 2):
        a, b = gt.contains(shapely.Point(X, Y)), est.contains(shapely.Point(X, Y))
        color = (255, 255, 255) if a and b else (0, 0, 255) if a else (255, 0, 0) if b else (120, 120, 120)
        cv2.circle(img, tuple(int(c) for c in to([X, Y])), 4, color, -1)
    cv2.imwrite(str(path_out), img)
