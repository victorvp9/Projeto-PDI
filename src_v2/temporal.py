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

from src_v2.config import CFG, ROOT, path
from src_v2.io import gsr
import src_v2.assign, src_v2.conics, src_v2.evaluate, src_v2.geometry, src_v2.homography, src_v2.lines, src_v2.render, src_v2.segment  # noqa: E401,E402,F401

# Bytes dos fontes que entram nas chaves, lidos UMA vez, na importação, logo depois de
# carregar os módulos (decisão de Victor, 2026-09-30): um trabalhador que nasça depois de
# uma edição carrega o código novo e os bytes novos, a chave dele diverge da recebida do
# processo principal e a tarefa falha, em vez de gravar com a chave antiga. Os módulos do
# detector e o io/gsr.py não guardam os próprios bytes: editá-los mudaria a série do
# detector (~11 h por partição) e o cache da H_gt.
_KEY_SOURCES = ("segment.py", "lines.py", "conics.py", "assign.py", "homography.py", "geometry.py", "render.py")
_SRC = {f: (ROOT / "src_v2" / f).read_bytes() for f in _KEY_SOURCES + ("temporal.py", "evaluate.py", "io/gsr.py", "pitch_model.py")}

T = CFG["temporal"]
SERIES_KEYS = ("ok", "img", "mod", "iou", "margem")


def _series_key():
    """Hash do config e do código de que a série do detector depende (bytes lidos na
    importação). v2 (achado 3 da revisão de 2026-10-14): entram também a seção `pitch`, o
    `eval.quality_grid_px` (margem de ambiguidade por evaluate.image_grid_displacement) e os
    bytes do evaluate.py e do pitch_model.py."""
    cfg = {k: CFG[k] for k in ("segment", "lines", "assign", "detector", "fit", "pitch")}
    cfg["eval.quality_grid_px"] = CFG["eval"]["quality_grid_px"]
    h = hashlib.sha1(json.dumps(cfg, sort_keys=True).encode())
    for f in _KEY_SOURCES + ("evaluate.py", "pitch_model.py"):
        h.update(_SRC[f])
    return h.hexdigest()


def load_series(clip, key=None):
    """Série do detector de um clipe, só se gravada com a chave do código e do config atuais
    (`key`, padrão `_series_key()`); senão, erro. v2, achado 2 da revisão de 2026-10-14: a
    série era lida sem conferir a chave, e um trecho com falha deixava a série velha valer."""
    p = _series_path(clip)
    if not p.exists():
        raise FileNotFoundError(f"sem a série do detector de {clip.name}: rode --detect-series")
    ser, key = dict(np.load(p)), key or _series_key()
    if str(ser["key"]) != key:
        raise RuntimeError(f"série de {clip.name} gravada com a chave {str(ser['key'])[:12]}, a atual é {key[:12]}: rode --detect-series")
    return ser


def _series_path(clip):
    return path("cache") / "detector" / clip.parent.name / f"{clip.name}.npz"


def series_chunk(args):
    """Detector (Etapas 1-7) nos frames [i0, i1) de um clipe do GSR; confere antes que o
    trabalhador roda o código da chave da rodada."""
    from src_v2.assign import detect_frame
    from src_v2.executor import check_key
    clip, i0, i1, key = args
    check_key(key, _series_key(), "série do detector")
    cv2.setNumThreads(1)
    out = []
    for s in gsr.load_clip(clip, fit="none")[i0:i1]:
        H, info = next(iter(detect_frame(s.image, "gsr").values()))
        out.append((s.frame_idx, np.full((3, 3), np.nan) if H is None else H,
                    [float(info.get(k, np.nan)) if info.get(k) is not None else np.nan for k in SERIES_KEYS]))
    return clip, out


def build_series(pool, clips):
    """Série do detector em todos os frames de cada clipe, em cache
    (outputs/cache/detector/<split>/<clipe>.npz); refeita se o config ou o código mudar.
    Cada clipe é gravado assim que seus trechos terminam: interromper perde só os clipes
    em andamento, e o mesmo comando retoma dos que faltam."""
    import time
    from collections import Counter
    key = _series_key()
    todo = [c for c in clips if not (_series_path(c).exists() and str(np.load(_series_path(c))["key"]) == key)]
    print(f"série do detector: {len(clips) - len(todo)} de {len(clips)} clipes já em cache", flush=True)
    n = T["series_chunk"]
    chunks = [(c, i, i + n) for c in todo for i in range(0, len(list((c / "img1").glob("*.jpg"))), n)]
    chunks = [(c, i0, i1, key) for c, i0, i1 in chunks]
    left, acc, t0 = Counter(c for c, _, _, _ in chunks), {}, time.time()
    with pool() as ex:
        for res in ex.map(series_chunk, chunks):
            if res is None:                               # trecho falhou (manifesto): o clipe fica para a próxima rodada
                continue
            clip, out = res
            acc.setdefault(clip, []).extend(out)
            left[clip] -= 1
            if left[clip]:
                continue
            out = sorted(acc.pop(clip), key=lambda r: r[0])
            p = _series_path(clip)
            p.parent.mkdir(parents=True, exist_ok=True)
            info = np.array([r[2] for r in out])
            np.savez_compressed(p, key=key, frames=np.array([r[0] for r in out]), H=np.array([r[1] for r in out]),
                                **{k: info[:, j] for j, k in enumerate(SERIES_KEYS)})
            done = sum(1 for v in left.values() if v == 0)
            print(f"   {clip.parent.name}/{clip.name} salvo: {done} de {len(todo)}, {(time.time() - t0) / 60:.0f} min", flush=True)
        # cada tarefa recebe uma tupla só, (clipe, i0, i1, chave): o clipe é a[0][0] (incidente da rodada do test, decisoes.md 2026-10-02)
        ex.verify_keys(key, lambda a: str(np.load(_series_path(a[0][0]))["key"]) if _series_path(a[0][0]).exists() else None)
    return {c: load_series(c, key) for c in clips if _series_path(c).exists() and str(np.load(_series_path(c))["key"]) == key}


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


