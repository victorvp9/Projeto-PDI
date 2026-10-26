"""Conferência do 6c do v2 no GSR test contra o v1, clipe a clipe (pedido de Victor, 2026-10-23), depois do 6c
e antes das tabelas. Referência: outputs/runs/rodada_test/falhas/clipes_test.csv (o v1 publicado, por clipe).

- "Sem H nova do A'" num clipe: a cobertura do detector (frames com H_gt) e o LocSim@5 penalizado do detector
  iguais aos do v1 (a série do v1 não está neste PC, então não dá para marcar frame a frame as H do A').
- Nesses clipes, com candidatas, verificáveis e aceitas iguais às do v1 (o B1 não recusou âncora): o LocSim@5
  penalizado do 6c, o teto e as aceitas têm de bater com o v1 (tolerância 1e-9). Divergência = reprova.
- Nesses clipes, com aceitas a menos (o B1 recusou): só a diferença, reportada.
- Os clipes com H nova do A': só a diferença, reportada.
Também: os clipes sem âncora aceita (v1: SNGS-127, 128, 134, 138, 147) e, para cada um dos 5 do v1, se o v2 tem
âncora e o NPE dela. Grava outputs/runs_v2/rodada_test_v2/conferencia_v1_6c.json; código 1 se reprovar.
Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/rodada_test_v2/confere_v1_6c.py"""
import csv
import json
import pickle
import sys

import numpy as np

from src_v2 import temporal as T
from src_v2.config import path
from src_v2.evaluate import locsim

TOL, WRONG = 1e-9, 0.05
V1_SEM_ANCORA = ["SNGS-127", "SNGS-128", "SNGS-134", "SNGS-138", "SNGS-147"]


def pen(rows):
    n = sum(r.get("n_pessoas", 0) for r in rows)
    return sum(locsim(r["locsim_d"], 5).sum() for r in rows if "locsim_d" in r) / n if n else np.nan


v1 = {r["clipe"]: r for r in csv.DictReader(open("outputs/runs/rodada_test/falhas/clipes_test.csv", encoding="utf-8"))}
key = T._eval_6c_key()
same = lambda a, b: (np.isnan(a) and np.isnan(b)) or abs(a - b) <= TOL
rows, falhas = [], []
for c in sorted((path("gsr") / "test").glob("SNGS-*")):
    k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
    assert k == key, f"{c.name}: cache do 6c com outra chave"
    rv = {v: [x for x in r[0] if x["variante"] == v] for v in ("detector", "6c fluxo", "6c âncora de gabarito")}
    anc = r[2]
    acc = [a for a in anc if a["aceita"]]
    m = dict(clipe=c.name, jogo=rv["detector"][0]["jogo"], det=pen(rv["detector"]), c6=pen(rv["6c fluxo"]), teto=pen(rv["6c âncora de gabarito"]),
             cob_det=float(np.mean([x["has_pred"] for x in rv["detector"] if x["has_gt"]])), candidatas=len(anc),
             verificaveis=sum(a["verificavel"] for a in anc), aceitas=len(acc),
             aceitas_erradas=sum(1 for a in acc if np.isfinite(a["npe"]) and a["npe"] > WRONG),
             npe_aceitas=[round(float(a["npe"]), 4) for a in acc if np.isfinite(a["npe"])])
    o = v1[c.name]
    f = lambda k: float(o[k])
    sem_nova = same(m["cob_det"], f("cob_det")) and same(m["det"], f("det"))
    b1_nada = sem_nova and m["candidatas"] == int(o["candidatas"]) and m["verificaveis"] == int(o["verificaveis"]) and m["aceitas"] == int(o["aceitas"])
    m |= dict(sem_h_nova=sem_nova, b1_nao_recusou=b1_nada, v1_c6=f("c6"), v1_teto=f("teto"), v1_aceitas=int(o["aceitas"]),
              v1_candidatas=int(o["candidatas"]), v1_verificaveis=int(o["verificaveis"]), d_c6=m["c6"] - f("c6"), d_teto=m["teto"] - f("teto"))
    if sem_nova and (m["candidatas"] != int(o["candidatas"]) or m["verificaveis"] != int(o["verificaveis"])):
        falhas.append(dict(clipe=c.name, motivo="sem H nova, mas candidatas ou verificáveis diferem do v1"))
    if b1_nada and not (same(m["c6"], f("c6")) and same(m["teto"], f("teto"))):
        falhas.append(dict(clipe=c.name, motivo="sem H nova e sem recusa do B1, mas 6c ou teto diferem do v1", d_c6=m["d_c6"], d_teto=m["d_teto"]))
    rows.append(m)

sem = [m["clipe"] for m in rows if m["aceitas"] == 0]
res = dict(aprovado=not falhas, falhas=falhas,
           clipes=len(rows), sem_h_nova=sum(m["sem_h_nova"] for m in rows), sem_h_nova_e_b1_nada=sum(m["b1_nao_recusou"] for m in rows),
           sem_h_nova_b1_recusou=[dict(clipe=m["clipe"], aceitas_v1=m["v1_aceitas"], aceitas_v2=m["aceitas"], d_c6=m["d_c6"], d_teto=m["d_teto"])
                                  for m in rows if m["sem_h_nova"] and not m["b1_nao_recusou"]],
           com_h_nova=[dict(clipe=m["clipe"], d_c6=m["d_c6"], d_teto=m["d_teto"], aceitas_v1=m["v1_aceitas"], aceitas_v2=m["aceitas"])
                       for m in rows if not m["sem_h_nova"]],
           clipes_sem_ancora_v2=sem,
           v1_sem_ancora=[dict(clipe=c, ancoras_v2=next(m["aceitas"] for m in rows if m["clipe"] == c),
                               npe_ancoras_v2=next(m["npe_aceitas"] for m in rows if m["clipe"] == c),
                               c6_v1=next(m["v1_c6"] for m in rows if m["clipe"] == c), c6_v2=next(m["c6"] for m in rows if m["clipe"] == c))
                          for c in V1_SEM_ANCORA])
out = path("runs") / "rodada_test_v2"
out.mkdir(parents=True, exist_ok=True)
# tipos do numpy (contagens de bool) viram tipos do Python no json
(out / "conferencia_v1_6c.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=lambda o: o.item()), encoding="utf-8")
with (out / "clipes_test_v2.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"aprovado: {res['aprovado']} | clipes sem H nova do A': {res['sem_h_nova']} (sem recusa do B1: {res['sem_h_nova_e_b1_nada']}; "
      f"com recusa: {len(res['sem_h_nova_b1_recusou'])}) | com H nova: {len(res['com_h_nova'])} | falhas: {len(falhas)}")
for x in falhas:
    print("   FALHA", x)
sys.exit(0 if res["aprovado"] else 1)
