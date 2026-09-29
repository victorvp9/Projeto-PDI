"""Máscaras do 6c (gramado, marcações, onde a grade pode ficar) na GPU, com CuPy (extra
`gpu` do pyproject). Mesma saída de temporal._masks, pixel a pixel
(tests/test_temporal.py). Espaço imagem (px).

A cadeia inteira fica na GPU: um envio (o Lab; a conversão BGR -> Lab de 8 bits fica
na CPU, porque só o OpenCV a reproduz bit a bit) e uma volta (as máscaras
empacotadas). As máscaras do clipe saem em lote, com a leitura do próximo frame numa
thread enquanto a GPU trabalha. Medições em docs/decisoes.md (2026-09-29).
"""
import warnings
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

from src import segment as seg
from src.config import CFG

# Com as wheels da CUDA 12 (uma pasta por componente), o CuPy não deriva uma raiz única e
# avisa; cabeçalhos e DLLs são achados pelo cuda-pathfinder (tests/test_temporal.py).
warnings.filterwarnings("ignore", message="CUDA path could not be detected")
try:                                   # sem o extra `gpu`, sem placa ou sem driver: AVAILABLE = False
    import cupy as cp
    import cupyx.scipy.ndimage as ndi
    AVAILABLE = cp.cuda.runtime.getDeviceCount() > 0
except Exception:
    AVAILABLE = False

P = seg.params("gsr")


