"""Fatia 4, análise só no treino (WC14 train_val, GSR train): amostra dos falsos
positivos da máscara de marcações, com folhas de contato e a forma do componente
(docs/03-plano.md, Fatia 4, item 1). Espaço imagem (px).
"""
import csv

import cv2
import numpy as np

from src.config import CFG, path
from src.evaluate import _dist_to, lines_target
from src.io import gsr, wc14
from src.render import lines_mask
from src.segment import grass_mask, line_mask, line_width, params

SW = CFG["sweep_lines"]
TOL = CFG["lines"]["tol_frac"]
STEP = CFG["eval_segment"]["gsr_frame_step"]
# pessoa: jogador, árbitro, staff, fotógrafo; linha_desalinhada: linha do modelo com a
# H_gt deslocada (não é falso positivo de verdade); marca_nao_modelada: pênalti,
# tracejados e área técnica; fora_do_campo: placas, torcida, bancos, equipamento
CATEGORIES = ["pessoa", "bola", "trave_rede_bandeira", "publicidade_gramado", "textura_grama",
              "linha_desalinhada", "marca_nao_modelada", "fora_do_campo", "grafismo_tv", "outros"]


def _masks(img, H, size, dataset):
    """Máscara de marcações (config) e seus falsos positivos: pixels a mais de
    `tol_frac`·h da linha com largura desenhada pela H_gt."""
    P = params(dataset)
    lines = line_mask(img, grass_mask(img, P), P)
    return lines, lines & (_dist_to(lines_mask(H, size)) > TOL * size[1])


def _load(base, item):
    """(imagem, H_gt, tamanho, sample) de um item: id do WC14 ou (clipe, frame) do GSR."""
    if base == "wc14":
        s = wc14.load_sample("train_val", item)
        return s.image, s.H_gt, (s.grass.shape[1], s.grass.shape[0]), s
    clip, f = item
    s = next(x for x in gsr.load_clip(clip) if x.frame_idx == f)
    return s.image, s.H_gt, s.size, s


def _count_wc14(image_id):
    cv2.setNumThreads(1)
    img, H, size, _ = _load("wc14", image_id)
    return [(image_id, int(_masks(img, H, size, "wc14")[1].sum()))]


def _count_gsr(clip):
    cv2.setNumThreads(1)
    return [((clip, s.frame_idx), int(_masks(s.image, s.H_gt, s.size, "gsr")[1].sum()))
            for s in gsr.load_clip(clip)[::STEP] if s.H_gt is not None]


def pick_uniform(counts, n, rng):
    """n pixels sorteados sem reposição, uniformes entre todos os falsos positivos:
    [(item, índice do pixel em np.nonzero(fp) do item)]."""
    items, c = zip(*counts)
    cum = np.cumsum(c)
    g = np.sort(rng.choice(cum[-1], n, replace=False))
    k = np.searchsorted(cum, g, side="right")
    return [(items[i], int(j)) for i, j in zip(k, g - np.r_[0, cum][k])]


def _crop(a, u, v, half):
    """Recorte 2·half x 2·half centrado em (u, v), com borda preta fora da imagem."""
    pad = cv2.copyMakeBorder(a, half, half, half, half, cv2.BORDER_CONSTANT, value=0)
    return pad[v:v + 2 * half, u:u + 2 * half]


