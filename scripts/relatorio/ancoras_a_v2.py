"""De onde vêm as âncoras do A' (pedido de Victor, 2026-10-26), só pelos caches; nada do método roda.

- Dev, jogo 3, base B1 + A': as H do A' são as dos frames com H na série atual e sem H na série da base guardada
  (outputs/cache_v2/detector_base/, scripts/v2/serie_a_metade.py). Para cada uma: se virou candidata, se é
  verificável, se foi aceita e o NPE (6c em cache). Grava outputs/runs_v2/base_b1a_local/a_jogo3.csv.
- Test, SNGS-147: a série do v1 não está neste PC e a do v2 não marca as H do A', então a origem da âncora só se
  apura se o frame estiver na amostra de 1 em 25 do v1 (outputs/pred_td6_e1_test_wc14-test.npz, chave = frame + 1).
  Grava outputs/runs_v2/rodada_test_v2/sngs147.csv: os frames da amostra (H no v1 e no v2) e a âncora aceita.
Uso (da raiz): PYTHONPATH=. uv run python scripts/relatorio/ancoras_a_v2.py"""
import csv
import pickle

import numpy as np

from src_v2 import temporal as T
from src_v2.config import path


def write(p, rows):
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(p, len(rows), "linhas")


has_h = lambda H: np.isfinite(H).all(axis=(1, 2))
key = T._eval_6c_key()
rows = []
for c in sorted((path("gsr") / "valid").glob("SNGS-*")):
    k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
    if str(r[0][0]["jogo"]) != "3":
        continue
    assert k == key, f"{c.name}: cache do 6c com outra chave"
    base = np.load(path("cache") / "detector_base" / "valid" / f"{c.name}.npz")["H"]
    cur = np.load(path("cache") / "detector" / "valid" / f"{c.name}.npz")["H"]
    anc = {a["t"]: a for a in r[2]}
    for t in np.nonzero(~has_h(base) & has_h(cur))[0]:
        a = anc.get(int(t))
        rows.append(dict(clipe=c.name, frame=int(t), candidata=a is not None, verificavel=bool(a and a["verificavel"]),
                         aceita=bool(a and a["aceita"]), npe=float(a["npe"]) if a else np.nan))
write(path("runs") / "base_b1a_local" / "a_jogo3.csv", rows)

c = path("gsr") / "test" / "SNGS-147"
k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
ser = np.load(path("cache") / "detector" / "test" / "SNGS-147.npz")
ok, pos = has_h(ser["H"]), {int(f): i for i, f in enumerate(ser["frames"])}
v1 = np.load(path("outputs").parent / "pred_td6_e1_test_wc14-test.npz")
rows = [dict(tipo="amostra do v1", frame=pos[int(kk.split("/")[-1])], v1_tem_H=bool(np.isfinite(v1[kk]).all()),
             v2_tem_H=bool(ok[pos[int(kk.split("/")[-1])]]), npe=np.nan) for kk in v1.files if kk.startswith("gsr/test/SNGS-147/")]
rows.sort(key=lambda x: x["frame"])
rows += [dict(tipo="âncora aceita", frame=a["t"], v1_tem_H="", v2_tem_H=True, npe=float(a["npe"])) for a in r[2] if a["aceita"]]
write(path("runs") / "rodada_test_v2" / "sngs147.csv", rows)
