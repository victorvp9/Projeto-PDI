"""Item 2 da leitura de Victor e análise de falhas (8.6) da rodada do test (2026-10-02).
Só a partir dos caches e pickles da rodada e de funções do src/ sem mudança: nenhum
parâmetro muda e nenhum número das tabelas é recalculado de outro jeito. As medidas da
segmentação (cruzamento com a Fatia 3) são diagnóstico, com as funções de avaliação da
Fatia 3, em 1 frame a cada 75 do test.

Saídas: tabelas impressas; CSVs em outputs/runs/rodada_test/falhas/; figuras em
outputs/figures/falhas_test/. Uso (da raiz, PYTHONPATH=.): analise_falhas.py"""
import csv
import pickle
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np

OUT = Path("outputs/runs/rodada_test/falhas")
FIG = Path("outputs/figures/falhas_test")
WRONG = 0.05                                     # NPE > 0,05: H errada (convenção das tabelas)


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


def load6(clip):
    from src import temporal as T
    k, res = pickle.loads(T._eval_6c_path(clip).read_bytes())
    assert k == T._eval_6c_key(), f"{clip.name}: cache do 6c de outro código"
    return res


def by_variant(rows):
    out = defaultdict(list)
    for r in rows:
        out[r["variante"]].append(r)
    return out


def t8(rows_by_clip):
    """A T8 (lacunas do detector: cobertura e NPE mediano), como na tabela do test."""
    out = []
    for lo, hi, lab in ((1, 3, "1-3"), (4, 25, "4-25"), (26, 10 ** 6, "> 25"), (-1, -1, "pontas")):
        line = dict(lacuna=lab)
        for v in ("6a Bassek", "6a robusto", "6c fluxo", "6c sem linhas"):
            rr = [r for rv in rows_by_clip for r in rv[v] if lo <= r["lacuna"] <= hi and r["has_gt"]]
            e = [r["npe"] for r in rr if "npe" in r]
            line |= {f"{v} cob": len(e) / max(len(rr), 1), f"{v} NPE": float(np.median(e)) if e else np.nan}
        line["frames"] = sum(1 for rv in rows_by_clip for r in rv["detector"] if lo <= r["lacuna"] <= hi and r["has_gt"])
        out.append(line)
    return out


def gaps(rv, lo=4, hi=25):
    """Lacunas internas do detector com lo <= L <= hi: (a, b) e as bordas a-1 e b+1."""
    has = np.array([r["has_pred"] for r in rv["detector"]])
    out, i, n = [], 0, len(has)
    while i < n:
        if has[i]:
            i += 1
            continue
        j = i
        while j < n and not has[j]:
            j += 1
        if i > 0 and j < n and lo <= j - i <= hi:
            out.append((i, j - 1))
        i = j
    return out


def gap_classes(clips_rows):
    """Cada lacuna de 4-25 frames classificada pela H do detector nas duas bordas."""
    rows = []
    for c, rv in clips_rows.items():
        det = rv["detector"]
        for a, b in gaps(rv):
            el, er = det[a - 1].get("npe", np.nan), det[b + 1].get("npe", np.nan)
            if not (np.isfinite(el) and np.isfinite(er)):
                cls = "borda sem gabarito"
            else:
                cls = {0: "bordas certas", 1: "uma borda errada", 2: "as duas bordas erradas"}[int(el > WRONG) + int(er > WRONG)]
            for v in ("6a Bassek", "6a robusto"):
                for i in range(a, b + 1):
                    r = rv[v][i]
                    if "npe" in r:
                        rows.append(dict(clipe=c, a=a, b=b, L=b - a + 1, classe=cls, serie=v, frame=i, npe=r["npe"], npe_borda_esq=el, npe_borda_dir=er))
    return rows


