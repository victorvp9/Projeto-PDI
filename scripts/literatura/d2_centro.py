"""D2: o centro da câmera C é estável por clipe e por jogo?

Fonte "detector" (aproximado, sem dados): as H do detector v1 (td6_e1) em outputs/*.npz, GSR train
e valid, 1 frame a cada 25; H erradas entram, por isso a dispersão é a distância à mediana.
Fonte "gt" (completo, pede data/ e o cache do ajuste): a H_gt pelas linhas, 1 frame a cada `passo`.
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/d2_centro.py <saída> [detector|gt] [passo]"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from camera import angles, decompose  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def rows_detector():
    game = {}
    with open(ROOT / "outputs/runs_v2/b1_diagnostico/sinais_por_candidata.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            game[r["clipe"]] = int(r["jogo"])
    for f in ("outputs/pred_td6_e1_train_wc14-train_val.npz", "outputs/pred_td6_e1_valid.npz"):
        d = np.load(ROOT / f)
        for k in d.files:
            if k.startswith("gsr/") and np.isfinite(d[k]).all():
                _, part, clip, t = k.split("/")
                yield clip, game.get(clip), int(t), d[k]


def rows_gt(step):
    from src_v2.config import path
    from src_v2.io import gsr
    for sp in ("train", "valid"):
        for c in sorted((path("gsr") / sp).glob("SNGS-*")):
            g = int(gsr.game_id(c))
            for s in gsr.load_clip(c)[::step]:
                if s.H_gt is not None:
                    yield c.name, g, s.frame_idx, s.H_gt


def main():
    out = Path(sys.argv[1])
    src = sys.argv[2] if len(sys.argv) > 2 else "detector"
    step = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for clip, g, t, H in (rows_detector() if src == "detector" else rows_gt(step)):
        dec = decompose(H)
        if dec is None:
            rows.append(dict(clipe=clip, jogo=g, t=t, ok=False))
            continue
        fo, R, C = dec
        pan, tilt, roll = np.degrees(angles(R))
        rows.append(dict(clipe=clip, jogo=g, t=t, ok=True, f=fo, cx=C[0], cy=C[1], cz=C[2], pan=pan, tilt=tilt, roll=roll))
    tag = "" if src == "detector" else "_gt"
    with open(out / f"d2_cameras{tag}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["clipe", "jogo", "t", "ok", "f", "cx", "cy", "cz", "pan", "tilt", "roll"])
        w.writeheader()
        w.writerows(rows)

    ok = [r for r in rows if r["ok"]]
    P = lambda a, q: float(np.percentile(a, q))

    def spread(rs):
        C = np.array([[r["cx"], r["cy"], r["cz"]] for r in rs])
        m = np.median(C, 0)
        return np.linalg.norm(C - m, axis=1), m

    lines = [f"Fonte: {src}. H: {len(rows)}; decomponíveis: {len(ok)}; sem focal real: {len(rows) - len(ok)}.", "",
             "| jogo | H | C mediano (X, Y, Z) m | dist. à mediana do jogo: p50 / p75 / p90 m | > 5 m | > 10 m | dist. à mediana do clipe: p50 / p90 m | mediana dos clipes: dist. p50 / máx. m | roll p50 / p90 abs. (°) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for g in sorted({r["jogo"] for r in ok}):
        rg = [r for r in ok if r["jogo"] == g]
        dg, mg = spread(rg)
        dclip, meds = [], []
        for c in sorted({r["clipe"] for r in rg}):
            rc = [r for r in rg if r["clipe"] == c]
            if len(rc) >= 3:
                d, m = spread(rc)
                dclip += list(d)
                meds.append(m)
        dm = np.linalg.norm(np.array(meds) - mg, axis=1)
        roll = np.abs([r["roll"] for r in rg])
        lines.append(f"| {g} | {len(rg)} | ({mg[0]:.1f}, {mg[1]:.1f}, {mg[2]:.1f}) | {P(dg,50):.1f} / {P(dg,75):.1f} / {P(dg,90):.1f} | "
                     f"{np.mean(dg > 5):.2f} | {np.mean(dg > 10):.2f} | {P(dclip,50):.1f} / {P(dclip,90):.1f} | {P(dm,50):.1f} / {dm.max():.1f} | "
                     f"{P(roll,50):.2f} / {P(roll,90):.2f} |")
    fs = np.array([r["f"] for r in ok])
    lines += ["", f"Focal (px): p10 {P(fs,10):.0f}, p50 {P(fs,50):.0f}, p90 {P(fs,90):.0f}."]
    txt = "\n".join(lines)
    print(txt)
    (out / f"d2_resumo{tag}.md").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
