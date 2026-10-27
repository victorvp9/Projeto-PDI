"""Figura do v2 no trabalho final (docs/trabalho-final.md): LocSim@5 penalizado por jogo do GSR test, v1 → v2, da
propagação e do teto condicionado às âncoras. Só lê a T6 da rodada do v2 (outputs/runs_v2/rodada_test_v2/tabelas/T6.csv),
que traz as colunas do v1 ao lado; nada do método roda e nenhum número é recalculado.

Saída: outputs/figures/relatorio_v2/fig_v2_por_jogo.png. Uso (da raiz): figura_v2.py"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

T6 = Path("outputs/runs_v2/rodada_test_v2/tabelas/T6.csv")
OUT = Path("outputs/figures/relatorio_v2")
COMMA = FuncFormatter(lambda x, _: f"{x:.2f}".replace(".", ","))   # vírgula decimal (texto em português)
SERIES = (("propagação", "6c", "#2a78d6", -0.12), ("teto condicionado às âncoras", "teto", "#eb6834", 0.12))  # paleta validada (dataviz)


def main():
    rows = list(csv.DictReader(open(T6, encoding="utf-8")))
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, col, color, dx in SERIES:
        for i, r in enumerate(rows):
            v1, v2 = float(r[f"v1_locsim_pen_{col}"]), float(r[f"locsim_pen_{col}"])
            ax.annotate("", (i + dx, v2), (i + dx, v1), arrowprops=dict(arrowstyle="-|>", color=color, lw=2, shrinkA=5, shrinkB=5))
            ax.plot(i + dx, v1, "o", ms=8, mfc="white", mec=color, mew=2, zorder=3)
            ax.plot(i + dx, v2, "o", ms=8, color=color, mec="white", mew=1.5, zorder=3)
            ax.text(i + dx + (0.06 if dx > 0 else -0.06), v2, f"{v2:.3f}".replace(".", ","), va="center",
                    ha="left" if dx > 0 else "right", fontsize=8, color="0.25")   # rótulo do lado de fora do par
    ax.set_xticks(range(len(rows)), [f"jogo {r['jogo']}" for r in rows])
    ax.set_xlim(-0.5, len(rows) - 0.4)
    ax.set_ylabel("LocSim@5 penalizado")
    ax.yaxis.set_major_formatter(COMMA)
    ax.grid(axis="y", color="0.9")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    leg = [Line2D([], [], color=c, lw=2, label=n) for n, _, c, _ in SERIES]
    leg += [Line2D([], [], ls="", marker="o", ms=8, mfc="white", mec="0.4", mew=2, label="v1 (rodada limpa)"),
            Line2D([], [], ls="", marker="o", ms=8, color="0.4", label="v2 (exploratória)")]
    ax.legend(handles=leg, loc="lower right", fontsize=8, frameon=False)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "fig_v2_por_jogo.png", dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main()
