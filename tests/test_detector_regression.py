"""Regressão do detector sozinho (Fatia 5, Etapas 1-7), com o config e dados reais.

Limites (decisão de Victor): cobertura e IoU_whole mediano com as folgas de sempre
(0,01 no GSR, 0,003 no WC14); NPE mediano <= medido + 10%, porque cobertura e IoU
não pegam piora pequena de geometria. Lentos (~7 min): `pytest -m "not slow"` no dia
a dia; a suíte completa roda antes de cada commit.
"""
import pytest

from src.assign import detect_frame
from src.config import path
from src.evaluate import frame_metrics, summarize
from src.io import gsr, wc14


def _h(frame_bgr, dataset):
    return next(iter(detect_frame(frame_bgr, dataset).values()))[0]


def _check(rows, cov, iou, npe):
    t = summarize(rows)["todos"]
    assert t["cobertura"] >= cov, t
    assert t["iou_whole"][1] >= iou, t
    assert t["npe"][1] <= npe, t


@pytest.mark.slow
@pytest.mark.skipif(not (path("gsr") / "train").exists(), reason="GSR train ausente em data/")
def test_gsr_detector_subset():
    # clipes do treino [::10], 1 frame a cada 75: o subconjunto das Fatias 3 e 4 (60 frames)
    rows = [frame_metrics(_h(s.image, "gsr"), s)
            for c in sorted((path("gsr") / "train").glob("SNGS-*"))[::10]
            for s in gsr.load_clip(c)[::75] if s.H_gt is not None]
    assert len(rows) == 60
    _check(rows, cov=0.423, iou=0.939, npe=0.0064)          # medidos 0,4333 / 0,9492 / 0,00581


@pytest.mark.slow
@pytest.mark.skipif(not (path("wc14") / "train_val").exists(), reason="WC14 ausente em data/")
def test_wc14_detector_subset():
    # 1 imagem a cada 6 do train_val (35): uma imagem vale 0,029 de cobertura, então é alarme exato
    rows = [frame_metrics(_h(s.image, "wc14"), s)
            for s in (wc14.load_sample("train_val", i) for i in wc14.split_ids("train_val")[::6])]
    _check(rows, cov=0.511, iou=0.907, npe=0.0108)          # medidos 0,5143 / 0,9101 / 0,00979
