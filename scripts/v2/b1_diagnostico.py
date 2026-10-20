"""B1, etapa 1 (decisoes.md, 2026-10-15): diagnóstico, sem regra, de sinais independentes dos
vizinhos imediatos para separar âncoras candidatas certas de erradas (NPE > 0,05 contra a H_gt),
em todas as candidatas de dev com gabarito. Não roda o detector: usa a série e o 6c do cache_v2
(linha de base, tag baseline-dev), as imagens e funções do src_v2 sem mudança.

Sinais, na candidata t (H = a do detector em t):
  a. consistência com âncoras distantes: das âncoras aceitas do mesmo plano, fora do trecho
     contíguo de frames com H do detector que contém t e a mais de 25 frames, a mais próxima de
     cada lado; a H dela é levada a t por Lucas–Kanade (temporal.propagate, sem linhas, como na
     verificação) e mede-se a discordância com H na imagem (evaluate.image_grid_displacement, em
     fração da altura). a_min: a menor entre os lados; a_n: quantos lados existem.
  b. linhas na imagem inteira, contra a máscara de marcações do frame (a do 6c), com a tolerância
     da nota do detector (assign.score_tol_frac·h): b_total, fração do comprimento do modelo
     projetado e visível (no gramado, sem jogadores) com marca a <= tol; b_longe, o mesmo só nas
     linhas longe da área (arcos da área, lateral próxima, linha do meio); b_min, a menor fração
     entre as classes com comprimento visível >= 0,1·h; b_expl, fração das marcas dentro do campo
     projetado a <= tol de alguma linha do modelo.
  c. o que a série já guarda (termos da nota do detector): img, mod, iou, margem, nota = iou + img.

Separação por jogo: AUC (erradas × certas), e a fração das erradas recusadas com o limiar que
recusa no máximo 2% das certas, com o sentido e o limiar escolhidos só nos jogos do treino
(4, 6, 9) e conferidos na valid (2, 3, 5); para todas as candidatas e só para as aceitas.
Saída: outputs/runs_v2/b1_diagnostico/. Uso (da raiz): PYTHONPATH=. uv run python
scripts/v2/b1_diagnostico.py <trabalhadores>"""
import csv
import json
import pickle
import subprocess
import sys
from collections import defaultdict

import cv2
import numpy as np

from src_v2.config import CFG, path

OUT = path("runs") / "b1_diagnostico"
DEV = ("train", "valid")
TRAIN_GAMES, VALID_GAMES = ("4", "6", "9"), ("2", "3", "5")
WRONG, FAR_FRAMES, MAX_RIGHT_REJECT = 0.05, 25, 0.02
FAR_CLASSES = ("Circle left", "Circle right", "Side line bottom", "Middle line")   # arcos da área, lateral próxima, linha do meio
SIGNALS = ["a_min", "b_total", "b_longe", "b_min", "b_expl", "img", "mod", "iou", "margem", "nota"]


def clip_signals(clip):
    import src_v2.temporal as T
    from src_v2.assign import A
    from src_v2.evaluate import image_grid_displacement
    from src_v2.geometry import project
    from src_v2.io import gsr
    from src_v2.pitch_model import POLYLINES
    from src_v2.render import axis_mask, pitch_mask
    cv2.setNumThreads(1)
    k6, r6 = pickle.loads(T._eval_6c_path(clip).read_bytes())
    assert k6 == T._eval_6c_key(), f"{clip.name}: 6c de outro código"
    cand = [a for a in r6[2] if np.isfinite(a["npe"])]
    if not cand:
        return []
    ser = T.load_series(clip)
    samples = gsr.load_clip(clip, fit="none")
    n, game = len(samples), gsr.game_id(clip)
    cf = T.ClipFrames(samples)
    size, h = cf.size, cf.size[1]
    hists = [T.frame_hist(s.image) for s in samples]
    seg = np.cumsum(np.r_[False, [T.hist_distance(hists[i], hists[i + 1]) > T.T["cut_thr"] for i in range(n - 1)]])
    ok = np.isfinite(ser["H"]).all(axis=(1, 2))
    run = np.cumsum(np.r_[True, ok[1:] != ok[:-1]])               # trechos contíguos de H / sem H
    accepted = [a["t"] for a in r6[2] if a["aceita"]]

    # a: âncoras distantes de cada lado e uma propagação por (âncora, sentido) até a candidata mais longe
    far = {}
    need = defaultdict(int)
    for c in cand:
        t = c["t"]
        ok_far = [a for a in accepted if seg[a] == seg[t] and abs(a - t) > FAR_FRAMES and run[a] != run[t]]
        sides = [max([a for a in ok_far if a < t], default=None), min([a for a in ok_far if a > t], default=None)]
        far[t] = [(a, 1 if a < t else -1) for a in sides if a is not None]
        for a, step in far[t]:
            need[(a, step)] = max(need[(a, step)], abs(t - a))
    prop = {(a, step): T.propagate(cf, a, ser["H"][a], a + step * (d + 1), step, lines=False) for (a, step), d in need.items()}

    tol = A["score_tol_frac"] * h
    rows = []
    for c in cand:
        t = c["t"]
        H = ser["H"][t]
        d = [image_grid_displacement(prop[(a, step)][t], H, size) / h for a, step in far[t] if t in prop[(a, step)]]
        d = [x for x in d if np.isfinite(x)]
        marks, keep = cf.masks(t)
        dist = cv2.distanceTransform((~marks).astype(np.uint8), cv2.DIST_L2, 5)
        visible = keep | marks
        vis, sup = {}, {}
        for name, poly in POLYLINES.items():
            uv, front = project(H, poly)
            seglen = np.r_[np.linalg.norm(np.diff(uv, axis=0), axis=1), 0.0]
            seglen = np.minimum(np.nan_to_num(seglen, nan=0.0), 0.05 * h)
            inside = front & (uv[:, 0] >= 0) & (uv[:, 0] <= size[0] - 1) & (uv[:, 1] >= 0) & (uv[:, 1] <= size[1] - 1)
            u, v = np.round(uv[inside, 0]).astype(int), np.round(uv[inside, 1]).astype(int)
            on = visible[v, u]
            vis[name] = float(seglen[inside][on].sum())
            sup[name] = float(seglen[inside][on][dist[v, u][on] <= tol].sum())
        frac = lambda names: sum(sup[k] for k in names) / sum(vis[k] for k in names) if sum(vis[k] for k in names) >= 0.05 * h else np.nan
        big = [k for k in vis if vis[k] >= 0.1 * h]
        field = pitch_mask(H, size)
        dm = cv2.distanceTransform((~axis_mask(H, size)).astype(np.uint8), cv2.DIST_L2, 5)
        mk = marks & field
        i = t                                                     # a série tem um registro por frame, na ordem do clipe (como no 6c)
        rows.append(dict(particao=clip.parent.name, clipe=clip.name, jogo=game, t=int(t), npe=float(c["npe"]), errada=bool(c["npe"] > WRONG),
                         verificavel=bool(c["verificavel"]), aceita=bool(c["aceita"]),
                         a_min=min(d) if d else np.nan, a_n=len(d),
                         b_total=frac(list(vis)), b_longe=frac(FAR_CLASSES), b_min=min((sup[k] / vis[k] for k in big), default=np.nan),
                         b_expl=float((dm[mk] <= tol).mean()) if mk.any() else np.nan,
                         img=float(ser["img"][i]), mod=float(ser["mod"][i]), iou=float(ser["iou"][i]), margem=float(ser["margem"][i]),
                         nota=float(ser["iou"][i] + ser["img"][i])))
    print(f"{clip.parent.name}/{clip.name}: {len(rows)} candidatas com gabarito", flush=True)
    return rows


