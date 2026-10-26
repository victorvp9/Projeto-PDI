---
title: "Adendo v2: registro de campo com mais âncoras em vista central"
author: "Victor Viana"
date: "Outubro de 2026"
lang: pt-BR
---

> **v2 exploratória (test já visto no v1).** Todo número do GSR test neste adendo leva este rótulo. O relatório v1 (`docs/04-relatorio.md`) não muda; este adendo vem ao lado dele, com as mesmas medidas e os mesmos scripts de tabela, adaptados ao `src_v2`. As duas ressalvas da Seção 1 valem para tudo o que segue.

# 1. Ressalvas

> **Ressalva central: a escolha da hipótese A usou informação do test.** A hipótese A (mais âncoras em vista central) nasceu da análise de falhas do v1, feita no test (relatório v1, seção 7): dos 5 clipes do test sem âncora, três eram vistas do círculo central e da linha do meio, com uma única reta transversal, e um da zona entre o meio e a área. O plano do v2 proibiu escolher pelo test e reproduziu a categoria de falha no dev (`docs/05-melhorias-plano.md`, seção 3), e o A' foi medido e aceito só no dev; mas a hipótese foi escolhida olhando o test. A decisão de deixar o E (segmentação) para depois usou a mesma análise: o test não tem jogo com sombra (`docs/decisoes.md`, `2026-10-23`). **Por isso o 0,902 é exploratório, e não uma estimativa limpa de generalização.** O ganho nos clipes sem âncora do test (5 → 0) é justamente o efeito para o qual a hipótese foi desenhada.

> **A troca do critério no meio do ciclo.** O critério do plano era Δ > 0 em pelo menos 4 de 6 jogos, média dos Δ > 0 e nenhum jogo abaixo de −0,03. Depois dos resultados de B2, A e B1b, Victor trocou a primeira condição por Δ ≥ 0 (empates contam), só para as hipóteses seguintes (`docs/decisoes.md`, `2026-10-22`); ela foi aplicada a partir do A'. O A' passaria também pelo critério antigo: Δ > 0 em 5 de 6 jogos (o jogo 3 ficou com Δ = 0), média +0,178.

> **A comparação com o AuxFlow é indicativa.** O LocSim não usa homografia de gabarito, nem lá nem aqui: projeta o centro da borda inferior de cada caixa de pessoa com a homografia estimada do frame e compara com a posição da pessoa no campo dada pelo gabarito (o `bbox_pitch`, no nosso caso). O que o artigo do AuxFlow deixa verificar sobre o número deles:
>
> - **conjunto:** o split de test do SoccerNet GSR (seção 5.6 deles), o mesmo dos nossos 49 clipes; o artigo não diz se usou todos os clipes e frames;
> - **agregação:** a legenda da tabela 7 diz que as métricas são calculadas por frame e que depois se tiram a média e a mediana; a coluna do LocSim@5 traz um valor só, sem dizer qual dos dois. A nossa agregação é por pessoa-frame: a soma do LocSim de todas as pessoas (sem a bola) de todos os frames, dividida pelo número delas;
> - **frames sem homografia:** o artigo não diz como entram. No v2, a propagação cobre todos os frames do test (cobertura 1,000), então isso não pesa no nosso número.
>
> Uma frase do v1 sobre o protocolo do AuxFlow não tem apoio no artigo (Seção 6).

# 2. O ciclo v2

O plano foi congelado antes de qualquer experimento (`docs/05-melhorias-plano.md`, tag `plano-v2-congelado`). O dev são 6 jogos, os jogos 4, 6 e 9 do train e os jogos 2, 3 e 5 da valid; o test só entra no fim, uma vez. Cada hipótese é uma mudança, decidida pelo LocSim@5 penalizado da propagação por jogo, com leitura leave-one-game-out quando há limiar ajustado e, nas mudanças do detector, uma checagem barata seguida da confirmação na metade fixa dos clipes de cada jogo. A tabela abaixo é gerada dos `decisao.json` de cada hipótese.

