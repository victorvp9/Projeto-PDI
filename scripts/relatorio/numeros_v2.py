"""Números do adendo v2 (docs/04-relatorio-v2.md): cada número do texto com a origem, conferido, no estilo de
scripts/relatorio/numeros.py (de onde vêm o parser, a conferência de CSV, texto e conta e a completude).

- Entradas: C (célula de CSV), X (linha de documento), D (conta sobre outras entradas) e J (valor de JSON).
- As tabelas do adendo ficam entre <!-- gerado: nome --> e <!-- fim: nome --> e são geradas aqui, dos CSVs das
  rodadas do test do v1 (outputs/runs/rodada_test/) e do v2 (outputs/runs_v2/rodada_test_v2/) e dos decisao.json
  do ciclo (outputs/runs_v2/*/); o texto do adendo tem que trazê-las tal como geradas.
- Completude: todo número do corpo, fora das tabelas geradas e dos blocos de código, tem uma entrada. Ficam de fora
  os identificadores, como no v1, mais datas e listas de jogos.

Uso (da raiz, PYTHONPATH=.): numeros_v2.py [--escrever]. Sem a opção, só confere (código 1 se algo falhar); com
ela, grava as tabelas no adendo e o docs/04-relatorio-v2-numeros.md."""
import ast
import csv
import json
import math
import re
import sys
from pathlib import Path

from scripts.relatorio import numeros as N

REL = Path("docs/04-relatorio-v2.md")
OUT_MD = Path("docs/04-relatorio-v2-numeros.md")
T1D, T2D = "outputs/runs/rodada_test/tabelas", "outputs/runs_v2/rodada_test_v2/tabelas"
R2, RV2 = "outputs/runs_v2/rodada_test_v2", "outputs/runs_v2"
CL1, CL2 = "outputs/runs/rodada_test/falhas/clipes_test.csv", f"{R2}/clipes_test_v2.csv"
PI, PV, HSB = f"{R2}/pioras.csv", f"{R2}/pioras_vizinhos.csv", "data_splits/hsb.csv"
B134 = "outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv"
DEC, PL2, CFG2, P0, V2OUT = "docs/decisoes.md", "docs/05-melhorias-plano.md", "config_v2.yaml", "docs/00-problema.md", "outputs/runs/rodada_test/tabelas_v2.out"
V1_SEM = ["SNGS-127", "SNGS-128", "SNGS-134", "SNGS-138", "SNGS-147"]
N.IGNORE[:0] = [r"\b\d{4}-\d{2}-\d{2}\b", r"\bjogos? \d+(?:, \d+)*(?: e \d+)?"]   # datas e listas de jogos: identificadores

NUMEROS = []


def _src(s):
    return f"{T1D}/{s[3:]}.csv" if s.startswith("v1:") else f"{T2D}/{s[3:]}.csv" if s.startswith("v2:") else s


def C(txt, desc, src, sel, col, esc=1, key=None, sec=""):
    NUMEROS.append(dict(tipo="csv", txt=txt, desc=desc, src=_src(src), sel=sel, col=col, esc=esc, key=key, sec=sec))


def X(txt, desc, src, anchor, key=None, sec=""):
    NUMEROS.append(dict(tipo="txt", txt=txt, desc=desc, src=src, anchor=anchor, key=key, sec=sec))


def D(txt, desc, expr, fn, key=None, sec=""):
    NUMEROS.append(dict(tipo="der", txt=txt, desc=desc, expr=expr, fn=fn, key=key, sec=sec))


def J(txt, desc, src, path, esc=1, key=None, sec=""):
    """Valor de JSON: `path` é a sequência de chaves."""
    NUMEROS.append(dict(tipo="json", txt=txt, desc=desc, src=src, path=path, esc=esc, key=key, sec=sec))


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