def summarize_gaps(rows, label):
    print(f"\n   {label}: lacunas de 4-25 frames do detector, pela H do detector nas bordas")
    print("   classe                  | lacunas | frames com gabarito | 6a Bassek NPE med, erradas | 6a robusto NPE med, erradas")
    out = []
    for cls in ("bordas certas", "uma borda errada", "as duas bordas erradas", "borda sem gabarito"):
        b = [r for r in rows if r["classe"] == cls and r["serie"] == "6a Bassek"]
        rb = [r for r in rows if r["classe"] == cls and r["serie"] == "6a robusto"]
        ng = len({(r["clipe"], r["a"]) for r in rows if r["classe"] == cls})
        f = lambda rr: (float(np.median([r["npe"] for r in rr])), float(np.mean([r["npe"] > WRONG for r in rr]))) if rr else (np.nan, np.nan)
        (mb, wb), (mr, wr) = f(b), f(rb)
        print(f"   {cls:23} | {ng:7} | {len(b):19} | {mb:.4f}, {wb:.0%}             | {mr:.4f}, {wr:.0%}")
        out.append(dict(conjunto=label, classe=cls, lacunas=ng, frames=len(b), bassek_npe_med=mb, bassek_erradas=wb, robusto_npe_med=mr, robusto_erradas=wr))
    return out


def seg_diag(clip):
    """Diagnóstico da segmentação (Fatia 3) num clipe, 1 frame a cada 75 com H_gt: campo
    projetado como grama, vazamento, cobertura das marcações a 2 px dos pontos anotados,
    resposta do filtro de linha nos pontos anotados (mediana) e fração acima do limiar, sombra."""
    from src.config import CFG
    from src.evaluate import field_grass_and_leak, is_shadow, point_coverage, shadow_score
    from src.io import gsr
    from src.segment import grass_mask, line_mask, line_response, params
    cv2.setNumThreads(1)
    P = params("gsr")
    out = []
    for s in gsr.load_clip(clip)[::75]:
        if s.H_gt is None or not s.lines_uv:
            continue
        img = s.image
        grass = grass_mask(img, P)
        resp = line_response(img, P)
        lines = line_mask(img, grass, P, response=resp)
        pts = np.concatenate(list(s.lines_uv.values()))
        u = np.clip(np.round(pts[:, 0]).astype(int), 0, img.shape[1] - 1)
        v = np.clip(np.round(pts[:, 1]).astype(int), 0, img.shape[0] - 1)
        frac, leak = field_grass_and_leak(grass, s.H_gt, s.size)
        out.append(dict(clipe=clip.name, frame=s.frame_idx, campo_grama=frac, vazamento=leak,
                        cobertura_2px=point_coverage(lines, pts, CFG["eval_segment"]["gsr_coverage_px"]),
                        resposta_mediana=float(np.median(resp[v, u])), acima_limiar=float(np.mean(resp[v, u] > P["line_thr"])),
                        sombra=is_shadow(*shadow_score(img, grass))))
    return out