<!-- gerado: ciclo -->

| Hipótese | O que muda | Medida em | Critério | Jogos com Δ > 0 | Jogos com Δ ≥ 0 | Média dos Δ | Pior Δ | Decisão |
|---|---|---|---|---|---|---|---|---|
| B1 | limiar de nota da âncora | dev, leave-one-game-out | antigo | 5 | — | +0,0179 | −0,0223 | aceita |
| C | propagação bidirecional entre âncoras | dev | antigo | 1 | — | −0,0051 | −0,0123 | recusada |
| B2 | centro da câmera da âncora | dev, leave-one-game-out | antigo | 2 | — | +0,0022 | −0,0083 | recusada |
| B1b | recupera a melhor candidata recusada pelo B1 | dev (4 clipes recalculados) | antigo | 2 | — | +0,0038 | 0,0000 | recusada |
| A' | vista central em forma fechada (o filtro da elipse quase não age) | dev, metade fixa | novo | 5 | 6 | +0,1781 | 0,0000 | aceita |

: Tabela 1 — O ciclo v2 no dev: LocSim@5 penalizado da propagação, Δ por jogo contra a base de cada hipótese (`outputs/runs_v2/<hipótese>/decisao.json`). O A, antes do A', parou na checagem barata e não tem confirmação.

<!-- fim: ciclo -->

- **B1, aceito.** A âncora verificada só entra com nota (IoU com o gramado + fração explicada) de pelo menos `1.6153357723089734`, limiar do treino; ganho em 5 de 6 jogos na leitura leave-one-game-out.
- **C, recusado.** A propagação bidirecional entre âncoras piorou em 5 de 6 jogos. **Lição, registrada como defeito de desenho:** a homografia fundida das duas propagações era reestimada por DLT sem passar de novo pelo ajuste às linhas do frame, que é o que segura a deriva na propagação de um lado só. A recusa mede essa versão, e não a ideia da fusão; uma correção só entra como hipótese nova, registrada antes de rodar.
- **B2, recusado.** O limite na distância do centro da câmera da âncora ao do jogo recusou as âncoras erradas onde havia, mas deu Δ = 0 em 3 dos 6 jogos e perda no jogo 2.
- **A, parado na checagem barata; A', aceito.** A vista central em forma fechada (linha do meio, círculo central e laterais) parou no jogo 3, com 3 H novas, todas erradas. O A' acrescentou o filtro de consistência da elipse e a contagem mínima de 20 H novas por jogo na regra de parada, ambos fixados antes de rodar, e foi aceito na metade fixa (59 clipes) com Δ ≥ 0 em 6 de 6 jogos. **O filtro da elipse é quase vazio:** na checagem barata, recusou 4 de 448 H centrais, e nenhuma nos jogos 6, 2, 3 e 5 (`outputs/runs_v2/a_central/relatorio_a2.md`), porque a H central é construída a partir da própria elipse. Quem barra as H erradas do A' são a verificação temporal e o B1. No jogo 3, na base B1 + A' do dev inteiro, das 15 H do A', 11 viraram candidatas, todas erradas (NPE de 0,14 a 0,20), e nenhuma é verificável, porque têm menos de 2 vizinhos com H; nenhuma vira âncora (`scripts/relatorio/ancoras_a_v2.py`). Na confirmação da metade fixa, foram 3 candidatas do A' no jogo 3, nenhuma aceita. Nos outros jogos, a barreira não é completa: das 168 âncoras do A' na metade fixa, 3 são erradas. **O ganho vem da construção da vista central, e não do filtro.**
- **B1b, recusado por construção.** Recuperar a melhor candidata quando o B1 deixa um clipe sem âncora mexia em 4 clipes de 2 jogos e não tinha como cumprir os 4 de 6 jogos.
- **Fora do ciclo:** o D espera, o E não entra agora (Seção 1) e o sinal das pessoas (F) muda a natureza do método.

O v2 final é B1 + A' (tag `v2-final`), congelado antes de qualquer número do test.

