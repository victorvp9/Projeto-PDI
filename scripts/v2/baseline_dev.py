"""Linha de base do v2 (docs/05-melhorias-plano.md, seção 7) nos 6 jogos de dev (GSR train +
valid, 115 clipes), pelo src_v2/ do commit 4f201c5, bit a bit idêntico ao v1 nos 6 clipes
conferidos (decisoes.md, 2026-10-15). Roda só de um commit limpo com a tag `baseline-dev`.

- Série do detector e 6c pelo src_v2, com os caches do cache_v2 (os regravados do v1 com as
  chaves do v2 e os calculados aqui, para os 34 clipes do treino que faltavam). Manifestos e
  métricas em outputs/runs_v2/baseline_dev/; nada em outputs/cache nem outputs/runs do v1.
- Métricas por jogo: cobertura do detector e do 6c; clipes sem âncora aceita; fração das âncoras
  aceitas erradas (NPE > 0,05); LocSim@5 penalizado do detector, do 6c e do teto condicionado
  às âncoras; NPE mediano do 6c nas lacunas do detector por comprimento (1-3, 4-25, > 25,
  pontas); e a mediana entre os 6 jogos.
- "Vizinhos concordam e todos errados": para cada âncora aceita errada, a verificação temporal
  (temporal.anchors) é refeita só para ela, a partir da série em cache, dos cortes e do
  Lucas–Kanade, sem o detector: quantos vizinhos, quantos concordaram e quantos dos que
  concordaram também tinham a H do detector errada (NPE > 0,05). Confere que a verificação
  refeita aceita a âncora de novo.

Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/baseline_dev.py plano|roda [trab. série] [trab. 6c]"""
import csv
import json
import pickle
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from src_v2.config import path

OUT = path("runs") / "baseline_dev"
DEV = ("train", "valid")
WRONG = 0.05
COST = {"série": 630, "6c": 126}      # s de parede por clipe na rodada do test (relatório v1, T9): 15 e 10 processos


def clips_dev():
    return [c for s in DEV for c in sorted((path("gsr") / s).glob("SNGS-*"))]


def missing():
    import src_v2.temporal as T
    ks, k6 = T._series_key(), T._eval_6c_key()
    f = {"série": [], "6c": []}
    for c in clips_dev():
        ps, p6 = T._series_path(c), T._eval_6c_path(c)
        if not (ps.exists() and str(np.load(ps)["key"]) == ks):
            f["série"].append(c.name)
        if not (p6.exists() and pickle.loads(p6.read_bytes())[0] == k6):
            f["6c"].append(c.name)
    return f


def _pool(n):
    import cv2
    from src_v2.executor import SafeProcessPool
    return lambda: SafeProcessPool(n, initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=OUT / "manifestos")


def run(n_series, n_6c):
    import src_v2.temporal as T
    from src_v2.executor import exit_if_failed
    clips = clips_dev()
    T.build_series(_pool(n_series), clips)                # só os que faltam no cache_v2
    with _pool(n_6c)() as ex:
        key = T._eval_6c_key()
        res = list(ex.map(T._eval_clip_6c_cached, clips, [key] * len(clips)))
        ex.verify_keys(key, lambda a: pickle.loads(T._eval_6c_path(a[0]).read_bytes())[0] if T._eval_6c_path(a[0]).exists() else None)
    exit_if_failed()
    assert all(r is not None for r in res), "clipe com falha no 6c (ver o manifesto)"
    return dict(zip(clips, res))


def neighbours(clip, ts):
    """A verificação temporal de temporal.anchors refeita para as âncoras `ts` do clipe, com o
    registro de cada vizinho: {t: [(vizinho, concordou, NPE da H do detector no vizinho)]}."""
    import src_v2.temporal as T
    from src_v2.io import gsr
    ser, samples = T.load_series(clip), gsr.load_clip(clip)
    cf, n = T.ClipFrames(samples), len(samples)
    hists = [T.frame_hist(s.image) for s in samples]
    seg = np.cumsum(np.r_[False, [T.hist_distance(hists[i], hists[i + 1]) > T.T["cut_thr"] for i in range(n - 1)]])
    ok = np.isfinite(ser["H"]).all(axis=(1, 2))
    tol = T.T["verify_tol_frac"] * cf.size[1]
    return {t: _check(T, cf, ser, samples, seg, ok, tol, t, clip.name) for t in ts}


