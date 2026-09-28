"""Regressão das Etapas 3 e 4 (Fatia 4), com a configuração do config e dados reais.

Limites = valor medido menos a folga (decisão de Victor): 0,003 no WC14 (1 imagem a
cada 3 do train_val, sem pool de processos, que costuma quebrar no pytest do
Windows) e 0,01 no GSR. As cordas marcadas contam como removidas. As elipses do GSR
ficam fora (25 círculos centrais no subconjunto: um vale 0,04).
"""
import pytest

from src.config import CFG, path
from src.io import gsr, wc14
from src.segment import grass_mask, line_mask, params
from src.sweep_lines import pipeline_counts, summ_pipeline


def _total(rows):
    acc = {}
    for r in rows:
        for k, v in r.items():
            acc[k] = acc.get(k, 0) + v
    return acc


@pytest.mark.skipif(not (path("wc14") / "train_val").exists(), reason="WC14 ausente em data/")
def test_wc14_lines_and_ellipses():
    P, at3, at8 = params("wc14"), [], []
    for i in wc14.split_ids("train_val")[::3]:
        s = wc14.load_sample("train_val", i)
        r3, r8 = pipeline_counts(line_mask(s.image, grass_mask(s.image, P), P), s.H_gt,
                                 (s.grass.shape[1], s.grass.shape[0]), [3, 8], s.grass)
        at3.append(r3)
        at8.append(r8)
    m3, m8 = summ_pipeline(_total(at3)), summ_pipeline(_total(at8))
    assert m3["F1"] >= 0.532, m3                     # medido 0,5359 (70 imagens)
    assert m8["F1"] >= 0.773, m8                     # medido 0,7761; 8 px = p75 do deslocamento do gabarito
    assert m8["elipse_precisao"] >= 0.682, m8        # medido 0,6852 (37 de 54)
    assert m8["elipse_rec_central"] >= 0.357, m8     # medido 0,36 (9 de 25 círculos centrais)


@pytest.mark.skipif(not (path("gsr") / "train").exists(), reason="GSR train ausente em data/")
def test_gsr_lines_subset():
    # clipes do treino [::10], 1 frame a cada 75: o mesmo subconjunto da Fatia 3 (60 frames)
    P, rows = params("gsr"), []
    for clip in sorted((path("gsr") / "train").glob("SNGS-*"))[::10]:
        for s in gsr.load_clip(clip)[::75]:
            if s.H_gt is not None:
                img = s.image
                rows.append(pipeline_counts(line_mask(img, grass_mask(img, P), P), s.H_gt, s.size,
                                            [CFG["lines"]["tol_frac"] * s.size[1]])[0])
    assert len(rows) == 60
    m = summ_pipeline(_total(rows))
    assert m["F1"] >= 0.647, m                       # medido 0,6575
    assert m["recall_linhas"] >= 0.755, m            # medido 0,7654
