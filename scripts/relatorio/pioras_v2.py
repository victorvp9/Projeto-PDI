"""Diagnóstico dos clipes do test que pioram do v1 para o v2 (pedido de Victor, 2026-10-24), só a partir dos
caches da rodada do test do v2 (série e 6c); nada é recalculado. Uma linha por candidata a âncora: frame, NPE
contra a H_gt, nota (iou + img da série) e a situação: "aceita"; "B1" se a nota está abaixo de
temporal.anchor_min_nota (o B1 a recusa, passe ou não na maioria); "maioria" se passa na nota e cai na
verificação por maioria; "não verificável" se tem menos de verify_min vizinhos com H.
Para as recusadas pela maioria, os frames da janela de voto (+-verify_window) que estão na amostra de 1 em 25
do detector v1 (outputs/pred_td6_e1_test_wc14-test.npz, chave = frame + 1) e se têm H no v1 e no v2: um frame
sem H no v1 e com H no v2 é H do A' entre os votantes.
Grava outputs/runs_v2/rodada_test_v2/pioras.csv e pioras_vizinhos.csv.
Uso (da raiz): PYTHONPATH=. uv run python scripts/relatorio/pioras_v2.py [clipes...]"""
import csv
import pickle
import sys

import numpy as np

from src_v2 import temporal as T
from src_v2.config import CFG, path

clips = sys.argv[1:] or ["SNGS-136", "SNGS-123"]
thr, W = CFG["temporal"]["anchor_min_nota"], CFG["temporal"]["verify_window"]
v1 = np.load(path("outputs").parent / "pred_td6_e1_test_wc14-test.npz")
rows, viz = [], []
for c in clips:
    ser = np.load(path("cache") / "detector" / "test" / f"{c}.npz")
    k, r = pickle.loads(T._eval_6c_path(path("gsr") / "test" / c).read_bytes())
    for a in sorted(r[2], key=lambda a: a["t"]):
        t = a["t"]
        nota = float(ser["iou"][t] + ser["img"][t])
        sit = "aceita" if a["aceita"] else "não verificável" if not a["verificavel"] else "B1" if nota < thr else "maioria"
        rows.append(dict(clipe=c, frame=t, situacao=sit, npe=float(a["npe"]), nota=nota, limiar_b1=thr))
        if sit == "maioria":
            for u in range(max(0, t - W), min(len(ser["H"]), t + W + 1)):
                key = f"gsr/test/{c}/{int(ser['frames'][u])}"
                if u != t and key in v1.files:
                    viz.append(dict(clipe=c, candidata=t, vizinho=u, v1_tem_H=bool(np.isfinite(v1[key]).all()),
                                    v2_tem_H=bool(np.isfinite(ser["H"][u]).all())))
out = path("runs") / "rodada_test_v2"
for name, rs in (("pioras.csv", rows), ("pioras_vizinhos.csv", viz)):
    with (out / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rs[0]))
        w.writeheader()
        w.writerows(rs)
for r in rows + viz:
    print(r)
