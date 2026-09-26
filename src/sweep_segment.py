"""Calibração da Fatia 3, só no treino (WC14 train_val e GSR train): espaço de cor
do gramado, ablação morfológica, top-hat x filtro de linha e cobertura das
marcações por faixa de largura projetada. Regras de decisão em docs/03-plano.md.
"""
import itertools

import cv2
import numpy as np

from src.config import CFG, path
from src.evaluate import (_dist_to, _iou, field_grass_and_leak, is_shadow, lines_target,
                          point_widths, shadow_score)
from src.geometry import project
from src.io import gsr, wc14
from src.pitch_model import POLYLINES
from src.render import lines_mask
from src.segment import grass_mask, line_mask, line_response, params

W = CFG["sweep_segment"]
ES = CFG["eval_segment"]
GAIN_ALL, GAIN_SHADOW, MAX_DROP = 0.005, 0.02, 0.002    # regra da ablação (aprovada por Victor)


def _grid(d):
    keys = list(d)
    return [dict(zip(keys, v)) for v in itertools.product(*(d[k] for k in keys))]


def color_configs():
    return [{"grass_method": m, **c} for m in ("hsv", "lab", "lab_hue") for c in _grid(W[m])]


def _wc14_grass(args):
    """IoU de cada configuração de gramado numa imagem do WC14 + se ela tem sombra."""
    image_id, configs = args
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    img, base = s.image, params("wc14")
    return is_shadow(*shadow_score(img, s.grass)), [_iou(grass_mask(img, {**base, **c}), s.grass) for c in configs]


def _summ(shadow, ious):
    sh = np.array(shadow)
    a = np.array(ious)
    return dict(media=a.mean(), mediana=np.median(a), media_sombra=a[sh].mean(), media_sem_sombra=a[~sh].mean())


def _line_combos():
    return [(m, k, tuple(sc), t) for m in ("tophat", "filter") for k in W["line_k"]
            for sc in W["line_scales"] for t in W["line_thr"]]


def _bin_counts(d_pred, pts, widths, gamma):
    """Pontos cobertos e totais por faixa de largura projetada."""
    edges = W["width_bins_px"]
    u = np.clip(np.round(pts[:, 0]).astype(int), 0, d_pred.shape[1] - 1)
    v = np.clip(np.round(pts[:, 1]).astype(int), 0, d_pred.shape[0] - 1)
    ok = d_pred[v, u] <= gamma
    b = np.digitize(widths, edges[1:-1])
    return np.bincount(b, weights=ok, minlength=len(edges) - 1), np.bincount(b, minlength=len(edges) - 1)


def _line_counts(img, grass, P, axis, width_t, pts, widths, gammas_cov, gamma_prec, gamma_bins):
    """Contagens (somáveis entre imagens) de cobertura, precisão e cobertura por
    largura para todas as combinações de método, escala e limiar."""
    d_w = _dist_to(width_t)
    out = {}
    for m, k, sc in {(m, k, sc) for m, k, sc, _ in _line_combos()}:
        Q = {**P, "line_method": m, "line_k": k, "line_scales": list(sc)}
        resp = line_response(img, Q)
        for t in W["line_thr"]:
            pred = line_mask(img, grass, {**Q, "line_thr": t}, response=resp)
            d_pred = _dist_to(pred)
            c = {"pred": pred.sum(), "axis": axis.sum() if axis is not None else 0}
            for g in gammas_cov:
                c[f"cob{g}"] = (d_pred[axis] <= g).sum() if axis is not None else 0
            c[f"prec{gamma_prec}"] = (d_w[pred] <= gamma_prec).sum()
            c["pts_ok"], c["pts"] = _bin_counts(d_pred, pts, widths, gamma_bins)
            out[(m, k, sc, t)] = c
    return out