def panel(img, H, lines_uv, text, w=640):
    from src.render import draw_overlay
    out = draw_overlay(img, H, lines_uv) if H is not None and np.isfinite(H).all() else img.copy()
    out = cv2.resize(out, (w, int(out.shape[0] * w / out.shape[1])))
    cv2.rectangle(out, (0, 0), (w, 26), (0, 0, 0), -1)
    cv2.putText(out, text, (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def top_view(M, out_path):
    """Vista de cima: o modelo pela H do detector levado ao campo do gabarito (M = H_gt^-1·H_det),
    em vermelho, sobre o modelo (cinza)."""
    from src.pitch_model import HL, HW, POLYLINES
    ppm, m = 6, 10
    to = lambda XY: np.round((np.asarray(XY) + [HL + m, HW + m]) * ppm).astype(np.int32)
    img = np.full((int(2 * (HW + m) * ppm), int(2 * (HL + m) * ppm), 3), (40, 90, 40), np.uint8)
    for poly in POLYLINES.values():
        cv2.polylines(img, [to(poly)], False, (200, 200, 200), 1, cv2.LINE_AA)
        q = np.c_[poly, np.ones(len(poly))] @ M.T
        ok = q[:, 2] > 1e-9
        if ok.sum() > 1:
            cv2.polylines(img, [np.clip(to(q[ok, :2] / q[ok, 2:]), -10 ** 5, 10 ** 5)], False, (0, 0, 230), 1, cv2.LINE_AA)
    cv2.imwrite(str(out_path), img)


def error_type(M):
    """Tipo do erro de uma âncora pela M = H_gt^-1·H_det (campo do detector -> campo do
    gabarito, m): para onde vão o centro e os marcos; heurística, conferida nas figuras."""
    from src.pitch_model import HL, HW
    P = np.array([[0, 0], [-HL, -HW], [HL, -HW], [HL, HW], [-HL, HW], [-HL + 11, 0], [HL - 11, 0]], float)
    q = np.c_[P, np.ones(len(P))] @ M.T
    Q = q[:, :2] / q[:, 2:]
    d = Q - P
    if np.allclose(Q[0], 0, atol=6) and np.mean(np.linalg.norm(Q[1:5] + P[1:5], axis=1)) < 10:
        return "simetria de 180°", Q
    if np.std(d[:, 0]) < 6 and abs(np.mean(d[:, 0])) > 4 and np.std(d[:, 1]) < 6:
        return f"deslocamento ao longo do comprimento ({np.mean(d[:, 0]):+.1f} m): troca de reta", Q
    if np.std(d[:, 1]) < 6 and abs(np.mean(d[:, 1])) > 3 and np.std(d[:, 0]) < 6:
        return f"deslocamento lateral ({np.mean(d[:, 1]):+.1f} m): troca de reta na largura", Q
    sx = np.ptp(Q[1:5, 0]) / np.ptp(P[1:5, 0]); sy = np.ptp(Q[1:5, 1]) / np.ptp(P[1:5, 1])
    return f"escala/perspectiva errada (comprimento x{sx:.2f}, largura x{sy:.2f})", Q


if __name__ == "__main__":
    from src import temporal as T
    from src.config import CFG, path
    from src.evaluate import npe_re
    from src.executor import SafeProcessPool, exit_if_failed
    from src.io import gsr
    FIG.mkdir(parents=True, exist_ok=True)
    test = sorted((path("gsr") / "test").glob("SNGS-*"))
    train3 = sorted((path("gsr") / "train").glob("SNGS-*"))[::3]
    res = {c.name: load6(c) for c in test}
    rv_test = {c: by_variant(r[0]) for c, r in res.items()}
    rv_train = {c.name: by_variant(load6(c)[0]) for c in train3}

    # ---------------- item 2: T8 no train[::3] e no test, lacunas 4-25 pelas bordas
    print("== Item 2. T8 (lacunas do detector: cobertura / NPE mediano)")
    t8rows = []
    for lab, rvs in (("test (49 clipes)", rv_test), ("train[::3] (19 clipes)", rv_train)):
        print(f"   {lab}")
        for line in t8(list(rvs.values())):
            print("     " + " | ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in line.items()))
            t8rows.append(dict(conjunto=lab, **line))
    write("T8_test_e_train3", t8rows)
    g_test, g_train = gap_classes(rv_test), gap_classes(rv_train)
    write("lacunas_4a25_test", g_test)
    write("lacunas_4a25_train3", g_train)
    write("lacunas_4a25_resumo", summarize_gaps(g_test, "test") + summarize_gaps(g_train, "train[::3]"))

    # conferência do NPE (erro de cálculo da tabela?): 30 frames de lacuna do test, NPE refeito da série guardada
    sample = [r for r in g_test if r["serie"] == "6a Bassek"][::max(1, len(g_test) // 60)][:30]
    worst = 0.0
    for r in sample:
        s = gsr.load_clip(path("gsr") / "test" / r["clipe"])[r["frame"]]
        H = res[r["clipe"]][3]["6a Bassek"][r["frame"]].astype(float)
        worst = max(worst, abs(npe_re(H, s.H_gt, s.size)[0] - r["npe"]) / max(r["npe"], 1e-9))
    print(f"\n   conferência do NPE: {len(sample)} frames de lacuna refeitos da série guardada (float32); maior diferença relativa {worst:.2e}")

    # 3 figuras: borda esquerda (detector), meio da lacuna (6a Bassek), borda direita (detector)
    picks, seen = [], set()
    for cls in ("bordas certas", "uma borda errada", "as duas bordas erradas", "bordas certas", "uma borda errada"):
        cand = sorted({(r["clipe"], r["a"], r["b"]) for r in g_test if r["classe"] == cls and r["serie"] == "6a Bassek" and r["npe"] > 0.5} - seen,
                      key=lambda x: -(x[2] - x[1]))
        if cand and len(picks) < 3:
            picks.append((cls, *cand[0]))
            seen.add(cand[0])
    fig_rows = []
    for cls, c, a, b in picks:
        samples = gsr.load_clip(path("gsr") / "test" / c)
        ser = dict(np.load(T._series_path(path("gsr") / "test" / c)))
        mid = (a + b) // 2
        H6 = res[c][3]["6a Bassek"][mid].astype(float)
        e = lambda H, s: npe_re(H, s.H_gt, s.size)[0] if s.H_gt is not None and np.isfinite(H).all() else np.nan
        pa, pm, pb = samples[a - 1], samples[mid], samples[b + 1]
        strip = np.hstack([panel(pa.image, ser["H"][a - 1], pa.lines_uv, f"{c} f{a - 1}: detector (borda) NPE {e(ser['H'][a - 1], pa):.3f}"),
                           panel(pm.image, H6, pm.lines_uv, f"f{mid}: 6a Bassek, lacuna {a}-{b} NPE {e(H6, pm):.3f}"),
                           panel(pb.image, ser["H"][b + 1], pb.lines_uv, f"f{b + 1}: detector (borda) NPE {e(ser['H'][b + 1], pb):.3f}")])
        fn = FIG / f"lacuna_{c}_{a}-{b}.jpg"
        cv2.imwrite(str(fn), strip, [cv2.IMWRITE_JPEG_QUALITY, 85])
        fig_rows.append(dict(classe=cls, clipe=c, lacuna=f"{a}-{b}", figura=str(fn)))
        print(f"   figura {fn}: classe '{cls}'")
    write("lacunas_figuras", fig_rows)

    # ---------------- 8.6: piores clipes do 6c
    from src.evaluate import locsim
    def pen(rows):
        n = sum(r.get("n_pessoas", 0) for r in rows)
        return sum(locsim(r["locsim_d"], 5).sum() for r in rows if "locsim_d" in r) / n if n else np.nan
    clip_rows = []
    for c, r in res.items():
        rv, anc = rv_test[c], r[2]
        acc = [a for a in anc if a["aceita"]]
        clip_rows.append(dict(clipe=c, jogo=rv["detector"][0]["jogo"], det=pen(rv["detector"]), c6=pen(rv["6c fluxo"]), teto=pen(rv["6c âncora de gabarito"]),
                              cob_det=np.mean([x["has_pred"] for x in rv["detector"] if x["has_gt"]]), cob_6c=np.mean([x["has_pred"] for x in rv["6c fluxo"] if x["has_gt"]]),
                              candidatas=len(anc), verificaveis=sum(a["verificavel"] for a in anc), aceitas=len(acc),
                              aceitas_erradas=sum(1 for a in acc if np.isfinite(a["npe"]) and a["npe"] > WRONG)))
    write("clipes_test", clip_rows)
    print("\n== 8.6. Piores clipes do 6c no test (LocSim@5 penalizado), com âncora")
    print("   clipe     jogo | detector | 6c    | teto  | cobertura 6c | âncoras cand/verif/aceitas/erradas")
    worst_clips = sorted([r for r in clip_rows if r["aceitas"]], key=lambda r: r["c6"])[:6]
    for r in worst_clips:
        print(f"   {r['clipe']}  {r['jogo']:>4} | {r['det']:.3f}    | {r['c6']:.3f} | {r['teto']:.3f} | {r['cob_6c']:.3f}        | "
              f"{r['candidatas']}/{r['verificaveis']}/{r['aceitas']}/{r['aceitas_erradas']}")
        rv = rv_test[r["clipe"]]
        e6 = [(x.get("npe", -1), i) for i, x in enumerate(rv["6c fluxo"]) if "npe" in x]
        if e6:
            npe_max, i = max(e6)
            s = gsr.load_clip(path("gsr") / "test" / r["clipe"])[i]
            H = res[r["clipe"]][3]["6c fluxo"][i].astype(float)
            cv2.imwrite(str(FIG / f"pior_6c_{r['clipe']}_f{i}.jpg"),
                        panel(s.image, H, s.lines_uv, f"{r['clipe']} f{i}: 6c fluxo, NPE {npe_max:.3f} (pior frame do clipe)", w=960), [cv2.IMWRITE_JPEG_QUALITY, 85])

    # ---------------- 8.6: deriva do 6c pela distância à âncora (pontas e lacunas longas)
    print("\n== 8.6. 6c fluxo: NPE mediano pela distância (frames) à âncora aceita mais próxima")
    drift = defaultdict(list)
    for c, r in res.items():
        acc = np.array([a["t"] for a in r[2] if a["aceita"]])
        if not len(acc):
            continue
        for i, x in enumerate(rv_test[c]["6c fluxo"]):
            if "npe" in x:
                d = int(np.min(np.abs(acc - i)))
                lac = rv_test[c]["detector"][i]["lacuna"]
                where = "pontas" if lac == -1 else "lacuna > 25" if lac > 25 else "lacuna 1-25" if lac > 0 else "detector com H"
                drift[(where, 0 if d <= 25 else 1 if d <= 100 else 2 if d <= 250 else 3)].append(x["npe"])
    drows = []
    for where in ("detector com H", "lacuna 1-25", "lacuna > 25", "pontas"):
        cells = []
        for b, lab in enumerate(("<= 25", "26-100", "101-250", "> 250")):
            e = drift.get((where, b), [])
            cells.append(f"{lab}: {np.median(e):.4f} ({len(e)})" if e else f"{lab}: — (0)")
            drows.append(dict(onde=where, distancia=lab, frames=len(e), npe_med=float(np.median(e)) if e else np.nan,
                              erradas=float(np.mean(np.array(e) > WRONG)) if e else np.nan))
        print(f"   {where:15} | " + " | ".join(cells))
    write("deriva_6c", drows)

    # ---------------- 8.6: as âncoras erradas aceitas, com o tipo
    print("\n== 8.6. Âncoras aceitas erradas (NPE > 0,05) no test")
    arows = []
    for c, r in res.items():
        for a in r[2]:
            if a["aceita"] and np.isfinite(a["npe"]) and a["npe"] > WRONG:
                samples = gsr.load_clip(path("gsr") / "test" / c)
                ser = dict(np.load(T._series_path(path("gsr") / "test" / c)))
                s, Hd = samples[a["t"]], ser["H"][a["t"]]
                M = np.linalg.inv(s.H_gt) @ Hd
                M = M / M[2, 2]
                typ, Q = error_type(M)
                cv2.imwrite(str(FIG / f"ancora_errada_{c}_f{a['t']}.jpg"),
                            panel(s.image, Hd, s.lines_uv, f"{c} f{a['t']}: âncora aceita, NPE {a['npe']:.3f}", w=960), [cv2.IMWRITE_JPEG_QUALITY, 85])
                top_view(M, FIG / f"ancora_errada_{c}_f{a['t']}_campo.png")
                arows.append(dict(clipe=c, frame=a["t"], npe=a["npe"], tipo_heuristico=typ, centro_vai_para=f"({Q[0, 0]:.1f}, {Q[0, 1]:.1f})",
                                  penalti_esq_vai_para=f"({Q[5, 0]:.1f}, {Q[5, 1]:.1f})", penalti_dir_vai_para=f"({Q[6, 0]:.1f}, {Q[6, 1]:.1f})"))
                print(f"   {c} f{a['t']:<4} NPE {a['npe']:.3f} | {typ} | centro -> ({Q[0, 0]:.1f}, {Q[0, 1]:.1f}), pênaltis -> "
                      f"({Q[5, 0]:.1f}, {Q[5, 1]:.1f}) e ({Q[6, 0]:.1f}, {Q[6, 1]:.1f})")
    write("ancoras_erradas_test", arows)

    # ---------------- 8.6: clipes sem âncora x limitações da Fatia 3 (diagnóstico da segmentação)
    with SafeProcessPool(15) as ex:
        diag = [x for rs in ex.map(seg_diag, test) if rs is not None for x in rs]
    write("segmentacao_test_diag", diag)
    no_anchor = sorted(r["clipe"] for r in clip_rows if not r["aceitas"])
    game = {r["clipe"]: r["jogo"] for r in clip_rows}
    agg = lambda rs: {k: float(np.nanmedian([x[k] for x in rs])) for k in ("campo_grama", "vazamento", "cobertura_2px", "resposta_mediana", "acima_limiar")} | \
        dict(sombra=float(np.mean([x["sombra"] for x in rs])), frames=len(rs))
    print("\n== 8.6. Clipes sem âncora aceita x limitações da segmentação (Fatia 3); medianas por frame, 1 a cada 75")
    print("   conjunto                       | frames | campo como grama | vazamento | cobertura 2 px | resposta mediana (L*) | acima do limiar 30 | sombra")
    srows = []
    groups = [(f"sem âncora: {c} (jogo {game[c]})", [x for x in diag if x["clipe"] == c]) for c in no_anchor] + \
             [(f"com âncora, jogo {g}", [x for x in diag if game[x["clipe"]] == g and x["clipe"] not in no_anchor]) for g in sorted(set(game.values()), key=int)]
    for lab, rs in groups:
        if not rs:
            print(f"   {lab:30} | sem frame com H_gt e linhas anotadas")
            continue
        m = agg(rs)
        print(f"   {lab:30} | {m['frames']:6} | {m['campo_grama']:.3f}            | {m['vazamento']:.3f}     | {m['cobertura_2px']:.3f}          | "
              f"{m['resposta_mediana']:5.1f}                 | {m['acima_limiar']:.2f}               | {m['sombra']:.2f}")
        srows.append(dict(conjunto=lab, **m))
    write("sem_ancora_x_fatia3", srows)
    print("   referência (Fatia 3, GSR train, 1.697 frames): campo como grama 0,994; cobertura 2 px 0,79 (mediana 0,89); "
          "resposta mediana nos pontos 36 / 74 / 81 nos jogos 4 / 6 / 9, fração acima de 30: 0,64 / 0,92 / 0,92")
    for c in no_anchor:                                             # uma folha por clipe: gramado e marcações
        from src.segment import debug_overlay, grass_mask, line_mask, params
        s = gsr.load_clip(path("gsr") / "test" / c)[375]
        P = params("gsr")
        g = grass_mask(s.image, P)
        cv2.imwrite(str(FIG / f"sem_ancora_{c}_f375.jpg"),
                    np.hstack([panel(s.image, s.H_gt, s.lines_uv, f"{c} f375: H_gt e pontos anotados", w=800),
                               cv2.resize(debug_overlay(s.image, g, line_mask(s.image, g, P)), (800, 450))]), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"\nCSVs em {OUT}; figuras em {FIG}")
    exit_if_failed()