# ------------------------------------------------------------------ 1. ressalvas
C("5", "clipes do test sem âncora aceita, v1", "v1:T7", {"conjunto": "clipes sem âncora aceita"}, "n", sec="1, 3.6")
C("0", "clipes do test sem âncora aceita, v2", "v2:T7", {"conjunto": "clipes sem âncora aceita"}, "n", sec="1, 3.6")
C("0,902", "LocSim@5 penalizado da propagação, v2", "v2:T1", {"serie": "6c fluxo"}, "locsim_pen", key="c6_2", sec="1, 3, 4")
X("4", "critério do plano: ganho em >= 4 de 6 jogos", DEC, "**D1, aceite:** ganho em ≥ 4 dos 6 jogos", sec="1, 2")
X("6", "critério do plano: 6 jogos de dev", DEC, "**D1, aceite:** ganho em ≥ 4 dos 6 jogos", sec="1, 2")
X("−0,03", "critério do plano: nenhum jogo abaixo de −0,03", DEC, "**D2, queda máxima num jogo:** −0,03", sec="1")
AC = f"{RV2}/a_central/decisao.json"
J("5", "A': jogos com Δ > 0 (critério antigo)", AC, ("decisao", "jogos_com_ganho"), sec="1")
J("6", "A': jogos com Δ >= 0 (critério novo)", AC, ("decisao", "jogos_sem_perda"), sec="2")
J("+0,178", "A': média dos Δ por jogo", AC, ("decisao", "media"), sec="1")
J("0", "A': pior Δ (o jogo 3, Δ = 0)", AC, ("decisao", "pior"), sec="1")
D("49", "clipes do GSR test", f"linhas de {CL2}", lambda v: len(rows(CL2)), sec="1, 3.7")
C("1,000", "cobertura da propagação, v2", "v2:T1", {"serie": "6c fluxo"}, "cobertura", sec="1, 3.1")

# ------------------------------------------------------------------ 2. ciclo
X("6", "dev: 6 jogos", PL2, "ou seja, **6 jogos**", sec="2")
B1 = f"{RV2}/b1_regra/decisao.json"
J("5", "B1: jogos com Δ > 0 na leitura leave-one-game-out", B1, ("logo_jogo9", "decisao", "jogos_com_ganho"), sec="2")
J("1", "C: jogos com Δ > 0", f"{RV2}/c_bidirecional/decisao.json", ("decisao", "jogos_com_ganho"), key="c_ganho", sec="2")
D("5", "C: jogos em que piorou (6 − jogos com ganho; nenhum com Δ = 0)", "6 − 1", lambda v: 6 - v["c_ganho"], sec="2")
X("3", "B2: jogos com Δ = 0", DEC, "com Δ = 0 em 3 dos 6 jogos", sec="2")
X("3", "A: H novas no jogo 3, todas erradas", DEC, "3 H novas, as 3 erradas", sec="2")
X("20", "A': contagem mínima de H novas por jogo na regra de parada", DEC, "**com pelo menos 20 H novas**", sec="2")
X("59", "A': clipes da metade fixa", DEC, "59 clipes, de 9 a 11 por jogo", sec="2")
X("4", "B1b: clipes que a regra mexe", DEC, "restrita a 4 clipes de 2 jogos", sec="2")
X("2", "B1b: jogos que a regra mexe", DEC, "restrita a 4 clipes de 2 jogos", sec="2")

# ------------------------------------------------------------------ 3.1 test inteiro
for s, cols in (("detector", (("0,419", "0,624", "locsim_pen"), ("0,505", "0,702", "cobertura"))),
                ("6c fluxo", (("0,749", None, "locsim_pen"), ("0,897", None, "cobertura"), ("0,959", "0,959", "fracao_teto"))),
                ("6c âncora de gabarito", (("0,763", "0,914", "locsim_pen"),))):
    for t1, t2, col in cols:
        C(t1, f"{col} de {s}, v1", "v1:T1", {"serie": s}, col, key={("6c fluxo", "locsim_pen"): "c6_1"}.get((s, col)), sec="3.1")
        if t2:
            C(t2, f"{col} de {s}, v2", "v2:T1", {"serie": s}, col, sec="3.1")
X("1", "conferência contra o v1 a 1 frame em 25", "scripts/v2/rodada_test_v2/confere_v1_test.py", "as H do detector v1 a 1 frame em 25", sec="3.1, 3.7")
X("25", "conferência contra o v1 a 1 frame em 25", "scripts/v2/rodada_test_v2/confere_v1_test.py", "as H do detector v1 a 1 frame em 25", sec="3.1, 3.7")
J("722", "H do v1 idênticas bit a bit na série do v2", f"{R2}/conferencia_v1.json", ("iguais_bit_a_bit",), sec="3.1")
J("290", "H novas no v2 (frames sem H no v1)", f"{R2}/conferencia_v1.json", ("novas_no_v2",), sec="3.1")

# ------------------------------------------------------------------ 3.2 por jogo
for jogo, a, b in (("7", "0,676", "0,914"), ("8", "0,650", "0,839"), ("11", "0,920", "0,956")):
    C(a, f"LocSim@5 pen. da propagação, jogo {jogo}, v1", "v2:T6", {"jogo": jogo}, "v1_locsim_pen_6c", sec="3.2")
    C(b, f"LocSim@5 pen. da propagação, jogo {jogo}, v2", "v2:T6", {"jogo": jogo}, "locsim_pen_6c", sec="3.2")
