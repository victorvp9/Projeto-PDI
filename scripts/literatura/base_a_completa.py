"""Nova base do v2 (B1 + A', docs/decisoes.md 2026-10-22) no dev inteiro: 6c nos clipes da outra metade (a
metade fixa já tem o 6c do A' em cache) e a tabela por jogo dos 115 clipes em outputs/runs_v2/base_b1a_local/,
contra a qual as hipóteses seguintes são medidas. Confere que os 115 caches do 6c têm a chave atual.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/base_a_completa.py [trabalhadores]"""
import csv
import pickle
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v2"))
from baseline_dev import per_game                       # noqa: E402
from rodada_6c_dev import clips_dev                      # noqa: E402
from src_v2.config import CFG, path                      # noqa: E402

if __name__ == "__main__":
    import src_v2.temporal as T
    from src_v2.executor import SafeProcessPool, exit_if_failed
    assert CFG["assign"]["central_view"] and CFG["temporal"]["anchor_c_max_m"] is None and not CFG["temporal"]["bidirectional"]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    out = path("runs") / "base_b1a_local"
    out.mkdir(parents=True, exist_ok=True)
    half = set(clips_dev(metade=True))
    other = [c for c in clips_dev() if c not in half]
    key = T._eval_6c_key()
    with SafeProcessPool(n, initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=out / "manifestos") as ex:
        list(ex.map(T._eval_clip_6c_cached, other, [key] * len(other)))
        ex.verify_keys(key, lambda a: pickle.loads(T._eval_6c_path(a[0]).read_bytes())[0] if T._eval_6c_path(a[0]).exists() else None)
    exit_if_failed()
    res = {}
    for c in clips_dev():
        k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
        assert k == key, f"{c.name}: cache do 6c com outra chave"
        res[c] = r
    rows, med = per_game(res)
    with (out / "por_jogo.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows + [med] for k in r)))
        w.writeheader()
        w.writerows(rows + [med])
    for r in rows:
        print(f"jogo {r['jogo']}: 6c {r['locsim_pen_6c']:.4f}; teto {r['locsim_pen_teto']:.4f}; cobertura {r['cob_6c']:.3f}; "
              f"sem âncora {r['sem_ancora']}; aceitas erradas {r['aceitas_erradas']}")
    print(f"mediana dos 6 jogos: 6c {med['locsim_pen_6c']:.4f}; teto {med['locsim_pen_teto']:.4f}")