def auc(pos, neg):
    """P(sinal de uma errada > sinal de uma certa), empates valendo 1/2."""
    from scipy.stats import rankdata
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return np.nan
    r = rankdata(np.r_[pos, neg])
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def separation(rows):
    """Por sinal: sentido e limiar escolhidos no treino (todas as candidatas); por jogo e subconjunto,
    AUC, cobertura do sinal e as frações recusadas."""
    out = []
    train = [r for r in rows if r["jogo"] in TRAIN_GAMES]
    for s in SIGNALS:
        def vals(rs):
            return np.array([r[s] for r in rs], float)
        tr_w, tr_r = vals([r for r in train if r["errada"]]), vals([r for r in train if not r["errada"]])
        a = auc(tr_w[np.isfinite(tr_w)], tr_r[np.isfinite(tr_r)])
        sign = 1.0 if a >= 0.5 else -1.0                           # sentido: valor alto (após o sinal) = errada
        rr = sign * tr_r[np.isfinite(tr_r)]
        thr = float(np.quantile(rr, 1 - MAX_RIGHT_REJECT, method="higher")) if len(rr) else np.nan   # recusa: sign·s > thr
        for subset, keep in (("candidatas", lambda r: True), ("aceitas", lambda r: r["aceita"])):
            for g in TRAIN_GAMES + VALID_GAMES + ("treino", "valid"):
                rs = [r for r in rows if keep(r) and (r["jogo"] == g or (g == "treino" and r["jogo"] in TRAIN_GAMES)
                                                      or (g == "valid" and r["jogo"] in VALID_GAMES))]
                w, ri = vals([r for r in rs if r["errada"]]), vals([r for r in rs if not r["errada"]])
                rej = lambda x: float(np.mean(np.isfinite(x) & (sign * np.where(np.isfinite(x), x, 0.0) > thr))) if len(x) else np.nan
                out.append(dict(sinal=s, sentido="alto = errada" if sign > 0 else "baixo = errada", limiar=sign * thr, subconjunto=subset, jogo=g,
                                certas=len(ri), erradas=len(w), cobertura=float(np.mean(np.isfinite(np.r_[w, ri]))) if len(rs) else np.nan,
                                auc=auc(sign * w[np.isfinite(w)], sign * ri[np.isfinite(ri)]),
                                erradas_recusadas=rej(w), certas_recusadas=rej(ri)))
    return out


def write(name, rows):
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    from src_v2.executor import SafeProcessPool, exit_if_failed
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    assert not git("status", "--porcelain", "--", "src_v2", "config_v2.yaml", "scripts/v2"), "código do v2 com alteração sem commit"
    OUT.mkdir(parents=True, exist_ok=True)
    clips = [c for s in DEV for c in sorted((path("gsr") / s).glob("SNGS-*"))]
    with SafeProcessPool(int(sys.argv[1]), initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=OUT / "manifestos") as ex:
        res = list(ex.map(clip_signals, clips))
    exit_if_failed()
    assert all(r is not None for r in res)
    rows = [x for r in res for x in r]
    write("sinais_por_candidata", rows)
    sep = separation(rows)
    write("separacao", sep)
    (OUT / "meta.json").write_text(json.dumps(dict(commit=git("rev-parse", "HEAD"), candidatas=len(rows),
                                                   erradas=sum(r["errada"] for r in rows)), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} candidatas com gabarito, {sum(r['errada'] for r in rows)} erradas")
    for r in sep:
        if r["jogo"] in ("treino", "valid"):
            print(f"{r['sinal']:8} {r['subconjunto']:10} {r['jogo']:6} AUC {r['auc']:.3f} cob {r['cobertura']:.2f} erradas recusadas {r['erradas_recusadas']:.3f} certas {r['certas_recusadas']:.3f}")
