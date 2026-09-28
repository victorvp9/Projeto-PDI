"""Fatia 4, análise só no treino (WC14 train_val, GSR train): amostra dos falsos
positivos da máscara de marcações, com folhas de contato e a forma do componente
(docs/03-plano.md, Fatia 4, item 1). Espaço imagem (px).
"""
import csv
import itertools

import cv2
import numpy as np

from src.config import CFG, path
from src.evaluate import _dist_to, lines_target, segment_counts, segment_gt
from src.io import gsr, wc14
from src.lines import fuse, hough, shape_filter
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


# ======================= Etapa 3: varredura das retas (só no treino) =======================
HOUGH_KEYS = ("hough_votes_frac", "hough_min_len_frac", "hough_gap_frac", "shape_filter")
FUSE_KEYS = ("fuse_theta_deg", "fuse_d_frac", "fuse_gap_frac")


def _grid(keys):
    return [dict(zip(keys, v)) for v in itertools.product(*(SW[k] for k in keys))]


def _configs():
    """Configurações da Hough e da fusão (None = sem fusão)."""
    return _grid(HOUGH_KEYS), [None, *_grid(FUSE_KEYS)]


def _frame_counts(marks, gts):
    """Contagens de `segment_counts` de cada configuração (i_hough, i_fusão) para cada
    (gabarito, tolerância) de `gts`."""
    hs, fs = _configs()
    h, filtered, out = marks.shape[0], {}, {}
    for i, hc in enumerate(hs):
        P = {**CFG["lines"], **hc}
        if hc["shape_filter"] not in filtered:
            filtered[hc["shape_filter"]] = shape_filter(marks, P) if hc["shape_filter"] else marks
        raw = hough(filtered[hc["shape_filter"]], P)
        for j, fc in enumerate(fs):
            segs = raw if fc is None else fuse(raw, {**P, **fc}, h)
            out[(i, j)] = [segment_counts(segs, gt, tol)[0] for gt, tol in gts]
    return out


def _add(acc, new):
    for k, per_tol in new.items():
        if k not in acc:
            acc[k] = [dict(c) for c in per_tol]
        else:
            for a, c in zip(acc[k], per_tol):
                for kk, v in c.items():
                    a[kk] += v
    return acc


def _gsr_lines_clip(clip):
    cv2.setNumThreads(1)
    P, acc = params("gsr"), {}
    for s in gsr.load_clip(clip)[::STEP]:
        if s.H_gt is None:
            continue
        img = s.image
        marks = line_mask(img, grass_mask(img, P), P)
        _add(acc, _frame_counts(marks, [(segment_gt(s.H_gt, s.size), TOL * s.size[1])]))
    return acc


def _wc14_lines(image_id):
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    P, size = params("wc14"), (s.grass.shape[1], s.grass.shape[0])
    marks = line_mask(s.image, grass_mask(s.image, P), P)
    gt = segment_gt(s.H_gt, size, region=s.grass)
    return _frame_counts(marks, [(gt, t) for t in SW["wc14_check_px"]])


def _summ(c):
    """Precisão e recall por comprimento, F1, recall de linhas, fragmentação e fração em arcos."""
    p = c["len_match"] / max(c["len_total"], 1e-9)
    r = c["axis_cov"] / max(c["axis_total"], 1)
    return dict(precisao=p, recall=r, F1=2 * p * r / max(p + r, 1e-9), recall_linhas=c["lines_det"] / max(c["lines_vis"], 1),
                fragmentacao=c["segs_match"] / max(c["classes_match"], 1), arco=c["len_arc"] / max(c["len_total"], 1e-9))


