"""Relatório do A' (docs/decisoes.md, 2026-10-22), pedido por Victor: (1) H da vista central recusadas pelo filtro
ellipse_consistent, por jogo; (2) o jogo 3 na checagem barata; (3) na confirmação, por jogo, as âncoras novas que
vieram de H do A' (frame sem H na série da base) e passaram no B1 e na verificação, quantas erradas (NPE > 0,05),
e o Δ de LocSim; o jogo 3 à parte.

(1) é exato na checagem barata: o A e o A' só diferem pelo filtro, então os frames com H central no A e sem H no A'
são os recusados (a_triagem_A × a_triagem). Na série da metade fixa a contagem não existe (a série grava H e notas,
não o motivo da recusa); o relatório diz isso e dá a contagem da checagem restrita aos clipes da metade.
Rode depois de rodada_6c_dev.py a_central. Saída: outputs/runs_v2/a_central/relatorio_a2.md.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/a2_relatorio.py"""
import csv
import pickle
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v2"))
from rodada_6c_dev import clips_dev                     # noqa: E402
from src_v2.config import path                          # noqa: E402
from src_v2.io import gsr                               # noqa: E402

GAMES, WRONG = ("4", "6", "9", "2", "3", "5"), 0.05
runs = path("runs")
L = ["# A' — relatório (pedido de Victor, 2026-10-22)", ""]

# (1) filtro na checagem barata
A = {(r["clipe"], r["t"]): r for r in csv.DictReader(open(runs / "a_triagem_A" / "frames.csv", encoding="utf-8"))}
A2 = {(r["clipe"], r["t"]): r for r in csv.DictReader(open(runs / "a_triagem" / "frames.csv", encoding="utf-8"))}
assert A.keys() == A2.keys()
half = {c.name for c in clips_dev(metade=True)}
cent, rej, rej_bad, cent_h, rej_h, other = Counter(), Counter(), Counter(), Counter(), Counter(), 0
for k, a in A.items():
    b, g = A2[k], a["jogo"]
    is_rej = a["central"] == "True" and b["a_ok"] == "False"
    cent[g] += a["central"] == "True"
    rej[g] += is_rej
    rej_bad[g] += is_rej and a["npe_a"] not in ("", "nan") and float(a["npe_a"]) > WRONG
    cent_h[g] += a["central"] == "True" and k[0] in half
    rej_h[g] += is_rej and k[0] in half
    other += not is_rej and (a["a_ok"], a["npe_a"]) != (b["a_ok"], b["npe_a"])
L += ["## 1. H da vista central recusadas pelo filtro `ellipse_consistent`", "",
      "Checagem barata (1 frame em 25, 115 clipes). Exato: o A e o A' só diferem pelo filtro "
      f"(frames com qualquer outra diferença entre as duas checagens: {other}).", "",
      "| jogo | H centrais (sem filtro) | recusadas pelo filtro | delas, erradas | só na metade fixa: H centrais / recusadas |",
      "|---|---|---|---|---|"]
for g in GAMES:
    L.append(f"| {g} | {cent[g]} | {rej[g]} | {rej_bad[g]} | {cent_h[g]} / {rej_h[g]} |")
tot_c, tot_r = sum(cent.values()), sum(rej.values())
L += ["", f"O filtro recusou {tot_r} de {tot_c} H centrais; **zero** nos jogos "
      f"{', '.join(g for g in GAMES if not rej[g])}. Como a H do A é construída a partir da própria elipse, o filtro é quase vazio.",
      "", "**Na série da metade fixa, a contagem não existe:** a série grava a H e as notas de cada frame, não o motivo da recusa; "
      "contá-la exatamente exigiria rodar de novo o detector sem o filtro nos frames sem H (quase o custo da série). "
      "A última coluna dá a contagem da checagem barata restrita aos clipes da metade fixa.", ""]

