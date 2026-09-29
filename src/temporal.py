"""Etapa 8 (docs/01-metodo.md): consistência temporal sobre a série do detector.

Série do detector em todos os frames (cache por clipe) e 6a, Savitzky–Golay sobre a
série de homografias (campo -> imagem), em duas representações: as entradas da
matriz (H[2,2] = 1) e quatro pontos fixos da imagem levados ao campo, com a H
reestimada deles.
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.signal import savgol_filter

from src.config import CFG, ROOT, path
from src.io import gsr

T = CFG["temporal"]
SERIES_KEYS = ("ok", "img", "mod", "iou", "margem")


def _series_key():
    """Hash do config e do código de que a série do detector depende."""
    h = hashlib.sha1(json.dumps({k: CFG[k] for k in ("segment", "lines", "assign", "detector", "fit")}, sort_keys=True).encode())
    for f in ("segment.py", "lines.py", "conics.py", "assign.py", "homography.py", "geometry.py", "render.py"):
        h.update((ROOT / "src" / f).read_bytes())
    return h.hexdigest()


def _series_path(clip):
    return path("outputs") / "cache" / "detector" / clip.parent.name / f"{clip.name}.npz"


def series_chunk(args):
    """Detector (Etapas 1-7) nos frames [i0, i1) de um clipe do GSR."""
    from src.assign import detect_frame
    clip, i0, i1 = args
    cv2.setNumThreads(1)
    out = []
    for s in gsr.load_clip(clip, fit="none")[i0:i1]:
        H, info = next(iter(detect_frame(s.image, "gsr").values()))
        out.append((s.frame_idx, np.full((3, 3), np.nan) if H is None else H,
                    [float(info.get(k, np.nan)) if info.get(k) is not None else np.nan for k in SERIES_KEYS]))
    return clip, out


def build_series(pool, clips):
    """Série do detector em todos os frames de cada clipe, em cache
    (outputs/cache/detector/<split>/<clipe>.npz); refeita se o config ou o código mudar."""
    key = _series_key()
    todo = [c for c in clips if not (_series_path(c).exists() and str(np.load(_series_path(c))["key"]) == key)]
    n = T["series_chunk"]
    chunks = [(c, i, i + n) for c in todo for i in range(0, len(list((c / "img1").glob("*.jpg"))), n)]
    acc = {}
    with pool() as ex:
        for clip, out in ex.map(series_chunk, chunks):
            acc.setdefault(clip, []).extend(out)
    for clip, out in acc.items():
        out.sort(key=lambda r: r[0])
        p = _series_path(clip)
        p.parent.mkdir(parents=True, exist_ok=True)
        info = np.array([r[2] for r in out])
        np.savez_compressed(p, key=key, frames=np.array([r[0] for r in out]), H=np.array([r[1] for r in out]),
                            **{k: info[:, j] for j, k in enumerate(SERIES_KEYS)})
    return {c: dict(np.load(_series_path(c))) for c in clips}


# ======================= 6a: Savitzky–Golay =======================
def _runs(valid, max_gap):
    """Trechos [a, b] da série: frames válidos separados por lacunas de até max_gap frames."""
    idx = np.nonzero(valid)[0]
    if not len(idx):
        return []
    cut = np.nonzero(np.diff(idx) > max_gap + 1)[0]
    starts, ends = np.r_[idx[0], idx[cut + 1]], np.r_[idx[cut], idx[-1]]
    return list(zip(starts, ends))


def smooth_series(X, max_gap=None, window=None, poly=None):
    """Série (N, D) com linhas NaN nas falhas: em cada trecho (lacunas <= max_gap),
    lacunas por interpolação linear e Savitzky–Golay (janela reduzida ao maior ímpar <=
    tamanho do trecho). Frames fora dos trechos continuam NaN."""
    max_gap = T["max_gap"] if max_gap is None else max_gap
    window, poly = window or T["sg_window"], T["sg_poly"] if poly is None else poly
    out = np.full_like(X, np.nan)
    valid = np.isfinite(X).all(1)
    for a, b in _runs(valid, max_gap):
        t = np.arange(a, b + 1)
        ok = valid[a:b + 1]
        seg = np.stack([np.interp(t, t[ok], X[a:b + 1][ok, j]) for j in range(X.shape[1])], 1)
        w = min(window, len(t) if len(t) % 2 else len(t) - 1)
        out[a:b + 1] = savgol_filter(seg, w, min(poly, w - 1), axis=0) if w > poly + 1 else seg
    return out


def to_matrix_rep(Hs):
    """H (N,3,3) -> 9 entradas com H[2,2] = 1 (NaN onde não há H)."""
    return (Hs / Hs[:, 2:3, 2:3]).reshape(len(Hs), 9)


def from_matrix_rep(X):
    return X.reshape(-1, 3, 3)


def _img_points(size):
    w, h = size
    fu, fv = T["points_u"], T["points_v"]
    return np.array([[w * u, h * v] for v in fv for u in fu], np.float32)


def to_points_rep(Hs, size):
    """H (N,3,3) -> campo (m) dos 4 pontos fixos da imagem (N, 8), NaN onde não há H
    ou um ponto cai atrás da câmera."""
    P = np.c_[_img_points(size), np.ones(4)]
    out = np.full((len(Hs), 8), np.nan)
    for i, H in enumerate(Hs):
        if np.isfinite(H).all():
            q = P @ np.linalg.inv(H).T
            front = (np.c_[q[:, :2] / q[:, 2:], np.ones(4)] @ H[2]) * np.sign(H[2, 2]) > 0
            if front.all():
                out[i] = (q[:, :2] / q[:, 2:]).ravel()
    return out


def from_points_rep(X, size):
    img = _img_points(size)
    out = np.full((len(X), 3, 3), np.nan)
    for i, x in enumerate(X):
        if np.isfinite(x).all():
            out[i] = cv2.getPerspectiveTransform(x.reshape(4, 2).astype(np.float32), img).astype(float)
    return out


def smooth_homographies(Hs, size, rep="matrix", **kw):
    """Savitzky–Golay na série de homografias (N,3,3; NaN = falha) na representação
    `rep` ("matrix" ou "points")."""
    if rep == "matrix":
        return from_matrix_rep(smooth_series(to_matrix_rep(Hs), **kw))
    return from_points_rep(smooth_series(to_points_rep(Hs, size), **kw), size)


def jitter(Hs, size):
    """Tremor da série: mediana, por frame, da segunda diferença (px) da grade do campo
    projetada, nos frames com H no frame e nos dois vizinhos, e só nos pontos dentro da
    imagem nos três. Medido na série estimada, nunca contra a H_gt."""
    from src.geometry import project
    X, Y = np.meshgrid(np.arange(-50, 51, 5.0), np.arange(-32, 33, 4.0))
    grid = np.c_[X.ravel(), Y.ravel()]
    w, h = size
    uv = np.full((len(Hs), len(grid), 2), np.nan)
    for i, H in enumerate(Hs):
        if np.isfinite(H).all():
            p, front = project(H, grid)
            inside = front & (p[:, 0] >= 0) & (p[:, 0] < w) & (p[:, 1] >= 0) & (p[:, 1] < h)
            uv[i, inside] = p[inside]
    d2 = np.linalg.norm(uv[2:] - 2 * uv[1:-1] + uv[:-2], axis=2)
    per_frame = np.array([np.nanmedian(r) if np.isfinite(r).any() else np.nan for r in d2])
    return per_frame


VARIANTS_6A = {  # nome: (representação, lacuna máxima preenchida) ; None = detector sozinho
    "detector": None,
    "SG matriz": ("matrix", None),
    "SG pontos": ("points", None),
    "SG matriz, sem preencher": ("matrix", 0),
    "SG pontos, sem preencher": ("points", 0),
}


def _eval_clip_6a(clip):
    """Métricas por frame (todos os frames) e tremor de cada série do 6a num clipe."""
    from src.evaluate import frame_metrics
    cv2.setNumThreads(1)
    ser = dict(np.load(_series_path(clip)))
    samples = gsr.load_clip(clip)
    assert [s.frame_idx for s in samples] == list(ser["frames"])
    size = samples[0].size
    game = gsr.game_id(clip)
    rows, jit = [], {}
    for name, v in VARIANTS_6A.items():
        Hs = ser["H"] if v is None else smooth_homographies(ser["H"], size, v[0], max_gap=v[1])
        jit[name] = jitter(Hs, size)
        for s, H in zip(samples, Hs):
            rows.append(dict(**frame_metrics(H if np.isfinite(H).all() else None, s), variante=name, jogo=game,
                             n_pessoas=0 if s.persons_XY is None else len(s.persons_XY)))
    return rows, jit


def evaluate_6a(pool, clips):
    """Tabela do 6a nos clipes (séries em cache): cobertura, NPE, IoU_whole, LocSim
    penalizado e tremor, por série."""
    from src.evaluate import summarize
    with pool() as ex:
        res = list(ex.map(_eval_clip_6a, clips))
    rows = [r for rs, _ in res for r in rs]
    print(f"{len(clips)} clipes, {len(rows) // len(VARIANTS_6A)} frames")
    print("série                        | cobertura | NPE med  média  | IoU_whole med | LocSim@5 pen | mAP pen | tremor med (px) p90")
    out = {}
    for name in VARIANTS_6A:
        t = summarize([r for r in rows if r["variante"] == name])["todos"]
        j = np.concatenate([jj[name] for _, jj in res])
        out[name] = (t, j)
        print(f"{name:28} | {t['cobertura']:.3f}     | {t['npe'][1]:.4f} {t['npe'][0]:.3f} | {t['iou_whole'][1]:.3f}         | "
              f"{t.get('locsim@5 penalizado', np.nan):.3f}        | {t.get('mAP-locsim penalizado', np.nan):.3f}   | {np.nanmedian(j):.2f} {np.nanpercentile(j, 90):.2f}")
    return out
