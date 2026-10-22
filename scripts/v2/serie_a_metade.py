"""v2, A': série do detector com o A nos clipes da metade fixa, reaproveitando a série da base.

O A só roda nos frames em que a 2 + 2 não dá H aceita (assign.detect_frame): nos frames em que a série da
base tem H, a saída com o A é a mesma, e ela é copiada; o detector roda só nos outros. A série da base fica
guardada intacta em outputs/cache_v2/detector_base/ (copiada uma vez, antes de qualquer gravação); a nova
é gravada em outputs/cache_v2/detector/ com a chave do código atual, no formato de temporal.build_series,
para o 6c (rodada_6c_dev.py --metade) a ler. Retomável: clipe já gravado com a chave atual é pulado.
Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/serie_a_metade.py [trabalhadores]"""
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from rodada_6c_dev import clips_dev                      # noqa: E402
from src_v2.config import CFG, path                      # noqa: E402

STEP = 50                                                # frames por tarefa (como temporal.series_chunk)


def base_path(clip):
    return path("cache") / "detector_base" / clip.parent.name / f"{clip.name}.npz"


def chunk(args):
    """Detector (com o A) nos frames `idx` do clipe; devolve (frame_idx, H, info) de cada um."""
    from src_v2.assign import detect_frame
    from src_v2.executor import check_key
    from src_v2.io import gsr
    from src_v2.temporal import SERIES_KEYS, _series_key
    clip, idx, key = args
    check_key(key, _series_key(), "série do A")
    cv2.setNumThreads(1)
    samples = gsr.load_clip(clip, fit="none")
    out = []
    for i in idx:
        H, info = next(iter(detect_frame(samples[i].image, "gsr").values()))
        out.append((i, np.full((3, 3), np.nan) if H is None else H,
                    [float(info.get(k, np.nan)) if info.get(k) is not None else np.nan for k in SERIES_KEYS]))
    return clip, out


if __name__ == "__main__":
    from src_v2.executor import SafeProcessPool, exit_if_failed
    from src_v2.temporal import SERIES_KEYS, _series_key, _series_path
    assert CFG["assign"]["central_view"], "a série do A pede assign.central_view ligado"
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    src, dst = path("cache") / "detector", path("cache") / "detector_base"
    if not dst.exists():
        shutil.copytree(src, dst)
        print(f"série da base guardada em {dst}", flush=True)
    key = _series_key()
    clips = clips_dev(metade=True)
    todo = [c for c in clips if not (_series_path(c).exists() and str(np.load(_series_path(c))["key"]) == key)]
    print(f"série do A: {len(clips) - len(todo)} de {len(clips)} clipes já gravados", flush=True)
    base = {c: dict(np.load(base_path(c))) for c in todo}
    tasks = []
    for c in todo:
        nan = np.nonzero(~np.isfinite(base[c]["H"]).all(axis=(1, 2)))[0]
        tasks += [(c, list(nan[k:k + STEP]), key) for k in range(0, len(nan), STEP)]
    left = {c: sum(t[0] == c for t in tasks) for c in todo}
    new = {c: [] for c in todo}
    for c in todo:
        if not left[c]:                                   # sem frame sem H: a série do A é a da base
            b = base[c]
            np.savez_compressed(_series_path(c), key=key, frames=b["frames"], H=b["H"], **{k: b[k] for k in SERIES_KEYS})
            print(f"   {c.parent.name}/{c.name}: nenhum frame a rodar", flush=True)
    out_dir = path("runs") / "a_serie_metade"
    with SafeProcessPool(n, initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=out_dir / "manifestos") as ex:
        for res in ex.map(chunk, tasks):
            if res is None:
                continue
            c, rows = res
            new[c] += rows
            left[c] -= 1
            if left[c]:
                continue
            b = base[c]
            H, info = b["H"].copy(), {k: b[k].copy() for k in SERIES_KEYS}
            for i, Hi, inf in new[c]:
                H[i] = Hi
                for j, k in enumerate(SERIES_KEYS):
                    info[k][i] = inf[j]
            np.savez_compressed(_series_path(c), key=key, frames=b["frames"], H=H, **info)
            print(f"   {c.parent.name}/{c.name}: {len(new[c])} frames rodados, {int(np.isfinite(H).all(axis=(1, 2)).sum() - np.isfinite(b['H']).all(axis=(1, 2)).sum())} H novas", flush=True)
    exit_if_failed()
