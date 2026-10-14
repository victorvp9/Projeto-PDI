"""Números do relatório (docs/04-relatorio.md): cada número do texto com a origem, conferido.

- Cada entrada da lista NUMEROS liga um número, como escrito no texto, à origem:
  - uma célula de CSV (arquivo, linha escolhida pelas colunas-chave, coluna): confere que o
    valor do CSV, arredondado às casas do texto, é o número do texto;
  - uma linha de documento ou saída (arquivo e um trecho que acha a linha): confere que o
    número está naquela linha;
  - uma conta sobre outras entradas (derivado): confere o resultado.
- Completude: todo número do corpo do relatório tem que ter uma entrada. Ficam de fora só os
  identificadores (clipes SNGS-xxx, frames fNNN, nomes de tabela, figura, seção, etapa,
  fatia e jogo, anos de citação, enumerações e trechos de código).
- O Apêndice A é gerado aqui a partir dos CSVs T1-T9 e tem que estar no relatório tal como
  gerado.

Uso (da raiz, PYTHONPATH=.): numeros.py [--escrever]. Sem a opção, só confere (código 1 se
algo falhar); com ela, grava o Apêndice A no relatório e o docs/04-relatorio-numeros.md."""
import csv
import math
import re
import sys
from pathlib import Path

REL = Path("docs/04-relatorio.md")
OUT_MD = Path("docs/04-relatorio-numeros.md")
TAB = "outputs/runs/rodada_test/tabelas"
FAL = "outputs/runs/rodada_test/falhas"
POS = "outputs/runs/rodada_test/pos_rodada"          # análises posteriores à rodada (scripts/relatorio/pos_rodada.py)
B134 = f"{POS}/B1_B3_B4.csv"
V2 = "outputs/runs/rodada_test/tabelas_v2.out"
AF = "outputs/runs/rodada_test/analise_falhas.out"
DEC, P0, M1, D2, PL, CFG = "docs/decisoes.md", "docs/00-problema.md", "docs/01-metodo.md", "docs/02-dados.md", "docs/03-plano.md", "config.yaml"

NUMEROS = []


def C(txt, desc, src, sel, col, esc=1, key=None, sec=""):
    """Célula de CSV. `src` "T1" = tabela da rodada; senão, caminho. `sel` {coluna: valor}."""
    NUMEROS.append(dict(tipo="csv", txt=txt, desc=desc, src=f"{TAB}/{src}.csv" if re.fullmatch(r"T\d+b?", src) else src,
                        sel=sel, col=col, esc=esc, key=key, sec=sec))


def X(txt, desc, src, anchor, key=None, sec=""):
    """Número numa linha de documento ou saída, achada pelo trecho `anchor`."""
    NUMEROS.append(dict(tipo="txt", txt=txt, desc=desc, src=src, anchor=anchor, key=key, sec=sec))


def D(txt, desc, expr, fn, key=None, sec=""):
    """Conta sobre outras entradas (por `key`): fn(valores) -> valor esperado."""
    NUMEROS.append(dict(tipo="der", txt=txt, desc=desc, expr=expr, fn=fn, key=key, sec=sec))


# ------------------------------------------------------------------ resultados (rodada do test)
S = "Resumo, 6, 9"
C("0,505", "cobertura do detector, GSR test", "T1", {"serie": "detector"}, "cobertura", key="det_cob", sec=S)
C("0,419", "LocSim@5 penalizado do detector", "T1", {"serie": "detector"}, "locsim_pen", key="det_pen", sec=S)
C("0,341", "LocSim@5 penalizado do detector, IC inferior (= jogo 7)", "T1", {"serie": "detector"}, "locsim_pen_lo", sec="6")
C("0,555", "LocSim@5 penalizado do detector, IC superior (= jogo 11)", "T1", {"serie": "detector"}, "locsim_pen_hi", sec="6")
C("0,869", "LocSim@5 do detector nos cobertos", "T1", {"serie": "detector"}, "locsim_cob", sec=S)
C("0,0072", "NPE mediano do detector", "T1", {"serie": "detector"}, "npe_med", sec="6")
C("0,897", "cobertura do 6c fluxo", "T1", {"serie": "6c fluxo"}, "cobertura", sec=S)
C("0,749", "LocSim@5 penalizado do 6c fluxo", "T1", {"serie": "6c fluxo"}, "locsim_pen", key="c6_pen", sec=S)
C("0,650", "LocSim@5 penalizado do 6c, IC inferior", "T1", {"serie": "6c fluxo"}, "locsim_pen_lo", sec="6")
C("0,920", "LocSim@5 penalizado do 6c, IC superior", "T1", {"serie": "6c fluxo"}, "locsim_pen_hi", sec="6")
C("0,833", "LocSim@5 do 6c nos cobertos", "T1", {"serie": "6c fluxo"}, "locsim_cob", sec="6")
C("0,0105", "NPE mediano do 6c fluxo", "T1", {"serie": "6c fluxo"}, "npe_med", sec="6")
C("0,959", "fração da distância ao teto condicionado às âncoras, propagação", "T1", {"serie": "6c fluxo"}, "fracao_teto", sec="6")
C("95,9", "a mesma fração, em %", "T1", {"serie": "6c fluxo"}, "fracao_teto", 100, sec="6")
C("0,925", "fração ao teto, IC inferior", "T1", {"serie": "6c fluxo"}, "fracao_teto_lo", sec="6")
C("0,986", "fração ao teto, IC superior", "T1", {"serie": "6c fluxo"}, "fracao_teto_hi", sec="6")
for serie, cols in (("6a Bassek", ("0,680", "0,0126", "0,446", "0,681", "0,078")), ("6a robusto", ("0,665", "0,0097", "0,478", "0,747", "0,171")),
                    ("Kalman + RTS", ("0,680", "0,0113", "0,490", "0,749", "0,207")), ("6c sem linhas", ("0,897", "0,0122", "0,715", "0,796", "0,861")),
                    ("6c sem fluxo", ("0,897", "0,1248", "0,366", "0,407", "−0,155")), ("6c âncora ingênua /150", ("1,000", "0,0262", "0,571", "0,571", "0,442"))):
    for txt, col in zip(cols, ("cobertura", "npe_med", "locsim_pen", "locsim_cob", "fracao_teto")):
        C(txt, f"{col} de {serie} (Tabela 1)", "T1", {"serie": serie}, col, sec="6")
C("0,897", "cobertura da âncora de gabarito (teto)", "T1", {"serie": "6c âncora de gabarito"}, "cobertura", sec="6")
C("0,0064", "NPE mediano do teto", "T1", {"serie": "6c âncora de gabarito"}, "npe_med", sec="6")
C("0,763", "LocSim@5 penalizado do teto", "T1", {"serie": "6c âncora de gabarito"}, "locsim_pen", sec="6")
C("0,849", "LocSim@5 do teto nos cobertos", "T1", {"serie": "6c âncora de gabarito"}, "locsim_cob", sec="6")
X("49", "clipes do GSR test", V2, "GSR test: 49 clipes", key="n_test", sec=S)
X("3", "jogos do GSR test", V2, "GSR test: 49 clipes, 3 jogos", sec=S)
X("10", "reamostragens distintas do bootstrap com 3 jogos", V2, "10 reamostragens distintas", sec="5")
X("44", "clipes com >= 1 âncora aceita", V2, "44 clipes com", sec="6")
for jogo, cl, ca, cd, c6, pd, p6, pt in (("7", "16", "14", "0,472", "0,874", "0,341", "0,676", "0,703"), ("8", "19", "16", "0,447", "0,838", "0,360", "0,650", "0,661"),
                                         ("11", "14", "14", "0,617", "1,000", "0,555", "0,920", "0,925")):
    C(jogo, "jogo do GSR test", "T6", {"jogo": jogo}, "jogo", sec="4, 6")
    C(cl, f"clipes do jogo {jogo}", "T6", {"jogo": jogo}, "clipes", sec="4, 6")
    C(ca, f"clipes com âncora do jogo {jogo}", "T6", {"jogo": jogo}, "com_ancora", sec="6")
    C(cd, f"cobertura do detector, jogo {jogo}", "T6", {"jogo": jogo}, "cob_detector", sec="6")
    C(c6, f"cobertura do 6c, jogo {jogo}", "T6", {"jogo": jogo}, "cob_6c", sec="6")
    C(pd, f"LocSim@5 penalizado do detector, jogo {jogo}", "T6", {"jogo": jogo}, "locsim_pen_detector", key=f"pd{jogo}", sec="6")
    C(p6, f"LocSim@5 penalizado do 6c, jogo {jogo}", "T6", {"jogo": jogo}, "locsim_pen_6c", key=f"p6{jogo}", sec="6")
    C(pt, f"LocSim@5 penalizado do teto, jogo {jogo}", "T6", {"jogo": jogo}, "locsim_pen_teto", key=f"pt{jogo}", sec="6")
D("0,03", "o 6c fica a menos disto do teto nos três jogos (máximo de teto − 6c: 0,027)", "max(teto − 6c) < 0,03",
  lambda v: 0.03 if max(v[f"pt{j}"] - v[f"p6{j}"] for j in ("7", "8", "11")) < 0.03 else math.nan, sec="6")
C("+0,330", "ganho 6c − detector, penalizado", "T5", {"linha": "ganho 6c - detector"}, "pen", sec=S)
C("0,290", "ganho, IC inferior", "T5", {"linha": "ganho 6c - detector"}, "pen_lo", sec="6")
C("0,365", "ganho, IC superior", "T5", {"linha": "ganho 6c - detector"}, "pen_hi", sec="6")
C("−0,035", "ganho 6c − detector nos cobertos", "T5", {"linha": "ganho 6c - detector"}, "cob", key="g_cob", sec="6")
D("0,035", "o mesmo, em módulo (\"fica 0,035 abaixo\")", "|ganho nos cobertos|", lambda v: abs(v["g_cob"]), sec="6")
C("−0,078", "ganho nos cobertos, IC inferior", "T5", {"linha": "ganho 6c - detector"}, "cob_lo", sec="6")
C("−0,003", "ganho nos cobertos, IC superior", "T5", {"linha": "ganho 6c - detector"}, "cob_hi", sec="6")
C("0,885", "LocSim@5 do NBJW, tabela 7 do AuxFlow", "T5", {"linha": "NBJW (AuxFlow, tab. 7)"}, "locsim5", key="nbjw", sec="2, 6, 9")
C("0,929", "LocSim@5 do AuxFlow, tabela 7", "T5", {"linha": "AuxFlow (tab. 7)"}, "locsim5", key="auxflow", sec="2, 6, 9")
C("+0,044", "ganho AuxFlow − NBJW", "T5", {"linha": "ganho AuxFlow - NBJW"}, "locsim5", sec=S)
C("0,869", "LocSim@5 do detector no conjunto comum", "T5", {"linha": "nosso detector"}, "comum", sec="6")
D("65", "fração da distância detector -> AuxFlow fechada pelo 6c (%)", "(6c − detector) / (AuxFlow − detector)",
  lambda v: 100 * (v["c6_pen"] - v["det_pen"]) / (v["auxflow"] - v["det_pen"]), sec="6, 9")