def _wc14_lines(args):
    image_id, P = args
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    img, H, size = s.image, s.H_gt, (s.grass.shape[1], s.grass.shape[0])
    grass = grass_mask(img, P)
    axis = lines_target(H, size, region=s.grass)
    # pontos do modelo (1 m) dentro da grass de gabarito, para a cobertura por largura
    b = ES["border_px"]
    model = {}
    for k, poly in POLYLINES.items():
        uv, ok = project(H, poly[:: max(1, int(W["wc14_model_step_m"] / CFG["pitch"]["sample_step_m"]))])
        uv = uv[ok & (uv[:, 0] > b) & (uv[:, 0] < size[0] - b) & (uv[:, 1] > b) & (uv[:, 1] < size[1] - b)]
        uv = uv[s.grass[uv[:, 1].astype(int), uv[:, 0].astype(int)]] if len(uv) else uv
        if len(uv):
            model[k] = uv
    widths = point_widths(H, model)
    pts = np.concatenate(list(model.values())) if model else np.zeros((0, 2))
    wd = np.concatenate(list(widths.values())) if model else np.zeros(0)
    return _line_counts(img, grass, P, axis, lines_mask(H, size), pts, wd,
                        ES["wc14_gamma_px"], ES["decision_gamma_px"], ES["decision_gamma_px"])


def _gsr_clip(args):
    """GSR, 1 frame a cada `gsr_frame_step`: marcações (com o gramado escolhido) e as
    métricas de gramado de cada configuração em `grass_cfgs`."""
    clip, P, grass_cfgs = args
    cv2.setNumThreads(1)
    lines_tot, grass_rows = {}, []
    for s in gsr.load_clip(clip)[::ES["gsr_frame_step"]]:
        if s.H_gt is None:
            continue
        img = s.image
        for name, c in grass_cfgs:
            frac, leak = field_grass_and_leak(grass_mask(img, {**params("gsr"), **c}), s.H_gt, s.size)
            grass_rows.append(dict(config=name, clip=clip.name, frame=s.frame_idx, campo_grama=frac, vazamento=leak))
        pts = gsr.inner_points(s.lines_uv, s.size)
        widths = point_widths(s.H_gt, pts)
        P_ = {**params("gsr"), **P}
        c = _line_counts(img, grass_mask(img, P_), P_, None, lines_mask(s.H_gt, s.size),
                         np.concatenate(list(pts.values())) if pts else np.zeros((0, 2)),
                         np.concatenate(list(widths.values())) if pts else np.zeros(0),
                         [], ES["gsr_precision_px"], ES["gsr_coverage_px"])
        for key, v in c.items():
            acc = lines_tot.setdefault(key, {kk: 0 for kk in v})
            for kk, vv in v.items():
                acc[kk] = acc[kk] + vv
    return lines_tot, grass_rows


def _sum_counts(dicts):
    tot = {}
    for d in dicts:
        for key, v in d.items():
            acc = tot.setdefault(key, {kk: 0 for kk in v})
            for kk, vv in v.items():
                acc[kk] = acc[kk] + vv
    return tot


STEPS = ["open", "close", "largest", "fill"]


def _step_configs(color):
    """Todos os subconjuntos (na ordem canônica) dos passos, e as variantes com
    "componentes >= f" no lugar do "maior componente"."""
    out = {}
    for mask in itertools.product([False, True], repeat=len(STEPS)):
        st = [s for s, on in zip(STEPS, mask) if on]
        out[tuple(st)] = {**color, "grass_steps": st}
        if "largest" in st:
            for f in W["component_min_frac"]:
                alt = ["components" if s == "largest" else s for s in st]
                out[(*alt, f)] = {**color, "grass_steps": alt, "component_min_frac": f}
    return out


def _passes(new, cur):
    d_all, d_sh = new["media"] - cur["media"], new["media_sombra"] - cur["media_sombra"]
    return (d_all >= GAIN_ALL and d_sh >= -MAX_DROP) or (d_sh >= GAIN_SHADOW and d_all >= -MAX_DROP)


def _wc14_table(ex, configs):
    ids = wc14.split_ids("train_val")
    res = list(ex.map(_wc14_grass, [(i, configs) for i in ids]))
    shadow = [r[0] for r in res]
    return shadow, [_summ(shadow, [r[1][j] for r in res]) for j in range(len(configs))]


def _pr(c, cov_key, prec_key):
    cov = c[cov_key] / max(c["axis"], 1) if c["axis"] else c["pts_ok"].sum() / max(c["pts"].sum(), 1)
    prec = c[prec_key] / max(c["pred"], 1)
    return cov, prec, 2 * cov * prec / max(cov + prec, 1e-9)


