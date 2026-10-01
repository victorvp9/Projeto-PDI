"""Execução paralela à prova de falha silenciosa (decisão de Victor, 2026-09-30).

`map` roda cada tarefa dentro de try/except no processo (ou thread) que a executa: a
que falha rende None e as outras seguem. Cada rodada grava um manifesto em
`outputs/runs/<função>_<data>.json` — status, contagens e, por tarefa concluída, o
rótulo, a duração e, se falhou, o erro e o traceback — atualizado a cada tarefa, para
o vigia ler durante a rodada. As falhas vão para FAILURES, e `exit_if_failed` (chamado
no fim da CLI) sai com código != 0 se houve alguma.
"""
import hashlib
import json
import sys
import threading
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from src.config import ROOT, path

FAILURES = []            # falhas desta execução (processo principal)
# Impressão digital do código: bytes de todos os src/*.py, lidos UMA vez, na importação
# deste módulo (no processo principal, no início da CLI; no trabalhador, quando ele nasce).
# Cada tarefa leva a do processo principal, e o trabalhador que nasceu depois de uma edição
# falha antes de rodar, em vez de rodar código diferente (decisão de Victor, 2026-09-30).
FINGERPRINT = hashlib.sha1(b"".join(p.read_bytes() for p in sorted((ROOT / "src").rglob("*.py")))).hexdigest()


def _call(fn, args, fingerprint):
    """Roda fn(*args) no trabalhador, se ele roda o código do processo principal; nunca
    propaga exceção: (ok, resultado, erro, s)."""
    t = time.time()
    try:
        if fingerprint != FINGERPRINT:
            raise RuntimeError(f"trabalhador com código diferente do processo principal: impressão digital {FINGERPRINT[:12]} != {fingerprint[:12]}")
        return True, fn(*args), None, time.time() - t
    except Exception as e:
        return False, None, dict(erro=repr(e), traceback=traceback.format_exc()), time.time() - t


def _label(args):
    """Rótulo legível de uma tarefa: nomes de caminhos, números e textos curtos."""
    parts = []
    for a in args:
        for x in (a if isinstance(a, tuple) else (a,)):
            parts.append(x.name if isinstance(x, Path) else str(x) if isinstance(x, (int, float, str)) or x is None else type(x).__name__)
    return " ".join(parts)[:120]


class SafeMap:
    """Mistura para um Executor: `map` seguro com manifesto."""

    def __init__(self, *a, manifest_dir=None, **k):
        super().__init__(*a, **k)
        self._dir = Path(manifest_dir) if manifest_dir else path("outputs") / "runs"
        self._lock = threading.Lock()

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        items = list(zip(*iterables))
        name = getattr(fn, "__name__", "tarefa")
        man = dict(rodada=name, comando=" ".join(sys.argv), inicio=datetime.now().isoformat(timespec="seconds"),
                   status="rodando", total=len(items), ok=0, falhas=0, tarefas=[])
        self._dir.mkdir(parents=True, exist_ok=True)
        mpath = self._dir / f"{name}_{datetime.now():%Y%m%d_%H%M%S_%f}.json"

        def write():
            mpath.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")

        def outcome(f):
            try:
                return f.result()
            except Exception as e:                       # o próprio pool quebrou (processo morto etc.)
                return False, None, dict(erro=repr(e), traceback=traceback.format_exc()), 0.0

        def record(f, label):                            # na ordem em que as tarefas terminam
            ok, _, err, secs = outcome(f)
            with self._lock:
                man["ok" if ok else "falhas"] += 1
                man["tarefas"].append(dict(tarefa=label, ok=ok, segundos=round(secs, 1), **(err or {})))
                if not ok:
                    FAILURES.append(dict(rodada=name, tarefa=label, manifesto=str(mpath), **err))
                    print(f"FALHA em {name}: {label}: {err['erro']} (manifesto: {mpath})", flush=True)
                if man["ok"] + man["falhas"] == man["total"]:
                    man["status"] = "concluída"
                    man["fim"] = datetime.now().isoformat(timespec="seconds")
                write()

        if not items:
            man["status"] = "concluída"
        write()
        futs = [self.submit(_call, fn, args, FINGERPRINT) for args in items]     # submete já, como o map original
        for args, f in zip(items, futs):
            f.add_done_callback(lambda f, label=_label(args): record(f, label))

        self._last = (man, write, items, name, mpath)

        def results():                                   # na ordem de entrada; None para a que falhou
            for f in futs:
                ok, res, _, _ = outcome(f)
                yield res if ok else None
        return results()


    def verify_keys(self, round_key, stored_key):
        """Fechamento da rodada (depois de consumir os resultados do último `map`): grava
        no manifesto a chave gravada por tarefa (`stored_key(args)`) e marca falha em cada
        tarefa concluída cuja chave gravada não é a da rodada; a rodada fica com status
        "falha"."""
        man, write, items, name, mpath = self._last
        with self._lock:
            by_label = {t["tarefa"]: t for t in man["tarefas"]}
            man["chave_rodada"] = round_key
            for args in items:
                t = by_label.get(_label(args))
                if t is None or not t["ok"]:
                    continue
                stored = stored_key(args)
                t["chave_gravada"] = stored
                if stored != round_key:
                    t["ok"] = False
                    t["erro"] = f"chave gravada {str(stored)[:12]} != chave da rodada {round_key[:12]}"
                    man["ok"] -= 1
                    man["falhas"] += 1
                    FAILURES.append(dict(rodada=name, tarefa=t["tarefa"], manifesto=str(mpath), erro=t["erro"]))
                    print(f"FALHA em {name}: {t['tarefa']}: {t['erro']} (manifesto: {mpath})", flush=True)
            if man["falhas"]:
                man["status"] = "falha"
            write()


class SafeProcessPool(SafeMap, ProcessPoolExecutor):
    pass


class SafeThreadPool(SafeMap, ThreadPoolExecutor):
    pass


def check_key(received, own, what):
    """No trabalhador: a chave recebida do processo principal tem de ser a que o próprio
    trabalhador calcula com o código que importou; senão ele roda código diferente do da
    rodada (arquivo editado depois de o processo principal calcular a chave) e grava com a
    chave errada. Lança exceção: o executor registra a falha no manifesto."""
    if received != own:
        raise RuntimeError(f"trabalhador com código diferente do da rodada ({what}): chave {own[:12]} != {received[:12]} da rodada")


def exit_if_failed():
    """Fim da CLI: resume as falhas e sai com código 1 se houve alguma."""
    if FAILURES:
        print(f"\n{len(FAILURES)} tarefa(s) falharam:", flush=True)
        for f in FAILURES:
            print(f"   {f['rodada']}: {f['tarefa']}: {f['erro']}  ({f['manifesto']})")
        sys.exit(1)
