"""Regressão da segmentação da Fatia 3, com a configuração do config e dados reais.

Limites = valor medido no treino menos a folga (decisão de Victor, docs/decisoes.md):
0,003 no WC14 (cálculo determinístico; a folga só cobre versão de biblioteca, e a
abertura sozinha vale +0,005) e 0,01 no subconjunto do GSR.
"""
import numpy as np
import pytest

from src.config import path
from src.evaluate import _iou, is_shadow, shadow_score
from src.io import wc14
from src.segment import grass_mask, params
from src.sweep_segment import _eval_gsr_clip


@pytest.mark.skipif(not (path("wc14") / "train_val").exists(), reason="WC14 ausente em data/")
def test_wc14_grass_iou():
    P, iou, shadow = params("wc14"), [], []
    for i in wc14.split_ids("train_val"):
        s = wc14.load_sample("train_val", i)
        iou.append(_iou(grass_mask(s.image, P), s.grass))
        shadow.append(is_shadow(*shadow_score(s.image, s.grass)))
    iou, shadow = np.array(iou), np.array(shadow)
    assert shadow.sum() == 52                   # critério de sombra aprovado: 52 de 209
    assert iou.mean() >= 0.983, iou.mean()      # medido 0,9861
    assert iou[shadow].mean() >= 0.975, iou[shadow].mean()   # medido 0,9788


GSR_TRAIN = path("gsr") / "train"


@pytest.mark.skipif(not GSR_TRAIN.exists(), reason="GSR train ausente em data/")
def test_gsr_lines_subset():
    # clipes do treino [::10] (SNGS-060, 070, 099, 109, 154, 164), 1 frame a cada 75: 60 frames
    clips = sorted(GSR_TRAIN.glob("SNGS-*"))[::10]
    rows = [r for c in clips for r in _eval_gsr_clip(c, step=75) if r["n_pontos"]]
    assert len(rows) == 60
    cov = np.mean([r["cobertura"] for r in rows])
    prec = np.mean([r["precisao"] for r in rows])
    assert cov >= 0.751, cov                    # medido 0,7608
    assert prec >= 0.523, prec                  # medido 0,5338 (gabarito das linhas corrigido); barra o "marcar tudo"