C("0,954", "LocSim@5 pen. do teto condicionado, jogo 11, v2", "v2:T6", {"jogo": "11"}, "locsim_pen_teto", sec="3.2")
C("0,946", "H_gt pelas linhas como predição: LocSim@5 nos frames com gabarito (análise posterior do v1)", B134,
  {"conjunto": "test inteiro", "serie": "H_gt pelas linhas"}, "locsim_cob", sec="3.2")

# ------------------------------------------------------------------ 3.3 conjunto comum
C("18.133", "frames do conjunto comum, v1", "v1:T1b", {"serie": "detector"}, "frames", sec="3.3")
C("25.382", "frames do conjunto comum, v2", "v2:T1b", {"serie": "detector"}, "frames", sec="3.3")
C("0,926", "LocSim@5 pen. da propagação no conjunto comum, v2", "v2:T1b", {"serie": "6c fluxo"}, "locsim_pen", sec="3.3, 3.5")
C("0,882", "LocSim@5 pen. do detector no conjunto comum, v2", "v2:T1b", {"serie": "detector"}, "locsim_pen", sec="3.3")

# ------------------------------------------------------------------ 3.4 HSB
T2A = {"clipe": "todos"}
for t, v, col, esc in (("61,7", "v1", "(3) pipeline pen média", 100), ("74,5", "v2", "(3) pipeline pen média", 100),
                       ("71,1", "v1", "(3) pipeline pen mediana", 100), ("81,9", "v2", "(3) pipeline pen mediana", 100),
                       ("0,829", "v1", "(3) pipeline cobertura frames com pessoas", 1), ("1,000", "v2", "(3) pipeline cobertura frames com pessoas", 1),
                       ("81,4", "v2", "(1) só propagação pen média", 100)):
    C(t, f"HSB, {col}, {v}", f"{v}:T2", T2A, col, esc, sec="3.4, 4")
X("83,67", "AuxFlow no HSB, média (tabela 4 deles)", P0, "de 83,67 para 23,42", sec="3.4, 4")
X("96,15", "AuxFlow no HSB, mediana (tabela 4 deles)", V2OUT, "AuxFlow (83.67, 96.15)", sec="3.4")
for c, a, b in (("SNGS-136", "85,7", "72,6"), ("SNGS-123", "59,1", "45,7"), ("SNGS-124", "70,3", "61,9"), ("SNGS-150", "56,7", "56,2")):
    C(a, f"HSB, pipeline, média, {c}, v1", "v1:T2", {"clipe": c}, "(3) pipeline pen média", 100, sec="3.4")
    C(b, f"HSB, pipeline, média, {c}, v2", "v2:T2", {"clipe": c}, "(3) pipeline pen média", 100, sec="3.4")

# ------------------------------------------------------------------ 3.5 AuxFlow e 4
C("0,929", "LocSim@5 do AuxFlow, tabela 7 dele", "v2:T5", {"linha": "AuxFlow (tab. 7)"}, "locsim5", key="aux", sec="3.5, 4")
C("0,885", "LocSim@5 do NBJW, tabela 7 do AuxFlow", "v2:T5", {"linha": "NBJW (AuxFlow, tab. 7)"}, "locsim5", key="nbjw", sec="3.5, 4")
D("0,027", "AuxFlow − propagação do v2", "0,929 − 0,902", lambda v: v["aux"] - v["c6_2"], sec="3.5")
D("0,017", "propagação do v2 − NBJW", "0,902 − 0,885", lambda v: v["c6_2"] - v["nbjw"], sec="3.5")
D("85", "fração da distância entre a propagação do v1 e o AuxFlow fechada pelo v2 (%)", "(0,902 − 0,749) / (0,929 − 0,749)",
  lambda v: 100 * (v["c6_2"] - v["c6_1"]) / (v["aux"] - v["c6_1"]), sec="3.5, 4")

# ------------------------------------------------------------------ 3.6 âncoras e lacunas
for t1, t2, conj, col in (("958", "1.193", "candidatas", "n"), ("558", "765", "aceitas", "n"), ("12", "11", "aceitas", "erradas")):
    C(t1, f"âncoras {conj} ({col}), v1", "v1:T7", {"conjunto": conj}, col, sec="3.6")
    C(t2, f"âncoras {conj} ({col}), v2", "v2:T7", {"conjunto": conj}, col, sec="3.6")