# 3. Resultados no GSR test, v1 × v2

## 3.1 O test inteiro

<!-- gerado: t1 -->

| Série | Cobertura | LocSim@5 penalizado | Nos cobertos | NPE mediano | Fração ao teto |
|---|---|---|---|---|---|
| detector | 0,505 → 0,702 | 0,419 → 0,624 | 0,869 → 0,882 | 0,0072 → 0,0080 | — → — |
| suavização S-G (Bassek) | 0,680 → 0,909 | 0,446 → 0,672 | 0,681 → 0,738 | 0,0126 → 0,0136 | 0,078 → 0,167 |
| S-G robusta | 0,665 → 0,893 | 0,478 → 0,743 | 0,747 → 0,830 | 0,0097 → 0,0100 | 0,171 → 0,410 |
| Kalman + RTS | 0,680 → 0,909 | 0,490 → 0,758 | 0,749 → 0,832 | 0,0113 → 0,0112 | 0,207 → 0,461 |
| propagação | 0,897 → 1,000 | 0,749 → 0,902 | 0,833 → 0,902 | 0,0105 → 0,0083 | 0,959 → 0,959 |
| propagação sem linhas | 0,897 → 1,000 | 0,715 → 0,896 | 0,796 → 0,896 | 0,0122 → 0,0093 | 0,861 → 0,939 |
| propagação sem fluxo | 0,897 → 1,000 | 0,366 → 0,521 | 0,407 → 0,521 | 0,1248 → 0,0663 | −0,155 → −0,355 |
| âncora ingênua /150 | 1,000 → 1,000 | 0,571 → 0,738 | 0,571 → 0,738 | 0,0262 → 0,0159 | 0,442 → 0,394 |
| teto condicionado às âncoras | 0,897 → 1,000 | 0,763 → 0,914 | 0,849 → 0,914 | 0,0064 → 0,0046 | — → — |

: Tabela 2 — GSR test, 49 clipes, v1 → v2 (T1 das duas rodadas). O teto condicionado às âncoras é a propagação a partir da homografia de gabarito nos frames das âncoras aceitas; a fração ao teto é (série − detector) / (teto − detector).

<!-- fim: t1 -->

- **A propagação vai de 0,749 a 0,902,** e o teto condicionado às âncoras, de 0,763 a 0,914. A cobertura da propagação chega a 1,000 (v1: 0,897), porque todo clipe passa a ter âncora.
- **O detector sozinho vai de 0,419 a 0,624,** com a cobertura de 0,505 a 0,702. O A' só roda nos frames em que o detector não acha H: na conferência contra o v1, a 1 frame em 25, as 722 H do v1 saíram idênticas bit a bit e há 290 H novas.
- **A fração da distância ao teto é a mesma** (0,959 no v1 e no v2): o ganho veio de ter mais âncoras, e não de propagar melhor.

## 3.2 Por jogo

<!-- gerado: t6 -->

| Jogo | Clipes | Com âncora | Cobertura: detector | Cobertura: propagação | LocSim@5 pen.: detector | LocSim@5 pen.: propagação | LocSim@5 pen.: teto condicionado |
|---|---|---|---|---|---|---|---|
| 7 | 16 | 14 → 16 | 0,472 → 0,687 | 0,874 → 1,000 | 0,341 → 0,580 | 0,676 → 0,914 | 0,703 → 0,922 |
| 8 | 19 | 16 → 19 | 0,447 → 0,650 | 0,838 → 1,000 | 0,360 → 0,553 | 0,650 → 0,839 | 0,661 → 0,868 |
| 11 | 14 | 14 → 14 | 0,617 → 0,787 | 1,000 → 1,000 | 0,555 → 0,739 | 0,920 → 0,956 | 0,925 → 0,954 |

: Tabela 3 — GSR test por jogo, v1 → v2 (T6 do v2, com as colunas do v1).

<!-- fim: t6 -->

