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
def variants():
    """Variantes da escolha na GSR valid: a atual, as do config e a combinação."""
    V = ES["variants"]
    return {"atual": {}, **V, "+".join(V): {k: v for d in V.values() for k, v in d.items()}}


def _variant_masks(img, P, variants):
    """Gramado e marcações de cada variante; a resposta do filtro é uma só e o gramado,
    um por método."""
    resp, grasses, out = line_response(img, P), {}, {}
    for name, v in variants.items():
        Q = {**P, **v}
        if Q["grass_method"] not in grasses:
            grasses[Q["grass_method"]] = grass_mask(img, Q)
        g = grasses[Q["grass_method"]]
        out[name] = (g, line_mask(img, g, Q, response=resp))
    return out


def _eval_wc14_image(image_id, variants=None):
    """WC14: IoU do gramado, sombra e cobertura/precisão das marcações, por variante
    (padrão: só a do config)."""
    from src.evaluate import coverage_precision
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    img, H, size, P = s.image, s.H_gt, (s.grass.shape[1], s.grass.shape[0]), params("wc14")
    target, width = lines_target(H, size, region=s.grass), lines_mask(H, size)
    shadow = is_shadow(*shadow_score(img, s.grass))
    rows = []
    for name, (grass, lines) in _variant_masks(img, P, variants or {"config": {}}).items():
        m = coverage_precision(lines, target, ES["wc14_gamma_px"], width_target=width)
        rows.append(dict(variante=name, image_id=image_id, sombra=shadow, iou=_iou(grass, s.grass), **m))
    return rows


