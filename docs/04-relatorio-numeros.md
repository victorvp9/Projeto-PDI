# Números do relatório e a origem de cada um

Gerado por `scripts/relatorio/numeros.py`, que confere cada linha: o valor da origem, arredondado às casas do texto, tem que ser o número do texto. Nas origens em CSV, a linha conta o cabeçalho como linha 1; nas origens em texto, a linha é a do arquivo; as contas (derivados) dizem a expressão. A completude também é conferida: todo número do corpo do relatório tem uma linha aqui. Ficam de fora só os identificadores (clipes, frames, nomes de tabela, figura, seção, etapa, fatia e jogo, anos de citação e trechos de código).

O Apêndice A (tabelas T1 a T9) é gerado pelo mesmo script a partir de `outputs/runs/rodada_test/tabelas/T*.csv`: cada célula vem da linha e da coluna do CSV de mesmo nome, e o script confere que o apêndice no relatório é o gerado.

| nº | número no texto | o que é | seção | origem | linha | coluna | valor na origem |
|---|---|---|---|---|---|---|---|
| 1 | 0,505 | cobertura do detector, GSR test | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | cobertura | 0.5049593224116795 |
| 2 | 0,419 | LocSim@5 penalizado do detector | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | locsim_pen | 0.4192764091198964 |
| 3 | 0,341 | LocSim@5 penalizado do detector, IC inferior (= jogo 7) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | locsim_pen_lo | 0.34108693524125355 |
| 4 | 0,555 | LocSim@5 penalizado do detector, IC superior (= jogo 11) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | locsim_pen_hi | 0.5546704626197827 |
| 5 | 0,869 | LocSim@5 do detector nos cobertos | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | locsim_cob | 0.8685472817991973 |
| 6 | 0,0072 | NPE mediano do detector | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | npe_med | 0.007228082696151382 |
| 7 | 0,897 | cobertura do 6c fluxo | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | cobertura | 0.8971358520004458 |
| 8 | 0,749 | LocSim@5 penalizado do 6c fluxo | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | locsim_pen | 0.7490157917374893 |
| 9 | 0,650 | LocSim@5 penalizado do 6c, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | locsim_pen_lo | 0.6499967158730244 |
| 10 | 0,920 | LocSim@5 penalizado do 6c, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | locsim_pen_hi | 0.9199799820597923 |
| 11 | 0,833 | LocSim@5 do 6c nos cobertos | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | locsim_cob | 0.8334717576561902 |
| 12 | 0,0105 | NPE mediano do 6c fluxo | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | npe_med | 0.01048316446179856 |
| 13 | 0,959 | fração da distância ao teto, 6c fluxo | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto | 0.9590228680694096 |
| 14 | 0,925 | fração ao teto, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto_lo | 0.9254527945921875 |
| 15 | 0,986 | fração ao teto, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto_hi | 0.9860390545455364 |
| 16 | 0,680 | cobertura de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | cobertura | 0.6801794271704001 |
| 17 | 0,0126 | npe_med de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | npe_med | 0.012613672816508013 |
| 18 | 0,446 | locsim_pen de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | locsim_pen | 0.446264162800887 |
| 19 | 0,681 | locsim_cob de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | locsim_cob | 0.681350553316294 |
| 20 | 0,078 | fracao_teto de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | fracao_teto | 0.07849190694916243 |
| 21 | 0,665 | cobertura de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | cobertura | 0.6648556781455478 |
| 22 | 0,0097 | npe_med de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | npe_med | 0.0096917669537372 |
| 23 | 0,478 | locsim_pen de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | locsim_pen | 0.47804103599812126 |
| 24 | 0,747 | locsim_cob de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | locsim_cob | 0.747117357316682 |
| 25 | 0,171 | fracao_teto de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | fracao_teto | 0.1709126176024358 |
| 26 | 0,680 | cobertura de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | cobertura | 0.6798172294661763 |
| 27 | 0,0113 | npe_med de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | npe_med | 0.011285736170425269 |
| 28 | 0,490 | locsim_pen de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | locsim_pen | 0.49042315851089474 |
| 29 | 0,749 | locsim_cob de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | locsim_cob | 0.749173260806681 |
| 30 | 0,207 | fracao_teto de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | fracao_teto | 0.20692511495935076 |
| 31 | 0,897 | cobertura de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | cobertura | 0.8971358520004458 |
| 32 | 0,0122 | npe_med de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | npe_med | 0.01220103731093986 |
| 33 | 0,715 | locsim_pen de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | locsim_pen | 0.715153688402002 |
| 34 | 0,796 | locsim_cob de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | locsim_cob | 0.7957915016505123 |
| 35 | 0,861 | fracao_teto de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | fracao_teto | 0.8605374181305308 |
| 36 | 0,897 | cobertura de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | cobertura | 0.8971358520004458 |
| 37 | 0,1248 | npe_med de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | npe_med | 0.12482665639288845 |
| 38 | 0,366 | locsim_pen de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | locsim_pen | 0.3659943581643886 |
| 39 | 0,407 | locsim_cob de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | locsim_cob | 0.4072623893334853 |
| 40 | −0,155 | fracao_teto de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | fracao_teto | -0.15496694667871075 |
| 41 | 1,000 | cobertura de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | cobertura | 1.0 |
| 42 | 0,0262 | npe_med de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | npe_med | 0.026157020939553043 |
| 43 | 0,571 | locsim_pen de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | locsim_pen | 0.5713680143832477 |
| 44 | 0,571 | locsim_cob de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | locsim_cob | 0.5713680143832477 |
| 45 | 0,442 | fracao_teto de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | fracao_teto | 0.4423473057147572 |
| 46 | 0,897 | cobertura da âncora de gabarito (teto) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | cobertura | 0.8971358520004458 |
| 47 | 0,0064 | NPE mediano do teto | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | npe_med | 0.00643616224779207 |
| 48 | 0,763 | LocSim@5 penalizado do teto | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | locsim_pen | 0.7631048970488494 |
| 49 | 0,849 | LocSim@5 do teto nos cobertos | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | locsim_cob | 0.8491494930219861 |
| 50 | 49 | clipes do GSR test | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 1 | — | (no texto da linha) |
| 51 | 3 | jogos do GSR test | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 1 | — | (no texto da linha) |
| 52 | 10 | reamostragens distintas do bootstrap com 3 jogos | 5 | `outputs/runs/rodada_test/tabelas_v2.out` | 4 | — | (no texto da linha) |
| 53 | 44 | clipes com >= 1 âncora aceita | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 1 | — | (no texto da linha) |
| 54 | 7 | jogo do GSR test | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | jogo | 7 |
| 55 | 16 | clipes do jogo 7 | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | clipes | 16 |
| 56 | 14 | clipes com âncora do jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | com_ancora | 14 |
| 57 | 0,472 | cobertura do detector, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | cob_detector | 0.4719110587046239 |
| 58 | 0,874 | cobertura do 6c, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | cob_6c | 0.8736629327044555 |
| 59 | 0,341 | LocSim@5 penalizado do detector, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | locsim_pen_detector | 0.3410869352412535 |
| 60 | 0,676 | LocSim@5 penalizado do 6c, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | locsim_pen_6c | 0.6759710080828238 |
| 61 | 0,703 | LocSim@5 penalizado do teto, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | locsim_pen_teto | 0.7029466376468649 |
| 62 | 8 | jogo do GSR test | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | jogo | 8 |
| 63 | 19 | clipes do jogo 8 | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | clipes | 19 |
| 64 | 16 | clipes com âncora do jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | com_ancora | 16 |
| 65 | 0,447 | cobertura do detector, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | cob_detector | 0.4473489883325949 |
| 66 | 0,838 | cobertura do 6c, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | cob_6c | 0.8381332151823955 |
| 67 | 0,360 | LocSim@5 penalizado do detector, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | locsim_pen_detector | 0.35974187056903534 |
| 68 | 0,650 | LocSim@5 penalizado do 6c, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | locsim_pen_6c | 0.6499967158730243 |
| 69 | 0,661 | LocSim@5 penalizado do teto, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | locsim_pen_teto | 0.6608245337278049 |
| 70 | 11 | jogo do GSR test | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | jogo | 11 |
| 71 | 14 | clipes do jogo 11 | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | clipes | 14 |
| 72 | 14 | clipes com âncora do jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | com_ancora | 14 |
| 73 | 0,617 | cobertura do detector, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | cob_detector | 0.6168750596544812 |
| 74 | 1,000 | cobertura do 6c, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | cob_6c | 1.0 |
| 75 | 0,555 | LocSim@5 penalizado do detector, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | locsim_pen_detector | 0.5546704626197827 |
| 76 | 0,920 | LocSim@5 penalizado do 6c, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | locsim_pen_6c | 0.9199799820597924 |
| 77 | 0,925 | LocSim@5 penalizado do teto, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | locsim_pen_teto | 0.9251522581997559 |
| 78 | 0,03 | o 6c fica a menos disto do teto nos três jogos (máximo de teto − 6c: 0,027) | 6 | `derivado: max(teto − 6c) < 0,03` | — | — | 0.03 |
| 79 | +0,330 | ganho 6c − detector, penalizado | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | pen | 0.32973938261759295 |
| 80 | 0,290 | ganho, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | pen_lo | 0.2902548453039891 |
| 81 | 0,365 | ganho, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | pen_hi | 0.36530951944000956 |
| 82 | −0,035 | ganho 6c − detector nos cobertos | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | cob | -0.035075524143007075 |
| 83 | 0,035 | o mesmo, em módulo ("fica 0,035 abaixo") | 6 | `derivado: |ganho nos cobertos|` | — | — | 0.0350755 |
| 84 | −0,078 | ganho nos cobertos, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | cob_lo | -0.0780199152971085 |
| 85 | −0,003 | ganho nos cobertos, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | cob_hi | -0.00307166492950528 |
| 86 | 0,885 | LocSim@5 do NBJW, tabela 7 do AuxFlow | 2, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 2 | locsim5 | 0.885 |
| 87 | 0,929 | LocSim@5 do AuxFlow, tabela 7 | 2, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 3 | locsim5 | 0.929 |
| 88 | +0,044 | ganho AuxFlow − NBJW | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 4 | locsim5 | 0.04400000000000004 |
| 89 | 0,930 | LocSim@5 do 6c no conjunto comum (nos cobertos) | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 6 | comum | 0.9302394650733893 |
| 90 | 0,869 | LocSim@5 do detector no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 5 | comum | 0.8685472817991973 |
| 91 | 65 | fração da distância detector -> AuxFlow fechada pelo 6c (%) | 6, 9 | `derivado: (6c − detector) / (AuxFlow − detector)` | — | — | 64.6898 |
| 92 | 18.133 | frames do conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 2 | frames | 18133 |
| 93 | 0,922 | LocSim@5 penalizado do 6c no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 6 | locsim_pen | 0.9218309048117984 |
| 94 | 0,0066 | NPE mediano do 6c no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 6 | npe_med | 0.006647632074273963 |
| 95 | 0,818 | LocSim@5 da âncora ingênua no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 9 | locsim_pen | 0.8184115515728485 |
| 96 | 85 | fração ao teto nos 19 clipes do train[::3] (%) | 6 | `docs/decisoes.md` | 287 | — | (no texto da linha) |
| 97 | 19 | clipes de calibração do treino (train[::3]) | 6 | `docs/decisoes.md` | 287 | — | (no texto da linha) |
| 98 | 74 | fração ao teto na validação (%) | 6 | `docs/decisoes.md` | 472 | — | (no texto da linha) |
| 99 | 10 | âncoras aceitas erradas na validação (%) | 6 | `docs/decisoes.md` | 476 | — | (no texto da linha) |
| 100 | 81,4 | HSB (1) só propagação, média por frame (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T2.csv` | 12 | (1) só propagação pen média × 100 | 0.8137045363350623 |
| 101 | 92,7 | HSB (1) só propagação, mediana (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 12 | (1) só propagação pen mediana × 100 | 0.9270635285619413 |
| 102 | 1,000 | HSB (1) cobertura nos frames com pessoas | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 12 | (1) só propagação cobertura frames com pessoas | 1.0 |
| 103 | 17,7 | HSB (2) detector, média (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector pen média × 100 | 0.17652374081667707 |
| 104 | 0,0 | HSB (2) detector, mediana (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector pen mediana × 100 | 0.0 |
| 105 | 0,221 | HSB (2) detector, cobertura nos frames com pessoas | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector cobertura frames com pessoas | 0.22142857142857142 |
| 106 | 79,7 | HSB (2) detector nos cobertos, média (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector cob média × 100 | 0.7972039907849933 |
| 107 | 61,7 | HSB (3) pipeline, média (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen média × 100 | 0.617443855691164 |
| 108 | 71,1 | HSB (3) pipeline, mediana (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen mediana × 100 | 0.7110783802185268 |
| 109 | 0,829 | HSB (3) pipeline, cobertura nos frames com pessoas | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline cobertura frames com pessoas | 0.8285714285714286 |
| 110 | 1.120 | frames com pessoas do HSB | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 46 | — | (no texto da linha) |
| 111 | 43,15 | NBJW sozinho no HSB, média (AuxFlow, tabela 4) | 2, 6, 9 | `docs/00-problema.md` | 49 | — | (no texto da linha) |
| 112 | 35,93 | NBJW no HSB, mediana (AuxFlow, tabela 4) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 49 | — | (no texto da linha) |
| 113 | 83,67 | AuxFlow no HSB, média (tabela 4) | 2, 6, 9 | `docs/00-problema.md` | 40 | — | (no texto da linha) |
| 114 | 96,15 | AuxFlow no HSB, mediana (tabela 4) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 49 | — | (no texto da linha) |
| 115 | 97,4 | SNGS-128, só propagação (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 5 | (1) só propagação pen média × 100 | 0.9739655444663796 |
| 116 | 96,5 | SNGS-138, só propagação (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 7 | (1) só propagação pen média × 100 | 0.9650115435209584 |
| 117 | 0 | SNGS-128 e SNGS-138: pipeline vale 0 (sem âncora) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 5 | (3) pipeline pen média | 0.0 |
| 118 | 87,2 | SNGS-136, só propagação (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (1) só propagação pen média × 100 | 0.8722673151278317 |
| 119 | 85,7 | SNGS-136, pipeline (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (3) pipeline pen média × 100 | 0.8570981719191836 |
| 120 | 44,2 | SNGS-136, detector penalizado (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (2) detector pen média × 100 | 0.4424735973751346 |
| 121 | 60 | SNGS-136, início do intervalo do HSB | 6 | `data_splits/hsb.csv` | 6 | inicio | 60 |
| 122 | 280 | SNGS-136, fim do intervalo do HSB | 6 | `data_splits/hsb.csv` | 6 | fim | 280 |
| 123 | 0,64 | SNGS-150: cobertura do detector nos frames com H_gt | 8 | `outputs/runs/rodada_test/tabelas/T2.csv` | 8 | (2) detector cobertura | 0.6428571428571429 |
| 124 | 0,07 | SNGS-150: cobertura do detector nos frames com pessoas | 8 | `outputs/runs/rodada_test/tabelas/T2.csv` | 8 | (2) detector cobertura frames com pessoas | 0.06870229007633588 |
| 125 | 0,575 | cobertura do detector no WC14 test | 6, 9 | `outputs/runs/rodada_test/tabelas/T3.csv` | 4 | media | 0.5752688172043011 |
| 126 | 186 | imagens do WC14 test | Resumo, 4, 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 2 | media | 186 |
| 127 | 0,913 | IoU_whole mediano, WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 5 | mediana | 0.9131266960388786 |
| 128 | 0,864 | IoU_whole médio, WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 5 | media | 0.8635098695256653 |
| 129 | 0,995 | IoU_part mediano, WC14 test | 6, 9 | `outputs/runs/rodada_test/tabelas/T3.csv` | 6 | mediana | 0.9946079029829488 |
| 130 | 0,380 | RE mediano (m), WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 8 | mediana | 0.37991867462940904 |
| 131 | 1,615 | RE médio (m), WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 8 | media | 1.615112838440006 |
| 132 | 107 | imagens com H (protocolo KpSFR) | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 2 | imagens | 107 |
| 133 | 0,937 | iou_part médio no protocolo KpSFR, 107 imagens | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 2 | media | 0.9369692023209888 |
| 134 | 0,539 | iou_part médio, 186 imagens com 0 nas sem H | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 6 | media | 0.5390091647760527 |
| 135 | 79 | imagens do WC14 test sem H | 6 | `derivado: 186 − 107` | — | — | 79 |
| 136 | 0 | imagem sem H vale 0 na nossa convenção | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 6 | — | (no texto da linha) |
| 137 | 100 | ECC convergiu em 100% dos pares | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 67 | — | (no texto da linha) |
| 138 | 36.701 | pares de frames consecutivos do ECC | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 67 | — | (no texto da linha) |
| 139 | 0,987 | correlação mediana do ECC | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 67 | — | (no texto da linha) |
| 140 | 17.828 | frames na interseção das cinco séries | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 76 | — | (no texto da linha) |
| 141 | 36.750 | frames do GSR test | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 76 | — | (no texto da linha) |
| 142 | 0,13 | tremor_med (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | tremor_med | 0.12705495063616054 |
| 143 | 0,57 | tremor_p90 (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | tremor_p90 | 0.5747011364830146 |
| 144 | 1,71 | deslize_med (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | deslize_med | 1.7122490859544373 |
| 145 | 5,45 | deslize_p90 (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | deslize_p90 | 5.44652216220271 |
| 146 | 0,40 | tremor_med (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | tremor_med | 0.39837273079606117 |
| 147 | 1,43 | tremor_p90 (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | tremor_p90 | 1.4311293022953095 |
| 148 | 1,38 | deslize_med (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | deslize_med | 1.3759090615954128 |
| 149 | 4,33 | deslize_p90 (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | deslize_p90 | 4.32759718031505 |
| 150 | 1,29 | tremor_med (px) de detector na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 2 | tremor_med | 1.2880092272994736 |
| 151 | 15,50 | tremor_p90 (px) de detector na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 2 | tremor_p90 | 15.502834899744936 |
| 152 | 1,90 | deslize_med (px) de 6a Bassek na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 3 | deslize_med | 1.89765570974326 |
| 153 | 8,31 | deslize_p90 (px) de 6a Bassek na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 3 | deslize_p90 | 8.307192313852513 |
| 154 | 4,17 | deslize p90 (px) do 6c no próprio conjunto | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | deslize_p90 | 4.174295627239621 |
| 155 | 23,51 | deslize p90 (px) do Kalman no próprio conjunto | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 5 | deslize_p90 | 23.513633413460205 |
| 156 | 72,61 | deslize p90 (px) do 6a Bassek no próprio conjunto | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 3 | deslize_p90 | 72.60673345089245 |
| 157 | 4,25 | deslize mediano (px) do 6c sem fluxo | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 7 | deslize_med | 4.250941912282512 |
| 158 | 0,8 | jogadores invertidos do 6c na interseção (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | jogadores × 100 | 0.008411584582703042 |
| 159 | 4,4 | jogadores invertidos do Kalman na interseção (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | jogadores × 100 | 0.043892732929131484 |
| 160 | 5,0 | jogadores invertidos do detector na interseção (%) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 2 | jogadores × 100 | 0.0499068324247626 |
| 161 | 53,5 | jogadores invertidos do detector, penalizada (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 2 | jogadores_penalizada × 100 | 0.5347640828260538 |
| 162 | 11,8 | jogadores invertidos do 6c, penalizada (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | jogadores_penalizada × 100 | 0.1184785773854684 |
| 163 | 5,6 | jogadores invertidos do detector, só cobertos (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 2 | jogadores_só cobertos × 100 | 0.05558504435383341 |
| 164 | 2,1 | jogadores invertidos do 6c, só cobertos (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | jogadores_só cobertos × 100 | 0.020613020580008055 |
| 165 | 0,1 | frames com 0 visíveis do 6c, só cobertos (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | zero_visiveis_só cobertos × 100 | 0.0008182790961163215 |
| 166 | 3 | 0 visíveis no feed de scouting de Bassek et al. (%) | 2, 6 | `docs/00-problema.md` | 92 | — | (no texto da linha) |
| 167 | 1 | 1 jogador visível no feed de scouting de Bassek et al. (%) | 2 | `docs/00-problema.md` | 91 | — | (no texto da linha) |
| 168 | 958 | âncoras candidatas | 6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 2 | n | 958 |
| 169 | 28,3 | candidatas erradas, entre as com gabarito (%) | 6, 9 | `derivado: 270 / 955` | — | — | 28.2723 |
| 170 | 558 | âncoras aceitas | 6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | n | 558 |
| 171 | 2,2 | aceitas erradas, entre as com gabarito (%) = 12 / 557 | 6, 9 | `derivado: 12 / 557` | — | — | 2.1544 |
| 172 | 12 | âncoras aceitas erradas | 6, 7 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | erradas | 12 |
| 173 | 5 | clipes sem âncora aceita | 6, 7 | `outputs/runs/rodada_test/tabelas/T7.csv` | 5 | n | 5 |
| 174 | 0,05 | limiar de âncora/H errada (NPE > 0,05) | 4, 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 92 | — | (no texto da linha) |
| 175 | 1.665 | frames na lacuna 1-3 | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | frames | 1665 |
| 176 | 0,0974 | NPE mediano, 6a Bassek, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6a Bassek NPE | 0.09738772017678735 |
| 177 | 0,0324 | NPE mediano, 6a robusto, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6a robusto NPE | 0.03239201394670842 |
| 178 | 0,0095 | NPE mediano, 6c fluxo, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6c fluxo NPE | 0.00951444925996717 |
| 179 | 0,0115 | NPE mediano, 6c sem linhas, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6c sem linhas NPE | 0.011450080998323666 |
| 180 | 4.624 | frames na lacuna 4-25 | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | frames | 4624 |
| 181 | 0,8994 | NPE mediano, 6a Bassek, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6a Bassek NPE | 0.899380036414921 |
| 182 | 0,7960 | NPE mediano, 6a robusto, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6a robusto NPE | 0.7960247823207365 |
| 183 | 0,0168 | NPE mediano, 6c fluxo, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6c fluxo NPE | 0.01679906796130583 |
| 184 | 0,0247 | NPE mediano, 6c sem linhas, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6c sem linhas NPE | 0.024700604200718 |
| 185 | 8.391 | frames na lacuna > 25 | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 4 | frames | 8391 |
| 186 | 0,0551 | NPE mediano, 6c fluxo, lacuna > 25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 4 | 6c fluxo NPE | 0.055100629444049976 |
| 187 | 0,0785 | NPE mediano, 6c sem linhas, lacuna > 25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 4 | 6c sem linhas NPE | 0.07853632934367849 |
| 188 | 3.088 | frames na lacuna pontas | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 5 | frames | 3088 |
| 189 | 0,1221 | NPE mediano, 6c fluxo, lacuna pontas | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 5 | 6c fluxo NPE | 0.12207070026322503 |
| 190 | 0,1355 | NPE mediano, 6c sem linhas, lacuna pontas | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 5 | 6c sem linhas NPE | 0.1355059881198888 |
| 191 | 1 | limite das faixas de lacuna (1-3) | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | — | (no texto da linha) |
| 192 | 3 | limite das faixas de lacuna (1-3) | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | — | (no texto da linha) |
| 193 | 4 | limite das faixas de lacuna (4-25) | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | — | (no texto da linha) |
| 194 | 25 | limite das faixas de lacuna (4-25, > 25) | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | — | (no texto da linha) |
| 195 | 99 | lacunas de 4-25 com as duas bordas certas | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 2 | lacunas | 99 |
| 196 | 106 | lacunas de 4-25 com uma borda errada | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 3 | lacunas | 106 |
| 197 | 331 | lacunas de 4-25 com as duas bordas erradas | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 4 | lacunas | 331 |
| 198 | 1 | lacuna de 4-25 com borda sem gabarito | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 5 | lacunas | 1 |
| 199 | 537 | lacunas de 4-25 frames no test | 7 | `derivado: 99 + 106 + 331 + 1` | — | — | 537 |
| 200 | 62 | lacunas de 4-25 com as duas bordas erradas (%) | 6 | `derivado: 331 / 537` | — | — | 61.6387 |
| 201 | 0,0242 | NPE mediano do 6a Bassek com as duas bordas certas | 6 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 2 | bassek_npe_med | 0.024242664392004017 |
| 202 | 8,58 | parede da série do detector (h) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | parede_h | 8.575277777777778 |
| 203 | 15 | processos da série do detector | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | processos | 15 |
| 204 | 1,19 | vazão da série (frames/s) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | frames_por_s | 1.1904376275468886 |
| 205 | 9.344 | s por clipe num processo, série | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | s_por_clipe_processo | 9343.991836734693 |
| 206 | 630 | s de parede por clipe com 15 processos, série | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | s_por_clipe_parede | 630.0204081632653 |
| 207 | 1,71 | parede do 6c (h) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 3 | parede_h | 1.7094444444444445 |
| 208 | 10 | processos do 6c | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 3 | processos | 10 |
| 209 | 292 | AuxFlow, s por clipe (tabela 6) | 6, 9 | `outputs/runs/rodada_test/tabelas/T9.csv` | 8 | s_por_clipe | 292 |
| 210 | 2,6 | AuxFlow, FPS (tabela 6) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 8 | fps | 2.6 |
| 211 | 4,76 | detector, s por frame num núcleo, GSR | 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 106 | — | (no texto da linha) |
| 212 | 3.570 | detector, s por clipe de 750 frames num núcleo (perfil) | 9 | `docs/03-plano.md` | 580 | — | (no texto da linha) |
| 213 | 2,90 | detector, s por frame num núcleo, WC14 | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 106 | — | (no texto da linha) |
| 214 | 127 | 6c fluxo, ms por frame | 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 106 | — | (no texto da linha) |
| 215 | 750 | frames por clipe | 4, 6 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 216 | 7 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 217 | 8 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 218 | 16 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 219 | 5060 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 220 | 4090 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 221 | 0,252 | LocSim@5 penalizado do 6c, SNGS-149 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 35 | c6 | 0.25245385124828923 |
| 222 | 0,458 | LocSim@5 penalizado do 6c, SNGS-119 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 5 | c6 | 0.45772018093220884 |
| 223 | 0,495 | LocSim@5 penalizado do 6c, SNGS-143 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 29 | c6 | 0.4952325656550445 |
| 224 | 0,495 | LocSim@5 penalizado do teto, SNGS-143 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 29 | teto | 0.49477118746227106 |
| 225 | 0,506 | LocSim@5 penalizado do 6c, SNGS-144 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 30 | c6 | 0.5055174044700732 |
| 226 | 0,508 | LocSim@5 penalizado do teto, SNGS-144 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 30 | teto | 0.5077625470280754 |
| 227 | 0,587 | LocSim@5 penalizado do 6c, SNGS-148 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 34 | c6 | 0.5873981000471749 |
| 228 | 0,635 | LocSim@5 penalizado do 6c, SNGS-126 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 12 | c6 | 0.634512353785477 |
| 229 | 0,954 | LocSim@5 penalizado do teto, SNGS-126 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 12 | teto | 0.9541771572553578 |
| 230 | 6 | piores clipes inspecionados | 7 | `docs/03-plano.md` | 664 | — | (no texto da linha) |
| 231 | 12 | âncoras erradas inspecionadas | 7 | `docs/03-plano.md` | 664 | — | (no texto da linha) |
| 232 | 5 | clipes sem âncora inspecionados | 7 | `docs/03-plano.md` | 636 | — | (no texto da linha) |
| 233 | 3 | lacunas de exemplo inspecionadas | 7 | `docs/03-plano.md` | 636 | — | (no texto da linha) |
| 234 | 1,355 | NPE da âncora SNGS-126 f588 | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 3 | npe | 1.3550949476054246 |
| 235 | 0,060 | menor NPE das âncoras de encaixe parcial (SNGS-122 f657) | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 2 | npe | 0.0596927737995924 |
| 236 | 0,235 | maior NPE das âncoras de encaixe parcial (SNGS-190 f525) | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 12 | npe | 0.23549481829491842 |
| 237 | 0,063 | NPE da âncora SNGS-132 f721 | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 4 | npe | 0.0633359702238581 |
| 238 | 10 | âncoras de encaixe parcial: as aceitas erradas menos a troca de reta (SNGS-126 f588) e a quase certa (SNGS-132 f721) | 7 | `derivado: linhas de outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv sem SNGS-126 e SNGS-132` | — | — | 10 |
| 239 | 13 | clipes sem âncora da valid no jogo 3 | 7, 8 | `docs/decisoes.md` | 370 | — | (no texto da linha) |
| 240 | 18 | clipes sem âncora da valid | 7, 8 | `docs/decisoes.md` | 374 | — | (no texto da linha) |
| 241 | 1 | diagnóstico da segmentação em 1 frame a cada 75 | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 61 | — | (no texto da linha) |
| 242 | 75 | diagnóstico da segmentação em 1 frame a cada 75 | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 61 | — | (no texto da linha) |
| 243 | 0,988 | menor fração do campo como grama nos sem âncora (SNGS-138) | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 5 | campo_grama | 0.9881636617093701 |
| 244 | 0,81 | cobertura das marcações a 2 px, SNGS-127 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 2 | cobertura_2px | 0.8090467516697024 |
| 245 | 0,85 | cobertura das marcações a 2 px, SNGS-128 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 3 | cobertura_2px | 0.8461538461538461 |
| 246 | 0,98 | cobertura das marcações a 2 px, SNGS-138 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 5 | cobertura_2px | 0.9770642201834863 |
| 247 | 0,89 | cobertura das marcações a 2 px, clipes com âncora do jogo 7 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 7 | cobertura_2px | 0.8863636363636364 |
| 248 | 0,79 | cobertura das marcações a 2 px, referência da Fatia 3 (GSR train) | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 71 | — | (no texto da linha) |
| 249 | 2 | cobertura das marcações a 2 px | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 71 | — | (no texto da linha) |
| 250 | 52 | SNGS-147: pontos anotados acima do limiar (%) | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 6 | acima_limiar × 100 | 0.5192307692307692 |
| 251 | 68 | clipes com âncora do jogo 8: pontos acima do limiar (%) | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 8 | acima_limiar × 100 | 0.6809593023255813 |
| 252 | 11 | candidatas verificáveis do SNGS-147 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 33 | verificaveis | 11 |
| 253 | 0,7 | menor cobertura do detector nos sem âncora (SNGS-138, %) | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 24 | cob_det × 100 | 0.007194244604316547 |
| 254 | 15,9 | maior cobertura do detector nos sem âncora (SNGS-147, %) | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 33 | cob_det × 100 | 0.15930388219544847 |
| 255 | 0,0059 | NPE mediano do 6c a <= 25 frames da âncora, frames com H do detector | 7 | `outputs/runs/rodada_test/falhas/deriva_6c.csv` | 2 | npe_med | 0.005897785590997996 |
| 256 | 0,0101 | NPE mediano do 6c a <= 25 frames da âncora, pontas | 7 | `outputs/runs/rodada_test/falhas/deriva_6c.csv` | 14 | npe_med | 0.010138998451541235 |
| 257 | 0,208 | NPE mediano do 6c nas pontas a > 250 frames da âncora | 7, 8 | `outputs/runs/rodada_test/falhas/deriva_6c.csv` | 17 | npe_med | 0.207852393306958 |
| 258 | 250 | faixa de distância à âncora (> 250 frames) | 7, 8 | `outputs/runs/rodada_test/analise_falhas.out` | 45 | — | (no texto da linha) |
| 259 | 7,1 | NPE do 6a Bassek no meio da lacuna da Figura 7 (SNGS-121, f14) | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_test.csv` | 521 | npe | 7.107828310199786 |
| 260 | 2 | lacuna da Figura 7 (2-26) | 7 | `outputs/runs/rodada_test/falhas/lacunas_figuras.csv` | 4 | — | (no texto da linha) |
| 261 | 26 | lacuna da Figura 7 (2-26) | 7 | `outputs/runs/rodada_test/falhas/lacunas_figuras.csv` | 4 | — | (no texto da linha) |
| 262 | 25 | passos da sensibilidade (±25%) | 8 | `docs/03-plano.md` | 445 | — | (no texto da linha) |
| 263 | 50 | passos da sensibilidade (±50%) | 8 | `docs/03-plano.md` | 445 | — | (no texto da linha) |
| 264 | 0,017 | valor de um frame ou imagem nos subconjuntos | 8 | `docs/decisoes.md` | 518 | — | (no texto da linha) |
| 265 | 0,029 | valor de um frame ou imagem nos subconjuntos | 8 | `docs/decisoes.md` | 518 | — | (no texto da linha) |
| 266 | 14 | configurações da confirmação do detector (atual + 13 candidatos) | 8 | `docs/decisoes.md` | 646 | — | (no texto da linha) |
| 267 | 3 | configurações da confirmação do 6c (atual + 2 candidatos) | 8 | `docs/decisoes.md` | 646 | — | (no texto da linha) |
| 268 | 15 | candidatos confirmados (13 do detector + 2 do 6c) | 8 | `derivado: (14 − 1) + (3 − 1)` | — | — | 15 |
| 269 | 0,02 | ganho mínimo para virar candidato | 8 | `docs/decisoes.md` | 538 | — | (no texto da linha) |
| 270 | 30 | limiar de contraste das marcações no GSR, atual | 3, 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 271 | 15 | limiar candidato (recusado) | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 272 | +0,034 | Δ LocSim do line_thr 15 | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 273 | +0,003 | IC inferior do Δ do line_thr 15 | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 274 | +0,065 | IC superior do Δ do line_thr 15 | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 275 | +0,127 | Δ LocSim do line_thr 15 no jogo 4 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 276 | −0,046 | Δ LocSim do line_thr 15 no jogo 9 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 277 | 0,0056 | NPE mediano do jogo 9, limiar 30 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 278 | 0,0130 | NPE mediano do jogo 9, limiar 15 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 279 | 52 | fração do campo coberta pelo gramado no jogo 3 da valid (%) | 8 | `docs/decisoes.md` | 114 | — | (no texto da linha) |
| 280 | 2,33 | frames do test sem H_gt na geração do gabarito (Fatia 2, %) | 8 | `docs/decisoes.md` | 63 | — | (no texto da linha) |
| 281 | 3 | homografia 3 × 3 | 1 | `docs/00-problema.md` | 8 | — | (no texto da linha) |
| 282 | 2 | 2 + 2 retas de duas famílias | Resumo, 3, 7, 8 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 283 | 0,5 | BroadTrack reinicia com IoU < 0,5 | 2 | `docs/01-metodo.md` | 285 | — | (no texto da linha) |
| 284 | 0,8397 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 313 | — | (no texto da linha) |
| 285 | 0,8352 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 313 | — | (no texto da linha) |
| 286 | 0,9224 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 314 | — | (no texto da linha) |
| 287 | 0,9426 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 314 | — | (no texto da linha) |
| 288 | 1,34 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 314 | — | (no texto da linha) |
| 289 | 0,84 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 315 | — | (no texto da linha) |
| 290 | 2,5 | grade de pontos auxiliares 2,5 × 2 m | 2, 3, 5 | `docs/01-metodo.md` | 251 | — | (no texto da linha) |
| 291 | 2 | grade de pontos auxiliares 2,5 × 2 m | 2, 3, 5 | `docs/01-metodo.md` | 251 | — | (no texto da linha) |
| 292 | 1 | erro de ida e volta <= 1 px | 2, 3 | `docs/01-metodo.md` | 256 | — | (no texto da linha) |
| 293 | 23,42 | AuxFlow sem fluxo no HSB | 2 | `docs/00-problema.md` | 40 | — | (no texto da linha) |
| 294 | 78,30 | AuxFlow sem pontos-chave do detector no HSB | 2 | `docs/01-metodo.md` | 258 | — | (no texto da linha) |
| 295 | 78,71 | RAFT no lugar do Lucas–Kanade | 2 | `docs/00-problema.md` | 42 | — | (no texto da linha) |
| 296 | 39,68 | amostragem geométrica no AuxFlow | 2 | `docs/01-metodo.md` | 253 | — | (no texto da linha) |
| 297 | 83,39 | amostragem aleatória no AuxFlow | 2 | `docs/01-metodo.md` | 254 | — | (no texto da linha) |
| 298 | 150 | âncoras ingênuas a cada 150 frames | 2, 3 | `docs/01-metodo.md` | 265 | — | (no texto da linha) |
| 299 | 82,48 | âncoras ingênuas no AuxFlow | 2 | `docs/01-metodo.md` | 266 | — | (no texto da linha) |
| 300 | 83,48 | detector sem propagação no AuxFlow | 2 | `docs/01-metodo.md` | 266 | — | (no texto da linha) |
| 301 | 90,65 | âncoras por heurística no AuxFlow | 2 | `docs/01-metodo.md` | 267 | — | (no texto da linha) |
| 302 | 91,88 | âncora de gabarito no AuxFlow | 2 | `docs/01-metodo.md` | 267 | — | (no texto da linha) |
| 303 | 54,74 | AuxFlow com a H inicial perturbada | 2 | `docs/00-problema.md` | 48 | — | (no texto da linha) |
| 304 | 31 | janela do Savitzky–Golay (Bassek et al.) | 2, 3 | `docs/00-problema.md` | 59 | — | (no texto da linha) |
| 305 | 3 | grau do Savitzky–Golay (Bassek et al.) | 2, 3 | `config.yaml` | 225 | — | (no texto da linha) |
| 306 | 25 | lacunas preenchidas por interpolação (Bassek et al.) | 2, 3 | `docs/01-metodo.md` | 212 | — | (no texto da linha) |
| 307 | 981 | cortes por partida (Bassek et al.) | 2 | `docs/01-metodo.md` | 276 | — | (no texto da linha) |
| 308 | 10,9 | cortes por minuto (Bassek et al.) | 2 | `docs/01-metodo.md` | 276 | — | (no texto da linha) |
| 309 | 115 | molde do PnLCalib no WC14 (115 × 74 jardas) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 310 | 74 | molde do PnLCalib no WC14 (115 × 74 jardas) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 311 | 100 | molde do KpSFR e de Maglo et al. (100 × 60 m) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 312 | 60 | molde do KpSFR e de Maglo et al. (100 × 60 m) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 313 | 105 | modelo do campo 105 × 68 m | 3 | `docs/01-metodo.md` | 19 | — | (no texto da linha) |
| 314 | 68 | modelo do campo 105 × 68 m | 3 | `docs/01-metodo.md` | 19 | — | (no texto da linha) |
| 315 | 20 | faixa de matiz do gramado (±20°) | 3 | `docs/decisoes.md` | 73 | — | (no texto da linha) |
| 316 | 0,9861 | IoU médio do gramado no WC14 train_val | 3 | `docs/decisoes.md` | 75 | — | (no texto da linha) |
| 317 | 15 | limiar das marcações no WC14 | 3 | `docs/decisoes.md` | 74 | — | (no texto da linha) |
| 318 | 30 | limiar das marcações no GSR | 3 | `docs/decisoes.md` | 74 | — | (no texto da linha) |
| 319 | 180 | simetria de 180° do campo | 3, 7 | `docs/03-plano.md` | 310 | — | (no texto da linha) |
| 320 | 0,45 | portão: fração explicada | 3 | `config.yaml` | 201 | — | (no texto da linha) |
| 321 | 0,85 | portão: IoU com o gramado | 3 | `config.yaml` | 202 | — | (no texto da linha) |
| 322 | 5 | portões logo abaixo do percentil 5 da H_gt | 3 | `config.yaml` | 202 | — | (no texto da linha) |
| 323 | 12 | janela das âncoras candidatas (±12 frames) | 3 | `config.yaml` | 246 | — | (no texto da linha) |
| 324 | 2 | vizinhos mínimos da verificação | 3 | `config.yaml` | 249 | — | (no texto da linha) |
| 325 | 209 | imagens de treino do WC14 | 4 | `docs/02-dados.md` | 35 | — | (no texto da linha) |
| 326 | 1280 | resolução do WC14 | 4 | `docs/02-dados.md` | 36 | — | (no texto da linha) |
| 327 | 720 | resolução do WC14 | 4 | `docs/02-dados.md` | 36 | — | (no texto da linha) |
| 328 | 25 | fps do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 329 | 1920 | resolução do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 330 | 1080 | resolução do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 331 | 57 | clipes de treino do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 332 | 58 | clipes de validação do GSR | 4 | `docs/02-dados.md` | 75 | — | (no texto da linha) |
| 333 | 3 | RANSAC a 3 px da H_gt_auxflow | 4 | `docs/01-metodo.md` | 332 | — | (no texto da linha) |
| 334 | 10 | clipes do HSB | 4 | `docs/02-dados.md` | 91 | — | (no texto da linha) |
| 335 | 0 | numeração dos frames a partir de 0 | 4 | `docs/02-dados.md` | 112 | — | (no texto da linha) |
| 336 | 90 | intervalo "90–0" do SNGS-128 | 4 | `docs/02-dados.md` | 107 | — | (no texto da linha) |
| 337 | 0 | intervalo "90–0" do SNGS-128 | 4 | `docs/02-dados.md` | 107 | — | (no texto da linha) |
| 338 | 0,05 | LocSim: exp(ln(0,05)·d²/τ²) | 5 | `docs/01-metodo.md` | 367 | — | (no texto da linha) |
| 339 | 5 | τ = 5 m | 5 | `docs/01-metodo.md` | 370 | — | (no texto da linha) |
| 340 | 1 | mAP-LocSim: τ = 1 a 10 m | 5 | `docs/01-metodo.md` | 371 | — | (no texto da linha) |
| 341 | 10 | mAP-LocSim: τ = 1 a 10 m | 5 | `docs/01-metodo.md` | 371 | — | (no texto da linha) |
| 342 | 0 | pessoa de frame sem H vale 0 | 5 | `docs/01-metodo.md` | 377 | — | (no texto da linha) |
| 343 | 95 | intervalo de 95% | 5, 6 | `docs/03-plano.md` | 560 | — | (no texto da linha) |
| 344 | 2.000 | reamostragens do bootstrap | 5 | `docs/03-plano.md` | 560 | — | (no texto da linha) |
| 345 | 1.470 | frames da conferência de determinismo | 5, B | `docs/03-plano.md` | 678 | — | (no texto da linha) |
| 346 | 25 | frames da conferência: 1 a cada 25 | 5, B | `docs/03-plano.md` | 679 | — | (no texto da linha) |
| 347 | 735 | tarefas da série com a chave congelada | 5, B | `docs/03-plano.md` | 672 | — | (no texto da linha) |
| 348 | 47 | caches da valid gravados com a chave errada | 5 | `docs/decisoes.md` | 487 | — | (no texto da linha) |
| 349 | 0 | manifestos com 0 falhas | B | `docs/decisoes.md` | 849 | — | (no texto da linha) |
