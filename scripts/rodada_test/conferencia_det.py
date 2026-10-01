"""Conferência de determinismo entre as etapas 1 e 2 da rodada do test (regra de Victor,
2026-10-01): nos 1.470 frames do GSR test a cada 25 (etapa 2, `--detect`), a H tem que ser
bit a bit igual à da série da etapa 1 (`--detect-series`), que usa o mesmo código.

Espera a etapa 2 fechar (outputs/runs/rodada_test/2.ok), compara e grava o resultado:
- no manifesto da etapa 2 (_detect_gsr_clip) e no da etapa 1 (series_chunk), campo
  "conferencia_serie";
- em outputs/runs/rodada_test/conferencia_det.json, que o extras_test.py exige aprovado.
Se algum frame diferir: lista o frame, as duas H e a tarefa e o manifesto de cada uma, e
registra PAROU no rodada.log, o que impede o fechamento. Nada é corrigido.
Uso (da raiz, PYTHONPATH=.): conferencia_det.py"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

OUT = Path("outputs/runs/rodada_test")
LOG = OUT / "rodada.log"


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[conferencia] {datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


def latest(prefix, needle):
    ms = [m for m in sorted(Path("outputs/runs").glob(f"{prefix}_*.json")) if needle in json.loads(m.read_text(encoding="utf-8"))["comando"]]
    return ms[-1]


if __name__ == "__main__":
    from src import temporal as T
    from src.config import path
    while not (OUT / "2.ok").exists():
        if "PAROU" in (LOG.read_text(encoding="utf-8") if LOG.exists() else ""):
            sys.exit(1)
        time.sleep(120)
    preds = np.load(path("outputs") / "pred_td6_e1_test_wc14-test.npz")
    keys = [k for k in preds.files if k.startswith("gsr/test/")]
    m1, m2 = latest("series_chunk", "--detect-series"), latest("_detect_gsr_clip", "--detect")
    chunks = [t["tarefa"].split() for t in json.loads(m1.read_text(encoding="utf-8"))["tarefas"]]
    series, diff = {}, []
    for k in keys:
        _, _, clip, fidx = k.split("/")
        if clip not in series:
            series[clip] = dict(np.load(T._series_path(path("gsr") / "test" / clip)))
        ser = series[clip]
        pos = int(np.nonzero(ser["frames"] == int(fidx))[0][0])
        a, b = preds[k], ser["H"][pos]
        if a.dtype != b.dtype or a.tobytes() != b.tobytes():
            task1 = next((" ".join(c[:3]) for c in chunks if c[0] == clip and int(c[1]) <= pos < int(c[2])), "?")
            diff.append(dict(clipe=clip, frame=int(fidx), posicao=pos, H_etapa2=a.tolist(), H_etapa1=b.tolist(),
                             etapa2=f"--detect, tarefa {clip}, manifesto {m2.name}", etapa1=f"--detect-series, tarefa {task1}, manifesto {m1.name}"))
    res = dict(data=datetime.now().isoformat(timespec="seconds"), frames=len(keys), clipes=len(series), iguais=len(keys) - len(diff),
               diferentes=len(diff), aprovado=not diff and len(keys) == 1470, divergencias=diff,
               nota="os manifestos não guardam o PID dos trabalhadores; o processo de cada H é identificado pela etapa e pela tarefa")
    for m in (m1, m2):
        d = json.loads(m.read_text(encoding="utf-8"))
        d["conferencia_serie"] = {k: v for k, v in res.items() if k != "divergencias"} | dict(n_divergencias=len(diff))
        m.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "conferencia_det.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if res["aprovado"]:
        log(f"OK: {len(keys)} frames do GSR test a cada 25 (etapa 2) bit a bit iguais à série da etapa 1, em {len(series)} clipes")
        sys.exit(0)
    log(f"PAROU: {len(diff)} de {len(keys)} frames diferem entre a etapa 2 e a série da etapa 1 (ver conferencia_det.json); "
        "o fechamento não roda")
    sys.exit(2)
