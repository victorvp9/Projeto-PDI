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
| 13 | 0,959 | fração da distância ao teto condicionado às âncoras, propagação | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto | 0.9590228680694096 |
| 14 | 95,9 | a mesma fração, em % | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto × 100 | 0.9590228680694096 |
| 15 | 0,925 | fração ao teto, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto_lo | 0.9254527945921875 |
| 16 | 0,986 | fração ao teto, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto_hi | 0.9860390545455364 |
| 17 | 0,680 | cobertura de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | cobertura | 0.6801794271704001 |
| 18 | 0,0126 | npe_med de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | npe_med | 0.012613672816508013 |
| 19 | 0,446 | locsim_pen de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | locsim_pen | 0.446264162800887 |
| 20 | 0,681 | locsim_cob de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | locsim_cob | 0.681350553316294 |
| 21 | 0,078 | fracao_teto de 6a Bassek (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 3 | fracao_teto | 0.07849190694916243 |
| 22 | 0,665 | cobertura de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | cobertura | 0.6648556781455478 |
| 23 | 0,0097 | npe_med de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | npe_med | 0.0096917669537372 |
| 24 | 0,478 | locsim_pen de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | locsim_pen | 0.47804103599812126 |
| 25 | 0,747 | locsim_cob de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | locsim_cob | 0.747117357316682 |
| 26 | 0,171 | fracao_teto de 6a robusto (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 4 | fracao_teto | 0.1709126176024358 |
| 27 | 0,680 | cobertura de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | cobertura | 0.6798172294661763 |
| 28 | 0,0113 | npe_med de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | npe_med | 0.011285736170425269 |
| 29 | 0,490 | locsim_pen de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | locsim_pen | 0.49042315851089474 |
| 30 | 0,749 | locsim_cob de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | locsim_cob | 0.749173260806681 |
| 31 | 0,207 | fracao_teto de Kalman + RTS (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 5 | fracao_teto | 0.20692511495935076 |
| 32 | 0,897 | cobertura de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | cobertura | 0.8971358520004458 |
| 33 | 0,0122 | npe_med de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | npe_med | 0.01220103731093986 |
| 34 | 0,715 | locsim_pen de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | locsim_pen | 0.715153688402002 |
| 35 | 0,796 | locsim_cob de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | locsim_cob | 0.7957915016505123 |
| 36 | 0,861 | fracao_teto de 6c sem linhas (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 7 | fracao_teto | 0.8605374181305308 |
| 37 | 0,897 | cobertura de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | cobertura | 0.8971358520004458 |
| 38 | 0,1248 | npe_med de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | npe_med | 0.12482665639288845 |
| 39 | 0,366 | locsim_pen de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | locsim_pen | 0.3659943581643886 |
| 40 | 0,407 | locsim_cob de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | locsim_cob | 0.4072623893334853 |
| 41 | −0,155 | fracao_teto de 6c sem fluxo (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 8 | fracao_teto | -0.15496694667871075 |
| 42 | 1,000 | cobertura de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | cobertura | 1.0 |
| 43 | 0,0262 | npe_med de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | npe_med | 0.026157020939553043 |
| 44 | 0,571 | locsim_pen de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | locsim_pen | 0.5713680143832477 |
| 45 | 0,571 | locsim_cob de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | locsim_cob | 0.5713680143832477 |
| 46 | 0,442 | fracao_teto de 6c âncora ingênua /150 (Tabela 1) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 9 | fracao_teto | 0.4423473057147572 |
| 47 | 0,897 | cobertura da âncora de gabarito (teto) | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | cobertura | 0.8971358520004458 |
| 48 | 0,0064 | NPE mediano do teto | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | npe_med | 0.00643616224779207 |
| 49 | 0,763 | LocSim@5 penalizado do teto | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | locsim_pen | 0.7631048970488494 |
| 50 | 0,849 | LocSim@5 do teto nos cobertos | 6 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | locsim_cob | 0.8491494930219861 |
| 51 | 49 | clipes do GSR test | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 1 | — | (no texto da linha) |
| 52 | 3 | jogos do GSR test | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 1 | — | (no texto da linha) |
| 53 | 10 | reamostragens distintas do bootstrap com 3 jogos | 5 | `outputs/runs/rodada_test/tabelas_v2.out` | 4 | — | (no texto da linha) |
| 54 | 44 | clipes com >= 1 âncora aceita | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 1 | — | (no texto da linha) |
| 55 | 7 | jogo do GSR test | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | jogo | 7 |
| 56 | 16 | clipes do jogo 7 | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | clipes | 16 |
| 57 | 14 | clipes com âncora do jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | com_ancora | 14 |
| 58 | 0,472 | cobertura do detector, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | cob_detector | 0.4719110587046239 |
| 59 | 0,874 | cobertura do 6c, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | cob_6c | 0.8736629327044555 |
| 60 | 0,341 | LocSim@5 penalizado do detector, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | locsim_pen_detector | 0.3410869352412535 |
| 61 | 0,676 | LocSim@5 penalizado do 6c, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | locsim_pen_6c | 0.6759710080828238 |
| 62 | 0,703 | LocSim@5 penalizado do teto, jogo 7 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 2 | locsim_pen_teto | 0.7029466376468649 |
| 63 | 8 | jogo do GSR test | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | jogo | 8 |
| 64 | 19 | clipes do jogo 8 | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | clipes | 19 |
| 65 | 16 | clipes com âncora do jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | com_ancora | 16 |
| 66 | 0,447 | cobertura do detector, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | cob_detector | 0.4473489883325949 |
| 67 | 0,838 | cobertura do 6c, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | cob_6c | 0.8381332151823955 |
| 68 | 0,360 | LocSim@5 penalizado do detector, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | locsim_pen_detector | 0.35974187056903534 |
| 69 | 0,650 | LocSim@5 penalizado do 6c, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | locsim_pen_6c | 0.6499967158730243 |
| 70 | 0,661 | LocSim@5 penalizado do teto, jogo 8 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 3 | locsim_pen_teto | 0.6608245337278049 |
| 71 | 11 | jogo do GSR test | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | jogo | 11 |
| 72 | 14 | clipes do jogo 11 | 4, 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | clipes | 14 |
| 73 | 14 | clipes com âncora do jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | com_ancora | 14 |
| 74 | 0,617 | cobertura do detector, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | cob_detector | 0.6168750596544812 |
| 75 | 1,000 | cobertura do 6c, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | cob_6c | 1.0 |
| 76 | 0,555 | LocSim@5 penalizado do detector, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | locsim_pen_detector | 0.5546704626197827 |
| 77 | 0,920 | LocSim@5 penalizado do 6c, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | locsim_pen_6c | 0.9199799820597924 |
| 78 | 0,925 | LocSim@5 penalizado do teto, jogo 11 | 6 | `outputs/runs/rodada_test/tabelas/T6.csv` | 4 | locsim_pen_teto | 0.9251522581997559 |
| 79 | 0,03 | o 6c fica a menos disto do teto nos três jogos (máximo de teto − 6c: 0,027) | 6 | `derivado: max(teto − 6c) < 0,03` | — | — | 0.03 |
| 80 | +0,330 | ganho 6c − detector, penalizado | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | pen | 0.32973938261759295 |
| 81 | 0,290 | ganho, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | pen_lo | 0.2902548453039891 |
| 82 | 0,365 | ganho, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | pen_hi | 0.36530951944000956 |
| 83 | −0,035 | ganho 6c − detector nos cobertos | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | cob | -0.035075524143007075 |
| 84 | 0,035 | o mesmo, em módulo ("fica 0,035 abaixo") | 6 | `derivado: |ganho nos cobertos|` | — | — | 0.0350755 |
| 85 | −0,078 | ganho nos cobertos, IC inferior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | cob_lo | -0.0780199152971085 |
| 86 | −0,003 | ganho nos cobertos, IC superior | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 7 | cob_hi | -0.00307166492950528 |
| 87 | 0,885 | LocSim@5 do NBJW, tabela 7 do AuxFlow | 2, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 2 | locsim5 | 0.885 |
| 88 | 0,929 | LocSim@5 do AuxFlow, tabela 7 | 2, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 3 | locsim5 | 0.929 |
| 89 | +0,044 | ganho AuxFlow − NBJW | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T5.csv` | 4 | locsim5 | 0.04400000000000004 |
| 90 | 0,869 | LocSim@5 do detector no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 5 | comum | 0.8685472817991973 |
| 91 | 65 | fração da distância detector -> AuxFlow fechada pelo 6c (%) | 6, 9 | `derivado: (6c − detector) / (AuxFlow − detector)` | — | — | 64.6898 |
| 92 | 18.133 | frames do conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 2 | frames | 18133 |
| 93 | 0,922 | LocSim@5 penalizado do 6c no conjunto comum | Resumo, 6, 9 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 6 | locsim_pen | 0.9218309048117984 |
| 94 | 0,869 | LocSim@5 penalizado do detector no conjunto comum | 6, 9 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 2 | locsim_pen | 0.8685472817991973 |
| 95 | 0,131 | erro residual do detector no conjunto comum | 6 | `derivado: 1 − LocSim@5 pen. do detector (T1b)` | — | — | 0.131453 |
| 96 | 0,078 | erro residual da propagação no conjunto comum | 6 | `derivado: 1 − LocSim@5 pen. da propagação (T1b)` | — | — | 0.0781691 |
| 97 | 40 | redução do erro residual no conjunto comum (%), com os resíduos como escritos no texto (0,131 → 0,078; 40,5% com os brutos) | Resumo, 6, 9 | `derivado: (0,131 − 0,078) / 0,131` | — | — | 40.458 |
| 98 | 0,115 | erro residual do NBJW (tabela 7 do AuxFlow) | 6 | `derivado: 1 − 0,885` | — | — | 0.115 |
| 99 | 0,071 | erro residual do AuxFlow (tabela 7) | 6 | `derivado: 1 − 0,929` | — | — | 0.071 |
| 100 | 38 | redução do erro residual do AuxFlow sobre o NBJW (%) | Resumo, 6, 9 | `derivado: (0,929 − 0,885) / (1 − 0,885)` | — | — | 38.2609 |
| 101 | 0,581 | erro residual do detector, penalizado | 6 | `derivado: 1 − 0,419` | — | — | 0.580724 |
| 102 | 0,251 | erro residual da propagação, penalizado | 6 | `derivado: 1 − 0,749` | — | — | 0.250984 |
| 103 | 57 | redução do erro residual no conjunto inteiro (%) | 6 | `derivado: (0,749 − 0,419) / (1 − 0,419)` | — | — | 56.7808 |
| 104 | 0,0066 | NPE mediano do 6c no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 6 | npe_med | 0.006647632074273963 |
| 105 | 0,818 | LocSim@5 da âncora ingênua no conjunto comum | 6 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 9 | locsim_pen | 0.8184115515728485 |
| 106 | 85 | fração ao teto nos 19 clipes do train[::3] (%) | 6 | `docs/decisoes.md` | 287 | — | (no texto da linha) |
| 107 | 19 | clipes de calibração do treino (train[::3]) | 6 | `docs/decisoes.md` | 287 | — | (no texto da linha) |
| 108 | 74 | fração ao teto na validação (%) | 6 | `docs/decisoes.md` | 472 | — | (no texto da linha) |
| 109 | 10 | âncoras aceitas erradas na validação (%) | 6 | `docs/decisoes.md` | 476 | — | (no texto da linha) |
| 110 | 81,4 | HSB (1) só propagação, média por frame (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T2.csv` | 12 | (1) só propagação pen média × 100 | 0.8137045363350623 |
| 111 | 92,7 | HSB (1) só propagação, mediana (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 12 | (1) só propagação pen mediana × 100 | 0.9270635285619413 |
| 112 | 1,000 | HSB (1) cobertura nos frames com pessoas | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 12 | (1) só propagação cobertura frames com pessoas | 1.0 |
| 113 | 17,7 | HSB (2) detector, média (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector pen média × 100 | 0.17652374081667707 |
| 114 | 0,0 | HSB (2) detector, mediana (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector pen mediana × 100 | 0.0 |
| 115 | 0,221 | HSB (2) detector, cobertura nos frames com pessoas | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector cobertura frames com pessoas | 0.22142857142857142 |
| 116 | 79,7 | HSB (2) detector nos cobertos, média (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 13 | (2) detector cob média × 100 | 0.7972039907849933 |
| 117 | 61,7 | HSB (3) pipeline, média (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen média × 100 | 0.617443855691164 |
| 118 | 71,1 | HSB (3) pipeline, mediana (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen mediana × 100 | 0.7110783802185268 |
| 119 | 0,829 | HSB (3) pipeline, cobertura nos frames com pessoas | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline cobertura frames com pessoas | 0.8285714285714286 |
| 120 | 1.120 | frames com pessoas do HSB | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 46 | — | (no texto da linha) |
| 121 | 43,15 | NBJW sozinho no HSB, média (AuxFlow, tabela 4) | 2, 6, 9 | `docs/00-problema.md` | 49 | — | (no texto da linha) |
| 122 | 35,93 | NBJW no HSB, mediana (AuxFlow, tabela 4) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 49 | — | (no texto da linha) |
| 123 | 83,67 | AuxFlow no HSB, média (tabela 4) | 2, 6, 9 | `docs/00-problema.md` | 40 | — | (no texto da linha) |
| 124 | 96,15 | AuxFlow no HSB, mediana (tabela 4) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 49 | — | (no texto da linha) |
| 125 | 50,8 | SNGS-124, só propagação (%): a menor média do HSB | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 4 | (1) só propagação pen média × 100 | 0.508383235450467 |
| 126 | 97,4 | SNGS-128, só propagação (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 5 | (1) só propagação pen média × 100 | 0.9739655444663796 |
| 127 | 96,5 | SNGS-138, só propagação (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 7 | (1) só propagação pen média × 100 | 0.9650115435209584 |
| 128 | 0 | SNGS-128 e SNGS-138: pipeline vale 0 (sem âncora) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 5 | (3) pipeline pen média | 0.0 |
| 129 | 87,2 | SNGS-136, só propagação (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (1) só propagação pen média × 100 | 0.8722673151278317 |
| 130 | 85,7 | SNGS-136, pipeline (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (3) pipeline pen média × 100 | 0.8570981719191836 |
| 131 | 44,2 | SNGS-136, detector penalizado (%) | 6 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (2) detector pen média × 100 | 0.4424735973751346 |
| 132 | 60 | SNGS-136, início do intervalo do HSB | 6 | `data_splits/hsb.csv` | 6 | inicio | 60 |
| 133 | 280 | SNGS-136, fim do intervalo do HSB | 6 | `data_splits/hsb.csv` | 6 | fim | 280 |
| 134 | 0,64 | SNGS-150: cobertura do detector nos frames com H_gt | 8 | `outputs/runs/rodada_test/tabelas/T2.csv` | 8 | (2) detector cobertura | 0.6428571428571429 |
| 135 | 0,07 | SNGS-150: cobertura do detector nos frames com pessoas | 8 | `outputs/runs/rodada_test/tabelas/T2.csv` | 8 | (2) detector cobertura frames com pessoas | 0.06870229007633588 |
| 136 | 0,575 | cobertura do detector no WC14 test | 6, 9 | `outputs/runs/rodada_test/tabelas/T3.csv` | 4 | media | 0.5752688172043011 |
| 137 | 186 | imagens do WC14 test | Resumo, 4, 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 2 | media | 186 |
| 138 | 0,913 | IoU_whole mediano, WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 5 | mediana | 0.9131266960388786 |
| 139 | 0,864 | IoU_whole médio, WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 5 | media | 0.8635098695256653 |
| 140 | 0,995 | IoU_part mediano, WC14 test | 6, 9 | `outputs/runs/rodada_test/tabelas/T3.csv` | 6 | mediana | 0.9946079029829488 |
| 141 | 0,380 | RE mediano (m), WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 8 | mediana | 0.37991867462940904 |
| 142 | 1,615 | RE médio (m), WC14 test | 6 | `outputs/runs/rodada_test/tabelas/T3.csv` | 8 | media | 1.615112838440006 |
| 143 | 107 | imagens com H (protocolo KpSFR) | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 2 | imagens | 107 |
| 144 | 0,937 | iou_part médio no protocolo KpSFR, 107 imagens | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 2 | media | 0.9369692023209888 |
| 145 | 0,5155 | iou_whole médio no protocolo KpSFR, 186 imagens com 0 nas sem H | 6, 9 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 7 | media | 0.5155405764999672 |
| 146 | 0,8634 | iou_whole mediano no protocolo KpSFR, 186 imagens com 0 nas sem H | 6, 9 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 7 | mediana | 0.8634408188538885 |
| 147 | 0,8962 | iou_whole médio no protocolo KpSFR, 107 imagens com H | 6, 9 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 3 | media | 0.8961733385887282 |
| 148 | 0,9534 | iou_whole mediano no protocolo KpSFR, 107 imagens com H | 6, 9 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 3 | mediana | 0.953413059768704 |
| 149 | 0,539 | iou_part médio, 186 imagens com 0 nas sem H | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 6 | media | 0.5390091647760527 |
| 150 | 79 | imagens do WC14 test sem H | 6 | `derivado: 186 − 107` | — | — | 79 |
| 151 | 0 | imagem sem H vale 0 na nossa convenção | 6 | `outputs/runs/rodada_test/tabelas/T3b.csv` | 6 | — | (no texto da linha) |
| 152 | 100 | ECC convergiu em 100% dos pares | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 67 | — | (no texto da linha) |
| 153 | 36.701 | pares de frames consecutivos do ECC | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 67 | — | (no texto da linha) |
| 154 | 0,987 | correlação mediana do ECC | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 67 | — | (no texto da linha) |
| 155 | 17.828 | frames na interseção das cinco séries | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 76 | — | (no texto da linha) |
| 156 | 36.750 | frames do GSR test | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 76 | — | (no texto da linha) |
| 157 | 0,13 | tremor_med (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | tremor_med | 0.12705495063616054 |
| 158 | 0,57 | tremor_p90 (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | tremor_p90 | 0.5747011364830146 |
| 159 | 1,71 | deslize_med (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | deslize_med | 1.7122490859544373 |
| 160 | 5,45 | deslize_p90 (px) de Kalman + RTS na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | deslize_p90 | 5.44652216220271 |
| 161 | 0,40 | tremor_med (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | tremor_med | 0.39837273079606117 |
| 162 | 1,43 | tremor_p90 (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | tremor_p90 | 1.4311293022953095 |
| 163 | 1,38 | deslize_med (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | deslize_med | 1.3759090615954128 |
| 164 | 4,33 | deslize_p90 (px) de 6c fluxo na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | deslize_p90 | 4.32759718031505 |
| 165 | 1,29 | tremor_med (px) de detector na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 2 | tremor_med | 1.2880092272994736 |
| 166 | 15,50 | tremor_p90 (px) de detector na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 2 | tremor_p90 | 15.502834899744936 |
| 167 | 1,90 | deslize_med (px) de 6a Bassek na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 3 | deslize_med | 1.89765570974326 |
| 168 | 8,31 | deslize_p90 (px) de 6a Bassek na interseção (T4b) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 3 | deslize_p90 | 8.307192313852513 |
| 169 | 4,17 | deslize p90 (px) do 6c no próprio conjunto | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | deslize_p90 | 4.174295627239621 |
| 170 | 23,51 | deslize p90 (px) do Kalman no próprio conjunto | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 5 | deslize_p90 | 23.513633413460205 |
| 171 | 72,61 | deslize p90 (px) do 6a Bassek no próprio conjunto | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 3 | deslize_p90 | 72.60673345089245 |
| 172 | 4,25 | deslize mediano (px) do 6c sem fluxo | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 7 | deslize_med | 4.250941912282512 |
| 173 | 0,8 | jogadores invertidos do 6c na interseção (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 6 | jogadores × 100 | 0.008411584582703042 |
| 174 | 4,4 | jogadores invertidos do Kalman na interseção (%) | 6, 9 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 5 | jogadores × 100 | 0.043892732929131484 |
| 175 | 5,0 | jogadores invertidos do detector na interseção (%) | 6 | `outputs/runs/rodada_test/tabelas/T4b.csv` | 2 | jogadores × 100 | 0.0499068324247626 |
| 176 | 53,5 | jogadores invertidos do detector, penalizada (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 2 | jogadores_penalizada × 100 | 0.5347640828260538 |
| 177 | 11,8 | jogadores invertidos do 6c, penalizada (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | jogadores_penalizada × 100 | 0.1184785773854684 |
| 178 | 5,6 | jogadores invertidos do detector, só cobertos (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 2 | jogadores_só cobertos × 100 | 0.05558504435383341 |
| 179 | 2,1 | jogadores invertidos do 6c, só cobertos (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | jogadores_só cobertos × 100 | 0.020613020580008055 |
| 180 | 0,1 | frames com 0 visíveis do 6c, só cobertos (%) | 6 | `outputs/runs/rodada_test/tabelas/T4.csv` | 6 | zero_visiveis_só cobertos × 100 | 0.0008182790961163215 |
| 181 | 3 | 0 visíveis no feed de scouting de Bassek et al. (%) | 2, 6 | `docs/00-problema.md` | 92 | — | (no texto da linha) |
| 182 | 1 | 1 jogador visível no feed de scouting de Bassek et al. (%) | 2 | `docs/00-problema.md` | 91 | — | (no texto da linha) |
| 183 | 958 | âncoras candidatas | 6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 2 | n | 958 |
| 184 | 28,3 | candidatas erradas, entre as com gabarito (%) | 6, 9 | `derivado: 270 / 955` | — | — | 28.2723 |
| 185 | 558 | âncoras aceitas | 6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | n | 558 |
| 186 | 2,2 | aceitas erradas, entre as com gabarito (%) = 12 / 557 | 6, 9 | `derivado: 12 / 557` | — | — | 2.1544 |
| 187 | 12 | âncoras aceitas erradas | 6, 7 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | erradas | 12 |
| 188 | 5 | clipes sem âncora aceita | 6, 7 | `outputs/runs/rodada_test/tabelas/T7.csv` | 5 | n | 5 |
| 189 | 0,05 | limiar de âncora/H errada (NPE > 0,05) | 4, 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 92 | — | (no texto da linha) |
| 190 | 1.665 | frames na lacuna 1-3 | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | frames | 1665 |
| 191 | 0,0974 | NPE mediano, 6a Bassek, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6a Bassek NPE | 0.09738772017678735 |
| 192 | 0,0324 | NPE mediano, 6a robusto, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6a robusto NPE | 0.03239201394670842 |
| 193 | 0,0095 | NPE mediano, 6c fluxo, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6c fluxo NPE | 0.00951444925996717 |
| 194 | 0,0115 | NPE mediano, 6c sem linhas, lacuna 1-3 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | 6c sem linhas NPE | 0.011450080998323666 |
| 195 | 4.624 | frames na lacuna 4-25 | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | frames | 4624 |
| 196 | 0,8994 | NPE mediano, 6a Bassek, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6a Bassek NPE | 0.899380036414921 |
| 197 | 0,7960 | NPE mediano, 6a robusto, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6a robusto NPE | 0.7960247823207365 |
| 198 | 0,0168 | NPE mediano, 6c fluxo, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6c fluxo NPE | 0.01679906796130583 |
| 199 | 0,0247 | NPE mediano, 6c sem linhas, lacuna 4-25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | 6c sem linhas NPE | 0.024700604200718 |
| 200 | 8.391 | frames na lacuna > 25 | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 4 | frames | 8391 |
| 201 | 0,0551 | NPE mediano, 6c fluxo, lacuna > 25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 4 | 6c fluxo NPE | 0.055100629444049976 |
| 202 | 0,0785 | NPE mediano, 6c sem linhas, lacuna > 25 | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 4 | 6c sem linhas NPE | 0.07853632934367849 |
| 203 | 3.088 | frames na lacuna pontas | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 5 | frames | 3088 |
| 204 | 0,1221 | NPE mediano, 6c fluxo, lacuna pontas | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 5 | 6c fluxo NPE | 0.12207070026322503 |
| 205 | 0,1355 | NPE mediano, 6c sem linhas, lacuna pontas | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 5 | 6c sem linhas NPE | 0.1355059881198888 |
| 206 | 1 | limite das faixas de lacuna (1-3) | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | — | (no texto da linha) |
| 207 | 3 | limite das faixas de lacuna (1-3) | 6 | `outputs/runs/rodada_test/tabelas/T8.csv` | 2 | — | (no texto da linha) |
| 208 | 4 | limite das faixas de lacuna (4-25) | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | — | (no texto da linha) |
| 209 | 25 | limite das faixas de lacuna (4-25, > 25) | 6, 7 | `outputs/runs/rodada_test/tabelas/T8.csv` | 3 | — | (no texto da linha) |
| 210 | 99 | lacunas de 4-25 com as duas bordas certas | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 2 | lacunas | 99 |
| 211 | 106 | lacunas de 4-25 com uma borda errada | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 3 | lacunas | 106 |
| 212 | 331 | lacunas de 4-25 com as duas bordas erradas | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 4 | lacunas | 331 |
| 213 | 1 | lacuna de 4-25 com borda sem gabarito | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 5 | lacunas | 1 |
| 214 | 537 | lacunas de 4-25 frames no test | 7 | `derivado: 99 + 106 + 331 + 1` | — | — | 537 |
| 215 | 62 | lacunas de 4-25 com as duas bordas erradas (%) | 6 | `derivado: 331 / 537` | — | — | 61.6387 |
| 216 | 0,0242 | NPE mediano do 6a Bassek com as duas bordas certas | 6 | `outputs/runs/rodada_test/falhas/lacunas_4a25_resumo.csv` | 2 | bassek_npe_med | 0.024242664392004017 |
| 217 | 8,58 | parede da série do detector (h) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | parede_h | 8.575277777777778 |
| 218 | 15 | processos da série do detector | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | processos | 15 |
| 219 | 1,19 | vazão da série (frames/s) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | frames_por_s | 1.1904376275468886 |
| 220 | 630 | s de parede por clipe com 15 processos, série (máquina inteira) | 6, 9 | `outputs/runs/rodada_test/tabelas/T9.csv` | 2 | s_por_clipe_parede | 630.0204081632653 |
| 221 | 126 | s de parede por clipe com 10 processos, 6c com as ablações | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 3 | s_por_clipe_parede | 125.59183673469387 |
| 222 | 756 | s de parede por clipe: série + 6c | 9 | `derivado: 630 + 126 (T9, s_por_clipe_parede)` | — | — | 755.612 |
| 223 | 10 | o --all do zero só no test passa disto (h): 49 clipes × 756 s = 10,3 h | 9 | `derivado: 49 × (série + 6c) / 3600 > 10` | — | — | 10 |
| 224 | 30 | o --all do zero nas três partições passa disto (h): 164 clipes × 756 s = 34,4 h | 9 | `derivado: (57 + 58 + 49) × (série + 6c) / 3600 > 30` | — | — | 30 |
| 225 | 1,71 | parede do 6c (h) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 3 | parede_h | 1.7094444444444445 |
| 226 | 10 | processos do 6c | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 3 | processos | 10 |
| 227 | 292 | AuxFlow, s por clipe (tabela 6) | 6, 9 | `outputs/runs/rodada_test/tabelas/T9.csv` | 8 | s_por_clipe | 292 |
| 228 | 2,6 | AuxFlow, FPS (tabela 6) | 6 | `outputs/runs/rodada_test/tabelas/T9.csv` | 8 | fps | 2.6 |
| 229 | 4,76 | detector, s por frame num núcleo, GSR | 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 106 | — | (no texto da linha) |
| 230 | 3.570 | detector, s por clipe de 750 frames num núcleo (perfil) | 9 | `docs/03-plano.md` | 580 | — | (no texto da linha) |
| 231 | 2,90 | detector, s por frame num núcleo, WC14 | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 106 | — | (no texto da linha) |
| 232 | 127 | 6c fluxo, ms por frame | 6, 9 | `outputs/runs/rodada_test/tabelas_v2.out` | 106 | — | (no texto da linha) |
| 233 | 750 | frames por clipe | 4, 6 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 234 | 7 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 235 | 8 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 236 | 16 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 237 | 5060 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 238 | 4090 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `outputs/runs/rodada_test/tabelas_v2.out` | 107 | — | (no texto da linha) |
| 239 | 0,252 | LocSim@5 penalizado do 6c, SNGS-149 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 35 | c6 | 0.25245385124828923 |
| 240 | 0,458 | LocSim@5 penalizado do 6c, SNGS-119 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 5 | c6 | 0.45772018093220884 |
| 241 | 0,495 | LocSim@5 penalizado do 6c, SNGS-143 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 29 | c6 | 0.4952325656550445 |
| 242 | 0,495 | LocSim@5 penalizado do teto, SNGS-143 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 29 | teto | 0.49477118746227106 |
| 243 | 0,506 | LocSim@5 penalizado do 6c, SNGS-144 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 30 | c6 | 0.5055174044700732 |
| 244 | 0,508 | LocSim@5 penalizado do teto, SNGS-144 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 30 | teto | 0.5077625470280754 |
| 245 | 0,587 | LocSim@5 penalizado do 6c, SNGS-148 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 34 | c6 | 0.5873981000471749 |
| 246 | 0,635 | LocSim@5 penalizado do 6c, SNGS-126 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 12 | c6 | 0.634512353785477 |
| 247 | 0,954 | LocSim@5 penalizado do teto, SNGS-126 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 12 | teto | 0.9541771572553578 |
| 248 | 6 | piores clipes inspecionados | 7 | `docs/03-plano.md` | 669 | — | (no texto da linha) |
| 249 | 12 | âncoras erradas inspecionadas | 7 | `docs/03-plano.md` | 669 | — | (no texto da linha) |
| 250 | 5 | clipes sem âncora inspecionados | 7 | `docs/03-plano.md` | 636 | — | (no texto da linha) |
| 251 | 3 | lacunas de exemplo inspecionadas | 7 | `docs/03-plano.md` | 636 | — | (no texto da linha) |
| 252 | 1,355 | NPE da âncora SNGS-126 f588 | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 3 | npe | 1.3550949476054246 |
| 253 | 0,060 | menor NPE das âncoras de encaixe parcial (SNGS-122 f657) | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 2 | npe | 0.0596927737995924 |
| 254 | 0,235 | maior NPE das âncoras de encaixe parcial (SNGS-190 f525) | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 12 | npe | 0.23549481829491842 |
| 255 | 0,063 | NPE da âncora SNGS-132 f721 | 7 | `outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv` | 4 | npe | 0.0633359702238581 |
| 256 | 10 | âncoras de encaixe parcial: as aceitas erradas menos a troca de reta (SNGS-126 f588) e a quase certa (SNGS-132 f721) | 7 | `derivado: linhas de outputs/runs/rodada_test/falhas/ancoras_erradas_test.csv sem SNGS-126 e SNGS-132` | — | — | 10 |
| 257 | 13 | clipes sem âncora da valid no jogo 3 | 7, 8 | `docs/decisoes.md` | 370 | — | (no texto da linha) |
| 258 | 18 | clipes sem âncora da valid | 6, 7, 8 | `docs/decisoes.md` | 374 | — | (no texto da linha) |
| 259 | 1 | diagnóstico da segmentação em 1 frame a cada 75 | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 61 | — | (no texto da linha) |
| 260 | 75 | diagnóstico da segmentação em 1 frame a cada 75 | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 61 | — | (no texto da linha) |
| 261 | 0,988 | menor fração do campo como grama nos sem âncora (SNGS-138) | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 5 | campo_grama | 0.9881636617093701 |
| 262 | 0,81 | cobertura das marcações a 2 px, SNGS-127 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 2 | cobertura_2px | 0.8090467516697024 |
| 263 | 0,85 | cobertura das marcações a 2 px, SNGS-128 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 3 | cobertura_2px | 0.8461538461538461 |
| 264 | 0,98 | cobertura das marcações a 2 px, SNGS-138 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 5 | cobertura_2px | 0.9770642201834863 |
| 265 | 0,89 | cobertura das marcações a 2 px, clipes com âncora do jogo 7 | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 7 | cobertura_2px | 0.8863636363636364 |
| 266 | 0,79 | cobertura das marcações a 2 px, referência da Fatia 3 (GSR train) | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 71 | — | (no texto da linha) |
| 267 | 2 | cobertura das marcações a 2 px | 7 | `outputs/runs/rodada_test/analise_falhas.out` | 71 | — | (no texto da linha) |
| 268 | 52 | SNGS-147: pontos anotados acima do limiar (%) | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 6 | acima_limiar × 100 | 0.5192307692307692 |
| 269 | 68 | clipes com âncora do jogo 8: pontos acima do limiar (%) | 7 | `outputs/runs/rodada_test/falhas/sem_ancora_x_fatia3.csv` | 8 | acima_limiar × 100 | 0.6809593023255813 |
| 270 | 11 | candidatas verificáveis do SNGS-147 | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 33 | verificaveis | 11 |
| 271 | 0,7 | menor cobertura do detector nos sem âncora (SNGS-138, %) | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 24 | cob_det × 100 | 0.007194244604316547 |
| 272 | 15,9 | maior cobertura do detector nos sem âncora (SNGS-147, %) | 7 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 33 | cob_det × 100 | 0.15930388219544847 |
| 273 | 0,0059 | NPE mediano do 6c a <= 25 frames da âncora, frames com H do detector | 7 | `outputs/runs/rodada_test/falhas/deriva_6c.csv` | 2 | npe_med | 0.005897785590997996 |
| 274 | 0,0101 | NPE mediano do 6c a <= 25 frames da âncora, pontas | 7 | `outputs/runs/rodada_test/falhas/deriva_6c.csv` | 14 | npe_med | 0.010138998451541235 |
| 275 | 0,208 | NPE mediano do 6c nas pontas a > 250 frames da âncora | 7, 8 | `outputs/runs/rodada_test/falhas/deriva_6c.csv` | 17 | npe_med | 0.207852393306958 |
| 276 | 250 | faixa de distância à âncora (> 250 frames) | 7, 8 | `outputs/runs/rodada_test/analise_falhas.out` | 45 | — | (no texto da linha) |
| 277 | 7,1 | NPE do 6a Bassek no meio da lacuna da Figura 7 (SNGS-121, f14) | 7 | `outputs/runs/rodada_test/falhas/lacunas_4a25_test.csv` | 521 | npe | 7.107828310199786 |
| 278 | 2 | lacuna da Figura 7 (2-26) | 7 | `outputs/runs/rodada_test/falhas/lacunas_figuras.csv` | 4 | — | (no texto da linha) |
| 279 | 26 | lacuna da Figura 7 (2-26) | 7 | `outputs/runs/rodada_test/falhas/lacunas_figuras.csv` | 4 | — | (no texto da linha) |
| 280 | 25 | passos da sensibilidade (±25%) | 8 | `docs/03-plano.md` | 445 | — | (no texto da linha) |
| 281 | 50 | passos da sensibilidade (±50%) | 8 | `docs/03-plano.md` | 445 | — | (no texto da linha) |
| 282 | 0,017 | valor de um frame ou imagem nos subconjuntos | 8 | `docs/decisoes.md` | 518 | — | (no texto da linha) |
| 283 | 0,029 | valor de um frame ou imagem nos subconjuntos | 8 | `docs/decisoes.md` | 518 | — | (no texto da linha) |
| 284 | 14 | configurações da confirmação do detector (atual + 13 candidatos) | 8 | `docs/decisoes.md` | 646 | — | (no texto da linha) |
| 285 | 3 | configurações da confirmação do 6c (atual + 2 candidatos) | 8 | `docs/decisoes.md` | 646 | — | (no texto da linha) |
| 286 | 15 | candidatos confirmados (13 do detector + 2 do 6c) | 8 | `derivado: (14 − 1) + (3 − 1)` | — | — | 15 |
| 287 | 0,02 | ganho mínimo para virar candidato | 8 | `docs/decisoes.md` | 538 | — | (no texto da linha) |
| 288 | 30 | limiar de contraste das marcações no GSR, atual | 3, 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 289 | 15 | limiar candidato (recusado) | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 290 | +0,034 | Δ LocSim do line_thr 15 | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 291 | +0,003 | IC inferior do Δ do line_thr 15 | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 292 | +0,065 | IC superior do Δ do line_thr 15 | 8 | `docs/decisoes.md` | 652 | — | (no texto da linha) |
| 293 | +0,127 | Δ LocSim do line_thr 15 no jogo 4 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 294 | −0,046 | Δ LocSim do line_thr 15 no jogo 9 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 295 | 0,0056 | NPE mediano do jogo 9, limiar 30 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 296 | 0,0130 | NPE mediano do jogo 9, limiar 15 | 8 | `docs/decisoes.md` | 751 | — | (no texto da linha) |
| 297 | 52 | fração do campo coberta pelo gramado no jogo 3 da valid (%) | 8 | `docs/decisoes.md` | 114 | — | (no texto da linha) |
| 298 | 2,33 | frames do test sem H_gt na geração do gabarito (Fatia 2, %) | 8 | `docs/decisoes.md` | 63 | — | (no texto da linha) |
| 299 | 3 | homografia 3 × 3 | 1 | `docs/00-problema.md` | 8 | — | (no texto da linha) |
| 300 | 2 | 2 + 2 retas de duas famílias | Resumo, 3, 7, 8 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 301 | 0,5 | BroadTrack reinicia com IoU < 0,5 | 2 | `docs/01-metodo.md` | 286 | — | (no texto da linha) |
| 302 | 0,8397 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 315 | — | (no texto da linha) |
| 303 | 0,8352 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 315 | — | (no texto da linha) |
| 304 | 0,9224 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 316 | — | (no texto da linha) |
| 305 | 0,9426 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 316 | — | (no texto da linha) |
| 306 | 1,34 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 316 | — | (no texto da linha) |
| 307 | 0,84 | BroadTrack × AuxFlow no GSR (01-metodo) | 2 | `docs/01-metodo.md` | 317 | — | (no texto da linha) |
| 308 | 2,5 | grade de pontos auxiliares 2,5 × 2 m | 2, 3, 5 | `docs/01-metodo.md` | 252 | — | (no texto da linha) |
| 309 | 2 | grade de pontos auxiliares 2,5 × 2 m | 2, 3, 5 | `docs/01-metodo.md` | 252 | — | (no texto da linha) |
| 310 | 1 | erro de ida e volta <= 1 px | 2, 3 | `docs/01-metodo.md` | 257 | — | (no texto da linha) |
| 311 | 23,42 | AuxFlow sem fluxo no HSB | 2 | `docs/00-problema.md` | 40 | — | (no texto da linha) |
| 312 | 78,30 | AuxFlow sem pontos-chave do detector no HSB | 2 | `docs/01-metodo.md` | 259 | — | (no texto da linha) |
| 313 | 78,71 | RAFT no lugar do Lucas–Kanade | 2 | `docs/00-problema.md` | 42 | — | (no texto da linha) |
| 314 | 39,68 | amostragem geométrica no AuxFlow | 2 | `docs/01-metodo.md` | 254 | — | (no texto da linha) |
| 315 | 83,39 | amostragem aleatória no AuxFlow | 2 | `docs/01-metodo.md` | 255 | — | (no texto da linha) |
| 316 | 150 | âncoras ingênuas a cada 150 frames | 2, 3 | `docs/01-metodo.md` | 266 | — | (no texto da linha) |
| 317 | 82,48 | âncoras ingênuas no AuxFlow | 2 | `docs/01-metodo.md` | 267 | — | (no texto da linha) |
| 318 | 83,48 | detector sem propagação no AuxFlow | 2 | `docs/01-metodo.md` | 267 | — | (no texto da linha) |
| 319 | 90,65 | âncoras por heurística no AuxFlow | 2 | `docs/01-metodo.md` | 268 | — | (no texto da linha) |
| 320 | 91,88 | âncora de gabarito no AuxFlow | 2 | `docs/01-metodo.md` | 268 | — | (no texto da linha) |
| 321 | 54,74 | AuxFlow com a H inicial perturbada | 2 | `docs/00-problema.md` | 48 | — | (no texto da linha) |
| 322 | 31 | janela do Savitzky–Golay (Bassek et al.) | 2, 3 | `docs/00-problema.md` | 59 | — | (no texto da linha) |
| 323 | 3 | grau do Savitzky–Golay (Bassek et al.) | 2, 3 | `config.yaml` | 225 | — | (no texto da linha) |
| 324 | 25 | lacunas preenchidas por interpolação (Bassek et al.) | 2, 3 | `docs/01-metodo.md` | 212 | — | (no texto da linha) |
| 325 | 981 | cortes por partida (Bassek et al.) | 2 | `docs/01-metodo.md` | 277 | — | (no texto da linha) |
| 326 | 10,9 | cortes por minuto (Bassek et al.) | 2 | `docs/01-metodo.md` | 277 | — | (no texto da linha) |
| 327 | 115 | molde do PnLCalib no WC14 (115 × 74 jardas) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 328 | 74 | molde do PnLCalib no WC14 (115 × 74 jardas) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 329 | 100 | molde do KpSFR e de Maglo et al. (100 × 60 m) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 330 | 60 | molde do KpSFR e de Maglo et al. (100 × 60 m) | 2 | `docs/01-metodo.md` | 32 | — | (no texto da linha) |
| 331 | 105 | modelo do campo 105 × 68 m | 3 | `docs/01-metodo.md` | 19 | — | (no texto da linha) |
| 332 | 68 | modelo do campo 105 × 68 m | 3 | `docs/01-metodo.md` | 19 | — | (no texto da linha) |
| 333 | 20 | faixa de matiz do gramado (±20°) | 3 | `docs/decisoes.md` | 73 | — | (no texto da linha) |
| 334 | 0,9861 | IoU médio do gramado no WC14 train_val | 3 | `docs/decisoes.md` | 75 | — | (no texto da linha) |
| 335 | 15 | limiar das marcações no WC14 | 3 | `docs/decisoes.md` | 74 | — | (no texto da linha) |
| 336 | 30 | limiar das marcações no GSR | 3 | `docs/decisoes.md` | 74 | — | (no texto da linha) |
| 337 | 180 | simetria de 180° do campo | 3, 7 | `docs/03-plano.md` | 310 | — | (no texto da linha) |
| 338 | 0,45 | portão: fração explicada | 3 | `config.yaml` | 201 | — | (no texto da linha) |
| 339 | 0,85 | portão: IoU com o gramado | 3 | `config.yaml` | 202 | — | (no texto da linha) |
| 340 | 5 | portões logo abaixo do percentil 5 da H_gt | 3 | `config.yaml` | 202 | — | (no texto da linha) |
| 341 | 12 | janela das âncoras candidatas (±12 frames) | 3 | `config.yaml` | 246 | — | (no texto da linha) |
| 342 | 2 | vizinhos mínimos da verificação | 3 | `config.yaml` | 249 | — | (no texto da linha) |
| 343 | 209 | imagens de treino do WC14 | 4 | `docs/02-dados.md` | 35 | — | (no texto da linha) |
| 344 | 1280 | resolução do WC14 | 4 | `docs/02-dados.md` | 36 | — | (no texto da linha) |
| 345 | 720 | resolução do WC14 | 4 | `docs/02-dados.md` | 36 | — | (no texto da linha) |
| 346 | 25 | fps do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 347 | 1920 | resolução do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 348 | 1080 | resolução do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 349 | 57 | clipes de treino do GSR | 4 | `docs/02-dados.md` | 74 | — | (no texto da linha) |
| 350 | 58 | clipes de validação do GSR | 4 | `docs/02-dados.md` | 75 | — | (no texto da linha) |
| 351 | 0,8852 | BHITK no GSR, tabela 7 do AuxFlow (conferido por Victor) | 2 | `docs/decisoes.md` | 877 | — | (no texto da linha) |
| 352 | 0,8851 | NBJW no GSR, tabela 7 do AuxFlow (conferido por Victor) | 2 | `docs/decisoes.md` | 877 | — | (no texto da linha) |
| 353 | 3 | RANSAC a 3 px da H_gt_auxflow | 4 | `docs/01-metodo.md` | 334 | — | (no texto da linha) |
| 354 | 10 | clipes do HSB | 4 | `docs/02-dados.md` | 91 | — | (no texto da linha) |
| 355 | 0 | numeração dos frames a partir de 0 | 4 | `docs/02-dados.md` | 112 | — | (no texto da linha) |
| 356 | 90 | intervalo "90–0" do SNGS-128 | 4 | `docs/02-dados.md` | 107 | — | (no texto da linha) |
| 357 | 0 | intervalo "90–0" do SNGS-128 | 4 | `docs/02-dados.md` | 107 | — | (no texto da linha) |
| 358 | 0,05 | LocSim: exp(ln(0,05)·d²/τ²) | 5 | `docs/01-metodo.md` | 369 | — | (no texto da linha) |
| 359 | 5 | τ = 5 m | 5 | `docs/01-metodo.md` | 372 | — | (no texto da linha) |
| 360 | 1 | mAP-LocSim: τ = 1 a 10 m | 5 | `docs/01-metodo.md` | 373 | — | (no texto da linha) |
| 361 | 10 | mAP-LocSim: τ = 1 a 10 m | 5 | `docs/01-metodo.md` | 373 | — | (no texto da linha) |
| 362 | 0 | pessoa de frame sem H vale 0 | 5 | `docs/01-metodo.md` | 379 | — | (no texto da linha) |
| 363 | 95 | intervalo de 95% | 5, 6 | `docs/03-plano.md` | 560 | — | (no texto da linha) |
| 364 | 2.000 | reamostragens do bootstrap | 5 | `docs/03-plano.md` | 560 | — | (no texto da linha) |
| 365 | 1.470 | frames da conferência de determinismo | 5, B | `docs/03-plano.md` | 683 | — | (no texto da linha) |
| 366 | 25 | frames da conferência: 1 a cada 25 | 5, B | `docs/03-plano.md` | 684 | — | (no texto da linha) |
| 367 | 735 | tarefas da série com a chave congelada | 5, B | `docs/03-plano.md` | 677 | — | (no texto da linha) |
| 368 | 47 | caches da valid gravados com a chave errada | 5 | `docs/decisoes.md` | 487 | — | (no texto da linha) |
| 369 | 0 | manifestos com 0 falhas | B | `docs/decisoes.md` | 849 | — | (no texto da linha) |
| 370 | 0,9838 | Tabela 1: IoU do gramado, lab_hue (média) (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 371 | 0,9797 | Tabela 1: IoU do gramado, lab_hue (sombra) (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 372 | 0,9822 | Tabela 1: IoU do gramado, HSV (média) (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 373 | 0,9764 | Tabela 1: IoU do gramado, HSV (sombra) (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 374 | 0,9728 | Tabela 1: IoU do gramado, Lab por distância (média) (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 375 | 0,9319 | Tabela 1: IoU do gramado, Lab por distância (sombra) (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 376 | 0,9441 | Tabela 1: ablação do gramado: cru (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 377 | 0,9492 | Tabela 1: ablação: + abertura (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 378 | 0,9548 | Tabela 1: ablação: + fechamento (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 379 | 0,9763 | Tabela 1: ablação: + maior componente (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 380 | 0,579 | Tabela 1: F1 a 3 px, filtro de linha, WC14 (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 381 | 0,560 | Tabela 1: F1 a 3 px, top-hat, WC14 (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 382 | 0,634 | Tabela 1: F1 a 3 px, filtro de linha, GSR (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 383 | 0,577 | Tabela 1: F1 a 3 px, top-hat, GSR (treino) | 3 | `docs/decisoes.md` | 72 | — | (no texto da linha) |
| 384 | 0,641 | Tabela 1: F1 dos segmentos na configuração escolhida, GSR (GSR train) | 3 | `docs/decisoes.md` | 99 | — | (no texto da linha) |
| 385 | 0,597 | Tabela 1: F1 sem o filtro de forma (GSR train) | 3 | `docs/decisoes.md` | 99 | — | (no texto da linha) |
| 386 | 1,17 | Tabela 1: fragmentação com a fusão (GSR train) | 3 | `docs/decisoes.md` | 99 | — | (no texto da linha) |
| 387 | 4,70 | Tabela 1: fragmentação sem a fusão (GSR train) | 3 | `docs/decisoes.md` | 99 | — | (no texto da linha) |
| 388 | 0,634 | Tabela 1: F1 sem a fusão (GSR train) | 3 | `docs/decisoes.md` | 99 | — | (no texto da linha) |
| 389 | 0,9928 | LocSim@5 do gabarito do AuxFlow (tabela 2 deles) | 4, 6 | `docs/decisoes.md` | 56 | — | (no texto da linha) |
| 390 | 0,933 | LocSim@5 da H_gt pelas linhas como predição, train (antes da rodada) | 4 | `outputs/metrics_gt_train.csv` | 16 | media | 0.9332444747326908 |
| 391 | 0,930 | LocSim@5 da propagação no conjunto comum, nos frames que ela cobre | 6 | `outputs/runs/rodada_test/tabelas/T5.csv` | 6 | comum | 0.9302394650733893 |
| 392 | 1,000 | B4, teto do sistema: cobertura | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | cobertura | 1.0 |
| 393 | 0,0058 | B4, teto do sistema: NPE mediano | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | npe_med | 0.005792020346120532 |
| 394 | 0,922 | B4, teto do sistema: LocSim@5 penalizado | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_pen | 0.92204315807928 |
| 395 | 0,922 | B4, teto do sistema: LocSim@5 nos cobertos | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_cob | 0.92204315807928 |
| 396 | 0,899 | B4, teto do sistema: LocSim@5 pen., mín. entre os jogos (jogo 8) | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_pen_min | 0.8989835004477721 |
| 397 | 0,949 | B4, teto do sistema: LocSim@5 pen., máx. entre os jogos (jogo 11) | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_pen_max | 0.9486980128017087 |
| 398 | 0,919 | B4, teto do sistema: LocSim@5 pen., jogo 7 | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_pen_jogo7 | 0.9188654375913603 |
| 399 | 0,899 | B4, teto do sistema: LocSim@5 pen., jogo 8 | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_pen_jogo8 | 0.8989835004477721 |
| 400 | 0,949 | B4, teto do sistema: LocSim@5 pen., jogo 11 | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | locsim_pen_jogo11 | 0.9486980128017087 |
| 401 | 0,733 | B4, teto do sistema: acurácia a 5 px, penalizada | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | acc5_pen | 0.7332502174318501 |
| 402 | 0,733 | B4, teto do sistema: acurácia a 5 px, nos cobertos | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 11 | acc5_cob | 0.7332502174318501 |
| 403 | 0,934 | B4, teto do sistema no conjunto comum: LocSim@5 pen. | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 23 | locsim_pen | 0.9339418502696739 |
| 404 | 0,794 | B4, teto do sistema no conjunto comum: acurácia a 5 px | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 23 | acc5_pen | 0.7937354952810199 |
| 405 | 0,054 | B4, fração ao teto do sistema: 6a Bassek | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 3 | fracao_teto_sistema | 0.05367847761779819 |
| 406 | 0,117 | B4, fração ao teto do sistema: 6a robusto | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 4 | fracao_teto_sistema | 0.11688248477023223 |
| 407 | 0,142 | B4, fração ao teto do sistema: Kalman + RTS | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 5 | fracao_teto_sistema | 0.14151045099592402 |
| 408 | 0,656 | B4, fração ao teto do sistema: 6c fluxo | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 6 | fracao_teto_sistema | 0.6558496227128815 |
| 409 | 0,588 | B4, fração ao teto do sistema: 6c sem linhas | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 7 | fracao_teto_sistema | 0.588498105522114 |
| 410 | −0,106 | B4, fração ao teto do sistema: 6c sem fluxo | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 8 | fracao_teto_sistema | -0.10597767466880698 |
| 411 | 0,303 | B4, fração ao teto do sistema: 6c âncora ingênua /150 | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 9 | fracao_teto_sistema | 0.3025092760771207 |
| 412 | 0,684 | B4, fração ao teto do sistema: 6c âncora de gabarito | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B4_fracao.csv` | 10 | fracao_teto_sistema | 0.6838727673232315 |
| 413 | 0,946 | B1, H_gt pelas linhas como predição: LocSim@5 nos frames com gabarito (test) | Resumo, 4, 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 12 | locsim_cob | 0.9464115216354456 |
| 414 | 0,978 | B1, H_gt_auxflow como predição: LocSim@5 nos frames com ela (test) | 4, 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 13 | locsim_cob | 0.9778654624887865 |
| 415 | 0,387 | B3, acurácia a 5 px penalizada, test inteiro: detector | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 2 | acc5_pen | 0.3870120116100024 |
| 416 | 0,784 | B3, acurácia a 5 px nos cobertos, test inteiro: detector | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 2 | acc5_cob | 0.7843540190077531 |
| 417 | 0,784 | B3, acurácia a 5 px penalizada, conjunto comum: detector | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 14 | acc5_pen | 0.7843540190077531 |
| 418 | 0,398 | B3, acurácia a 5 px penalizada, test inteiro: 6a Bassek | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 3 | acc5_pen | 0.3984779370217103 |
| 419 | 0,599 | B3, acurácia a 5 px nos cobertos, test inteiro: 6a Bassek | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 3 | acc5_cob | 0.5994786386747935 |
| 420 | 0,735 | B3, acurácia a 5 px penalizada, conjunto comum: 6a Bassek | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 15 | acc5_pen | 0.7345968707726277 |
| 421 | 0,430 | B3, acurácia a 5 px penalizada, test inteiro: 6a robusto | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 4 | acc5_pen | 0.43036299703119063 |
| 422 | 0,662 | B3, acurácia a 5 px nos cobertos, test inteiro: 6a robusto | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 4 | acc5_cob | 0.662443566110838 |
| 423 | 0,779 | B3, acurácia a 5 px penalizada, conjunto comum: 6a robusto | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 16 | acc5_pen | 0.7792224312359847 |
| 424 | 0,419 | B3, acurácia a 5 px penalizada, test inteiro: Kalman + RTS | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 5 | acc5_pen | 0.41911716249381314 |
| 425 | 0,631 | B3, acurácia a 5 px nos cobertos, test inteiro: Kalman + RTS | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 5 | acc5_cob | 0.6308644571635319 |
| 426 | 0,760 | B3, acurácia a 5 px penalizada, conjunto comum: Kalman + RTS | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 17 | acc5_pen | 0.759651080891726 |
| 427 | 0,551 | B3, acurácia a 5 px penalizada, test inteiro: 6c fluxo | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 6 | acc5_pen | 0.5507461043869207 |
| 428 | 0,613 | B3, acurácia a 5 px nos cobertos, test inteiro: 6c fluxo | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 6 | acc5_cob | 0.6133308889763437 |
| 429 | 0,807 | B3, acurácia a 5 px penalizada, conjunto comum: 6c fluxo | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 18 | acc5_pen | 0.8071876639570899 |
| 430 | 0,508 | B3, acurácia a 5 px penalizada, test inteiro: 6c sem linhas | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 7 | acc5_pen | 0.5079574314574316 |
| 431 | 0,566 | B3, acurácia a 5 px nos cobertos, test inteiro: 6c sem linhas | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 7 | acc5_cob | 0.5656798668503213 |
| 432 | 0,787 | B3, acurácia a 5 px penalizada, conjunto comum: 6c sem linhas | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 19 | acc5_pen | 0.7871037227018035 |
| 433 | 0,576 | B3, acurácia a 5 px penalizada, test inteiro: 6c âncora de gabarito | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 10 | acc5_pen | 0.5759762699885149 |
| 434 | 0,641 | B3, acurácia a 5 px nos cobertos, test inteiro: 6c âncora de gabarito | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 10 | acc5_cob | 0.6414281188508462 |
| 435 | 0,829 | B3, acurácia a 5 px penalizada, conjunto comum: 6c âncora de gabarito | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 22 | acc5_pen | 0.8293025961213796 |
| 436 | 0,849 | B3, acurácia a 5 px penalizada, test inteiro: H_gt pelas linhas | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 12 | acc5_pen | 0.8491634773389874 |
| 437 | 0,869 | B3, acurácia a 5 px nos cobertos, test inteiro: H_gt pelas linhas | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 12 | acc5_cob | 0.8694627714311767 |
| 438 | 0,904 | B3, acurácia a 5 px penalizada, conjunto comum: H_gt pelas linhas | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 24 | acc5_pen | 0.9036594446565219 |
| 439 | 0,515 | B3, acurácia a 5 px penalizada, test inteiro: H_gt_auxflow | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 13 | acc5_pen | 0.5149711018861395 |
| 440 | 0,533 | B3, acurácia a 5 px nos cobertos, test inteiro: H_gt_auxflow | 6 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 13 | acc5_cob | 0.5329837781433937 |
| 441 | 0,545 | B3, acurácia a 5 px penalizada, conjunto comum: H_gt_auxflow | 6, 9 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 25 | acc5_pen | 0.5445809936186597 |
| 442 | 11 | B3: redução do erro (1 − acurácia a 5 px) no conjunto comum, detector -> propagação (%) | 6 | `derivado: (acc_c6 − acc_det) / (1 − acc_det)` | — | — | 10.5885 |
| 443 | 20,9 | B2, HSB, 6a Bassek: pen_media | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 42 | pen_media × 100 | 0.20927468016171605 |
| 444 | 0,0 | B2, HSB, 6a Bassek: pen_mediana | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 42 | pen_mediana × 100 | 0.0 |
| 445 | 0,396 | B2, HSB, 6a Bassek: cob_fr | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 42 | cob_fr | 0.39553571428571427 |
| 446 | 52,9 | B2, HSB, 6a Bassek: cob_media | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 42 | cob_media × 100 | 0.5290917421695756 |
| 447 | 24,5 | B2, HSB, 6a robusto: pen_media | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 43 | pen_media × 100 | 0.24468732504909463 |
| 448 | 0,0 | B2, HSB, 6a robusto: pen_mediana | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 43 | pen_mediana × 100 | 0.0 |
| 449 | 0,371 | B2, HSB, 6a robusto: cob_fr | 6 | `outputs/runs/rodada_test/pos_rodada/B2.csv` | 43 | cob_fr | 0.37142857142857144 |
| 450 | 5 | B5, protocolo: ruído σ = 5 | 6, B | `docs/decisoes.md` | 904 | — | (no texto da linha) |
| 451 | 10 | B5, protocolo: ruído σ = 10 | 6, B | `docs/decisoes.md` | 904 | — | (no texto da linha) |
| 452 | 20 | B5, protocolo: ruído σ = 20 | 6, B | `docs/decisoes.md` | 904 | — | (no texto da linha) |
| 453 | 11 | B5, protocolo: núcleo do borrão de 11 px | 6, B | `docs/decisoes.md` | 905 | — | (no texto da linha) |
| 454 | 21 | B5, protocolo: núcleo do borrão de 21 px | 6, B | `docs/decisoes.md` | 905 | — | (no texto da linha) |
| 455 | 0,7 | B5, protocolo: sombra: L* × 0,7 | 6, B | `docs/decisoes.md` | 906 | — | (no texto da linha) |
| 456 | 0,5 | B5, protocolo: sombra: L* × 0,5 | 6, B | `docs/decisoes.md` | 906 | — | (no texto da linha) |
| 457 | 0,35 | B5, protocolo: sombra: L* × 0,35 | 6, B | `docs/decisoes.md` | 906 | — | (no texto da linha) |
| 458 | 0,05 | B5, protocolo: sombra: rampa de 0,05·h | 6, B | `docs/decisoes.md` | 906 | — | (no texto da linha) |
| 459 | 0,6 | B5, protocolo: oclusão: elipse de 0,6 m de largura | 6, B | `docs/decisoes.md` | 907 | — | (no texto da linha) |
| 460 | 1,8 | B5, protocolo: oclusão: elipse de 1,8 m de altura | 6, B | `docs/decisoes.md` | 907 | — | (no texto da linha) |
| 461 | 0,8 | B5, protocolo: aceita errada: IoU do campo inteiro < 0,8 | 6, B | `docs/decisoes.md` | 908 | — | (no texto da linha) |
| 462 | 209 | B5, protocolo: imagens do WC14 train_val | 6, B | `docs/decisoes.md` | 902 | — | (no texto da linha) |
| 463 | 0,9861 | B5: IoU do gramado na imagem limpa | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 2 | gramado_iou | 0.9861109669697167 |
| 464 | 0,612 | B5: cobertura das marcações a 2 px, limpa | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 2 | marcas_cob2 | 0.6116499441208049 |
| 465 | 0,517 | B5: cobertura do detector, limpa | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 2 | det_cobertura | 0.5167464114832536 |
| 466 | 0,102 | B5: aceitas erradas, limpa | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 2 | det_aceitas_erradas | 0.10185185185185185 |
| 467 | 0,708 | B5: IoU do gramado, ruído σ = 10 | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 4 | gramado_iou | 0.7081201491899404 |
| 468 | 0,244 | B5: cobertura do detector, ruído σ = 10 | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 4 | det_cobertura | 0.24401913875598086 |
| 469 | 0,004 | B5: IoU do gramado, ruído σ = 20 | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 5 | gramado_iou | 0.004165937081813937 |
| 470 | 0,000 | B5: cobertura do detector, ruído σ = 20 (nenhuma imagem) | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 5 | det_cobertura | 0.0 |
| 471 | 0,543 | B5: cobertura das marcações, borrão de 11 px | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 7 | marcas_cob2 | 0.5432420429051623 |
| 472 | 0,077 | B5: cobertura do detector, borrão de 21 px | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 8 | det_cobertura | 0.07655502392344497 |
| 473 | 0,375 | B5: aceitas erradas, borrão de 21 px | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 8 | det_aceitas_erradas | 0.375 |
| 474 | 0,526 | B5: cobertura das marcações, sombra L* × 0,5 | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 10 | marcas_cob2 | 0.5262829077424046 |
| 475 | 0,969 | B5: IoU do gramado, sombra L* × 0,35 | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 11 | gramado_iou | 0.9692651972516488 |
| 476 | 0,533 | B5: cobertura das marcações, oclusão de 20% | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 14 | marcas_cob2 | 0.5333991581010133 |
| 477 | 0,478 | B5: cobertura do detector, oclusão de 20% | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 14 | det_cobertura | 0.4784688995215311 |
| 478 | 0,889 | B5: menor IoU do campo inteiro mediano entre os níveis com resposta (borrão de 21 px) | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 8 | det_iou_mediano | 0.8894947602438756 |
| 479 | 0,930 | B5: maior IoU do campo inteiro mediano entre os níveis com resposta (ruído σ = 5) | 6 | `outputs/runs/rodada_test/pos_rodada/B5.csv` | 3 | det_iou_mediano | 0.9302916877530989 |
| 480 | 16 | B5: imagens aceitas com o borrão de 21 px (0,077 × 209) | 6 | `derivado: cobertura × 209` | — | — | 16 |
| 481 | 10 | B5: queda de mais de 10% em relação à imagem limpa ("quebra") | 6 | `docs/decisoes.md` | 909 | — | (no texto da linha) |
| 482 | 960 | escala da acurácia contra as linhas (960 × 540) | 5 | `config.yaml` | 62 | — | (no texto da linha) |
| 483 | 540 | escala da acurácia contra as linhas (960 × 540) | 5 | `config.yaml` | 62 | — | (no texto da linha) |
| 484 | 20 | limiares da acurácia (5, 10, 20 px) | 5, 6 | `config.yaml` | 63 | — | (no texto da linha) |