def _eval_gsr_clip(clip, step=None, variants=None):
    """GSR, 1 frame a cada `step` (padrão `gsr_frame_step`): gramado no campo projetado,
    vazamento, cobertura dos pontos anotados (2 px) e precisão contra a linha com largura
    (3 px), por variante (padrão: só a do config). Com variantes, salva a depuração do
    primeiro frame em outputs/debug/segment_variantes/."""
    from src.evaluate import coverage_precision, point_coverage
    from src.segment import debug_overlay
    cv2.setNumThreads(1)
    P, rows, game = params("gsr"), [], gsr.game_id(clip)
    gc, gp = ES["gsr_coverage_px"], ES["gsr_precision_px"]
    for s in gsr.load_clip(clip)[::step or ES["gsr_frame_step"]]:
        if s.H_gt is None:
            continue
        img = s.image
        pts = gsr.inner_points(s.lines_uv, s.size)
        allp = np.concatenate(list(pts.values())) if pts else np.zeros((0, 2))
        width = lines_mask(s.H_gt, s.size)
        field = {}
        for name, (grass, lines) in _variant_masks(img, P, variants or {"config": {}}).items():
            if id(grass) not in field:
                field[id(grass)] = field_grass_and_leak(grass, s.H_gt, s.size)
            frac, leak = field[id(grass)]
            prec = coverage_precision(lines, width, [gp], width_target=width)[f"precisao@{gp}"]
            rows.append(dict(variante=name, split=clip.parent.name, jogo=game, clip=clip.name, frame=s.frame_idx,
                             campo_grama=frac, vazamento=leak, cobertura=point_coverage(lines, allp, gc),
                             n_pontos=len(allp), precisao=prec))
            if variants and len(rows) <= len(variants):
                out = path("debug") / "segment_variantes"
                out.mkdir(parents=True, exist_ok=True)
                dbg = cv2.resize(debug_overlay(img, grass, lines), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                cv2.imwrite(str(out / f"{clip.parent.name}_jogo{game}_{clip.name}_{s.frame_idx}_{name}.jpg"), dbg)
    return rows


def evaluate_final(pool, gsr_splits):
    """Métricas da configuração do config: WC14 train_val e GSR `gsr_splits`, com
    depuração (melhores, piores, sombra) em outputs/debug/segment/."""
    from src.run import _write_csv
    from src.segment import debug_overlay
    with pool() as ex:
        w = [r for rs in ex.map(_eval_wc14_image, wc14.split_ids("train_val")) for r in rs]
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


def _means(rows, keys):
    return {k: float(np.nanmean([r[k] for r in rows])) for k in keys}


def evaluate_variants(pool, gsr_splits):
    """Rodada das variantes: WC14 train_val e GSR `gsr_splits`, por variante e por jogo.
    CSVs em outputs/segment_variantes_*.csv."""
    from src.run import _write_csv
    V = variants()
    clips = [c for sp in gsr_splits for c in sorted((path("gsr") / sp).glob("SNGS-*"))]
    with pool() as ex:
        w = [r for rs in ex.map(_eval_wc14_image, wc14.split_ids("train_val"), itertools.repeat(V)) for r in rs]
        g = [r for rs in ex.map(_eval_gsr_clip, clips, itertools.repeat(None), itertools.repeat(V)) for r in rs]
    _write_csv(path("outputs") / "segment_variantes_wc14.csv", w)
    _write_csv(path("outputs") / f"segment_variantes_gsr_{'+'.join(gsr_splits)}.csv", g)
    g3 = ES["decision_gamma_px"]
    print(f"WC14 train_val (média por imagem): IoU gramado / com sombra | marcações a {g3} px cobertura / precisão / F1")
    for name in V:
        rs = [r for r in w if r["variante"] == name]
        m = _means(rs, ["iou", f"cobertura@{g3}", f"precisao@{g3}"])
        sh = _means([r for r in rs if r["sombra"]], ["iou"])["iou"]
        c, p_ = m[f"cobertura@{g3}"], m[f"precisao@{g3}"]
        print(f"   {name:16} {m['iou']:.4f} / {sh:.4f} | {c:.4f} / {p_:.4f} / {2 * c * p_ / (c + p_):.4f}")
    keys = ["campo_grama", "vazamento", "cobertura", "precisao"]
    for sp in gsr_splits:
        games = sorted({r["jogo"] for r in g if r["split"] == sp}, key=int)
        print(f"GSR {sp} (média por frame): campo como grama / vazamento / cobertura a 2 px / precisão a 3 px / F1")
        for name in V:
            for gm in [*games, "todos"]:
                rs = [r for r in g if r["split"] == sp and r["variante"] == name and gm in (r["jogo"], "todos")]
                m = _means(rs, keys)
                c, p_ = m["cobertura"], m["precisao"]
                print(f"   {name:16} jogo {gm:5} ({len(rs):4d}) {m['campo_grama']:.4f} / {m['vazamento']:.4f} / {c:.4f} / {p_:.4f} / {2 * c * p_ / (c + p_):.4f}")


# ======================= calibração das variantes, só no treino =======================
def _kmeans_cfgs():
    G = W["kmeans"]
    return [dict(grass_method="kmeans", kmeans_k=k, kmeans_hue_deg=[lo, hi], kmeans_c_min=c)
            for k in G["kmeans_k"] for lo in G["hue_lo"] for hi in G["hue_hi"] for c in G["kmeans_c_min"]]


def _kmeans_masks(img, P, cfgs):
    """Gramado de cada configuração do k-means, mais o do config (primeiro da lista).
    O k-means roda uma vez por K e o pós-processamento uma vez por conjunto de grupos
    escolhidos. Devolve a chave de cada configuração e as máscaras por chave."""
    from src.segment import _post, green_centers, lab_clusters
    frame_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    clusters, masks, keys = {}, {"config": grass_mask(img, P)}, ["config"]
    for c in cfgs:
        Q = {**P, **c}
        k = c["kmeans_k"]
        if k not in clusters:
            clusters[k] = lab_clusters(frame_lab, Q)
        labels, centers = clusters[k]
        sel = green_centers(centers, Q)
        key = (k, tuple(sel))
        if key not in masks:
            masks[key] = _post(sel[labels], Q)
        keys.append(key)
    return keys, masks


def _hyst_cfgs():
    G = W["hysteresis"]
    return [dict(grass_method="hysteresis", hyst_dhue_deg=d, hyst_c_min=c) for d in G["hyst_dhue_deg"] for c in G["hyst_c_min"]]


FAMILIES = {  # família: (configurações, chave de "mais permissiva", colunas da tabela)
    "kmeans": (_kmeans_cfgs, lambda c: (c["kmeans_hue_deg"][1] - c["kmeans_hue_deg"][0], -c["kmeans_c_min"]),
               lambda c: dict(K=c["kmeans_k"], hue_lo=c["kmeans_hue_deg"][0], hue_hi=c["kmeans_hue_deg"][1], c_min=c["kmeans_c_min"])),
    "hysteresis": (_hyst_cfgs, lambda c: (c["hyst_dhue_deg"], -c["hyst_c_min"]),
                   lambda c: dict(dhue=c["hyst_dhue_deg"], c_min=c["hyst_c_min"])),
}


def _family_masks(img, P, family):
    """Gramado do config (primeiro) e de cada configuração da família."""
    if family == "kmeans":
        return _kmeans_masks(img, P, _kmeans_cfgs())
    cfgs = FAMILIES[family][0]()
    return ["config", *range(len(cfgs))], {"config": grass_mask(img, P), **{i: grass_mask(img, {**P, **c}) for i, c in enumerate(cfgs)}}


def _wc14_family(args):
    image_id, family = args
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    keys, masks = _family_masks(s.image, params("wc14"), family)
    iou = {k: _iou(m, s.grass) for k, m in masks.items()}
    return is_shadow(*shadow_score(s.image, s.grass)), [iou[k] for k in keys]


def _gsr_family(args):
    clip, family = args
    cv2.setNumThreads(1)
    out = []
    for s in gsr.load_clip(clip)[::ES["gsr_frame_step"]]:
        if s.H_gt is None:
            continue
        keys, masks = _family_masks(s.image, params("gsr"), family)
        fl = {k: field_grass_and_leak(m, s.H_gt, s.size) for k, m in masks.items()}
        out.append([fl[k] for k in keys])
    return out


def _disk(r):
    v, u = np.mgrid[-r:r + 1, -r:r + 1]
    return (u * u + v * v <= r * r).astype(np.uint8)


def _thresholds_of(resp, grass):
    """Limiares de cada (percentil, α) da grade, seguidos dos fixos da grade."""
    pct = np.percentile(resp[grass], W["line_pct"]) if grass.any() else np.full(len(W["line_pct"]), np.inf)
    return np.concatenate([np.outer(pct, W["line_alpha"]).ravel(), W["line_thr"]])


def _rel_counts(img, P, cover_at, gamma_cov, near):
    """Contagens somáveis das marcações, por limiar de `_thresholds_of`: [alvos
    cobertos, alvos, pixels preditos, preditos a <= γ da linha com largura].
    `cover_at` = índices (v, u) dos alvos da cobertura. Alvo coberto <=> máximo da
    resposta (dentro do gramado dilatado) num disco de raio γ acima do limiar; para
    γ <= 3 o disco é o mesmo da distância de _dist_to (chanfro 5x5)."""
    from src.segment import grass_grown
    grass = grass_mask(img, P)
    resp = line_response(img, P)
    r = np.where(grass_grown(grass, P), resp, -np.inf).astype(np.float32)
    cov_v = np.sort(cv2.dilate(r, _disk(gamma_cov))[cover_at])
    inside = np.isfinite(r)
    pred_v, near_v = np.sort(r[inside]), np.sort(r[inside & near])
    above = lambda v, t: len(v) - np.searchsorted(v, t, "right")
    return np.array([[above(cov_v, t), len(cov_v), above(pred_v, t), above(near_v, t)]
                     for t in _thresholds_of(resp, grass)], float)


def _wc14_rel(image_id):
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    size, g = (s.grass.shape[1], s.grass.shape[0]), ES["decision_gamma_px"]
    return _rel_counts(s.image, params("wc14"), np.nonzero(lines_target(s.H_gt, size, region=s.grass)), g,
                       _dist_to(lines_mask(s.H_gt, size)) <= g)


def _gsr_rel(clip):
    cv2.setNumThreads(1)
    tot = 0
    for s in gsr.load_clip(clip)[::ES["gsr_frame_step"]]:
        if s.H_gt is None:
            continue
        pts = gsr.inner_points(s.lines_uv, s.size)
        if not pts:
            continue
        p = np.concatenate(list(pts.values()))
        u = np.clip(np.round(p[:, 0]).astype(int), 0, s.size[0] - 1)
        v = np.clip(np.round(p[:, 1]).astype(int), 0, s.size[1] - 1)
        tot = tot + _rel_counts(s.image, params("gsr"), (v, u), ES["gsr_coverage_px"],
                                _dist_to(lines_mask(s.H_gt, s.size)) <= ES["gsr_precision_px"])
    return tot


def _f1(c):
    cov, prec = c[..., 0] / np.maximum(c[..., 1], 1), c[..., 3] / np.maximum(c[..., 2], 1)
    return cov, prec, 2 * cov * prec / np.maximum(cov + prec, 1e-9)


def _calib_grass(ex, family, ids, clips):
    """Gramado da `family` no treino. Passa quem fica no ruído do atual em tudo: IoU
    do WC14 (média e sombra) e campo como grama e vazamento no GSR train. Das que
    passam, fica a mais permissiva (docs/decisoes.md)."""
    from src.run import _write_csv
    cfgs, permissive, cols = FAMILIES[family]
    cfgs = cfgs()
    k14 = list(ex.map(_wc14_family, [(i, family) for i in ids]))
    kg = [f for fs in ex.map(_gsr_family, [(c, family) for c in clips]) for f in fs]
    sh = np.array([x[0] for x in k14])
    iou = np.array([x[1] for x in k14])                      # imagens x (config + cfgs)
    fl = np.array(kg)                                        # frames x (config + cfgs) x (campo, vazamento)
    summ = lambda j: dict(wc14_iou=iou[:, j].mean(), wc14_sombra=iou[sh, j].mean(),
                          gsr_campo=np.nanmean(fl[:, j, 0]), gsr_vazamento=np.nanmean(fl[:, j, 1]))
    ref = summ(0)
    rows = [dict(**cols(c), **summ(j + 1)) for j, c in enumerate(cfgs)]
    _write_csv(path("outputs") / f"segment_variantes_{family}.csv",
               [{k: round(float(v), 4) if isinstance(v, (float, np.floating)) else v for k, v in r.items()} for r in rows])
    n = W["noise_grass"]
    ok = [j for j, r in enumerate(rows) if r["wc14_iou"] >= ref["wc14_iou"] - n and r["wc14_sombra"] >= ref["wc14_sombra"] - n
          and r["gsr_campo"] >= ref["gsr_campo"] - n and r["gsr_vazamento"] <= ref["gsr_vazamento"] + n]
    pick = max(ok, key=lambda j: permissive(cfgs[j]), default=None)
    f4 = lambda r: f"WC14 IoU {r['wc14_iou']:.4f} sombra {r['wc14_sombra']:.4f} | GSR campo {r['gsr_campo']:.4f} vazamento {r['gsr_vazamento']:.4f}"
    print(f"== Gramado {family}, treino. Atual (config): {f4(ref)}")
    print(f"   passam (no ruído {n} do atual nas quatro): {len(ok)} de {len(rows)}; escolhida: {rows[pick] if pick is not None else 'nenhuma'}")
    for j in sorted(range(len(rows)), key=lambda j: -rows[j]["wc14_iou"])[:24]:
        r = rows[j]
        print("   " + " ".join(f"{k}={r[k]}" for k in cols(cfgs[j])) + f"  {f4(r)}" + ("  passa" if j in ok else "") + ("  <- escolhida" if j == pick else ""))
    return cfgs[pick] if pick is not None else None


def _calib_alpha(ex, ids, clips):
    """Limiar relativo: máximo do F1 médio das duas bases no treino."""
    from src.run import _write_csv
    r14 = sum(ex.map(_wc14_rel, ids))
    rg = sum(ex.map(_gsr_rel, clips))
    npct, nal = len(W["line_pct"]), len(W["line_alpha"])
    c14, cg = r14[:npct * nal].reshape(npct, nal, 4), rg[:npct * nal].reshape(npct, nal, 4)
    f14, fg = _f1(c14)[2], _f1(cg)[2]
    obj = (f14 + fg) / 2
    i, j = np.unravel_index(np.argmax(obj), obj.shape)
    _write_csv(path("outputs") / "segment_variantes_alfa.csv",
               [dict(pct=p_, alpha=a, wc14_F1=round(float(f14[a_i, b_i]), 4), gsr_F1=round(float(fg[a_i, b_i]), 4), media=round(float(obj[a_i, b_i]), 4))
                for a_i, p_ in enumerate(W["line_pct"]) for b_i, a in enumerate(W["line_alpha"])])
    print("\n== Marcações, limiar relativo, treino: F1 médio das duas bases (WC14 cob@3 x prec@3; GSR cob@2 x prec@3)")
    print("   percentil  " + "  ".join(f"{a:5}" for a in W["line_alpha"]))
    for a_i, p_ in enumerate(W["line_pct"]):
        print(f"   {p_:9}  " + "  ".join(f"{x:.3f}" for x in obj[a_i]))
    cw, cgg = _f1(c14[i, j]), _f1(cg[i, j])
    print(f"   escolhido: percentil {W['line_pct'][i]}, α {W['line_alpha'][j]}: WC14 cob {cw[0]:.3f} prec {cw[1]:.3f} F1 {cw[2]:.3f} | GSR cob {cgg[0]:.3f} prec {cgg[1]:.3f} F1 {cgg[2]:.3f}")
    fx14, fxg = r14[npct * nal:], rg[npct * nal:]
    for base, fx, thr in (("WC14", fx14, params("wc14")["line_thr"]), ("GSR", fxg, params("gsr")["line_thr"])):
        c, p_, f = _f1(fx[W["line_thr"].index(thr)])
        print(f"   limiar fixo {base} {thr}: cob {c:.3f} prec {p_:.3f} F1 {f:.3f}")


def calibrate_variants(pool, parts):
    """Calibra no treino (WC14 train_val + GSR train) as variantes em `parts`
    ("kmeans", "hysteresis", "alpha") e imprime as tabelas; regras em docs/decisoes.md."""
    ids, clips = wc14.split_ids("train_val"), sorted((path("gsr") / "train").glob("SNGS-*"))
    with pool() as ex:
        for part in parts:
            if part == "alpha":
                _calib_alpha(ex, ids, clips)
            else:
                _calib_grass(ex, part, ids, clips)