C("18.133", "frames do conjunto comum", "T1b", {"serie": "detector"}, "frames", sec="6")
C("0,922", "LocSim@5 penalizado do 6c no conjunto comum", "T1b", {"serie": "6c fluxo"}, "locsim_pen", key="c6_com", sec="Resumo, 6, 9")
C("0,869", "LocSim@5 penalizado do detector no conjunto comum", "T1b", {"serie": "detector"}, "locsim_pen", key="det_com", sec="6, 9")
D("0,131", "erro residual do detector no conjunto comum", "1 − LocSim@5 pen. do detector (T1b)", lambda v: 1 - v["det_com"], sec="6")
D("0,078", "erro residual da propagação no conjunto comum", "1 − LocSim@5 pen. da propagação (T1b)", lambda v: 1 - v["c6_com"], sec="6")
D("40", "redução do erro residual no conjunto comum (%), com os resíduos como escritos no texto (0,131 → 0,078; 40,5% com os brutos)",
  "(0,131 − 0,078) / 0,131", lambda v: 100 * (round(1 - v["det_com"], 3) - round(1 - v["c6_com"], 3)) / round(1 - v["det_com"], 3), sec="Resumo, 6, 9")
D("0,115", "erro residual do NBJW (tabela 7 do AuxFlow)", "1 − 0,885", lambda v: 1 - v["nbjw"], sec="6")
D("0,071", "erro residual do AuxFlow (tabela 7)", "1 − 0,929", lambda v: 1 - v["auxflow"], sec="6")
D("38", "redução do erro residual do AuxFlow sobre o NBJW (%)", "(0,929 − 0,885) / (1 − 0,885)",
  lambda v: 100 * (v["auxflow"] - v["nbjw"]) / (1 - v["nbjw"]), sec="Resumo, 6, 9")
D("0,581", "erro residual do detector, penalizado", "1 − 0,419", lambda v: 1 - v["det_pen"], sec="6")
D("0,251", "erro residual da propagação, penalizado", "1 − 0,749", lambda v: 1 - v["c6_pen"], sec="6")
D("57", "redução do erro residual no conjunto inteiro (%)", "(0,749 − 0,419) / (1 − 0,419)",
  lambda v: 100 * (v["c6_pen"] - v["det_pen"]) / (1 - v["det_pen"]), sec="6")
C("0,0066", "NPE mediano do 6c no conjunto comum", "T1b", {"serie": "6c fluxo"}, "npe_med", sec="6")
C("0,818", "LocSim@5 da âncora ingênua no conjunto comum", "T1b", {"serie": "6c âncora ingênua /150"}, "locsim_pen", sec="6")
X("85", "fração ao teto nos 19 clipes do train[::3] (%)", DEC, "fração da distância fechada entre o detector e o teto", sec="6")
X("19", "clipes de calibração do treino (train[::3])", DEC, "fração da distância fechada entre o detector e o teto", sec="6")
X("74", "fração ao teto na validação (%)", DEC, "Fração da distância ao teto: (0,436 − 0,173)", sec="6")
X("10", "âncoras aceitas erradas na validação (%)", DEC, "**10% delas erradas**", sec="6")

# HSB (T2), em %
T2A = {"clipe": "todos"}
C("81,4", "HSB (1) só propagação, média por frame (%)", "T2", T2A, "(1) só propagação pen média", 100, sec="6, 9")
C("92,7", "HSB (1) só propagação, mediana (%)", "T2", T2A, "(1) só propagação pen mediana", 100, sec="6")
C("1,000", "HSB (1) cobertura nos frames com pessoas", "T2", T2A, "(1) só propagação cobertura frames com pessoas", sec="6")
C("17,7", "HSB (2) detector, média (%)", "T2", T2A, "(2) detector pen média", 100, sec="6")
C("0,0", "HSB (2) detector, mediana (%)", "T2", T2A, "(2) detector pen mediana", 100, sec="6")
C("0,221", "HSB (2) detector, cobertura nos frames com pessoas", "T2", T2A, "(2) detector cobertura frames com pessoas", sec="6")
C("79,7", "HSB (2) detector nos cobertos, média (%)", "T2", T2A, "(2) detector cob média", 100, sec="6")
C("61,7", "HSB (3) pipeline, média (%)", "T2", T2A, "(3) pipeline pen média", 100, sec="6, 9")
C("71,1", "HSB (3) pipeline, mediana (%)", "T2", T2A, "(3) pipeline pen mediana", 100, sec="6")
C("0,829", "HSB (3) pipeline, cobertura nos frames com pessoas", "T2", T2A, "(3) pipeline cobertura frames com pessoas", sec="6")
X("1.120", "frames com pessoas do HSB", V2, "frames com pessoas 1120", sec="6")
X("43,15", "NBJW sozinho no HSB, média (AuxFlow, tabela 4)", P0, "contra 43,15 do detector sozinho", sec="2, 6, 9")
X("35,93", "NBJW no HSB, mediana (AuxFlow, tabela 4)", V2, "NBJW (43.15, 35.93)", sec="6")
X("83,67", "AuxFlow no HSB, média (tabela 4)", P0, "de 83,67 para 23,42", sec="2, 6, 9")
X("96,15", "AuxFlow no HSB, mediana (tabela 4)", V2, "AuxFlow (83.67, 96.15)", sec="6")
C("50,8", "SNGS-124, só propagação (%): a menor média do HSB", "T2", {"clipe": "SNGS-124"}, "(1) só propagação pen média", 100, sec="6")
C("97,4", "SNGS-128, só propagação (%)", "T2", {"clipe": "SNGS-128"}, "(1) só propagação pen média", 100, sec="6")
C("96,5", "SNGS-138, só propagação (%)", "T2", {"clipe": "SNGS-138"}, "(1) só propagação pen média", 100, sec="6")
C("0", "SNGS-128 e SNGS-138: pipeline vale 0 (sem âncora)", "T2", {"clipe": "SNGS-128"}, "(3) pipeline pen média", sec="6")
C("87,2", "SNGS-136, só propagação (%)", "T2", {"clipe": "SNGS-136"}, "(1) só propagação pen média", 100, sec="6")
C("85,7", "SNGS-136, pipeline (%)", "T2", {"clipe": "SNGS-136"}, "(3) pipeline pen média", 100, sec="6")
C("44,2", "SNGS-136, detector penalizado (%)", "T2", {"clipe": "SNGS-136"}, "(2) detector pen média", 100, sec="6")
C("60", "SNGS-136, início do intervalo do HSB", "data_splits/hsb.csv", {"clipe": "SNGS-136"}, "inicio", sec="6")
C("280", "SNGS-136, fim do intervalo do HSB", "data_splits/hsb.csv", {"clipe": "SNGS-136"}, "fim", sec="6")
C("0,64", "SNGS-150: cobertura do detector nos frames com H_gt", "T2", {"clipe": "SNGS-150"}, "(2) detector cobertura", sec="8")
C("0,07", "SNGS-150: cobertura do detector nos frames com pessoas", "T2", {"clipe": "SNGS-150"}, "(2) detector cobertura frames com pessoas", sec="8")

# WC14 (T3, T3b)
C("0,575", "cobertura do detector no WC14 test", "T3", {"metrica": "cobertura"}, "media", sec="6, 9")
C("186", "imagens do WC14 test", "T3", {"metrica": "frames"}, "media", sec="Resumo, 4, 6")
C("0,913", "IoU_whole mediano, WC14 test", "T3", {"metrica": "iou_whole"}, "mediana", sec="6")
C("0,864", "IoU_whole médio, WC14 test", "T3", {"metrica": "iou_whole"}, "media", sec="6")
C("0,995", "IoU_part mediano, WC14 test", "T3", {"metrica": "iou_part"}, "mediana", sec="6, 9")
C("0,380", "RE mediano (m), WC14 test", "T3", {"metrica": "re_m"}, "mediana", sec="6")
C("1,615", "RE médio (m), WC14 test", "T3", {"metrica": "re_m"}, "media", sec="6")
C("107", "imagens com H (protocolo KpSFR)", "T3b", {"metrica": "iou_part"}, "imagens", key="kp_n", sec="6")
C("0,937", "iou_part médio no protocolo KpSFR, 107 imagens", "T3b", {"metrica": "iou_part"}, "media", sec="6")
C("0,5155", "iou_whole médio no protocolo KpSFR, 186 imagens com 0 nas sem H", "T3b", {"metrica": "iou_whole (nossa convenção: imagem sem H vale 0)"}, "media", sec="6, 9")
C("0,8634", "iou_whole mediano no protocolo KpSFR, 186 imagens com 0 nas sem H", "T3b", {"metrica": "iou_whole (nossa convenção: imagem sem H vale 0)"}, "mediana", sec="6, 9")
C("0,8962", "iou_whole médio no protocolo KpSFR, 107 imagens com H", "T3b", {"metrica": "iou_whole"}, "media", sec="6, 9")
C("0,9534", "iou_whole mediano no protocolo KpSFR, 107 imagens com H", "T3b", {"metrica": "iou_whole"}, "mediana", sec="6, 9")
C("0,539", "iou_part médio, 186 imagens com 0 nas sem H", "T3b", {"metrica": "iou_part (nossa convenção: imagem sem H vale 0)"}, "media", sec="6")
D("79", "imagens do WC14 test sem H", "186 − 107", lambda v: 186 - v["kp_n"], sec="6")
X("0", "imagem sem H vale 0 na nossa convenção", f"{TAB}/T3b.csv", "nossa convenção: imagem sem H vale 0", sec="6")

# estabilidade e visibilidade (T4, T4b)
X("100", "ECC convergiu em 100% dos pares", V2, "ECC convergiu em 100.0% dos 36701 pares", sec="6")
X("36.701", "pares de frames consecutivos do ECC", V2, "ECC convergiu em 100.0% dos 36701 pares", sec="6")
X("0,987", "correlação mediana do ECC", V2, "correlação mediana 0.987", sec="6")
X("17.828", "frames na interseção das cinco séries", V2, "17828 frames de 36750", sec="6")
X("36.750", "frames do GSR test", V2, "17828 frames de 36750", sec="6")
for serie, tm, tp, dm, dp in (("Kalman + RTS", "0,13", "0,57", "1,71", "5,45"), ("6c fluxo", "0,40", "1,43", "1,38", "4,33"), ("detector", "1,29", "15,50", None, None),
                              ("6a Bassek", None, None, "1,90", "8,31")):
    for txt, col in ((tm, "tremor_med"), (tp, "tremor_p90"), (dm, "deslize_med"), (dp, "deslize_p90")):
        if txt:
            C(txt, f"{col} (px) de {serie} na interseção (T4b)", "T4b", {"serie": serie}, col, sec="6")
