"""Fatia 7d: sensibilidade descritiva dos parâmetros — um de cada vez, com os passos
relativos de `sensitivity.steps` — sem recalibrar nada (decisoes.md, 2026-09-30).
Detector nos subconjuntos da regressão (GSR: 60 frames; WC14: train_val[::6]); 6c com
fluxo no subconjunto de 6 clipes do treino. O 6a (Hampel) e o Kalman já têm as
tabelas das grades de calibração. Mais a auditoria da origem das constantes do config.
"""
import hashlib
import inspect
import json
import os
import pickle
import re

import cv2
import numpy as np

from src.config import CFG, ROOT, path

SENS = CFG["sensitivity"]
# código e config lidos UMA vez, na importação: chave do checkpoint por tarefa do 6c
_CODE = hashlib.sha1(b"".join(p.read_bytes() for p in sorted((ROOT / "src").rglob("*.py"))) + (ROOT / "config.yaml").read_bytes()).hexdigest()


def _get(p):
    d = CFG
    for k in p.split("."):
        d = d[k]
    return d


def _set(p, v):
    *head, last = p.split(".")
    d = CFG
    for k in head:
        d = d[k]
    d[last] = v


def perturbed(p, step):
    """Valor do parâmetro `p` com o passo relativo `step`: inteiros arredondados (e ao
    menos ±1), frações limitadas a (0, 1] onde `sensitivity.bounded` diz, listas escaladas."""
    v = _get(p)
    if isinstance(v, list):
        return [x * (1 + step) for x in v]
    if isinstance(v, int):
        n = max(1, int(round(v * (1 + step))))
        return n if n != v else max(1, v + (1 if step > 0 else -1))
    x = v * (1 + step)
    return min(x, 1.0) if p in SENS["bounded"] else x


# lidos só na importação (valores derivados congelados no módulo): trocar no CFG não chega ao
# código; temporal.grid_m é a exceção tratada em _with (auditoria, decisoes.md, 2026-10-01)
_IMPORT_TIME = ("assign.score_step_m", "pitch.", "eval.", "eval_segment.", "render.", "visibility.", "gsr.")


def _check_reaches(p):
    """A troca de p tem que chegar ao que o código lê: recusa parâmetro sombreado por uma
    variante do detector (detect_frame mescla a variante por cima de segment/lines) e
    parâmetro lido só na importação."""
    sec, key = p.split(".")[0], p.split(".")[-1]
    for name, v in CFG["detector"]["variants"].items():
        if sec in ("segment", "lines") and key in v.get(sec, {}):
            raise ValueError(f"{p} é sombreado pela variante {name} do detector: perturbe detector.variants.{name}.{sec}.{key}")
    if p.startswith(_IMPORT_TIME):
        raise ValueError(f"{p} é lido só na importação: trocar no CFG não chega ao código")


def _with(p, value, fn):
    """Roda fn() com o parâmetro p trocado por value, no CFG deste processo, e restaura."""
    from src import temporal
    _check_reaches(p)
    old = _get(p)
    _set(p, value)
    if p == "temporal.grid_m":                     # derivada no import
        temporal.GRID = np.stack(np.meshgrid(np.arange(-52.5, 52.51, value[0]), np.arange(-34, 34.01, value[1])), -1).reshape(-1, 2)
    try:
        return fn()
    finally:
        _set(p, old)
        if p == "temporal.grid_m":
            temporal.GRID = np.stack(np.meshgrid(np.arange(-52.5, 52.51, old[0]), np.arange(-34, 34.01, old[1])), -1).reshape(-1, 2)


def _detector_samples(dataset):
    """Subconjunto da regressão, com o gabarito. Carregado FORA da perturbação: fit.* entra
    na chave e no aceite da H de gabarito do GSR, e o gabarito não pode mudar com o
    parâmetro medido (decisoes.md, 2026-10-01)."""
    from src.io import gsr, wc14
    if dataset == "gsr":
        return [s for c in sorted((path("gsr") / "train").glob("SNGS-*"))[::10] for s in gsr.load_clip(c)[::75] if s.H_gt is not None]
    return [wc14.load_sample("train_val", i) for i in wc14.split_ids("train_val")[::6]]


