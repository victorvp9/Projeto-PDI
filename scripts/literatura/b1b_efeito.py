"""B1b (docs/decisoes.md, 2026-10-16): quando a regra do B1 deixa um clipe sem nenhuma âncora, recuperar a
candidata de maior nota entre as que passaram na verificação por maioria e foram recusadas pela nota.

Só os clipes sem âncora na base do B1 mudam (nos outros, `anchors` devolve o mesmo); eles são recalculados
com a regra aplicada por fora do src_v2 (camada em volta de temporal.anchors, nos trabalhadores) e os demais
vêm da base (outputs/cache_v2/eval_6c_b1), idênticos por construção. Critério congelado por jogo contra a
base do B1 recalculada (outputs/runs_v2/base_b1_local/por_jogo.csv). Saída em outputs/runs_v2/b1b/.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/b1b_efeito.py"""
import csv
import json
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v2"))


def _patch():
    """Camada do B1b em volta de temporal.anchors (no processo que a chama)."""
    import src_v2.temporal as T
    orig = T.anchors

    def anchors(ser, cf, seg, verify=True, c_ref=None):
        out, cand, verifiable = orig(ser, cf, seg, verify, c_ref)
        if out or not verify:
            return out, cand, verifiable
        nota, T.T["anchor_min_nota"] = T.T["anchor_min_nota"], None    # só a verificação por maioria
        try:
            maj = orig(ser, cf, seg, verify, c_ref)[0]
        finally:
            T.T["anchor_min_nota"] = nota
        if maj:
            a = np.nan_to_num(ser["iou"]) + np.nan_to_num(ser["img"])
            out = [max(maj, key=lambda t: a[t])]
        return out, cand, verifiable
    T.anchors = anchors


def run(clip):
    cv2.setNumThreads(1)
    _patch()
    import src_v2.temporal as T
    return clip, T._eval_clip_6c(clip)


if __name__ == "__main__":
    from baseline_dev import per_game
    from rodada_6c_dev import clips_dev, decide
    from src_v2.config import CFG, path
    assert CFG["temporal"]["anchor_c_max_m"] is None and not CFG["temporal"]["bidirectional"] and not CFG["assign"].get("central_view"), \
        "a base do B1b é o B1: B2, C e A desligados"
    base = {c: pickle.loads((path("cache") / "eval_6c_b1" / c.parent.name / f"{c.name}.pkl").read_bytes())[1] for c in clips_dev()}
    # clipes sem âncora na base com alguma candidata que passou na maioria e só caiu pela nota
    # (diagnóstico do B1: `aceita` = passou na verificação por maioria); nos outros, o B1b não muda nada
    nota = CFG["temporal"]["anchor_min_nota"]
    resc = {r["clipe"] for r in csv.DictReader(open(ROOT / "outputs/runs_v2/b1_diagnostico/sinais_por_candidata.csv", encoding="utf-8"))
            if r["aceita"] == "True" and float(r["nota"]) < nota}
    todo = [c for c, r in base.items() if not any(a["aceita"] for a in r[2]) and c.name in resc]
    print("clipes sem âncora na base (recalculados):", [c.name for c in todo], flush=True)
    res = dict(base)
    with ProcessPoolExecutor(len(todo)) as ex:
        for c, r in ex.map(run, todo):
            res[c] = r
            print(f"{c.name}: aceitas {sum(a['aceita'] for a in r[2])} (antes 0)", flush=True)
    rows, med = per_game(res)
    ref = {r["jogo"]: r for r in csv.DictReader(open(ROOT / "outputs/runs_v2/base_b1_local/por_jogo.csv", encoding="utf-8")) if r["particao"] != "mediana"}
    for r in rows:
        r["base_locsim_pen_6c"] = float(ref[r["jogo"]]["locsim_pen_6c"])
        r["delta_6c"] = r["locsim_pen_6c"] - r["base_locsim_pen_6c"]
    out = path("runs") / "b1b"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "por_jogo.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)
    dec = decide({r["jogo"]: r["delta_6c"] for r in rows})
    (out / "decisao.json").write_text(json.dumps(dict(recalculados=[c.name for c in todo], decisao=dec), ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(f"jogo {r['jogo']}: 6c {r['base_locsim_pen_6c']:.4f} -> {r['locsim_pen_6c']:.4f} (Δ {r['delta_6c']:+.4f}); "
              f"sem âncora {r['sem_ancora']}; aceitas erradas {r['aceitas_erradas']}")
    print(json.dumps(dec, ensure_ascii=False))
