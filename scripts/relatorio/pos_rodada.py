"""Medidas posteriores à rodada do test, pedidas na revisão externa do relatório (Victor,
2026-10-13). Nenhum parâmetro muda: só os caches da rodada (série do detector, 6c, extras,
H_gt do test com a chave do congelamento) e funções do src/ sem mudança.

- B1: LocSim@5 da H_gt pelas linhas e da H_gt_auxflow como predição, no GSR test (o
  análogo do 0,933 do train, decisoes.md, 2026-09-25).
- B2: 6a Bassek e 6a robusto no HSB, com as colunas da T2.
- B3: acurácia contra as linhas anotadas (contagem do SN-Calib, 5/10/20 px em 960x540),
  já gravada por frame nos caches da rodada (frame_metrics): de todas as séries, no test
  inteiro e no conjunto comum (frames com H do detector), e das duas H_gt de B1.
- B4: teto do sistema: âncoras de gabarito escolhidas sem o detector (o primeiro frame
  com H_gt em cada bloco de `naive_step` frames, como a âncora ingênua) e a mesma
  propagação do 6c (fill_from_anchors, modo "flow").

Grava outputs/runs/rodada_test/pos_rodada/B*.csv, cada linha com o commit do método e o
deste script (recusa rodar com alteração sem commit). As linhas por frame ficam em
pos_rodada.pkl; com ele presente, só refaz as tabelas.
Uso (da raiz, PYTHONPATH=.): pos_rodada.py <trabalhadores>"""
import csv
import json
import pickle
import subprocess
import sys
from collections import defaultdict

import cv2
import numpy as np

from src.config import path

OUT = path("outputs") / "runs" / "rodada_test"
DST = OUT / "pos_rodada"
FROZEN = json.loads((path("outputs") / "runs" / "congelamento.json").read_text(encoding="utf-8"))
HGT_LINES, HGT_AUX, B4 = "H_gt pelas linhas", "H_gt_auxflow", "teto do sistema (âncora de gabarito /150)"


def script_commit():
    here = "scripts/relatorio/pos_rodada.py"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", here], capture_output=True, text=True).stdout.strip()
    assert not dirty, "pos_rodada.py com alteração sem commit"
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", here], capture_output=True, text=True).stdout.strip()


def clip_rows(clip):
    """B1 e B4 num clipe: linhas de frame_metrics das duas H_gt e do teto do sistema."""
    from src import temporal as T
    from src.evaluate import frame_metrics
    from src.io import gsr
    cv2.setNumThreads(1)
    key = str(np.load(path("outputs") / "cache" / "gsr" / "test" / f"{clip.name}.npz")["key"])
    assert key == FROZEN["chaves"]["h_gt_test"][clip.name], f"{clip.name}: H_gt com chave diferente da congelada"
    samples = gsr.load_clip(clip)
    n, game = len(samples), gsr.game_id(clip)
    row = lambda H, s, v: dict(**frame_metrics(H, s), variante=v, jogo=game, clipe=clip.name,
                               n_pessoas=0 if s.persons_XY is None else len(s.persons_XY))
    rows = [row(s.H_gt, s, HGT_LINES) for s in samples] + [row(s.H_gt_auxflow, s, HGT_AUX) for s in samples]
    H_gt = np.array([np.full((3, 3), np.nan) if s.H_gt is None else s.H_gt for s in samples])
    ok, step = np.isfinite(H_gt).all(axis=(1, 2)), T.T["naive_step"]
    anc = [next(t for t in range(k, min(k + step, n)) if ok[t]) for k in range(0, n, step) if ok[k:k + step].any()]
    hists = [T.frame_hist(s.image) for s in samples]
    seg = np.cumsum(np.r_[False, [T.hist_distance(hists[i], hists[i + 1]) > T.T["cut_thr"] for i in range(n - 1)]])
    Hs = T.fill_from_anchors(T.ClipFrames(samples), anc, H_gt, seg, "flow")
    rows += [row(H if np.isfinite(H).all() else None, s, B4) for s, H in zip(samples, Hs)]
    print(f"{clip.name}: {len(anc)} âncoras de gabarito", flush=True)
    return rows


# ------------------------------------------------------------------ agregação
def locsim5(r):
    from src.evaluate import locsim
    return locsim(r["locsim_d"], 5).sum() if "locsim_d" in r else 0.0