Os três jogos sobem: o jogo 7 de 0,676 a 0,914, o jogo 8 de 0,650 a 0,839 e o jogo 11 de 0,920 a 0,956. **No jogo 11, a propagação (0,956) fica acima do teto condicionado (0,954): o teto não é um limite estrito.** Ele propaga a homografia de gabarito, ajustada às linhas, a partir dos frames das âncoras, e essa homografia não é a melhor possível para o LocSim, que mede contra o `bbox_pitch` (como predição, ela tira 0,946 de LocSim@5 nos frames com gabarito; relatório v1, seção 6.5).

## 3.3 O conjunto comum

<!-- gerado: t1b -->

| Série | NPE mediano: v1 / v2 | LocSim@5 pen.: v1 | LocSim@5 pen.: v2 |
|---|---|---|---|
| detector | 0,0072 / 0,0080 | 0,869 | 0,882 |
| suavização S-G (Bassek) | 0,0081 / 0,0096 | 0,827 | 0,819 |
| S-G robusta | 0,0073 / 0,0080 | 0,868 | 0,895 |
| Kalman + RTS | 0,0081 / 0,0088 | 0,873 | 0,900 |
| propagação | 0,0066 / 0,0071 | 0,922 | 0,926 |
| propagação sem linhas | 0,0069 / 0,0075 | 0,916 | 0,922 |
| propagação sem fluxo | 0,0294 / 0,0337 | 0,665 | 0,637 |
| âncora ingênua /150 | 0,0087 / 0,0106 | 0,818 | 0,827 |
| teto condicionado às âncoras | 0,0032 / 0,0034 | 0,926 | 0,935 |

: Tabela 4 — Conjunto comum: os frames com homografia do detector de cada versão, 18.133 no v1 e 25.382 no v2 (T1b). As colunas não são do mesmo conjunto de frames.

<!-- fim: t1b -->

O conjunto comum são os frames com homografia do detector de cada versão: 18.133 no v1 e 25.382 no v2. As duas colunas não são do mesmo conjunto de frames. No v2, a propagação tira 0,926 nele, contra 0,882 do detector.

## 3.4 O subconjunto difícil (HSB)

<!-- gerado: t2 -->

| Medição | Média (%) | Mediana (%) | Cobertura (frames com pessoas) |
|---|---|---|---|
| (1) só propagação | 81,4 → 81,4 | 92,7 → 92,7 | 1,000 → 1,000 |
| (2) detector | 17,7 → 29,2 | 0,0 → 0,0 | 0,221 → 0,403 |
| (3) pipeline | 61,7 → 74,5 | 71,1 → 81,9 | 0,829 → 1,000 |

: Tabela 5 — HSB, LocSim@5 por frame, penalizado, v1 → v2 (T2). A medição (1) começa da `H_gt_auxflow` e não depende do detector. AuxFlow, tabela 4 deles (média / mediana): NBJW 43,15 / 35,93; AuxFlow 83,67 / 96,15.

<!-- fim: t2 -->

<!-- gerado: t2clipes -->

| Clipe | Intervalo | (2) detector (%) | (3) pipeline (%) |
|---|---|---|---|
| SNGS-117 | 350–500 | 0,0 → 6,0 | 59,4 → 86,3 |
| SNGS-123 | 100–200 | 10,1 → 19,2 | 59,1 → 45,7 |
| SNGS-124 | 250–320 | 40,6 → 41,6 | 70,3 → 61,9 |
| SNGS-128 | 90–0 | 0,0 → 5,2 | 0,0 → 77,4 |
| SNGS-136 | 60–280 | 44,2 → 55,8 | 85,7 → 72,6 |
| SNGS-138 | 130–230 | 0,0 → 11,4 | 0,0 → 77,4 |
| SNGS-150 | 150–280 | 6,6 → 56,2 | 56,7 → 56,2 |
| SNGS-187 | 300–400 | 21,8 → 22,6 | 95,0 → 95,0 |
| SNGS-191 | 450–500 | 0,0 → 0,6 | 77,6 → 80,2 |
| SNGS-193 | 550–650 | 30,0 → 32,8 | 92,1 → 93,3 |