# (2) jogo 3 na checagem
t3 = {r["jogo"]: r for r in csv.DictReader(open(runs / "a_triagem" / "por_jogo.csv", encoding="utf-8"))}["3"]
L += ["## 2. Jogo 3 na checagem barata", "",
      f"A fração de aceitas erradas no jogo 3 vai de {float(t3['frac_erradas_base']):.4f} a {float(t3['frac_erradas_a']):.4f} "
      f"(+{float(t3['piora_erradas']):.4f}), com {t3['novas']} H novas, {t3['novas_erradas']} erradas. O A' passa na checagem "
      "**pela contagem mínima** (a piora só conta em jogo com >= 20 H novas), e **não** por evidência de que o filtro barra "
      f"encaixes errados: o filtro recusou {rej['3']} H centrais no jogo 3, e as {t3['novas_erradas']} H erradas do A passam por ele.", ""]

# (3) confirmação: âncoras novas vindas de H do A'
key_dir = path("cache")
pj = {r["jogo"]: r for r in csv.DictReader(open(runs / "a_central" / "por_jogo.csv", encoding="utf-8")) if r["particao"] != "mediana"}
rows = {g: Counter() for g in GAMES}
for c in clips_dev(metade=True):
    g = gsr.game_id(c)
    base_H = np.load(key_dir / "detector_base" / c.parent.name / f"{c.name}.npz")["H"]
    new_H = np.load(key_dir / "detector" / c.parent.name / f"{c.name}.npz")["H"]
    r_new = pickle.loads((key_dir / "eval_6c" / c.parent.name / f"{c.name}.pkl").read_bytes())[1]
    r_base = pickle.loads((key_dir / "eval_6c_b1" / c.parent.name / f"{c.name}.pkl").read_bytes())[1]
    acc_new = {a["t"]: a for a in r_new[2] if a["aceita"]}
    acc_base = {a["t"] for a in r_base[2] if a["aceita"]}
    from_a = [a for t, a in acc_new.items() if not np.isfinite(base_H[t]).all() and np.isfinite(new_H[t]).all()]
    rows[g]["ancoras_A"] += len(from_a)
    rows[g]["ancoras_A_erradas"] += sum(np.isfinite(a["npe"]) and a["npe"] > WRONG for a in from_a)
    rows[g]["cand_A"] += sum(1 for a in r_new[2] if not np.isfinite(base_H[a["t"]]).all())
    rows[g]["ancoras_base"] += len(acc_base)
    rows[g]["ancoras"] += len(acc_new)
    rows[g]["ancoras_base_perdidas"] += len(acc_base - set(acc_new))
L += ["## 3. Confirmação na metade fixa: âncoras que vieram de H do A'", "",
      "Âncora \"do A'\" = aceita (B1 + verificação por maioria) num frame em que a série da base não tinha H. "
      "Δ = LocSim@5 penalizado do 6c, A' − base B1, nos mesmos clipes.", "",
      "| jogo | candidatas do A' | âncoras do A' | delas, erradas (NPE > 0,05) | âncoras: base → A' | âncoras da base que saíram | Δ LocSim |",
      "|---|---|---|---|---|---|---|"]
for g in [x for x in GAMES if x != "3"] + ["3"]:
    r = rows[g]
    line = (f"| {g} | {r['cand_A']} | {r['ancoras_A']} | {r['ancoras_A_erradas']} | {r['ancoras_base']} → {r['ancoras']} | "
            f"{r['ancoras_base_perdidas']} | {float(pj[g]['delta_6c']):+.4f} |")
    if g == "3":
        L += ["", "**Jogo 3, à parte:**", "", "| jogo | candidatas do A' | âncoras do A' | delas, erradas (NPE > 0,05) | âncoras: base → A' | âncoras da base que saíram | Δ LocSim |",
              "|---|---|---|---|---|---|---|"]
    L.append(line)
txt = "\n".join(L) + "\n"
(runs / "a_central" / "relatorio_a2.md").write_text(txt, encoding="utf-8")
print(txt)
