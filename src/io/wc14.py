"""Loader do WC14 (Homayounfar et al., 2017). Formato em docs/02-dados.md."""
import numpy as np
from scipy.io import loadmat

from src.config import path
from src.io import Sample
from src.pitch_model import HL, HW, LENGTH, WIDTH

# Molde do arquivo: jardas 115 x 74, origem no canto esquerdo do lado oposto à
# câmera. Afim por eixo campo (m) -> jardas, que leva canto a canto (docs/decisoes.md).
YD_LENGTH, YD_WIDTH = 115.0, 74.0
A = np.array([[YD_LENGTH / LENGTH, 0, HL * YD_LENGTH / LENGTH],
              [0, YD_WIDTH / WIDTH, HW * YD_WIDTH / WIDTH],
              [0, 0, 1]])


def file_to_internal(H_file):
    """`N.homographyMatrix` (imagem -> jardas) para H_gt interno (campo -> imagem)."""
    return np.linalg.inv(H_file) @ A


def load_sample(split: str, image_id: str) -> Sample:
    d = path("wc14") / split
    return Sample(
        image_id=image_id,
        image_path=d / f"{image_id}.jpg",
        H_gt=file_to_internal(np.loadtxt(d / f"{image_id}.homographyMatrix")),
        grass=loadmat(d / f"{image_id}_grass_gt.mat")["grass"].astype(bool),
    )


def split_ids(split: str) -> list[str]:
    """Ids da partição, pelo arquivo de homografia (não pega `*_seg_pred.mat`)."""
    return sorted((p.stem for p in (path("wc14") / split).glob("*.homographyMatrix")), key=int)


def load_split(split: str) -> list[Sample]:
    return [load_sample(split, i) for i in split_ids(split)]