def summary(rs):
    """Cobertura (frames com H_gt), NPE mediano, LocSim@5 penalizado e nos cobertos, por
    pessoa-frame, e acurácia contra as linhas: penalizada (frame com linhas e sem H vale 0;
    = completude x acurácia do evaluate.summarize) e nos frames cobertos."""
    gt = [r for r in rs if r["has_gt"]]
    npe = [r["npe"] for r in gt if r["has_pred"] and np.isfinite(r.get("npe", np.nan))]
    n_all, n_d = sum(r["n_pessoas"] for r in rs), sum(len(r["locsim_d"]) for r in rs if "locsim_d" in r)
    ls = sum(locsim5(r) for r in rs)
    out = dict(frames=len(rs), cobertura=np.mean([r["has_pred"] for r in gt]) if gt else np.nan,
               npe_med=float(np.median(npe)) if npe else np.nan,
               locsim_pen=ls / n_all if n_all else np.nan, locsim_cob=ls / n_d if n_d else np.nan)
    lines = [r for r in rs if r["has_lines"]]
    out["frames_com_linhas"] = len(lines)
    for t in (5, 10, 20):
        acc = np.array([r[f"acc@{t}"] if r["has_pred"] else 0.0 for r in lines])
        pred = np.array([r["has_pred"] for r in lines], bool)
        out[f"acc{t}_pen"] = float(acc.mean()) if len(acc) else np.nan
        out[f"acc{t}_cob"] = float(acc[pred].mean()) if pred.any() else np.nan
    return out


def by_game(rs, keys):
    """Mínimo e máximo entre os jogos de cada chave de `summary`."""
    games = sorted({r["jogo"] for r in rs}, key=int)
    per = [summary([r for r in rs if r["jogo"] == g]) for g in games]
    return {f"{k}_min": min(p[k] for p in per) for k in keys} | {f"{k}_max": max(p[k] for p in per) for k in keys} | \
        {f"{k}_jogo{g}": p[k] for g, p in zip(games, per) for k in keys}


def hsb_cols(rs):
    """Colunas da T2 (tabelas_test.py): LocSim@5 por frame (média sobre as pessoas do frame)
    nos frames com pessoas, penalizado (0 sem H) e nos cobertos; coberturas nos frames com
    H_gt, nos frames com pessoas e por pessoa; LocSim por pessoa-frame."""
    from src.evaluate import locsim
    wp = [r for r in rs if r.get("n_pessoas")]
    pen = np.array([float(locsim(r["locsim_d"], 5).mean()) if "locsim_d" in r else 0.0 for r in wp])
    has = np.array([r["has_pred"] for r in wp], bool)
    n_all, n_cov = sum(r["n_pessoas"] for r in wp), sum(r["n_pessoas"] for r in wp if r["has_pred"])
    ls = [locsim5(r) for r in wp]
    return dict(pen_media=pen.mean(), pen_mediana=np.median(pen),
                cob_media=pen[has].mean() if has.any() else np.nan, cob_mediana=np.median(pen[has]) if has.any() else np.nan,
                cob_gt=np.mean([r["has_pred"] for r in rs if r["has_gt"]]), cob_fr=has.mean(), cob_ps=n_cov / n_all,
                pen_ps=sum(ls) / n_all, cob_ps_ls=sum(x for x, h in zip(ls, has) if h) / n_cov if n_cov else np.nan,
                frames_com_pessoas=len(wp))


