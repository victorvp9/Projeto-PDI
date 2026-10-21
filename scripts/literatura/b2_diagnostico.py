"""B2, etapa 1: referência do centro da câmera (jogo × clipe) e limiar, só pelos jogos do treino.

Regra fixada antes de rodar (docs/decisoes.md, 2026-10-21):
  - sinal: distância do C da H da candidata (série do detector) à mediana de C de referência, das H do
    detector (sem gabarito); H sem focal real = distância infinita;
  - referência "jogo": todas as H decomponíveis dos clipes do jogo; "clipe": as do próprio clipe, com
    volta à do jogo se o clipe tiver menos de MIN_FRAMES H decomponíveis;
  - limiar de cada variante: quantil 0,98 (method="higher") da distância nas candidatas CERTAS dos jogos
    do treino (4, 6, 9), a regra do B1 (<= 2% das certas recusadas);
  - escolha: a variante que recusa mais candidatas ERRADAS do treino no seu limiar; empate, maior AUC no
    treino. A valid (2, 3, 5) só é impressa, como informação, e não entra na escolha.
Também mostra, para a variante escolhida, os limiares leave-one-game-out (a mesma regra nos outros 5
jogos) e se cada um recusa, entre as âncoras que passam no B1, as mesmas que o limiar do treino.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/b2_diagnostico.py"""
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from camera import decompose                            # noqa: E402
from src_v2.config import CFG, path                     # noqa: E402
from src_v2.io import gsr                               # noqa: E402
from src_v2.temporal import load_series                 # noqa: E402

MIN_FRAMES = 50                                         # escolha: ~2 s de vídeo com H
NOTA = CFG["temporal"]["anchor_min_nota"]
TRAIN, GAMES = ("4", "6", "9"), ("4", "6", "9", "2", "3", "5")


def auc(bad, good):
    b, g = np.asarray(bad)[:, None], np.asarray(good)[None, :]
    return float(((b > g) + 0.5 * (b == g)).mean())


def thr_of(rows, key, games):
    return float(np.quantile([r[key] for r in rows if r["jogo"] in games and not r["err"]], 0.98, method="higher"))


C, by_game, by_clip = {}, {}, {}
for sp in ("train", "valid"):
    for c in sorted((path("gsr") / sp).glob("SNGS-*")):
        g, ser = gsr.game_id(c), load_series(c)
        for t in np.nonzero(np.isfinite(ser["H"]).all(axis=(1, 2)))[0]:
            d = decompose(ser["H"][t])
            if d is not None:
                C[(c.name, int(t))] = d[2]
                by_game.setdefault(g, []).append(d[2])
                by_clip.setdefault(c.name, []).append(d[2])
med_game = {g: np.median(v, 0) for g, v in by_game.items()}
rows = []
for r in csv.DictReader(open(ROOT / "outputs/runs_v2/b1_diagnostico/sinais_por_candidata.csv", encoding="utf-8")):
    k, g = (r["clipe"], int(r["t"])), r["jogo"]
    clip_c = by_clip.get(r["clipe"], [])
    ref_clip = np.median(clip_c, 0) if len(clip_c) >= MIN_FRAMES else med_game[g]
    dist = lambda ref: float(np.linalg.norm(C[k] - ref)) if k in C else np.inf
    rows.append(dict(jogo=g, clipe=r["clipe"], t=int(r["t"]), err=r["errada"] == "True",
                     b1=r["aceita"] == "True" and float(r["nota"]) >= NOTA, d_jogo=dist(med_game[g]), d_clipe=dist(ref_clip)))

print(f"clipes com referência própria (>= {MIN_FRAMES} H): {sum(len(v) >= MIN_FRAMES for v in by_clip.values())} de {len(by_clip)}")
score = {}
for key in ("d_jogo", "d_clipe"):
    thr = thr_of(rows, key, TRAIN)
    tr = [r for r in rows if r["jogo"] in TRAIN]
    bad, good = [r for r in tr if r["err"]], [r for r in tr if not r["err"]]
    rej = sum(r[key] > thr for r in bad)
    score[key] = (rej, auc([r[key] for r in bad], [r[key] for r in good]))
    va = [r for r in rows if r["jogo"] not in TRAIN]
    vb, vg = [r for r in va if r["err"]], [r for r in va if not r["err"]]
    print(f"{key}: limiar {thr:.2f} m | TREINO: erradas recusadas {rej} de {len(bad)}, certas {sum(r[key] > thr for r in good)} de {len(good)}, "
          f"AUC {score[key][1]:.3f} | valid (informação): erradas {sum(r[key] > thr for r in vb)} de {len(vb)}, "
          f"certas {sum(r[key] > thr for r in vg)} de {len(vg)}, AUC {auc([r[key] for r in vb], [r[key] for r in vg]):.3f}")
best = max(score, key=lambda k: score[k])
print(f"escolhida pela regra do treino: {best}")

thr = thr_of(rows, best, TRAIN)
print(f"\nlimiar do treino ({best}): {thr!r}")
print("| jogo | limiar LOGO | aceitas pelo B1 recusadas: treino / LOGO | mesmas? | erradas recusadas (B1) | certas recusadas (B1) |")
print("|---|---|---|---|---|---|")
for g in GAMES:
    tl = thr_of(rows, best, [x for x in GAMES if x != g])
    acc = [r for r in rows if r["jogo"] == g and r["b1"]]
    a, b = {(r["clipe"], r["t"]) for r in acc if r[best] > thr}, {(r["clipe"], r["t"]) for r in acc if r[best] > tl}
    print(f"| {g} | {tl!r} | {len(a)} / {len(b)} | {'sim' if a == b else 'NÃO'} | "
          f"{sum(r['err'] and r[best] > thr for r in acc)} de {sum(r['err'] for r in acc)} | "
          f"{sum(not r['err'] and r[best] > thr for r in acc)} de {sum(not r['err'] for r in acc)} |")
