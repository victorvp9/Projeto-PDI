"""Conferência de fechamento da etapa 1 (série do detector no GSR test), feita por fora do
src/ (decisão de Victor, 2026-10-02): o `ex.verify_keys` do build_series quebrou na linha
temporal.py:93 (o argumento de cada tarefa é a tupla (clipe, i0, i1, chave), e a lambda usa
a[0] como clipe). Mesmo critério do verify_keys: para cada tarefa concluída, a chave
gravada no cache do clipe tem que ser a chave da rodada (a chave congelada da série).

Grava no manifesto da etapa 1 o que o verify_keys gravaria (chave_rodada; chave_gravada por
tarefa; falha e status "falha" se divergir) e o campo "fechamento" com a nota; marca a
etapa 1 como feita (outputs/runs/rodada_test/1.ok) só se tudo bater. Nada no src/ muda.
Uso (da raiz, PYTHONPATH=.): fechamento_serie.py"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from src import temporal as T
from src.config import path

HERE = "scripts/rodada_test"
dirty = subprocess.run(["git", "status", "--porcelain", "--", HERE], capture_output=True, text=True).stdout.strip()
assert not dirty, "scripts com alteração sem commit: " + dirty
commit = subprocess.run(["git", "log", "-1", "--format=%H", "--", HERE], capture_output=True, text=True).stdout.strip()
frozen = json.loads((path("outputs") / "runs" / "congelamento.json").read_text(encoding="utf-8"))
key = T._series_key()
assert key == frozen["chaves"]["serie_detector"], "a chave da série de agora não é a congelada"
mp = [m for m in sorted(Path("outputs/runs").glob("series_chunk_*.json")) if "--splits test" in json.loads(m.read_text(encoding="utf-8"))["comando"]][-1]
man = json.loads(mp.read_text(encoding="utf-8"))
assert man["status"] == "concluída" and man["ok"] == man["total"] == 735 and man["falhas"] == 0, "manifesto da etapa 1 não está completo"
man["chave_rodada"] = key
bad = []
for t in man["tarefas"]:
    clip = t["tarefa"].split()[0]                                  # o clipe é o 1º elemento da tupla (a[0][0])
    p = T._series_path(path("gsr") / "test" / clip)
    t["chave_gravada"] = str(np.load(p)["key"]) if p.exists() else None
    if t["chave_gravada"] != key:
        bad.append(t["tarefa"])
        t["ok"], t["erro"] = False, f"chave gravada {str(t['chave_gravada'])[:12]} != chave da rodada {key[:12]}"
if bad:
    man["ok"] -= len(bad)
    man["falhas"] += len(bad)
    man["status"] = "falha"
clips = sorted({t["tarefa"].split()[0] for t in man["tarefas"]})
man["fechamento"] = dict(
    nota="feita por fora, mesmo critério, por defeito na linha temporal.py:93",
    data=datetime.now().isoformat(timespec="seconds"), script=f"{HERE}/fechamento_serie.py", commit_scripts=commit,
    commit_metodo=frozen["commit"], tarefas=len(man["tarefas"]), clipes=len(clips), divergentes=bad)
mp.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{mp.name}: {len(man['tarefas'])} tarefas em {len(clips)} clipes; chave gravada = chave da rodada {key[:12]} em "
      f"{len(man['tarefas']) - len(bad)}; divergentes: {len(bad)}")
if bad:
    sys.exit(2)
(Path("outputs/runs/rodada_test") / "1.ok").write_text(json.dumps(dict(
    manifesto=mp.name, status=man["status"], ok=man["ok"], falhas=man["falhas"], total=man["total"],
    nota="etapa 1 marcada como feita depois da conferência de fechamento por fora (decisão de Victor, 2026-10-02)")), encoding="utf-8")
print("etapa 1 marcada como feita (1.ok)")