C("4,17", "deslize p90 (px) do 6c no próprio conjunto", "T4", {"serie": "6c fluxo"}, "deslize_p90", sec="6")
C("23,51", "deslize p90 (px) do Kalman no próprio conjunto", "T4", {"serie": "Kalman + RTS"}, "deslize_p90", sec="6")
C("72,61", "deslize p90 (px) do 6a Bassek no próprio conjunto", "T4", {"serie": "6a Bassek"}, "deslize_p90", sec="6")
C("4,25", "deslize mediano (px) do 6c sem fluxo", "T4", {"serie": "6c sem fluxo"}, "deslize_med", sec="6")
C("0,8", "jogadores invertidos do 6c na interseção (%)", "T4b", {"serie": "6c fluxo"}, "jogadores", 100, sec="6, 9")
C("4,4", "jogadores invertidos do Kalman na interseção (%)", "T4b", {"serie": "Kalman + RTS"}, "jogadores", 100, sec="6, 9")
C("5,0", "jogadores invertidos do detector na interseção (%)", "T4b", {"serie": "detector"}, "jogadores", 100, sec="6")
C("53,5", "jogadores invertidos do detector, penalizada (%)", "T4", {"serie": "detector"}, "jogadores_penalizada", 100, sec="6")
C("11,8", "jogadores invertidos do 6c, penalizada (%)", "T4", {"serie": "6c fluxo"}, "jogadores_penalizada", 100, sec="6")
C("5,6", "jogadores invertidos do detector, só cobertos (%)", "T4", {"serie": "detector"}, "jogadores_só cobertos", 100, sec="6")
C("2,1", "jogadores invertidos do 6c, só cobertos (%)", "T4", {"serie": "6c fluxo"}, "jogadores_só cobertos", 100, sec="6")
C("0,1", "frames com 0 visíveis do 6c, só cobertos (%)", "T4", {"serie": "6c fluxo"}, "zero_visiveis_só cobertos", 100, sec="6")
X("3", "0 visíveis no feed de scouting de Bassek et al. (%)", P0, "aparecia visível, em 3% nenhum", sec="2, 6")
X("1", "1 jogador visível no feed de scouting de Bassek et al. (%)", P0, "feed de scouting", sec="2")

# âncoras (T7) e lacunas (T8)
C("958", "âncoras candidatas", "T7", {"conjunto": "candidatas"}, "n", sec="6")
D("28,3", "candidatas erradas, entre as com gabarito (%)", "270 / 955", lambda v: 100 * 270 / 955, sec="6, 9")
C("558", "âncoras aceitas", "T7", {"conjunto": "aceitas"}, "n", sec="6")
D("2,2", "aceitas erradas, entre as com gabarito (%) = 12 / 557", "12 / 557", lambda v: 100 * 12 / 557, sec="6, 9")
C("12", "âncoras aceitas erradas", "T7", {"conjunto": "aceitas"}, "erradas", sec="6, 7")
C("5", "clipes sem âncora aceita", "T7", {"conjunto": "clipes sem âncora aceita"}, "n", sec="6, 7")
X("0,05", "limiar de âncora/H errada (NPE > 0,05)", V2, "candidatas      958  erradas (NPE > 0,05)", sec="4, 6")
for lac, fr, b, r, c, s in (("1-3", "1.665", "0,0974", "0,0324", "0,0095", "0,0115"), ("4-25", "4.624", "0,8994", "0,7960", "0,0168", "0,0247"),
                            ("> 25", "8.391", None, None, "0,0551", "0,0785"), ("pontas", "3.088", None, None, "0,1221", "0,1355")):
    C(fr, f"frames na lacuna {lac}", "T8", {"lacuna": lac}, "frames", sec="6")
    for txt, col in ((b, "6a Bassek NPE"), (r, "6a robusto NPE"), (c, "6c fluxo NPE"), (s, "6c sem linhas NPE")):
        if txt:
            C(txt, f"NPE mediano, {col.replace(' NPE', '')}, lacuna {lac}", "T8", {"lacuna": lac}, col, sec="6, 7")
X("1", "limite das faixas de lacuna (1-3)", f"{TAB}/T8.csv", "1-3,", sec="6")
X("3", "limite das faixas de lacuna (1-3)", f"{TAB}/T8.csv", "1-3,", sec="6")
X("4", "limite das faixas de lacuna (4-25)", f"{TAB}/T8.csv", "4-25,", sec="6, 7")
X("25", "limite das faixas de lacuna (4-25, > 25)", f"{TAB}/T8.csv", "4-25,", sec="6, 7")
LR = f"{FAL}/lacunas_4a25_resumo.csv"
C("99", "lacunas de 4-25 com as duas bordas certas", LR, {"conjunto": "test", "classe": "bordas certas"}, "lacunas", key="l0", sec="7")
C("106", "lacunas de 4-25 com uma borda errada", LR, {"conjunto": "test", "classe": "uma borda errada"}, "lacunas", key="l1", sec="7")
C("331", "lacunas de 4-25 com as duas bordas erradas", LR, {"conjunto": "test", "classe": "as duas bordas erradas"}, "lacunas", key="l2", sec="7")
C("1", "lacuna de 4-25 com borda sem gabarito", LR, {"conjunto": "test", "classe": "borda sem gabarito"}, "lacunas", key="l3", sec="7")
D("537", "lacunas de 4-25 frames no test", "99 + 106 + 331 + 1", lambda v: v["l0"] + v["l1"] + v["l2"] + v["l3"], sec="7")
D("62", "lacunas de 4-25 com as duas bordas erradas (%)", "331 / 537", lambda v: 100 * v["l2"] / (v["l0"] + v["l1"] + v["l2"] + v["l3"]), sec="6")
C("0,0242", "NPE mediano do 6a Bassek com as duas bordas certas", LR, {"conjunto": "test", "classe": "bordas certas"}, "bassek_npe_med", sec="6")

# custo (T9)
C("8,58", "parede da série do detector (h)", "T9", {"etapa": "série do detector (todos os frames)"}, "parede_h", sec="6")
C("15", "processos da série do detector", "T9", {"etapa": "série do detector (todos os frames)"}, "processos", sec="6")
C("1,19", "vazão da série (frames/s)", "T9", {"etapa": "série do detector (todos os frames)"}, "frames_por_s", sec="6")
C("630", "s de parede por clipe com 15 processos, série (máquina inteira)", "T9", {"etapa": "série do detector (todos os frames)"}, "s_por_clipe_parede",
  key="ser_clip", sec="6, 9")
C("126", "s de parede por clipe com 10 processos, 6c com as ablações", "T9", {"etapa": "6c com as ablações"}, "s_por_clipe_parede", key="c6_clip", sec="6")
D("756", "s de parede por clipe: série + 6c", "630 + 126 (T9, s_por_clipe_parede)", lambda v: v["ser_clip"] + v["c6_clip"], sec="9")
D("10", "o --all do zero só no test passa disto (h): 49 clipes × 756 s = 10,3 h", "49 × (série + 6c) / 3600 > 10",
  lambda v: 10 if v["n_test"] * (v["ser_clip"] + v["c6_clip"]) / 3600 > 10 else math.nan, sec="9")
D("30", "o --all do zero nas três partições passa disto (h): 164 clipes × 756 s = 34,4 h", "(57 + 58 + 49) × (série + 6c) / 3600 > 30",
  lambda v: 30 if (v["n_train"] + v["n_valid"] + v["n_test"]) * (v["ser_clip"] + v["c6_clip"]) / 3600 > 30 else math.nan, sec="9")
C("1,71", "parede do 6c (h)", "T9", {"etapa": "6c com as ablações"}, "parede_h", sec="6")
C("10", "processos do 6c", "T9", {"etapa": "6c com as ablações"}, "processos", sec="6")
C("292", "AuxFlow, s por clipe (tabela 6)", "T9", {"etapa": "AuxFlow Overall"}, "s_por_clipe", sec="6, 9")
C("2,6", "AuxFlow, FPS (tabela 6)", "T9", {"etapa": "AuxFlow Overall"}, "fps", sec="6")
X("4,76", "detector, s por frame num núcleo, GSR", V2, "detector 4,76 s/frame", sec="6, 9")
X("3.570", "detector, s por clipe de 750 frames num núcleo (perfil)", PL, "~3.570 s no detector", sec="9")
X("2,90", "detector, s por frame num núcleo, WC14", V2, "2,90 s no WC14", sec="6")
X("127", "6c fluxo, ms por frame", V2, "6c fluxo 127 ms/frame", sec="6, 9")
X("750", "frames por clipe", D2, "(750 frames, 25 fps", sec="4, 6")
for t in ("7", "8", "16", "5060", "4090"):
    X(t, "hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090)", V2, "hardware: nosso AMD Ryzen 7", sec="6")

# análise de falhas
CT = f"{FAL}/clipes_test.csv"
for c, d6, tt in (("SNGS-149", "0,252", None), ("SNGS-119", "0,458", None), ("SNGS-143", "0,495", "0,495"), ("SNGS-144", "0,506", "0,508"),
                  ("SNGS-148", "0,587", None), ("SNGS-126", "0,635", "0,954")):
    C(d6, f"LocSim@5 penalizado do 6c, {c}", CT, {"clipe": c}, "c6", sec="7")
    if tt:
        C(tt, f"LocSim@5 penalizado do teto, {c}", CT, {"clipe": c}, "teto", sec="7")
