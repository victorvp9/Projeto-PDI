"""Confirmação dos candidatos da sensibilidade (src/sensitivity.py): métricas iguais às de
evaluate.summarize, bootstrap pareado e troca de vários parâmetros com restauração."""
import numpy as np
import pytest

from src import sensitivity as S


def _rows(seed, n_units=8, per_unit=10, p_pred=0.8):
    """Linhas sintéticas no formato de frame_metrics: unidades (clipes) com frames."""
    rng = np.random.default_rng(seed)
    rows = []
    for u in range(n_units):
        for i in range(per_unit):
            pred = bool(rng.random() < p_pred)
            r = dict(unidade=f"c{u}", pos=i, has_gt=True, dubious=False, has_pred=pred, has_lines=False, n_pessoas=5)
            if pred:
                r.update(npe=float(rng.random() * 0.02), iou_whole=float(rng.random()), iou_part=0.5, re_m=1.0,
                         locsim_d=rng.random(5) * 10)
            rows.append(r)
    return rows


def test_metrics_equal_summarize():
    from src.evaluate import summarize
    rows = _rows(0)
    t, a = summarize(rows)["todos"], S._arrays(rows)
    assert np.isclose(S._metric(a, "cobertura"), t["cobertura"])
    assert np.isclose(S._metric(a, "locsim"), t["locsim@5 penalizado"])
    assert np.isclose(S._metric(a, "npe"), t["npe"][1]) and np.isclose(S._metric(a, "iou"), t["iou_whole"][1])


def test_paired_bootstrap():
    """Iguais: Δ = 0 e intervalo (0, 0). Candidato que ganha H em frames de todas as
    unidades: Δ > 0, intervalo acima de 0 e contendo Δ; mesma semente, mesmo resultado."""
    base = _rows(1)
    units = [r["unidade"] for r in base]
    a = S._arrays(base)
    same = S.bootstrap_delta(a, S._arrays(base), units, ("locsim", "cobertura"), 200, 0, 0.95)
    assert all(v == (0.0, 0.0, 0.0) for v in same.values())
    better = [dict(r, has_pred=True, locsim_d=np.zeros(5), npe=0.0, iou_whole=1.0) if not r["has_pred"] else r for r in base]
    b = S._arrays(better)
    d = S.bootstrap_delta(a, b, units, ("locsim", "cobertura"), 200, 0, 0.95)
    for m, (delta, lo, hi) in d.items():
        assert delta > 0 and 0 < lo <= delta <= hi
    assert d == S.bootstrap_delta(a, b, units, ("locsim", "cobertura"), 200, 0, 0.95)


def test_with_many_restores_config():
    from src.config import CFG
    old = (CFG["temporal"]["anchor_window"], CFG["temporal"]["verify_window"])
    seen = S._with_many([("temporal.anchor_window", 99), ("temporal.verify_window", 77)],
                        lambda: (CFG["temporal"]["anchor_window"], CFG["temporal"]["verify_window"]))
    assert seen == (99, 77) and (CFG["temporal"]["anchor_window"], CFG["temporal"]["verify_window"]) == old


def _effective(ds):
    """O config que detect_frame entrega para baixo: params(ds) e CFG["lines"] com a
    variante do detector por cima; assign e fit como estão."""
    import copy
    from src.config import CFG
    from src.segment import params
    v = next(iter(CFG["detector"]["variants"].values()))
    return copy.deepcopy({"segment": {**params(ds), **v.get("segment", {})}, "lines": {**CFG["lines"], **v.get("lines", {})},
                          "assign": CFG["assign"], "fit": CFG["fit"]})


def test_guard_refuses_shadowed_and_import_time_params():
    """lines.fuse_d_frac é sombreado pela variante do detector (a sensibilidade mediu um
    valor que o detector não lê); assign.score_step_m só é lido na importação."""
    for p in ("lines.fuse_d_frac", "segment.common.line_scales", "assign.score_step_m", "pitch.sample_step_m"):
        with pytest.raises(ValueError):
            S._with(p, 1, lambda: None)


def test_every_listed_detector_param_reaches_the_detector():
    """Cada parâmetro do detector na sensibilidade e na confirmação muda o config efetivo
    de detect_frame em pelo menos uma base (os line_thr, cada um na sua)."""
    cands = S.SENS["detector"] + [c[0] for c in S.CONF["detector"]]
    for p in cands:
        changed = [ds for ds in ("gsr", "wc14") if S._with(p, S.perturbed(p, 0.5), lambda: _effective(ds)) != _effective(ds)]
        assert changed, p
        if p.startswith("segment.gsr.") or p.startswith("segment.wc14."):
            assert changed == [p.split(".")[1]], (p, changed)