: Tabela 6 — HSB por clipe, média por frame, penalizada, v1 → v2 (T2). Os intervalos seguem a numeração do artigo do AuxFlow, a partir de 0.

<!-- fim: t2clipes -->

- **O pipeline completo vai de 61,7 a 74,5 de média** (mediana de 71,1 a 81,9), com a cobertura dos frames com pessoas de 0,829 a 1,000. O SNGS-128 e o SNGS-138, que valiam 0 no v1, passam a ter âncora.
- **Fica abaixo do AuxFlow** (83,67 de média e 96,15 de mediana, tabela 4 deles).
- **A medição (1), só propagação a partir da `H_gt_auxflow`, não depende do detector** e fica igual (81,4).
- **Quatro clipes pioram no intervalo do HSB:** o SNGS-136 (85,7 → 72,6), o SNGS-123 (59,1 → 45,7), o SNGS-124 (70,3 → 61,9) e o SNGS-150 (56,7 → 56,2). Os dois primeiros são também os que mais pioram no clipe inteiro (Seção 3.7).

## 3.5 Comparação com o AuxFlow

<!-- gerado: t5 -->

| Linha | LocSim@5 (penalizado, no nosso caso) | Nos cobertos | Conjunto comum |
|---|---|---|---|
| NBJW (AuxFlow, tab. 7) | 0,885 | — | — |
| AuxFlow (tab. 7) | 0,929 | — | — |
| ganho AuxFlow − NBJW | 0,044 | — | — |
| nosso detector | 0,419 → 0,624 | 0,869 → 0,882 | 0,869 → 0,882 |
| nossa propagação | 0,749 → 0,902 | 0,833 → 0,902 | 0,930 → 0,926 |
| ganho propagação − detector | 0,330 → 0,278 | −0,035 → 0,020 | — |

: Tabela 7 — Comparação com a tabela 7 do AuxFlow, v1 → v2 (T5). Comparação indicativa (Seção 1); o conjunto comum é o de cada versão (Tabela 4).

<!-- fim: t5 -->

Com a ressalva da Seção 1, o v2 fica 0,027 abaixo do AuxFlow e 0,017 acima do NBJW. Da distância entre a propagação do v1 e o AuxFlow, o v2 fecha cerca de 85%. No conjunto comum, a propagação do v2 tira 0,926; o conjunto comum são os frames fáceis do nosso detector, e o do AuxFlow é o test inteiro.

## 3.6 Âncoras e lacunas

<!-- gerado: t7 -->

| Conjunto | v1 | v2 | Erradas (NPE > 0,05): v1 → v2 |
|---|---|---|---|
| candidatas | 958 | 1.193 | 270 → 202 |
| verificáveis | 814 | 1.114 | 152 → 139 |
| aceitas | 558 | 765 | 12 → 11 |
| clipes sem âncora aceita | 5 | 0 | — |

: Tabela 8 — Âncoras no GSR test (T7).

<!-- fim: t7 -->

<!-- gerado: t8 -->

| Lacuna do detector | Frames | Propagação: cobertura | Propagação: NPE mediano | S-G (Bassek): NPE mediano |
|---|---|---|---|---|
| 1–3 | 1.665 → 2.688 | 0,943 → 1,000 | 0,0095 → 0,0107 | 0,0974 → 0,0297 |
| 4–25 | 4.624 → 4.740 | 0,886 → 1,000 | 0,0168 → 0,0132 | 0,8994 → 0,3439 |
| > 25 | 8.391 → 2.931 | 0,733 → 1,000 | 0,0551 → 0,0344 | — → — |
| pontas | 3.088 → 323 | 0,801 → 1,000 | 0,1221 → 0,0419 | — → — |

: Tabela 9 — Lacunas do detector no GSR test, v1 → v2 (T8). As lacunas são as do detector de cada versão: a comparação por faixa é entre conjuntos de frames diferentes. As pontas tocam o começo ou o fim do clipe.

<!-- fim: t8 -->