def hampel_outliers(X, half, n_sigma):
    """Frames da série (N, D; NaN = sem H) com alguma coordenada a mais de
    n_sigma·1,4826·MAD da mediana da janela [t-half, t+half], só entre os frames com H;
    janelas com menos de hampel_min_valid frames com H não julgam. O MAD inclui o
    movimento da câmera dentro da janela: janela longa em panorâmica rápida esconde o
    salto (por isso a janela é calibrada)."""
    valid = np.isfinite(X).all(1)
    out = np.zeros(len(X), bool)
    for t in np.nonzero(valid)[0]:
        w = X[max(0, t - half):t + half + 1]
        w = w[np.isfinite(w).all(1)]
        if len(w) < T["hampel_min_valid"]:
            continue
        med = np.median(w, 0)
        out[t] = (np.abs(X[t] - med) > n_sigma * 1.4826 * np.median(np.abs(w - med), 0)).any()
    return out


def hampel_homographies(Hs, size, half, n_sigma):
    """Série de H (campo -> imagem) sem os frames que o Hampel marca, julgados na
    representação por pontos (m no campo): os descartados viram NaN."""
    out = Hs.copy()
    out[hampel_outliers(to_points_rep(Hs, size), half, n_sigma)] = np.nan
    return out


def kalman_series(X, q, r):
    """Kalman de velocidade constante + suavizador RTS, simplificado (NÃO é o BHITK do
    Bassek et al.), na série (N, D; linhas NaN = sem medida). Cada coordenada tem o seu
    filtro [posição, velocidade], com aceleração branca de variância q e medição de
    variância r; a porta de Mahalanobis é conjunta (a medida inteira entra ou sai) e,
    depois de `kalman_reset` rejeições seguidas, o filtro reinicia na medida atual. Em
    cada trecho com lacunas <= max_gap, as lacunas saem da predição; fora dos trechos,
    NaN."""
    Fm = np.array([[1.0, 1.0], [0.0, 1.0]])
    Q = q * np.array([[0.25, 0.5], [0.5, 1.0]])
    out = np.full_like(X, np.nan)
    valid = np.isfinite(X).all(1)
    for a, b in _runs(valid, T["max_gap"]):
        n, D = b - a + 1, X.shape[1]
        xf, Pf = np.zeros((n, D, 2)), np.zeros((n, D, 2, 2))    # filtrado
        xp, Pp = np.zeros((n, D, 2)), np.zeros((n, D, 2, 2))    # previsto
        x, P, misses = np.c_[X[a], np.zeros(D)], np.tile(np.diag([r, T["kalman_v0"]]), (D, 1, 1)), 0
        for i in range(n):
            if i:
                x, P = x @ Fm.T, Fm @ P @ Fm.T + Q
            xp[i], Pp[i] = x, P
            z = X[a + i]
            if np.isfinite(z).all():
                y, S = z - x[:, 0], P[:, 0, 0] + r
                if (y ** 2 / S).sum() <= T["kalman_gate_chi2"]:
                    K = P[:, :, 0] / S[:, None]
                    x = x + K * y[:, None]
                    P = P - K[:, :, None] * P[:, None, 0, :]
                    misses = 0
                else:
                    misses += 1
                    if misses >= T["kalman_reset"]:           # o trecho seguido estava errado: reinicia
                        x, P, misses = np.c_[z, np.zeros(D)], np.tile(np.diag([r, T["kalman_v0"]]), (D, 1, 1)), 0
            xf[i], Pf[i] = x, P
        xs = xf.copy()
        for i in range(n - 2, -1, -1):                        # RTS
            C = Pf[i] @ Fm.T @ np.linalg.inv(Pp[i + 1])
            xs[i] = xf[i] + (C @ (xs[i + 1] - xp[i + 1])[:, :, None])[:, :, 0]
        out[a:b + 1] = xs[:, :, 0]
    return out


def kalman_homographies(Hs, size, q, r):
    """Kalman + RTS (kalman_series) na representação por pontos (m no campo)."""
    return from_points_rep(kalman_series(to_points_rep(Hs, size), q, r), size)


def _stability_grid():
    """Grade de pontos do campo (m) das medidas de estabilidade."""
    dX, dY = T["stability_grid_m"]
    X, Y = np.meshgrid(np.arange(-50, 51, dX), np.arange(-32, 33, dY))
    return np.c_[X.ravel(), Y.ravel()]


def jitter(Hs, size):
    """Tremor da série: mediana, por frame, da segunda diferença (px) da grade do campo
    projetada, nos frames com H no frame e nos dois vizinhos, e só nos pontos dentro da
    imagem nos três. Medido na série estimada, nunca contra a H_gt."""
    from src_v2.geometry import project
    grid = _stability_grid()
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
    from src_v2.evaluate import frame_metrics
    cv2.setNumThreads(1)
    ser = load_series(clip)
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
    from src_v2.evaluate import summarize
    with pool() as ex:
        res = [r for r in ex.map(_eval_clip_6a, clips) if r is not None]
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