def _detector_metrics(dataset, samples):
    """Cobertura, IoU_whole e NPE medianos e LocSim@5 penalizado (só GSR) do detector nas
    amostras do subconjunto da regressão."""
    from src.assign import detect_frame
    from src.evaluate import frame_metrics, summarize
    rows = []
    for s in samples:
        H = next(iter(detect_frame(s.image, dataset).values()))[0]
        rows.append(dict(**frame_metrics(H, s), n_pessoas=0 if getattr(s, "persons_XY", None) is None else len(s.persons_XY)))
    t = summarize(rows)["todos"]
    return dict(cobertura=t["cobertura"], iou=t["iou_whole"][1], npe=t["npe"][1], locsim=t.get("locsim@5 penalizado", np.nan))


def _detector_task(args):
    p, step, dataset = args
    cv2.setNumThreads(1)
    samples = _detector_samples(dataset)
    if p is None:
        return args, _detector_metrics(dataset, samples)
    return args, _with(p, perturbed(p, step), lambda: _detector_metrics(dataset, samples))


def _flow_metrics(clip, samples):
    """Só a variante 6c com fluxo num clipe (âncoras verificadas, propagação): métricas.
    `samples` (com o gabarito) vêm de fora da perturbação."""
    from src import temporal as T
    from src.evaluate import frame_metrics
    ser = dict(np.load(T._series_path(clip)))
    cf, seg = T.ClipFrames(samples), np.zeros(len(samples), int)
    anc, _, _ = T.anchors(ser, cf, seg)
    Hs = T.fill_from_anchors(cf, anc, ser["H"], seg, "flow")
    return [dict(**frame_metrics(H if np.isfinite(H).all() else None, s),
                 n_pessoas=0 if s.persons_XY is None else len(s.persons_XY)) for s, H in zip(samples, Hs)]


def _temporal_task(args):
    """Uma tarefa do 6c (parâmetro, passo, clipe), com checkpoint em
    outputs/cache/sensitivity/: a rodada interrompida retoma das tarefas que faltam."""
    p, step, clip = args
    cv2.setNumThreads(1)
    f = path("outputs") / "cache" / "sensitivity" / f"{(p or 'base').replace('.', '_')}_{step:+.2f}_{clip.name}.pkl"
    if f.exists():
        k, rows = pickle.loads(f.read_bytes())
        if k == _CODE:
            return args, rows
    from src.io import gsr
    samples = gsr.load_clip(clip)                    # gabarito fora da perturbação
    rows = _flow_metrics(clip, samples) if p is None else _with(p, perturbed(p, step), lambda: _flow_metrics(clip, samples))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(pickle.dumps((_CODE, rows)))
    return args, rows


_NUM = ("passo", "cobertura", "npe", "locsim", "iou")      # colunas numéricas dos CSVs da sensibilidade


def _tornado(rows, metric, title, out, res=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    params = sorted({r["parametro"] for r in rows}, key=lambda p: max(abs(r[metric]) for r in rows if r["parametro"] == p))
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(params) + 1.2))
    for step, color in zip(sorted(SENS["steps"]), ("#1f4e79", "#6fa8dc", "#f6b26b", "#b45f06")):
        vals = [next((r[metric] for r in rows if r["parametro"] == p and r["passo"] == step), 0.0) for p in params]
        ax.barh(np.arange(len(params)) + 0.2 * (sorted(SENS["steps"]).index(step) - 1.5), vals, 0.2, color=color, label=f"{step:+.0%}")
    ax.set_yticks(np.arange(len(params)), params, fontsize=8)
    ax.axvline(0, color="k", lw=0.8)
    for x in (-SENS["matters"], SENS["matters"]):
        ax.axvline(x, color="gray", ls=":", lw=0.8)
    if res:                                         # faixa "indistinguível": |Δ| < fator × resolução
        ax.axvspan(-res, res, color="gray", alpha=0.15, lw=0, label=f"indistinguível (|Δ| < {res:.3f})")
    ax.set_xlabel(f"Δ {metric} contra o config atual")
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)


