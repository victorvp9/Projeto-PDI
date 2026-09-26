"""Etapas 1 e 2 (docs/01-metodo.md): máscara do gramado e das marcações.

Espaço imagem (px), entrada BGR do OpenCV. Tamanhos em fração da altura; os que
dependem da largura da linha seguem w(v) = (a + b·v/h)·h, ajustada às larguras
projetadas pela H_gt do treino (regra geral: no pipeline não há H_gt).
"""
import cv2
import numpy as np

from src.config import CFG


def params(dataset: str) -> dict:
    """Parâmetros da segmentação: comuns + os do conjunto de dados ("wc14" | "gsr")."""
    S = CFG["segment"]
    return {**S["common"], **S.get(dataset, {})}


def line_width(v, h, P):
    """Largura típica (px) de uma linha de 0,12 m na linha v da imagem."""
    a, b = P["width_ab"]
    return (a + b * v / h) * h


def _odd(x):
    return int(max(1, 2 * round(x / 2) + 1))


def _ellipse(x):
    k = _odd(x)
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


def green_hue(frame_lab, dhue_deg, c_min, where=None):
    """Pixels (imagem, bool) com ângulo de matiz em (a*, b*) a <= dhue_deg do pico
    verde e croma >= c_min. O pico é medido em `where` (ou na imagem toda).
    Escurecer encolhe o croma mas quase não muda o ângulo: a grama ao sol e na
    sombra diferem ~10-17 graus, e ~27 em distância cromática (docs/decisoes.md)."""
    da = frame_lab[:, :, 1].astype(np.float32) - 128
    db = frame_lab[:, :, 2].astype(np.float32) - 128
    hue, chroma = np.degrees(np.arctan2(db, da)), np.hypot(da, db)
    ok = chroma >= c_min
    sel = ok & (da < 0) if where is None else ok & (da < 0) & where
    hist = np.bincount(np.round(hue[sel]).astype(int) + 180, minlength=361).astype(float)
    peak = np.argmax(np.convolve(hist, np.ones(5) / 5, "same")) - 180
    return ok & (np.abs((hue - peak + 180) % 360 - 180) <= dhue_deg)


def _grass_raw(frame_bgr, P):
    """Pixels verdes, com o pico de cor estimado no próprio quadro."""
    if P["grass_method"] == "hsv":
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        hue, sat, val = cv2.split(frame_hsv)
        valid = (sat >= P["hsv_s_min"]) & (val >= P["hsv_v_min"])
        lo, hi = P["hsv_green_band"]
        hist = np.bincount(hue[valid & (hue >= lo) & (hue <= hi)], minlength=180).astype(float)
        peak = int(np.argmax(np.convolve(hist, np.ones(5) / 5, "same")))
        return valid & (np.abs(hue.astype(int) - peak) <= P["hsv_dh"])
    frame_lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
    L, a, b = cv2.split(frame_lab)
    valid = L >= P["lab_l_min"]
    if P["grass_method"] == "lab_hue":
        return valid & green_hue(frame_lab, P["lab_dhue_deg"], P["lab_c_min"], where=valid)
    green = valid & (a < 128)                      # a* < 0: lado verde
    hist = np.zeros((256, 256), np.float32)
    np.add.at(hist, (a[green], b[green]), 1)
    a0, b0 = np.unravel_index(np.argmax(cv2.GaussianBlur(hist, (0, 0), 2)), hist.shape)
    dist = np.hypot(a.astype(np.float32) - a0, b.astype(np.float32) - b0)
    return valid & (dist <= P["lab_r"])


def _fill_holes(m):
    """Preenche regiões do fundo que não tocam a borda da imagem."""
    n, lab = cv2.connectedComponents((m == 0).astype(np.uint8))
    border = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    return m | ((m == 0) & ~np.isin(lab, border)).astype(np.uint8)


def _post(mask, P):
    h = mask.shape[0]
    m = mask.astype(np.uint8)
    for step in P["grass_steps"]:
        if step == "open":
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, _ellipse(P["open_frac"] * h))
        elif step == "close":
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, _ellipse(P["close_frac"] * h))
        elif step in ("largest", "components"):
            n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
            if n > 1:
                area = stats[1:, cv2.CC_STAT_AREA]
                keep = (1 + np.argmax(area),) if step == "largest" else \
                    tuple(1 + np.nonzero(area >= P["component_min_frac"] * m.size)[0])
                m = np.isin(lab, keep).astype(np.uint8)
        elif step == "fill":
            m = _fill_holes(m)
        else:
            raise ValueError(f"passo desconhecido: {step}")
    return m.astype(bool)


def grass_mask(frame_bgr, P):
    """Máscara bool (imagem) do gramado: cor verde pelo pico do quadro e pós-processamento."""
    return _post(_grass_raw(frame_bgr, P), P)


def line_response(frame_bgr, P):
    """Resposta (L*, 0-255) de faixa clara e fina: top-hat branco ou filtro de linha,
    com escala k·w(v) em `line_bands` faixas horizontais (máximo sobre `line_scales`)."""
    L = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)
    h = L.shape[0]
    out = np.zeros_like(L)
    rows = np.linspace(0, h, P["line_bands"] + 1).astype(int)
    for r0, r1 in zip(rows[:-1], rows[1:]):
        w = line_width((r0 + r1) / 2, h, P)
        for s in P["line_scales"]:
            size = P["line_k"] * s * w
            pad = int(size) + 2
            a0, a1 = max(0, r0 - pad), min(h, r1 + pad)
            sub = L[a0:a1]
            if P["line_method"] == "tophat":
                resp = cv2.morphologyEx(sub, cv2.MORPH_TOPHAT, _ellipse(size))
            else:
                d = max(1, int(round(size)))
                p = cv2.copyMakeBorder(sub, d, d, d, d, cv2.BORDER_REPLICATE)
                c = p[d:-d, d:-d]
                horiz = np.minimum(c - p[d:-d, :-2 * d], c - p[d:-d, 2 * d:])   # mais claro que esquerda e direita
                vert = np.minimum(c - p[:-2 * d, d:-d], c - p[2 * d:, d:-d])    # mais claro que cima e baixo
                resp = np.maximum(horiz, vert)
            out[r0:r1] = np.maximum(out[r0:r1], resp[r0 - a0:r1 - a0])
    return out


def line_mask(frame_bgr, grass, P, response=None):
    """Máscara bool (imagem) das marcações: resposta > `line_thr` dentro do gramado
    dilatado (para não cortar a lateral rente à borda da grama)."""
    if response is None:
        response = line_response(frame_bgr, P)
    h = grass.shape[0]
    grow = _ellipse(2 * P["grass_dilate_w"] * line_width(h, h, P) + 1)
    return (response > P["line_thr"]) & cv2.dilate(grass.astype(np.uint8), grow).astype(bool)


def debug_overlay(frame_bgr, grass=None, lines=None):
    """Depuração: gramado em verde translúcido, marcações em magenta."""
    out = frame_bgr.copy()
    if grass is not None:
        out[grass] = (0.6 * out[grass] + [0, 100, 0]).astype(np.uint8)
    if lines is not None:
        out[lines] = (255, 0, 255)
    return out