def write(name, rows, commit):
    DST.mkdir(parents=True, exist_ok=True)
    rows = [r | dict(analise="posterior à rodada", commit_metodo=FROZEN["commit"], commit_script=commit) for r in rows]
    with (DST / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    from src import temporal as T
    from src.executor import SafeProcessPool, exit_if_failed
    commit = script_commit()
    clips = sorted((path("gsr") / "test").glob("SNGS-*"))
    pkl = DST / "pos_rodada.pkl"
    if not pkl.exists():
        with SafeProcessPool(int(sys.argv[1]), initializer=cv2.setNumThreads, initargs=(1,)) as ex:
            res = list(ex.map(clip_rows, clips))
        exit_if_failed()
        assert all(r is not None for r in res)
        DST.mkdir(parents=True, exist_ok=True)
        pkl.write_bytes(pickle.dumps(dict(commit_script=commit, rows=[x for r in res for x in r])))
    new = pickle.loads(pkl.read_bytes())["rows"]

    # linhas da rodada: 6c e ablações (cache com a chave congelada ou a regravada) e Kalman (extras)
    rows = []
    for c in clips:
        k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
        assert k in (FROZEN["chaves"]["6c"], T._eval_6c_key()), f"{c.name}: cache do 6c com outra chave"
        rows += [x | {"clipe": c.name} for x in r[0]]
    ext = pickle.loads((OUT / "extras_test.pkl").read_bytes())
    rows += [x | {"clipe": e["clip"]} for e in ext["res"] for x in e["kalman_rows"]]
    rows += new
    byv = defaultdict(list)
    for r in rows:
        byv[r["variante"]].append(r)
    det_pred = {(r["clipe"], r["frame"]) for r in byv["detector"] if r["has_pred"]}
    order = ["detector", "6a Bassek", "6a robusto", "Kalman + RTS", "6c fluxo", "6c sem linhas", "6c sem fluxo",
             "6c âncora ingênua /150", "6c âncora de gabarito", B4, HGT_LINES, HGT_AUX]
    assert set(order) == set(byv) and all(len(byv[v]) == 49 * 750 for v in order)

    keys = ("cobertura", "locsim_pen", "locsim_cob", "acc5_pen", "acc5_cob")
    b = []
    for conj, sel in (("test inteiro", lambda r: True), ("conjunto comum", lambda r: (r["clipe"], r["frame"]) in det_pred)):
        for v in order:
            rs = [r for r in byv[v] if sel(r)]
            b.append(dict(conjunto=conj, serie=v, **summary(rs), **by_game(rs, keys)))
    write("B1_B3_B4", b, commit)
    print("conjunto       | série                                     | cob   | NPE med | LocSim@5 pen / cob | acc 5/10/20 pen        | acc 5/10/20 cob")
    for x in b:
        print(f"{x['conjunto']:14} | {x['serie']:41} | {x['cobertura']:.3f} | {x['npe_med']:.4f}  | {x['locsim_pen']:.4f} / {x['locsim_cob']:.4f}"
              f"    | {x['acc5_pen']:.3f} {x['acc10_pen']:.3f} {x['acc20_pen']:.3f} | {x['acc5_cob']:.3f} {x['acc10_cob']:.3f} {x['acc20_cob']:.3f}")

    # B4: âncoras e fração ao teto do sistema
    t = {x["serie"]: x for x in b if x["conjunto"] == "test inteiro"}
    d, s = t["detector"]["locsim_pen"], t[B4]["locsim_pen"]
    fr = [dict(serie=v, fracao_teto_sistema=(t[v]["locsim_pen"] - d) / (s - d)) for v in order[:9]]
    write("B4_fracao", fr, commit)
    print("\nfração ao teto do sistema:", ", ".join(f"{x['serie']} {x['fracao_teto_sistema']:.3f}" for x in fr))

    # B2: HSB (mesmos intervalos da T2)
    hsb = list(csv.DictReader(open("data_splits/hsb.csv", encoding="utf-8")))
    b2, pooled = [], defaultdict(list)
    for h in hsb:
        a, z = int(h["inicio"]), int(h["fim"])
        lo, hi = min(a, z), max(a, z)
        for v in ("6a Bassek", "6a robusto", "detector", "6c fluxo"):
            rs = sorted([r for r in byv[v] if r["clipe"] == h["clipe"]], key=lambda r: r["frame"])[lo:hi + 1]
            pooled[v] += rs
            b2.append(dict(clipe=h["clipe"], inicio=a, fim=z, serie=v, **hsb_cols(rs)))
    for v, rs in pooled.items():
        b2.append(dict(clipe="todos", serie=v, **hsb_cols(rs)))
    write("B2", b2, commit)
    print("\nB2 (HSB, %): série | pen média / mediana | cob média / mediana | cobertura H_gt / pessoas / por pessoa")
    for x in b2:
        if x["clipe"] == "todos":
            print(f"   {x['serie']:12} | {100 * x['pen_media']:5.1f} / {100 * x['pen_mediana']:5.1f} | {100 * x['cob_media']:5.1f} / "
                  f"{100 * x['cob_mediana']:5.1f} | {x['cob_gt']:.3f} / {x['cob_fr']:.3f} / {x['cob_ps']:.3f}")
    print("por clipe (pen média %):")
    for c in dict.fromkeys(x["clipe"] for x in b2 if x["clipe"] != "todos"):
        print(f"   {c}: " + ", ".join(f"{x['serie']} {100 * x['pen_media']:.1f}" for x in b2 if x["clipe"] == c))