C("557", "aceitas com gabarito, v1", "v1:T7", {"conjunto": "aceitas"}, "com_gabarito", key="g1", sec="—")
C("759", "aceitas com gabarito, v2", "v2:T7", {"conjunto": "aceitas"}, "com_gabarito", key="g2", sec="—")
D("2,2", "aceitas erradas entre as com gabarito, v1 (%)", "12 / 557", lambda v: 100 * 12 / v["g1"], sec="3.6")
D("1,4", "aceitas erradas entre as com gabarito, v2 (%)", "11 / 759", lambda v: 100 * 11 / v["g2"], sec="3.6")
S5 = lambda: [r for r in rows(CL2) if r["clipe"] in V1_SEM]
D("0,035", "maior NPE das âncoras do v2 nos 5 clipes sem âncora do v1", f"máx. de npe_aceitas em {CL2}",
  lambda v: max(max(ast.literal_eval(r["npe_aceitas"])) for r in S5()), sec="3.6")
X("0,05", "limiar de âncora errada (NPE > 0,05)", "scripts/v2/rodada_test_v2/confere_v1_6c.py", "TOL, WRONG = 1e-9, 0.05", sec="3.6")
D("0,69", "menor LocSim@5 pen. da propagação, v2, nos 4 sem âncora do v1 fora o SNGS-147", f"mín. de c6 em {CL2}",
  lambda v: min(float(r["c6"]) for r in S5() if r["clipe"] != "SNGS-147"), sec="3.6")
D("0,92", "maior LocSim@5 pen. da propagação, v2, nos 4 sem âncora do v1 fora o SNGS-147", f"máx. de c6 em {CL2}",
  lambda v: max(float(r["c6"]) for r in S5() if r["clipe"] != "SNGS-147"), sec="3.6")
C("1", "âncoras do v2 no SNGS-147", CL2, {"clipe": "SNGS-147"}, "aceitas", sec="3.6")
C("0,205", "LocSim@5 pen. da propagação no SNGS-147, v2", CL2, {"clipe": "SNGS-147"}, "c6", sec="3.6")

# ------------------------------------------------------------------ 3.7 pioras
DC = lambda: [float(r["d_c6"]) for r in rows(CL2)]
D("36", "clipes que melhoram (Δ > 0)", f"contagem em {CL2}", lambda v: sum(d > 0 for d in DC()), sec="3.7")
D("8", "clipes iguais (Δ = 0)", f"contagem em {CL2}", lambda v: sum(d == 0 for d in DC()), sec="3.7")
D("5", "clipes que pioram (Δ < 0)", f"contagem em {CL2}", lambda v: sum(d < 0 for d in DC()), sec="3.7")
D("0,008", "os três que pioram menos pioram menos que isto", "|Δ| dos três menores < 0,008",
  lambda v: 0.008 if sorted(-d for d in DC() if d < 0)[:3][-1] < 0.008 else math.nan, sec="3.7")
D("0,06", "os dois do HSB pioram cerca disto (|Δ| arredondado)", "|Δ| do SNGS-136 e do SNGS-123",
  lambda v: 0.06 if all(round(-float(r["d_c6"]), 2) == 0.06 for r in rows(CL2) if r["clipe"] in ("SNGS-136", "SNGS-123")) else math.nan, sec="3.7")
for c, cols in (("SNGS-136", (("0,883", "v1_teto"), ("0,933", "teto"), ("0,893", "v1_c6"), ("0,832", "c6"), ("21", "aceitas"), ("21", "v1_aceitas"))),
                ("SNGS-123", (("0,868", "v1_teto"), ("0,819", "teto")))):
    for t, col in cols:
        C(t, f"{c}: {col}", CL2, {"clipe": c}, col, sec="3.7")
for c, fr, t, col in (("SNGS-136", "39", "0,0198", "npe"), ("SNGS-136", "110", "0,0317", "npe"), ("SNGS-136", "90", "1,63", "nota"),
                      ("SNGS-136", "39", "1,65", "nota"), ("SNGS-136", "189", "0,0058", "npe"), ("SNGS-136", "9", "0,0204", "npe"),
                      ("SNGS-136", "234", "1,575", "nota"), ("SNGS-136", "189", "1,595", "nota"),
                      ("SNGS-123", "51", "0,043", "npe"), ("SNGS-123", "93", "0,0127", "npe"), ("SNGS-123", "195", "0,0049", "npe"),
                      ("SNGS-123", "132", "0,094", "npe"), ("SNGS-123", "153", "0,064", "npe")):
    C(t, f"{c}, candidata f{fr}: {col}", PI, {"clipe": c, "frame": fr}, col, sec="3.7")