def _check(T, cf, ser, samples, seg, ok, tol, t, name):
    from src_v2.evaluate import image_grid_displacement, npe_re
    n = len(samples)
    nb = [u for u in range(max(0, t - T.T["verify_window"]), min(n, t + T.T["verify_window"] + 1)) if u != t and ok[u] and seg[u] == seg[t]]
    out = []
    for step, group in ((1, [u for u in nb if u > t]), (-1, [u for u in nb if u < t])):
        if group:
            prop = T.propagate(cf, t, ser["H"][t], max(group) + step if step > 0 else min(group) + step, step, lines=False)
            for u in group:
                s = samples[u]
                e = npe_re(ser["H"][u], s.H_gt, s.size)[0] if s.H_gt is not None else np.nan
                out.append(dict(vizinho=int(u), concordou=bool(u in prop and image_grid_displacement(prop[u], ser["H"][u], cf.size) <= tol), npe=e))
    assert sum(r["concordou"] for r in out) > len(nb) / 2, f"{name} f{t}: a verificação refeita não aceita a âncora"
    return out


def per_game(res):
    from src_v2.evaluate import locsim
    from src_v2.io import gsr
    games = defaultdict(list)
    for c, r in res.items():
        games[(c.parent.name, gsr.game_id(c))].append((c, r))
    rows = []
    for (split, g), items in sorted(games.items(), key=lambda x: (x[0][0], int(x[0][1]))):
        fr = defaultdict(list)
        for _, r in items:
            for x in r[0]:
                fr[x["variante"]].append(x)
        acc = np.array([a["npe"] for _, r in items for a in r[2] if a["aceita"]], float)
        acc = acc[np.isfinite(acc)]
        pen = lambda v: sum(locsim(x["locsim_d"], 5).sum() for x in fr[v] if "locsim_d" in x) / sum(x["n_pessoas"] for x in fr[v])
        cov = lambda v: float(np.mean([x["has_pred"] for x in fr[v] if x["has_gt"]]))
        row = dict(particao=split, jogo=g, clipes=len(items), sem_ancora=sum(not any(a["aceita"] for a in r[2]) for _, r in items),
                   cob_detector=cov("detector"), cob_6c=cov("6c fluxo"), aceitas=len(acc), aceitas_erradas=int((acc > WRONG).sum()),
                   frac_aceitas_erradas=float(np.mean(acc > WRONG)) if len(acc) else np.nan,
                   locsim_pen_detector=pen("detector"), locsim_pen_6c=pen("6c fluxo"), locsim_pen_teto=pen("6c âncora de gabarito"))
        for lo, hi, lab in ((1, 3, "1-3"), (4, 25, "4-25"), (26, 10 ** 6, "> 25"), (-1, -1, "pontas")):
            e = [x["npe"] for x in fr["6c fluxo"] if lo <= x["lacuna"] <= hi and x["has_gt"] and "npe" in x]
            row[f"npe_lacuna_{lab}"] = float(np.median(e)) if e else np.nan
        rows.append(row)
    keys = [k for k in rows[0] if k.startswith(("cob_", "locsim_", "frac_", "npe_"))] + ["sem_ancora"]
    med = dict(particao="mediana", jogo="6 jogos", **{k: float(np.median([r[k] for r in rows])) for k in keys})
    return rows, med


def write(name, rows):
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    f = missing()
    if sys.argv[1] == "plano":
        print(json.dumps(dict(faltam={k: len(v) for k, v in f.items()}, clipes=f,
                              horas=round(sum(len(v) * COST[k] for k, v in f.items()) / 3600, 1)), ensure_ascii=False, indent=1))
        sys.exit(0)
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    assert not git("status", "--porcelain", "--", "src_v2", "config_v2.yaml", "scripts/v2"), "código do v2 com alteração sem commit"
    head = git("rev-parse", "HEAD")
    assert head == git("rev-parse", "baseline-dev^{commit}"), "rode do commit da tag baseline-dev"
    res = run(int(sys.argv[2]) if len(sys.argv) > 2 else 15, int(sys.argv[3]) if len(sys.argv) > 3 else 10)
    rows, med = per_game(res)
    write("baseline_por_jogo", rows + [med])
    nb_rows = []
    for c, r in res.items():
        wrong = [a for a in r[2] if a["aceita"] and np.isfinite(a["npe"]) and a["npe"] > WRONG]
        checks = neighbours(c, [a["t"] for a in wrong]) if wrong else {}
        for a in wrong:
            nb = checks[a["t"]]
            agree = [x for x in nb if x["concordou"]]
            nb_rows.append(dict(particao=c.parent.name, clipe=c.name, ancora=a["t"], npe_ancora=a["npe"], vizinhos=len(nb),
                                concordaram=len(agree), concordantes_errados=sum(x["npe"] > WRONG for x in agree),
                                concordantes_sem_gabarito=sum(not np.isfinite(x["npe"]) for x in agree),
                                todos_concordantes_errados=bool(agree) and all(x["npe"] > WRONG for x in agree)))
    write("vizinhos_aceitas_erradas", nb_rows)
    meta = dict(commit=head, tag="baseline-dev", clipes=len(res), calculados_aqui=f,
                aceitas_erradas=len(nb_rows), todos_concordantes_errados=sum(r["todos_concordantes_errados"] for r in nb_rows))
    (OUT / "baseline_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows + [med]:
        print(r)
    print(meta)