def calibrate_lines(pool):
    """Grade das retas: escolha no GSR train (F1 máximo; empate a `noise_lines`, menor
    fragmentação); WC14 train_val a 3 e 8 px só como verificação. Tabelas no
    terminal, outputs/lines_sweep.csv e depuração em outputs/debug/lines/."""
    from src.run import _write_csv
    from src.sweep_segment import W as WS
    hs, fs = _configs()
    with pool() as ex:
        g, w = {}, {}
        for acc in ex.map(_gsr_lines_clip, sorted((path("gsr") / "train").glob("SNGS-*"))):
            _add(g, acc)
        for acc in ex.map(_wc14_lines, wc14.split_ids("train_val")):
            _add(w, acc)
    name = lambda k: {**hs[k[0]], **(fs[k[1]] or {"fusao": "sem"})}
    rows = []
    for k in g:
        row = dict(**name(k), **{f"gsr_{a}": round(b, 4) for a, b in _summ(g[k][0]).items()})
        for t, c in zip(SW["wc14_check_px"], w[k]):
            row.update({f"wc14@{t}_{a}": round(b, 4) for a, b in _summ(c).items()})
        rows.append((k, row))
    _write_csv(path("outputs") / "lines_sweep.csv", [r for _, r in rows])
    n = WS["noise_lines"]
    best = max(r["gsr_F1"] for _, r in rows)
    pick_k, pick = min(((k, r) for k, r in rows if r["gsr_F1"] >= best - n), key=lambda x: (x[1]["gsr_fragmentacao"], -x[1]["gsr_F1"]))
    cols = ["precisao", "recall", "F1", "recall_linhas", "fragmentacao", "arco"]
    head = "   " + " ".join(f"{c[:9]:>9}" for c in cols)

    def show(title, keys):
        print(title)
        print(f"{'':62}GSR train{'':38}| WC14@3 F1  frag | WC14@8 F1  frag")
        for k in keys:
            r = dict(rows)[k]
            cfg = " ".join(f"{a.split('_', 1)[1] if '_' in a else a}={b}" for a, b in name(k).items())
            print(f"   {cfg[:58]:58} " + " ".join(f"{r[f'gsr_{c}']:9.3f}" for c in cols)
                  + f" | {r['wc14@3_F1']:.3f} {r['wc14@3_fragmentacao']:5.2f} | {r['wc14@8_F1']:.3f} {r['wc14@8_fragmentacao']:5.2f}")
    print(f"colunas GSR:{head}")
    top = sorted(g, key=lambda k: -dict(rows)[k]["gsr_F1"])[:12]
    show(f"== Retas, GSR train (1 frame a cada {STEP}), 12 melhores por F1; escolhida: F1 >= {best:.3f} - {n}, menor fragmentação", top)
    show("== Escolhida", [pick_k])
    # ablação na escolhida: sem fusão; filtro de forma trocado
    i, j = pick_k
    flip = next(ii for ii, hc in enumerate(hs) if hc == {**hs[i], "shape_filter": not hs[i]["shape_filter"]})
    show("== Ablação na escolhida: sem fusão; filtro de forma trocado", [(i, 0), (flip, j)])
    wbest = max(rows, key=lambda x: x[1]["wc14@8_F1"])
    show(f"== Melhor no WC14 a 8 px (verificação; escolhida lá: {pick['wc14@8_F1']:.3f})", [wbest[0]])
    _debug_segments(name(pick_k))
    return name(pick_k)


def _debug_segments(cfg):
    """Segmentos da configuração `cfg` sobre 6 frames do GSR train (clipes [::10], frame
    101) e 6 imagens do WC14 train_val, em outputs/debug/lines/segmentos_*.jpg."""
    from src.lines import detect_segments, draw_segments
    P = {**CFG["lines"], **{k: v for k, v in cfg.items() if k != "fusao"}, "fuse": "fusao" not in cfg}
    out = path("debug") / "lines"
    items = [("gsr", (c, 101)) for c in sorted((path("gsr") / "train").glob("SNGS-*"))[::10]]
    items += [("wc14", i) for i in wc14.split_ids("train_val")[::35]]
    for base, item in items:
        img, H, size, _ = _load(base, item)
        Q = params(base)
        segs = detect_segments(line_mask(img, grass_mask(img, Q), Q), P)
        tag = item if base == "wc14" else f"{item[0].name}_{item[1]}"
        cv2.imwrite(str(out / f"segmentos_{base}_{tag}.jpg"), draw_segments(img, segs))
    print(out)


