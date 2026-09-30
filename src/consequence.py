"""Fatia 7: consequência das séries estimadas — estabilidade (tremor e deslize contra o
movimento real por ECC) e taxa de inversão de visibilidade — para o detector, o 6a
(Bassek e robusto), o Kalman + RTS e o 6c (com e sem fluxo), sobre os caches da série
do detector e do 6c. Nunca contra a H_gt na estabilidade.
"""
import hashlib
import json
import pickle

import cv2
import numpy as np

from src import temporal as T
from src.config import CFG, ROOT, path
from src.io import gsr
from src.stability import S, ecc_motion, slip
from src.visibility import debug_top, frame_visibility, summarize_visibility

V_DEBUG_MIN = CFG["visibility"]["debug_min_flips"]
_SRC_ECC = (ROOT / "src" / "stability.py").read_bytes()     # lido uma vez, na importação (ver temporal._SRC)
VARIANTS_7 = ("detector","6a Bassek", "6a robusto", "Kalman + RTS", "6c fluxo", "6c sem fluxo")


def _ecc_path(clip):
    return path("outputs") / "cache" / "ecc" / clip.parent.name / f"{clip.name}.npz"


def _ecc_key():
    """Config do ECC e bytes (lidos na importação) do stability.py e do temporal.py
    (máscaras); o processo principal calcula no início da rodada e o trabalhador confere."""
    return hashlib.sha1(json.dumps(S, sort_keys=True).encode() + _SRC_ECC + T._SRC["temporal.py"]).hexdigest()


def clip_motions(clip, samples, key):
    """Movimento real de cada par (t-1, t) do clipe por ECC no gramado sem jogadores (a
    máscara "keep" do 6c), em cache (outputs/cache/ecc/): (W (N,3,3), convergiu, correlação)."""
    p = _ecc_path(clip)
    if p.exists():
        d = np.load(p)
        if str(d["key"]) == key:
            return d["W"], d["ok"], d["cc"]
    cf = T.ClipFrames(samples)
    n = len(samples)
    W, ok, cc = np.full((n, 3, 3), np.nan), np.zeros(n, bool), np.full(n, np.nan)
    g0 = cf.gray(0)
    for t in range(1, n):
        g1 = cf.gray(t)
        W[t], ok[t], cc[t] = ecc_motion(g0, g1, cf.masks(t)[1])
        g0 = g1
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(p, key=key, W=W, ok=ok, cc=cc)
    return W, ok, cc


def _eval_clip_7(clip, key6, key_ecc):
    """Tremor e deslize por frame e visibilidade por frame (com H_gt) de cada variante."""
    from src.executor import check_key
    check_key(key6, T._eval_6c_key(), "6c")
    check_key(key_ecc, _ecc_key(), "ECC")
    cv2.setNumThreads(1)
    ser = dict(np.load(T._series_path(clip)))
    samples = gsr.load_clip(clip)
    size = samples[0].size
    p6 = T._eval_6c_path(clip)
    assert p6.exists(), f"sem o cache do 6c de {clip.name}: rode --propagate-eval antes"
    k6, res6 = pickle.loads(p6.read_bytes())
    assert k6 == key6 and len(res6) == 4, f"cache do 6c de {clip.name} é de outro código: rode --propagate-eval"
    s6 = res6[3]
    series = {"detector": ser["H"], "6a Bassek": s6["6a Bassek"], "6a robusto": s6["6a robusto"],
              "Kalman + RTS": T.kalman_homographies(ser["H"], size, T.T["kalman_q"], T.T["kalman_r"]),
              "6c fluxo": s6["6c fluxo"], "6c sem fluxo": s6["6c sem fluxo"]}
    hists = [T.frame_hist(s.image) for s in samples]
    cut = np.r_[False, [T.hist_distance(hists[i], hists[i + 1]) > T.T["cut_thr"] for i in range(len(samples) - 1)]]
    W, ok, cc = clip_motions(clip, samples, key_ecc)
    grid = T._stability_grid()
    out = {}
    dbg = path("debug") / "visibilidade"
    dbg.mkdir(parents=True, exist_ok=True)
    for name, Hs in series.items():
        Hs = np.asarray(Hs, float)
        vis = []
        for s, H in zip(samples, Hs):
            if s.H_gt is None:
                continue
            has = bool(np.isfinite(H).all())
            v = frame_visibility(H if has else None, s.H_gt, size, s.persons_XY)
            if name in ("detector", "6c fluxo") and v["sai"] >= V_DEBUG_MIN and s.frame_idx % 50 == 0:
                debug_top(v, s.persons_XY, dbg / f"{clip.name}_{s.frame_idx:04d}_{name.replace(' ', '_')}.png")
            vis.append({k: v[k] for k in ("vis_gt", "vis_est", "sai", "entra", "grade_diff", "grade_uniao")} | {"has_pred": has})
        out[name] = (T.jitter(Hs, size), slip(Hs, W, ok & ~cut, size, grid), vis, float(np.isfinite(Hs).all(axis=(1, 2)).mean()))
    print(f"{clip.name}: ECC convergiu em {ok[1:].mean():.1%} dos pares", flush=True)
    return out, ok[1:], cc[1:]



def evaluate_7(pool, clips):
    """Tabela da Fatia 7 nos clipes: cobertura, tremor, deslize (com a taxa de
    convergência do ECC) e inversão de visibilidade, por variante."""
    with pool() as ex:
        n, key_ecc = len(clips), _ecc_key()
        res = [r for r in ex.map(_eval_clip_7, clips, [T._eval_6c_key()] * n, [key_ecc] * n) if r is not None]
        ex.verify_keys(key_ecc, lambda a: str(np.load(_ecc_path(a[0]))["key"]) if _ecc_path(a[0]).exists() else None)
    ok = np.concatenate([r[1] for r in res])
    cc = np.concatenate([r[2] for r in res])
    print(f"{len(clips)} clipes; ECC convergiu em {ok.mean():.1%} dos {len(ok)} pares (correlação mediana {np.nanmedian(cc):.3f}); "
          "pares sem convergência ficam fora do deslize")
    print("série          | cobertura | tremor med p90 (px) | deslize med p90 (px), pares | inversão jogadores pen / cob | grade pen / cob | 0 visíveis pen / cob")
    table = {}
    for name in VARIANTS_7:
        trem = np.concatenate([r[0][name][0] for r in res])
        sl = np.concatenate([r[0][name][1] for r in res])
        vis = summarize_visibility([v for r in res for v in r[0][name][2]])
        cov = np.mean([r[0][name][3] for r in res])
        table[name] = dict(tremor=np.nanmedian(trem), deslize=np.nanmedian(sl), vis=vis, cobertura=cov)
        pen, cob = vis["penalizada"], vis["só cobertos"]
        print(f"{name:14} | {cov:.3f}     | {np.nanmedian(trem):5.2f} {np.nanpercentile(trem, 90):6.2f}        | "
              f"{np.nanmedian(sl):5.2f} {np.nanpercentile(sl, 90):6.2f}, {int(np.isfinite(sl).sum()):6d}   | "
              f"{pen['jogadores']:.3f} / {cob['jogadores']:.3f}              | {pen['grade']:.3f} / {cob['grade']:.3f}   | "
              f"{pen['zero_visiveis']:.3f} / {cob['zero_visiveis']:.3f}")
    return table
