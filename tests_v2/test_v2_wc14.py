import numpy as np
import pytest

from src_v2.config import path
from src_v2.geometry import project
from src_v2.io import wc14
from src_v2.pitch_model import CORNERS
from src_v2.render import pitch_mask

pytestmark = pytest.mark.skipif(not (path("wc14") / "train_val").exists(), reason="WC14 ausente em data/")


@pytest.fixture(scope="module")
def train():
    return wc14.load_split("train_val")


def test_split_sizes():
    assert len(wc14.split_ids("train_val")) == 209
    assert len(wc14.split_ids("test")) == 186


def test_conversion_A(train):
    """H_gt nas bandeirinhas = inv(H_arquivo) nos cantos do molde em jardas."""
    corners_yd = np.array([[0, 0], [115, 0], [115, 74], [0, 74]])  # mesma ordem de CORNERS
    d = path("wc14") / "train_val"
    for s in train:
        H_file = np.loadtxt(d / f"{s.image_id}.homographyMatrix")
        uv, _ = project(s.H_gt, CORNERS)
        uv_ref, _ = project(np.linalg.inv(H_file), corners_yd)
        assert np.allclose(uv, uv_ref, rtol=1e-6, atol=1e-6), s.image_id


def test_projected_pitch_lies_on_grass(train):
    """>= 99% do campo projetado pela H_gt cai sobre a máscara `grass`, em todas.

    O IoU é só informativo: a `grass` inclui o gramado fora das linhas. Cego a
    espelhamento e a H que encolhe o campo — a convenção é protegida pelo teste
    de A e pelos overlays (docs/decisoes.md).
    """
    inside, ious = {}, []
    for s in train:
        h, w = s.grass.shape
        m = pitch_mask(s.H_gt, (w, h))
        inside[s.image_id] = (m & s.grass).sum() / m.sum()
        ious.append((m & s.grass).sum() / (m | s.grass).sum())
    print(f"\nWC14 train_val, IoU campo x grass: mediana {np.median(ious):.3f}, min {min(ious):.3f}")
    bad = {k: round(v, 4) for k, v in inside.items() if v < 0.99}
    assert not bad, bad
