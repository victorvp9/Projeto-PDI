"""Conferência da série do v2 no GSR test contra as H do detector v1 (docs/decisoes.md, 2026-10-23).

A série do v1 no test não está neste PC; as H do detector v1 a 1 frame em 25 estão em
outputs/pred_td6_e1_test_wc14-test.npz (chave gsr/test/<clipe>/<frame_idx>). Regra: em todo frame em
que o v1 tem H, a H da série do v2 tem de ser bit a bit igual; onde o v1 não tem H, o v2 pode ter H
(o A' só roda nesses frames). Qualquer outra diferença reprova, e o 6c não roda.
Grava outputs/runs_v2/rodada_test_v2/conferencia_v1.json. Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/rodada_test_v2/confere_v1_test.py"""
import json
import sys

import numpy as np

from src_v2.config import path
from src_v2.temporal import load_series

v1 = np.load(path("outputs").parent / "pred_td6_e1_test_wc14-test.npz")
clips = sorted((path("gsr") / "test").glob("SNGS-*"))
iguais = novas = ambos_sem = 0
falhas = []
for c in clips:
    ser = load_series(c)                                   # confere a chave da série do v2
    pos = {int(f): i for i, f in enumerate(ser["frames"])}
    for k in [k for k in v1.files if k.startswith(f"gsr/test/{c.name}/")]:
        f = int(k.split("/")[-1])
        H1, H2 = v1[k], ser["H"][pos[f]]
        ok1, ok2 = np.isfinite(H1).all(), np.isfinite(H2).all()
        if ok1 and ok2 and np.array_equal(H1, H2):
            iguais += 1
        elif not ok1 and ok2:
            novas += 1
        elif not ok1 and not ok2:
            ambos_sem += 1
        else:
            falhas.append(dict(clipe=c.name, frame=f, v1_tem_H=bool(ok1), v2_tem_H=bool(ok2),
                               dif_max=float(np.abs(H1 / H1[2, 2] - H2 / H2[2, 2]).max()) if ok1 and ok2 else None))
res = dict(aprovado=not falhas, clipes=len(clips), frames=iguais + novas + ambos_sem + len(falhas), iguais_bit_a_bit=iguais,
           novas_no_v2=novas, sem_H_nos_dois=ambos_sem, falhas=falhas[:50], n_falhas=len(falhas))
out = path("runs") / "rodada_test_v2"
out.mkdir(parents=True, exist_ok=True)
(out / "conferencia_v1.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in res.items() if k != "falhas"}, ensure_ascii=False))
sys.exit(0 if res["aprovado"] else 1)