for fr, t, d in (("39", "0,020", "menor NPE das aceitas até a f110"), ("110", "0,032", "maior NPE das aceitas até a f110"),
                 ("189", "0,006", "menor NPE das recusadas pelo B1"), ("9", "0,020", "maior NPE das recusadas pelo B1")):
    C(t, f"SNGS-136, f{fr}: {d} (limitações, 3 casas)", PI, {"clipe": "SNGS-136", "frame": fr}, "npe", sec="5")
for c, a, b in (("SNGS-136", "60", "280"), ("SNGS-123", "100", "200")):
    C(a, f"{c}: início do intervalo do HSB", HSB, {"clipe": c}, "inicio", sec="3.7")
    C(b, f"{c}: fim do intervalo do HSB", HSB, {"clipe": c}, "fim", sec="3.7")
X("10", "janela de voto da verificação (±10 frames)", CFG2, "verify_window: 10", sec="3.7")
for cand, viz in (("93", "100"), ("195", "200")):
    C("0", f"SNGS-123, vizinho f{viz} da candidata f{cand}: sem H no v1 (False = 0)", PV, {"clipe": "SNGS-123", "candidata": cand, "vizinho": viz},
      "v1_tem_H", sec="3.7")
    C("1", f"SNGS-123, vizinho f{viz} da candidata f{cand}: com H no v2 (True = 1)", PV, {"clipe": "SNGS-123", "candidata": cand, "vizinho": viz},
      "v2_tem_H", sec="3.7")


# ------------------------------------------------------------------ conferência
def resolve(e, values):
    if e["tipo"] == "json":
        x = json.loads(Path(e["src"]).read_text(encoding="utf-8"))
        for k in e["path"]:
            x = x[k]
        val, dec = N.parse(e["txt"])
        ok = math.isclose(round(float(x) * e["esc"], dec), val, abs_tol=1e-9)
        if e["key"]:
            values[e["key"]] = float(x)
        return ok, None, " → ".join(e["path"]), f"{x}", "" if ok else f"JSON dá {x}"
    if e["tipo"] == "csv":                                     # booleanos do CSV (True/False) viram 1/0
        L = N._lines(e["src"])
        N._cache[e["src"]] = [L[0]] + [re.sub(r"(?<=,)True(?=,|$)", "1", re.sub(r"(?<=,)False(?=,|$)", "0", s)) for s in L[1:]]
    return N.resolve(e, values)


# ------------------------------------------------------------------ tabelas geradas
f, table, n = N.f, N.table, N.n
ar = lambda a, b, d=3, pct=False: f"{f(a, d, pct)} → {f(b, d, pct)}"
sg = lambda x, d=4: ("+" if float(x) > 0 else "") + f(x, d)