- **Mais âncoras, com menos erradas:** candidatas de 958 a 1.193 e aceitas de 558 a 765; as aceitas erradas vão de 12 a 11, ou de 2,2% a 1,4% das aceitas com gabarito.
- **Clipes sem âncora: de 5 a 0.**
- **Lacunas:** as faixas são as lacunas do detector de cada versão. O detector do v2 cobre mais frames, e a comparação por faixa é entre conjuntos de frames diferentes.

**Os 5 clipes sem âncora do v1.**

<!-- gerado: sem_ancora -->

| Clipe | Jogo | Âncoras no v2 | NPE das âncoras | Erradas | Propagação: v1 → v2 | Teto condicionado, v2 |
|---|---|---|---|---|---|---|
| SNGS-127 | 7 | 23 | 0,0013–0,0074 | 0 | 0,000 → 0,899 | 0,898 |
| SNGS-128 | 7 | 11 | 0,0036–0,0244 | 0 | 0,000 → 0,916 | 0,937 |
| SNGS-134 | 8 | 12 | 0,0136–0,0258 | 0 | 0,000 → 0,694 | 0,727 |
| SNGS-138 | 8 | 11 | 0,0202–0,0283 | 0 | 0,000 → 0,786 | 0,928 |
| SNGS-147 | 8 | 1 | 0,0348 | 0 | 0,000 → 0,205 | 0,203 |

: Tabela 10 — Os 5 clipes sem âncora do v1 (`outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv`).

<!-- fim: sem_ancora -->

Os 5 ganharam âncora, todas certas (NPE de no máximo 0,035; o limiar de âncora errada é 0,05). Os três de vista central e o SNGS-138 passam a 0,69–0,92. O SNGS-147, de grande e pequena área oblíquas, e não de vista central, fica com 1 âncora e 0,205. **A origem dessa âncora (f246) não foi apurada.** O clipe ganhou H novas (a cobertura do detector vai de 0,159 a 0,203), mas a série do v2 não marca quais H vieram do A', e a série do v1 não está neste PC. Nos frames da amostra de 1 em 25 do v1, as H do v1 e do v2 são as mesmas, e a f246 não está entre eles (`outputs/runs_v2/rodada_test_v2/sngs147.csv`). Saber se ela é uma H do A' ou uma H de 2 + 2 retas que agora passa na verificação exigiria rodar o detector nesse frame sem a vista central.

## 3.7 Os clipes que pioram

<!-- gerado: pioram -->

| Clipe | Jogo | Aceitas: v1 → v2 | Propagação: v1 → v2 | Δ | Teto condicionado: v1 → v2 |
|---|---|---|---|---|---|
| SNGS-136 | 8 | 21 → 21 | 0,893 → 0,832 | −0,0608 | 0,883 → 0,933 |
| SNGS-123 | 7 | 12 → 13 | 0,872 → 0,812 | −0,0604 | 0,868 → 0,819 |
| SNGS-139 | 8 | 20 → 21 | 0,949 → 0,942 | −0,0077 | 0,915 → 0,937 |
| SNGS-125 | 7 | 18 → 19 | 0,940 → 0,935 | −0,0050 | 0,940 → 0,931 |
| SNGS-198 | 11 | 27 → 27 | 0,970 → 0,966 | −0,0042 | 0,972 → 0,970 |

: Tabela 11 — Os clipes que pioram do v1 para o v2 (`outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv`).

<!-- fim: pioram -->

Dos 49 clipes, 36 melhoram, 8 ficam iguais e 5 pioram. Três pioram menos de 0,008; os dois do HSB pioram cerca de 0,06. O diagnóstico abaixo usa só os caches da rodada (`scripts/relatorio/pioras_v2.py`, que grava `pioras.csv` e `pioras_vizinhos.csv`), sem rodar nada do método. Os frames contam a partir de 0.

<!-- gerado: candidatas -->

