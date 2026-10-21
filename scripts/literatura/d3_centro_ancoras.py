"""D3: o centro da câmera implicado pela H separa candidatas a âncora certas e erradas?

Candidatas e rótulos: o diagnóstico do B1 (sinais_por_candidata.csv; `errada` = NPE > 0,05 contra a
H_gt; t = índice na série). Sinal: distância do C da H da candidata à mediana do C do jogo, tirada
das H do próprio detector do jogo (sem gabarito). H sem focal real conta como distância infinita.
Protocolo do B1 (etapa 1): limiar com <= 2% das certas do treino (jogos 4, 6, 9) recusadas,
conferido na valid (2, 3, 5); à parte, as aceitas (B1) erradas e certas que o limiar recusaria.
Fonte "npz" (aproximado, sem dados): só as candidatas cujo frame está no .npz do detector (1 em 25).
Fonte "serie" (completo): a série do detector em cache (outputs/cache_v2/detector), todas as candidatas.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/d3_centro_ancoras.py <saída> [npz|serie]"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from camera import decompose  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
NOTA = 1.6153357723089734                                         # limiar do B1 (config_v2.yaml)


def auc(bad, good):
    """P(sinal da errada > sinal da certa), empates valem 1/2."""
    b, g = np.asarray(bad)[:, None], np.asarray(good)[None, :]
    return float(((b > g) + 0.5 * (b == g)).mean()) if b.size and g.size else np.nan


def center(H):
    d = decompose(H)
    return None if d is None else d[2]


def main():
    out = Path(sys.argv[1])
    src = sys.argv[2] if len(sys.argv) > 2 else "npz"
    cands = list(csv.DictReader(open(ROOT / "outputs/runs_v2/b1_diagnostico/sinais_por_candidata.csv", encoding="utf-8")))
    if src == "npz":
        cams = list(csv.DictReader(open(out / "d2_cameras.csv", encoding="utf-8")))
        C_of = {(r["clipe"], int(r["t"]) - 1): np.array([float(r["cx"]), float(r["cy"]), float(r["cz"])]) for r in cams if r["ok"] == "True"}
        by_game = {}
        for r in cams:
            if r["ok"] == "True":
                by_game.setdefault(int(r["jogo"]), []).append(C_of[(r["clipe"], int(r["t"]) - 1)])
        cands = [r for r in cands if int(r["t"]) % 25 == 0]
    else:
        from src_v2.config import path
        from src_v2.io import gsr
        from src_v2.temporal import load_series
        C_of, by_game = {}, {}
        for sp in ("train", "valid"):
            for c in sorted((path("gsr") / sp).glob("SNGS-*")):
                g = int(gsr.game_id(c))
                ser = load_series(c)
                for t in np.nonzero(np.isfinite(ser["H"]).all(axis=(1, 2)))[0]:
                    C = center(ser["H"][t])
                    if C is not None:
                        C_of[(c.name, int(t))] = C
                        by_game.setdefault(g, []).append(C)
    med = {g: np.median(v, 0) for g, v in by_game.items()}
    rows = []
    for r in cands:
        g, key = int(r["jogo"]), (r["clipe"], int(r["t"]))
        # toda candidata tem H (é máximo local entre os frames com H): fora de C_of = sem focal real
        d =float(np.linalg.norm(C_of[key] - med[g])) if key in C_of else np.inf
        rows.append(dict(jogo=g, part=r["particao"], err=r["errada"] == "True", aceita=r["aceita"] == "True", d=d, nota=float(r["nota"])))
    with open(out / f"d3_candidatas_{src}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    L = [f"Fonte: {src}. Candidatas: {len(rows)} (erradas {sum(r['err'] for r in rows)}); aceitas pelo B1: "
         f"{sum(r['aceita'] and r['nota'] >= NOTA for r in rows)} (erradas {sum(r['err'] and r['aceita'] and r['nota'] >= NOTA for r in rows)}).", "",
         "| conjunto | candidatas | erradas | AUC dist. C | AUC nota (menor = pior) |", "|---|---|---|---|---|"]
    for name, part in (("treino (4, 6, 9)", "train"), ("valid (2, 3, 5)", "valid")):
        rs = [r for r in rows if r["part"] == part]
        bad, good = [r for r in rs if r["err"]], [r for r in rs if not r["err"]]
        L.append(f"| {name} | {len(rs)} | {len(bad)} | {auc([r['d'] for r in bad], [r['d'] for r in good]):.3f} | "
                 f"{auc([-r['nota'] for r in bad], [-r['nota'] for r in good]):.3f} |")
    thr = float(np.percentile([r["d"] for r in rows if r["part"] == "train" and not r["err"]], 98))
    L += ["", f"Limiar do treino (98º percentil da distância nas certas do treino): {thr:.1f} m.", "",
          "| jogo | candidatas | erradas recusadas por C | certas recusadas por C | aceitas pelo B1: erradas recusadas por C | aceitas pelo B1: certas recusadas por C |",
          "|---|---|---|---|---|---|"]
    for g in (4, 6, 9, 2, 3, 5):
        rs = [r for r in rows if r["jogo"] == g]
        bad, good = [r for r in rs if r["err"]], [r for r in rs if not r["err"]]
        acc = [r for r in rs if r["aceita"] and r["nota"] >= NOTA]
        ab, ag = [r for r in acc if r["err"]], [r for r in acc if not r["err"]]
        L.append(f"| {g} | {len(rs)} | {sum(r['d'] > thr for r in bad)} de {len(bad)} | {sum(r['d'] > thr for r in good)} de {len(good)} | "
                 f"{sum(r['d'] > thr for r in ab)} de {len(ab)} | {sum(r['d'] > thr for r in ag)} de {len(ag)} |")
    txt = "\n".join(L)
    print(txt)
    (out / f"d3_resumo_{src}.md").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
