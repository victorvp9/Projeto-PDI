import numpy as np
import pytest

from src.evaluate import (iou_part, iou_whole, locsim, locsim_distances, npe_re,
                          sncalib_accuracy)
from src.geometry import project
from src.pitch_model import POLYLINES

SIZE = (1280, 720)
# campo inteiro dentro do quadro, com folga (o mesmo H de tests/test_render.py)
H = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1.0]])


def _shift_field(d):
    """H de uma estimativa que erra o campo em d metros ao longo de X."""
    return H @ np.array([[1, 0, d], [0, 1, 0], [0, 0, 1.0]])


def test_identity_is_perfect():
    assert iou_whole(H, H) == pytest.approx(1)
    assert iou_part(H, H, SIZE) == pytest.approx(1)
    assert npe_re(H, H, SIZE) == pytest.approx((0, 0), abs=1e-9)


def test_degrades_monotonically_with_known_translation():
    ds = [0.5, 1, 2, 4, 8]
    rows = [(iou_whole(_shift_field(d), H), iou_part(_shift_field(d), H, SIZE), *npe_re(_shift_field(d), H, SIZE))
            for d in ds]
    iw, ip, npe, re = map(np.array, zip(*rows))
    assert (np.diff(iw) < 0).all() and (np.diff(ip) < 0).all() and (np.diff(npe) > 0).all()
    assert re == pytest.approx(ds)     # H_est⁻¹·H_gt desloca todo ponto do campo exatamente d


def test_locsim():
    assert locsim(np.array([0.0, 5.0]), 5) == pytest.approx([1, 0.05])
    XY = np.array([[0.0, 0], [10, -5], [-30, 20]])
    uv, _ = project(H, XY)
    boxes = np.c_[uv[:, 0] - 10, uv[:, 1] - 40, np.full(3, 20), np.full(3, 40)]  # base-meio = uv
    assert locsim_distances(H, boxes, XY) == pytest.approx(0, abs=1e-9)
    assert locsim_distances(_shift_field(2), boxes, XY) == pytest.approx(2)


def test_sncalib_accuracy_counts_classes():
    lines = {}
    for k, poly in POLYLINES.items():
        uv, _ = project(H, poly[::10])
        lines[k] = uv
    assert sncalib_accuracy(H, lines, SIZE, [5, 10, 20]) == [1.0, 1.0, 1.0]
    # imagem deslocada 8 px para baixo em 960x540: as linhas quase horizontais erram ~8 px
    shifted = np.diag([1, 1, 1.0]) @ H
    shifted[1] += (8 / 0.75) * shifted[2]
    acc5, acc10, acc20 = sncalib_accuracy(shifted, lines, SIZE, [5, 10, 20])
    assert acc5 < 1 and acc10 == 1 and acc20 == 1
    # classe projetada sem anotação e classe anotada fora do lugar contam como FP
    wrong = {**lines, "Side line bottom": np.array([[10.0, 10.0], [20, 10]])}
    del wrong["Side line top"]
    assert sncalib_accuracy(H, wrong, SIZE, [5])[0] == pytest.approx(18 / 20)


def test_kpsfr_protocol_identity():
    from src.eval_kpsfr import kpsfr_metrics
    m = kpsfr_metrics(H, H)
    assert m["iou_part"] == pytest.approx(1) and m["iou_whole"] == pytest.approx(1)
    assert m["proj_error_m"] == pytest.approx(0, abs=1e-6) and m["reproj_error"] == pytest.approx(0, abs=1e-6)
