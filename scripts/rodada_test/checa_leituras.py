"""Item 2 do incidente da etapa 1 (decisão de Victor, 2026-10-02): testa, SEM executar as
etapas, as funções de leitura das conferências que as etapas 2 a 6 e o fechamento vão usar,
com os argumentos reais da rodada do test.

As lambdas do `verify_keys` são as do src/ (extraídas do código-fonte com ast e avaliadas no
namespace do próprio módulo), e os argumentos são montados como o SafeMap.map monta
(`list(zip(*iterables))`, com os mesmos iteráveis das chamadas reais). Nada é gravado.
Uso (da raiz, PYTHONPATH=.): checa_leituras.py ; código 0 só se tudo passar."""
import ast
import json
import sys
from pathlib import Path

import numpy as np

from src import consequence, temporal as T
from src.config import path


def lambdas(module):
    """As lambdas passadas a ex.verify_keys no fonte do módulo, avaliadas no namespace dele
    mais os imports locais da função onde a chamada está (o evaluate_6c importa o pickle no
    corpo, e a lambda real enxerga esse import)."""
    src = Path(module.__file__).read_text(encoding="utf-8")
    out = []
    for fn in ast.walk(ast.parse(src)):
        if not isinstance(fn, ast.FunctionDef):
            continue
        local = dict(vars(module))
        for st in fn.body:
            if isinstance(st, (ast.Import, ast.ImportFrom)):
                exec(compile(ast.Module(body=[st], type_ignores=[]), "imp", "exec"), local)
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "verify_keys":
                out.append((n.lineno, eval(ast.get_source_segment(src, n.args[1]), local)))
    return out


fails, frozen = [], json.loads((path("outputs") / "runs" / "congelamento.json").read_text(encoding="utf-8"))["chaves"]
test = sorted((path("gsr") / "test").glob("SNGS-*"))           # como o run.py monta com --splits test --clip-step 1
train3 = sorted((path("gsr") / "train").glob("SNGS-*"))[::3]


def check(name, fn, items, expect):
    """Chama a função de leitura em cada item; `expect(item, valor)` diz se o valor é o esperado."""
    try:
        vals = [fn(a) for a in items]
        bad = [(a[0] if not isinstance(a[0], tuple) else a[0][0], v) for a, v in zip(items, vals) if not expect(a, v)]
    except Exception as e:                                       # noqa: BLE001
        fails.append(name)
        print(f"QUEBRA  {name}: {type(e).__name__}: {e}")
        return
    if bad:
        fails.append(name)
    print(f"{'ok     ' if not bad else 'ERRADO '} {name}: {len(items)} chamadas" + (f"; inesperados: {[(getattr(c, 'name', c), v) for c, v in bad[:3]]}" if bad else ""))


# --- verify_keys do src/
(l_series,), (l_6c,) = [[f for ln, f in lambdas(T) if ln == k] for k in (93, 723)]
(l_ecc,) = [f for _, f in lambdas(consequence)]
chunks = [(c, 0, 50, frozen["serie_detector"]) for c in test]                  # map(series_chunk, chunks): 1 iterável
try:                                                                           # defeito conhecido (incidente da etapa 1)
    l_series(list(zip(chunks))[0])
    fails.append("série, temporal.py:93 deveria quebrar e não quebrou")
    print("ERRADO  série, temporal.py:93: não reproduz o defeito registrado")
except AttributeError as e:
    print(f"ok      série, temporal.py:93: reproduz o defeito registrado ({e}); conferência feita por fora")
check("série, a mesma leitura com o clipe em a[0][0] (a conferência por fora)",
      lambda a: str(np.load(T._series_path(a[0][0]))["key"]), list(zip(chunks)), lambda a, v: v == frozen["serie_detector"])
check("6c, temporal.py:723, test (caches ainda não existem: None esperado)", l_6c,
      list(zip(test, [frozen["6c"]] * len(test))), lambda a, v: v is None)
check("6c, temporal.py:723, train[::3] (caches existem: a chave congelada)", l_6c,
      list(zip(train3, [frozen["6c"]] * len(train3))), lambda a, v: v == frozen["6c"])
check("ECC, consequence.py:102, test (caches ainda não existem: None esperado)", l_ecc,
      list(zip(test, [frozen["6c"]] * len(test), [frozen["ecc"]] * len(test))), lambda a, v: v is None)
sub = [path("gsr") / "train" / c for c in ("SNGS-060", "SNGS-070", "SNGS-099", "SNGS-109", "SNGS-154", "SNGS-164")]
check("ECC, consequence.py:102, subconjunto do train (caches existem: a chave congelada)", l_ecc,
      list(zip(sub, [frozen["6c"]] * 6, [frozen["ecc"]] * 6)), lambda a, v: v == frozen["ecc"])

# --- conferências dos scripts da rodada que ainda não rodaram no test
read_key = lambda c: str(np.load(path("outputs") / "cache" / "gsr" / "test" / f"{c.name}.npz")["key"])
check("hgt_test.py: chave guardada da H_gt do test (antes do recálculo: chaves da Fatia 2)", lambda a: read_key(a[0]),
      [(c,) for c in test], lambda a, v: isinstance(v, str) and len(v) == 40)
check("hgt_test.py: clipes do test = clipes do congelamento", lambda a: sorted(c.name for c in test) == sorted(frozen["h_gt_test"]),
      [(None,)], lambda a, v: v is True)
m1 = sorted(Path("outputs/runs").glob("series_chunk_*.json"))[-1]
labels = [t["tarefa"].split() for t in json.loads(m1.read_text(encoding="utf-8"))["tarefas"]]
check("conferencia_det.py: rótulo das tarefas da série (clipe i0 i1 chave)", lambda a: (a[0][0], int(a[0][1]), int(a[0][2])),
      [(lb,) for lb in labels], lambda a, v: v[0].startswith("SNGS-") and v[2] - v[1] == 50)
check("conferencia_det.py: série do test (frames e H por clipe)", lambda a: dict(np.load(T._series_path(a[0]))),
      [(c,) for c in test], lambda a, v: len(v["frames"]) == 750 and v["H"].shape == (750, 3, 3))
man = json.loads(m1.read_text(encoding="utf-8"))
check("tabelas_test.py T9: parede da série (início e fim do manifesto)", lambda a: man["fim"] > man["inicio"] and "--splits test" in man["comando"],
      [(None,)], lambda a, v: v is True)

print(f"\n{'TUDO OK' if not fails else 'FALHOU: ' + '; '.join(fails)}")
sys.exit(1 if fails else 0)
