"""CLI única do projeto: `python -m src.run`."""
import argparse
import csv
from collections import defaultdict

import cv2
import numpy as np

from src.config import CFG, path
from src.io import gsr, wc14
from src.render import draw_overlay


def overlay(spec: str):
    """`wc14:<split>/<N>` ou `gsr:<split>/<clipe>/<frame>[-<frame>]` -> outputs/debug/."""
    source, rest = spec.split(":", 1)
    if source == "wc14":
        split, image_id = rest.split("/")
        samples = [wc14.load_sample(split, image_id)]
    elif source == "gsr":
        split, clip, frames = rest.split("/")
        first, _, last = frames.partition("-")
        wanted = range(int(first), int(last or first) + 1)
        samples = [s for s in gsr.load_clip(path("gsr") / split / clip) if s.frame_idx in wanted]
    else:
        raise ValueError(f"fonte desconhecida: {source}")
    out_dir = path("debug")
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in samples:
        if s.H_gt is None:
            print(f"{spec}: frame {s.frame_idx} sem H_gt")
            continue
        name = "_".join(str(x) for x in ("overlay", source, split, s.sequence_id, s.frame_idx or s.image_id) if x)
        out = out_dir / f"{name}.jpg"
        assert cv2.imwrite(str(out), draw_overlay(s.image, s.H_gt, s.lines_uv)), out
        print(out, f"erro contra as linhas: {s.line_err:.1f} px" if s.lines_uv else "")


def _write_csv(out, rows):
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(out)


def gsr_quality():
    """Qualidade da H_gt do GSR nas três partições -> outputs/gsr_gt_quality.csv
    (por clipe) e outputs/gsr_gt_classes.csv (por clipe x classe, com rótulo suspeito)."""
    G = CFG["gsr"]
    rows, class_rows = [], []
    for split in ("train", "valid", "test"):
        for clip in sorted((path("gsr") / split).glob("SNGS-*")):
            samples = gsr.load_clip(clip)
            err = np.array([s.line_err for s in samples])
            rows.append(dict(split=split, clip=clip.name, frames=len(samples),
                             sem_H=sum(s.H_gt is None for s in samples),
                             duvidosos=sum(s.dubious for s in samples),
                             mediana_px=round(float(np.nanmedian(err)), 2),
                             p90_px=round(float(np.nanpercentile(err, 90)), 2)))
            print(rows[-1])
            per_class = defaultdict(list)
            for s in samples:
                for name, e in s.class_err.items():
                    per_class[name].append(e)
            for name, e in sorted(per_class.items()):
                frac = float(np.mean(np.array(e) > G["label_suspect_px"]))
                class_rows.append(dict(split=split, clip=clip.name, classe=name, frames=len(e),
                                       mediana_px=round(float(np.median(e)), 2),
                                       frac_acima=round(frac, 3),
                                       suspeita=frac > G["label_suspect_frac"]))
                if class_rows[-1]["suspeita"]:
                    print("  rótulo suspeito:", class_rows[-1])
    _write_csv(path("outputs") / "gsr_gt_quality.csv", rows)
    _write_csv(path("outputs") / "gsr_gt_classes.csv", class_rows)


def main():
    ap = argparse.ArgumentParser(prog="python -m src.run")
    ap.add_argument("--overlay", nargs="+", metavar="SPEC",
                    help="wc14:<split>/<N> ou gsr:<split>/<clipe>/<frame>[-<frame>]")
    ap.add_argument("--gsr-quality", action="store_true", help="gera outputs/gsr_gt_quality.csv")
    args = ap.parse_args()
    if not (args.overlay or args.gsr_quality):
        ap.print_help()
    for spec in args.overlay or []:
        overlay(spec)
    if args.gsr_quality:
        gsr_quality()


if __name__ == "__main__":
    main()
