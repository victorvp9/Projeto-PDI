"""Extras da rodada do test, por clipe, a partir dos caches (série do detector e 6c) e de
funções do src/ sem mudança:
- Kalman + RTS: métricas por frame (frame_metrics) da série de kalman_homographies com o
  q e o r do config (a etapa 6 só guarda estabilidade e visibilidade dele);
- cobertura por frame das cinco séries da T4b (detector, 6a Bassek, 6a robusto, Kalman, 6c fluxo);
- HSB, medição 1 ("só propagação", decisão de Victor): o passo normal do 6c
  (fill_from_anchors, modo "flow": Lucas-Kanade + linhas detectadas em cada frame), com uma
  única âncora no frame inicial do intervalo, H = H_gt_auxflow, sem âncora do detector.
  Frames do intervalo: [min(início, fim), max(início, fim)], o frame N do artigo é o índice
  N (000(N+1).jpg); no SNGS-128 (90 -> 0) a âncora é o 90 e a propagação vai para trás.
Grava outputs/runs/rodada_test/extras_test.pkl e o hash do commit dos scripts no manifesto. Uso (da raiz, PYTHONPATH=.): extras_test.py <trabalhadores>"""
import csv
import json
import pickle
import sys

import cv2
import numpy as np


def scripts_commit():
    """Hash do último commit de scripts/rodada_test; recusa rodar com alteração sem commit
    (decisão de Victor: as tabelas saem de scripts versionados, com o hash gravado)."""
    import subprocess
    here = "scripts/rodada_test"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", here], capture_output=True, text=True).stdout.strip()
    assert not dirty, "scripts com alteração sem commit: " + dirty
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", here], capture_output=True, text=True).stdout.strip()


def clip_extras(clip, hsb):
    from src import temporal as T
    from src.evaluate import frame_metrics
    from src.io import gsr
    cv2.setNumThreads(1)
    ser = dict(np.load(T._series_path(clip)))
    samples = gsr.load_clip(clip)
    size, n, game = samples[0].size, len(samples), gsr.game_id(clip)
    k6, res6 = pickle.loads(T._eval_6c_path(clip).read_bytes())
    assert k6 == T._eval_6c_key(), f"cache do 6c de {clip.name} de outro código"
    rows6, _, _, s6 = res6
    lac = {r["frame"]: r["lacuna"] for r in rows6 if r["variante"] == "detector"}
    kal = T.kalman_homographies(ser["H"], size, T.T["kalman_q"], T.T["kalman_r"])
    kal_rows = [dict(**frame_metrics(H if np.isfinite(H).all() else None, s), variante="Kalman + RTS", jogo=game,
                     lacuna=lac[s.frame_idx], n_pessoas=0 if s.persons_XY is None else len(s.persons_XY))
                for s, H in zip(samples, kal)]
    fin = lambda H: np.isfinite(np.asarray(H, float)).all(axis=(1, 2))
    cov5 = {"detector": fin(ser["H"]), "6a Bassek": fin(s6["6a Bassek"]), "6a robusto": fin(s6["6a robusto"]),
            "Kalman + RTS": fin(kal), "6c fluxo": fin(s6["6c fluxo"])}
    out = dict(clip=clip.name, jogo=game, kalman_rows=kal_rows, cov5=cov5)
    if hsb is not None:
        a, b = int(hsb["inicio"]), int(hsb["fim"])
        lo, hi = min(a, b), max(a, b)
        Hgt0 = samples[a].H_gt_auxflow
        out["hsb"] = dict(inicio=a, fim=b, H_auxflow_inicial=Hgt0 is not None)
        if Hgt0 is not None:
            cf = T.ClipFrames(samples)
            hists = [T.frame_hist(s.image) for s in samples]
            seg = np.cumsum(np.r_[False, [T.hist_distance(hists[i], hists[i + 1]) > T.T["cut_thr"] for i in range(n - 1)]])
            H_anchor = np.full((n, 3, 3), np.nan)
            H_anchor[a] = Hgt0
            Hs = T.fill_from_anchors(cf, [a], H_anchor, seg, "flow")
            out["hsb"]["rows"] = [dict(**frame_metrics(Hs[i] if np.isfinite(Hs[i]).all() else None, samples[i]), pos=i,
                                       n_pessoas=0 if samples[i].persons_XY is None else len(samples[i].persons_XY))
                                  for i in range(lo, hi + 1)]
            out["hsb"]["cortes_no_intervalo"] = int(seg[hi] != seg[lo])
    print(f"{clip.name} ok", flush=True)
    return out


if __name__ == "__main__":
    from src.config import path
    from src.executor import SafeProcessPool, exit_if_failed
    commit = scripts_commit()
    hsb = {r["clipe"]: r for r in csv.DictReader(open("data_splits/hsb.csv", encoding="utf-8"))}
    clips = sorted((path("gsr") / "test").glob("SNGS-*"))
    assert set(hsb) <= {c.name for c in clips}
    with SafeProcessPool(int(sys.argv[1]), initializer=cv2.setNumThreads, initargs=(1,)) as ex:
        res = [r for r in ex.map(clip_extras, clips, [hsb.get(c.name) for c in clips]) if r is not None]
    mpath = ex._last[4]                                  # manifesto da rodada: o hash dos scripts vai junto
    m = json.loads(mpath.read_text(encoding="utf-8"))
    m["commit_scripts"] = commit
    m["commit_metodo"] = json.loads((path("outputs") / "runs" / "congelamento.json").read_text(encoding="utf-8"))["commit"]
    mpath.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    out = path("outputs") / "runs" / "rodada_test" / "extras_test.pkl"
    out.write_bytes(pickle.dumps(dict(commit_scripts=commit, res=res)))
    print(f"{len(res)} de {len(clips)} clipes; HSB: {sum('hsb' in r for r in res)}; com H_gt_auxflow no frame inicial: "
          f"{sum(r['hsb']['H_auxflow_inicial'] for r in res if 'hsb' in r)}")
    print(out)
    exit_if_failed()
    sys.exit(0 if len(res) == len(clips) else 2)