| Clipe | Candidata | Situação | NPE | Nota (iou + img) |
|---|---|---|---|---|
| SNGS-136 | f9 | B1 | 0,0204 | 1,5951 |
| SNGS-136 | f39 | aceita | 0,0198 | 1,6499 |
| SNGS-136 | f77 | aceita | 0,0208 | 1,6450 |
| SNGS-136 | f90 | aceita | 0,0205 | 1,6325 |
| SNGS-136 | f110 | aceita | 0,0317 | 1,6427 |
| SNGS-136 | f189 | B1 | 0,0058 | 1,5955 |
| SNGS-136 | f215 | B1 | 0,0164 | 1,5934 |
| SNGS-136 | f234 | B1 | 0,0096 | 1,5746 |
| SNGS-136 | f247 | B1 | 0,0097 | 1,5927 |
| SNGS-136 | f313 | aceita | 0,0081 | 1,7749 |
| SNGS-123 | f51 | maioria | 0,0430 | 1,8938 |
| SNGS-123 | f93 | maioria | 0,0127 | 1,9349 |
| SNGS-123 | f132 | maioria | 0,0936 | 1,9159 |
| SNGS-123 | f153 | maioria | 0,0638 | 1,9327 |
| SNGS-123 | f195 | maioria | 0,0049 | 1,7431 |
| SNGS-123 | f240 | aceita | 0,0095 | 1,6537 |

: Tabela 12 — Candidatas a âncora do SNGS-136 e do SNGS-123 até a primeira aceita depois do intervalo do HSB (`outputs/runs_v2/rodada_test_v2/pioras.csv`). Situação: aceita; B1 (nota abaixo do limiar, `config_v2.yaml`: `temporal.anchor_min_nota`); maioria (passa na nota e cai na verificação por maioria). Errada = NPE > 0,05.

<!-- fim: candidatas -->

- **SNGS-136: o B1 ficou com as âncoras piores e recusou as melhores.** O teto condicionado sobe (0,883 → 0,933), e a propagação cai (0,893 → 0,832): as âncoras estão em lugares bons, mas a homografia delas é pior. Até a f110, as quatro aceitas (f39, f77, f90, f110) têm NPE de 0,0198 a 0,0317, os maiores entre as aceitas do clipe, com nota logo acima do limiar do B1 (de 1,63 a 1,65). As cinco recusadas pelo B1 (f9, f189, f215, f234, f247) são todas certas, com NPE de 0,0058 a 0,0204 e nota de 1,575 a 1,595; quatro delas estão no intervalo do HSB (60–280). Neste clipe, a nota inverte a qualidade da homografia, e o B1 não tem como ver isso. O v1 também aceitou 21 âncoras, mas os frames delas não estão neste PC (só as contagens), e não dá para dizer quais foram trocadas.
- **SNGS-123: falta âncora antes da f240.** O intervalo do HSB (100–200) é propagado para trás a partir da f240, e o teto também cai (0,868 → 0,819), sinal de que o problema está em onde ficam as âncoras. Antes da f240, as cinco candidatas passam na nota e caem na verificação por maioria: três certas (f51, f93 e f195, com NPE de 0,043, 0,0127 e 0,0049) e duas erradas (f132 e f153, com 0,094 e 0,064). O B1 não recusou nenhuma. Na janela de voto (±10 frames), a f100 (da f93) e a f200 (da f195) estão na amostra de 1 em 25 do v1: não tinham H no v1 e têm no v2, ou seja, há H do A' entre os votantes. Que elas tenham mudado o voto é hipótese, não testada; conferir exigiria refazer a verificação.

# 4. Resposta franca

- **O v2 não supera o AuxFlow:** 0,902 contra 0,929, com a ressalva de que a comparação é indicativa e o test já tinha sido visto.
- **Passa do NBJW** (0,885), o detector em que o AuxFlow se apoia.
- **Fecha cerca de 85% da distância** entre a propagação do v1 (0,749) e o AuxFlow.
- **No HSB, fica abaixo:** 74,5 contra 83,67 de média.
- **De onde veio o ganho:** de ter mais âncoras, vindas das vistas centrais: os 5 clipes sem âncora do v1 passam a ter, e clipes que já tinham ganham outras. A propagação em si não mudou (a fração ao teto é a mesma), e o próximo limite, o teto condicionado (0,914), ainda fica abaixo do AuxFlow.