def _table(results, base, metrics, key):
    rows = []
    for (p, step, _), m in results:
        if p is not None:
            rows.append(dict(parametro=p, passo=step, valor=perturbed(p, step), **{k: m[k] - base[k] for k in metrics}))
    print(f"{'parâmetro':42} {'passo':>6} " + " ".join(f"{'Δ ' + k:>11}" for k in metrics) + "  importa?")
    for p in dict.fromkeys(r["parametro"] for r in rows):
        rs = [r for r in rows if r["parametro"] == p]
        big = max(abs(r[k]) for r in rs for k in key) >= SENS["matters"]
        for r in rs:
            print(f"{p:42} {r['passo']:>+6.0%} " + " ".join(f"{r[k]:>+11.4f}" for k in metrics) + ("  SIM" if big else ""))
    return rows


def run_detector(pool, params=None):
    """Sensibilidade do detector: tabela, CSV e tornados (GSR: LocSim@5; WC14: IoU). Com
    `params`, refaz só esses (e o atual) e mantém do CSV os outros que seguem na lista."""
    import csv
    from src.run import _write_csv
    params = params or SENS["detector"]
    tasks = [(None, 0.0, d) for d in ("gsr", "wc14")] + \
            [(p, s, d) for p in params for s in SENS["steps"] for d in ("gsr", "wc14")]
    with pool() as ex:
        res = [r for r in ex.map(_detector_task, tasks) if r is not None]
    assert len(res) == len(tasks), f"{len(tasks) - len(res)} tarefas sem resultado (ver o manifesto); nada foi agregado"
    out = {}
    for d, metrics, key in (("gsr", ("cobertura", "npe", "locsim"), ("cobertura", "locsim")),
                            ("wc14", ("cobertura", "iou", "npe"), ("cobertura", "iou"))):
        base = next(m for (p, _, dd), m in res if p is None and dd == d)
        print(f"\n== detector, {d.upper()} (config atual: " + ", ".join(f"{k} {base[k]:.4f}" for k in metrics) + ")")
        rows = _table([r for r in res if r[0][2] == d], base, metrics, key)
        out_csv = path("outputs") / f"sensibilidade_detector_{d}.csv"
        if params != SENS["detector"]:              # os outros ficam como estavam (mesmo atual)
            keep = [{k: (float(v) if k in _NUM else v) for k, v in r.items()} for r in csv.DictReader(out_csv.open(encoding="utf-8"))
                    if r["parametro"] in SENS["detector"] and r["parametro"] not in params]
            rows = sorted(keep + rows, key=lambda r: (SENS["detector"].index(r["parametro"]), r["passo"]))
        _write_csv(out_csv, rows)
        _tornado(rows, key[-1], f"Sensibilidade do detector ({d.upper()}, um parâmetro de cada vez)",
                 path("outputs") / "figures" / f"sensibilidade_detector_{d}.png")
        out[d] = rows
    return out


def run_temporal(pool, clips, params=None):
    """Sensibilidade do 6c com fluxo no subconjunto: tabela, CSV e tornado (LocSim@5).
    Com `params`, refaz só esses (e o atual) e mantém os outros do CSV existente."""
    import csv
    from src.evaluate import summarize
    from src.run import _write_csv
    params = params or SENS["temporal"]
    tasks = [(None, 0.0, c) for c in clips] + [(p, s, c) for p in params for s in SENS["steps"] for c in clips]
    with pool() as ex:
        res = [r for r in ex.map(_temporal_task, tasks) if r is not None]
    assert len(res) == len(tasks), f"{len(tasks) - len(res)} tarefas sem resultado (ver o manifesto); nada foi agregado"

    def agg(p, step):
        t = summarize([r for (pp, ss, _), rows in res if pp == p and ss == step for r in rows])["todos"]
        return dict(cobertura=t["cobertura"], npe=t["npe"][1], locsim=t.get("locsim@5 penalizado", np.nan))
    base = agg(None, 0.0)
    merged = [((p, s, None), agg(p, s)) for p in params for s in SENS["steps"]]
    print(f"\n== 6c com fluxo, {len(clips)} clipes (config atual: " + ", ".join(f"{k} {v:.4f}" for k, v in base.items()) + ")")
    rows = _table(merged, base, ("cobertura", "npe", "locsim"), ("cobertura", "locsim"))
    out = path("outputs") / "sensibilidade_6c.csv"
    if params != SENS["temporal"]:                  # os outros parâmetros ficam como estavam (mesmo atual)
        keep = [{k: (float(v) if k in _NUM else v) for k, v in r.items()}
                for r in csv.DictReader(out.open(encoding="utf-8")) if r["parametro"] not in params]
        rows = sorted(keep + rows, key=lambda r: (SENS["temporal"].index(r["parametro"]), r["passo"]))
    _write_csv(out, rows)
    _tornado(rows, "locsim", "Sensibilidade do 6c com fluxo (subconjunto, um parâmetro de cada vez)",
             path("outputs") / "figures" / "sensibilidade_6c.png")
    return rows


