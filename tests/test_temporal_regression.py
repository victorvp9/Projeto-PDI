"""Regressão da Fatia 6 (Etapa 8) sobre as séries do detector em cache.

Limites (aprovados por Victor em 2026-09-29, docs/decisoes.md): folga de 0,01 no GSR e
NPE mediano <= medido + 10%. A série do detector custa ~1 h por clipe, então vem do
cache (`--detect-series`): sem cache o teste é pulado; com cache de outro detector
(chave diferente) ele falha, para um cache velho não passar em silêncio. Lentos
(~3-5 min).
"""
import numpy as np
import pytest

from src import temporal as T
from src.config import path
from src.evaluate import frame_metrics, summarize
from src.io import gsr

pytestmark = [pytest.mark.slow,
              pytest.mark.skipif(not (path("gsr") / "train").exists(), reason="GSR train ausente em data/")]


def _load(name):
    clip = path("gsr") / "train" / name
    p = T._series_path(clip)
    if not p.exists():
        pytest.skip(f"série do detector de {name} fora do cache: rode --detect-series --splits train --clips {name}")
    ser = dict(np.load(p))
    assert str(ser["key"]) == T._series_key(), f"a série de {name} é de outro detector: rode --detect-series de novo"
    return ser, gsr.load_clip(clip)


def _summary(samples, Hs):
    rows = [dict(**frame_metrics(H if np.isfinite(H).all() else None, s),
                 n_pessoas=0 if s.persons_XY is None else len(s.persons_XY)) for s, H in zip(samples, Hs)]
    t = summarize(rows)["todos"]
    return t["cobertura"], t["npe"][1], t["locsim@5 penalizado"]


def test_propagation_window_sngs099():
    """6c com fluxo em 250 frames do SNGS-099 (5 âncoras aceitas; o detector sozinho dá
    cobertura 0,608 e LocSim@5 penalizado 0,596)."""
    ser, samples = _load("SNGS-099")
    k0, k1 = 400, 650
    win = {k: v[k0:k1] for k, v in ser.items() if k != "key"}
    cf, seg = T.ClipFrames(samples[k0:k1]), np.zeros(k1 - k0, int)
    anc, _, _ = T.anchors(win, cf, seg)
    cov, npe, loc = _summary(samples[k0:k1], T.fill_from_anchors(cf, anc, win["H"], seg, "flow"))
    assert cov >= 0.99 and loc >= 0.811 and npe <= 0.0111, (cov, npe, loc)   # medidos 1,000 / 0,0101 / 0,821


def test_verification_rejects_all_sngs060():
    """SNGS-060: todas as candidatas têm a H do detector errada; a verificação temporal
    não pode aceitar nenhuma (e o teste tem de exercitá-la: >= 5 verificáveis)."""
    ser, samples = _load("SNGS-060")
    anc, _, verifiable = T.anchors(ser, T.ClipFrames(samples), np.zeros(len(samples), int))
    assert len(verifiable) >= 5 and anc == [], (len(verifiable), anc)       # medidos 6 e nenhuma


def test_robust_smoothing_sngs099():
    """6a robusto (Hampel 12/6 + SG na matriz) no SNGS-099 inteiro, e acima do Bassek."""
    ser, samples = _load("SNGS-099")
    size = samples[0].size
    robust = T.smooth_homographies(T.hampel_homographies(ser["H"], size, T.T["hampel_half"], T.T["hampel_sigma"]),
                                   size, "matrix")
    _, npe, loc = _summary(samples, robust)
    _, _, loc_bassek = _summary(samples, T.smooth_homographies(ser["H"], size, "matrix"))
    assert loc >= 0.568 and npe <= 0.0074 and loc >= loc_bassek, (npe, loc, loc_bassek)   # medidos 0,578 / 0,0067; Bassek 0,553