# 5. Limitações

- **O limiar de nota do B1 pode inverter a qualidade das âncoras num clipe.** No SNGS-136, ele manteve âncoras com NPE de 0,020 a 0,032 e recusou candidatas certas com NPE de 0,006 a 0,020 (Seção 3.7): a nota (IoU com o gramado + fração explicada) não ordena as candidatas pela precisão da homografia.
- **O jogo 3 do dev continua sem solução:** na base B1 + A', 16 dos 21 clipes seguem sem âncora, por causa da segmentação na sombra azulada. A hipótese que ataca isso, o E, ficou fora do ciclo.
- **O test tem só 3 jogos.** O ganho da propagação vai de +0,037 (jogo 11) a +0,238 (jogo 7); a generalização a outros estádios e outra luz não foi medida.
- **No SNGS-123, que H do A' tenham mudado o voto da verificação é hipótese, não testada** (Seção 3.7).

# 6. Errata do v1

O relatório v1 (`docs/04-relatorio.md`) não é editado; a correção fica registrada aqui.

- **Onde:** na Seção 6.5, legenda da Tabela 6 ("O LocSim deles não tem frames sem homografia; o nosso penalizado dá 0 à pessoa de frame sem homografia."), e no Apêndice A, legenda da Tabela T5 ("O LocSim deles não tem frames sem homografia; o nosso é agregado sobre pessoas-frame, e a pessoa de frame sem homografia vale 0.").
- **O erro:** o artigo do AuxFlow não diz como entram os frames sem homografia (seções 4.2 e 5.6 deles e legenda da tabela 7). A afirmação de que o LocSim deles não tem esses frames não tem apoio no artigo.
- **O que vale:** o que o artigo permite verificar está na Seção 1 deste adendo. A segunda metade das duas legendas, sobre o nosso LocSim, está certa.

# 7. Reprodução

Método: tag `v2-final` (commit `0f25442`, o congelamento, com as chaves em `outputs/runs_v2/congelamento_v2.json`; `src_v2/` e `config_v2.yaml` idênticos aos do `67ae704`, o A' medido). Scripts das tabelas: `scripts/v2/rodada_test_v2/`, commit `b9e35ea`. Registro da rodada: `b4d2aa5`. Marcos do ciclo: tags `plano-v2-congelado`, `baseline-dev` e `b1-aceito`; o A' aceito em `68201a3`, a base B1 + A' no dev inteiro em `a55a9c3`. Ambiente: `uv sync`, com `Python 3.12` (`.python-version`; `docs/02-dados.md`). Tudo vai para `outputs/cache_v2/` e `outputs/runs_v2/rodada_test_v2/`; nada em `outputs/cache` nem em `outputs/runs` do v1.

```
powershell -ExecutionPolicy Bypass -File scripts/literatura/fila_test.ps1
```

A fila baixa e confere o test, e então roda, da raiz e com `PYTHONPATH=.`:

```
uv run python -m src_v2.run --detect-series --splits test --clip-step 1
uv run python scripts/v2/rodada_test_v2/confere_v1_test.py
uv run python -m src_v2.run --propagate-eval --splits test --clip-step 1 --workers 6
uv run python scripts/v2/rodada_test_v2/confere_v1_6c.py
uv run python scripts/v2/rodada_test_v2/extras_test_v2.py 8
uv run python scripts/v2/rodada_test_v2/tabelas_test_v2.py test
```

Depois, o diagnóstico da Seção 3.7 e as tabelas e a conferência dos números deste adendo:

```
uv run python scripts/relatorio/pioras_v2.py
uv run python scripts/relatorio/numeros_v2.py --escrever
```

Cada número do texto, com a origem, está em `docs/04-relatorio-v2-numeros.md`, gerado e conferido pelo `numeros_v2.py`.