X("6", "piores clipes inspecionados", PL, "os 6 piores clipes do 6c", sec="7")
X("12", "âncoras erradas inspecionadas", PL, "os 6 piores clipes do 6c", sec="7")
X("5", "clipes sem âncora inspecionados", PL, "os 5 clipes sem âncora", sec="7")
X("3", "lacunas de exemplo inspecionadas", PL, "os 5 clipes sem âncora", sec="7")
AE = f"{FAL}/ancoras_erradas_test.csv"
C("1,355", "NPE da âncora SNGS-126 f588", AE, {"clipe": "SNGS-126", "frame": "588"}, "npe", sec="7")
C("0,060", "menor NPE das âncoras de encaixe parcial (SNGS-122 f657)", AE, {"clipe": "SNGS-122", "frame": "657"}, "npe", sec="7")
C("0,235", "maior NPE das âncoras de encaixe parcial (SNGS-190 f525)", AE, {"clipe": "SNGS-190", "frame": "525"}, "npe", sec="7")
C("0,063", "NPE da âncora SNGS-132 f721", AE, {"clipe": "SNGS-132", "frame": "721"}, "npe", sec="7")
D("10", "âncoras de encaixe parcial: as aceitas erradas menos a troca de reta (SNGS-126 f588) e a quase certa (SNGS-132 f721)",
  f"linhas de {AE} sem SNGS-126 e SNGS-132",
  lambda v: sum(1 for r in csv.DictReader(open(AE, encoding="utf-8")) if r["clipe"] not in ("SNGS-126", "SNGS-132")), sec="7")
X("13", "clipes sem âncora da valid no jogo 3", DEC, "13 / 21 (62%)", sec="7, 8")
X("18", "clipes sem âncora da valid", DEC, "Os 18 coincidem com as limitações da Fatia 3", sec="6, 7, 8")
X("1", "diagnóstico da segmentação em 1 frame a cada 75", AF, "medianas por frame, 1 a cada 75", sec="7")
X("75", "diagnóstico da segmentação em 1 frame a cada 75", AF, "medianas por frame, 1 a cada 75", sec="7")
SA = f"{FAL}/sem_ancora_x_fatia3.csv"
C("0,988", "menor fração do campo como grama nos sem âncora (SNGS-138)", SA, {"conjunto": "sem âncora: SNGS-138 (jogo 8)"}, "campo_grama", sec="7")
C("0,81", "cobertura das marcações a 2 px, SNGS-127", SA, {"conjunto": "sem âncora: SNGS-127 (jogo 7)"}, "cobertura_2px", sec="7")
C("0,85", "cobertura das marcações a 2 px, SNGS-128", SA, {"conjunto": "sem âncora: SNGS-128 (jogo 7)"}, "cobertura_2px", sec="7")
C("0,98", "cobertura das marcações a 2 px, SNGS-138", SA, {"conjunto": "sem âncora: SNGS-138 (jogo 8)"}, "cobertura_2px", sec="7")
C("0,89", "cobertura das marcações a 2 px, clipes com âncora do jogo 7", SA, {"conjunto": "com âncora, jogo 7"}, "cobertura_2px", sec="7")
X("0,79", "cobertura das marcações a 2 px, referência da Fatia 3 (GSR train)", AF, "referência (Fatia 3, GSR train", sec="7")
X("2", "cobertura das marcações a 2 px", AF, "cobertura 2 px 0,79", sec="7")
C("52", "SNGS-147: pontos anotados acima do limiar (%)", SA, {"conjunto": "sem âncora: SNGS-147 (jogo 8)"}, "acima_limiar", 100, sec="7")
C("68", "clipes com âncora do jogo 8: pontos acima do limiar (%)", SA, {"conjunto": "com âncora, jogo 8"}, "acima_limiar", 100, sec="7")
C("11", "candidatas verificáveis do SNGS-147", CT, {"clipe": "SNGS-147"}, "verificaveis", sec="7")
C("0,7", "menor cobertura do detector nos sem âncora (SNGS-138, %)", CT, {"clipe": "SNGS-138"}, "cob_det", 100, sec="7")
C("15,9", "maior cobertura do detector nos sem âncora (SNGS-147, %)", CT, {"clipe": "SNGS-147"}, "cob_det", 100, sec="7")
DR = f"{FAL}/deriva_6c.csv"
C("0,0059", "NPE mediano do 6c a <= 25 frames da âncora, frames com H do detector", DR, {"onde": "detector com H", "distancia": "<= 25"}, "npe_med", sec="7")
C("0,0101", "NPE mediano do 6c a <= 25 frames da âncora, pontas", DR, {"onde": "pontas", "distancia": "<= 25"}, "npe_med", sec="7")
C("0,208", "NPE mediano do 6c nas pontas a > 250 frames da âncora", DR, {"onde": "pontas", "distancia": "> 250"}, "npe_med", sec="7, 8")
X("250", "faixa de distância à âncora (> 250 frames)", AF, "> 250: 0.2079", sec="7, 8")
C("7,1", "NPE do 6a Bassek no meio da lacuna da Figura 7 (SNGS-121, f14)", f"{FAL}/lacunas_4a25_test.csv",
  {"clipe": "SNGS-121", "frame": "14", "serie": "6a Bassek"}, "npe", sec="7")
X("2", "lacuna da Figura 7 (2-26)", f"{FAL}/lacunas_figuras.csv", "SNGS-121", sec="7")
X("26", "lacuna da Figura 7 (2-26)", f"{FAL}/lacunas_figuras.csv", "SNGS-121", sec="7")

# limitações (sensibilidade, segmentação, gabarito)
X("25", "passos da sensibilidade (±25%)", PL, "Um parâmetro de cada vez, a ±25% e ±50%", sec="8")
X("50", "passos da sensibilidade (±50%)", PL, "Um parâmetro de cada vez, a ±25% e ±50%", sec="8")
X("0,017", "valor de um frame ou imagem nos subconjuntos", DEC, "um frame ou uma imagem vale de 0,017 a 0,029", sec="8")
X("0,029", "valor de um frame ou imagem nos subconjuntos", DEC, "um frame ou uma imagem vale de 0,017 a 0,029", sec="8")
X("14", "configurações da confirmação do detector (atual + 13 candidatos)", DEC, "detector com 14 configurações", key="cf_det", sec="8")
X("3", "configurações da confirmação do 6c (atual + 2 candidatos)", DEC, "6c com 3 configurações", key="cf_6c", sec="8")
D("15", "candidatos confirmados (13 do detector + 2 do 6c)", "(14 − 1) + (3 − 1)", lambda v: v["cf_det"] - 1 + v["cf_6c"] - 1, sec="8")
X("0,02", "ganho mínimo para virar candidato", DEC, "Δ ≥ 0,02 no LocSim@5 penalizado", sec="8")
X("30", "limiar de contraste das marcações no GSR, atual", DEC, "(30 → 15)", sec="3, 8")
X("15", "limiar candidato (recusado)", DEC, "(30 → 15)", sec="8")
X("+0,034", "Δ LocSim do line_thr 15", DEC, "Δ LocSim +0,034 [+0,003; +0,065]", sec="8")
X("+0,003", "IC inferior do Δ do line_thr 15", DEC, "Δ LocSim +0,034 [+0,003; +0,065]", sec="8")
X("+0,065", "IC superior do Δ do line_thr 15", DEC, "Δ LocSim +0,034 [+0,003; +0,065]", sec="8")
X("+0,127", "Δ LocSim do line_thr 15 no jogo 4", DEC, "um é a favor (jogo 4, +0,127)", sec="8")
X("−0,046", "Δ LocSim do line_thr 15 no jogo 9", DEC, "um é contra (jogo 9, −0,046", sec="8")
X("0,0056", "NPE mediano do jogo 9, limiar 30", DEC, "um é contra (jogo 9, −0,046", sec="8")
X("0,0130", "NPE mediano do jogo 9, limiar 15", DEC, "um é contra (jogo 9, −0,046", sec="8")
X("52", "fração do campo coberta pelo gramado no jogo 3 da valid (%)", DEC, "que ali cobre ~52% do campo", sec="8")
X("2,33", "frames do test sem H_gt na geração do gabarito (Fatia 2, %)", DEC, "Sem `H_gt`: treino 0,74%, validação 2,47%, teste 2,33%", sec="8")

# método e dados (documentos e config)
X("3", "homografia 3 × 3", P0, "uma matriz 3×3", sec="1")
X("2", "2 + 2 retas de duas famílias", DEC, "Teto da geração** (2 + 2 retas certas", sec="Resumo, 3, 7, 8")
X("0,5", "BroadTrack reinicia com IoU < 0,5", M1, "de 0,5.", sec="2")
for t in ("0,8397", "0,8352", "0,9224", "0,9426", "1,34", "0,84"):
    X(t, "BroadTrack × AuxFlow no GSR (01-metodo)", M1, {"0,8397": "0,8397", "0,8352": "0,8397", "0,9224": "0,9224", "0,9426": "0,9426",
                                                          "1,34": "(1,34 contra", "0,84": "0,84 m)"}[t], sec="2")
