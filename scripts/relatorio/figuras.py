"""Figuras do relatório (docs/04-relatorio.md) que não existiam: esquema do pipeline, etapas
do detector num frame, LocSim@5 por frame num clipe do HSB, deriva da propagação com a
distância à âncora e a lacuna da Figura 7 com os nomes descritivos das séries. Só lê os caches e os CSVs da rodada do test e funções do src/ sem mudança; nenhum
número das tabelas é recalculado de outro jeito. A única conta nova é a das máscaras, retas e
elipses do frame de ilustração (do train), com os parâmetros do detector congelado.

As outras figuras de falha do relatório são as da análise de falhas (outputs/figures/falhas_test/).
Saída: outputs/figures/relatorio/. Uso (da raiz, PYTHONPATH=.): figuras.py"""
import csv
import pickle
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

OUT = Path("outputs/figures/relatorio")
RUN = Path("outputs/runs/rodada_test")
STAGES = ("train", "SNGS-099", 525)   # frame de ilustração: do train, com H do detector e uma elipse detectada
HSB_CLIP = "SNGS-136"                 # o intervalo mais longo do HSB (60-280, 221 frames): regra fixa, sem olhar a curva
COMMA = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))   # vírgula decimal (texto em português)


def pipeline():
    """Esquema: detector frame a frame (em cima) e consistência temporal (embaixo)."""
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 104)
    ax.set_ylim(0, 46)
    ax.axis("off")
    box = lambda x, y, w, t, c: (ax.add_patch(FancyBboxPatch((x, y), w, 9, boxstyle="round,pad=0.4", fc=c, ec="0.3")),
                                 ax.text(x + w / 2, y + 4.5, t, ha="center", va="center", fontsize=8.5))
    arrow = lambda x0, y0, x1, y1: ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="->", color="0.25"))
    top = [("frame\n(BGR)", 8), ("1. gramado\n(matiz em Lab)", 12), ("2. marcações\n(filtro de linha)", 12),
           ("3-4. retas\ne elipses", 11), ("5. hipóteses:\n2 + 2 retas", 12),
           ("6. verificação:\nnota e portões", 13), ("7. refino\nponto-linha", 12)]
    x = 1
    for k, (t, w) in enumerate(top):
        box(x, 33, w, t, "#e8f0e0" if k else "#eeeeee")
        if k:
            arrow(x - 2.2, 37.5, x - 0.4, 37.5)
        x += w + 2.6
    ax.text(1, 44.5, "Detector frame a frame", fontsize=10, weight="bold")
    ax.text(1, 27, "Consistência temporal, por clipe", fontsize=10, weight="bold")
    bot = [("série do detector\n(H ou nada)", 15), ("detecção de corte\n(histograma)", 14),
           ("âncoras: máximos\nda nota + verificação", 18), ("propagação: Lucas-\nKanade + linhas guiadas", 20),
           ("H nos frames dos\nplanos com âncora", 16)]
    x = 1
    for k, (t, w) in enumerate(bot):
        box(x, 13, w, t, "#e0e8f4")
        if k:
            arrow(x - 2.2, 17.5, x - 0.4, 17.5)
        x += w + 2.6
    arrow(96, 33, 9, 22.6)
    ax.text(1, 7, "Comparadas a partir da mesma série: suavização S-G (Bassek: Savitzky-Golay 31/3, lacunas ≤ 25 frames por\n"
            "interpolação linear), S-G robusta (Hampel antes) e Kalman de velocidade constante + RTS. Ablações da propagação:\n"
            "sem fluxo, sem linhas, âncora ingênua a cada 150 frames e âncora de gabarito (teto condicionado às âncoras).",
            fontsize=8.5, va="top")
    fig.savefig(OUT / "fig1_pipeline.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def stages():
    """Etapas do detector num frame: gramado, marcações, retas e elipses, modelo pela H da série."""
    from src import temporal as T
    from src.conics import detect, ellipse_points
    from src.config import CFG, path
    from src.io import gsr
    from src.lines import draw_segments
    from src.render import draw_overlay
    from src.segment import debug_overlay, grass_mask, line_mask, params
    cv2.setNumThreads(1)
    split, clip, i = STAGES
    clip_dir = path("gsr") / split / clip
    ser = np.load(T._series_path(clip_dir))
    assert str(ser["key"]) == T._series_key(), "série do detector de outro código"
    H = ser["H"][i].astype(float)
    assert np.isfinite(H).all(), "o frame de ilustração não tem H do detector"
    img = gsr.load_clip(clip_dir, fit="none")[i].image   # sem ajuste da H_gt: nada de cache é lido ou gravado
    v = CFG["detector"]["variants"]["td6_e1"]
    P = params("gsr")
    grass = grass_mask(img, P)
    marks = line_mask(img, grass, {**P, **v.get("segment", {})})
    segs, ells, cid = detect(marks, {**CFG["lines"], **v.get("lines", {})})
    lines_img = draw_segments(img, segs[cid < 0])
    for E in ells:
        cv2.polylines(lines_img, [np.round(ellipse_points(E, 4)).astype(np.int32)], True, (0, 255, 255), 3, cv2.LINE_AA)
    marks_img = np.where(marks[..., None], 255, 30).astype(np.uint8).repeat(3, 2)
    panels = [(debug_overlay(img, grass), "(a) gramado"), (marks_img, "(b) marcações"),
              (lines_img, f"(c) {int((cid < 0).sum())} retas e {len(ells)} elipse(s)"), (draw_overlay(img, H), "(d) modelo pela H do detector")]
    tiles = []
    for p, t in panels:
        p = cv2.resize(p, (800, 450), interpolation=cv2.INTER_AREA)
        cv2.rectangle(p, (0, 0), (800, 30), (0, 0, 0), -1)
        cv2.putText(p, t, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(p)
    cv2.imwrite(str(OUT / "fig2_etapas.jpg"), np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])]), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"fig2: {clip} f{i} ({split}): {int((cid < 0).sum())} retas, {len(ells)} elipses")


