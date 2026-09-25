"""Formato interno comum aos loaders (docs/02-dados.md)."""
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Sample:
    image_id: str
    image_path: Path
    H_gt: np.ndarray | None               # 3x3, campo -> imagem (m -> px); None se não estimável
    sequence_id: str | None = None        # None no WC14; id do clipe no GSR
    frame_idx: int | None = None          # None no WC14; número do arquivo no GSR (1-based)
    grass: np.ndarray | None = None       # WC14: máscara de gramado de gabarito (imagem, bool)
    persons_XY: np.ndarray | None = None  # GSR: base-meio das pessoas (campo, m), (N,2)
    boxes_uv: np.ndarray | None = None    # GSR: caixas das mesmas pessoas (imagem, px), (N,4) x,y,w,h
    lines_uv: dict | None = None          # GSR: nome da classe -> pontos anotados (imagem, px), (K,2)
    line_err: float = np.nan              # GSR: mediana da distância pontos anotados -> modelo (px)
    class_err: dict | None = None         # GSR: classe -> mediana da distância dos seus pontos (px)
    dubious: bool = False                 # GSR: gabarito duvidoso (line_err > limiar)

    @property
    def image(self) -> np.ndarray:
        """Frame BGR, lido sob demanda (um clipe inteiro em memória teria ~4,6 GB)."""
        img = cv2.imdecode(np.fromfile(self.image_path, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(self.image_path)
        return img
