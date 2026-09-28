"""CLI única do projeto: `python -m src.run`."""
import argparse
import csv
import os
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np

from src.config import CFG, path
from src.evaluate import frame_metrics, image_grid_displacement, summarize
from src.io import gsr, wc14
from src.render import draw_overlay

WORKERS = max(1, (os.cpu_count() or 2) - 1)


def _pool():
    """Um processo por clipe; o OpenCV fica com uma thread em cada, para não disputar CPU."""
    return ProcessPoolExecutor(WORKERS, initializer=cv2.setNumThreads, initargs=(1,))


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
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)
    print(out)


def _clips(splits):
    return [c for s in splits for c in sorted((path("gsr") / s).glob("SNGS-*"))]


def _pct(v, q):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return round(float(np.percentile(v, q)), 2) if len(v) else np.nan


def _quality_of_clip(clip):
    """Resumo da H_gt de um clipe (roda em processo separado; ajusta e grava o cache)."""
    G = CFG["gsr"]
    samples = gsr.load_clip(clip)
    resid = [s.line_err for s in samples]
    dis = [s.gt_disagree_px for s in samples]
    row = dict(split=clip.parent.name, clip=clip.name, frames=len(samples),
               sem_H_pessoas=sum(s.H_persons is None for s in samples),
               sem_H=sum(s.H_gt is None for s in samples),
               duvidosos=sum(s.dubious for s in samples),
               residuo_mediana_px=_pct(resid, 50), residuo_p90_px=_pct(resid, 90),
               discordancia_mediana_px=_pct(dis, 50), discordancia_p90_px=_pct(dis, 90))
    per_class = defaultdict(list)
    for s in samples:
        for name, e in (s.class_err or {}).items():
            per_class[name].append(e)
    class_rows = []
    for name, e in sorted(per_class.items()):
        frac = float(np.mean(np.array(e) > G["label_suspect_px"]))
        class_rows.append(dict(split=row["split"], clip=clip.name, classe=name, frames=len(e),
                               mediana_px=round(float(np.median(e)), 2), frac_acima=round(frac, 3),
                               suspeita=frac > G["label_suspect_frac"]))
    return row, class_rows


def gsr_quality(splits):
    """Qualidade da H_gt do GSR -> outputs/gsr_gt_quality.csv (por clipe) e
    outputs/gsr_gt_classes.csv (por clipe x classe, com rótulo suspeito)."""
    rows, class_rows = [], []
    with _pool() as ex:
        for row, crows in ex.map(_quality_of_clip, _clips(splits)):
            rows.append(row)
            class_rows += crows
            print(row)
            for r in crows:
                if r["suspeita"]:
                    print("  rótulo suspeito:", r)
    _write_csv(path("outputs") / "gsr_gt_quality.csv", rows)
    _write_csv(path("outputs") / "gsr_gt_classes.csv", class_rows)


def _fit_stats_of_clip(clip):
    """Por frame: estatísticas do ajuste e dois indicadores de ajuste errado —
    discordância com a H pelas pessoas e salto em relação aos frames vizinhos."""
    samples = gsr.load_clip(clip)
    out = []
    for i, s in enumerate(samples):
        f = s.fit
        jump = np.nan
        if f.H is not None:
            nb = [samples[j].fit.H for j in (i - 1, i + 1) if 0 <= j < len(samples) and samples[j].fit.H is not None]
            if nb:
                jump = min(image_grid_displacement(f.H, H, s.size) for H in nb)
        dis = image_grid_displacement(f.H, s.H_persons, s.size) if f.H is not None and s.H_persons is not None else np.nan
        out.append((f.rank, f.cond, f.resid_px, f.n_points, dis, jump))
    return out


