"""Rodada única do test (Fatia 8, ordem do 8.2; aprovada por Victor em 2026-10-01). Retomável:
etapa feita fica marcada em outputs/runs/rodada_test/<n>.ok, e as tarefas têm checkpoint
(série e H_gt por clipe, 6c por clipe, ECC por clipe).

Conferência do congelamento (pedido de Victor), ANTES e DEPOIS de cada etapa, gravada em
cada manifesto que a etapa criou (campo "congelamento"): `git diff --quiet 418a3be -- src
config.yaml` (árvore de trabalho) e `git diff --quiet 418a3be HEAD -- src config.yaml`
vazios, SHA-1 do config e as chaves (série, 6c, ECC, impressão digital do código)
recalculadas iguais às de outputs/runs/congelamento.json. É feita aqui, fora do src/,
porque mudar o executor quebraria o próprio congelamento.

PARA (código != 0) em qualquer falha: código da etapa != 0, manifesto com falha ou
tarefa faltando, ou conferência do congelamento que não bate. Nada é corrigido aqui.
Log: outputs/runs/rodada_test/rodada.log, linhas [rodada]."""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path("outputs/runs/rodada_test")
LOG = OUT / "rodada.log"
FROZEN = json.loads(Path("outputs/runs/congelamento.json").read_text(encoding="utf-8"))
COMMIT = FROZEN["commit"]
PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONPATH": "."}
STAGES = [
    ("série do detector no GSR test (49 clipes)", ["series_chunk"], [PY, "-u", "-m", "src.run", "--workers", "15", "--detect-series", "--splits", "test", "--clip-step", "1"]),
    ("detector no WC14 test (186 imagens) e no GSR test a cada 25 frames", ["_detect_gsr_clip", "_detect_wc14"],
     [PY, "-u", "-m", "src.run", "--workers", "15", "--detect", "--splits", "test", "--wc14-split", "test"]),
    ("H de gabarito do GSR test", ["fit_clip_cache"], [PY, "-u", str(HERE / "hgt_test.py"), "15"]),
    ("avaliação do detector: WC14 test e GSR test a cada 25 frames", ["_eval_clip", "_eval_wc14"],
     [PY, "-u", "-m", "src.run", "--workers", "15", "--evaluate", "outputs/pred_td6_e1_test_wc14-test.npz", "--splits", "test"]),
    ("6c no GSR test (com 6a Bassek, 6a robusto e as ablações)", ["_eval_clip_6c_cached"],
     [PY, "-u", "-m", "src.run", "--workers", "10", "--propagate-eval", "--splits", "test", "--clip-step", "1"]),
    ("estabilidade (ECC), visibilidade e Kalman + RTS no GSR test", ["_eval_clip_7"], [PY, "-u", str(HERE / "consequencia_test.py"), "15"]),
]


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[rodada] {datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


def freeze_check():
    """Conferência do congelamento: dict com o resultado de cada item e 'ok'."""
    files = ["src", "config.yaml"]
    q = ("from src import temporal, consequence, executor; import json; "
         "print(json.dumps(dict(serie_detector=temporal._series_key(), **{'6c': temporal._eval_6c_key()}, "
         "ecc=consequence._ecc_key(), impressao_digital_codigo=executor.FINGERPRINT)))")
    keys = json.loads(subprocess.run([PY, "-c", q], capture_output=True, text=True, env=ENV, check=True).stdout)
    c = dict(
        data=datetime.now().isoformat(timespec="seconds"), commit=COMMIT,
        head=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        diff_arvore_vazio=subprocess.run(["git", "diff", "--quiet", COMMIT, "--"] + files).returncode == 0,
        diff_head_vazio=subprocess.run(["git", "diff", "--quiet", COMMIT, "HEAD", "--"] + files).returncode == 0,
        config_sha1_igual=hashlib.sha1(Path("config.yaml").read_bytes()).hexdigest() == FROZEN["config_sha1"],
        chaves_iguais={k: v == FROZEN["chaves"][k] for k, v in keys.items()})
    c["ok"] = c["diff_arvore_vazio"] and c["diff_head_vazio"] and c["config_sha1_igual"] and all(c["chaves_iguais"].values())
    return c


def manifests(prefixes, since):
    return [m for p in prefixes for m in sorted(Path("outputs/runs").glob(f"{p}_*.json")) if m.stat().st_mtime >= since]


OUT.mkdir(parents=True, exist_ok=True)
log("início")
for n, (name, prefixes, cmd) in enumerate(STAGES, 1):
    done = OUT / f"{n}.ok"
    if done.exists():
        log(f"ETAPA {n} já feita: {name}")
        continue
    before = freeze_check()
    if not before["ok"]:
        log(f"PAROU antes da etapa {n}: conferência do congelamento não bate: {before}")
        sys.exit(4)
    log(f"ETAPA {n}: {name} (congelamento conferido)")
    t0 = datetime.now().timestamp()
    with (OUT / f"{n}.out").open("w", encoding="utf-8") as f:
        code = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=ENV).returncode
    after = freeze_check()
    ms = manifests(prefixes, t0)
    for m in ms:                                     # a conferência vai para o manifesto da rodada
        d = json.loads(m.read_text(encoding="utf-8"))
        d["congelamento"] = dict(antes=before, depois=after)
        m.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    info = [(m.name, (d := json.loads(m.read_text(encoding="utf-8")))["status"], d["ok"], d["falhas"], d["total"]) for m in ms]
    bad = code != 0 or not after["ok"] or len(ms) < len(prefixes) or any(s != "concluída" or f or o != t for _, s, o, f, t in info)
    log(f"   manifestos: {info}; código {code}; congelamento depois: {'ok' if after['ok'] else after}")
    if bad:
        log(f"PAROU na etapa {n}: {name}. Saída em {OUT / f'{n}.out'}. Nada foi corrigido.")
        sys.exit(1)
    done.write_text(json.dumps(info), encoding="utf-8")
    log(f"ETAPA {n} OK")
log("FIM: etapas 1-6 concluídas")