# ======================= Etapa 4: varredura das elipses (só no treino) =======================
ELLIPSE_KEYS = ("ellipse_tol_frac", "ellipse_arc_min_frac", "ellipse_turn_min_deg", "ellipse_hough_min_len_frac")


def _ellipse_frame(marks, H, size, tols, region=None):
    """Por configuração de elipse e por tolerância: contagens das elipses e das retas
    antes e depois de tirar as cordas."""
    from src.conics import chord_ids, detect_ellipses
    from src.evaluate import ellipse_counts, ellipse_gt
    from src.lines import detect_segments
    segs, h = detect_segments(marks), size[1]
    gt, egt = segment_gt(H, size, region), ellipse_gt(H, size)
    before = [segment_counts(segs, gt, t)[0] for t in tols]
    out = []
    for cfg in _grid(ELLIPSE_KEYS):
        P = {**CFG["lines"], **cfg}
        ells = detect_ellipses(marks, P, lines=segs)
        after = segs[chord_ids(segs, ells, h, P) < 0]      # as marcadas contam como removidas
        out.append([dict(**ellipse_counts(ells, egt, marks.shape, t), **{f"antes_{k}": v for k, v in b.items()},
                         **{f"depois_{k}": v for k, v in segment_counts(after, gt, t)[0].items()})
                    for t, b in zip(tols, before)])
    return out


def _add_list(acc, new):
    if acc is None:
        return [[dict(c) for c in per_tol] for per_tol in new]
    for a_cfg, n_cfg in zip(acc, new):
        for a, c in zip(a_cfg, n_cfg):
            for k, v in c.items():
                a[k] += v
    return acc


def _gsr_ellipse_clip(clip):
    cv2.setNumThreads(1)
    P, acc = params("gsr"), None
    for s in gsr.load_clip(clip)[::STEP]:
        if s.H_gt is None:
            continue
        img = s.image
        acc = _add_list(acc, _ellipse_frame(line_mask(img, grass_mask(img, P), P), s.H_gt, s.size, [TOL * s.size[1]]))
    return acc


def _wc14_ellipse(image_id):
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    P, size = params("wc14"), (s.grass.shape[1], s.grass.shape[0])
    return _ellipse_frame(line_mask(s.image, grass_mask(s.image, P), P), s.H_gt, size, SW["wc14_check_px"], s.grass)


def _esumm(c):
    """Elipses: precisão, recall (central, arcos, junto), F1; o F1 pela regra dos 80%;
    e as retas antes/depois de tirar as cordas (fração em cordas, precisão, recall)."""
    r = lambda a, b: c[a] / max(c[b], 1)
    f1 = lambda p, q: 2 * p * q / max(p + q, 1e-9)
    p, p80 = r("det_match", "det"), r("det_match80", "det")
    rec = (c["det_central"] + c["det_arco"]) / max(c["vis_central"] + c["vis_arco"], 1)
    rec80 = (c["det_central80"] + c["det_arco80"]) / max(c["vis_central"] + c["vis_arco"], 1)
    lines = lambda k: dict(cordas=c[f"{k}_len_arc"] / max(c[f"{k}_len_total"], 1e-9),
                           precisao=c[f"{k}_len_match"] / max(c[f"{k}_len_total"], 1e-9),
                           recall=c[f"{k}_axis_cov"] / max(c[f"{k}_axis_total"], 1))
    return dict(precisao=p, rec_central=r("det_central", "vis_central"), rec_arco=r("det_arco", "vis_arco"), recall=rec,
                F1=f1(p, rec), F1_80=f1(p80, rec80), elipses=c["det"],
                **{f"retas_antes_{k}": v for k, v in lines("antes").items()},
                **{f"retas_depois_{k}": v for k, v in lines("depois").items()})