def hsb_curve():
    """LocSim@5 por frame (média sobre as pessoas do frame) num clipe do HSB, pela mesma conta
    da T2 (tabelas_test.per_frame): detector, 6c (pipeline) e só propagação."""
    from src import temporal as T
    from src.config import path
    from src.evaluate import locsim
    hsb = {r["clipe"]: r for r in csv.DictReader(open("data_splits/hsb.csv", encoding="utf-8"))}[HSB_CLIP]
    a, b = int(hsb["inicio"]), int(hsb["fim"])
    lo, hi = min(a, b), max(a, b)
    k, res6 = pickle.loads(T._eval_6c_path(path("gsr") / "test" / HSB_CLIP).read_bytes())
    assert k == T._eval_6c_key(), "cache do 6c de outro código"
    ext = {e["clip"]: e for e in pickle.loads((RUN / "extras_test.pkl").read_bytes())["res"]}[HSB_CLIP]["hsb"]["rows"]
    rows = lambda v: [r for r in res6[0] if r["variante"] == v][lo:hi + 1]
    val = lambda r: float(locsim(r["locsim_d"], 5).mean()) if "locsim_d" in r else np.nan
    fr = np.arange(lo, hi + 1)
    det, c6, prop = rows("detector"), rows("6c fluxo"), ext
    assert [r["pos"] for r in prop] == list(fr)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.plot(fr, [val(r) for r in prop], color="#1f77b4", lw=1.2, label="só propagação, a partir da H_gt_auxflow (medição 1)")
    ax.plot(fr, [val(r) for r in c6], color="#d62728", lw=1.2, label="pipeline: propagação com as nossas âncoras (medição 3)")
    has = np.array([r["has_pred"] for r in det])
    ax.plot(fr[has], [val(r) for r, h in zip(det, has) if h], "k.", ms=4, label="detector, só nos frames com H (medição 2)")
    ax.plot(fr[~has], np.full((~has).sum(), -0.04), "|", color="0.5", ms=5, label="detector sem H")
    ax.set_xlabel("frame (numeração do artigo do AuxFlow, a partir de 0)")
    ax.set_ylabel("LocSim@5 do frame")
    ax.set_ylim(-0.08, 1.02)
    ax.set_xlim(lo, hi)
    ax.grid(alpha=0.3)
    ax.yaxis.set_major_formatter(COMMA)
    ax.legend(fontsize=7.5, loc="center left", bbox_to_anchor=(0.0, 0.3), ncol=2)
    ax.set_title(f"{HSB_CLIP}, intervalo {a}-{b} do HSB", fontsize=10)
    fig.savefig(OUT / "fig3_hsb_curva.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def drift():
    """NPE mediano do 6c fluxo e fração de frames com NPE > 0,05 pela distância à âncora
    aceita mais próxima (outputs/runs/rodada_test/falhas/deriva_6c.csv)."""
    rows = list(csv.DictReader(open(RUN / "falhas" / "deriva_6c.csv", encoding="utf-8")))
    bins = ["<= 25", "26-100", "101-250", "> 250"]
    labels = ["≤ 25", "26–100", "101–250", "> 250"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for onde, mk in (("detector com H", "o"), ("lacuna 1-25", "s"), ("lacuna > 25", "^"), ("pontas", "D")):
        r = {x["distancia"]: x for x in rows if x["onde"] == onde}
        lab = {"detector com H": "frames com H do detector", "lacuna 1-25": "lacunas de 1 a 25 frames",
               "lacuna > 25": "lacunas > 25 frames", "pontas": "pontas do clipe"}[onde]
        axs[0].plot(labels, [float(r[b]["npe_med"]) for b in bins], marker=mk, label=lab)
        axs[1].plot(labels, [float(r[b]["erradas"]) for b in bins], marker=mk, label=lab)
    axs[0].set_yscale("log")
    axs[0].set_ylabel("NPE mediano da propagação")
    axs[1].set_ylabel("fração com NPE > 0,05")
    axs[1].yaxis.set_major_formatter(COMMA)
    for a in axs:
        a.set_xlabel("distância à âncora aceita mais próxima (frames)")
        a.grid(alpha=0.3)
    axs[0].legend(fontsize=7.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_deriva.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def gap_strip():
    """A primeira lacuna de lacunas_figuras.csv (a da Figura 7: duas bordas erradas), refeita como
    em analise_falhas.py, só com o rótulo descritivo da suavização S-G (Bassek)."""
    import sys
    sys.path.insert(0, "scripts/rodada_test")
    from analise_falhas import panel
    from src import temporal as T
    from src.config import path
    from src.evaluate import npe_re
    from src.io import gsr
    fig = next(r for r in csv.DictReader(open(RUN / "falhas" / "lacunas_figuras.csv", encoding="utf-8")) if r["classe"] == "as duas bordas erradas")
    c, (a, b) = fig["clipe"], map(int, fig["lacuna"].split("-"))
    clip = path("gsr") / "test" / c
    k, res6 = pickle.loads(T._eval_6c_path(clip).read_bytes())
    assert k == T._eval_6c_key(), "cache do 6c de outro código"
    samples, ser = gsr.load_clip(clip), dict(np.load(T._series_path(clip)))
    mid = (a + b) // 2
    H6 = res6[3]["6a Bassek"][mid].astype(float)
    e = lambda H, s: npe_re(H, s.H_gt, s.size)[0]
    pa, pm, pb = samples[a - 1], samples[mid], samples[b + 1]
    strip = np.hstack([panel(pa.image, ser["H"][a - 1], pa.lines_uv, f"{c} f{a - 1}: detector (borda) NPE {e(ser['H'][a - 1], pa):.3f}"),
                       panel(pm.image, H6, pm.lines_uv, f"f{mid}: S-G (Bassek), lacuna {a}-{b} NPE {e(H6, pm):.3f}"),
                       panel(pb.image, ser["H"][b + 1], pb.lines_uv, f"f{b + 1}: detector (borda) NPE {e(ser['H'][b + 1], pb):.3f}")])
    cv2.imwrite(str(OUT / "fig7_lacuna.jpg"), strip, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"fig7: {c}, lacuna {a}-{b}")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    gap_strip()
    pipeline()
    drift()
    hsb_curve()
    stages()
    print(f"figuras em {OUT}")