def tabelas():
    out = {}
    hip = (("B1", "limiar de nota da âncora", "dev, leave-one-game-out", "antigo", "b1_regra", ("logo_jogo9", "decisao")),
           ("C", "propagação bidirecional entre âncoras", "dev", "antigo", "c_bidirecional", ("decisao",)),
           ("B2", "centro da câmera da âncora", "dev, leave-one-game-out", "antigo", "b2_centro", ("decisao_logo",)),
           ("B1b", "recupera a melhor candidata recusada pelo B1", "dev (4 clipes recalculados)", "antigo", "b1b", ("decisao",)),
           ("A'", "vista central em forma fechada, com filtro da elipse", "dev, metade fixa", "novo", "a_central", ("decisao",)))
    rs = []
    for h, o, onde, crit, d, path in hip:
        x = json.loads(Path(f"{RV2}/{d}/decisao.json").read_text(encoding="utf-8"))
        for k in path:
            x = x[k]
        rs.append([h, o, onde, crit, str(x["jogos_com_ganho"]), str(x.get("jogos_sem_perda", "—")), sg(x["media"]), sg(x["pior"]),
                   "aceita" if x["aceita"] else "recusada"])
    out["ciclo"] = table(["Hipótese", "O que muda", "Medida em", "Critério", "Jogos com Δ > 0", "Jogos com Δ ≥ 0", "Média dos Δ", "Pior Δ", "Decisão"], rs,
                         "Tabela 1 — O ciclo v2 no dev: LocSim@5 penalizado da propagação, Δ por jogo contra a base de cada hipótese "
                         "(`outputs/runs_v2/<hipótese>/decisao.json`). O A, antes do A', parou na checagem barata e não tem confirmação.")
    v1, v2 = {r["serie"]: r for r in rows(f"{T1D}/T1.csv")}, {r["serie"]: r for r in rows(f"{T2D}/T1.csv")}
    out["t1"] = table(["Série", "Cobertura", "LocSim@5 penalizado", "Nos cobertos", "NPE mediano", "Fração ao teto"],
                      [[n(s), ar(v1[s]["cobertura"], v2[s]["cobertura"]), ar(v1[s]["locsim_pen"], v2[s]["locsim_pen"]),
                        ar(v1[s]["locsim_cob"], v2[s]["locsim_cob"]), ar(v1[s]["npe_med"], v2[s]["npe_med"], 4),
                        ar(v1[s]["fracao_teto"], v2[s]["fracao_teto"])] for s in v2],
                      "Tabela 2 — GSR test, 49 clipes, v1 → v2 (T1 das duas rodadas). O teto condicionado às âncoras é a propagação a partir "
                      "da homografia de gabarito nos frames das âncoras aceitas; a fração ao teto é (série − detector) / (teto − detector).")
    out["t6"] = table(["Jogo", "Clipes", "Com âncora", "Cobertura: detector", "Cobertura: propagação", "LocSim@5 pen.: detector", "LocSim@5 pen.: propagação",
                       "LocSim@5 pen.: teto condicionado"],
                      [[r["jogo"], r["clipes"], f"{int(float(r['v1_com_ancora']))} → {r['com_ancora']}", ar(r["v1_cob_detector"], r["cob_detector"]),
                        ar(r["v1_cob_6c"], r["cob_6c"]), ar(r["v1_locsim_pen_detector"], r["locsim_pen_detector"]),
                        ar(r["v1_locsim_pen_6c"], r["locsim_pen_6c"]), ar(r["v1_locsim_pen_teto"], r["locsim_pen_teto"])] for r in rows(f"{T2D}/T6.csv")],
                      "Tabela 3 — GSR test por jogo, v1 → v2 (T6 do v2, com as colunas do v1).")
    b1, b2 = {r["serie"]: r for r in rows(f"{T1D}/T1b.csv")}, {r["serie"]: r for r in rows(f"{T2D}/T1b.csv")}
    out["t1b"] = table(["Série", f"NPE mediano: v1 / v2", "LocSim@5 pen.: v1", "LocSim@5 pen.: v2"],
                       [[n(s), f"{f(b1[s]['npe_med'], 4)} / {f(b2[s]['npe_med'], 4)}", f(b1[s]["locsim_pen"]), f(b2[s]["locsim_pen"])] for s in b2],
                       f"Tabela 4 — Conjunto comum: os frames com homografia do detector de cada versão, {N.milhar(b1['detector']['frames'])} no v1 e "
                       f"{N.milhar(b2['detector']['frames'])} no v2 (T1b). As colunas não são do mesmo conjunto de frames.")
    agg = lambda p: {k: v for r in rows(p) if r["clipe"] == "todos" for k, v in r.items() if v != ""}
    a1, a2 = agg(f"{T1D}/T2.csv"), agg(f"{T2D}/T2.csv")
    out["t2"] = table(["Medição", "Média (%)", "Mediana (%)", "Cobertura (frames com pessoas)"],
                      [[m, ar(a1[f"{m} pen média"], a2[f"{m} pen média"], 1, True), ar(a1[f"{m} pen mediana"], a2[f"{m} pen mediana"], 1, True),
                        ar(a1[f"{m} cobertura frames com pessoas"], a2[f"{m} cobertura frames com pessoas"])]
                       for m in ("(1) só propagação", "(2) detector", "(3) pipeline")],
                      "Tabela 5 — HSB, LocSim@5 por frame, penalizado, v1 → v2 (T2). A medição (1) começa da `H_gt_auxflow` e não depende do "
                      "detector. AuxFlow, tabela 4 deles (média / mediana): NBJW 43,15 / 35,93; AuxFlow 83,67 / 96,15.")
    c1 = {r["clipe"]: r for r in rows(f"{T1D}/T2.csv") if r["clipe"] != "todos"}
    out["t2clipes"] = table(["Clipe", "Intervalo", "(2) detector (%)", "(3) pipeline (%)"],
                            [[r["clipe"], f"{r['inicio']}–{r['fim']}", ar(c1[r["clipe"]]["(2) detector pen média"], r["(2) detector pen média"], 1, True),
                              ar(c1[r["clipe"]]["(3) pipeline pen média"], r["(3) pipeline pen média"], 1, True)]
                             for r in rows(f"{T2D}/T2.csv") if r["clipe"] != "todos"],
                            "Tabela 6 — HSB por clipe, média por frame, penalizada, v1 → v2 (T2). Os intervalos seguem a numeração do artigo do "
                            "AuxFlow, a partir de 0.")
    t51, t52 = {r["linha"]: r for r in rows(f"{T1D}/T5.csv")}, {r["linha"]: r for r in rows(f"{T2D}/T5.csv")}
    lin = {"nosso detector": "nosso detector", "nosso 6c fluxo": "nossa propagação", "ganho 6c - detector": "ganho propagação − detector"}
    rs = [[r["linha"].replace(" - ", " − "), f(r["locsim5"]), "—", "—"] for k, r in t52.items() if r["locsim5"]]
    rs += [[lin[k], ar(t51[k]["pen"], r["pen"]), ar(t51[k]["cob"], r["cob"]), ar(t51[k]["comum"], r["comum"]) if r["comum"] else "—"]
           for k, r in t52.items() if not r["locsim5"]]
    out["t5"] = table(["Linha", "LocSim@5 (penalizado, no nosso caso)", "Nos cobertos", "Conjunto comum"], rs,
                      "Tabela 7 — Comparação com a tabela 7 do AuxFlow, v1 → v2 (T5). Comparação indicativa (Seção 1); o conjunto comum é "
                      "o de cada versão (Tabela 4).")
    s1, s2 = {r["conjunto"]: r for r in rows(f"{T1D}/T7.csv")}, {r["conjunto"]: r for r in rows(f"{T2D}/T7.csv")}
    out["t7"] = table(["Conjunto", "v1", "v2", "Erradas (NPE > 0,05): v1 → v2"],
                      [[k, N.milhar(s1[k]["n"]), N.milhar(r["n"]), f"{s1[k]['erradas']} → {r['erradas']}" if r["erradas"] else "—"] for k, r in s2.items()],
                      "Tabela 8 — Âncoras no GSR test (T7).")
    l1 = {r["lacuna"]: r for r in rows(f"{T1D}/T8.csv")}
    out["t8"] = table(["Lacuna do detector", "Frames", "Propagação: cobertura", "Propagação: NPE mediano", "S-G (Bassek): NPE mediano"],
                      [[r["lacuna"].replace("-", "–"), f"{N.milhar(l1[k]['frames'])} → {N.milhar(r['frames'])}", ar(l1[k]["6c fluxo cob"], r["6c fluxo cob"]),
                        ar(l1[k]["6c fluxo NPE"], r["6c fluxo NPE"], 4), ar(l1[k]["6a Bassek NPE"], r["6a Bassek NPE"], 4)]
                       for k, r in ((r["lacuna"], r) for r in rows(f"{T2D}/T8.csv"))],
                      "Tabela 9 — Lacunas do detector no GSR test, v1 → v2 (T8). As lacunas são as do detector de cada versão: a comparação "
                      "por faixa é entre conjuntos de frames diferentes. As pontas tocam o começo ou o fim do clipe.")
    cl2 = {r["clipe"]: r for r in rows(CL2)}
    rs = []
    for c in V1_SEM:
        r, npe = cl2[c], ast.literal_eval(cl2[c]["npe_aceitas"])
        faixa = f(npe[0], 4) if len(npe) == 1 else f"{f(min(npe), 4)}–{f(max(npe), 4)}"
        rs.append([c, r["jogo"], r["aceitas"], faixa, str(r["aceitas_erradas"]), ar(r["v1_c6"], r["c6"]), f(r["teto"])])
    out["sem_ancora"] = table(["Clipe", "Jogo", "Âncoras no v2", "NPE das âncoras", "Erradas", "Propagação: v1 → v2", "Teto condicionado, v2"], rs,
                              f"Tabela 10 — Os 5 clipes sem âncora do v1 (`{CL2}`).")
    pr = sorted((r for r in rows(CL2) if float(r["d_c6"]) < 0), key=lambda r: float(r["d_c6"]))
    out["pioram"] = table(["Clipe", "Jogo", "Aceitas: v1 → v2", "Propagação: v1 → v2", "Δ", "Teto condicionado: v1 → v2"],
                          [[r["clipe"], r["jogo"], f"{r['v1_aceitas']} → {r['aceitas']}", ar(r["v1_c6"], r["c6"]), sg(r["d_c6"]), ar(r["v1_teto"], r["teto"])]
                           for r in pr],
                          f"Tabela 11 — Os clipes que pioram do v1 para o v2 (`{CL2}`).")
    fim = {r["clipe"]: int(r["fim"]) for r in rows(HSB)}
    rs = []
    for c in ("SNGS-136", "SNGS-123"):
        cand = [r for r in rows(PI) if r["clipe"] == c]
        stop = min(int(r["frame"]) for r in cand if r["situacao"] == "aceita" and int(r["frame"]) > fim[c])
        rs += [[c, f"f{r['frame']}", r["situacao"], f(r["npe"], 4), f(r["nota"], 4)] for r in cand if int(r["frame"]) <= stop]
    out["candidatas"] = table(["Clipe", "Candidata", "Situação", "NPE", "Nota (iou + img)"], rs,
                              f"Tabela 12 — Candidatas a âncora do SNGS-136 e do SNGS-123 até a primeira aceita depois do intervalo do HSB (`{PI}`). "
                              f"Situação: aceita; B1 (nota abaixo do limiar, `{CFG2}`: `temporal.anchor_min_nota`); maioria (passa na nota e cai na "
                              "verificação por maioria). Errada = NPE > 0,05.")
    return {k: v.rstrip() + "\n" for k, v in out.items()}


