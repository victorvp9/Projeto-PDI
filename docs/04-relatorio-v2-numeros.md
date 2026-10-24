# Números do adendo v2 e a origem de cada um

Gerado por `scripts/relatorio/numeros_v2.py`, que confere cada linha: o valor da origem, arredondado às casas do texto, tem que ser o número do texto. Nas origens em CSV, a linha conta o cabeçalho como linha 1 (booleanos: True = 1, False = 0); nas origens em texto, a linha é a do arquivo; nas em JSON, a coluna diz o caminho das chaves; as contas (derivados) dizem a expressão. A completude também é conferida: todo número do corpo do adendo, fora das tabelas geradas e dos blocos de código, tem uma linha aqui.

As tabelas do adendo são geradas pelo mesmo script: a T1, T1b, T2, T5, T6, T7 e T8 de `outputs/runs/rodada_test/tabelas/` (v1) e de `outputs/runs_v2/rodada_test_v2/tabelas/` (v2), `clipes_test_v2.csv`, `pioras.csv` e os `decisao.json` de `outputs/runs_v2/<hipótese>/`; o script confere que as tabelas no adendo são as geradas.

| nº | número no texto | o que é | seção | origem | linha | coluna | valor na origem |
|---|---|---|---|---|---|---|---|
| 1 | 5 | clipes do test sem âncora aceita, v1 | 1, 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 5 | n | 5 |
| 2 | 0 | clipes do test sem âncora aceita, v2 | 1, 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 5 | n | 0 |
| 3 | 0,902 | LocSim@5 penalizado da propagação, v2 | 1, 3, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 6 | locsim_pen | 0.9021534525340882 |
| 4 | 4 | critério do plano: ganho em >= 4 de 6 jogos | 1, 2 | `docs/decisoes.md` | 939 | — | (no texto da linha) |
| 5 | 6 | critério do plano: 6 jogos de dev | 1, 2 | `docs/decisoes.md` | 939 | — | (no texto da linha) |
| 6 | −0,03 | critério do plano: nenhum jogo abaixo de −0,03 | 1 | `docs/decisoes.md` | 940 | — | (no texto da linha) |
| 7 | 5 | A': jogos com Δ > 0 (critério antigo) | 1 | `outputs/runs_v2/a_central/decisao.json` | — | decisao → jogos_com_ganho | 5 |
| 8 | 6 | A': jogos com Δ >= 0 (critério novo) | 2 | `outputs/runs_v2/a_central/decisao.json` | — | decisao → jogos_sem_perda | 6 |
| 9 | +0,178 | A': média dos Δ por jogo | 1 | `outputs/runs_v2/a_central/decisao.json` | — | decisao → media | 0.17811624575279686 |
| 10 | 0 | A': pior Δ (o jogo 3, Δ = 0) | 1 | `outputs/runs_v2/a_central/decisao.json` | — | decisao → pior | 0.0 |
| 11 | 49 | clipes do GSR test | 1, 3.7 | `derivado: linhas de outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 49 |
| 12 | 1,000 | cobertura da propagação, v2 | 1, 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 6 | cobertura | 1.0 |
| 13 | 6 | dev: 6 jogos | 2 | `docs/05-melhorias-plano.md` | 60 | — | (no texto da linha) |
| 14 | 5 | B1: jogos com Δ > 0 na leitura leave-one-game-out | 2 | `outputs/runs_v2/b1_regra/decisao.json` | — | logo_jogo9 → decisao → jogos_com_ganho | 5 |
| 15 | 1 | C: jogos com Δ > 0 | 2 | `outputs/runs_v2/c_bidirecional/decisao.json` | — | decisao → jogos_com_ganho | 1 |
| 16 | 5 | C: jogos em que piorou (6 − jogos com ganho; nenhum com Δ = 0) | 2 | `derivado: 6 − 1` | — | — | 5 |
| 17 | 3 | B2: jogos com Δ = 0 | 2 | `docs/decisoes.md` | 1106 | — | (no texto da linha) |
| 18 | 3 | A: H novas no jogo 3, todas erradas | 2 | `docs/decisoes.md` | 1119 | — | (no texto da linha) |
| 19 | 20 | A': contagem mínima de H novas por jogo na regra de parada | 2 | `docs/decisoes.md` | 1155 | — | (no texto da linha) |
| 20 | 59 | A': clipes da metade fixa | 2 | `docs/decisoes.md` | 1156 | — | (no texto da linha) |
| 21 | 4 | B1b: clipes que a regra mexe | 2 | `docs/decisoes.md` | 1137 | — | (no texto da linha) |
| 22 | 2 | B1b: jogos que a regra mexe | 2 | `docs/decisoes.md` | 1137 | — | (no texto da linha) |
| 23 | 0,419 | locsim_pen de detector, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | locsim_pen | 0.4192764091198964 |
| 24 | 0,624 | locsim_pen de detector, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 2 | locsim_pen | 0.624146109585618 |
| 25 | 0,505 | cobertura de detector, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | cobertura | 0.5049593224116795 |
| 26 | 0,702 | cobertura de detector, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 2 | cobertura | 0.7023849325755043 |
| 27 | 0,749 | locsim_pen de 6c fluxo, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | locsim_pen | 0.7490157917374893 |
| 28 | 0,897 | cobertura de 6c fluxo, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | cobertura | 0.8971358520004458 |
| 29 | 0,959 | fracao_teto de 6c fluxo, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto | 0.9590228680694096 |
| 30 | 0,959 | fracao_teto de 6c fluxo, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 6 | fracao_teto | 0.9588737408665611 |
| 31 | 0,763 | locsim_pen de 6c âncora de gabarito, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | locsim_pen | 0.7631048970488494 |
| 32 | 0,914 | locsim_pen de 6c âncora de gabarito, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 10 | locsim_pen | 0.9140772351342509 |
| 33 | 1 | conferência contra o v1 a 1 frame em 25 | 3.1, 3.7 | `scripts/v2/rodada_test_v2/confere_v1_test.py` | 3 | — | (no texto da linha) |
| 34 | 25 | conferência contra o v1 a 1 frame em 25 | 3.1, 3.7 | `scripts/v2/rodada_test_v2/confere_v1_test.py` | 3 | — | (no texto da linha) |
| 35 | 722 | H do v1 idênticas bit a bit na série do v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/conferencia_v1.json` | — | iguais_bit_a_bit | 722 |
| 36 | 290 | H novas no v2 (frames sem H no v1) | 3.1 | `outputs/runs_v2/rodada_test_v2/conferencia_v1.json` | — | novas_no_v2 | 290 |
| 37 | 0,676 | LocSim@5 pen. da propagação, jogo 7, v1 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 2 | v1_locsim_pen_6c | 0.6759710080828238 |
| 38 | 0,914 | LocSim@5 pen. da propagação, jogo 7, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 2 | locsim_pen_6c | 0.9135220326519915 |
| 39 | 0,650 | LocSim@5 pen. da propagação, jogo 8, v1 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 3 | v1_locsim_pen_6c | 0.6499967158730243 |
| 40 | 0,839 | LocSim@5 pen. da propagação, jogo 8, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 3 | locsim_pen_6c | 0.838581896876749 |
| 41 | 0,920 | LocSim@5 pen. da propagação, jogo 11, v1 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 4 | v1_locsim_pen_6c | 0.9199799820597924 |
| 42 | 0,956 | LocSim@5 pen. da propagação, jogo 11, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 4 | locsim_pen_6c | 0.9564874784910701 |
| 43 | 0,954 | LocSim@5 pen. do teto condicionado, jogo 11, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 4 | locsim_pen_teto | 0.954306161772318 |
| 44 | 0,946 | H_gt pelas linhas como predição: LocSim@5 nos frames com gabarito (análise posterior do v1) | 3.2 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 12 | locsim_cob | 0.9464115216354456 |
| 45 | 18.133 | frames do conjunto comum, v1 | 3.3 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 2 | frames | 18133 |
| 46 | 25.382 | frames do conjunto comum, v2 | 3.3 | `outputs/runs_v2/rodada_test_v2/tabelas/T1b.csv` | 2 | frames | 25382 |
| 47 | 0,926 | LocSim@5 pen. da propagação no conjunto comum, v2 | 3.3, 3.5 | `outputs/runs_v2/rodada_test_v2/tabelas/T1b.csv` | 6 | locsim_pen | 0.9260317577530113 |
| 48 | 0,882 | LocSim@5 pen. do detector no conjunto comum, v2 | 3.3 | `outputs/runs_v2/rodada_test_v2/tabelas/T1b.csv` | 2 | locsim_pen | 0.8823758985723601 |
| 49 | 61,7 | HSB, (3) pipeline pen média, v1 | 3.4, 4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen média × 100 | 0.617443855691164 |
| 50 | 74,5 | HSB, (3) pipeline pen média, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 14 | (3) pipeline pen média × 100 | 0.7447292972410947 |
| 51 | 71,1 | HSB, (3) pipeline pen mediana, v1 | 3.4, 4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen mediana × 100 | 0.7110783802185268 |
| 52 | 81,9 | HSB, (3) pipeline pen mediana, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 14 | (3) pipeline pen mediana × 100 | 0.8191605056318045 |
| 53 | 0,829 | HSB, (3) pipeline cobertura frames com pessoas, v1 | 3.4, 4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline cobertura frames com pessoas | 0.8285714285714286 |
| 54 | 1,000 | HSB, (3) pipeline cobertura frames com pessoas, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 14 | (3) pipeline cobertura frames com pessoas | 1.0 |
| 55 | 81,4 | HSB, (1) só propagação pen média, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 12 | (1) só propagação pen média × 100 | 0.8137045363350623 |
| 56 | 83,67 | AuxFlow no HSB, média (tabela 4 deles) | 3.4, 4 | `docs/00-problema.md` | 40 | — | (no texto da linha) |
| 57 | 96,15 | AuxFlow no HSB, mediana (tabela 4 deles) | 3.4 | `outputs/runs/rodada_test/tabelas_v2.out` | 49 | — | (no texto da linha) |
| 58 | 85,7 | HSB, pipeline, média, SNGS-136, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (3) pipeline pen média × 100 | 0.8570981719191836 |
| 59 | 72,6 | HSB, pipeline, média, SNGS-136, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 6 | (3) pipeline pen média × 100 | 0.7255668683761141 |
| 60 | 59,1 | HSB, pipeline, média, SNGS-123, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 3 | (3) pipeline pen média × 100 | 0.5911275246154905 |
| 61 | 45,7 | HSB, pipeline, média, SNGS-123, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 3 | (3) pipeline pen média × 100 | 0.4570200815129034 |
| 62 | 70,3 | HSB, pipeline, média, SNGS-124, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 4 | (3) pipeline pen média × 100 | 0.7029605282658911 |
| 63 | 61,9 | HSB, pipeline, média, SNGS-124, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 4 | (3) pipeline pen média × 100 | 0.6194730376440003 |
| 64 | 56,7 | HSB, pipeline, média, SNGS-150, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 8 | (3) pipeline pen média × 100 | 0.5673094429201146 |
| 65 | 56,2 | HSB, pipeline, média, SNGS-150, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 8 | (3) pipeline pen média × 100 | 0.5624648667136155 |
| 66 | 0,929 | LocSim@5 do AuxFlow, tabela 7 dele | 3.5, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T5.csv` | 3 | locsim5 | 0.929 |
| 67 | 0,885 | LocSim@5 do NBJW, tabela 7 do AuxFlow | 3.5, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T5.csv` | 2 | locsim5 | 0.885 |
| 68 | 0,027 | AuxFlow − propagação do v2 | 3.5 | `derivado: 0,929 − 0,902` | — | — | 0.0268465 |
| 69 | 0,017 | propagação do v2 − NBJW | 3.5 | `derivado: 0,902 − 0,885` | — | — | 0.0171535 |
| 70 | 85 | fração da distância entre a propagação do v1 e o AuxFlow fechada pelo v2 (%) | 3.5, 4 | `derivado: (0,902 − 0,749) / (0,929 − 0,749)` | — | — | 85.0839 |
| 71 | 958 | âncoras candidatas (n), v1 | 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 2 | n | 958 |
| 72 | 1.193 | âncoras candidatas (n), v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 2 | n | 1193 |
| 73 | 558 | âncoras aceitas (n), v1 | 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | n | 558 |
| 74 | 765 | âncoras aceitas (n), v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 4 | n | 765 |
| 75 | 12 | âncoras aceitas (erradas), v1 | 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | erradas | 12 |
| 76 | 11 | âncoras aceitas (erradas), v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 4 | erradas | 11 |
| 77 | 557 | aceitas com gabarito, v1 | — | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | com_gabarito | 557 |
| 78 | 759 | aceitas com gabarito, v2 | — | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 4 | com_gabarito | 759 |
| 79 | 2,2 | aceitas erradas entre as com gabarito, v1 (%) | 3.6 | `derivado: 12 / 557` | — | — | 2.1544 |
| 80 | 1,4 | aceitas erradas entre as com gabarito, v2 (%) | 3.6 | `derivado: 11 / 759` | — | — | 1.44928 |
| 81 | 0,035 | maior NPE das âncoras do v2 nos 5 clipes sem âncora do v1 | 3.6 | `derivado: máx. de npe_aceitas em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 0.0348 |
| 82 | 0,05 | limiar de âncora errada (NPE > 0,05) | 3.6 | `scripts/v2/rodada_test_v2/confere_v1_6c.py` | 24 | — | (no texto da linha) |
| 83 | 0,69 | menor LocSim@5 pen. da propagação, v2, nos 4 sem âncora do v1 fora o SNGS-147 | 3.6 | `derivado: mín. de c6 em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 0.693656 |
| 84 | 0,92 | maior LocSim@5 pen. da propagação, v2, nos 4 sem âncora do v1 fora o SNGS-147 | 3.6 | `derivado: máx. de c6 em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 0.916479 |
| 85 | 1 | âncoras do v2 no SNGS-147 | 3.6 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 33 | aceitas | 1 |
| 86 | 0,205 | LocSim@5 pen. da propagação no SNGS-147, v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 33 | c6 | 0.2045673097058661 |
| 87 | 36 | clipes que melhoram (Δ > 0) | 3.7 | `derivado: contagem em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 36 |
| 88 | 8 | clipes iguais (Δ = 0) | 3.7 | `derivado: contagem em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 8 |
| 89 | 5 | clipes que pioram (Δ < 0) | 3.7 | `derivado: contagem em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 5 |
| 90 | 0,008 | os três que pioram menos pioram menos que isto | 3.7 | `derivado: |Δ| dos três menores < 0,008` | — | — | 0.008 |
| 91 | 0,06 | os dois do HSB pioram cerca disto (|Δ| arredondado) | 3.7 | `derivado: |Δ| do SNGS-136 e do SNGS-123` | — | — | 0.06 |
| 92 | 0,883 | SNGS-136: v1_teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | v1_teto | 0.8829482446594011 |
| 93 | 0,933 | SNGS-136: teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | teto | 0.9329884794582567 |
| 94 | 0,893 | SNGS-136: v1_c6 | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | v1_c6 | 0.8928197823142751 |
| 95 | 0,832 | SNGS-136: c6 | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | c6 | 0.8319871461513194 |
| 96 | 21 | SNGS-136: aceitas | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | aceitas | 21 |
| 97 | 21 | SNGS-136: v1_aceitas | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | v1_aceitas | 21 |
| 98 | 0,868 | SNGS-123: v1_teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 9 | v1_teto | 0.8680514983597761 |
| 99 | 0,819 | SNGS-123: teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 9 | teto | 0.81901897796975 |
| 100 | 0,0198 | SNGS-136, candidata f39: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 3 | npe | 0.01977759733537401 |
| 101 | 0,0317 | SNGS-136, candidata f110: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 6 | npe | 0.03173352631317232 |
| 102 | 1,63 | SNGS-136, candidata f90: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 5 | nota | 1.6325153837664015 |
| 103 | 1,65 | SNGS-136, candidata f39: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 3 | nota | 1.6498971068454633 |
| 104 | 0,0058 | SNGS-136, candidata f189: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 7 | npe | 0.0057681588338117625 |
| 105 | 0,0204 | SNGS-136, candidata f9: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 2 | npe | 0.02036185695399478 |
| 106 | 1,575 | SNGS-136, candidata f234: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 9 | nota | 1.5746137599145933 |
| 107 | 1,595 | SNGS-136, candidata f189: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 7 | nota | 1.5954835994268128 |
| 108 | 0,043 | SNGS-123, candidata f51: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 28 | npe | 0.04304181575660122 |
| 109 | 0,0127 | SNGS-123, candidata f93: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 29 | npe | 0.012678433043977883 |
| 110 | 0,0049 | SNGS-123, candidata f195: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 32 | npe | 0.00487291185304517 |
| 111 | 0,094 | SNGS-123, candidata f132: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 30 | npe | 0.09360916639504269 |
| 112 | 0,064 | SNGS-123, candidata f153: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 31 | npe | 0.06381018119206373 |
| 113 | 0,020 | SNGS-136, f39: menor NPE das aceitas até a f110 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 3 | npe | 0.01977759733537401 |
| 114 | 0,032 | SNGS-136, f110: maior NPE das aceitas até a f110 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 6 | npe | 0.03173352631317232 |
| 115 | 0,006 | SNGS-136, f189: menor NPE das recusadas pelo B1 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 7 | npe | 0.0057681588338117625 |
| 116 | 0,020 | SNGS-136, f9: maior NPE das recusadas pelo B1 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 2 | npe | 0.02036185695399478 |
| 117 | 60 | SNGS-136: início do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 6 | inicio | 60 |
| 118 | 280 | SNGS-136: fim do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 6 | fim | 280 |
| 119 | 100 | SNGS-123: início do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 3 | inicio | 100 |
| 120 | 200 | SNGS-123: fim do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 3 | fim | 200 |
| 121 | 10 | janela de voto da verificação (±10 frames) | 3.7 | `config_v2.yaml` | 251 | — | (no texto da linha) |
| 122 | 0 | SNGS-123, vizinho f100 da candidata f93: sem H no v1 (False = 0) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 3 | v1_tem_H | 0 |
| 123 | 1 | SNGS-123, vizinho f100 da candidata f93: com H no v2 (True = 1) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 3 | v2_tem_H | 1 |
| 124 | 0 | SNGS-123, vizinho f200 da candidata f195: sem H no v1 (False = 0) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 6 | v1_tem_H | 0 |
| 125 | 1 | SNGS-123, vizinho f200 da candidata f195: com H no v2 (True = 1) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 6 | v2_tem_H | 1 |