X("2,5", "grade de pontos auxiliares 2,5 × 2 m", M1, "(2,5 m × 2 m no AuxFlow)", sec="2, 3, 5")
X("2", "grade de pontos auxiliares 2,5 × 2 m", M1, "(2,5 m × 2 m no AuxFlow)", sec="2, 3, 5")
X("1", "erro de ida e volta <= 1 px", M1, "(erro ida-e-volta ≤ 1 px no AuxFlow)", sec="2, 3")
X("23,42", "AuxFlow sem fluxo no HSB", P0, "de 83,67 para 23,42", sec="2")
X("78,30", "AuxFlow sem pontos-chave do detector no HSB", M1, "83,67 → 78,30", sec="2")
X("78,71", "RAFT no lugar do Lucas–Kanade", P0, "contra 78,71)", sec="2")
X("39,68", "amostragem geométrica no AuxFlow", M1, "(83,67 contra 39,68)", sec="2")
X("83,39", "amostragem aleatória no AuxFlow", M1, "na prática com a aleatória (83,39)", sec="2")
X("150", "âncoras ingênuas a cada 150 frames", M1, "no GSR completo, âncoras a cada 150 frames", sec="2, 3")
X("82,48", "âncoras ingênuas no AuxFlow", M1, "(82,48) ficaram", sec="2")
X("83,48", "detector sem propagação no AuxFlow", M1, "(83,48); as heurísticas", sec="2")
X("90,65", "âncoras por heurística no AuxFlow", M1, "levaram a 90,65", sec="2")
X("91,88", "âncora de gabarito no AuxFlow", M1, "levaram a 90,65", sec="2")
X("54,74", "AuxFlow com a H inicial perturbada", P0, "(54,74", sec="2")
X("31", "janela do Savitzky–Golay (Bassek et al.)", P0, "janela 31 e polinômio de terceiro grau", sec="2, 3")
X("3", "grau do Savitzky–Golay (Bassek et al.)", CFG, "sg_poly: 3", sec="2, 3")
X("25", "lacunas preenchidas por interpolação (Bassek et al.)", M1, "lacunas de até 25 frames preenchidas", sec="2, 3")
X("981", "cortes por partida (Bassek et al.)", M1, "**981 cortes por partida, ou 10,9 por", sec="2")
X("10,9", "cortes por minuto (Bassek et al.)", M1, "**981 cortes por partida, ou 10,9 por", sec="2")
X("115", "molde do PnLCalib no WC14 (115 × 74 jardas)", M1, "**115 × 74 jardas**", sec="2")
X("74", "molde do PnLCalib no WC14 (115 × 74 jardas)", M1, "**115 × 74 jardas**", sec="2")
X("100", "molde do KpSFR e de Maglo et al. (100 × 60 m)", M1, "Chu et al. (KpSFR) e Maglo et al. com **100 × 60 m**", sec="2")
X("60", "molde do KpSFR e de Maglo et al. (100 × 60 m)", M1, "Chu et al. (KpSFR) e Maglo et al. com **100 × 60 m**", sec="2")
X("105", "modelo do campo 105 × 68 m", M1, "Campo de **105 × 68 m**", sec="3")
X("68", "modelo do campo 105 × 68 m", M1, "Campo de **105 × 68 m**", sec="3")
X("20", "faixa de matiz do gramado (±20°)", DEC, "`lab_hue` (±20°, croma ≥ 10, L* ≥ 20), passos", sec="3")
X("0,9861", "IoU médio do gramado no WC14 train_val", DEC, "gramado IoU média 0,9861", sec="3")
X("15", "limiar das marcações no WC14", DEC, "**15 no WC14, 30 no GSR**", sec="3")
X("30", "limiar das marcações no GSR", DEC, "**15 no WC14, 30 no GSR**", sec="3")
X("180", "simetria de 180° do campo", PL, "**Simetria de 180°:**", sec="3, 7")
X("0,45", "portão: fração explicada", CFG, "gate_img: 0.45", sec="3")
X("0,85", "portão: IoU com o gramado", CFG, "gate_iou: 0.85", sec="3")
X("5", "portões logo abaixo do percentil 5 da H_gt", CFG, "gate_iou: 0.85", sec="3")
X("12", "janela das âncoras candidatas (±12 frames)", CFG, "anchor_window: 12", sec="3")
X("2", "vizinhos mínimos da verificação", CFG, "verify_min: 2", sec="3")
X("209", "imagens de treino do WC14", D2, "**209 imagens de treino** (dez jogos) e **186 de teste**", sec="4")
X("1280", "resolução do WC14", D2, "da Copa do Mundo de 2014, 1280×720", sec="4")
X("720", "resolução do WC14", D2, "da Copa do Mundo de 2014, 1280×720", sec="4")
X("25", "fps do GSR", D2, "(750 frames, 25 fps, 1920×1080)", sec="4")
X("1920", "resolução do GSR", D2, "(750 frames, 25 fps, 1920×1080)", sec="4")
X("1080", "resolução do GSR", D2, "(750 frames, 25 fps, 1920×1080)", sec="4")
X("57", "clipes de treino do GSR", D2, "**57 treino,", key="n_train", sec="4")
X("58", "clipes de validação do GSR", D2, "58 validação, 49 teste**", key="n_valid", sec="4")
X("0,8852", "BHITK no GSR, tabela 7 do AuxFlow (conferido por Victor)", DEC, "BHITK 0,8852 × NBJW 0,8851", sec="2")
X("0,8851", "NBJW no GSR, tabela 7 do AuxFlow (conferido por Victor)", DEC, "BHITK 0,8852 × NBJW 0,8851", sec="2")
X("3", "RANSAC a 3 px da H_gt_auxflow", M1, "`H_gt_auxflow` = RANSAC (3 px)", sec="4")
X("10", "clipes do HSB", D2, "São 10 clipes com o intervalo de frames", sec="4")
X("0", "numeração dos frames a partir de 0", D2, "contagem a partir de 0", sec="4")
X("90", "intervalo \"90–0\" do SNGS-128", D2, "**SNGS-128:** o artigo traz \"90–0\"", sec="4")
X("0", "intervalo \"90–0\" do SNGS-128", D2, "**SNGS-128:** o artigo traz \"90–0\"", sec="4")
X("0,05", "LocSim: exp(ln(0,05)·d²/τ²)", M1, "`exp(ln(0,05)·d²/τ²)`", sec="5")
X("5", "τ = 5 m", M1, "Reporte τ = 5 m", sec="5")
X("1", "mAP-LocSim: τ = 1 a 10 m", M1, "τ = 1..10 m", sec="5")
X("10", "mAP-LocSim: τ = 1 a 10 m", M1, "τ = 1..10 m", sec="5")
X("0", "pessoa de frame sem H vale 0", M1, "avaliados: a pessoa de um frame sem H vale 0", sec="5")
X("95", "intervalo de 95%", PL, "levam intervalo de 95% por bootstrap", sec="5, 6")
X("2.000", "reamostragens do bootstrap", PL, "(2.000", sec="5")
X("1.470", "frames da conferência de determinismo", PL, "nos 1.470 frames do", sec="5, B")
X("25", "frames da conferência: 1 a cada 25", PL, "GSR test a cada 25 (49 clipes)", sec="5, B")
X("735", "tarefas da série com a chave congelada", PL, "735/735 chaves iguais à congelada", sec="5, B")
X("47", "caches da valid gravados com a chave errada", DEC, "mas 47 foram gravados com a chave errada", sec="5")
X("0", "manifestos com 0 falhas", DEC, "imagens do WC14, 0 falhas", sec="B")

# revisão externa (2026-10-13): Tabela 1 (contribuição das etapas, treino), limite do LocSim e acurácia contra as linhas
SEG, RET = "Varredura da Fatia 3 no treino", "Varredura das retas (Etapa 3), só no GSR train"
for t, d in (("0,9838", "IoU do gramado, lab_hue (média)"), ("0,9797", "IoU do gramado, lab_hue (sombra)"), ("0,9822", "IoU do gramado, HSV (média)"),
             ("0,9764", "IoU do gramado, HSV (sombra)"), ("0,9728", "IoU do gramado, Lab por distância (média)"), ("0,9319", "IoU do gramado, Lab por distância (sombra)"),
             ("0,9441", "ablação do gramado: cru"), ("0,9492", "ablação: + abertura"), ("0,9548", "ablação: + fechamento"), ("0,9763", "ablação: + maior componente"),
             ("0,579", "F1 a 3 px, filtro de linha, WC14"), ("0,560", "F1 a 3 px, top-hat, WC14"), ("0,634", "F1 a 3 px, filtro de linha, GSR"), ("0,577", "F1 a 3 px, top-hat, GSR")):
    X(t, f"Tabela 1: {d} (treino)", DEC, SEG, sec="3")
for t, d in (("0,641", "F1 dos segmentos na configuração escolhida, GSR"), ("0,597", "F1 sem o filtro de forma"), ("1,17", "fragmentação com a fusão"),
             ("4,70", "fragmentação sem a fusão"), ("0,634", "F1 sem a fusão")):
    X(t, f"Tabela 1: {d} (GSR train)", DEC, RET, sec="3")
X("0,9928", "LocSim@5 do gabarito do AuxFlow (tabela 2 deles)", DEC, "nosso 0,932 / 0,983 / 0,38 m; AuxFlow", sec="4, 6")
C("0,933", "LocSim@5 da H_gt pelas linhas como predição, train (antes da rodada)", "outputs/metrics_gt_train.csv",
  {"conjunto": "todos", "metrica": "locsim@5"}, "media", sec="4")
C("0,930", "LocSim@5 da propagação no conjunto comum, nos frames que ela cobre", "T5", {"linha": "nosso 6c fluxo"}, "comum", sec="6")

# análises posteriores à rodada (pos_rodada.py): B1, B3 e B4 em B1_B3_B4.csv, B4 em B4_fracao.csv, B2 em B2.csv
TI, CC, SIS = "test inteiro", "conjunto comum", "teto do sistema (âncora de gabarito /150)"
for t, col, d in (("1,000", "cobertura", "cobertura"), ("0,0058", "npe_med", "NPE mediano"), ("0,922", "locsim_pen", "LocSim@5 penalizado"),
                  ("0,922", "locsim_cob", "LocSim@5 nos cobertos"), ("0,899", "locsim_pen_min", "LocSim@5 pen., mín. entre os jogos (jogo 8)"),
                  ("0,949", "locsim_pen_max", "LocSim@5 pen., máx. entre os jogos (jogo 11)"), ("0,919", "locsim_pen_jogo7", "LocSim@5 pen., jogo 7"),
                  ("0,899", "locsim_pen_jogo8", "LocSim@5 pen., jogo 8"), ("0,949", "locsim_pen_jogo11", "LocSim@5 pen., jogo 11"),
                  ("0,733", "acc5_pen", "acurácia a 5 px, penalizada"), ("0,733", "acc5_cob", "acurácia a 5 px, nos cobertos")):
    C(t, f"B4, teto do sistema: {d}", B134, {"conjunto": TI, "serie": SIS}, col, sec="6")
C("0,934", "B4, teto do sistema no conjunto comum: LocSim@5 pen.", B134, {"conjunto": CC, "serie": SIS}, "locsim_pen", sec="6")
C("0,794", "B4, teto do sistema no conjunto comum: acurácia a 5 px", B134, {"conjunto": CC, "serie": SIS}, "acc5_pen", sec="6")
for serie, t in (("6a Bassek", "0,054"), ("6a robusto", "0,117"), ("Kalman + RTS", "0,142"), ("6c fluxo", "0,656"), ("6c sem linhas", "0,588"),
                 ("6c sem fluxo", "−0,106"), ("6c âncora ingênua /150", "0,303"), ("6c âncora de gabarito", "0,684")):
    C(t, f"B4, fração ao teto do sistema: {serie}", f"{POS}/B4_fracao.csv", {"serie": serie}, "fracao_teto_sistema", sec="6, 9")
C("0,946", "B1, H_gt pelas linhas como predição: LocSim@5 nos frames com gabarito (test)", B134, {"conjunto": TI, "serie": "H_gt pelas linhas"},
  "locsim_cob", sec="Resumo, 4, 6, 9")