def audit():
    """Constantes numéricas das seções do pipeline e a origem que o comentário declara:
    fonte (artigo, norma, decisão), calibrado (varredura/grade no treino) ou escolha."""
    from src.run import _write_csv
    rows, sec, sub = [], None, None
    for line in (ROOT / "config.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\w+):", line)
        if m:
            sec, sub = m.group(1), None
            continue
        m = re.match(r"^  (\w+):\s*(#.*)?$", line)
        if m:
            sub = m.group(1)
            continue
        m = re.match(r"^(\s+)(\w+):\s*([-\d.eE+]+)\s*(#.*)?$", line)
        if not m or sec not in SENS["audit_sections"]:
            continue
        ind, key, _, com = m.groups()
        p = f"{sec}.{sub}.{key}" if len(ind) == 4 and sub else f"{sec}.{key}"
        c = (com or "").lower()
        tag = "escolha" if "escolha" in c else "calibrado" if re.search(r"calibr|empíric|varredura|escolhid", c) else "fonte" if c else "sem comentário"
        rows.append(dict(parametro=p, origem=tag, na_sensibilidade=p in SENS["detector"] + SENS["temporal"], comentario=(com or "")[2:]))
    _write_csv(path("outputs") / "auditoria_config.csv", rows)
    for tag in ("fonte", "calibrado", "escolha", "sem comentário"):
        rs = [r for r in rows if r["origem"] == tag]
        print(f"{tag:15} {len(rs):3}  (na sensibilidade: {sum(r['na_sensibilidade'] for r in rs)})")
    return rows


# ============ confirmação dos candidatos (decisão de Victor, 2026-10-01) ============
# Regra em docs/decisoes.md: lista fechada, subconjunto maior, Δ com intervalo por bootstrap
# pareado, critério fixado antes de rodar. Checkpoint por tarefa em outputs/cache/confirm/,
# com a chave _CODE_CONF (fim do módulo) e, no nome do arquivo, o candidato, a unidade e
# a parte da seção `confirm` que define a amostra.
CONF = SENS["confirm"]


def _with_many(pairs, fn):
    """fn() com vários parâmetros trocados ([(p, valor), ...]), aninhando _with."""
    if not pairs:
        return fn()
    (p, v), rest = pairs[0], pairs[1:]
    return _with(p, v, lambda: _with_many(rest, fn))


def _label(steps):
    return " + ".join(f"{p} {s:+.0%}" for p, s in steps) or "atual"


def _load(kind, unit):
    """Amostras da unidade, com o gabarito, carregadas FORA da perturbação (o gabarito não
    muda com o parâmetro medido): (posição, Sample) do GSR train (1 a cada
    `gsr_frame_step`, os com H_gt, como na regressão), do bloco do WC14 ou do clipe do 6c."""
    from src.io import gsr, wc14
    if kind == "wc14":
        ids = wc14.split_ids(CONF["wc14_split"])
        k = CONF["wc14_chunk"]
        return [(j, wc14.load_sample(CONF["wc14_split"], ids[j])) for j in range(unit * k, min((unit + 1) * k, len(ids)))]
    samples = gsr.load_clip(path("gsr") / "train" / unit)
    if kind == "6c":
        return samples
    step = CONF["gsr_frame_step"]
    return [(i * step, s) for i, s in enumerate(samples[::step]) if s.H_gt is not None]


def _rows_detector(unit, samples, dataset):
    """Detector nas amostras (GSR ou WC14): linhas de frame_metrics, com a posição."""
    from src.assign import detect_frame
    from src.evaluate import frame_metrics
    out = []
    for pos, s in samples:
        H = next(iter(detect_frame(s.image, dataset).values()))[0]
        out.append(dict(**frame_metrics(H, s), unidade=s.image_id if dataset == "wc14" else unit, pos=pos,
                        n_pessoas=0 if getattr(s, "persons_XY", None) is None else len(s.persons_XY)))
    return out