BLOCK = r"(<!-- gerado: {0} -->\n)(.*?)(<!-- fim: {0} -->)"


def numeros_md(res):
    head = ("# Números do adendo v2 e a origem de cada um\n\n"
            "Gerado por `scripts/relatorio/numeros_v2.py`, que confere cada linha: o valor da origem, arredondado às casas do texto, tem que ser "
            "o número do texto. Nas origens em CSV, a linha conta o cabeçalho como linha 1 (booleanos: True = 1, False = 0); nas origens em "
            "texto, a linha é a do arquivo; nas em JSON, a coluna diz o caminho das chaves; as contas (derivados) dizem a expressão. A "
            "completude também é conferida: todo número do corpo do adendo, fora das tabelas geradas e dos blocos de código, tem uma linha aqui.\n\n"
            "As tabelas do adendo são geradas pelo mesmo script: a T1, T1b, T2, T5, T6, T7 e T8 de `outputs/runs/rodada_test/tabelas/` (v1) e "
            "de `outputs/runs_v2/rodada_test_v2/tabelas/` (v2), `clipes_test_v2.csv`, `pioras.csv` e os `decisao.json` de "
            "`outputs/runs_v2/<hipótese>/`; o script confere que as tabelas no adendo são as geradas.\n\n"
            "| nº | número no texto | o que é | seção | origem | linha | coluna | valor na origem |\n|---|---|---|---|---|---|---|---|\n")
    out = []
    for i, (e, (ok, line, col, raw, msg)) in enumerate(zip(NUMEROS, res), 1):
        src = e.get("src") or f"derivado: {e['expr']}"
        out.append(f"| {i} | {e['txt']} | {e['desc']} | {e['sec']} | `{src}` | {line or '—'} | {col} | {raw} |")
    return head + "\n".join(out) + "\n"


