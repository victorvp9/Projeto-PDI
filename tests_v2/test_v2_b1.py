"""v2, B1 (docs/decisoes.md, 2026-10-15): a âncora que passa na verificação por maioria só é aceita
se a nota dela (iou + img) não estiver abaixo de temporal.anchor_min_nota; com null, nada muda."""
from types import SimpleNamespace

import numpy as np

import src_v2.evaluate as E
from src_v2 import temporal as T


def _setup(monkeypatch):
    n = 60
    ser = {"H": np.repeat(np.eye(3)[None], n, axis=0), "img": np.full(n, 0.5), "iou": np.full(n, 0.5)}
    ser["img"][10], ser["iou"][10] = 0.8, 0.9          # nota 1,7
    ser["img"][40], ser["iou"][40] = 0.7, 0.8          # nota 1,5
    monkeypatch.setattr(T, "propagate", lambda cf, a, H, stop, step, lines=True: {u: H for u in range(a + step, stop, step)})
    monkeypatch.setattr(E, "image_grid_displacement", lambda Ha, Hb, size: 0.0)   # todos os vizinhos concordam
    return ser, SimpleNamespace(size=(1920, 1080)), np.zeros(n, int)


def test_anchor_below_min_nota_is_refused(monkeypatch):
    ser, cf, seg = _setup(monkeypatch)
    monkeypatch.setitem(T.T, "anchor_min_nota", 1.6)
    anc, cand, verifiable = T.anchors(ser, cf, seg)
    assert 10 in cand and 40 in cand and 10 in verifiable and 40 in verifiable
    assert 10 in anc and 40 not in anc


def test_null_min_nota_keeps_the_v1_rule(monkeypatch):
    ser, cf, seg = _setup(monkeypatch)
    monkeypatch.setitem(T.T, "anchor_min_nota", None)
    anc, _, _ = T.anchors(ser, cf, seg)
    assert 10 in anc and 40 in anc
