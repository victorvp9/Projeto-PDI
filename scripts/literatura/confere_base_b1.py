"""Confere que o 6c do B1 recalculado neste PC (caches em outputs/cache_v2/eval_6c, rodados com
temporal.bidirectional: false) reproduz, por jogo, a tabela do B1 aceito (outputs/runs_v2/b1_regra/
por_jogo.csv, rodada original), e grava a tabela local da base (outputs/runs_v2/base_b1_local/por_jogo.csv),
contra a qual o C é medido: os dois lados calculados na mesma máquina.

Bloqueia (sai com erro) se divergir algum número que decide ou descreve as âncoras: LocSim@5 penalizado
do 6c, cobertura, clipes sem âncora e aceitas erradas. O teto (6c a partir da H_gt nas âncoras) só gera
aviso: em 21/10 ele diferiu em até 0,0009 nos jogos do treino (4, 6, 9) e foi idêntico na valid, com a H_gt
reproduzida em todos os clipes (outputs/gsr_gt_quality.csv) e a série e o 6c idênticos; causa não isolada.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/confere_base_b1.py"""
import csv
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v2"))
from baseline_dev import per_game                      # noqa: E402
from src_v2.config import path                          # noqa: E402

BLOCK = ("locsim_pen_6c", "cob_6c", "sem_ancora", "aceitas_erradas")
WARN = ("locsim_pen_teto",)

clips = [c for s in ("train", "valid") for c in sorted((path("gsr") / s).glob("SNGS-*"))]
res = {c: pickle.loads((path("cache") / "eval_6c" / c.parent.name / f"{c.name}.pkl").read_bytes())[1] for c in clips}
rows, med = per_game(res)
out = path("runs") / "base_b1_local"
out.mkdir(parents=True, exist_ok=True)
with (out / "por_jogo.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows + [med] for k in r)))
    w.writeheader()
    w.writerows(rows + [med])
ref = {r["jogo"]: r for r in csv.DictReader(open(ROOT / "outputs/runs_v2/b1_regra/por_jogo.csv", encoding="utf-8")) if r["particao"] != "mediana"}
bad = warn = 0
for r in rows:
    for k in BLOCK + WARN:
        a, b = float(r[k]), float(ref[r["jogo"]][k])
        same = abs(a - b) <= 1e-12 * max(1.0, abs(b))
        if not same:
            bad += k in BLOCK
            warn += k in WARN
        print(f"jogo {r['jogo']} {k}: aqui {a:.12g} | B1 original {b:.12g} {'ok' if same else ('DIFERENTE' if k in BLOCK else 'aviso: diferente')}")
print(f"tabela local da base em {out / 'por_jogo.csv'}")
print("base do B1 reproduzida" if not bad else f"{bad} números que decidem diferentes", f"({warn} avisos no teto)" if warn else "")
sys.exit(1 if bad else 0)
