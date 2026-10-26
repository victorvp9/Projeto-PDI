"""v2 (adaptado de scripts/rodada_test/tabelas_test.py, mesmo cálculo; docs/decisoes.md 2026-10-23): só T1, T6 (com o v1 ao lado), T1b, T2, T5, T7, T8. Tabelas T1-T9 da rodada do test (03-plano, 8.3), só a partir dos caches e dos pickles da
rodada (outputs/runs/rodada_test/); nenhum parâmetro, nenhuma H recalculada. Intervalo de
95% por bootstrap sorteando JOGOS (2.000 reamostragens, semente 20261001), pareado entre as
séries. Os valores pontuais são conferidos contra evaluate.summarize. Grava os CSVs em
outputs/runs/rodada_test/tabelas/, cada linha com o commit do método (congelado) e o dos
scripts (versionados em scripts/rodada_test, sem alteração pendente), e o fechamento.json. Uso (da raiz, PYTHONPATH=.): tabelas_test.py"""
import csv
import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from src_v2 import temporal as T
from src_v2.config import CFG, path
from src_v2.evaluate import E, locsim, summarize
from src_v2.io import gsr, wc14

SPLIT = sys.argv[1] if len(sys.argv) > 1 else "test"
DRY = SPLIT != "test"                 # ensaio da lógica em outra partição: sem Kalman, T2, T3, T4 e T9
OUT = path("runs") / "rodada_test_v2"
TAB = OUT / ("tabelas" if not DRY else f"ensaio_{SPLIT}")
TAB.mkdir(parents=True, exist_ok=True)
FROZEN = json.loads((path("runs") / "congelamento_v2.json").read_text(encoding="utf-8"))
FROZEN["commit"] = FROZEN["commit_metodo"]
V1_T6 = {r["jogo"]: r for r in csv.DictReader(open("outputs/runs/rodada_test/tabelas/T6.csv", encoding="utf-8"))}   # v1 publicado
def scripts_commit():
    """Hash do último commit de scripts/rodada_test; recusa rodar com alteração sem commit
    (decisão de Victor: as tabelas saem de scripts versionados, com o hash gravado)."""
    import subprocess
    here = "scripts/v2/rodada_test_v2"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", here], capture_output=True, text=True).stdout.strip()
    assert not dirty, "scripts com alteração sem commit: " + dirty
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", here], capture_output=True, text=True).stdout.strip()


COMMIT_T = scripts_commit()
N_BOOT, SEED, CI = 2000, 20261001, 0.95
TAUS = E["locsim_taus_m"]
SERIES = ["detector", "6a Bassek", "6a robusto", "Kalman + RTS", "6c fluxo", "6c sem linhas", "6c sem fluxo",
          "6c âncora ingênua /150", "6c âncora de gabarito"]
AUXFLOW_T7 = {"NBJW": 0.885, "AuxFlow": 0.929}                     # tabela 7 do AuxFlow, LocSim@5
AUXFLOW_T4 = {"NBJW": (43.15, 35.93), "AuxFlow": (83.67, 96.15)}  # tabela 4, HSB, % (média, mediana)
AUXFLOW_T6 = [("NBJW keypoints", "8", 54, 13.9), ("NBJW H estimation", "1", 27, 27.8), ("U-Net initialization", "1", 61, 12.3),
              ("Propagation", "1", 150, 5.0), ("Overall", "–", 292, 2.6)]   # tabela 6, i7-8700K + RTX 4090, por clipe de 750 frames


