"""Fatia 7d: sensibilidade descritiva dos parâmetros — um de cada vez, com os passos
relativos de `sensitivity.steps` — sem recalibrar nada (decisoes.md, 2026-09-30).
Detector nos subconjuntos da regressão (GSR: 60 frames; WC14: train_val[::6]); 6c com
fluxo no subconjunto de 6 clipes do treino. O 6a (Hampel) e o Kalman já têm as
tabelas das grades de calibração. Mais a auditoria da origem das constantes do config.
"""
import hashlib
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


def _with(p, value, fn):
    """Roda fn() com o parâmetro p trocado por value, no CFG deste processo, e restaura."""
    from src import temporal
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


def _detector_metrics(dataset):
    """Cobertura, IoU_whole e NPE medianos e LocSim@5 penalizado (só GSR) do detector no
    subconjunto da regressão."""
    from src.assign import detect_frame
    from src.evaluate import frame_metrics, summarize
    from src.io import gsr, wc14
    if dataset == "gsr":
        samples = [s for c in sorted((path("gsr") / "train").glob("SNGS-*"))[::10] for s in gsr.load_clip(c)[::75] if s.H_gt is not None]
    else:
        samples = [wc14.load_sample("train_val", i) for i in wc14.split_ids("train_val")[::6]]
    rows = []
    for s in samples:
        H = next(iter(detect_frame(s.image, dataset).values()))[0]
        rows.append(dict(**frame_metrics(H, s), n_pessoas=0 if getattr(s, "persons_XY", None) is None else len(s.persons_XY)))
    t = summarize(rows)["todos"]
    return dict(cobertura=t["cobertura"], iou=t["iou_whole"][1], npe=t["npe"][1], locsim=t.get("locsim@5 penalizado", np.nan))


def _detector_task(args):
    p, step, dataset = args
    cv2.setNumThreads(1)
    if p is None:
        return args, _detector_metrics(dataset)
    return args, _with(p, perturbed(p, step), lambda: _detector_metrics(dataset))


def _flow_metrics(clip):
    """Só a variante 6c com fluxo num clipe (âncoras verificadas, propagação): métricas."""
    from src import temporal as T
    from src.evaluate import frame_metrics, summarize
    from src.io import gsr
    ser = dict(np.load(T._series_path(clip)))
    samples = gsr.load_clip(clip)
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
    rows = _flow_metrics(clip) if p is None else _with(p, perturbed(p, step), lambda: _flow_metrics(clip))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(pickle.dumps((_CODE, rows)))
    return args, rows


def _tornado(rows, metric, title, out):
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


def run_detector(pool):
    """Sensibilidade do detector: tabela, CSV e tornados (GSR: LocSim@5; WC14: IoU)."""
    from src.run import _write_csv
    tasks = [(None, 0.0, d) for d in ("gsr", "wc14")] + \
            [(p, s, d) for p in SENS["detector"] for s in SENS["steps"] for d in ("gsr", "wc14")]
    with pool() as ex:
        res = [r for r in ex.map(_detector_task, tasks) if r is not None]
    out = {}
    for d, metrics, key in (("gsr", ("cobertura", "npe", "locsim"), ("cobertura", "locsim")),
                            ("wc14", ("cobertura", "iou", "npe"), ("cobertura", "iou"))):
        base = next(m for (p, _, dd), m in res if p is None and dd == d)
        print(f"\n== detector, {d.upper()} (config atual: " + ", ".join(f"{k} {base[k]:.4f}" for k in metrics) + ")")
        rows = _table([r for r in res if r[0][2] == d], base, metrics, key)
        _write_csv(path("outputs") / f"sensibilidade_detector_{d}.csv", rows)
        _tornado(rows, key[-1], f"Sensibilidade do detector ({d.upper()}, um parâmetro de cada vez)",
                 path("outputs") / "figures" / f"sensibilidade_detector_{d}.png")
        out[d] = rows
    return out


def run_temporal(pool, clips):
    """Sensibilidade do 6c com fluxo no subconjunto: tabela, CSV e tornado (LocSim@5)."""
    from src.evaluate import summarize
    from src.run import _write_csv
    tasks = [(None, 0.0, c) for c in clips] + [(p, s, c) for p in SENS["temporal"] for s in SENS["steps"] for c in clips]
    with pool() as ex:
        res = [r for r in ex.map(_temporal_task, tasks) if r is not None]

    def agg(p, step):
        t = summarize([r for (pp, ss, _), rows in res if pp == p and ss == step for r in rows])["todos"]
        return dict(cobertura=t["cobertura"], npe=t["npe"][1], locsim=t.get("locsim@5 penalizado", np.nan))
    base = agg(None, 0.0)
    merged = [((p, s, None), agg(p, s)) for p in SENS["temporal"] for s in SENS["steps"]]
    print(f"\n== 6c com fluxo, {len(clips)} clipes (config atual: " + ", ".join(f"{k} {v:.4f}" for k, v in base.items()) + ")")
    rows = _table(merged, base, ("cobertura", "npe", "locsim"), ("cobertura", "locsim"))
    _write_csv(path("outputs") / "sensibilidade_6c.csv", rows)
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