def calibrate_ellipses(pool):
    """Grade das elipses: escolha no GSR train (F1 máximo; empate a `noise_lines`, menor
    fração de cordas restante); WC14 train_val a 3 e 8 px como verificação."""
    from src.run import _write_csv
    from src.sweep_segment import W as WS
    cfgs = _grid(ELLIPSE_KEYS)
    with pool() as ex:
        g, w = None, None
        for acc in ex.map(_gsr_ellipse_clip, sorted((path("gsr") / "train").glob("SNGS-*"))):
            if acc is not None:
                g = _add_list(g, acc)
        for acc in ex.map(_wc14_ellipse, wc14.split_ids("train_val")):
            w = _add_list(w, acc)
    rows = []
    for cfg, gc, wc in zip(cfgs, g, w):
        row = dict(**cfg, **{f"gsr_{k}": round(v, 4) for k, v in _esumm(gc[0]).items()},
                   vis_central=gc[0]["vis_central"], vis_arco=gc[0]["vis_arco"])
        for t, c in zip(SW["wc14_check_px"], wc):
            row.update({f"wc14@{t}_{k}": round(v, 4) for k, v in _esumm(c).items()})
        rows.append(row)
    _write_csv(path("outputs") / "lines_sweep_elipses.csv", rows)
    n = WS["noise_lines"]
    best = max(r["gsr_F1"] for r in rows)
    pick = min((r for r in rows if r["gsr_F1"] >= best - n), key=lambda r: (r["gsr_retas_depois_cordas"], -r["gsr_F1"]))
    print(f"== Elipses, GSR train ({rows[0]['vis_central']} círculos centrais e {rows[0]['vis_arco']} arcos visíveis): escolhida = F1 >= {best:.3f} - {n}, menor fração de cordas depois")
    print("   tau     S    leque | prec  rec_c  rec_a  F1    F1_80 elipses | cordas antes->depois | prec retas antes->depois | rec retas antes->depois | WC14@3 F1 | WC14@8 F1 cordas depois")
    for r in sorted(rows, key=lambda r: -r["gsr_F1"]):
        print(f"   {r['ellipse_tol_frac']:.4f} {r['ellipse_arc_min_frac']:4} {r['ellipse_turn_min_deg']:5} | {r['gsr_precisao']:.3f} {r['gsr_rec_central']:.3f} {r['gsr_rec_arco']:.3f} "
              f"{r['gsr_F1']:.3f} {r['gsr_F1_80']:.3f} {r['gsr_elipses']:6.0f} | {r['gsr_retas_antes_cordas']:.3f} -> {r['gsr_retas_depois_cordas']:.3f} | "
              f"{r['gsr_retas_antes_precisao']:.3f} -> {r['gsr_retas_depois_precisao']:.3f} | {r['gsr_retas_antes_recall']:.3f} -> {r['gsr_retas_depois_recall']:.3f} "
              f"| {r['wc14@3_F1']:.3f}     | {r['wc14@8_F1']:.3f} {r['wc14@8_retas_depois_cordas']:.3f}" + ("   <- escolhida" if r is pick else ""))
    return {k: pick[k] for k in ELLIPSE_KEYS}


# ======================= Etapas 3 e 4: avaliação da configuração do config =======================
def pipeline_counts(marks, H, size, tols, region=None):
    """Contagens das retas (sem as cordas marcadas, contadas como removidas) e das
    elipses da configuração do config, a cada tolerância de `tols` (px)."""
    from src.conics import detect
    from src.evaluate import ellipse_counts, ellipse_gt
    segs, ells, cid = detect(marks)
    gt, egt = segment_gt(H, size, region), ellipse_gt(H, size)
    return [dict(**segment_counts(segs[cid < 0], gt, t)[0], **ellipse_counts(ells, egt, marks.shape, t)) for t in tols]


def summ_pipeline(c):
    """Retas: precisão, recall, F1, recall de linhas, fragmentação; elipses: precisão, recall do central."""
    return dict(**_summ(c), elipse_precisao=c["det_match"] / max(c["det"], 1),
                elipse_rec_central=c["det_central"] / max(c["vis_central"], 1))