def run(pool):
    """Roda a calibração inteira e grava tabelas em outputs/ e figuras em outputs/figures/."""
    from src.run import _write_csv
    out_rows = {}
    with pool() as ex:
        # 1. espaço de cor (pós-processamento padrão)
        colors = color_configs()
        shadow, summ = _wc14_table(ex, colors)
        print(f"WC14 train_val: {len(shadow)} imagens, {sum(shadow)} com sombra")
        rows = [dict(**c, **{k: round(v, 4) for k, v in s.items()}) for c, s in zip(colors, summ)]
        _write_csv(path("outputs") / "segment_sweep_cor_wc14.csv", rows)
        best = {m: max((r for r in rows if r["grass_method"] == m), key=lambda r: r["media"])
                for m in ("hsv", "lab", "lab_hue")}
        color = max(best.values(), key=lambda r: r["media"])
        color_cfg = {k: color[k] for k in colors[rows.index(color)]}
        out_rows["cor"] = best

        # 2. ablação dos passos, em sequência, com a regra aprovada
        step_cfgs = _step_configs(color_cfg)
        _, s_summ = _wc14_table(ex, list(step_cfgs.values()))
        table = dict(zip(step_cfgs, s_summ))
        cur, log = (), [("cru", table[()], True)]
        for step in STEPS:
            cand = tuple(s for s in STEPS if s in cur or s == step)
            ok = _passes(table[cand], table[cur])
            log.append((f"+ {step}", table[cand], ok))
            if ok:
                cur = cand
        if "largest" in cur:
            for f in W["component_min_frac"]:
                alt = (*["components" if s == "largest" else s for s in cur], f)
                ok = _passes(table[alt], table[cur])
                log.append((f"maior componente -> componentes >= {f}", table[alt], ok))
                if ok and table[alt]["media"] > table[cur]["media"]:
                    cur = alt
        steps = [s for s in cur if isinstance(s, str)]
        final = {**step_cfgs[cur]}
        out_rows["ablacao"] = log

        # 3. tamanhos da abertura e do fechamento (tabela; a escolha é a do config)
        if "open" in steps or "close" in steps:
            sizes = [{**final, "open_frac": o, "close_frac": c} for o in W["open_frac"] for c in W["close_frac"]]
            _, z = _wc14_table(ex, sizes)
            out_rows["tamanhos"] = list(zip(sizes, z))
        final = grass_config()
        _, (final_summ,) = _wc14_table(ex, [final])
        out_rows["final"] = (final, final_summ)

        # 4. marcações no WC14 e no GSR, com o gramado final
        post = {k: final[k] for k in ("grass_steps", "open_frac", "close_frac", "component_min_frac") if k in final}
        gcfgs = [(m, {**{k: best[m][k] for k in ["grass_method", *W[m]]}, **post}) for m in best]
        lines = run_lines(ex, final, gcfgs)
    return dict(rows=out_rows, final=final, **lines)


def grass_config():
    """Gramado aprovado (config), para a varredura das marcações."""
    keys = ("grass_method", "lab_dhue_deg", "lab_c_min", "lab_l_min", "grass_steps", "open_frac", "close_frac")
    return {k: CFG["segment"]["common"][k] for k in keys}


def run_lines(ex, final, gcfgs):
    """Varredura das marcações (WC14 e GSR) com o gramado `final`; métricas de gramado
    no GSR para cada configuração de `gcfgs`."""
    P14 = {**params("wc14"), **final}
    lines14 = _sum_counts(ex.map(_wc14_lines, [(i, P14) for i in wc14.split_ids("train_val")]))
    res = list(ex.map(_gsr_clip, [(c, final, gcfgs) for c in sorted((path("gsr") / "train").glob("SNGS-*"))]))
    return dict(lines14=lines14, lines_gsr=_sum_counts([r[0] for r in res]), grass_gsr=[row for r in res for row in r[1]])


