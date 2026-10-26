"""Executor seguro (src_v2/executor.py): uma tarefa que falha não derruba as outras, vai
para o manifesto e deixa o código de saída != 0. Com threads (sem pool de processos no
pytest); o código de saída é conferido num subprocesso."""
import json
import os
import subprocess
import sys

from src_v2 import executor
from src_v2.executor import SafeThreadPool


def _task(i):
    if i == 2:
        raise ValueError("clipe 2 quebrou")
    return i * 10


def test_failing_task_does_not_stop_the_others(tmp_path):
    executor.FAILURES.clear()
    with SafeThreadPool(2, manifest_dir=tmp_path) as ex:
        res = list(ex.map(_task, range(5)))
    assert res == [0, 10, None, 30, 40]
    (manifest,) = tmp_path.glob("_task_*.json")
    m = json.loads(manifest.read_text(encoding="utf-8"))
    assert m["status"] == "concluída" and m["ok"] == 4 and m["falhas"] == 1
    (bad,) = [t for t in m["tarefas"] if not t["ok"]]
    assert bad["tarefa"] == "2" and "clipe 2 quebrou" in bad["erro"] and "Traceback" in bad["traceback"]
    assert len(executor.FAILURES) == 1
    executor.FAILURES.clear()


def test_worker_with_other_code_becomes_a_failure(tmp_path):
    """Trabalhador cuja chave (do código que ele importou) não é a recebida do processo
    principal: a tarefa falha antes de tocar nos dados e vai para o manifesto."""
    from pathlib import Path
    from src_v2 import temporal
    executor.FAILURES.clear()
    with SafeThreadPool(2, manifest_dir=tmp_path) as ex:
        a = list(ex.map(temporal._eval_clip_6c_cached, [Path("SNGS-000")], ["chave-de-outro-codigo"]))
        b = list(ex.map(temporal.series_chunk, [(Path("SNGS-000"), 0, 1, "chave-de-outro-codigo")]))
    assert a == [None] and b == [None]
    erros = [t["erro"] for m in tmp_path.glob("*.json") for t in json.loads(m.read_text(encoding="utf-8"))["tarefas"]]
    assert len(erros) == 2 and all("código diferente do da rodada" in e for e in erros)
    executor.FAILURES.clear()


def test_round_closing_flags_stored_key_mismatch(tmp_path):
    """Fechamento da rodada: tarefa que terminou bem mas gravou com outra chave vira falha
    e a rodada fica com status "falha"."""
    executor.FAILURES.clear()
    with SafeThreadPool(2, manifest_dir=tmp_path) as ex:
        list(ex.map(_task, [0, 1, 3]))
        ex.verify_keys("chave-da-rodada", lambda args: "chave-da-rodada" if args[0] != 3 else "outra")
    (manifest,) = tmp_path.glob("_task_*.json")
    m = json.loads(manifest.read_text(encoding="utf-8"))
    assert m["status"] == "falha" and m["ok"] == 2 and m["falhas"] == 1
    assert [t["tarefa"] for t in m["tarefas"] if not t["ok"]] == ["3"]
    assert len(executor.FAILURES) == 1
    executor.FAILURES.clear()


def test_exit_code_is_nonzero_when_a_task_fails(tmp_path):
    script = ("import sys; from src_v2.executor import SafeThreadPool, exit_if_failed\n"
              "def f(i):\n    if i == int(sys.argv[1]): raise RuntimeError('falhou')\n    return i\n"
              f"with SafeThreadPool(2, manifest_dir=r'{tmp_path}') as ex: print(list(ex.map(f, range(3))))\n"
              "exit_if_failed()\n")
    bad = subprocess.run([sys.executable, "-c", script, "1"], capture_output=True, text=True)
    good = subprocess.run([sys.executable, "-c", script, "99"], capture_output=True, text=True)
    assert bad.returncode == 1 and "[0, None, 2]" in bad.stdout, bad.stdout + bad.stderr
    assert good.returncode == 0 and "[0, 1, 2]" in good.stdout, good.stdout + good.stderr


def test_worker_with_other_fingerprint_fails_before_running():
    """Impressão digital do código (bytes de src_v2/*.py na importação): a tarefa que chega
    com a de outro código falha sem rodar; com a do processo principal, roda."""
    ran = []
    ok, res, err, _ = executor._call(ran.append, (1,), "impressao-de-outro-codigo")
    assert not ok and res is None and "código diferente do processo principal" in err["erro"] and ran == []
    ok, res, err, _ = executor._call(_task, (1,), executor.FINGERPRINT)
    assert ok and res == 10 and err is None


def test_process_pool_sets_worker_blas_threads(monkeypatch):
    """O pool põe OPENBLAS_NUM_THREADS no ambiente antes de criar os trabalhadores (que o
    herdam). Sem tarefa, nenhum processo nasce: o teste não abre pool de processos."""
    from src_v2.config import CFG
    monkeypatch.setenv("OPENBLAS_NUM_THREADS", "16")
    with executor.SafeProcessPool(1) as ex:
        assert os.environ["OPENBLAS_NUM_THREADS"] == str(CFG["executor"]["worker_blas_threads"])
        assert not ex._processes
