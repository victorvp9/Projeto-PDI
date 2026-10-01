"""Etapa 6 do 8.2: estabilidade (ECC) e visibilidade no GSR test pela função da Fatia 7
(consequence.evaluate_7, sem mudança), com um pool que guarda também os resultados por
clipe (para a T4b, a interseção dos frames cobertos). Grava
outputs/runs/rodada_test/consequencia_test.pkl. Uso (da raiz, PYTHONPATH=.): consequencia_test.py <trabalhadores>"""
import pickle
import sys

import cv2

CAP = []


if __name__ == "__main__":
    from src import consequence
    from src.config import path
    from src.executor import SafeProcessPool, exit_if_failed

    class Tee(SafeProcessPool):
        def map(self, fn, *iterables, **kw):
            items = [list(it) for it in iterables]
            out = list(super().map(fn, *items, **kw))
            CAP.append(([a.name for a in items[0]], out))
            return out

    clips = sorted((path("gsr") / "test").glob("SNGS-*"))
    table = consequence.evaluate_7(lambda: Tee(int(sys.argv[1]), initializer=cv2.setNumThreads, initargs=(1,)), clips)
    out = path("outputs") / "runs" / "rodada_test" / "consequencia_test.pkl"
    out.parent.mkdir(parents=True, exist_ok=True)
    names, res = CAP[0]
    out.write_bytes(pickle.dumps(dict(clipes=names, res=res, tabela=table)))
    print(out)
    exit_if_failed()