def report(r):
    """Tabelas no terminal, CSVs em outputs/ e curvas precisão x cobertura."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.run import _write_csv
    f4 = lambda x: f"{x:.4f}"
    if "rows" not in r:
        return report_lines(r)
    print("\n== 1. Espaço de cor (melhor de cada, pós-processamento padrão), IoU no WC14 train_val")
    print("método    média   mediana  sombra  sem sombra  parâmetros")
    for m, row in r["rows"]["cor"].items():
        print(f"{m:8} {f4(row['media'])} {f4(row['mediana'])}  {f4(row['media_sombra'])}  {f4(row['media_sem_sombra'])}   "
              + " ".join(f"{k}={row[k]}" for k in W[m]))
    print("\n== 2. Ablação (regra: +0,005 na média ou +0,02 na sombra, sem o outro cair > 0,002)")
    print("passo                                   média   mediana  sombra  sem sombra  fica?")
    for name, s, ok in r["rows"]["ablacao"]:
        print(f"{name:38} {f4(s['media'])} {f4(s['mediana'])}  {f4(s['media_sombra'])}  {f4(s['media_sem_sombra'])}   {'sim' if ok else 'não'}")
    _write_csv(path("outputs") / "segment_ablacao_wc14.csv",
               [dict(passo=n, fica=ok, **{k: round(v, 4) for k, v in s.items()}) for n, s, ok in r["rows"]["ablacao"]])
    if "tamanhos" in r["rows"]:
        print("\n   tamanhos (abertura x fechamento, fração da altura): média / sombra")
        for c, s in r["rows"]["tamanhos"]:
            print(f"   abertura {c['open_frac']:<6} fechamento {c['close_frac']:<5} {f4(s['media'])} / {f4(s['media_sombra'])}")
    final, fs = r["rows"]["final"]
    print(f"\n   FINAL (config): {final}\n   IoU média {f4(fs['media'])} mediana {f4(fs['mediana'])} sombra {f4(fs['media_sombra'])} sem sombra {f4(fs['media_sem_sombra'])}")

    print("\n== 3. Gramado no GSR train (1 a cada 25 frames): fração do campo projetado como grama; vazamento (> 4,1 m fora das linhas)")
    g = r["grass_gsr"]
    for m in dict.fromkeys(x["config"] for x in g):
        fr = np.array([x["campo_grama"] for x in g if x["config"] == m]); lk = np.array([x["vazamento"] for x in g if x["config"] == m])
        print(f"   {m:8} campo como grama: média {np.nanmean(fr):.4f} mediana {np.nanmedian(fr):.4f}   vazamento: média {np.nanmean(lk):.4f} mediana {np.nanmedian(lk):.4f}")
    _write_csv(path("outputs") / "segment_gramado_gsr.csv", g)

    report_lines(r)


def report_lines(r):
    """Seções 4 e 5 do relatório (marcações)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.run import _write_csv
    print("\n== 4. Marcações: top-hat x filtro de linha")
    g3, gc, gp = ES["decision_gamma_px"], ES["gsr_coverage_px"], ES["gsr_precision_px"]
    rows, best = [], {}
    for key, c in r["lines14"].items():
        cov, prec, f1 = _pr(c, f"cob{g3}", f"prec{g3}")
        cg = r["lines_gsr"][key]
        covg, precg, f1g = _pr(cg, None, f"prec{gp}")
        row = dict(metodo=key[0], k=key[1], escalas="+".join(f"{x:g}" for x in key[2]), limiar=key[3], **{f"wc14_cob@{g}": round(c[f"cob{g}"] / max(c["axis"], 1), 4) for g in ES["wc14_gamma_px"]},
                   **{f"wc14_prec@{g3}": round(prec, 4), f"wc14_F1@{g3}": round(f1, 4),
                      f"gsr_cob@{gc}": round(covg, 4), f"gsr_prec@{gp}": round(precg, 4), "gsr_F1": round(f1g, 4)})
        rows.append(row)
        if key[0] not in best or f1 > best[key[0]][0]:
            best[key[0]] = (f1, key, row)
    _write_csv(path("outputs") / "segment_sweep_linhas.csv", rows)
    print(f"método   k     escalas  limiar   WC14 cob@2/@3/@5          prec@3   F1@3   |  GSR cob@{gc}  prec@{gp}  F1")
    for m, (_, key, row) in best.items():
        print(f"{m:7} {key[1]:5} {row['escalas']:8} {key[3]:6}   {row['wc14_cob@2']:.3f} / {row['wc14_cob@3']:.3f} / {row['wc14_cob@5']:.3f}   "
              f"{row[f'wc14_prec@{g3}']:.3f}   {row[f'wc14_F1@{g3}']:.3f}  |  {row[f'gsr_cob@{gc}']:.3f}    {row[f'gsr_prec@{gp}']:.3f}   {row['gsr_F1']:.3f}")
    gbest = {m: max((x for x in rows if x["metodo"] == m), key=lambda x: x["gsr_F1"]) for m in ("tophat", "filter")}
    print("   (melhor F1 no próprio GSR, só referência: " + "; ".join(f"{m} k={x['k']} escalas={x['escalas']} limiar={x['limiar']} F1 {x['gsr_F1']:.3f}" for m, x in gbest.items()) + ")")
    print("   melhor F1@3 no WC14 por método e escalas:")
    for m in ("tophat", "filter"):
        for sc in W["line_scales"]:
            e = "+".join(f"{x:g}" for x in sc)
            x = max((x for x in rows if x["metodo"] == m and x["escalas"] == e), key=lambda x: x[f"wc14_F1@{g3}"])
            print(f"     {m:7} escalas {e:6} k={x['k']:<5} limiar={x['limiar']:<3} WC14 F1 {x[f'wc14_F1@{g3}']:.3f} cob@3 {x['wc14_cob@3']:.3f} prec@3 {x[f'wc14_prec@{g3}']:.3f} | GSR cob@2 {x[f'gsr_cob@{gc}']:.3f} prec@3 {x[f'gsr_prec@{gp}']:.3f}")

    print("\n== 5. Cobertura por faixa de largura projetada (px), no ponto de F1 máximo do WC14")
    edges = W["width_bins_px"]
    labels = [f"[{a},{b})" if b < 999 else f">={a}" for a, b in zip(edges[:-1], edges[1:])]
    wrows = []
    for m, (_, key, _) in best.items():
        for name, c, g in (("WC14", r["lines14"][key], g3), ("GSR", r["lines_gsr"][key], gc)):
            cov = c["pts_ok"] / np.maximum(c["pts"], 1)
            print(f"   {m:7} {name:4} @{g}px: " + "  ".join(f"{l} {v:.3f} (n={int(n)})" for l, v, n in zip(labels, cov, c["pts"])))
            wrows.append(dict(metodo=m, base=name, gamma=g, **{l: round(v, 4) for l, v in zip(labels, cov)},
                              **{f"n {l}": int(n) for l, n in zip(labels, c["pts"])}))
    _write_csv(path("outputs") / "segment_cobertura_largura.csv", wrows)

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for m, ls in (("tophat", "-"), ("filter", "--")):
        for sc in W["line_scales"]:
            k = best[m][1][1]
            pts14 = [_pr(r["lines14"][(m, k, tuple(sc), t)], f"cob{g3}", f"prec{g3}")[:2] for t in W["line_thr"]]
            ptsg = [_pr(r["lines_gsr"][(m, k, tuple(sc), t)], None, f"prec{gp}")[:2] for t in W["line_thr"]]
            lab = f"{m} k={k} escalas {'+'.join(f'{x:g}' for x in sc)}"
            ax[0].plot(*zip(*pts14), ls, marker="o", label=lab)
            ax[1].plot(*zip(*ptsg), ls, marker="o", label=lab)
    ax[0].set(xlabel=f"cobertura @{g3} px", ylabel=f"precisão @{g3} px", title="WC14 train_val")
    ax[1].set(xlabel=f"cobertura @{gc} px (pontos anotados)", ylabel=f"precisão @{gp} px", title="GSR train")
    for a in ax:
        a.grid(alpha=0.3); a.legend(fontsize=8)
    fig.tight_layout()
    out = path("outputs") / "figures" / "segment_pr_linhas.png"
    fig.savefig(out, dpi=110)
    print(out)