def fit_calibration(splits):
    """Distribuições para calibrar max_cond e max_resid_px -> outputs/figures/."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with _pool() as ex:
        a = np.array([r for rows in ex.map(_fit_stats_of_clip, _clips(splits)) for r in rows], float)
    rank, cond, resid, n, dis, jump = a.T
    tried = np.isfinite(resid)
    r8 = tried & (rank == 8)
    print(f"frames {len(a)}; ajuste tentado {tried.sum()}; posto 8 {r8.sum()}; posto < 8 {(tried & (rank < 8)).sum()}")
    for name, v in (("cond", cond[r8]), ("resíduo px", resid[r8]), ("discordância px", dis[r8]), ("salto px", jump[r8])):
        print(f"{name:16}", {q: _pct(v, q) for q in (50, 90, 99, 99.9, 100)})

    def by_bins(x, edges, label):
        print(f"\n{label}: mediana e p90 da discordância e do salto, e fração com discordância > 10 px")
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = r8 & (x >= lo) & (x < hi)
            if m.sum():
                print(f"  [{lo:>8.3g}, {hi:<8.3g}) n={m.sum():6d}  disc {_pct(dis[m], 50):7} / {_pct(dis[m], 90):7}"
                      f"  salto {_pct(jump[m], 50):7} / {_pct(jump[m], 90):7}"
                      f"  disc>10: {np.mean(dis[m][np.isfinite(dis[m])] > 10):.3f}")
    by_bins(cond, [1, 30, 100, 300, 1e3, 3e3, 1e4, 1e5, np.inf], "condição")
    by_bins(resid, [0, 1, 2, 3, 5, 10, 20, 50, np.inf], "resíduo (px)")

    out = path("outputs") / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    for row, (x, xl) in enumerate(((cond, "condição do jacobiano"), (resid, "resíduo mediano (px)"))):
        for col, (y, yl) in enumerate(((dis, "discordância com a H pelas pessoas (px)"), (jump, "salto até o vizinho (px)"))):
            m = r8 & np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
            ax[row, col].scatter(x[m], y[m], s=1, alpha=0.15)
            ax[row, col].set(xscale="log", yscale="log", xlabel=xl, ylabel=yl)
            ax[row, col].grid(True, which="both", alpha=0.3)
    fig.suptitle(f"GSR {'+'.join(splits)}: ajuste pelas linhas, {r8.sum()} frames com posto 8")
    fig.tight_layout()
    fig.savefig(out / "fit_calibration_scatter.png", dpi=110)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].hist(np.log10(cond[r8 & np.isfinite(cond)]), bins=100)
    ax[0].set(xlabel="log10(condição)", ylabel="frames")
    ax[1].hist(np.log10(np.clip(resid[r8], 1e-2, None)), bins=100)
    ax[1].set(xlabel="log10(resíduo mediano, px)", ylabel="frames")
    fig.tight_layout()
    fig.savefig(out / "fit_calibration_hist.png", dpi=110)
    print(out / "fit_calibration_scatter.png", out / "fit_calibration_hist.png", sep="\n")


def _sheet(tiles, labels, path_out, cols=6, tw=320):
    """Folha de contato: miniaturas com rótulo, em grade."""
    th = tw * 9 // 16
    rows = []
    for i in range(0, len(tiles), cols):
        row = []
        for img, lab in zip(tiles[i:i + cols], labels[i:i + cols]):
            t = cv2.resize(img, (tw, th), interpolation=cv2.INTER_AREA)
            cv2.rectangle(t, (0, 0), (tw, 20), (0, 0, 0), -1)
            cv2.putText(t, lab, (4, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
            row.append(t)
        row += [np.zeros((th, tw, 3), np.uint8)] * (cols - len(row))
        rows.append(np.hstack(row))
    cv2.imwrite(str(path_out), np.vstack(rows))
    print(path_out)


def _tint_dark(frame, dark):
    """Depuração da sombra: classe escura do Otsu em azul translúcido."""
    out = frame.copy()
    if dark is not None:
        out[dark] = (0.5 * out[dark] + [120, 40, 0]).astype(np.uint8)
    return out


def _shadow_of_clip(clip):
    """GSR: pontuação de sombra em 1 frame a cada `gsr_frame_step`, com o campo
    projetado pela H_gt como região; devolve linhas por frame e o frame mediano."""
    from src.evaluate import shadow_score
    from src.render import pitch_mask
    rows = []
    for s in gsr.load_clip(clip)[::CFG["eval_segment"]["gsr_frame_step"]]:
        if s.H_gt is None:
            continue
        dl, f, w = shadow_score(s.image, pitch_mask(s.H_gt, s.size))
        rows.append(dict(split=clip.parent.name, clip=clip.name, frame=s.frame_idx, dL=round(dl, 2),
                         f_escuro=round(f, 3), f_claro=round(w, 3)))
    return rows


def shadow_sheet():
    """Folhas de contato para fixar dL_min: WC14 train_val (região = grass) e GSR
    train (região = campo projetado), ordenadas por dL; CSVs com as pontuações."""
    from src.evaluate import shadow_score
    from src.render import pitch_mask
    out = path("debug") / "sombra"
    out.mkdir(parents=True, exist_ok=True)
    rows, tiles = [], []
    for s in wc14.load_split("train_val"):
        img = s.image
        dl, f, w, dark = shadow_score(img, s.grass, dark_mask=True)
        rows.append(dict(image_id=s.image_id, dL=round(dl, 2), f_escuro=round(f, 3), f_claro=round(w, 3)))
        tiles.append((dl, f, w, s.image_id, _tint_dark(img, dark)))
    _write_csv(path("outputs") / "shadow_wc14.csv", rows)
    tiles.sort(key=lambda t: -t[0])
    per = 48
    for k in range(0, len(tiles), per):
        chunk = tiles[k:k + per]
        _sheet([t[4] for t in chunk], [f"{t[3]} dL {t[0]:.0f} fe {t[1]:.2f} fc {t[2]:.3f}" for t in chunk],
               out / f"wc14_{k // per + 1}.jpg")
    with _pool() as ex:
        frames = [r for rs in ex.map(_shadow_of_clip, _clips(["train"])) for r in rs]
    _write_csv(path("outputs") / "shadow_gsr.csv", frames)
    clips = defaultdict(list)
    for r in frames:
        clips[r["clip"]].append(r)
    tiles = []
    for clip, rs in clips.items():
        med = {k: np.median([r[k] for r in rs]) for k in ("dL", "f_escuro", "f_claro")}
        rep = min(rs, key=lambda r: abs(r["dL"] - med["dL"]))
        s = next(x for x in gsr.load_clip(path("gsr") / "train" / clip) if x.frame_idx == rep["frame"])
        *_, dark = shadow_score(s.image, pitch_mask(s.H_gt, s.size), dark_mask=True)
        tiles.append((med["dL"], med["f_escuro"], med["f_claro"], f"{clip} f{s.frame_idx}", _tint_dark(s.image, dark)))
    tiles.sort(key=lambda t: -t[0])
    _sheet([t[4] for t in tiles], [f"{t[3]} dL {t[0]:.0f} fe {t[1]:.2f} fc {t[2]:.3f}" for t in tiles], out / "gsr_train.jpg")


def _eval_clip(args):
    """Linhas de métrica de um clipe do GSR para a predição `name`: arquivo .npz,
    "persons" (H pelas pessoas) ou "gt" (a própria H_gt, conferência do LocSim)."""
    clip, name = args
    preds = None if name in ("persons", "gt") else np.load(name)
    rows = []
    for s in gsr.load_clip(clip):
        if name == "persons":
            H = s.H_persons
        elif name == "gt":
            H = s.H_gt
        else:
            key = f"gsr/{clip.parent.name}/{clip.name}/{s.frame_idx}"
            H = preds[key] if key in preds else None
        rows.append(frame_metrics(H, s))
    return rows


def evaluate(name, splits):
    """Tabela de métricas da predição `name` no GSR, com e sem os duvidosos."""
    with _pool() as ex:
        rows = [r for rs in ex.map(_eval_clip, [(c, name) for c in _clips(splits)]) for r in rs]
    table = summarize(rows)
    for label, t in table.items():
        print(f"\n[{label}]")
        for k, v in t.items():
            print(f"  {k:16} " + (f"média {v[0]:.4f}  mediana {v[1]:.4f}" if isinstance(v, tuple) else f"{v:.4f}"))
    tag = os.path.splitext(os.path.basename(name))[0]
    _write_csv(path("outputs") / f"metrics_{tag}_{'+'.join(splits)}.csv",
               [dict(conjunto=label, metrica=k, **({"media": v[0], "mediana": v[1]} if isinstance(v, tuple) else {"media": v, "mediana": ""}))
                for label, t in table.items() for k, v in t.items()])


def main():
    sys.stdout.reconfigure(encoding="utf-8")    # saída redirecionada no Windows cai em cp1252 e quebra no "α"
    ap = argparse.ArgumentParser(prog="python -m src.run")
    ap.add_argument("--overlay", nargs="+", metavar="SPEC",
                    help="wc14:<split>/<N> ou gsr:<split>/<clipe>/<frame>[-<frame>]")
    ap.add_argument("--gsr-quality", action="store_true", help="gera outputs/gsr_gt_quality.csv e gsr_gt_classes.csv")
    ap.add_argument("--fit-calibration", action="store_true", help="figuras para calibrar max_cond e max_resid_px")
    ap.add_argument("--evaluate", metavar="PREDS", help="arquivo .npz de homografias preditas, 'persons' ou 'gt'")
    ap.add_argument("--shadow-sheet", action="store_true", help="folhas de contato da sombra (fixar dL_min)")
    ap.add_argument("--segment-sweep", action="store_true", help="calibração da Fatia 3 no treino (tabelas e curvas)")
    ap.add_argument("--segment-sweep-lines", action="store_true", help="só a varredura das marcações, com o gramado do config")
    ap.add_argument("--segment-eval", action="store_true", help="métricas da segmentação do config (WC14 train_val; GSR --splits)")
    ap.add_argument("--segment-variants-calib", nargs="*", metavar="PARTE",
                    help="calibra no treino as variantes da Fatia 3: kmeans, hysteresis, alpha (padrão: todas)")
    ap.add_argument("--segment-variants", action="store_true", help="rodada das variantes da Fatia 3 (WC14 train_val; GSR --splits)")
    ap.add_argument("--lines-fp-sheet", action="store_true", help="Fatia 4: amostra dos falsos positivos da máscara de marcações (treino) e folhas de contato")
    ap.add_argument("--lines-fp-table", action="store_true", help="Fatia 4: tabela das categorias de falsos positivos (outputs/lines_fp_classes.csv)")
    ap.add_argument("--splits", nargs="+", default=["train", "valid", "test"], help="partições do GSR")
    args = ap.parse_args()
    if not (args.overlay or args.gsr_quality or args.fit_calibration or args.evaluate or args.shadow_sheet
            or args.segment_sweep or args.segment_sweep_lines or args.segment_eval
            or args.segment_variants_calib is not None or args.segment_variants
            or args.lines_fp_sheet or args.lines_fp_table):
        ap.print_help()
    for spec in args.overlay or []:
        overlay(spec)
    if args.gsr_quality:
        gsr_quality(args.splits)
    if args.fit_calibration:
        fit_calibration(args.splits)
    if args.evaluate:
        evaluate(args.evaluate, args.splits)
    if args.shadow_sheet:
        shadow_sheet()
    if args.segment_sweep:
        from src import sweep_segment
        sweep_segment.report(sweep_segment.run(_pool))
    if args.segment_sweep_lines:
        from src import sweep_segment
        with _pool() as ex:
            sweep_segment.report(sweep_segment.run_lines(ex, sweep_segment.grass_config(), []))
    if args.segment_eval:
        from src import sweep_segment
        sweep_segment.evaluate_final(_pool, args.splits)
    if args.segment_variants_calib is not None:
        from src import sweep_segment
        sweep_segment.calibrate_variants(_pool, args.segment_variants_calib or ["kmeans", "hysteresis", "alpha"])
    if args.segment_variants:
        from src import sweep_segment
        sweep_segment.evaluate_variants(_pool, args.splits)
    if args.lines_fp_sheet:
        from src import sweep_lines
        sweep_lines.sample_fp(_pool)
    if args.lines_fp_table:
        from src import sweep_lines
        sweep_lines.fp_table()


if __name__ == "__main__":
    main()