def test_ground_truth_is_loaded_outside_the_perturbation(monkeypatch, tmp_path):
    """fit.* entra na chave e no aceite da H de gabarito do GSR: as amostras (com o
    gabarito) têm que ser carregadas com o config atual, antes da troca, na sensibilidade
    do detector e na confirmação."""
    from src.config import CFG
    from src.io import gsr
    seen = []
    monkeypatch.setattr(gsr, "load_clip", lambda *a, **k: seen.append(CFG["fit"]["max_cond"]) or [])
    monkeypatch.setattr(S, "_detector_metrics", lambda ds, samples: {"max_cond": CFG["fit"]["max_cond"]})
    monkeypatch.setattr(S, "_rows_detector", lambda unit, samples, ds: [CFG["fit"]["max_cond"]])
    monkeypatch.setattr(S, "_ckpt", lambda steps, kind, unit: tmp_path / "c.pkl")
    base = CFG["fit"]["max_cond"]
    _, inside = S._detector_task(("fit.max_cond", 0.5, "gsr"))
    _, inside2 = S._confirm_task(((("fit.max_cond", 0.5),), "gsr", "SNGS-000"))
    assert seen and all(v == base for v in seen)
    assert inside["max_cond"] == inside2[0] == S.perturbed("fit.max_cond", 0.5) != base


def _stages(img, ds):
    """Saídas intermediárias do detector como em detect_frame (mesmas mesclas, lidas na
    hora): gramado, marcações, segmentos, elipses e o info da estimativa."""
    from src.assign import estimate
    from src.conics import detect
    from src.config import CFG
    from src.segment import grass_mask, line_mask, params
    v = next(iter(CFG["detector"]["variants"].values()))
    P = params(ds)
    grass = grass_mask(img, P)
    marks = line_mask(img, grass, {**P, **v.get("segment", {})})
    segs, ells, cid = detect(marks, {**CFG["lines"], **v.get("lines", {})})
    _, info = estimate(marks, grass, segs[cid < 0], CFG["detector"]["refine"])
    return dict(grass=grass, marks=marks, segs=np.asarray(segs), ells=[tuple(np.round(e, 6)) for e in ells], info=info)


def _frame(ds, which):
    from src.config import path
    from src.io import gsr, wc14
    try:
        if ds == "gsr":
            clip, i = which
            return gsr.load_clip(path("gsr") / "train" / clip, fit="none")[i].image
        return wc14.load_sample("train_val", wc14.split_ids("train_val")[which]).image
    except (FileNotFoundError, IndexError, OSError):
        pytest.skip("sem os dados")


# Parâmetros com Δ exatamente 0 nos quatro passos da sensibilidade (decisoes.md, 2026-10-01):
# num frame escolhido para isso, o valor muda alguma saída intermediária do detector. O
# zero era do subconjunto, não do código. (fit.*: limiar logo abaixo do valor do ajuste
# neste frame, resíduo 1,07 px; gate_img: acima do termo da imagem, 0,904.)
ZERO_CASES = [
    ("segment.common.close_frac", "wc14", 0, -0.5, None, "grass"),
    ("lines.ellipse_arc_min_frac", "wc14", 0, 0.5, None, "ells"),
    ("lines.ellipse_arc_min_frac", "gsr", ("SNGS-099", 300), -0.5, None, "ells"),
    ("assign.iou_prune", "wc14", 0, -0.5, None, "podadas"),
    ("assign.gate_img", "gsr", ("SNGS-099", 0), None, 0.95, "ok"),
    ("fit.max_resid_px", "gsr", ("SNGS-099", 0), None, 0.5, "fit_ok"),
    ("fit.max_cond", "gsr", ("SNGS-099", 0), None, 1.0, "fit_ok"),
    ("detector.variants.td6_e1.lines.fuse_d_frac", "gsr", ("SNGS-099", 0), -0.5, None, "segs"),
    ("segment.gsr.line_thr", "gsr", ("SNGS-099", 0), -0.5, None, "marks"),
    ("segment.wc14.line_thr", "wc14", 0, -0.5, None, "marks"),
]



@pytest.mark.slow
@pytest.mark.parametrize("p, ds, which, step, value, out", ZERO_CASES, ids=[f"{c[0]}-{c[1]}" for c in ZERO_CASES])
def test_zero_delta_params_change_an_intermediate_output(p, ds, which, step, value, out):
    img = _frame(ds, which)
    v = S.perturbed(p, step) if value is None else value
    a, b = _stages(img, ds), S._with(p, v, lambda: _stages(img, ds))
    if out in ("grass", "marks"):
        assert (a[out] != b[out]).any()
    elif out == "segs":
        assert a["segs"].shape != b["segs"].shape or not np.array_equal(a["segs"], b["segs"])
    elif out == "ells":
        assert a["ells"] != b["ells"]
    else:
        assert a["info"][out] != b["info"][out], (a["info"], b["info"])