# ======================= avaliação da configuração do config =======================
def _eval_wc14_image(image_id):
    """WC14: IoU do gramado, sombra e cobertura/precisão das marcações (config)."""
    from src.evaluate import coverage_precision
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    img, H, size, P = s.image, s.H_gt, (s.grass.shape[1], s.grass.shape[0]), params("wc14")
    grass = grass_mask(img, P)
    lines = line_mask(img, grass, P)
    m = coverage_precision(lines, lines_target(H, size, region=s.grass), ES["wc14_gamma_px"], width_target=lines_mask(H, size))
    return dict(image_id=image_id, sombra=is_shadow(*shadow_score(img, s.grass)), iou=_iou(grass, s.grass), **m)


def _eval_gsr_clip(clip, step=None):
    """GSR, 1 frame a cada `step` (padrão `gsr_frame_step`): gramado no campo projetado,
    vazamento, cobertura dos pontos anotados (2 px) e precisão contra a linha com largura (3 px)."""
    from src.evaluate import coverage_precision, point_coverage
    cv2.setNumThreads(1)
    P, rows = params("gsr"), []
    for s in gsr.load_clip(clip)[::step or ES["gsr_frame_step"]]:
        if s.H_gt is None:
            continue
        img = s.image
        grass = grass_mask(img, P)
        lines = line_mask(img, grass, P)
        frac, leak = field_grass_and_leak(grass, s.H_gt, s.size)
        pts = gsr.inner_points(s.lines_uv, s.size)
        allp = np.concatenate(list(pts.values())) if pts else np.zeros((0, 2))
        prec = coverage_precision(lines, lines_mask(s.H_gt, s.size), [ES["gsr_precision_px"]],
                                  width_target=lines_mask(s.H_gt, s.size))[f"precisao@{ES['gsr_precision_px']}"]
        rows.append(dict(split=clip.parent.name, clip=clip.name, frame=s.frame_idx, campo_grama=frac, vazamento=leak,
                         cobertura=point_coverage(lines, allp, ES["gsr_coverage_px"]), n_pontos=len(allp), precisao=prec))
    return rows


