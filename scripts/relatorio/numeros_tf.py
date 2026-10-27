"""Números do trabalho final (docs/trabalho-final.md): cada número do texto com a origem, conferido, no estilo de
scripts/relatorio/numeros_v2.py (de onde vêm a conferência de CSV, texto, conta e JSON e a completude).

- Entradas: R (linha dos arquivos de números dos relatórios, já conferidos por numeros.py e numeros_v2.py), C (célula
  de CSV), X (linha de documento, como o docs/decisoes.md), D (conta sobre outras entradas) e J (valor de JSON).
- R confere que o arquivo de números tem uma linha com o mesmo número no texto e com `anchor` na coluna "o que é".
- Tabelas copiadas dos relatórios ficam entre <!-- copia: arquivo | legenda --> e <!-- fim: copia -->: as linhas da
  tabela têm que ser as da tabela de mesma legenda (prefixo) no arquivo; a legenda nova entra na completude.
- Completude: todo número do corpo, fora das linhas das tabelas copiadas, dos blocos de código e das referências, tem
  uma entrada.

Uso (da raiz, PYTHONPATH=.): numeros_tf.py [--escrever]. Sem a opção, só confere (código 1 se algo falhar); com
ela, grava também o docs/trabalho-final-numeros.md.

As entradas P (frase de artigo da pasta do projeto) exigem o `pdftotext` do poppler no PATH: o script roda no Git
Bash, que o traz em /mingw64/bin. Sem ele, o script para com uma mensagem, em vez de passar sem conferir."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.relatorio import numeros as N
from scripts.relatorio import numeros_v2 as V

REL = Path("docs/trabalho-final.md")
OUT_MD = Path("docs/trabalho-final-numeros.md")
NUM = {"v1": "docs/04-relatorio-numeros.md", "v2": "docs/04-relatorio-v2-numeros.md"}
DEC = "docs/decisoes.md"
N.IGNORE[:0] = [r"\d+†"]                                        # ano da citação herdada, com a marca

NUMEROS = []


def R(txt, rel, anchor, sec=""):
    NUMEROS.append(dict(tipo="num", txt=txt, desc=anchor, src=NUM[rel], sec=sec))


def C(txt, desc, src, sel, col, esc=1, key=None, sec=""):
    NUMEROS.append(dict(tipo="csv", txt=txt, desc=desc, src=V._src(src), sel=sel, col=col, esc=esc, key=key, sec=sec))


def X(txt, desc, src, anchor, key=None, sec=""):
    NUMEROS.append(dict(tipo="txt", txt=txt, desc=desc, src=src, anchor=anchor, key=key, sec=sec))


def D(txt, desc, expr, fn, key=None, sec=""):
    NUMEROS.append(dict(tipo="der", txt=txt, desc=desc, expr=expr, fn=fn, key=key, sec=sec))


def J(txt, desc, src, path, esc=1, key=None, sec=""):
    NUMEROS.append(dict(tipo="json", txt=txt, desc=desc, src=src, path=path, esc=esc, key=key, sec=sec))


def P(txt, desc, pdf, page, anchor, sec=""):
    """Frase de artigo da pasta do projeto: `anchor` está na página `page` do PDF e contém o número (ou o número é a
    própria página, citada no texto como "p. N")."""
    NUMEROS.append(dict(tipo="pdf", txt=txt, desc=desc, src=f"{PDFS}/{pdf}", page=page, anchor=anchor, sec=sec))


PDFS = "C:/Users/victo/Downloads/Topicos Av pdi"                  # pasta dos artigos do projeto, fora do repositório
BT = "BroadTrack__Broadcast Camera Tracking for Soccer_compressed.pdf"
BA = "Broadcast analytics.pdf"                                     # Bassek et al. (2025)
GS = "SoccerNet Game State Reconstruction__End-to-End Athlete Tracking and Identification on a Minimap_compressed.pdf"


# ------------------------------------------------------------------ Resumo
S0 = "Resumo"
R("49", "v2", "clipes do GSR test", S0)
R("3", "v1", "jogos do GSR test", S0)
R("0,505", "v1", "cobertura do detector, GSR test", S0)
R("0,419", "v1", "LocSim@5 penalizado do detector", S0)
R("0,897", "v1", "cobertura do 6c fluxo", S0)
R("0,749", "v1", "LocSim@5 penalizado do 6c fluxo", S0)
R("0,650", "v1", "LocSim@5 penalizado do 6c, IC inferior", S0)
R("0,920", "v1", "LocSim@5 penalizado do 6c, IC superior", S0)
R("40", "v1", "redução do erro residual", S0)
R("38", "v1", "redução do erro residual", S0)
R("0,902", "v2", "LocSim@5 penalizado da propagação, v2", S0)
R("0,929", "v1", "AuxFlow", S0)
R("0,946", "v1", "H_gt pelas linhas", S0)

# ------------------------------------------------------------------ 1. introdução
R("3", "v1", "homografia 3 × 3", "1")
P("25", "zoom de até 25× da câmera de transmissão (BroadTrack)", BT, 3, "can zoom up to 25 times", "1")

# ------------------------------------------------------------------ 2. trabalhos relacionados
S2 = "2"
R("0,5", "v1", "BroadTrack reinicia com IoU < 0,5", S2)
for t in ("0,8397", "0,8352", "0,9224", "0,9426", "1,34", "0,84"):
    R(t, "v1", "BroadTrack × AuxFlow no GSR", S2)
R("2,5", "v1", "grade de pontos auxiliares 2,5 × 2 m", S2)
R("2", "v1", "grade de pontos auxiliares 2,5 × 2 m", S2)
R("1", "v1", "erro de ida e volta <= 1 px", S2)
for t, a in (("83,67", "AuxFlow no HSB, média"), ("23,42", "AuxFlow sem fluxo no HSB"), ("78,30", "AuxFlow sem pontos-chave do detector"),
             ("78,71", "RAFT no lugar do Lucas–Kanade"), ("39,68", "amostragem geométrica no AuxFlow"), ("83,39", "amostragem aleatória no AuxFlow"),
             ("150", "âncoras ingênuas a cada 150 frames"), ("82,48", "âncoras ingênuas no AuxFlow"), ("83,48", "detector sem propagação no AuxFlow"),
             ("90,65", "âncoras por heurística no AuxFlow"), ("91,88", "âncora de gabarito no AuxFlow"), ("54,74", "AuxFlow com a H inicial perturbada"),
             ("43,15", "NBJW sozinho no HSB, média"), ("0,885", "LocSim@5 do NBJW, tabela 7 do AuxFlow"),
             ("0,8852", "BHITK no GSR, tabela 7 do AuxFlow"), ("0,8851", "NBJW no GSR, tabela 7 do AuxFlow"),
             ("115", "molde do PnLCalib no WC14"), ("74", "molde do PnLCalib no WC14"), ("100", "molde do KpSFR e de Maglo"), ("60", "molde do KpSFR e de Maglo")):
    R(t, "v1", a, S2)

# Bassek et al. (2025), conferidos no PDF (página do arquivo)
for t, d, p, a in (("31", "janela do Savitzky–Golay", 4, "window length 31 and third-degree polynomial"),
                   ("3", "grau do Savitzky–Golay", 4, "window length 31 and third-degree polynomial"),
                   ("25", "lacunas de até 25 frames interpoladas linearmente", 4, "up to 25 frames (1 second) were interpolated linearly"),
                   ("981", "cortes por partida", 8, "981 cuts per match, or 10.9 cuts per minute"),
                   ("10,9", "cortes por minuto", 8, "981 cuts per match, or 10.9 cuts per minute"),
                   ("1", "só 1 jogador visível no feed de scouting (%)", 8, "only a single player (1% of footage) or no players (3%)"),
                   ("3", "nenhum jogador visível no feed de scouting (%)", 8, "only a single player (1% of footage) or no players (3%)")):
    P(t, f"Bassek et al.: {d}", BA, p, a, "2, 3, 6")
P("8", "Bassek et al.: página dos artefatos do pipeline do campo de visão", BA, 8,
  "field of view detection and filtering pipeline introduced few artifacts", "2")

# ------------------------------------------------------------------ 3. método
for t, a in (("105", "modelo do campo 105 × 68 m"), ("68", "modelo do campo 105 × 68 m"), ("20", "faixa de matiz do gramado"),
             ("0,9861", "IoU médio do gramado no WC14 train_val"), ("15", "limiar das marcações no WC14"), ("30", "limiar das marcações no GSR"),
             ("180", "simetria de 180° do campo"), ("0,45", "portão: fração explicada"), ("0,85", "portão: IoU com o gramado"),
             ("5", "portões logo abaixo do percentil 5"), ("12", "janela das âncoras candidatas")):
    R(t, "v1", a, "3")
# Tabela 2: medidas das Fatias 4 e 5, calibração no treino (GSR train) (entradas de 2026-09-28 do docs/decisoes.md)
for anchor, nums in (("**Elipses: calibração no GSR train, com uma repetição.**", "0,668 0,740 643 0,202 1.105"),
                     ("**Decisões pendentes resolvidas pelo erro da homografia: td da fusão 6/720 e escala única**",
                      "3 720 6 1 2 1.697 0,388 0,0057 3,05 0,418 0,0064 0,58 0,339 0,0060 0,71 0,398 1,02 0,030 0,01"),
                     ("**Fatia 5, pipeline mínimo: diagnóstico e nova verificação**",
                      "60 31 37 84 9 6 4 0,48 300 0,483 0,0216 10 0,467 0,0076 8 0,433 0,0062 24"),
                     ("**Elipses conferidas depois da H e ablação correspondências + RANSAC**", "33 10 7 0,433 0,0058 6 0,417 0,200 0,226 5")):
    for t in nums.split():
        X(t, f"Fatias 4 e 5, calibração no treino (GSR train): {anchor.strip('*')[:60]}", DEC, anchor, sec="3.1, Tabela 2")

# ------------------------------------------------------------------ 4. dados e métricas
for t, a in (("209", "imagens de treino do WC14"), ("186", "imagens do WC14 test"), ("1280", "resolução do WC14"), ("720", "resolução do WC14"),
             ("750", "frames por clipe"), ("1080", "resolução do GSR"), ("57", "clipes de treino do GSR"), ("58", "clipes de validação do GSR"),
             ("16", "clipes do jogo 7"), ("19", "clipes do jogo 8"), ("14", "clipes do jogo 11"),
             ("0,05", "limiar de âncora/H errada (NPE > 0,05)"), ("0,933", "H_gt pelas linhas como predição, train"),
             ("0,9928", "LocSim@5 do gabarito do AuxFlow (tabela 2 deles)"), ("0,978", "H_gt_auxflow como predição: LocSim@5"),
             ("3", "RANSAC a 3 px da H_gt_auxflow"), ("10", "clipes do HSB"), ("0", "numeração dos frames a partir de 0"),
             ("90", "intervalo \"90–0\" do SNGS-128"), ("0", "intervalo \"90–0\" do SNGS-128"),
             ("0,05", "LocSim: exp(ln(0,05)·d²/τ²)"), ("5", "τ = 5 m"), ("0", "pessoa de frame sem H vale 0"), ("10", "mAP-LocSim: τ = 1 a 10 m"),
             ("960", "escala da acurácia contra as linhas"), ("540", "escala da acurácia contra as linhas"), ("20", "limiares da acurácia (5, 10, 20 px)")):
    R(t, "v1", a, "4")

# ------------------------------------------------------------------ 5. protocolo
for t, a in (("2.000", "reamostragens do bootstrap"), ("10", "reamostragens distintas do bootstrap com 3 jogos"), ("95", "intervalo de 95%"),
             ("1.470", "frames da conferência de determinismo"), ("25", "frames da conferência: 1 a cada 25"),
             ("735", "tarefas da série com a chave congelada"), ("47", "caches da valid gravados com a chave errada")):
    R(t, "v1", a, "5")


# ------------------------------------------------------------------ 6. resultados do v1
# (txt, trecho da coluna "o que é" em docs/04-relatorio-numeros.md)
for t, a in (
        ('18', 'clipes sem âncora da valid'),
        ('21', 'B5, protocolo: núcleo do borrão de 21 px'),
        ('50', 'passos da sensibilidade (±50%)'),
        ('62', 'lacunas de 4-25 com as duas bordas erradas (%)'),
        ('65', 'fração da distância detector -> AuxFlow fechada pelo 6c (%)'),
        ('79', 'imagens do WC14 test sem H'),
        ('85', 'fração ao teto nos 19 clipes do train[::3] (%)'),
        ('0,1', 'frames com 0 visíveis do 6c, só cobertos (%)'),
        ('107', 'imagens com H (protocolo KpSFR)'),
        ('126', 's de parede por clipe com 10 processos, 6c com as ablações'),
        ('127', '6c fluxo, ms por frame'),
        ('2,1', 'jogadores invertidos do 6c, só cobertos (%)'),
        ('2,2', 'aceitas erradas, entre as com gabarito (%) = 12 / 557'),
        ('2,6', 'AuxFlow, FPS (tabela 6)'),
        ('280', 'SNGS-136, fim do intervalo do HSB'),
        ('292', 'AuxFlow, s por clipe (tabela 6)'),
        ('4,4', 'jogadores invertidos do Kalman na interseção (%)'),
        ('5,0', 'jogadores invertidos do detector na interseção (%)'),
        ('5,6', 'jogadores invertidos do detector, só cobertos (%)'),
        ('558', 'âncoras aceitas'),
        ('630', 's de parede por clipe com 15 processos, série (máquina inteira)'),
        ('958', 'âncoras candidatas'),
        ('0,02', 'ganho mínimo para virar candidato'),
        ('0,03', 'o 6c fica a menos disto do teto nos três jogos (máximo de teto − 6c: 0,027)'),
        ('0,13', 'tremor_med (px) de Kalman + RTS na interseção (T4b)'),
        ('0,35', 'B5, protocolo: sombra: L* × 0,35'),
        ('0,40', 'tremor_med (px) de 6c fluxo na interseção (T4b)'),
        ('0,57', 'tremor_p90 (px) de Kalman + RTS na interseção (T4b)'),
        ('1,19', 'vazão da série (frames/s)'),
        ('1,29', 'tremor_med (px) de detector na interseção (T4b)'),
        ('1,38', 'deslize_med (px) de 6c fluxo na interseção (T4b)'),
        ('1,43', 'tremor_p90 (px) de 6c fluxo na interseção (T4b)'),
        ('1,90', 'deslize_med (px) de 6a Bassek na interseção (T4b)'),
        ('11,8', 'jogadores invertidos do 6c, penalizada (%)'),
        ('17,7', 'HSB (2) detector, média (%)'),
        ('2,90', 'detector, s por frame num núcleo, WC14'),
        ('20,9', 'B2, HSB, 6a Bassek: pen_media'),
        ('24,5', 'B2, HSB, 6a robusto: pen_media'),
        ('28,3', 'candidatas erradas, entre as com gabarito (%)'),
        ('4,17', 'deslize p90 (px) do 6c no próprio conjunto'),
        ('4,25', 'deslize mediano (px) do 6c sem fluxo'),
        ('4,33', 'deslize_p90 (px) de 6c fluxo na interseção (T4b)'),
        ('4,76', 'detector, s por frame num núcleo, GSR'),
        ('4090', 'hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090)'),
        ('44,2', 'SNGS-136, detector penalizado (%)'),
        ('5,45', 'deslize_p90 (px) de Kalman + RTS na interseção (T4b)'),
        ('50,8', 'SNGS-124, só propagação (%): a menor média do HSB'),
        ('5060', 'hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090)'),
        ('52,9', 'B2, HSB, 6a Bassek: cob_media'),
        ('53,5', 'jogadores invertidos do detector, penalizada (%)'),
        ('61,7', 'HSB (3) pipeline, média (%)'),
        ('79,7', 'HSB (2) detector nos cobertos, média (%)'),
        ('8,31', 'deslize_p90 (px) de 6a Bassek na interseção (T4b)'),
        ('8,58', 'parede da série do detector (h)'),
        ('81,4', 'HSB (1) só propagação, média por frame (%)'),
        ('85,7', 'SNGS-136, pipeline (%)'),
        ('87,2', 'SNGS-136, só propagação (%)'),
        ('92,7', 'HSB (1) só propagação, mediana (%)'),
        ('95,9', 'a mesma fração, em %'),
        ('96,5', 'SNGS-138, só propagação (%)'),
        ('97,4', 'SNGS-128, só propagação (%)'),
        ('0,004', 'B5: IoU do gramado, ruído σ = 20'),
        ('0,017', 'valor de um frame ou imagem nos subconjuntos'),
        ('0,029', 'valor de um frame ou imagem nos subconjuntos'),
        ('0,035', 'o mesmo, em módulo ("fica 0,035 abaixo")'),
        ('0,077', 'B5: cobertura do detector, borrão de 21 px'),
        ('0,102', 'B5: aceitas erradas, limpa'),
        ('0,131', 'erro residual do detector no conjunto comum'),
        ('0,221', 'HSB (2) detector, cobertura nos frames com pessoas'),
        ('0,244', 'B5: cobertura do detector, ruído σ = 10'),
        ('0,290', 'ganho, IC inferior'),
        ('0,360', 'LocSim@5 penalizado do detector, jogo 8'),
        ('0,365', 'ganho, IC superior'),
        ('0,366', 'locsim_pen de 6c sem fluxo (Tabela 1)'),
        ('0,375', 'B5: aceitas erradas, borrão de 21 px'),
        ('0,380', 'RE mediano (m), WC14 test'),
        ('0,387', 'B3, acurácia a 5 px penalizada, test inteiro: detector'),
        ('0,396', 'B2, HSB, 6a Bassek: cob_fr'),
        ('0,517', 'B5: cobertura do detector, limpa'),
        ('0,526', 'B5: cobertura das marcações, sombra L* × 0,5'),
        ('0,543', 'B5: cobertura das marcações, borrão de 11 px'),
        ('0,551', 'B3, acurácia a 5 px penalizada, test inteiro: 6c fluxo'),
        ('0,575', 'cobertura do detector no WC14 test'),
        ('0,612', 'B5: cobertura das marcações a 2 px, limpa'),
        ('0,613', 'B3, acurácia a 5 px nos cobertos, test inteiro: 6c fluxo'),
        ('0,656', 'B4, fração ao teto do sistema: 6c fluxo'),
        ('0,676', 'LocSim@5 penalizado do 6c, jogo 7'),
        ('0,684', 'B4, fração ao teto do sistema: 6c âncora de gabarito'),
        ('0,708', 'B5: IoU do gramado, ruído σ = 10'),
        ('0,715', 'locsim_pen de 6c sem linhas (Tabela 1)'),
        ('0,735', 'B3, acurácia a 5 px penalizada, conjunto comum: 6a Bassek'),
        ('0,763', 'LocSim@5 penalizado do teto'),
        ('0,807', 'B3, acurácia a 5 px penalizada, conjunto comum: 6c fluxo'),
        ('0,818', 'LocSim@5 da âncora ingênua no conjunto comum'),
        ('0,838', 'cobertura do 6c, jogo 8'),
        ('0,864', 'IoU_whole médio, WC14 test'),
        ('0,889', 'B5: menor IoU do campo inteiro mediano entre os níveis com resposta (borrão de 21 px)'),
        ('0,913', 'IoU_whole mediano, WC14 test'),
        ('0,934', 'B4, teto do sistema no conjunto comum: LocSim@5 pen.'),
        ('0,959', 'fração da distância ao teto condicionado às âncoras, propagação'),
        ('0,969', 'B5: IoU do gramado, sombra L* × 0,35'),
        ('0,986', 'fração ao teto, IC superior'),
        ('0,987', 'correlação mediana do ECC'),
        ('0,995', 'IoU_part mediano, WC14 test'),
        ('1,615', 'RE médio (m), WC14 test'),
        ('1.120', 'frames com pessoas do HSB'),
        ('15,50', 'tremor_p90 (px) de detector na interseção (T4b)'),
        ('23,51', 'deslize p90 (px) do Kalman no próprio conjunto'),
        ('3.570', 'detector, s por clipe de 750 frames num núcleo (perfil)'),
        ('72,61', 'deslize p90 (px) do 6a Bassek no próprio conjunto'),
        ('96,15', 'AuxFlow no HSB, mediana (tabela 4)'),
        ('+0,003', 'IC inferior do Δ do line_thr 15'),
        ('+0,034', 'Δ LocSim do line_thr 15'),
        ('+0,044', 'ganho AuxFlow − NBJW'),
        ('+0,065', 'IC superior do Δ do line_thr 15'),
        ('+0,127', 'Δ LocSim do line_thr 15 no jogo 4'),
        ('+0,330', 'ganho 6c − detector, penalizado'),
        ('0,0056', 'NPE mediano do jogo 9, limiar 30'),
        ('0,0066', 'NPE mediano do 6c no conjunto comum'),
        ('0,0072', 'NPE mediano do detector'),
        ('0,0095', 'NPE mediano, 6c fluxo, lacuna 1-3'),
        ('0,0130', 'NPE mediano do jogo 9, limiar 15'),
        ('0,0168', 'NPE mediano, 6c fluxo, lacuna 4-25'),
        ('0,0242', 'NPE mediano do 6a Bassek com as duas bordas certas'),
        ('0,0551', 'NPE mediano, 6c fluxo, lacuna > 25'),
        ('0,0785', 'NPE mediano, 6c sem linhas, lacuna > 25'),
        ('0,1248', 'npe_med de 6c sem fluxo (Tabela 1)'),
        ('0,5155', 'iou_whole médio no protocolo KpSFR, 186 imagens com 0 nas sem H'),
        ('0,8634', 'iou_whole mediano no protocolo KpSFR, 186 imagens com 0 nas sem H'),
        ('0,8962', 'iou_whole médio no protocolo KpSFR, 107 imagens com H'),
        ('0,8994', 'NPE mediano, 6a Bassek, lacuna 4-25'),
        ('0,9534', 'iou_whole mediano no protocolo KpSFR, 107 imagens com H'),
        ('17.828', 'frames na interseção das cinco séries'),
        ('18.133', 'frames do conjunto comum'),
        ('36.701', 'pares de frames consecutivos do ECC'),
        ('36.750', 'frames do GSR test'),
        ('−0,003', 'ganho nos cobertos, IC superior'),
        ('−0,046', 'Δ LocSim do line_thr 15 no jogo 9'),
        ('−0,078', 'ganho nos cobertos, IC inferior'),
        ('11', 'B5, protocolo: núcleo do borrão de 11 px'),
        ('11', 'B3: redução do erro (1 − acurácia a 5 px)'),
        ('52', 'fração do campo coberta pelo gramado no jogo 3 da valid'),
        ('0,0', 'HSB (2) detector, mediana'),
        ('0,8', 'jogadores invertidos do 6c na interseção'),
        ('0,8', 'aceita errada: IoU do campo inteiro < 0,8'),
        ('1,71', 'deslize_med (px) de Kalman + RTS na interseção'),
        ('1,71', 'parede do 6c (h)'),
        ('0,078', 'erro residual da propagação no conjunto comum'),
        ('0,341', 'LocSim@5 penalizado do detector, jogo 7'),
        ('0,478', 'B5: cobertura do detector, oclusão de 20%'),
        ('0,533', 'B3, acurácia a 5 px nos cobertos, test inteiro: H_gt_auxflow'),
        ('0,533', 'B5: cobertura das marcações, oclusão de 20%'),
        ('0,555', 'LocSim@5 penalizado do detector, jogo 11'),
        ('0,571', 'locsim_pen de 6c âncora ingênua /150'),
        ('0,784', 'B3, acurácia a 5 px nos cobertos, test inteiro: detector'),
        ('0,784', 'B3, acurácia a 5 px penalizada, conjunto comum: detector'),
        ('0,869', 'LocSim@5 do detector nos cobertos'),
        ('0,869', 'LocSim@5 penalizado do detector no conjunto comum'),
        ('0,869', 'B3, acurácia a 5 px nos cobertos, test inteiro: H_gt pelas linhas'),
        ('0,899', 'B4, teto do sistema: LocSim@5 pen., mín. entre os jogos'),
        ('0,922', 'LocSim@5 penalizado do 6c no conjunto comum'),
        ('0,922', 'B4, teto do sistema: LocSim@5 penalizado'),
        ('0,925', 'fração ao teto, IC inferior'),
        ('0,930', 'LocSim@5 da propagação no conjunto comum, nos frames que ela cobre'),
        ('0,930', 'B5: maior IoU do campo inteiro mediano'),
        ('0,949', 'B4, teto do sistema: LocSim@5 pen., máx. entre os jogos'),
        ('1,000', 'cobertura do 6c, jogo 11'),
        ('1,000', 'B4, teto do sistema: cobertura'),
):
    R(t, "v1", a, "6")

# ------------------------------------------------------------------ 7. análise de falhas do v1
for t, a in (
        ('13', 'clipes sem âncora da valid no jogo 3'),
        ('26', 'lacuna da Figura 7 (2-26)'),
        ('99', 'lacunas de 4-25 com as duas bordas certas'),
        ('106', 'lacunas de 4-25 com uma borda errada'),
        ('250', 'faixa de distância à âncora (> 250 frames)'),
        ('331', 'lacunas de 4-25 com as duas bordas erradas'),
        ('537', 'lacunas de 4-25 frames no test'),
        ('7,1', 'NPE do 6a Bassek no meio da lacuna da Figura 7 (SNGS-121, f14)'),
        ('0,79', 'cobertura das marcações a 2 px, referência da Fatia 3 (GSR train)'),
        ('0,81', 'cobertura das marcações a 2 px, SNGS-127'),
        ('0,98', 'cobertura das marcações a 2 px, SNGS-138'),
        ('15,9', 'maior cobertura do detector nos sem âncora (SNGS-147, %)'),
        ('71,1', 'HSB (3) pipeline, mediana (%)'),
        ('0,060', 'menor NPE das âncoras de encaixe parcial (SNGS-122 f657)'),
        ('0,063', 'NPE da âncora SNGS-132 f721'),
        ('0,208', 'NPE mediano do 6c nas pontas a > 250 frames da âncora'),
        ('0,235', 'maior NPE das âncoras de encaixe parcial (SNGS-190 f525)'),
        ('0,506', 'LocSim@5 penalizado do 6c, SNGS-144'),
        ('0,635', 'LocSim@5 penalizado do 6c, SNGS-126'),
        ('0,954', 'LocSim@5 penalizado do teto, SNGS-126'),
        ('0,988', 'menor fração do campo como grama nos sem âncora (SNGS-138)'),
        ('1,355', 'NPE da âncora SNGS-126 f588'),
        ('0,0059', 'NPE mediano do 6c a <= 25 frames da âncora, frames com H do detector'),
        ('0,0101', 'NPE mediano do 6c a <= 25 frames da âncora, pontas'),
        ('0,7', 'menor cobertura do detector nos sem âncora'),
        ('0,495', 'LocSim@5 penalizado do 6c, SNGS-143'),
        ('0,495', 'LocSim@5 penalizado do teto, SNGS-143'),
        ('0,508', 'LocSim@5 penalizado do teto, SNGS-144'),
):
    R(t, "v1", a, "7")

# ------------------------------------------------------------------ 8. segundo ciclo (v2)
for t, a in (
        ('36', 'clipes que melhoram'),
        ('59', "A': clipes da metade fixa"),
        ('1,4', 'aceitas erradas entre as com gabarito, v2'),
        ('290', 'H novas no v2'),
        ('448', "A': H centrais da checagem barata"),
        ('722', 'H do v1 idênticas bit a bit'),
        ('765', 'âncoras aceitas (n), v2'),
        ('0,06', 'os dois do HSB pioram cerca disto'),
        ('74,5', 'HSB, (3) pipeline pen média, v2'),
        ('81,9', 'HSB, (3) pipeline pen mediana, v2'),
        ('0,006', 'SNGS-136, f189: menor NPE das recusadas pelo B1'),
        ('0,008', 'os três que pioram menos pioram menos que isto'),
        ('0,020', 'SNGS-136, f39: menor NPE das aceitas até a f110'),
        ('0,020', 'SNGS-136, f9: maior NPE das recusadas pelo B1'),
        ('0,027', 'AuxFlow − propagação do v2'),
        ('0,032', 'SNGS-136, f110: maior NPE das aceitas até a f110'),
        ('0,624', 'locsim_pen de detector, v2'),
        ('0,914', 'locsim_pen de 6c âncora de gabarito, v2'),
        ('0,914', 'LocSim@5 pen. da propagação, jogo 7, v2'),
        ('0,956', 'LocSim@5 pen. da propagação, jogo 11, v2'),
        ('0,954', 'LocSim@5 pen. do teto condicionado, jogo 11, v2'),
        ('0,902', 'LocSim@5 penalizado da propagação, v2'),
        ('0,017', 'propagação do v2 − NBJW'),
        ('85', 'fração da distância entre a propagação do v1 e o AuxFlow'),
        ('0,839', 'LocSim@5 pen. da propagação, jogo 8, v2'),
        ('0,702', 'cobertura de detector, v2'),
        ('0,763', 'locsim_pen de 6c âncora de gabarito, v1'),
        ('0,959', 'fracao_teto de 6c fluxo, v2'),
        ('5', "A': jogos com Δ > 0 (critério antigo)"),
        ('6', "A': jogos com Δ >= 0 (critério novo)"),
        ('−0,03', 'critério do plano: nenhum jogo abaixo de −0,03'),
        ('+0,178', "A': média dos Δ por jogo"),
        ('4', 'critério do plano: ganho em >= 4 de 6 jogos'),
        ('6', 'critério do plano: 6 jogos de dev'),
        ('5', 'C: jogos em que piorou'),
        ('3', 'B2: jogos com Δ = 0'),
        ('3', 'A: H novas no jogo 3, todas erradas'),
        ('20', "A': contagem mínima de H novas"),
        ('4', "A': H centrais recusadas pelo filtro"),
        ('4', 'B1b: clipes que a regra mexe'),
        ('2', 'B1b: jogos que a regra mexe'),
        ('5', 'B1: jogos com Δ > 0 na leitura leave-one-game-out'),
        ('1,000', 'cobertura da propagação, v2'),
        ('558', 'âncoras aceitas (n), v1'),
        ('12', 'âncoras aceitas (erradas), v1'),
        ('11', 'âncoras aceitas (erradas), v2'),
        ('2,2', 'aceitas erradas entre as com gabarito, v1'),
        ('5', 'clipes do test sem âncora aceita, v1'),
        ('0', 'clipes do test sem âncora aceita, v2'),
        ('61,7', 'HSB, (3) pipeline pen média, v1'),
        ('71,1', 'HSB, (3) pipeline pen mediana, v1'),
        ('83,67', 'AuxFlow no HSB, média'),
        ('96,15', 'AuxFlow no HSB, mediana'),
        ('81,4', 'HSB, (1) só propagação pen média, v2'),
        ('0,929', 'LocSim@5 do AuxFlow'),
        ('0,885', 'LocSim@5 do NBJW'),
        ('1', 'conferência contra o v1 a 1 frame em 25'),
        ('25', 'conferência contra o v1 a 1 frame em 25'),
        ('49', 'clipes do GSR test'),
):
    R(t, "v2", a, "8")
# Tabela 11: Δ por jogo de dev (C 2026-10-21; B2, B1b, A' 2026-10-22), linha da tabela da entrada no docs/decisoes.md
for anchor, t in (
        ('| 4 | 0,5155 | 0,5032 | −0,0123', '−0,0123'),
        ('| 6 | 0,8805 | 0,8839 | +0,0034', '+0,0034'),
        ('| 9 | 0,8282 | 0,8252 | −0,0029', '−0,0029'),
        ('| 2 | 0,6427 | 0,6368 | −0,0059', '−0,0059'),
        ('| 3 | 0,1410 | 0,1332 | −0,0078', '−0,0078'),
        ('| 5 | 0,6273 | 0,6223 | −0,0050', '−0,0050'),
        ('| 4 | 0,5155 | 0,5331 | +0,0175 | = | +0,0175', '+0,0175'),
        ('| 6 | 0,8805 | 0,8805 | 0,0000 | = | 0,0000', '0,0000'),
        ('| 9 | 0,8282 | 0,8282 | 0,0000 | 0,8282 (11,25 m) | 0,0000', '0,0000'),
        ('| 2 | 0,6427 | 0,6130 | −0,0297 | 0,6344 (8,48 m) | −0,0083', '−0,0083'),
        ('| 3 | 0,1410 | 0,1452 | +0,0042 | = | +0,0042', '+0,0042'),
        ('| 5 | 0,6273 | 0,6273 | 0,0000 | = | 0,0000', '0,0000'),
        ('| 4 | 0,5155 | 0,5155 | 0 |', '0'),
        ('| 6 | 0,8805 | 0,8805 | 0 |', '0'),
        ('| 9 | 0,8282 | 0,8282 | 0 |', '0'),
        ('| 2 | 0,6427 | 0,6651 | +0,0223 |', '+0,0223'),
        ('| 3 | 0,1410 | 0,1417 | +0,0007 |', '+0,0007'),
        ('| 5 | 0,6273 | 0,6273 | 0 |', '0'),
        ('| 4 | 9 | 0,4219 | 0,8155 | +0,3936 |', '+0,3936'),
        ('| 6 | 10 | 0,8898 | 0,9220 | +0,0322 |', '+0,0322'),
        ('| 9 | 10 | 0,7665 | 0,8868 | +0,1203 |', '+0,1203'),
        ('| 2 | 9 | 0,5499 | 0,8478 | +0,2978 |', '+0,2978'),
        ('| 3 | 11 | 0,2471 | 0,2471 | 0 |', '0'),
        ('| 5 | 10 | 0,6256 | 0,8504 | +0,2247 |', '+0,2247'),
):
    X(t, "Δ por jogo de dev, linha " + anchor.replace("|", "/").strip(" /"), DEC, anchor, sec="8.3, Tabela 11")   # | quebraria a tabela
X("+0,0245", "A: piora da fração de aceitas erradas no jogo 3 (checagem barata)", DEC, "No jogo 3 ela sobe +0,0245", sec="8.3")
X("0,02", "checagem barata: limite de piora da fração de aceitas erradas", "docs/05-melhorias-plano.md", "0,02 em termos absolutos", sec="8.2, 8.3")

# ------------------------------------------------------------------ 9. discussão e limitações
for a in ("pinhole camera model augmented with one radial distortion coefficient",
          "only the camera position can be considered fixed", "It is estimated as the median 3D position",
          "A similar version of the Two-Point PTZ algorithm", "an industrial tool is used"):
    P("14", "calibração do GSR (material suplementar)", GS, 14, a, "9.1")
for t in ("0,9319", "0,9330", "0,9333", "3.362", "1", "25", "0,029", "+0,001"):
    X(t, "D1, lente (diagnóstico no dev do v2)", DEC, "**D1, lente (negativo):**", sec="9.1")
for t in ("0,4", "1,3", "1,2", "2,4"):
    X(t, "D2, centro da câmera por clipe e por frame (diagnóstico no dev do v2)", DEC, "**D2, centro da câmera C**", sec="9.1, 9.5")
for t in ("0,855", "0,918", "0,984", "0,966"):
    X(t, "D3, AUC da nota da âncora e do centro da câmera (diagnóstico no dev do v2)", DEC, "**D3, C contra âncoras erradas**", sec="9.2")
for t in ("5", "6", "+0,0179", "−0,0223"):
    X(t, "B1: critério na leitura leave-one-game-out", DEC, "**Critério na leitura LOGO (a que decide):**", sec="9.2")
for t in ("0", "4"):
    X(t, "B1: no jogo 2, a nota recusa 0 das 4 aceitas erradas", DEC, "**Fraqueza conhecida:**", sec="9.2")
for t in ("0,5", "1", "12"):
    X(t, "T5: reinicialização de 2 pontos contra o erro no centro da câmera", DEC, "**T4 e T5 sintéticos**", sec="9.5")
for t, a in (("+0,037", "ganho da propagação v1 -> v2, jogo 11"), ("+0,238", "ganho da propagação v1 -> v2, jogo 7"),
             ("16", "jogo 3 do dev, base B1 + A': clipes sem âncora"), ("21", "jogo 3 do dev: clipes")):
    R(t, "v2", a, "9.4")
# 9.4: jogo 3 do dev, base → B1 (outputs/runs_v2/b1_regra/por_jogo.csv; os 3 clipes no registro do B1 aceito, 2026-10-16)
B1J = "outputs/runs_v2/b1_regra/por_jogo.csv"
C("13", "jogo 3 do dev, v1 (base do B1): clipes sem âncora", B1J, {"jogo": "3"}, "base_sem_ancora", sec="9.4")
R("1", "v1", "lacuna de 4-25 com borda sem gabarito", "7")
C("+0,002", "jogo 3 do dev: Δ do LocSim@5 penalizado do 6c, base → B1", B1J, {"jogo": "3"}, "delta_6c", sec="9.4")
X("3", "B1: clipes do jogo 3 que perderam só aceitas erradas (SNGS-042, -044, -049)", DEC, "SNGS-044 e SNGS-049 (jogo 3): 0,007 e 0,006 antes", sec="9.4")
# 9.1 e Conclusão: o gabarito pelas linhas como predição, penalizado no test inteiro e no jogo 11 (análise posterior à rodada)
GTP = "outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv"
C("0,929", "H_gt pelas linhas como predição: LocSim@5 penalizado no test inteiro", GTP, {"conjunto": "test inteiro", "serie": "H_gt pelas linhas"}, "locsim_pen", sec="9.1, 10")
C("0,956", "H_gt pelas linhas como predição: LocSim@5 penalizado no jogo 11", GTP, {"conjunto": "test inteiro", "serie": "H_gt pelas linhas"}, "locsim_pen_jogo11", sec="9.1")

# 5. defeitos de chave do v1 achados na revisão de 2026-10-14, depois da rodada
X("735", "revisão de 2026-10-14: chaves da série conferidas na rodada do test", DEC, "as 735/735 chaves da série foram conferidas", sec="5")
X("49", "revisão de 2026-10-14: chaves do 6c conferidas na rodada do test", DEC, "as 49/49 do 6c também", sec="5")

# ------------------------------------------------------------------ conferência
def pdf_page(path, page):
    """Texto da página, com os espaços e as quebras de linha reduzidos a um espaço (pdftotext, do poppler)."""
    exe = shutil.which("pdftotext")
    if exe is None:
        raise SystemExit("pdftotext (poppler) não achado no PATH: as entradas P precisam dele")
    out = subprocess.run([exe, "-f", str(page), "-l", str(page), "-enc", "UTF-8", path, "-"], capture_output=True, check=True)
    return re.sub(r"\s+", " ", out.stdout.decode("utf-8", "replace"))


def resolve(e, values):
    if e["tipo"] == "pdf":
        ok = e["anchor"] in pdf_page(e["src"], e["page"]) and (e["txt"] == str(e["page"])     # o número é a página citada
                                                               or any(v in e["anchor"] for v in N.variants(e["txt"])))
        return ok, None, f"p. {e['page']}", f"“{e['anchor']}”", "" if ok else "trecho não está na página ou não tem o número"
    if e["tipo"] != "num":
        return V.resolve(e, values)
    for i, line in enumerate(N._lines(e["src"]), 1):
        cel = [c.strip() for c in line.split("|")]
        if len(cel) > 4 and cel[2] == e["txt"] and e["desc"] in cel[3]:
            return True, i, f"nº {cel[1]}", cel[-2], ""
    return False, None, "—", None, f"sem linha com {e['txt']!r} e {e['desc']!r}"


COPY = r"<!-- copia: (.+?) \| (.+?) -->\n(.*?)<!-- fim: copia -->"


def table_rows(text, caption):
    """Linhas da tabela (as que começam por |) logo antes da legenda que começa por `caption`."""
    L = text.splitlines()
    for i, line in enumerate(L):
        if line.startswith(f": {caption}"):
            j = i - 1
            while j >= 0 and not L[j].startswith("|"):
                j -= 1
            k = j
            while k >= 0 and L[k].startswith("|"):
                k -= 1
            return L[k + 1:j + 1]
    return None


def check_copies(text):
    bad = []
    for src, cap, block in re.findall(COPY, text, flags=re.S):
        rows = [s for s in block.splitlines() if s.startswith("|")]
        if table_rows(Path(src).read_text(encoding="utf-8"), cap) != rows:
            bad.append(f"TABELA COPIADA DIFERENTE DA ORIGEM: {src} | {cap}")
    return bad


def body(text):
    text = re.sub(COPY, lambda m: "\n".join(s for s in m.group(3).splitlines() if not s.startswith("|")), text, flags=re.S)
    text = re.sub(r"\n```.*?\n```", "\n", text, flags=re.S)
    return re.sub(r"\n# Referências.*?(?=\n# |\Z)", "\n", text, flags=re.S)


def numeros_md(res):
    head = ("# Números do trabalho final e a origem de cada um\n\n"
            "Gerado por `scripts/relatorio/numeros_tf.py`, que confere cada linha. Nas origens que são os arquivos de números dos "
            "relatórios (`docs/04-relatorio-numeros.md` e `docs/04-relatorio-v2-numeros.md`, conferidos por `numeros.py` e "
            "`numeros_v2.py`), a linha é a do arquivo e a coluna diz o nº da entrada; a origem primária está nela. Nas origens em CSV, "
            "a linha conta o cabeçalho como linha 1; nas em texto, a linha é a do arquivo; nas em JSON, a coluna diz o caminho das "
            "chaves; as contas dizem a expressão. As tabelas copiadas dos relatórios são conferidas linha a linha contra a tabela de "
            "mesma legenda na origem. A completude também é conferida: todo número do corpo, fora das linhas dessas tabelas, tem uma "
            "linha aqui.\n\n"
            "As origens em PDF (artigos da pasta do projeto) dizem a página do arquivo e o trecho conferido. Elas exigem o `pdftotext` "
            "do poppler no PATH: o script roda no Git Bash, que o traz em `/mingw64/bin`; sem ele, o script para com uma mensagem.\n\n"
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
    bad = [f"ORIGEM NÃO CONFERE: {e['txt']!r} ({e['desc']}): {r[4]}" for e, r in zip(NUMEROS, res) if not r[0]]
    text = REL.read_text(encoding="utf-8")
    bad += check_copies(text)
    for b in bad:
        print(b)
    known = {e["txt"] for e in NUMEROS}
    missing = sorted(set(t for t in N.body_tokens(body(text)) if t not in known), key=lambda s: (len(s), s))
    for t in missing:
        print(f"SEM ORIGEM NA LISTA: {t!r}")
    if "--escrever" in sys.argv:
        OUT_MD.write_text(numeros_md(res), encoding="utf-8")
        print(f"gravado: {OUT_MD} ({len(NUMEROS)} entradas)")
    print(f"{len(NUMEROS)} entradas; {len(bad)} sem conferir; {len(missing)} números sem origem")
    sys.exit(1 if bad or missing else 0)
