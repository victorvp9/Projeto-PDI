"""Etapa 4 do 8.2: H de gabarito do GSR test, calculada uma vez, com a chave registrada no
congelamento. Os caches antigos da Fatia 2 (chave velha) vão para
outputs/cache/gsr_test_fatia2 antes. Confere, no fim, a chave guardada de cada clipe contra
outputs/runs/congelamento.json. Uso (da raiz, PYTHONPATH=.): hgt_test.py <trabalhadores>"""
import json
import shutil
import sys

import numpy as np


def fit_clip_cache(clip):
    from src.io import gsr
    gsr.load_clip(clip)                    # chave nova != guardada -> ajusta e grava
    return clip.name


if __name__ == "__main__":
    from src.config import path
    from src.executor import SafeProcessPool, exit_if_failed
    frozen = json.loads((path("outputs") / "runs" / "congelamento.json").read_text(encoding="utf-8"))["chaves"]["h_gt_test"]
    clips = sorted((path("gsr") / "test").glob("SNGS-*"))
    assert [c.name for c in clips] == sorted(frozen), "clipes do test diferentes dos do congelamento"
    cache, bak = path("outputs") / "cache" / "gsr" / "test", path("outputs") / "cache" / "gsr_test_fatia2"
    bak.mkdir(parents=True, exist_ok=True)
    old = {}
    for f in cache.glob("*.npz"):
        old[f.stem] = str(np.load(f)["key"])
        if not (bak / f.name).exists():
            shutil.copy2(f, bak / f.name)
    print(f"caches antigos: {len(old)}; com a chave registrada: {sum(old[c] == frozen[c] for c in old)}")
    with SafeProcessPool(int(sys.argv[1])) as ex:
        done = [r for r in ex.map(fit_clip_cache, clips) if r is not None]
    keys = {c.name: str(np.load(cache / f"{c.name}.npz")["key"]) for c in clips}
    bad = [c for c in keys if keys[c] != frozen[c]]
    print(f"H_gt do test: {len(done)} de {len(clips)} clipes; com a chave registrada: {len(clips) - len(bad)}; divergentes: {bad}")
    exit_if_failed()
    sys.exit(0 if not bad and len(done) == len(clips) else 2)