# ======================= 6b: detecção de corte =======================
def frame_hist(frame_bgr):
    """Histograma HSV (hist_bins) da imagem reduzida (hist_scale)."""
    f = T["hist_scale"]
    small = cv2.resize(frame_bgr, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    return cv2.calcHist([cv2.cvtColor(small, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, T["hist_bins"], [0, 180, 0, 256, 0, 256]).ravel()


def hist_distance(a, b):
    return float(cv2.compareHist(a, b, cv2.HISTCMP_BHATTACHARYYA))


def _clip_hists(clip):
    cv2.setNumThreads(1)
    return [frame_hist(s.image) for s in gsr.load_clip(clip, fit="none")]


def calibrate_cuts(pool, clips):
    """Distância de histograma entre frames consecutivos dentro dos clipes (negativos) e
    em cortes sintéticos, último frame de um clipe x primeiro de outro, para todos os
    pares ordenados (positivos; mesmo jogo à parte). Tabela e outputs/cortes_sinteticos.csv."""
    from src_v2.run import _write_csv
    with pool() as ex:
        hists = {c: h for c, h in zip(clips, ex.map(_clip_hists, clips)) if h is not None}
    games = {c: gsr.game_id(c) for c in clips}
    neg = [(c.name, i + 1, hist_distance(h[i], h[i + 1])) for c, h in hists.items() for i in range(len(h) - 1)]
    pos = [(a.name, b.name, games[a] == games[b], hist_distance(hists[a][-1], hists[b][0]))
           for a in clips for b in clips if a != b]
    dn = np.array([d for *_, d in neg])
    dp = np.array([d for *_, d in pos])
    same = np.array([s_ for _, _, s_, _ in pos])
    print(f"negativos (frames consecutivos, {len(clips)} clipes): {len(dn)}; p50 {np.median(dn):.3f} p99 {np.percentile(dn, 99):.3f} p99,9 {np.percentile(dn, 99.9):.3f} máx {dn.max():.3f}")
    print(f"cortes sintéticos: {len(dp)} ({same.sum()} do mesmo jogo); mín {dp.min():.3f} p5 {np.percentile(dp, 5):.3f} mediana {np.median(dp):.3f}; "
          f"mesmo jogo: mín {dp[same].min():.3f} mediana {np.median(dp[same]):.3f}; jogos diferentes: mín {dp[~same].min():.3f}")
    print("   maiores negativos:", [(c, f, round(d, 3)) for c, f, d in sorted(neg, key=lambda x: -x[2])[:8]])
    for t in sorted({round(dn.max() + 1e-3, 3), 0.2, 0.3, 0.4, 0.5}):
        print(f"   limiar {t:.3f}: falsos positivos dentro dos clipes {int((dn > t).sum())}; recall dos cortes {np.mean(dp > t):.3f} "
              f"(mesmo jogo {np.mean(dp[same] > t):.3f}, jogos diferentes {np.mean(dp[~same] > t):.3f})")
    _write_csv(path("outputs") / "cortes_sinteticos.csv", [dict(clipe_a=a, clipe_b=b, mesmo_jogo=s_, distancia=round(d, 4)) for a, b, s_, d in pos])
    return dn, dp, same


def cut_table(pool, clips):
    """Precisão e recall do corte em torno de cut_thr: falsos positivos entre frames
    consecutivos dos clipes (os 19 da calibração, train[::3], x os demais) e recall nos
    cortes sintéticos da calibração (outputs/cortes_sinteticos.csv). Negativos em
    outputs/cortes_negativos.csv."""
    import csv
    from src_v2.run import _write_csv
    with pool() as ex:
        hists = {c: h for c, h in zip(clips, ex.map(_clip_hists, clips)) if h is not None}
    calib = {c.name for c in sorted(clips[0].parent.glob("SNGS-*"))[::3]}
    neg = [dict(clipe=c.name, frame=i + 1, calibracao=c.name in calib, distancia=round(hist_distance(h[i], h[i + 1]), 4))
           for c, h in hists.items() for i in range(len(h) - 1)]
    _write_csv(path("outputs") / "cortes_negativos.csv", neg)
    with open(path("outputs") / "cortes_sinteticos.csv", encoding="utf-8") as f:
        pos = list(csv.DictReader(f))
    dp = np.array([float(r["distancia"]) for r in pos])
    same = np.array([r["mesmo_jogo"] == "True" for r in pos])
    dn = np.array([r["distancia"] for r in neg])
    cal = np.array([r["calibracao"] for r in neg])
    print(f"negativos: {cal.sum()} pares consecutivos nos {len(calib & {c.name for c in clips})} clipes da calibração, "
          f"{(~cal).sum()} nos outros {len(clips) - len(calib & {c.name for c in clips})}; máximo {dn[cal].max():.3f} x {dn[~cal].max():.3f}")
    print(f"positivos: {len(dp)} cortes sintéticos ({same.sum()} do mesmo jogo)")
    print("limiar | FP calibração | FP outros clipes | recall (mesmo jogo; diferentes) | precisão")
    for t in sorted({0.15, 0.2, T["cut_thr"], 0.25, 0.3, 0.4}):
        tp, fp_c, fp_o = int((dp > t).sum()), int((dn[cal] > t).sum()), int((dn[~cal] > t).sum())
        print(f"{t:.3f}  | {fp_c:13} | {fp_o:16} | {tp / len(dp):.3f} ({np.mean(dp[same] > t):.3f}; {np.mean(dp[~same] > t):.3f})    | "
              f"{tp / max(tp + fp_c + fp_o, 1):.3f}")
    print("   maiores negativos fora da calibração:", [(r["clipe"], r["frame"], r["distancia"]) for r in sorted(neg, key=lambda r: -r["distancia"]) if not r["calibracao"]][:8])
    return dn, cal, dp, same


# ======================= 6c: propagação por Lucas–Kanade =======================
# TODO(divida): repete o fit_point_line com um termo a mais; homography.py está na chave do
# cache da série do detector (_series_key), e editá-lo agora refaria ~11 h de série. Unificar
# na Fatia 8, quando a série for refeita de qualquer jeito.
def fit_points_lines(H0, lines_uv, points, size, alpha):
    """fit_point_line da Fatia 2 com um termo de pontos: distância (px) de cada ponto do
    campo projetado por H ao seu ponto rastreado na imagem, com peso alpha. Aceite
    como o da Fatia 2 (posto 8, condição, resíduo mediano), sobre linhas e pontos."""
    from scipy.optimize import least_squares
    from src_v2.homography import F, N_FIELD, Fit, _img_norm, class_distances, smooth_distances
    XY, uv = points
    n = sum(len(p) for p in lines_uv.values()) + len(XY)
    if n < F["min_points"]:
        return Fit(None, np.nan, 0, np.inf, n, False)
    Ni = _img_norm(size)
    Ni_inv = np.linalg.inv(Ni)
    Xh = np.c_[XY, np.ones(len(XY))]

    def H_of(g):
        return Ni_inv @ np.append(g, 1.0).reshape(3, 3) @ N_FIELD

    def pts_err(H):
        q = Xh @ H.T
        return q[:, :2] / q[:, 2:] - uv

    def resid(g, sampson):
        # pontos como (du, dv): a norma não é diferenciável no zero e segurava o
        # least_squares em ~300 avaliações por frame contra 3 (mesma mediana)
        cap = F["resid_cap_px"]
        H = H_of(g)
        r = np.clip(alpha * pts_err(H).ravel(), -cap, cap)
        return np.r_[np.minimum(smooth_distances(H, lines_uv, sampson), cap), r] if lines_uv else r

    G0 = Ni @ H0 @ np.linalg.inv(N_FIELD)
    kw = dict(loss=F["loss"], f_scale=F["f_scale_px"], x_scale="jac")
    # só o passo de Sampson: H0 vem dos pontos propagados, perto da solução; o passo
    # geométrico da Fatia 2 (polilinha densa nos círculos) é para inícios distantes e
    # custava ~90% do tempo (2,3 s por frame)
    r = least_squares(resid, (G0 / G0[2, 2]).ravel()[:8], args=(True,), **kw)
    sv = np.linalg.svd(r.jac, compute_uv=False)
    rank = int((sv > sv[0] * np.sqrt(np.finfo(float).eps)).sum())
    cond = float(sv[0] / sv[-1]) if sv[-1] > 0 else np.inf
    H = H_of(r.x)
    d = [np.concatenate(list(class_distances(H, lines_uv).values()))] if lines_uv else []
    med = float(np.median(np.concatenate(d + [np.linalg.norm(pts_err(H), axis=1)])))
    return Fit(H, med, rank, cond, n, rank == 8 and cond <= F["max_cond"] and med <= F["max_resid_px"])


def _masks(img):
    """Gramado, marcações e a máscara onde a grade pode ficar: gramado ou linha, sem os
    componentes compactos de não-gramado (jogadores, bola), dilatados (decisão de Victor).
    O gramado bruto sai uma vez só (grass_mask = _post(_grass_raw)); a versão GPU é
    src_v2/gpu.py, com a mesma saída."""
    from src_v2.lines import shape_filter
    from src_v2.segment import _grass_raw, _post, line_mask, params
    P = params("gsr")
    raw = _grass_raw(img, P)
    grass = _post(raw, P)
    marks = line_mask(img, grass, P)
    nong = grass & ~raw
    compact = nong & ~shape_filter(nong, CFG["lines"])
    k = 2 * int(T["compact_dilate_frac"] * img.shape[0]) + 1
    compact = cv2.dilate(compact.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    return grass, marks, grass & ~compact


GRID = np.stack(np.meshgrid(np.arange(-52.5, 52.51, T["grid_m"][0]), np.arange(-34, 34.01, T["grid_m"][1])), -1).reshape(-1, 2)


def _sample_grid(H, keep, size):
    """Pontos da grade do campo projetados por H, dentro da imagem (menos a borda) e
    sobre `keep`: (campo (K,2), imagem (K,2) float32)."""
    from src_v2.geometry import project
    w, h = size
    uv, front = project(H, GRID)
    b = T["border_frac"] * h
    ok = front & (uv[:, 0] >= b) & (uv[:, 0] < w - b) & (uv[:, 1] >= b) & (uv[:, 1] < h - b)
    ok[ok] = keep[uv[ok, 1].astype(int), uv[ok, 0].astype(int)]
    return GRID[ok], uv[ok].astype(np.float32)


def _lk(g0, g1, p0):
    """Lucas–Kanade piramidal de g0 para g1 com verificação ida-e-volta: (pontos em g1,
    máscara dos que passaram)."""
    kw = dict(winSize=(T["lk_win"], T["lk_win"]), maxLevel=T["lk_levels"])
    if not len(p0):
        return p0, np.zeros(0, bool)
    p1, st1, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0, None, **kw)
    p0b, st2, _ = cv2.calcOpticalFlowPyrLK(g1, g0, p1, None, **kw)
    ok = (st1.ravel() == 1) & (st2.ravel() == 1) & (np.linalg.norm(p0b - p0, axis=1) <= T["lk_fb_px"])
    return p1, ok


# TODO(divida): mesma saída de assign.guided_points (tests/test_temporal.py), ~9x mais rápida;
# assign.py está na chave do cache da série do detector. Trocar lá na Fatia 8.
def _guided_points(H, marks, classes):
    """Classe -> pixels da máscara (imagem) a <= band_frac·h da polilinha da classe
    projetada por H, subamostrados para no máximo `guided_max_pts`. Lê as marcações uma
    vez; cada classe é desenhada com o próprio valor por cima das anteriores e lida logo
    em seguida (sem limpar o canvas)."""
    from src_v2.geometry import project_segments
    from src_v2.pitch_model import POLYLINES
    A = CFG["assign"]
    t = 2 * int(round(A["band_frac"] * marks.shape[0])) + 1
    v_m, u_m = np.nonzero(marks)
    canvas, out = np.zeros(marks.shape, np.uint8), {}
    for j, k in enumerate(classes, 1):
        g = project_segments(H, POLYLINES[k])
        if not len(g):
            continue
        cv2.polylines(canvas, list(np.clip(g, -1e6, 1e6).astype(np.int32)), False, j, t)
        on = canvas[v_m, u_m] == j
        if on.sum() >= 2:
            u, v = u_m[on], v_m[on]
            sel = np.linspace(0, len(u) - 1, min(len(u), A["guided_max_pts"])).astype(int)
            out[k] = np.stack([u[sel], v[sel]], 1).astype(float)
    return out


class ClipFrames:
    """Frames de um clipe em cinza (sob demanda) e máscaras empacotadas, reaproveitadas
    entre as variantes. Com GPU (src_v2/gpu.py) e `use_gpu`, as máscaras do clipe inteiro
    saem em lote ao abrir; sem, sob demanda na CPU. Mesma saída nos dois caminhos."""

    def __init__(self, samples):
        from src_v2 import gpu
        self.samples = samples
        self.size = samples[0].size
        self._m = gpu.clip_masks(samples) if T["use_gpu"] and gpu.AVAILABLE else {}

    def gray(self, i):
        return cv2.cvtColor(self.samples[i].image, cv2.COLOR_BGR2GRAY)

    def masks(self, i):
        if i not in self._m:
            _, marks, keep = _masks(self.samples[i].image)
            self._m[i] = (np.packbits(marks), np.packbits(keep))
        shape = (self.size[1], self.size[0])
        return tuple(np.unpackbits(x)[:shape[0] * shape[1]].reshape(shape).astype(bool) for x in self._m[i])


def propagate(cf, a, H_a, stop, step, lines=True, dbg=None):
    """Propaga a H da âncora a (índice de frame) até `stop` (exclusivo) no sentido `step`
    (+1 ou -1): Lucas–Kanade na grade do campo, reestimativa com pontos propagados +
    pixels guiados das linhas (ou só pontos). {índice: H}. Com `dbg` (pasta), salva a
    cada debug_every frames o modelo projetado e os pontos rastreados."""
    from src_v2.pitch_model import POLYLINES
    from src_v2.render import draw_overlay
    size = cf.size
    fld, img = _sample_grid(H_a, cf.masks(a)[1], size)
    H, g0, out, since = H_a, cf.gray(a), {}, 0
    for t in range(a + step, stop, step):
        g1 = cf.gray(t)
        p1, ok = _lk(g0, g1, img)
        fld, img = fld[ok], p1[ok]
        if len(fld) >= 4:
            Hp, _ = cv2.findHomography(fld.astype(np.float32), img, 0)
            # pontos quase colineares dão H degenerada (SNGS-049: condição 5e19); fica a anterior
            if Hp is not None and np.isfinite(Hp).all() and np.linalg.cond(Hp) <= T["h_cond_max"]:
                H = Hp
        marks, keep = cf.masks(t)
        lines_uv = _guided_points(H, marks, list(POLYLINES)) if lines else {}
        try:
            fit = fit_points_lines(H, lines_uv, (fld, img), size, T["alpha_points"])
        except np.linalg.LinAlgError:             # o otimizador passou por uma H singular: ajuste não aceito
            fit = None
        if fit is not None and fit.ok:
            H = fit.H
        out[t] = H
        if dbg is not None and t % T["debug_every"] == 0:
            im = draw_overlay(cf.samples[t].image, H)
            for u, v in img.astype(int):
                cv2.circle(im, (int(u), int(v)), 3, (0, 255, 0), -1)
            cv2.imwrite(str(dbg / f"{cf.samples[t].sequence_id}_{t:04d}_ancora{a:04d}.jpg"),
                        cv2.resize(im, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
        since += 1
        if len(fld) < T["resample_min"] or since >= T["resample_every"]:
            fld, img = _sample_grid(H, keep, size)
            since = 0
        g0 = g1
    return out


def anchors(ser, cf, seg, verify=True):
    """Âncoras: máximos locais de (IoU com o gramado + fração explicada) entre os frames
    com H do detector; com `verify`, só as que concordam com o detector nos vizinhos (do
    mesmo plano, `seg`) pelo movimento medido por Lucas–Kanade. Devolve (âncoras,
    candidatas, verificáveis)."""
    from src_v2.evaluate import image_grid_displacement
    ok = np.isfinite(ser["H"]).all(axis=(1, 2))
    a = np.where(ok, np.nan_to_num(ser["iou"]) + np.nan_to_num(ser["img"]), -np.inf)
    W = T["anchor_window"]
    cand = [t for t in np.nonzero(ok)[0] if a[t] >= a[max(0, t - W):t + W + 1].max()]
    if not verify:
        return cand, cand, cand
    out, verifiable = [], []
    tol = T["verify_tol_frac"] * cf.size[1]
    for t in cand:
        nb = [u for u in range(max(0, t - T["verify_window"]), min(len(ok), t + T["verify_window"] + 1)) if u != t and ok[u] and seg[u] == seg[t]]
        if len(nb) < T["verify_min"]:
            continue
        verifiable.append(t)
        agree = 0
        for step, group in ((1, [u for u in nb if u > t]), (-1, [u for u in nb if u < t])):
            if group:
                prop = propagate(cf, t, ser["H"][t], max(group) + step if step > 0 else min(group) + step, step, lines=False)
                agree += sum(image_grid_displacement(prop[u], ser["H"][u], cf.size) <= tol for u in group if u in prop)
        # v2, B1: a maioria não recusa erro sistemático; a nota da âncora também tem que passar no limiar
        if agree > len(nb) / 2 and (T["anchor_min_nota"] is None or a[t] >= T["anchor_min_nota"]):
            out.append(t)
    return out, cand, verifiable


def dlt_normalized(XY, uv):
    """H (campo -> imagem) por DLT com a normalização de Hartley nos dois conjuntos de pontos."""
    def norm(p):
        c = p.mean(axis=0)
        s = np.sqrt(2) / np.mean(np.linalg.norm(p - c, axis=1))
        return np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1.0]])
    Ta, Tb = norm(XY), norm(uv)
    a, b = np.c_[XY, np.ones(len(XY))] @ Ta.T, np.c_[uv, np.ones(len(uv))] @ Tb.T
    M = np.zeros((2 * len(a), 9))
    M[0::2, 0:3], M[0::2, 6:9] = a, -b[:, [0]] * a
    M[1::2, 3:6], M[1::2, 6:9] = a, -b[:, [1]] * a
    H = np.linalg.inv(Tb) @ np.linalg.svd(M)[2][-1].reshape(3, 3) @ Ta
    return H / H[2, 2]


def fuse(Ha, Hb, wa, size):
    """C (v2): fusão, no espaço da imagem, das H propagadas de duas âncoras (campo -> imagem), com
    peso wa para Ha. Pontos da grade do campo (evaluate.FIELD_GRID) à frente da câmera e dentro da
    imagem pelas duas H, com margem c_margin_frac·h; posições combinadas e H reestimada por DLT
    normalizada. Com menos de c_min_points pontos, fica a H de maior peso. Devolve também a
    discordância entre Ha e Hb nesses pontos (mediana, em fração da altura), só para diagnóstico."""
    from src_v2.evaluate import FIELD_GRID
    from src_v2.geometry import project
    w, h = size
    m = T["c_margin_frac"] * h
    ua, oka = project(Ha, FIELD_GRID)
    ub, okb = project(Hb, FIELD_GRID)
    inside = lambda u: (u[:, 0] >= -m) & (u[:, 0] <= w - 1 + m) & (u[:, 1] >= -m) & (u[:, 1] <= h - 1 + m)
    sel = oka & okb & inside(ua) & inside(ub)
    if sel.sum() < T["c_min_points"]:
        return (Ha if wa >= 0.5 else Hb), np.nan
    d = float(np.median(np.linalg.norm(ua[sel] - ub[sel], axis=1)) / h)
    return dlt_normalized(FIELD_GRID[sel], wa * ua[sel] + (1 - wa) * ub[sel]), d


def fill_from_anchors(cf, anc, H_anchor, seg, mode="flow", dbg=None, diag=None):
    """H de cada frame pela âncora mais próxima do mesmo plano (`seg`, entre cortes):
    "flow" (propaga e reestima), "noflow" (a H da âncora copiada) ou "nolines" (propaga,
    só pontos na reestimativa). Plano sem âncora fica sem H. v2, C (`temporal.bidirectional`,
    só no "flow"): entre duas âncoras a1 < a2, cada frame t recebe a fusão (`fuse`) das
    propagações vindas de a1 e de a2, com peso (a2 - t)/(a2 - a1) para a de a1; nas pontas, nada
    muda. `diag` (dict), se dado, recebe a discordância das duas propagações por frame."""
    Hs = np.full((len(seg), 3, 3), np.nan)
    bidir = mode == "flow" and T["bidirectional"]
    for k in np.unique(seg):
        idx = np.nonzero(seg == k)[0]
        s0, s1 = idx[0], idx[-1] + 1
        A = sorted(a for a in anc if s0 <= a < s1)
        for i, a in enumerate(A):
            Hs[a] = H_anchor[a]
            lo = s0 if i == 0 else (A[i - 1] + a) // 2 + 1
            hi = s1 if i == len(A) - 1 else (a + A[i + 1]) // 2 + 1
            for stop, step in ((hi, 1), (lo - 1, -1)):
                if bidir and ((step == 1 and i < len(A) - 1) or (step == -1 and i > 0)):
                    continue                                # entre âncoras: fusão abaixo
                if mode == "noflow":
                    Hs[list(range(a + step, stop, step))] = H_anchor[a]
                else:
                    for t, H in propagate(cf, a, H_anchor[a], stop, step, lines=mode != "nolines", dbg=dbg).items():
                        Hs[t] = H
        if bidir:
            for a1, a2 in zip(A[:-1], A[1:]):
                if a2 - a1 < 2:
                    continue
                fwd = propagate(cf, a1, H_anchor[a1], a2, 1, lines=True, dbg=dbg)
                bwd = propagate(cf, a2, H_anchor[a2], a1, -1, lines=True)
                for t in range(a1 + 1, a2):
                    Hs[t], d = fuse(fwd[t], bwd[t], (a2 - t) / (a2 - a1), cf.size)
                    if diag is not None:
                        diag[t] = d
    return Hs


def _gap_lengths(ok):
    """Comprimento da lacuna do detector em cada frame: 0 onde há H; -1 nas lacunas que
    tocam a ponta do clipe (sem os dois lados para interpolar)."""
    L = np.zeros(len(ok), int)
    for a, b in _runs(~ok, 0):
        L[a:b + 1] = b - a + 1 if a > 0 and b < len(ok) - 1 else -1
    return L


VARIANTS_6C = ("detector", "6a Bassek", "6a robusto", "6c fluxo", "6c sem fluxo", "6c sem linhas", "6c âncora ingênua /150", "6c âncora de gabarito")


def _eval_clip_6c(clip):
    """Séries do 6c e ablações num clipe: métricas por frame, tremor, as âncoras
    (candidatas, verificáveis, aceitas, com o NPE da H do detector nelas) e as séries
    de H (campo -> imagem) de cada variante, para a Fatia 7."""
    import time
    from src_v2.evaluate import frame_metrics, npe_re
    cv2.setNumThreads(1)
    t0 = time.time()
    ser = load_series(clip)
    samples = gsr.load_clip(clip)
    assert [s.frame_idx for s in samples] == list(ser["frames"])
    cf = ClipFrames(samples)
    size, n = cf.size, len(samples)
    ok = np.isfinite(ser["H"]).all(axis=(1, 2))
    hists = [frame_hist(s.image) for s in samples]
    cut = np.r_[False, [hist_distance(hists[i], hists[i + 1]) > T["cut_thr"] for i in range(n - 1)]]
    seg = np.cumsum(cut)
    anc, cand, verifiable = anchors(ser, cf, seg)
    naive = [next(t for t in range(k, min(k + T["naive_step"], n)) if ok[t]) for k in range(0, n, T["naive_step"])
             if ok[k:k + T["naive_step"]].any()]
    H_gt = np.array([np.full((3, 3), np.nan) if s.H_gt is None else s.H_gt for s in samples])
    dbg = path("debug") / "propagacao"
    dbg.mkdir(parents=True, exist_ok=True)
    series = {
        "detector": ser["H"],
        "6a Bassek": smooth_homographies(ser["H"], size, "matrix"),
        "6a robusto": smooth_homographies(hampel_homographies(ser["H"], size, T["hampel_half"], T["hampel_sigma"]), size, "matrix"),
        "6c fluxo": fill_from_anchors(cf, anc, ser["H"], seg, "flow", dbg, diag=(diag_c := {})),
        "6c sem fluxo": fill_from_anchors(cf, anc, ser["H"], seg, "noflow"),
        "6c sem linhas": fill_from_anchors(cf, anc, ser["H"], seg, "nolines"),
        "6c âncora ingênua /150": fill_from_anchors(cf, naive, ser["H"], seg, "flow"),
        "6c âncora de gabarito": fill_from_anchors(cf, [a for a in anc if np.isfinite(H_gt[a]).all()], H_gt, seg, "flow"),
    }
    game, gaps = gsr.game_id(clip), _gap_lengths(ok)
    rows, jit = [], {}
    for name, Hs in series.items():
        jit[name] = jitter(Hs, size)
        for i, (s, H) in enumerate(zip(samples, Hs)):
            rows.append(dict(**frame_metrics(H if np.isfinite(H).all() else None, s), variante=name, jogo=game,
                             lacuna=int(gaps[i]), n_pessoas=0 if s.persons_XY is None else len(s.persons_XY),
                             discordancia_c=diag_c.get(i, np.nan) if name == "6c fluxo" else np.nan))   # v2, C: só diagnóstico
    anc_rows = [dict(clip=clip.name, t=int(t), verificavel=t in verifiable, aceita=t in anc,
                     npe=npe_re(ser["H"][t], H_gt[t], size)[0] if np.isfinite(H_gt[t]).all() else np.nan) for t in cand]
    print(f"{clip.name}: {n} frames, {int(cut.sum())} cortes, {len(cand)} candidatas, {len(verifiable)} verificáveis, "
          f"{len(anc)} âncoras, {time.time() - t0:.0f} s", flush=True)
    return rows, jit, anc_rows, {k: v.astype(np.float32) for k, v in series.items()}


def _eval_6c_key():
    """Hash do que o resultado do 6c num clipe depende: config temporal, série do
    detector e os bytes (lidos na importação) do temporal.py, do evaluate.py e do
    io/gsr.py. Não usa `inspect.getsource`, que lê o arquivo na hora com os números de
    linha da importação (valid, 2026-09-30: 47 de 58 clipes gravados com chave errada).
    O processo principal a calcula no início da rodada e cada trabalhador confere."""
    h = hashlib.sha1(json.dumps(T, sort_keys=True).encode() + _series_key().encode())
    # v2, achado 3: as métricas (eval), o gabarito (gsr, gsr_label_fixes) e o molde (pitch)
    h.update(json.dumps({k: CFG[k] for k in ("eval", "gsr", "gsr_label_fixes", "pitch")}, sort_keys=True).encode())
    for f in ("temporal.py", "evaluate.py", "io/gsr.py"):
        h.update(_SRC[f])
    return h.hexdigest()


def _eval_6c_path(clip):
    return path("cache") / "eval_6c" / clip.parent.name / f"{clip.name}.pkl"


def _eval_clip_6c_cached(clip, key):
    """_eval_clip_6c com cache por clipe: interromper perde só os clipes em andamento, e o
    mesmo comando retoma dos que faltam; refeito se a chave (`_eval_6c_key`, calculada no
    início da rodada) mudar."""
    import pickle
    from src_v2.executor import check_key
    check_key(key, _eval_6c_key(), "6c")
    p = _eval_6c_path(clip)
    if p.exists():
        k, res = pickle.loads(p.read_bytes())
        if k == key:
            return res
    res = _eval_clip_6c(clip)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(pickle.dumps((key, res)))
    return res


def evaluate_6c(pool, clips):
    """Roda o 6c nos clipes (cache por clipe em outputs/cache/eval_6c/), confere no fim a
    chave gravada de cada clipe e imprime as tabelas."""
    import pickle
    with pool() as ex:
        key = _eval_6c_key()
        res = [r for r in ex.map(_eval_clip_6c_cached, clips, [key] * len(clips)) if r is not None]
        ex.verify_keys(key, lambda a: pickle.loads(_eval_6c_path(a[0]).read_bytes())[0] if _eval_6c_path(a[0]).exists() else None)
    return report_6c(res, f"{clips[0].parent.name}_{len(clips)}clipes")


def report_6c(res, tag):
    """Tabelas do 6c: geral, conjunto comum (frames com H do detector), âncoras e as
    lacunas do detector (6a preenchendo por interpolação x 6c propagando)."""
    from src_v2.evaluate import summarize
    from src_v2.run import _write_csv
    rows = [r for x in res for r in x[0]]
    anc = [a for x in res for a in x[2]]
    _write_csv(path("outputs") / f"ancoras_6c_{tag}.csv", anc)
    print(f"{len(res)} clipes, {len(rows) // len(VARIANTS_6C)} frames")
    print("série                    | cobertura | NPE med  média  | IoU_whole med | LocSim@5 pen | mAP pen | tremor med (px) p90")
    for name in VARIANTS_6C:
        t = summarize([r for r in rows if r["variante"] == name])["todos"]
        j = np.concatenate([x[1][name] for x in res])
        print(f"{name:24} | {t['cobertura']:.3f}     | {t['npe'][1]:.4f} {t['npe'][0]:.3f} | {t['iou_whole'][1]:.3f}         | "
              f"{t.get('locsim@5 penalizado', np.nan):.3f}        | {t.get('mAP-locsim penalizado', np.nan):.3f}   | "
              f"{np.nanmedian(j):.2f} {np.nanpercentile(j, 90):.2f}")
    common = [r for r in rows if r["lacuna"] == 0]
    print(f"\nconjunto comum: só os frames em que o detector tem H ({len(common) // len(VARIANTS_6C)} frames)")
    print("série                    | cobertura | NPE med  média  | LocSim@5 pen | LocSim@5 nos cobertos")
    for name in VARIANTS_6C:
        t = summarize([r for r in common if r["variante"] == name])["todos"]
        print(f"{name:24} | {t['cobertura']:.3f}     | {t['npe'][1]:.4f} {t['npe'][0]:.3f} | "
              f"{t.get('locsim@5 penalizado', np.nan):.3f}        | {t.get('locsim@5', (np.nan,))[0]:.3f}")
    print("\nâncoras: candidata = máximo local da nota; verificável = >= verify_min vizinhos com H; aceita = maioria concorda")
    for label, sel in (("candidatas", lambda a: True), ("verificáveis", lambda a: a["verificavel"]),
                       ("aceitas", lambda a: a["aceita"]), ("rejeitadas (verificáveis)", lambda a: a["verificavel"] and not a["aceita"])):
        e = np.array([a["npe"] for a in anc if sel(a)])
        f = e[np.isfinite(e)]
        print(f"   {label:26} {len(e):5}  NPE mediano {np.median(f) if len(f) else np.nan:.4f}  "
              f"NPE > 0,05 (erradas): {int((f > 0.05).sum())} ({np.mean(f > 0.05) if len(f) else np.nan:.1%})")
    print("\nlacunas do detector (frames sem H, lacuna interna de L frames): cobertura e NPE mediano")
    print("   L        frames | detector cob NPE | 6a Bassek cob NPE | 6a robusto        | 6c fluxo cob NPE  | 6c sem linhas     | 6c sem fluxo cob NPE")
    for lo, hi in ((0, 0), (1, 3), (4, 25), (26, 10**6), (-1, -1)):
        line = []
        for name in ("detector", "6a Bassek", "6a robusto", "6c fluxo", "6c sem linhas", "6c sem fluxo"):
            rs = [r for r in rows if r["variante"] == name and lo <= r["lacuna"] <= hi and r["has_gt"]]
            e = [r["npe"] for r in rs if "npe" in r]
            line.append(f"{len(e) / max(len(rs), 1):.3f} {np.median(e) if e else np.nan:.4f}")
        nfr = sum(1 for r in rows if r["variante"] == "detector" and lo <= r["lacuna"] <= hi and r["has_gt"])
        tag = "com H" if hi == 0 else "pontas" if hi == -1 else f"{lo}-{hi}" if hi < 10**6 else f">{lo - 1}"
        print(f"   {tag:8} {nfr:6} | " + " | ".join(f"{x:17}" for x in line))
    return rows, anc


# ======================= 6a robusto: calibração do Hampel =======================
def _eval_clip_hampel(clip):
    """Métricas por frame de cada (meia janela, limiar) do Hampel + SG matriz e do 6a
    Bassek (sem Hampel), e o que o Hampel descartou (NPE da H do detector descartada)."""
    from src_v2.evaluate import frame_metrics, npe_re
    cv2.setNumThreads(1)
    ser = load_series(clip)
    samples = gsr.load_clip(clip)
    assert [s.frame_idx for s in samples] == list(ser["frames"])
    size, game = samples[0].size, gsr.game_id(clip)
    X = to_points_rep(ser["H"], size)
    npe_det = np.array([npe_re(H, s.H_gt, size)[0] if s.H_gt is not None and np.isfinite(H).all() else np.nan
                        for H, s in zip(ser["H"], samples)])
    configs = [None] + [(h, k) for h in T["hampel_half_grid"] for k in T["hampel_sigma_grid"]]
    rows, drops = [], []
    for c in configs:
        Hs = ser["H"]
        if c is not None:
            bad = hampel_outliers(X, *c)
            drops.append(dict(clip=clip.name, half=c[0], sigma=c[1], descartados=int(bad.sum()),
                              com_gt=int(np.isfinite(npe_det[bad]).sum()), errados=int((npe_det[bad] > 0.05).sum()),
                              errados_total=int((npe_det > 0.05).sum()), com_gt_total=int(np.isfinite(npe_det).sum())))
            Hs = Hs.copy()
            Hs[bad] = np.nan
        Hs = smooth_homographies(Hs, size, "matrix")
        for s, H in zip(samples, Hs):
            rows.append(dict(**frame_metrics(H if np.isfinite(H).all() else None, s), variante=c, jogo=game,
                             n_pessoas=0 if s.persons_XY is None else len(s.persons_XY)))
    print(f"{clip.name} ok", flush=True)
    return rows, drops


def calibrate_hampel(pool, clips):
    """Grade do Hampel antes do SG nos clipes de calibração; regra (decisoes.md): maior
    LocSim@5 penalizado, empate a 0,01 decidido pelo menor NPE mediano."""
    from src_v2.evaluate import summarize
    from src_v2.run import _write_csv
    with pool() as ex:
        res = [r for r in ex.map(_eval_clip_hampel, clips) if r is not None]
    rows = [r for rs, _ in res for r in rs]
    drops = [d for _, dd in res for d in dd]
    _write_csv(path("outputs") / "hampel_descartes.csv", drops)
    configs = [None] + [(h, k) for h in T["hampel_half_grid"] for k in T["hampel_sigma_grid"]]
    print(f"{len(clips)} clipes, {len(rows) // len(configs)} frames; H do detector erradas (NPE > 0,05): "
          f"{sum(d['errados_total'] for d in drops if (d['half'], d['sigma']) == configs[1])} de "
          f"{sum(d['com_gt_total'] for d in drops if (d['half'], d['sigma']) == configs[1])} com gabarito")
    print("meia janela  limiar | descartados (com gab.; errados) | cobertura | NPE med  média  | LocSim@5 pen | mAP pen")
    table = {}
    for c in configs:
        t = summarize([r for r in rows if r["variante"] == c])["todos"]
        table[c] = t
        dd = [d for d in drops if c is not None and (d["half"], d["sigma"]) == c]
        drop = f"{sum(d['descartados'] for d in dd):5} ({sum(d['com_gt'] for d in dd):5}; {sum(d['errados'] for d in dd):4})" if dd else "        -        "
        name = "Bassek (sem Hampel)" if c is None else f"{c[0]:5}      {c[1]:4}  "
        print(f"{name:19} | {drop:31} | {t['cobertura']:.3f}     | {t['npe'][1]:.4f} {t['npe'][0]:.3f} | "
              f"{t.get('locsim@5 penalizado', np.nan):.3f}        | {t.get('mAP-locsim penalizado', np.nan):.3f}")
    best = max(t.get("locsim@5 penalizado", -1) for c, t in table.items() if c is not None)
    tied = [c for c, t in table.items() if c is not None and t.get("locsim@5 penalizado", -1) >= best - 0.01]
    pick = min(tied, key=lambda c: table[c]["npe"][1])
    print(f"escolhido pela regra: meia janela {pick[0]}, limiar {pick[1]} (empatados a 0,01: {tied})")
    return table, pick


# ======================= 7b: calibração do Kalman =======================
def _kalman_configs():
    return ["Bassek", "6a robusto"] + [(q, r) for q in T["kalman_q_grid"] for r in T["kalman_r_grid"]]


def _eval_clip_kalman(clip):
    """Métricas por frame e tremor de cada (q, r) do Kalman + RTS e das referências
    (6a Bassek, 6a robusto) num clipe."""
    from src_v2.evaluate import frame_metrics
    cv2.setNumThreads(1)
    ser = load_series(clip)
    samples = gsr.load_clip(clip)
    assert [s.frame_idx for s in samples] == list(ser["frames"])
    size = samples[0].size
    rows, trem = [], {}
    for c in _kalman_configs():
        if c == "Bassek":
            Hs = smooth_homographies(ser["H"], size, "matrix")
        elif c == "6a robusto":
            Hs = smooth_homographies(hampel_homographies(ser["H"], size, T["hampel_half"], T["hampel_sigma"]), size, "matrix")
        else:
            Hs = kalman_homographies(ser["H"], size, *c)
        trem[c] = jitter(Hs, size)
        for s, H in zip(samples, Hs):
            rows.append(dict(**frame_metrics(H if np.isfinite(H).all() else None, s), variante=c,
                             n_pessoas=0 if s.persons_XY is None else len(s.persons_XY)))
    print(f"{clip.name} ok", flush=True)
    return rows, trem


def calibrate_kalman(pool, clips):
    """Grade (q, r) do Kalman + RTS nos clipes de calibração; regra fixada antes de rodar
    (decisoes.md, 2026-09-30): maior LocSim@5 penalizado, empate a 0,01 pelo menor
    tremor mediano."""
    from src_v2.evaluate import summarize
    with pool() as ex:
        res = [r for r in ex.map(_eval_clip_kalman, clips) if r is not None]
    rows = [r for rs, _ in res for r in rs]
    configs = _kalman_configs()
    print(f"{len(clips)} clipes, {len(rows) // len(configs)} frames")
    print("config (q, r)          | cobertura | NPE med  média  | LocSim@5 pen | mAP pen | tremor med (px) p90")
    table = {}
    for c in configs:
        t = summarize([r for r in rows if r["variante"] == c])["todos"]
        j = np.concatenate([tt[c] for _, tt in res])
        table[c] = (t.get("locsim@5 penalizado", -1), np.nanmedian(j))
        name = c if isinstance(c, str) else f"q={c[0]:<6g} r={c[1]:<6g}"
        print(f"{name:22} | {t['cobertura']:.3f}     | {t['npe'][1]:.4f} {t['npe'][0]:.3f} | "
              f"{t.get('locsim@5 penalizado', np.nan):.3f}        | {t.get('mAP-locsim penalizado', np.nan):.3f}   | "
              f"{np.nanmedian(j):.2f} {np.nanpercentile(j, 90):.2f}")
    grid = [c for c in configs if not isinstance(c, str)]
    best = max(table[c][0] for c in grid)
    tied = [c for c in grid if table[c][0] >= best - 0.01]
    pick = min(tied, key=lambda c: table[c][1])
    print(f"escolhido pela regra: q={pick[0]}, r={pick[1]} (empatados a 0,01: {len(tied)} de {len(grid)})")
    return table, pick
