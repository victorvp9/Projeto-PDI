"""v2, achados 2 e 3 (docs/05-melhorias-plano.md, regra 1): conferência bit a bit do v2 contra o
v1 e regravação conferida das chaves (rekey) dos caches do v1 para o v2.

1. `confere`: nos clipes de CONFERENCIA (em cada jogo de dev, o primeiro clipe por ID com
   caches no v1: no treino, com série, 6c e ECC; na valid, com série e 6c), compara, valor a
   valor e bit a bit, o que o v2 calculou do zero (outputs/cache_v2, pela CLI
   `python -m src_v2.run --detect-series --propagate-eval --consequence-eval --clips ...`) com o
   cache do v1 (outputs/cache, só leitura): H de gabarito, série do detector, 6c e ECC. As
   chaves diferem (o v2 tem as chaves completas e os bytes do src_v2); o conteúdo tem que ser igual.
2. `regrava`: só se a conferência passou. Para cada cache do v1 no dev (train e valid) cuja
   chave gravada é a chave atual do v1, grava o mesmo conteúdo no cache do v2 com a chave do
   v2. O cache do v1 só é lido. Os já calculados pelo v2 ficam como estão.

Grava outputs/runs_v2/rekey.json com o resultado. Uso (da raiz): rekey.py confere|regrava"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np

import src.consequence as C1
import src.temporal as T1
import src_v2.consequence as C2
import src_v2.temporal as T2
from src.io import gsr as G1
from src_v2.io import gsr as G2
from src.config import path as path1
from src_v2.config import path as path2

CONFERENCIA = ["train/SNGS-060", "train/SNGS-099", "train/SNGS-154", "valid/SNGS-021", "valid/SNGS-039", "valid/SNGS-078"]
DEV = ("train", "valid")
OUT = path2("runs") / "rekey.json"


def same(a, b, where=""):
    """Igualdade exata e recursiva (arrays: mesmo dtype, forma e bytes; NaN no mesmo lugar)."""
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a, b = np.asarray(a), np.asarray(b)
        assert a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes(), f"diferente em {where}"
    elif isinstance(a, dict):
        assert isinstance(b, dict) and list(a) == list(b), f"chaves diferentes em {where}"
        for k in a:
            same(a[k], b[k], f"{where}/{k}")
    elif isinstance(a, (list, tuple)):
        assert type(a) is type(b) and len(a) == len(b), f"tamanho diferente em {where}"
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{where}[{i}]")
    elif isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        pass
    else:
        assert type(a) is type(b) and a == b, f"diferente em {where}: {a!r} != {b!r}"


def npz(p, skip=("key",)):
    d = np.load(p)
    return {k: d[k] for k in d.files if k not in skip}, str(d["key"])


def kinds(clip):
    """(nome, caminho no v1, caminho no v2, chave atual do v1, chave do v2, leitor)."""
    return [("H_gt", path1("outputs") / "cache" / "gsr" / clip.parent.name / f"{clip.name}.npz",
             path2("cache") / "gsr" / clip.parent.name / f"{clip.name}.npz", G1._cache_key(clip.name), G2._cache_key(clip.name), "npz"),
            ("série", T1._series_path(clip), T2._series_path(clip), T1._series_key(), T2._series_key(), "npz"),
            ("6c", T1._eval_6c_path(clip), T2._eval_6c_path(clip), T1._eval_6c_key(), T2._eval_6c_key(), "pkl"),
            ("ECC", C1._ecc_path(clip), C2._ecc_path(clip), C1._ecc_key(), C2._ecc_key(), "npz")]


def read(p, how):
    if how == "npz":
        return npz(p)
    k, res = pickle.loads(p.read_bytes())
    return res, k


def confere():
    out = []
    for name in CONFERENCIA:
        clip = path1("gsr") / name
        for kind, p1, p2, k1, k2, how in kinds(clip):
            if not p1.exists():
                out.append(dict(clipe=name, cache=kind, resultado="sem cache no v1"))
                continue
            c1, s1 = read(p1, how)
            assert s1 == k1, f"{name} {kind}: o cache do v1 não tem a chave atual do v1"
            assert p2.exists(), f"{name} {kind}: o v2 ainda não calculou"
            c2, s2 = read(p2, how)
            assert s2 == k2, f"{name} {kind}: o cache do v2 não tem a chave do v2"
            same(c1, c2, f"{name}/{kind}")
            out.append(dict(clipe=name, cache=kind, resultado="idêntico bit a bit", chave_v1=k1, chave_v2=k2))
            print(f"{name:16} {kind:6} idêntico bit a bit", flush=True)
    return out


def regrava():
    rep = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    assert rep.get("conferencia") and all(r["resultado"] != "diferente" for r in rep["conferencia"]), "rode `confere` antes"
    n = {}
    for split in DEV:
        for clip in sorted((path1("gsr") / split).glob("SNGS-*")):
            for kind, p1, p2, k1, k2, how in kinds(clip):
                if not p1.exists() or p2.exists():
                    n[(kind, "sem v1" if not p1.exists() else "já no v2")] = n.get((kind, "sem v1" if not p1.exists() else "já no v2"), 0) + 1
                    continue
                c, s1 = read(p1, how)
                if s1 != k1:                                     # cache velho no v1: não vale nem lá
                    n[(kind, "v1 com chave velha")] = n.get((kind, "v1 com chave velha"), 0) + 1
                    continue
                p2.parent.mkdir(parents=True, exist_ok=True)
                if how == "npz":
                    np.savez_compressed(p2, key=k2, **c) if kind != "H_gt" else np.savez(p2, key=k2, **c)
                else:
                    p2.write_bytes(pickle.dumps((k2, c)))
                c2, s2 = read(p2, how)                           # relido e conferido
                assert s2 == k2
                same(c, c2, f"{clip.name}/{kind} regravado")
                n[(kind, "regravado")] = n.get((kind, "regravado"), 0) + 1
    rep["regravacao"] = [dict(cache=k, situacao=s, clipes=v) for (k, s), v in sorted(n.items())]
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rep["regravacao"]:
        print(r)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "confere":
        try:
            res = confere()
        except AssertionError as e:
            res = [dict(resultado="diferente", erro=str(e))]
            print("FALHOU:", e)
        OUT.write_text(json.dumps(dict(conferencia=res), ensure_ascii=False, indent=1), encoding="utf-8")
        sys.exit(0 if all(r["resultado"] != "diferente" for r in res) else 1)
    regrava()
