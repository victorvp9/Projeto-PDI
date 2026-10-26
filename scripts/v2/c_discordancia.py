"""v2, C: resumo por jogo da discordância entre a propagação vinda de a1 e a vinda de a2 (só
diagnóstico, não é regra; docs/decisoes.md, 2026-10-15), lida dos caches do 6c da rodada do C.
Discordância = mediana, nos pontos da grade usados na fusão, da distância entre as duas projeções,
em fração da altura da imagem. Relata também a correlação de Spearman com o NPE do frame (frames
com gabarito). Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/c_discordancia.py <saída>"""
import csv
import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from rodada_6c_dev import GAMES, clips_dev                 # noqa: E402
from src_v2.config import path                              # noqa: E402
from src_v2.io import gsr                                   # noqa: E402

def summarize(rows_by_game):
    """{jogo: [linhas por frame do cache do 6c]} -> uma linha por jogo (na ordem de GAMES) com a
    discordância dos frames do "6c fluxo" que vieram da fusão (os demais têm nan)."""
    rows = []
    for g in GAMES:
        fr = [x for x in rows_by_game.get(g, []) if x["variante"] == "6c fluxo" and np.isfinite(x.get("discordancia_c", np.nan))]
        v = np.array([x["discordancia_c"] for x in fr])
        p = np.array([(x["discordancia_c"], x["npe"]) for x in fr if x["has_gt"] and np.isfinite(x.get("npe", np.nan))]).reshape(-1, 2)
        rows.append(dict(jogo=g, frames_entre_ancoras=len(v), mediana=float(np.median(v)) if len(v) else np.nan,
                         p90=float(np.quantile(v, 0.9)) if len(v) else np.nan, maximo=float(v.max()) if len(v) else np.nan,
                         spearman_npe=float(spearmanr(p[:, 0], p[:, 1])[0]) if len(p) > 2 else np.nan, frames_com_gabarito=len(p)))
    return rows


if __name__ == "__main__":
    out = path("runs") / sys.argv[1]
    man = sorted((out / "manifestos").glob("_eval_clip_6c_cached_*.json"))[-1]
    key = json.loads(man.read_text(encoding="utf-8"))["chave_rodada"]       # só os caches da rodada do C
    by_game = defaultdict(list)
    for c in clips_dev():
        k, r = pickle.loads((path("cache") / "eval_6c" / c.parent.name / f"{c.name}.pkl").read_bytes())
        assert k == key, (c.name, k[:12], key[:12])
        by_game[gsr.game_id(c)] += r[0]
    rows = summarize(by_game)
    with (out / "discordancia_por_jogo.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print({k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})