def _rows_6c(clip, samples):
    """Só o "6c fluxo" de temporal._eval_clip_6c (mesmos cortes, âncoras e preenchimento;
    copiado para não mexer no temporal.py, cuja chave guarda os caches do 6c): linhas por
    frame, âncoras (candidatas, verificáveis, aceitas) e as H (float32). A rodada do config
    atual confere as H com as do cache da produção, frame a frame."""
    from src import temporal as TM
    from src.evaluate import frame_metrics
    ser = dict(np.load(TM._series_path(path("gsr") / "train" / clip)))
    cf, n = TM.ClipFrames(samples), len(samples)
    hists = [TM.frame_hist(s.image) for s in samples]
    cut = np.r_[False, [TM.hist_distance(hists[i], hists[i + 1]) > TM.T["cut_thr"] for i in range(n - 1)]]
    seg = np.cumsum(cut)
    anc, cand, verifiable = TM.anchors(ser, cf, seg)
    Hs = TM.fill_from_anchors(cf, anc, ser["H"], seg, "flow")
    rows = [dict(**frame_metrics(H if np.isfinite(H).all() else None, s), unidade=clip, pos=i,
                 n_pessoas=0 if s.persons_XY is None else len(s.persons_XY)) for i, (s, H) in enumerate(zip(samples, Hs))]
    return dict(rows=rows, aceitas=[int(t) for t in anc], verificaveis=[int(t) for t in verifiable],
                candidatas=[int(t) for t in cand], H=Hs.astype(np.float32))


def _ckpt(steps, kind, unit):
    sample = (CONF["gsr_frame_step"], CONF["wc14_split"], CONF["wc14_chunk"])
    return path("outputs") / "cache" / "confirm" / f"{kind}_{hashlib.sha1(repr((steps, unit, sample)).encode()).hexdigest()[:16]}.pkl"