C("0,978", "B1, H_gt_auxflow como predição: LocSim@5 nos frames com ela (test)", B134, {"conjunto": TI, "serie": "H_gt_auxflow"}, "locsim_cob", sec="4, 6")
for serie, (tp, tc, cp) in (("detector", ("0,387", "0,784", "0,784")), ("6a Bassek", ("0,398", "0,599", "0,735")), ("6a robusto", ("0,430", "0,662", "0,779")),
                            ("Kalman + RTS", ("0,419", "0,631", "0,760")), ("6c fluxo", ("0,551", "0,613", "0,807")),
                            ("6c sem linhas", ("0,508", "0,566", "0,787")), ("6c âncora de gabarito", ("0,576", "0,641", "0,829")),
                            ("H_gt pelas linhas", ("0,849", "0,869", "0,904")), ("H_gt_auxflow", ("0,515", "0,533", "0,545"))):
    k = {"detector": "acc_det", "6c fluxo": "acc_c6"}.get(serie)
    C(tp, f"B3, acurácia a 5 px penalizada, test inteiro: {serie}", B134, {"conjunto": TI, "serie": serie}, "acc5_pen", sec="6")
    C(tc, f"B3, acurácia a 5 px nos cobertos, test inteiro: {serie}", B134, {"conjunto": TI, "serie": serie}, "acc5_cob", sec="6")
    C(cp, f"B3, acurácia a 5 px penalizada, conjunto comum: {serie}", B134, {"conjunto": CC, "serie": serie}, "acc5_pen", key=k, sec="6, 9")
D("11", "B3: redução do erro (1 − acurácia a 5 px) no conjunto comum, detector -> propagação (%)", "(acc_c6 − acc_det) / (1 − acc_det)",
  lambda v: 100 * (v["acc_c6"] - v["acc_det"]) / (1 - v["acc_det"]), sec="6")
B2T = {"clipe": "todos"}
for serie, cols in (("6a Bassek", (("20,9", "pen_media", 100), ("0,0", "pen_mediana", 100), ("0,396", "cob_fr", 1), ("52,9", "cob_media", 100))),
                    ("6a robusto", (("24,5", "pen_media", 100), ("0,0", "pen_mediana", 100), ("0,371", "cob_fr", 1)))):
    for t, col, esc in cols:
        C(t, f"B2, HSB, {serie}: {col}", f"{POS}/B2.csv", B2T | {"serie": serie}, col, esc, sec="6")
B5 = f"{POS}/B5.csv"
B5A = {"ruído": "ruído gaussiano, σ = 5, 10 e 20 (8 bits)", "borrão": "borrão de movimento horizontal, núcleo linear 1 × k",
       "sombra": "sombra: faixa por uma reta que passa pelo centroide", "oclusão": "oclusão: elipses cheias, uma por",
       "medidas": "fração das aceitas com IoU do campo inteiro < 0,8", "dados": "WC14 `train_val` (209 imagens), nunca o test. Script `scripts/relatorio/degradacao.py`"}
for t, d, a in (("5", "ruído σ = 5", "ruído"), ("10", "ruído σ = 10", "ruído"), ("20", "ruído σ = 20", "ruído"), ("11", "núcleo do borrão de 11 px", "borrão"),
                ("21", "núcleo do borrão de 21 px", "borrão"), ("0,7", "sombra: L* × 0,7", "sombra"), ("0,5", "sombra: L* × 0,5", "sombra"),
                ("0,35", "sombra: L* × 0,35", "sombra"), ("0,05", "sombra: rampa de 0,05·h", "sombra"), ("0,6", "oclusão: elipse de 0,6 m de largura", "oclusão"),
                ("1,8", "oclusão: elipse de 1,8 m de altura", "oclusão"), ("0,8", "aceita errada: IoU do campo inteiro < 0,8", "medidas"),
                ("209", "imagens do WC14 train_val", "dados")):
    X(t, f"B5, protocolo: {d}", DEC, B5A[a], sec="6, B")
LV = lambda deg, nv: {"degradacao": deg, "nivel": str(nv)}
for t, deg, nv, col, d in (("0,9861", "limpa", 0, "gramado_iou", "IoU do gramado na imagem limpa"), ("0,612", "limpa", 0, "marcas_cob2", "cobertura das marcações a 2 px, limpa"),
                           ("0,517", "limpa", 0, "det_cobertura", "cobertura do detector, limpa"), ("0,102", "limpa", 0, "det_aceitas_erradas", "aceitas erradas, limpa"),
                           ("0,708", "ruído", 2, "gramado_iou", "IoU do gramado, ruído σ = 10"), ("0,244", "ruído", 2, "det_cobertura", "cobertura do detector, ruído σ = 10"),
                           ("0,004", "ruído", 3, "gramado_iou", "IoU do gramado, ruído σ = 20"), ("0,000", "ruído", 3, "det_cobertura", "cobertura do detector, ruído σ = 20 (nenhuma imagem)"),
                           ("0,543", "borrão", 2, "marcas_cob2", "cobertura das marcações, borrão de 11 px"),
                           ("0,077", "borrão", 3, "det_cobertura", "cobertura do detector, borrão de 21 px"),
                           ("0,375", "borrão", 3, "det_aceitas_erradas", "aceitas erradas, borrão de 21 px"),
                           ("0,526", "sombra", 2, "marcas_cob2", "cobertura das marcações, sombra L* × 0,5"),
                           ("0,969", "sombra", 3, "gramado_iou", "IoU do gramado, sombra L* × 0,35"),
                           ("0,533", "oclusão", 3, "marcas_cob2", "cobertura das marcações, oclusão de 20%"),
                           ("0,478", "oclusão", 3, "det_cobertura", "cobertura do detector, oclusão de 20%"),
                           ("0,889", "borrão", 3, "det_iou_mediano", "menor IoU do campo inteiro mediano entre os níveis com resposta (borrão de 21 px)"),
                           ("0,930", "ruído", 1, "det_iou_mediano", "maior IoU do campo inteiro mediano entre os níveis com resposta (ruído σ = 5)")):
    C(t, f"B5: {d}", B5, LV(deg, nv), col, key={"0,077": "b5_cob21"}.get(t), sec="6")
D("16", "B5: imagens aceitas com o borrão de 21 px (0,077 × 209)", "cobertura × 209", lambda v: v["b5_cob21"] * 209, sec="6")
X("10", "B5: queda de mais de 10% em relação à imagem limpa (\"quebra\")", DEC, "cai mais de 10% em relação à imagem limpa", sec="6")
X("960", "escala da acurácia contra as linhas (960 × 540)", CFG, "sncalib_size: [960, 540]", sec="5")
X("540", "escala da acurácia contra as linhas (960 × 540)", CFG, "sncalib_size: [960, 540]", sec="5")
X("20", "limiares da acurácia (5, 10, 20 px)", CFG, "sncalib_thresholds_px: [5, 10, 20]", sec="5, 6")


# ------------------------------------------------------------------ fontes
_cache = {}


def _lines(path):
    if path not in _cache:
        _cache[path] = Path(path).read_text(encoding="utf-8").splitlines()
    return _cache[path]


def parse(txt):
    """Número como escrito no texto -> (valor, casas decimais)."""
    s = txt.replace("−", "-").replace("+", "")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    dec = len(s.split(",")[1]) if "," in s else 0
    return float(s.replace(",", ".")), dec


def variants(txt):
    s = txt.replace("−", "-")
    out = {txt, s, s.lstrip("+"), txt.lstrip("+−-")}
    if re.fullmatch(r"[+-]?\d{1,3}(\.\d{3})+", s):
        out.add(s.replace(".", "").lstrip("+"))
    out |= {v.replace(",", ".") for v in list(out)}
    return out


def resolve(e, values):
    """Confere a entrada; devolve (ok, linha, coluna, valor na origem, mensagem)."""
    if e["tipo"] == "csv":
        L = _lines(e["src"])
        head = next(csv.reader([L[0]]))
        for i, line in enumerate(L[1:], 2):
            row = dict(zip(head, next(csv.reader([line]))))
            if all(row.get(k) == v for k, v in e["sel"].items()) and row.get(e["col"], "") != "":
                raw = float(row[e["col"]])
                val, dec = parse(e["txt"])
                ok = math.isclose(round(raw * e["esc"], dec), val, abs_tol=1e-9)
                if e["key"]:
                    values[e["key"]] = raw
                return ok, i, e["col"] + (" × 100" if e["esc"] == 100 else ""), row[e["col"]], "" if ok else f"CSV dá {raw * e['esc']}"
        return False, None, e["col"], None, f"linha {e['sel']} não achada"
    if e["tipo"] == "txt":
        for i, line in enumerate(_lines(e["src"]), 1):
            if e["anchor"] in line:
                ok = any(re.search(r"(?<![\d,])(?<!\d\.)" + re.escape(v) + r"(?![\d])", line) for v in variants(e["txt"]))
                if e["key"]:
                    values[e["key"]] = parse(e["txt"])[0]
                return ok, i, "—", "(no texto da linha)", "" if ok else "número não está na linha"
        return False, None, "—", None, f"trecho não achado: {e['anchor']!r}"
    try:
        got = e["fn"](values)
    except KeyError as k:
        return False, None, "—", None, f"entrada {k} ainda não resolvida"
    val, dec = parse(e["txt"])
    ok = math.isfinite(got) and math.isclose(round(got, dec), val, abs_tol=1e-9)
    if e["key"]:
        values[e["key"]] = got
    return ok, None, "—", f"{got:.6g}", "" if ok else f"conta dá {got}"


# ------------------------------------------------------------------ completude
IGNORE = [r"`[^`]*`", r"SNGS-\d+", r"\bf\d+\b", r"\bT\d+b?\b", r"\b\d[a-c]\b", r"@\d+", r"\bFiguras? \d+", r"\b[Tt]abelas? \d+(?: e \d+)?",
          r"\bTabela A\d+", r"\b[Ss]eç(?:ão|ões) \d+(?:\.\d+)?(?: e \d+(?:\.\d+)?)?", r"\bApêndice [AB]", r"\bFatias? \d+", r"\b[Ee]tapas? \d+(?:-\d+)?",
          r"\bjogo \d+", r"\bframe \d+", r"\b(?:19|20)\d\d\b", r"\(\d\)", r"HRNetv\d", r"i\d-\d+K", r"\d+X\b", r"\bd²", r"τ²"]


def body_tokens(text):
    """Números do corpo: sem o cabeçalho YAML, os títulos, as referências e o Apêndice A."""
    text = re.sub(r"\A---.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"\n# Referências.*?(?=\n# Apêndice B)", "\n", text, flags=re.S)
    out = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        line = re.sub(r"^\s*\d+\.\s", "", line)                      # item de lista numerada
        line = re.sub(r"!\[[^\]]*\]\(([^)]*)\)", lambda m: m.group(0).replace(m.group(1), ""), line)   # caminho da figura
        for pat in IGNORE:
            line = re.sub(pat, " ", line)
        out += re.findall(r"(?<![\w,.])[+−-]?\d+(?:\.\d{3})*(?:,\d+)?(?![\w])", line)
    return out


# ------------------------------------------------------------------ Apêndice A
def _t(name, d=TAB):
    return list(csv.DictReader(open(f"{d}/{name}.csv", encoding="utf-8")))


def f(x, d=3, pct=False):
    if x in ("", None):
        return "—"
    x = float(x) * (100 if pct else 1)
    if not math.isfinite(x):
        return "—"
    s = f"{x:.{d}f}".replace(".", ",")
    return s.replace("-", "−")


MM = "mín.–máx. por jogo (bootstrap de 3 jogos)"


def mm(r, c, d=3):
    """Intervalo do bootstrap de jogos: com 3 jogos, o mínimo e o máximo entre eles (T6)."""
    if r.get(c + "_lo", "") in ("", "nan"):
        return "—"
    lo, hi = f(r[c + "_lo"], d), f(r[c + "_hi"], d)
    return f"{lo} a {hi}" if lo.startswith("−") else f"{lo}–{hi}"


def milhar(x):
    return f"{int(float(x)):,}".replace(",", ".")


def table(head, rows, caption):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows] + ["", f": {caption}", ""])