if __name__ == "__main__":
    values, res = {}, [None] * len(NUMEROS)
    for derived in (False, True):
        for k, e in enumerate(NUMEROS):
            if (e["tipo"] == "der") == derived:
                res[k] = resolve(e, values)
    bad = [(e, r) for e, r in zip(NUMEROS, res) if not r[0]]
    for e, r in bad:
        print(f"ORIGEM NÃO CONFERE: {e['txt']!r} ({e['desc']}): {r[4]}")
    text = REL.read_text(encoding="utf-8")
    gen = tabelas()
    for name in gen:
        if not re.search(BLOCK.format(name), text, flags=re.S):
            print(f"MARCADOR AUSENTE: {name}")
            bad.append(None)
    body = re.sub(BLOCK.format(r"\w+"), "", text, flags=re.S)
    body = re.sub(r"\n```.*?\n```", "\n", body, flags=re.S)
    known = {e["txt"] for e in NUMEROS}
    missing = sorted(set(t for t in N.body_tokens(body) if t not in known), key=lambda s: (len(s), s))
    for t in missing:
        print(f"SEM ORIGEM NA LISTA: {t!r}")
    if "--escrever" in sys.argv:
        for name, tab in gen.items():
            text = re.sub(BLOCK.format(name), lambda m: m.group(1) + "\n" + tab + "\n" + m.group(3), text, flags=re.S)
        REL.write_text(text, encoding="utf-8")
        OUT_MD.write_text(numeros_md(res), encoding="utf-8")
        print(f"gravados: tabelas em {REL}; {OUT_MD} ({len(NUMEROS)} entradas)")
    else:
        for name, tab in gen.items():
            m = re.search(BLOCK.format(name), text, flags=re.S)
            if m and m.group(2) != "\n" + tab + "\n":
                print(f"TABELA DIFERENTE DA GERADA: {name} (rode com --escrever)")
                bad.append(None)
    print(f"{len(NUMEROS)} entradas; {len(bad)} sem conferir; {len(missing)} números sem origem")
    sys.exit(1 if bad or missing else 0)