def evaluate_final(pool, gsr_splits):
    """Métricas da configuração do config: WC14 train_val e GSR `gsr_splits`, com
    depuração (melhores, piores, sombra) em outputs/debug/segment/."""
    from src.run import _write_csv
    from src.segment import debug_overlay
    with pool() as ex:
        w = list(ex.map(_eval_wc14_image, wc14.split_ids("train_val")))
        g = [r for rs in ex.map(_eval_gsr_clip, [c for sp in gsr_splits for c in sorted((path("gsr") / sp).glob("SNGS-*"))]) for r in rs]
    _write_csv(path("outputs") / "segment_wc14.csv", w)
    _write_csv(path("outputs") / f"segment_gsr_{'+'.join(gsr_splits)}.csv", g)
    iou = np.array([r["iou"] for r in w]); sh = np.array([r["sombra"] for r in w])
    print(f"WC14 train_val: gramado IoU média {iou.mean():.4f} mediana {np.median(iou):.4f} sombra {iou[sh].mean():.4f} sem sombra {iou[~sh].mean():.4f}")
    for g_ in ES["wc14_gamma_px"]:
        c = np.nanmean([r[f"cobertura@{g_}"] for r in w]); p_ = np.nanmean([r[f"precisao@{g_}"] for r in w])
        print(f"   marcações a {g_} px: cobertura {c:.4f}  precisão {p_:.4f}  (média por imagem)")
    for key, lab in (("campo_grama", "campo projetado como grama"), ("vazamento", "vazamento"), ("cobertura", "cobertura a 2 px"), ("precisao", "precisão a 3 px")):
        v = np.array([r[key] for r in g], float)
        print(f"GSR {'+'.join(gsr_splits)} ({len(g)} frames): {lab}: média {np.nanmean(v):.4f} mediana {np.nanmedian(v):.4f}")
    out = path("debug") / "segment"
    out.mkdir(parents=True, exist_ok=True)
    order = np.argsort(iou)
    picks = [("pior", i) for i in order[:5]] + [("melhor", i) for i in order[-5:]] + [("sombra", i) for i in np.nonzero(sh)[0][:5]]
    for tag, i in picks:
        s = wc14.load_sample("train_val", w[i]["image_id"]); img, P = s.image, params("wc14")
        grass = grass_mask(img, P)
        cv2.imwrite(str(out / f"wc14_{tag}_{s.image_id}_iou{iou[i]:.3f}.jpg"), debug_overlay(img, grass, line_mask(img, grass, P)))
    print(out)