NAMES = {"6a Bassek": "suavização S-G (Bassek)", "6a robusto": "S-G robusta", "6c fluxo": "propagação", "6c sem linhas": "propagação sem linhas",
         "6c sem fluxo": "propagação sem fluxo", "6c âncora ingênua /150": "âncora ingênua /150",
         "6c âncora de gabarito": "teto condicionado às âncoras", "teto do sistema (âncora de gabarito /150)": "teto do sistema (âncora de gabarito /150)"}
n = lambda s: NAMES.get(s, s)


def apendice():
    t1 = _t("T1")
    out = ["Geradas por `scripts/relatorio/numeros.py` a partir dos CSVs da rodada (`outputs/runs/rodada_test/tabelas/`), cada um com o commit do "
           "método e o dos scripts das tabelas, e, nas tabelas marcadas, das análises posteriores à rodada "
           "(`outputs/runs/rodada_test/pos_rodada/`). A coluna \"" + MM + "\" é o intervalo de 95% do bootstrap que sorteia jogos "
           "(2.000 reamostragens): com 3 jogos, há só 10 reamostragens distintas, e o intervalo é o mínimo e o máximo entre os jogos (T6). "
           "O teto condicionado às âncoras é a propagação a partir da homografia de gabarito nos frames das âncoras verificadas.", ""]
    out.append(table(["Série", "Cobertura", MM, "NPE mediano (média)", "IoU_whole mediano", "mAP-LocSim penalizado", MM],
                     [[n(r["serie"]), f(r["cobertura"]), mm(r, "cobertura"), f"{f(r['npe_med'], 4)} ({f(r['npe_media'])})", f(r["iou_med"]),
                       f(r["map_pen"]), mm(r, "map_pen")] for r in t1],
                     "Tabela T1 (a) — GSR test, 49 clipes, 3 jogos: cobertura e geometria."))
    out.append(table(["Série", "LocSim@5 penalizado", MM, "Nos cobertos", MM],
                     [[n(r["serie"]), f(r["locsim_pen"]), mm(r, "locsim_pen"), f(r["locsim_cob"]), mm(r, "locsim_cob")] for r in t1],
                     "Tabela T1 (b) — GSR test: LocSim@5."))
    out.append(table(["Série", "Penalizado, clipes com âncora", MM, "Fração ao teto condicionado", MM],
                     [[n(r["serie"]), f(r["locsim_pen_com_ancora"]), mm(r, "locsim_pen_com_ancora"), f(r["fracao_teto"]), mm(r, "fracao_teto")] for r in t1],
                     "Tabela T1 (c) — GSR test: LocSim@5 penalizado nos 44 clipes com âncora e fração da distância ao teto condicionado às âncoras, "
                     "(série − detector) / (teto − detector)."))
    t1b = _t("T1b")
    out.append(table(["Série", "NPE mediano", "LocSim@5 penalizado", "Nos cobertos"],
                     [[n(r["serie"]), f(r["npe_med"], 4), f(r["locsim_pen"]), f(r["locsim_cob"])] for r in t1b],
                     f"Tabela T1b — Conjunto comum: os {int(t1b[0]['frames']):,} frames com homografia do detector.".replace(",", ".")))
    t2 = _t("T2")
    k = lambda r, m, c: f(r.get(f"{m} {c}", ""), 1, pct=True)
    rows = []
    for r in [r for r in t2 if r["clipe"] != "todos"]:
        rows.append([r["clipe"], f"{r['inicio']}–{r['fim']}", f(r["locsim5_nbjw"], 1, pct=True),
                     f"{k(r, '(1) só propagação', 'pen média')} / {f(r['(1) só propagação cobertura frames com pessoas'], 2)}",
                     f"{k(r, '(2) detector', 'pen média')} / {k(r, '(2) detector', 'cob média')} / {f(r['(2) detector cobertura frames com pessoas'], 2)}",
                     f"{k(r, '(3) pipeline', 'pen média')} / {k(r, '(3) pipeline', 'cob média')} / {f(r['(3) pipeline cobertura frames com pessoas'], 2)}"])
    out.append(table(["Clipe", "Intervalo", "NBJW (tab. 3)", "(1) só propagação: penalizado / cobertura", "(2) detector: penalizado / nos cobertos / cobertura",
                      "(3) pipeline: penalizado / nos cobertos / cobertura"],
                     rows, "Tabela T2 (a) — HSB por clipe: LocSim@5 médio por frame (%), penalizado e nos cobertos, e cobertura nos frames com pessoas. "
                           "Os intervalos seguem a numeração do artigo do AuxFlow, a partir de 0."))
    agg = {}
    for r in [r for r in t2 if r["clipe"] == "todos"]:
        agg.update({c: v for c, v in r.items() if v != ""})
    rows = [[m, f"{k(agg, m, 'pen média')} / {k(agg, m, 'pen mediana')}", f"{k(agg, m, 'cob média')} / {k(agg, m, 'cob mediana')}",
             f(agg[f"{m} cobertura"]), f(agg[f"{m} cobertura frames com pessoas"]), f(agg[f"{m} cobertura por pessoa"]),
             f"{k(agg, m, 'pen por pessoa-frame')} / {k(agg, m, 'cob por pessoa-frame')}"] for m in ("(1) só propagação", "(2) detector", "(3) pipeline")]
    out.append(table(["Medição", "Penalizado: média / mediana", "Cobertos: média / mediana", "Cobertura (frames com H_gt)", "Cobertura (frames com pessoas)",
                      "Cobertura (por pessoa)", "Por pessoa-frame: pen. / cob."], rows,
                     "Tabela T2 (b) — HSB, todos os frames dos intervalos (%). AuxFlow, tabela 4 (média / mediana): NBJW 43,15 / 35,93; AuxFlow 83,67 / 96,15."))
    b2 = {r["serie"]: r for r in _t("B2", POS) if r["clipe"] == "todos"}
    out.append(table(["Série", "Penalizado: média / mediana", "Cobertos: média / mediana", "Cobertura (frames com H_gt)", "Cobertura (frames com pessoas)",
                      "Cobertura (por pessoa)", "Por pessoa-frame: pen. / cob."],
                     [[n(s), f"{f(r['pen_media'], 1, True)} / {f(r['pen_mediana'], 1, True)}", f"{f(r['cob_media'], 1, True)} / {f(r['cob_mediana'], 1, True)}",
                       f(r["cob_gt"]), f(r["cob_fr"]), f(r["cob_ps"]), f"{f(r['pen_ps'], 1, True)} / {f(r['cob_ps_ls'], 1, True)}"]
                      for s, r in b2.items() if s in ("6a Bassek", "6a robusto")],
                     "Tabela T2 (c) — Análise posterior à rodada: as suavizações S-G sobre a série do detector, nos mesmos frames do HSB e com as "
                     "colunas da T2 (b) (%)."))
    t3 = {r["metrica"]: r for r in _t("T3")}
    out.append(table(["Cobertura", "IoU_whole (média / mediana)", "IoU_part (média / mediana)", "NPE (média / mediana)", "RE em m (média / mediana)"],
                     [[f(t3["cobertura"]["media"]), *(f"{f(t3[m]['media'], d)} / {f(t3[m]['mediana'], d)}" for m, d in
                                                      (("iou_whole", 3), ("iou_part", 3), ("npe", 4), ("re_m", 3)))]],
                     f"Tabela T3 — WC14 test, {t3['frames']['media']} imagens, só o detector, molde 105 × 68 m."))
    out.append(table(["Métrica", "Média", "Mediana", "Imagens"], [[r["metrica"], f(r["media"], 4), f(r["mediana"], 4), r["imagens"]] for r in _t("T3b")],
                     "Tabela T3b — WC14 test no protocolo KpSFR (código deles sem mudança, molde 100 × 60 m). O protocolo foi aplicado só nas imagens com "
                     "homografia; a literatura o reporta sobre todas. As duas últimas linhas seguem a nossa convenção: imagem sem homografia vale 0."))
    t4 = _t("T4")
    out.append(table(["Série", "Cobertura", "Tremor mediano / p90 (px)", "Deslize mediano / p90 (px)", "Pares"],
                     [[n(r["serie"]), f(r["cobertura"]), f"{f(r['tremor_med'], 2)} / {f(r['tremor_p90'], 2)}", f"{f(r['deslize_med'], 2)} / {f(r['deslize_p90'], 2)}",
                       f"{int(r['pares']):,}".replace(",", ".")] for r in t4],
                     "Tabela T4 (a) — Estabilidade no GSR test, cada série no próprio conjunto de frames. O ECC convergiu em todos os pares."))
    out.append(table(["Série", "Jogadores invertidos: pen. / cobertos", "Grade: pen. / cobertos", "0 visíveis: pen. / cobertos"],
                     [[n(r["serie"]), f"{f(r['jogadores_penalizada'])} / {f(r['jogadores_só cobertos'])}", f"{f(r['grade_penalizada'])} / {f(r['grade_só cobertos'])}",
                       f"{f(r['zero_visiveis_penalizada'])} / {f(r['zero_visiveis_só cobertos'])}"] for r in t4],
                     "Tabela T4 (b) — Visibilidade no GSR test: fração de jogadores-frame jogados para fora do quadro, de pontos da grade com rótulo trocado e "
                     "de frames com 0 jogadores visíveis, penalizada (frame sem homografia conta como erro) e só nos frames cobertos."))
    out.append(table(["Série", "Tremor mediano / p90 (px), trios", "Deslize mediano / p90 (px), pares", "Jogadores invertidos", "0 visíveis"],
                     [[n(r["serie"]), f"{f(r['tremor_med'], 2)} / {f(r['tremor_p90'], 2)} ({milhar(r['trios'])})",
                       f"{f(r['deslize_med'], 2)} / {f(r['deslize_p90'], 2)} ({milhar(r['pares'])})", f(r["jogadores"]), f(r["zero_visiveis"])]
                      for r in _t("T4b")],
                     "Tabela T4b — Estabilidade e visibilidade na interseção dos frames cobertos pelas cinco séries (detector, suavização S-G "
                     "(Bassek), S-G robusta, Kalman + RTS e propagação)."))
    rows = []
    lin = lambda s: s.replace(" - ", " − ").replace("6c fluxo", "propagação").replace("nosso propagação", "nossa propagação").replace("6c", "propagação")
    for r in _t("T5"):
        sg = "+" if r["linha"].startswith("ganho") else ""
        if r["locsim5"]:
            rows.append([lin(r["linha"]), sg + f(r["locsim5"]), "—", "—", "—", "—"])
        else:
            rows.append([lin(r["linha"]), sg + f(r["pen"]), mm(r, "pen"), f(r["cob"]), mm(r, "cob"), f(r["comum"])])
    out.append(table(["Linha", "LocSim@5 (penalizado, no nosso caso)", MM, "Nos cobertos", MM, "Conjunto comum (nos cobertos)"], rows,
                     "Tabela T5 — Comparação com a tabela 7 do AuxFlow. O LocSim deles não tem frames sem homografia; o nosso é agregado sobre "
                     "pessoas-frame, e a pessoa de frame sem homografia vale 0."))
    out.append(table(["Jogo", "Clipes", "Com âncora", "Frames", "Cobertura detector / propagação", "LocSim@5 pen.: detector / propagação / teto condicionado"],
                     [[r["jogo"], r["clipes"], r["com_ancora"], f"{int(r['frames']):,}".replace(",", "."), f"{f(r['cob_detector'])} / {f(r['cob_6c'])}",
                       f"{f(r['locsim_pen_detector'])} / {f(r['locsim_pen_6c'])} / {f(r['locsim_pen_teto'])}"] for r in _t("T6")],
                     "Tabela T6 — GSR test por jogo."))
    t7 = _t("T7")
    out.append(table(["Conjunto", "Número", "Com gabarito", "Erradas (NPE > 0,05)"],
                     [[r["conjunto"], r["n"], r["com_gabarito"] or "—", (f"{r['erradas']} ({f(int(r['erradas']) / int(r['com_gabarito']), 1, pct=True)}%)"
                                                                         if r["erradas"] else r["lista"].replace(" ", ", "))] for r in t7],
                     "Tabela T7 — Âncoras no GSR test."))
    out.append(table(["Lacuna", "Frames", "suavização S-G (Bassek)", "S-G robusta", "propagação", "propagação sem linhas"],
                     [[r["lacuna"].replace("-", "–"), milhar(r["frames"]), *(f"{f(r[s + ' cob'])} / {f(r[s + ' NPE'], 4)}" for s in
                                                                                 ("6a Bassek", "6a robusto", "6c fluxo", "6c sem linhas"))] for r in _t("T8")],
                     "Tabela T8 — Lacunas do detector no GSR test: cobertura / NPE mediano. As pontas são lacunas que tocam o começo ou o fim do clipe."))
    t9 = _t("T9")
    out.append(table(["Etapa", "Processos", "Parede (h)", "Vazão (frames/s)", "ms por frame num processo", "s por clipe num processo", "s por clipe de parede"],
                     [[r["etapa"].replace("6c", "propagação"), r["processos"], f(r["parede_h"], 2), f(r["frames_por_s"], 2), f"{float(r['ms_por_frame_processo']):,.0f}".replace(",", "."),
                       f"{float(r['s_por_clipe_processo']):,.0f}".replace(",", "."), f(r["s_por_clipe_parede"], 0)] for r in t9 if r["processos"]],
                     "Tabela T9 (a) — Custo na rodada do test (AMD Ryzen 7 5700X, 8 núcleos e 16 threads, com RTX 5060; o detector em CPU, as máscaras da "
                     "propagação em GPU). Com 15 processos em 8 núcleos, o custo por frame num processo é maior que o do perfil num núcleo sem concorrência "
                     "(4,76 s por frame no detector; 127 ms na propagação)."))
    out.append(table(["Etapa (AuxFlow)", "Lote", "Tempo por clipe (s)", "FPS"],
                     [[r["etapa"].replace("AuxFlow ", ""), r["lote"], r["s_por_clipe"], f(r["fps"], 1)] for r in t9 if not r["processos"]],
                     "Tabela T9 (b) — Tabela 6 do AuxFlow, por clipe de 750 frames (i7-8700K com RTX 4090; o lote é o tamanho do lote na GPU ou o "
                     "número de threads)."))
    b = _t("B1_B3_B4", POS)
    fr = {r["serie"]: r["fracao_teto_sistema"] for r in _t("B4_fracao", POS)}
    acc = lambda r, k: " / ".join(f(r[f"acc{t}_{k}"]) for t in (5, 10, 20))
    for conj, cap in (("test inteiro", "Tabela T10 (a) — Análise posterior à rodada, GSR test inteiro: o teto do sistema (âncora de gabarito no primeiro frame "
                                       "com gabarito de cada bloco de 150 frames, com a mesma propagação), as duas homografias de gabarito como predição e "
                                       "a acurácia contra as linhas anotadas (contagem do SN-Calib, 960 × 540). Acurácia penalizada: frame com linhas "
                                       "anotadas e sem homografia vale 0. A fração ao teto do sistema é (série − detector) / (teto do sistema − detector), "
                                       "no LocSim@5 penalizado."),
                      ("conjunto comum", "Tabela T10 (b) — O mesmo, no conjunto comum: os frames com homografia do detector.")):
        rs = [r for r in b if r["conjunto"] == conj]
        head = ["Série", "Cobertura", "NPE mediano", "LocSim@5 pen.", "Nos cobertos", "Acurácia 5 / 10 / 20 px, pen.", "Acurácia 5 / 10 / 20 px, cobertos"]
        rows = [[n(r["serie"]), f(r["cobertura"]), f(r["npe_med"], 4), f(r["locsim_pen"]), f(r["locsim_cob"]), acc(r, "pen"), acc(r, "cob")] for r in rs]
        if conj == "test inteiro":
            head.append("Fração ao teto do sistema")
            rows = [x + [f(fr.get(r["serie"], "")) if r["serie"] != "detector" else "—"] for x, r in zip(rows, rs)]
        out.append(table(head, rows, cap))
    b5 = [r for r in _t("B5", POS) if r["nivel"] != "quebra"]
    out.append(table(["Degradação", "Nível", "Gramado: IoU", "Marcações: cobertura a 2 px", "Marcações: precisão a 3 px", "Retas: recall de linhas",
                      "Detector: cobertura", "IoU do campo inteiro mediano", "Aceitas erradas (IoU < 0,8)"],
                     [[r["degradacao"], r["valor"].replace(".", ",") if r["valor"] else "—", f(r["gramado_iou"]), f(r["marcas_cob2"]), f(r["marcas_prec3"]),
                       f(r["recall_linhas"]), f(r["det_cobertura"]), f(r["det_iou_mediano"]), f(r["det_aceitas_erradas"])] for r in b5],
                     "Tabela T11 — Análise posterior à rodada, WC14 train_val (209 imagens): robustez a degradações sintéticas, uma de cada vez "
                     "(ruído: σ em 8 bits; borrão horizontal: núcleo em px; sombra: fator do L* na faixa; oclusão: fração do gramado coberta). "
                     "Médias por imagem no gramado e nas marcações; recall de linhas somado nas imagens."))
    return "\n".join(out).rstrip() + "\n"