def _units(part):
    """Unidades de cada base: clipes do GSR train, blocos do WC14, clipes do train[::3]."""
    from src.io import wc14
    if part == "detector":
        return {"gsr": [c.name for c in sorted((path("gsr") / "train").glob("SNGS-*"))],
                "wc14": list(range(-(-len(wc14.split_ids(CONF["wc14_split"])) // CONF["wc14_chunk"])))}
    return {"6c": [c.name for c in sorted((path("gsr") / "train").glob("SNGS-*"))[::3]]}


def _confirm_task(args):
    """Uma tarefa: (passos, base, unidade) -> resultado, com checkpoint (retomável)."""
    steps, kind, unit = args
    cv2.setNumThreads(1)
    f = _ckpt(steps, kind, unit)
    if f.exists():
        k, res = pickle.loads(f.read_bytes())
        if k == _CODE_CONF:
            return args, res
    samples = _load(kind, unit)                     # gabarito fora da perturbação
    run = (lambda: _rows_6c(unit, samples)) if kind == "6c" else (lambda: _rows_detector(unit, samples, kind))
    res = _with_many([(p, perturbed(p, s)) for p, s in steps], run)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.name + ".tmp")
    tmp.write_bytes(pickle.dumps((_CODE_CONF, res)))
    os.replace(tmp, f)
    return args, res


def _arrays(rows):
    """Por frame/imagem: com H_gt, com H, soma do LocSim@5 das pessoas, nº de pessoas,
    NPE e IoU_whole (NaN sem H); hasd: frame com distâncias do LocSim (com H e pessoas)."""
    from src.evaluate import locsim
    g = lambda k: np.array([r.get(k, np.nan) for r in rows], float)
    return dict(gt=np.array([r["has_gt"] for r in rows], bool), pred=np.array([r["has_pred"] for r in rows], bool),
                ls5=np.array([locsim(r["locsim_d"], 5).sum() if "locsim_d" in r else 0.0 for r in rows]),
                hasd=np.array(["locsim_d" in r for r in rows], bool),
                npers=np.array([r["n_pessoas"] for r in rows], float), npe=g("npe"), iou=g("iou_whole"))


def _metric(a, m, ix=None):
    """Métricas da regressão (as de evaluate.summarize, "todos") sobre as linhas ix:
    cobertura, LocSim@5 penalizado e as medianas de NPE e IoU_whole nos frames com H."""
    a = a if ix is None else {k: v[ix] for k, v in a.items()}
    if m == "cobertura":
        return (a["gt"] & a["pred"]).sum() / a["gt"].sum()
    if m == "locsim":
        return a["ls5"].sum() / a["npers"].sum() if a["npers"].sum() and a["hasd"].any() else np.nan     # como summarize
    v = a[m][a["gt"] & a["pred"]]
    return np.nanmedian(v) if np.isfinite(v).any() else np.nan


def bootstrap_delta(base, cand, units, metrics, n_boot, seed, ci):
    """Δ = métrica(candidato) − métrica(atual) e o intervalo de `ci` por bootstrap pareado:
    sorteia as unidades (clipes ou imagens) com reposição, as mesmas para os dois.
    base/cand: _arrays alinhados (mesmas linhas, mesma ordem); units: unidade de cada linha.
    Devolve {métrica: (Δ, limite inferior, limite superior)}."""
    _, inv = np.unique(np.asarray(units, dtype=str), return_inverse=True)
    groups = [np.nonzero(inv == u)[0] for u in range(inv.max() + 1)]
    draws = np.random.default_rng(seed).integers(0, len(groups), (n_boot, len(groups)))
    ixs = [np.concatenate([groups[j] for j in dr]) for dr in draws]
    out = {}
    for m in metrics:
        bs = np.array([_metric(cand, m, ix) - _metric(base, m, ix) for ix in ixs])
        lo, hi = np.nanpercentile(bs, [100 * (1 - ci) / 2, 100 * (1 + ci) / 2])
        out[m] = (float(_metric(cand, m) - _metric(base, m)), float(lo), float(hi))
    return out


def run_confirm(pool, part):
    """Confirmação dos candidatos (`part`: detector ou 6c): mede o atual, cada candidato e
    as combinações de `confirm.combos`; aplica o critério; grava as tabelas."""
    from src.evaluate import summarize
    from src.run import _write_csv
    B = dict(n_boot=CONF["n_boot"], seed=CONF["seed"], ci=CONF["ci"])
    units = _units(part)
    kinds = tuple(units)
    if part == "detector":
        cands = [((), None)] + [(((p, s),), kind) for p, s, kind in CONF["detector"]] + \
                [(tuple((p, s) for p, s in steps), kind) for kind, steps in CONF["combos"] if kind in kinds]
    else:
        cands = [((), None)] + [(((p, s),), "6c") for p, s in CONF["temporal"]] + \
                [(tuple((p, s) for p, s in steps), kind) for kind, steps in CONF["combos"] if kind == "6c"]
    tasks = [(steps, k, u) for steps, _ in cands for k in kinds for u in units[k]]
    with pool() as ex:
        res = {a: r for a, r in (x for x in ex.map(_confirm_task, tasks) if x is not None)}
    missing = [t for t in tasks if t not in res]
    assert not missing, f"{len(missing)} tarefas sem resultado (ver o manifesto); nada foi avaliado"

    def collect(steps, k):
        rows = [r for u in units[k] for r in (res[(steps, k, u)]["rows"] if k == "6c" else res[(steps, k, u)])]
        return sorted(rows, key=lambda r: (str(r["unidade"]), r["pos"]))
    base = {k: collect((), k) for k in kinds}
    for k in kinds:                                         # a fórmula do bootstrap = summarize
        t, a = summarize(base[k])["todos"], _arrays(base[k])
        for m, ref in (("cobertura", t["cobertura"]), ("locsim", t.get("locsim@5 penalizado", np.nan)), ("npe", t["npe"][1]), ("iou", t["iou_whole"][1])):
            assert np.isclose(_metric(a, m), ref, equal_nan=True), (k, m, _metric(a, m), ref)
    if part == "6c":
        from src import temporal as TM
        for c in units["6c"]:                               # o atual reproduz o cache da produção
            cached = pickle.loads(TM._eval_6c_path(path("gsr") / "train" / c).read_bytes())[1][3]["6c fluxo"]
            assert np.array_equal(res[((), "6c", c)]["H"], cached, equal_nan=True), f"{c}: o 6c fluxo do atual difere do cache"
        print(f"6c: o atual reproduz o cache da produção, H a H, nos {len(units['6c'])} clipes")
    rows_out, anc_out = [], []
    for steps, kind in cands:
        row = dict(candidato=_label(steps), base_do_ganho=kind or "")
        for k in kinds:
            rc = collect(steps, k)
            assert [(r["unidade"], r["pos"]) for r in rc] == [(r["unidade"], r["pos"]) for r in base[k]]
            a, b = _arrays(base[k]), _arrays(rc)
            ms = ("iou", "cobertura", "npe") if k == "wc14" else ("locsim", "cobertura", "npe")
            for m in ms:
                row[f"{k}_{m}"] = _metric(b, m)
            if steps:
                for m, (d, lo, hi) in bootstrap_delta(a, b, [r["unidade"] for r in base[k]], ms, **B).items():
                    row[f"{k}_d_{m}"], row[f"{k}_lo_{m}"], row[f"{k}_hi_{m}"] = d, lo, hi
        if steps:
            mg, ml = CONF["min_gain"], CONF["max_loss"]
            if kind == "gsr":
                row["passa"] = row["gsr_d_locsim"] >= mg and row["gsr_lo_locsim"] > 0 and row["wc14_d_iou"] >= -ml
            elif kind == "wc14":
                row["passa"] = row["wc14_d_iou"] >= mg and row["wc14_lo_iou"] > 0 and row["gsr_d_locsim"] >= -ml
            else:
                row["passa"] = row["6c_d_locsim"] >= mg and row["6c_lo_locsim"] > 0
                for c in units["6c"]:                       # âncoras que mudaram, por clipe
                    b0, b1 = res[((), "6c", c)], res[(steps, "6c", c)]
                    ls = lambda r: _metric(_arrays(r["rows"]), "locsim")
                    anc_out.append(dict(candidato=row["candidato"], clipe=c, d_locsim_clipe=ls(b1) - ls(b0),
                                        aceitas_atual=len(b0["aceitas"]), aceitas_candidato=len(b1["aceitas"]),
                                        entraram=" ".join(map(str, sorted(set(b1["aceitas"]) - set(b0["aceitas"])))),
                                        sairam=" ".join(map(str, sorted(set(b0["aceitas"]) - set(b1["aceitas"]))))))
        rows_out.append(row)
    print(f"\n== confirmação ({part}): " + ", ".join(f"{k}: {len(base[k])} linhas em {len(units[k])} unidades" for k in kinds))
    for r in rows_out:
        print(r["candidato"][:50].ljust(50), "  ".join(f"{k} {v:+.4f}" for k, v in r.items() if "_d_" in k), "" if "passa" not in r else ("PASSA" if r["passa"] else "não passa"))
    _write_csv(path("outputs") / f"confirmacao_{part}.csv", rows_out)
    if anc_out:
        _write_csv(path("outputs") / "confirmacao_6c_ancoras.csv", anc_out)
    return rows_out, anc_out


def _resolution(v, kind):
    """O valor de um frame/imagem numa métrica: média ou proporção sobre N unidades -> 1/N;
    mediana -> quanto uma unidade a mais, acima ou abaixo, desloca a mediana."""
    if kind == "proporcao":
        return 1 / len(v)
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    m = np.median(v)
    return max(abs(np.median(np.r_[v, np.inf]) - m), abs(np.median(np.r_[v, -np.inf]) - m))


def importa_table():
    """Tabela "importa / não importa" revisada (decisão de Victor, 2026-10-01): a resolução
    de cada métrica-chave nos subconjuntos da sensibilidade (um frame ou uma imagem) e
    |Δ| < `resolution_factor`× ela marcado como "indistinguível"; tornados com a faixa.
    Os valores por frame do config atual vêm da confirmação (os subconjuntos da regressão
    estão dentro dos dela: clipes [::10] e frames [::75] do GSR; train_val[::6] do WC14)."""
    import csv
    from src.io import gsr
    from src.run import _write_csv
    f = CONF["resolution_factor"]

    def pick(kind, unit):                                   # o config atual, da confirmação
        k, r = pickle.loads(_ckpt((), kind, unit).read_bytes())
        assert k == _CODE_CONF, f"checkpoint da confirmação de outro código ({kind} {unit}): rode --confirm detector"
        return r
    clips10 = [c.name for c in sorted((path("gsr") / "train").glob("SNGS-*"))[::10]]
    g = [r for c in clips10 for r in pick("gsr", c) if r["pos"] % 75 == 0]
    w = [r for k in _units("detector")["wc14"] for r in pick("wc14", k) if r["pos"] % 6 == 0]
    assert len(g) == 60 and len(w) == 35, (len(g), len(w))
    s6 = [s for c in CFG["temporal"]["subset_clips"] for s in gsr.load_clip(path("gsr") / "train" / c)]
    res = {"gsr": dict(cobertura=_resolution([r for r in g if r["has_gt"]], "proporcao"),
                       locsim=_resolution([r for r in g if r["n_pessoas"]], "proporcao")),
           "wc14": dict(cobertura=_resolution([r for r in w if r["has_gt"]], "proporcao"),
                        iou=_resolution([r["iou_whole"] for r in w if r["has_pred"] and r["has_gt"]], "mediana")),
           "6c": dict(cobertura=_resolution([s for s in s6 if s.H_gt is not None], "proporcao"),
                      locsim=_resolution([s for s in s6 if s.persons_XY is not None and len(s.persons_XY)], "proporcao"))}
    out = []
    for kind, fname, key, title in (("gsr", "sensibilidade_detector_gsr", "locsim", "detector (GSR)"),
                                    ("wc14", "sensibilidade_detector_wc14", "iou", "detector (WC14)"),
                                    ("6c", "sensibilidade_6c", "locsim", "6c com fluxo")):
        rows = [{k: (float(v) if k in _NUM else v) for k, v in r.items()}
                for r in csv.DictReader((path("outputs") / f"{fname}.csv").open(encoding="utf-8"))]
        for p in dict.fromkeys(r["parametro"] for r in rows):
            rs = [r for r in rows if r["parametro"] == p]
            big = {m: max(abs(r[m]) for r in rs) for m in ("cobertura", key)}
            dist = [f"{r['passo']:+.0%}" for r in rs if any(abs(r[m]) >= SENS["matters"] and abs(r[m]) >= f * res[kind][m] for m in big)]
            cls = "não importa" if max(big.values()) < SENS["matters"] else "importa" if dist else "indistinguível"
            out.append(dict(base=kind, parametro=p, max_d_cobertura=big["cobertura"], res_cobertura=res[kind]["cobertura"],
                            metrica=key, max_d_metrica=big[key], res_metrica=res[kind][key], classificacao=cls,
                            passos_distinguiveis=" ".join(dist)))
        _tornado(rows, key, f"Sensibilidade do {title}, um parâmetro de cada vez", path("outputs") / "figures" / f"{fname}.png",
                 res=f * res[kind][key])
    _write_csv(path("outputs") / "sensibilidade_importa.csv", out)
    print("resolução (um frame/imagem):", {k: {m: round(v, 4) for m, v in d.items()} for k, d in res.items()})
    for kind in ("gsr", "wc14", "6c"):
        rs = [r for r in out if r["base"] == kind]
        print(f"{kind}: " + ", ".join(f"{c} {sum(r['classificacao'] == c for r in rs)}" for c in ("importa", "indistinguível", "não importa")))
    return out


# Chave dos checkpoints da confirmação, lida UMA vez, na importação (com o arquivo que foi
# carregado): os fontes de src/ menos este, o código das funções de medição deste e o config
# sem a seção `sensitivity` (a parte dela que define a amostra vai no nome do arquivo).
# Mudar o relatório (agregação, bootstrap, tabelas) não refaz a medição; mudar a medição, sim.
_CODE_CONF = hashlib.sha1(
    b"".join(p.read_bytes() for p in sorted((ROOT / "src").rglob("*.py")) if p.name != "sensitivity.py") +
    "".join(inspect.getsource(f) for f in (perturbed, _check_reaches, _with, _with_many, _load, _rows_detector, _rows_6c, _confirm_task, _ckpt)).encode() +
    json.dumps({k: v for k, v in CFG.items() if k != "sensitivity"}, sort_keys=True, default=str).encode()).hexdigest()