class GPUMasks:
    """Máscaras de frames de um tamanho (w, h). Sincroniza só no pico do histograma de
    matiz, no número de componentes e nos momentos do filtro de forma."""

    def __init__(self, size):
        assert P["grass_method"] == "lab_hue" and P["grass_steps"] == ["open", "close", "largest", "fill"]
        assert P["line_method"] == "filter" and P["line_alpha"] is None
        w, h = size
        self.open = cp.asarray(seg._ellipse(P["open_frac"] * h)).astype(bool)
        self.close = cp.asarray(seg._ellipse(P["close_frac"] * h)).astype(bool)
        self.grow = cp.asarray(seg._ellipse(2 * P["grass_dilate_w"] * seg.line_width(h, h, P) + 1)).astype(bool)
        self.k_compact = 2 * int(CFG["temporal"]["compact_dilate_frac"] * h) + 1
        self.e8 = cp.ones((3, 3), bool)                    # 8-vizinhança, como o OpenCV
        vv, uu = cp.mgrid[0:h, 0:w]
        self.u, self.v = uu.astype(cp.uint64).ravel(), vv.astype(cp.uint64).ravel()
        rows = np.linspace(0, h, P["line_bands"] + 1).astype(int)
        self.bands = []                                    # as faixas de segment.line_response
        for r0, r1 in zip(rows[:-1], rows[1:]):
            for s in P["line_scales"]:
                size_ = P["line_k"] * s * seg.line_width((r0 + r1) / 2, h, P)
                pad = int(size_) + 2
                self.bands.append((r0, r1, max(0, r0 - pad), min(h, r1 + pad), max(1, int(round(size_)))))

    def _raw(self, lab):
        """segment._grass_raw (lab_hue)."""
        da = lab[:, :, 1].astype(cp.float32) - 128
        db = lab[:, :, 2].astype(cp.float32) - 128
        valid = lab[:, :, 0] >= P["lab_l_min"]
        hue, chroma = cp.degrees(cp.arctan2(db, da)), cp.hypot(da, db)
        sel = (chroma >= P["lab_c_min"]) & (da < 0) & valid
        idx = cp.where(sel, cp.rint(hue).astype(cp.int32) + 180, 0).ravel()
        hist = cp.bincount(idx, weights=sel.ravel().astype(cp.float64), minlength=361).get()
        peak = np.argmax(np.convolve(hist, np.ones(5) / 5, "same")) - 180
        d = cp.abs((hue.astype(cp.float64) - peak + 180) % 360 - 180)
        return valid & (chroma >= P["lab_c_min"]) & (d <= P["lab_dhue_deg"])

    def _post(self, m):
        """segment._post: abertura e fechamento (borda do OpenCV: 1 na erosão, 0 na
        dilatação), maior componente, buracos preenchidos."""
        m = ndi.binary_dilation(ndi.binary_erosion(m, self.open, border_value=1), self.open, border_value=0)
        m = ndi.binary_erosion(ndi.binary_dilation(m, self.close, border_value=0), self.close, border_value=1)
        lab, n = ndi.label(m, self.e8)
        if n > 0:
            cnt = cp.bincount(lab.ravel(), minlength=n + 1)
            cnt[0] = 0
            m = lab == cp.argmax(cnt)
        bg, _ = ndi.label(~m, self.e8)
        border = cp.unique(cp.concatenate([bg[0], bg[-1], bg[:, 0], bg[:, -1]]))
        return m | (~m & ~cp.isin(bg, border))

    def _lines(self, L, grass):
        """segment.line_mask com o filtro de linha e limiar fixo."""
        out = cp.zeros_like(L)
        for r0, r1, a0, a1, d in self.bands:
            p = cp.pad(L[a0:a1], d, mode="edge")           # BORDER_REPLICATE
            c = p[d:-d, d:-d]
            horiz = cp.minimum(c - p[d:-d, :-2 * d], c - p[d:-d, 2 * d:])
            vert = cp.minimum(c - p[:-2 * d, d:-d], c - p[2 * d:, d:-d])
            out[r0:r1] = cp.maximum(out[r0:r1], cp.maximum(horiz, vert)[r0 - a0:r1 - a0])
        return (out > P["line_thr"]) & ndi.binary_dilation(grass, self.grow, border_value=0)

    def _shape_keep(self, nong):
        """lines.shape_filter: somas inteiras (uint64) dos momentos só nos pixels do
        não-gramado, exatas como as somas em float64 da CPU (inteiros < 2^53)."""
        lab, n = ndi.label(nong, self.e8)
        on = lab.ravel() > 0
        k, u, v = lab.ravel()[on], self.u[on], self.v[on]
        S = cp.zeros((5, n + 1), cp.uint64)
        for j, x in enumerate((u, v, u * u, v * v, u * v)):
            cp.add.at(S[j], k, x)
        cnt = np.maximum(cp.bincount(k, minlength=n + 1).get(), 1).astype(float)
        mu, mv, suu, svv, suv = (s / cnt for s in S.get().astype(float))
        cuu, cvv, cuv = suu - mu ** 2, svv - mv ** 2, suv - mu * mv
        half, disc = (cuu + cvv) / 2, np.sqrt(np.maximum(((cuu - cvv) / 2) ** 2 + cuv ** 2, 0))
        keep = np.sqrt(np.maximum(half + disc, 1 / 12) / np.maximum(half - disc, 1 / 12)) >= CFG["lines"]["shape_elong_min"]
        keep[0] = False
        return cp.asarray(keep)[lab]

    def __call__(self, frame_lab):
        """Lab (uint8, CPU) -> (gramado, marcações, onde a grade pode ficar), cada uma
        empacotada com np.packbits da máscara achatada."""
        lab = cp.asarray(frame_lab)
        raw = self._raw(lab)
        grass = self._post(raw)
        marks = self._lines(lab[:, :, 0].astype(cp.float32), grass)
        nong = grass & ~raw
        compact = nong & ~self._shape_keep(nong)
        compact = ndi.maximum_filter(compact.astype(cp.uint8), size=self.k_compact, mode="constant", cval=0).astype(bool)
        return tuple(cp.packbits(x.ravel()).get() for x in (grass, marks, grass & ~compact))


_cache = {}


def clip_masks(samples):
    """{índice: (marcações, onde a grade pode ficar)} empacotadas, de todos os frames,
    lendo o próximo frame numa thread enquanto a GPU trabalha no atual."""
    size = samples[0].size
    if size not in _cache:
        _cache[size] = GPUMasks(size)
    G = _cache[size]
    load =lambda s: cv2.cvtColor(s.image, cv2.COLOR_BGR2LAB)
    out = {}
    with ThreadPoolExecutor(1) as ex:
        nxt = ex.submit(load, samples[0])
        for i in range(len(samples)):
            lab = nxt.result()
            if i + 1 < len(samples):
                nxt = ex.submit(load, samples[i + 1])
            out[i] = G(lab)[1:]
    return out