def numeros_md(res):
    head = ("# Números do relatório e a origem de cada um\n\n"
            "Gerado por `scripts/relatorio/numeros.py`, que confere cada linha: o valor da origem, arredondado às casas do texto, tem que ser o "
            "número do texto. Nas origens em CSV, a linha conta o cabeçalho como linha 1; nas origens em texto, a linha é a do arquivo; as "
            "contas (derivados) dizem a expressão. A completude também é conferida: todo número do corpo do relatório tem uma linha aqui. "
            "Ficam de fora só os identificadores (clipes, frames, nomes de tabela, figura, seção, etapa, fatia e jogo, anos de citação e "
            "trechos de código).\n\n"
            "O Apêndice A (tabelas T1 a T9) é gerado pelo mesmo script a partir de `outputs/runs/rodada_test/tabelas/T*.csv`: cada célula "
            "vem da linha e da coluna do CSV de mesmo nome, e o script confere que o apêndice no relatório é o gerado.\n\n"
            "| nº | número no texto | o que é | seção | origem | linha | coluna | valor na origem |\n|---|---|---|---|---|---|---|---|\n")
    rows = []
    for i, (e, (ok, line, col, raw, msg)) in enumerate(zip(NUMEROS, res), 1):
        src = e.get("src") or f"derivado: {e['expr']}"
        rows.append(f"| {i} | {e['txt']} | {e['desc']} | {e['sec']} | `{src}` | {line or '—'} | {col} | {raw} |")
    return head + "\n".join(rows) + "\n"


if __name__ == "__main__":
    values, res = {}, [None] * len(NUMEROS)
    for derived in (False, True):                        # as contas por último: usam valores de qualquer entrada
        for k, e in enumerate(NUMEROS):
            if (e["tipo"] == "der") == derived:
                res[k] = resolve(e, values)
    bad = [(e, r) for e, r in zip(NUMEROS, res) if not r[0]]
    for e, r in bad:
        print(f"ORIGEM NÃO CONFERE: {e['txt']!r} ({e['desc']}): {r[4]}")
    text = REL.read_text(encoding="utf-8")
    known = {e["txt"] for e in NUMEROS}
    missing = sorted(set(t for t in body_tokens(text) if t not in known), key=lambda s: (len(s), s))
    for t in missing:
        print(f"SEM ORIGEM NA LISTA: {t!r}")
    gen = apendice()
    m = re.search(r"\n# Apêndice A[^\n]*\n\n(.*?)\n# Apêndice B", text, flags=re.S)
    if "--escrever" in sys.argv:
        new = text[:m.start(1)] + gen + text[m.end(1) - 1:] if m else text
        REL.write_text(new, encoding="utf-8")
        OUT_MD.write_text(numeros_md(res), encoding="utf-8")
        print(f"gravados: Apêndice A em {REL}; {OUT_MD} ({len(NUMEROS)} entradas)")
    elif not m or m.group(1).rstrip() + "\n" != gen:
        print("APÊNDICE A diferente do gerado (rode com --escrever)")
        bad.append(None)
    print(f"{len(NUMEROS)} entradas; {len(bad)} sem conferir; {len(missing)} números sem origem")
    sys.exit(1 if bad or missing else 0)