def _triptych(img, lines, fp, axis, u, v, h):
    """Contexto (com o recorte marcado), recorte cru e recorte com a máscara:
    verdadeiro positivo em verde, falso positivo em magenta, eixo da H_gt em amarelo,
    pixel sorteado no círculo vermelho."""
    S = SW["fp_panel_px"]
    zh, ch = max(4, int(SW["fp_crop_frac"] * h / 2)), int(SW["fp_context_frac"] * h / 2)
    over = img.copy()
    over[lines & ~fp] = (0, 200, 0)
    over[fp] = (255, 0, 255)
    over[axis] = (0, 255, 255)
    ctx = cv2.resize(_crop(img, u, v, ch), (S, S), interpolation=cv2.INTER_AREA)
    r = int(round(zh * S / (2 * ch)))
    cv2.rectangle(ctx, (S // 2 - r, S // 2 - r), (S // 2 + r, S // 2 + r), (0, 0, 255), 1)
    zoom = [cv2.resize(_crop(a, u, v, zh), (S, S), interpolation=cv2.INTER_NEAREST) for a in (img, over)]
    cv2.circle(zoom[1], (S // 2, S // 2), 6, (0, 0, 255), 1)
    gap = np.full((S, 4, 3), 255, np.uint8)
    return np.hstack([ctx, gap, zoom[0], gap, zoom[1]])


def _describe(args):
    """Forma do componente da máscara (8-vizinhança) que contém cada pixel sorteado
    de um item, e o tríptico da folha de contato."""
    base, item, picks = args
    cv2.setNumThreads(1)
    img, H, size, s = _load(base, item)
    P = params(base)
    lines, fp = _masks(img, H, size, base)
    vv, uu = np.nonzero(fp)
    _, lab = cv2.connectedComponents(lines.astype(np.uint8))
    d_gt = _dist_to(lines_mask(H, size))
    axis = lines_target(H, size)
    rows, tiles = [], []
    for pid, j in picks:
        u, v = int(uu[j]), int(vv[j])
        comp = lab == lab[v, u]
        cv_, cu_ = np.nonzero(comp)
        lam = np.sort(np.linalg.eigvalsh(np.cov(np.stack([cu_, cv_])))) if len(cu_) > 2 else np.zeros(2)
        l2, l1 = np.maximum(lam, 1 / 12)                     # barra de 1 px: variância 1/12
        length = np.sqrt(12 * l1)                            # barra uniforme de comprimento L: variância L²/12
        rows.append(dict(id=pid, base=base, imagem=item if base == "wc14" else f"{item[0].name}/{item[1]}",
                         u=u, v=v, dist_gt_px=round(float(d_gt[v, u]), 1), dist_gt_tol=round(float(d_gt[v, u]) / (TOL * size[1]), 2),
                         area_px=len(cu_), alongamento=round(float(np.sqrt(l1 / l2)), 2),
                         espessura_w=round(float(len(cu_) / length / line_width(cv_.mean(), size[1], P)), 2),
                         frac_fp_comp=round(float(fp[comp].mean()), 3),
                         gsr_duvidoso=s.dubious if base == "gsr" else "", gsr_resid_px=round(float(s.line_err), 2)))
        tiles.append(_triptych(img, lines, fp, axis, u, v, size[1]))
    return rows, tiles


def _sheets(tiles, ids, prefix):
    """Folhas de contato: 3 colunas, rótulo acima de cada tríptico."""
    out = path("debug") / "lines"
    out.mkdir(parents=True, exist_ok=True)
    per, cols = SW["fp_per_sheet"], 3
    for k in range(0, len(tiles), per):
        cells = []
        for t, pid in zip(tiles[k:k + per], ids[k:k + per]):
            label = np.full((18, t.shape[1], 3), 255, np.uint8)
            cv2.putText(label, pid, (2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cells.append(cv2.copyMakeBorder(np.vstack([label, t]), 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255, 255, 255)))
        blank = np.full_like(cells[0], 255)
        cells += [blank] * (-len(cells) % cols)
        sheet = np.vstack([np.hstack(cells[i:i + cols]) for i in range(0, len(cells), cols)])
        cv2.imwrite(str(out / f"fp_{prefix}_{k // per + 1:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(out)


def sample_fp(pool):
    """Sorteia `fp_n` pixels falsos positivos por base e grava a forma de cada
    componente (outputs/lines_fp_amostra.csv) e as folhas (outputs/debug/lines/)."""
    from src.run import _write_csv
    rng = np.random.default_rng(SW["fp_seed"])
    rows = []
    with pool() as ex:
        for base, prefix, worker, units in (
                ("wc14", "W", _count_wc14, wc14.split_ids("train_val")),
                ("gsr", "G", _count_gsr, sorted((path("gsr") / "train").glob("SNGS-*")))):
            counts = [c for cs in ex.map(worker, units) for c in cs]
            picks = pick_uniform(counts, SW["fp_n"], rng)
            print(f"{base}: {sum(c for _, c in counts)} pixels falsos positivos em {len(counts)} imagens; {len(picks)} sorteados")
            by_item = {}
            for n_, (item, j) in enumerate(picks, 1):
                by_item.setdefault(item, []).append((f"{prefix}{n_:03d}", j))
            res = list(ex.map(_describe, [(base, item, p) for item, p in by_item.items()]))
            r = [x for rs, _ in res for x in rs]
            t = [x for _, ts in res for x in ts]
            _sheets(t, [x["id"] for x in r], base)
            rows += r
    _write_csv(path("outputs") / "lines_fp_amostra.csv", rows)


def fp_table():
    """Tabela das categorias (outputs/lines_fp_classes.csv, classificação à mão) por
    base, com erro-padrão, e a forma mediana do componente por categoria."""
    read = lambda f: list(csv.DictReader(open(path("outputs") / f, encoding="utf-8")))
    shape = {r["id"]: r for r in read("lines_fp_amostra.csv")}
    cls = read("lines_fp_classes.csv")
    assert {r["categoria"] for r in cls} <= set(CATEGORIES), {r["categoria"] for r in cls} - set(CATEGORIES)
    print("categoria               WC14 (%, ± ep)   GSR (%, ± ep)   | mediana: área px, alongamento, espessura (larguras de linha)")
    for c in CATEGORIES:
        cells = []
        for base in ("wc14", "gsr"):
            b = [r for r in cls if shape[r["id"]]["base"] == base]
            p = sum(r["categoria"] == c for r in b) / len(b)
            cells.append(f"{100 * p:5.1f} ± {100 * np.sqrt(p * (1 - p) / len(b)):4.1f}")
        sel = [shape[r["id"]] for r in cls if r["categoria"] == c]
        med = (lambda k: np.median([float(x[k]) for x in sel])) if sel else (lambda k: np.nan)
        print(f"{c:22}  {cells[0]}      {cells[1]}     | {med('area_px'):8.0f}  {med('alongamento'):6.1f}  {med('espessura_w'):5.1f}   (n={len(sel)})")
