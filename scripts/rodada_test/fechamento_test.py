"""Fechamento da rodada do test: espera a rodada_test.py registrar FIM (se registrar PAROU,
sai sem rodar nada), confere o congelamento como lá, roda extras_test.py (Kalman, cobertura
das cinco séries, HSB medição 1; manifesto com a conferência) e tabelas_test.py (T1-T9).
Retomável pelos marcadores outputs/runs/rodada_test/f<n>.ok. Log em rodada.log, linhas [fechamento]."""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path("outputs/runs/rodada_test")
LOG = OUT / "rodada.log"
src = (HERE / "rodada_test.py").read_text(encoding="utf-8")
ns = {"__file__": str(HERE / "rodada_test.py")}
exec(src[:src.index("OUT.mkdir(parents=True, exist_ok=True)\nlog(")], ns)   # só as definições (freeze_check, manifests, ENV, PY)
freeze_check, manifests, ENV, PY = ns["freeze_check"], ns["manifests"], ns["ENV"], ns["PY"]


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[fechamento] {datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


while True:
    text = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    if "PAROU" in text:
        log("a rodada parou: fechamento não roda")
        sys.exit(1)
    if "FIM: etapas 1-6" in text:
        break
    time.sleep(120)
log("início")
for n, (name, prefixes, cmd) in enumerate([
        ("extras: Kalman + RTS, cobertura das cinco séries, HSB medição 1", ["clip_extras"], [PY, "-u", str(HERE / "extras_test.py"), "10"]),
        ("tabelas T1-T9", [], [PY, "-u", str(HERE / "tabelas_test.py")])], 1):
    done = OUT / f"f{n}.ok"
    if done.exists():
        log(f"ETAPA f{n} já feita: {name}")
        continue
    before = freeze_check()
    if not before["ok"]:
        log(f"PAROU antes de f{n}: conferência do congelamento não bate: {before}")
        sys.exit(4)
    log(f"ETAPA f{n}: {name} (congelamento conferido)")
    t0 = datetime.now().timestamp()
    with (OUT / f"f{n}.out").open("w", encoding="utf-8") as f:
        code = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=ENV).returncode
    after = freeze_check()
    ms = manifests(prefixes, t0)
    for m in ms:
        d = json.loads(m.read_text(encoding="utf-8"))
        d["congelamento"] = dict(antes=before, depois=after)
        m.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    info = [(m.name, (d := json.loads(m.read_text(encoding="utf-8")))["status"], d["ok"], d["falhas"], d["total"]) for m in ms]
    bad = code != 0 or not after["ok"] or len(ms) < len(prefixes) or any(s != "concluída" or f or o != t for _, s, o, f, t in info)
    log(f"   manifestos: {info}; código {code}; congelamento depois: {'ok' if after['ok'] else after}")
    if bad:
        log(f"PAROU em f{n}: {name}. Saída em {OUT / f'f{n}.out'}. Nada foi corrigido.")
        sys.exit(1)
    done.write_text(json.dumps(info), encoding="utf-8")
    log(f"ETAPA f{n} OK")
log("FIM: extras e tabelas prontos")