def write(name, rows):
    """CSV da tabela; toda linha leva o commit do método (congelado) e o dos scripts das tabelas."""
    rows = [r | dict(commit_metodo=FROZEN["commit"], commit_tabelas=COMMIT_T) for r in rows]
    with (TAB / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- dados
clips = sorted((path("gsr") / SPLIT).glob("SNGS-*"))
res6 = {}
for c in clips:
    k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
    # a chave congelada (418a3be) ou a do código atual: depois da correção da conferência da série
    # (temporal.py:93, que não muda saída) a chave do 6c foi regravada com conferência (decisoes.md)
    assert k in (FROZEN["chaves"]["6c"], T._eval_6c_key()), f"{c.name}: cache do 6c com outra chave"
    res6[c.name] = r
if DRY:
    extras, cons = {}, None
    SERIES = [v for v in SERIES if v != "Kalman + RTS"]
else:
    ext = pickle.loads((OUT / "extras_test.pkl").read_bytes())
    COMMIT_EXTRAS = ext["commit_scripts"]                           # os extras valem se o extras_test.py não mudou desde o commit deles
    assert COMMIT_EXTRAS == COMMIT_T or __import__("subprocess").run(
        ["git", "diff", "--quiet", COMMIT_EXTRAS, "HEAD", "--", "scripts/v2/rodada_test_v2/extras_test_v2.py"]).returncode == 0, \
        "extras de um commit em que o extras_test.py era diferente"
    extras = {e["clip"]: e for e in ext["res"]}
    cons = None
    assert set(res6) == set(extras) and len(res6) == 49
rows = [r | {"clipe": c} for c, x in res6.items() for r in x[0]] + [r | {"clipe": c} for c, e in extras.items() for r in e["kalman_rows"]]
anc_by_clip = {c: x[2] for c, x in res6.items()}
with_anchor = {c for c, a in anc_by_clip.items() if any(z["aceita"] for z in a)}
games = sorted({r["jogo"] for r in rows}, key=int)
clip_game = {c: next(r["jogo"] for r in res6[c][0]) for c in res6}
print(f"GSR {SPLIT}: {len(clips)} clipes, {len(games)} jogos ({', '.join(f'jogo {g}: {sum(clip_game[c] == g for c in clip_game)} clipes' for g in games)}); "
      f"{len(with_anchor)} clipes com >= 1 âncora aceita")


def arrays(rs):
    """Por frame: gabarito, H, soma do LocSim@5 e de cada τ do mAP, pessoas, pessoas nos
    frames com H e distâncias, NPE, IoU_whole, jogo, clipe."""
    g = lambda k: np.array([r.get(k, np.nan) for r in rs], float)
    return dict(gt=np.array([r["has_gt"] for r in rs]), pred=np.array([r["has_pred"] for r in rs]),
                ls5=np.array([locsim(r["locsim_d"], 5).sum() if "locsim_d" in r else 0.0 for r in rs]),
                lsT=np.array([[locsim(r["locsim_d"], t).sum() if "locsim_d" in r else 0.0 for t in TAUS] for r in rs]).reshape(len(rs), len(TAUS)),
                npers=np.array([r.get("n_pessoas", 0) for r in rs], float),
                nd=np.array([len(r["locsim_d"]) if "locsim_d" in r else 0 for r in rs], float),
                npe=g("npe"), iou=g("iou_whole"), jogo=np.array([r["jogo"] for r in rs]), clipe=np.array([r["clipe"] for r in rs]))


def metrics(a, ix=None):
    a = a if ix is None else {k: v[ix] for k, v in a.items()}
    gp = a["gt"] & a["pred"]
    med = lambda v: float(np.nanmedian(v)) if np.isfinite(v).any() else np.nan
    n = a["npers"].sum()
    return dict(cobertura=gp.sum() / a["gt"].sum(), npe_med=med(a["npe"][gp]), npe_media=float(np.nanmean(a["npe"][gp])) if np.isfinite(a["npe"][gp]).any() else np.nan,
                iou_med=med(a["iou"][gp]), locsim_pen=a["ls5"].sum() / n if n else np.nan,
                locsim_cob=a["ls5"].sum() / a["nd"].sum() if a["nd"].sum() else np.nan,
                map_pen=float(np.mean(a["lsT"].sum(axis=0) / n)) if n else np.nan)


A = {v: arrays([r for r in rows if r["variante"] == v]) for v in SERIES}
for v in SERIES:                                                   # mesma ordem de frames em todas as séries
    assert (A[v]["clipe"] == A["detector"]["clipe"]).all()
    t, m = summarize([r for r in rows if r["variante"] == v])["todos"], metrics(A[v])
    for k, ref in (("cobertura", t["cobertura"]), ("npe_med", t["npe"][1]), ("iou_med", t["iou_whole"][1]),
                   ("locsim_pen", t["locsim@5 penalizado"]), ("locsim_cob", t.get("locsim@5", (np.nan,))[0]),
                   ("map_pen", t["mAP-locsim penalizado"])):
        assert np.isclose(m[k], ref, equal_nan=True), (v, k, m[k], ref)

games_arr = A["detector"]["jogo"]
groups = [np.nonzero(games_arr == g)[0] for g in games]
draws = np.random.default_rng(SEED).integers(0, len(groups), (N_BOOT, len(groups)))
IX = [np.concatenate([groups[j] for j in d]) for d in draws]
anc_mask = np.isin(A["detector"]["clipe"], sorted(with_anchor))


def frac(m, v):
    d, t = m["detector"]["locsim_pen"], m["6c âncora de gabarito"]["locsim_pen"]
    return (m[v]["locsim_pen"] - d) / (t - d) if t != d else np.nan


def boot(fn):
    """Valor pontual e intervalo de `fn(ix)` (ix: frames sorteados por jogo)."""
    vals = np.array([fn(ix) for ix in IX], float)
    lo, hi = np.nanpercentile(vals, [100 * (1 - CI) / 2, 100 * (1 + CI) / 2])
    return float(fn(None)), float(lo), float(hi)


# ---------------------------------------------------------------- T1 (com intervalo) e T6
def all_metrics(ix):
    return {v: metrics(A[v], ix) for v in SERIES}


boot_all = [all_metrics(ix) for ix in IX]
point = all_metrics(None)


def ci(get):
    vals = np.array([get(m) for m in boot_all], float)
    lo, hi = np.nanpercentile(vals, [100 * (1 - CI) / 2, 100 * (1 + CI) / 2])
    return float(get(point)), float(lo), float(hi)


def anc_metric(v, ix):
    sel = np.nonzero(anc_mask)[0] if ix is None else ix[anc_mask[ix]]
    return metrics(A[v], sel)["locsim_pen"]


fmt = lambda t: f"{t[0]:.3f} [{t[1]:.3f}; {t[2]:.3f}]"
NOTE_BOOT = (f"bootstrap com {len(games)} jogos: {__import__('math').comb(2 * len(games) - 1, len(games))} reamostragens distintas; "
             "o intervalo é praticamente o mínimo e o máximo dos jogos; ver T6")   # nota pedida por Victor (2026-10-02)
t1 = []
print(f"\n== T1. GSR test, {len(clips)} clipes, {len(games)} jogos (intervalo de 95% por bootstrap de jogos; com < 5 jogos, ver a T6 ao lado)")
print(f"   nota: {NOTE_BOOT}")
print("série                     | cobertura              | NPE med (média) | IoU_whole med | LocSim@5 pen           | nos cobertos           | mAP pen                | pen, clipes com âncora | fração ao teto")
for v in SERIES:
    m = point[v]
    c = {k: ci(lambda mm, k=k: mm[v][k]) for k in ("cobertura", "locsim_pen", "locsim_cob", "map_pen", "npe_med")}
    an = boot(lambda ix, v=v: anc_metric(v, ix))
    fr = ci(lambda mm, v=v: frac(mm, v)) if v not in ("detector", "6c âncora de gabarito") else (np.nan, np.nan, np.nan)
    print(f"{v:25} | {fmt(c['cobertura'])} | {m['npe_med']:.4f} ({m['npe_media']:.3f}) | {m['iou_med']:.3f}         | {fmt(c['locsim_pen'])} | "
          f"{fmt(c['locsim_cob'])} | {fmt(c['map_pen'])} | {fmt(an)} | {fmt(fr) if np.isfinite(fr[0]) else '—'}")
    t1.append(dict(serie=v, **{f"{k}": c[k][0] for k in c}, **{f"{k}_lo": c[k][1] for k in c}, **{f"{k}_hi": c[k][2] for k in c},
                   npe_media=m["npe_media"], iou_med=m["iou_med"], locsim_pen_com_ancora=an[0], locsim_pen_com_ancora_lo=an[1],
                   locsim_pen_com_ancora_hi=an[2], fracao_teto=fr[0], fracao_teto_lo=fr[1], fracao_teto_hi=fr[2], nota=NOTE_BOOT))
write("T1", t1)

t6 = []
print(f"\n== T6. GSR test por jogo")
print("jogo | clipes | com âncora | frames | cobertura det / 6c | LocSim@5 pen det / 6c / teto")
for g, ix in zip(games, groups):
    md, m6, mt = metrics(A["detector"], ix), metrics(A["6c fluxo"], ix), metrics(A["6c âncora de gabarito"], ix)
    cs = [c for c in clip_game if clip_game[c] == g]
    print(f"{g:4} | {len(cs):6} | {sum(c in with_anchor for c in cs):10} | {len(ix):6} | {md['cobertura']:.3f} / {m6['cobertura']:.3f}    | "
          f"{md['locsim_pen']:.3f} / {m6['locsim_pen']:.3f} / {mt['locsim_pen']:.3f}")
    v1 = V1_T6.get(g, {}) if not DRY else {}
    t6.append(dict(jogo=g, clipes=len(cs), com_ancora=sum(c in with_anchor for c in cs), frames=len(ix), cob_detector=md["cobertura"],
                   cob_6c=m6["cobertura"], locsim_pen_detector=md["locsim_pen"], locsim_pen_6c=m6["locsim_pen"], locsim_pen_teto=mt["locsim_pen"],
                   **{f"v1_{k}": float(v1[k]) for k in ("com_ancora", "cob_detector", "cob_6c", "locsim_pen_detector", "locsim_pen_6c", "locsim_pen_teto") if k in v1}))
write("T6", t6)

# ---------------------------------------------------------------- T1b
common = A["detector"]["pred"]
print(f"\n== T1b. Conjunto comum (frames com H do detector: {int(common.sum())})")
t1b = []
for v in SERIES:
    m = metrics(A[v], np.nonzero(common)[0])
    print(f"{v:25} | NPE med {m['npe_med']:.4f} | LocSim@5 pen {m['locsim_pen']:.3f} | nos cobertos {m['locsim_cob']:.3f}")
    t1b.append(dict(serie=v, frames=int(common.sum()), npe_med=m["npe_med"], locsim_pen=m["locsim_pen"], locsim_cob=m["locsim_cob"]))
write("T1b", t1b)

# ---------------------------------------------------------------- T2 (HSB)
if not DRY:
    hsb_csv = {r["clipe"]: r for r in csv.DictReader(open("data_splits/hsb.csv", encoding="utf-8"))}


    def per_frame(rs):
        """LocSim@5 por frame (média sobre as pessoas do frame), nos frames com pessoas: (valor
        penalizado, com 0 sem H; valor só se coberto ou NaN)."""
        pen, cob = [], []
        for r in rs:
            if not r.get("n_pessoas"):
                continue
            v = float(locsim(r["locsim_d"], 5).mean()) if "locsim_d" in r else 0.0
            pen.append(v)
            cob.append(v if r["has_pred"] else np.nan)
        return np.array(pen), np.array(cob)


    def interval(rs_variant, a, b):
        lo, hi = min(a, b), max(a, b)
        return rs_variant[lo:hi + 1]                                     # linhas na ordem dos frames do clipe


    def coverages(rs):
        """Cobertura nos frames com H_gt (a coluna original), nos frames com pessoas (a que fecha
        pen = cob x cobertura nas médias por frame) e por pessoa (fração das pessoas-frame com H,
        a que fecha pen = cob no agregado por pessoa-frame); e o LocSim por pessoa-frame."""
        wp = [r for r in rs if r.get("n_pessoas")]
        ls = lambda r: float(locsim(r["locsim_d"], 5).sum()) if "locsim_d" in r else 0.0
        n_all, n_cov = sum(r["n_pessoas"] for r in wp), sum(r["n_pessoas"] for r in wp if r["has_pred"])
        return dict(cov_gt=np.mean([r["has_pred"] for r in rs if r["has_gt"]]) if any(r["has_gt"] for r in rs) else np.nan,
                    cov_fr=np.mean([r["has_pred"] for r in wp]), cov_ps=n_cov / n_all,
                    pen_ps=sum(ls(r) for r in wp) / n_all, cob_ps=sum(ls(r) for r in wp if r["has_pred"]) / n_cov if n_cov else np.nan)

    t2, pooled = [], defaultdict(lambda: ([], [], [], []))
    print("\n== T2. HSB: 10 clipes do test, LocSim@5 por frame (%), penalizado / só nos cobertos; cobertura nos frames com H_gt / "
          "nos frames com pessoas / por pessoa. Confere: pen = cob x cobertura nos frames com pessoas (médias por frame) e, "
          "no agregado por pessoa-frame, pen = cob x cobertura por pessoa")
    print("clipe    intervalo | NBJW (tab. 3) | (1) só propagação | (2) detector | (3) pipeline (6c)")
    for c, h in hsb_csv.items():
        a, b = int(h["inicio"]), int(h["fim"])
        rs6 = res6[c][0]
        byv = {v: [r for r in rs6 if r["variante"] == v] for v in ("detector", "6c fluxo")}
        meas = {"(1) só propagação": extras[c]["hsb"].get("rows"), "(2) detector": interval(byv["detector"], a, b),
                "(3) pipeline": interval(byv["6c fluxo"], a, b)}
        cells, rec = [], dict(clipe=c, inicio=a, fim=b, locsim5_nbjw=float(h["locsim5_nbjw"]))
        for k, rs in meas.items():
            if rs is None:
                cells.append("sem H_gt_auxflow no frame inicial")
                continue
            pen, cob = per_frame(rs)
            cv = coverages(rs)
            cob_m = np.nanmean(cob) if np.isfinite(cob).any() else 0.0
            assert abs(np.mean(pen) - cob_m * cv["cov_fr"]) < 1e-9, (c, k, "pen != cob x cobertura nos frames com pessoas")
            assert not np.isfinite(cv["cob_ps"]) or abs(cv["pen_ps"] - cv["cob_ps"] * cv["cov_ps"]) < 1e-9, (c, k, "identidade por pessoa")
            for i, x in enumerate((pen, cob)):
                pooled[k][i].extend(x)
            pooled[k][2].extend(rs)
            pooled[k][3].extend([r["has_pred"] for r in rs if r["has_gt"]])
            cells.append(f"{100 * np.mean(pen):5.1f} / {100 * np.nanmean(cob) if np.isfinite(cob).any() else np.nan:5.1f}; "
                         f"{cv['cov_gt']:.2f} / {cv['cov_fr']:.2f} / {cv['cov_ps']:.2f}")
            rec |= {f"{k} pen média": np.mean(pen), f"{k} cob média": np.nanmean(cob) if np.isfinite(cob).any() else np.nan,
                    f"{k} cobertura": cv["cov_gt"], f"{k} cobertura frames com pessoas": cv["cov_fr"], f"{k} cobertura por pessoa": cv["cov_ps"],
                    f"{k} pen por pessoa-frame": cv["pen_ps"], f"{k} cob por pessoa-frame": cv["cob_ps"]}
        print(f"{c} {a:4}-{b:<4} | {100 * float(h['locsim5_nbjw']):5.1f}         | " + " | ".join(cells))
        t2.append(rec)
    print("todos os frames do HSB (média / mediana por frame, %):")
    for k, (pen, cob, rs_all, hp) in pooled.items():
        pen, cob = np.array(pen), np.array(cob)
        cv = coverages(rs_all)
        print(f"   {k:18} pen {100 * pen.mean():5.1f} / {100 * np.median(pen):5.1f} | cob {100 * np.nanmean(cob):5.1f} / {100 * np.nanmedian(cob):5.1f} | "
              f"cobertura {np.mean(hp):.3f} (frames com H_gt) / {cv['cov_fr']:.3f} (frames com pessoas) / {cv['cov_ps']:.3f} (por pessoa) | "
              f"por pessoa-frame: pen {100 * cv['pen_ps']:5.1f}, cob {100 * cv['cob_ps']:5.1f} | frames com pessoas {len(pen)}")
        t2.append(dict(clipe="todos", **{f"{k} pen média": pen.mean(), f"{k} pen mediana": np.median(pen), f"{k} cob média": np.nanmean(cob),
                                         f"{k} cob mediana": np.nanmedian(cob), f"{k} cobertura": np.mean(hp),
                                         f"{k} cobertura frames com pessoas": cv["cov_fr"], f"{k} cobertura por pessoa": cv["cov_ps"],
                                         f"{k} pen por pessoa-frame": cv["pen_ps"], f"{k} cob por pessoa-frame": cv["cob_ps"]}))
    print(f"   AuxFlow, tabela 4 (média / mediana, %): NBJW {AUXFLOW_T4['NBJW']}, AuxFlow {AUXFLOW_T4['AuxFlow']}; "
          "a medição (1) começa da H_gt_auxflow (RANSAC nas pessoas) e é o análogo da tabela 4")
    write("T2", t2)

# ---------------------------------------------------------------- T5
print("\n== T5. Comparação com a tabela 7 do AuxFlow (LocSim@5). O deles não tem frame sem H; o nosso é agregado sobre pessoas-frame,")
print("   penalizado (pessoa de frame sem H vale 0); agregar por frame quase não muda a média (conferência de 2026-09-25)")
print(f"   nota: {NOTE_BOOT}")
gain = ci(lambda mm: mm["6c fluxo"]["locsim_pen"] - mm["detector"]["locsim_pen"])
gain_cob = ci(lambda mm: mm["6c fluxo"]["locsim_cob"] - mm["detector"]["locsim_cob"])
cm = {v: metrics(A[v], np.nonzero(common)[0]) for v in ("detector", "6c fluxo")}
t5 = [dict(linha="NBJW (AuxFlow, tab. 7)", locsim5=AUXFLOW_T7["NBJW"]), dict(linha="AuxFlow (tab. 7)", locsim5=AUXFLOW_T7["AuxFlow"]),
      dict(linha="ganho AuxFlow - NBJW", locsim5=AUXFLOW_T7["AuxFlow"] - AUXFLOW_T7["NBJW"])]
for v in ("detector", "6c fluxo"):
    p, cb = ci(lambda mm, v=v: mm[v]["locsim_pen"]), ci(lambda mm, v=v: mm[v]["locsim_cob"])
    print(f"   nosso {v:9}: penalizado {fmt(p)} | nos cobertos {fmt(cb)} | conjunto comum {cm[v]['locsim_cob']:.3f}")
    t5.append(dict(linha=f"nosso {v}", pen=p[0], pen_lo=p[1], pen_hi=p[2], cob=cb[0], cob_lo=cb[1], cob_hi=cb[2], comum=cm[v]["locsim_cob"], nota=NOTE_BOOT))
print(f"   ganho 6c - detector: penalizado {fmt(gain)} | nos cobertos {fmt(gain_cob)} | AuxFlow - NBJW: {AUXFLOW_T7['AuxFlow'] - AUXFLOW_T7['NBJW']:+.3f}")
t5.append(dict(linha="ganho 6c - detector", pen=gain[0], pen_lo=gain[1], pen_hi=gain[2], cob=gain_cob[0], cob_lo=gain_cob[1], cob_hi=gain_cob[2], nota=NOTE_BOOT))
write("T5", t5)

# ---------------------------------------------------------------- T7 e T8
anc = [a for c in res6 for a in anc_by_clip[c]]
print("\n== T7. Âncoras no test")
t7 = []
for label, sel in (("candidatas", lambda a: True), ("verificáveis", lambda a: a["verificavel"]), ("aceitas", lambda a: a["aceita"])):
    e = np.array([a["npe"] for a in anc if sel(a)], float)
    f = e[np.isfinite(e)]
    print(f"   {label:13} {len(e):5}  erradas (NPE > 0,05): {int((f > 0.05).sum())} ({np.mean(f > 0.05) if len(f) else np.nan:.1%} das com gabarito)")
    t7.append(dict(conjunto=label, n=len(e), com_gabarito=len(f), erradas=int((f > 0.05).sum())))
sem = sorted(set(res6) - with_anchor)
print(f"   clipes sem âncora aceita: {len(sem)} {sem}")
t7.append(dict(conjunto="clipes sem âncora aceita", n=len(sem), lista=" ".join(sem)))
write("T7", t7)

print("\n== T8. Lacunas do detector no test: cobertura e NPE mediano")
t8 = []
by_v = {v: [r for r in rows if r["variante"] == v] for v in ("detector", "6a Bassek", "6a robusto", "6c fluxo", "6c sem linhas")}
for lo, hi, lab in ((1, 3, "1-3"), (4, 25, "4-25"), (26, 10 ** 6, "> 25"), (-1, -1, "pontas")):
    line = dict(lacuna=lab, frames=sum(1 for r in by_v["detector"] if lo <= r["lacuna"] <= hi and r["has_gt"]))
    for v, rs in by_v.items():
        rr = [r for r in rs if lo <= r["lacuna"] <= hi and r["has_gt"]]
        e = [r["npe"] for r in rr if "npe" in r]
        line |= {f"{v} cob": len(e) / max(len(rr), 1), f"{v} NPE": float(np.median(e)) if e else np.nan}
    print("   " + " | ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in line.items()))
    t8.append(line)
write("T8", t8)

(TAB / "fechamento.json").write_text(json.dumps(dict(
    data=__import__("datetime").datetime.now().isoformat(timespec="seconds"), particao=SPLIT, commit_metodo=FROZEN["commit"],
    commit_tabelas=COMMIT_T, commit_extras=None if DRY else COMMIT_EXTRAS, tabelas=sorted(p.name for p in TAB.glob("*.csv")),
    rotulo=FROZEN["rotulo"], reproducao="método: python -m src_v2.run no commit_metodo (tag v2-final); tabelas: scripts/v2/rodada_test_v2 no commit_tabelas"),
    ensure_ascii=False, indent=1), encoding="utf-8")
print(f"commit do método {FROZEN['commit'][:12]}; commit dos scripts das tabelas {COMMIT_T[:12]}")
print(f"\nCSVs em {TAB}")
