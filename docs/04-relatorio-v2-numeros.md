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
| 23 | 4 | A': H centrais recusadas pelo filtro da elipse (checagem barata) | 2 | `outputs/runs_v2/a_central/relatorio_a2.md` | 16 | — | (no texto da linha) |
| 24 | 448 | A': H centrais da checagem barata | 2 | `outputs/runs_v2/a_central/relatorio_a2.md` | 16 | — | (no texto da linha) |
| 25 | 15 | jogo 3 do dev, base B1 + A': H do A' | 2 | `derivado: linhas de outputs/runs_v2/base_b1a_local/a_jogo3.csv` | — | — | 15 |
| 26 | 11 | jogo 3: H do A' que viraram candidatas | 2 | `derivado: candidata = True em outputs/runs_v2/base_b1a_local/a_jogo3.csv` | — | — | 11 |
| 27 | 0 | jogo 3: candidatas do A' verificáveis ou aceitas | 2 | `derivado: verificavel ou aceita = True em outputs/runs_v2/base_b1a_local/a_jogo3.csv` | — | — | 0 |
| 28 | 0,14 | jogo 3: menor NPE das candidatas do A' | 2 | `derivado: mín. de npe em outputs/runs_v2/base_b1a_local/a_jogo3.csv` | — | — | 0.142159 |
| 29 | 0,20 | jogo 3: maior NPE das candidatas do A' | 2 | `derivado: máx. de npe em outputs/runs_v2/base_b1a_local/a_jogo3.csv` | — | — | 0.202297 |
| 30 | 2 | verificação: vizinhos mínimos com H | 2 | `config_v2.yaml` | 253 | — | (no texto da linha) |
| 31 | 3 | jogo 3, metade fixa: candidatas do A' (nenhuma aceita) | 2 | `outputs/runs_v2/a_central/relatorio_a2.md` | 40 | — | (no texto da linha) |
| 32 | 168 | metade fixa, fora o jogo 3: âncoras do A' | 2 | `docs/decisoes.md` | 1177 | — | (no texto da linha) |
| 33 | 3 | metade fixa, fora o jogo 3: âncoras do A' erradas | 2 | `docs/decisoes.md` | 1177 | — | (no texto da linha) |
| 34 | 16 | jogo 3 do dev, base B1 + A': clipes sem âncora | 5 | `outputs/runs_v2/base_b1a_local/por_jogo.csv` | 6 | sem_ancora | 16 |
| 35 | 21 | jogo 3 do dev: clipes | 5 | `outputs/runs_v2/base_b1a_local/por_jogo.csv` | 6 | clipes | 21 |
| 36 | 3 | jogos do GSR test (linhas da T6) | 5 | `derivado: linhas de outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | — | — | 3 |
| 37 | 0,159 | SNGS-147: cobertura do detector, v1 | 3.6 | `outputs/runs/rodada_test/falhas/clipes_test.csv` | 33 | cob_det | 0.15930388219544847 |
| 38 | 0,203 | SNGS-147: cobertura do detector, v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 33 | cob_det | 0.2034805890227577 |
| 39 | 2 | H de 2 + 2 retas (detector do v1) | 3.6 | `docs/04-relatorio.md` | 321 | — | (no texto da linha) |
| 40 | 0,419 | locsim_pen de detector, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | locsim_pen | 0.4192764091198964 |
| 41 | 0,624 | locsim_pen de detector, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 2 | locsim_pen | 0.624146109585618 |
| 42 | 0,505 | cobertura de detector, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 2 | cobertura | 0.5049593224116795 |
| 43 | 0,702 | cobertura de detector, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 2 | cobertura | 0.7023849325755043 |
| 44 | 0,749 | locsim_pen de 6c fluxo, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | locsim_pen | 0.7490157917374893 |
| 45 | 0,897 | cobertura de 6c fluxo, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | cobertura | 0.8971358520004458 |
| 46 | 0,959 | fracao_teto de 6c fluxo, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 6 | fracao_teto | 0.9590228680694096 |
| 47 | 0,959 | fracao_teto de 6c fluxo, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 6 | fracao_teto | 0.9588737408665611 |
| 48 | 0,763 | locsim_pen de 6c âncora de gabarito, v1 | 3.1 | `outputs/runs/rodada_test/tabelas/T1.csv` | 10 | locsim_pen | 0.7631048970488494 |
| 49 | 0,914 | locsim_pen de 6c âncora de gabarito, v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/tabelas/T1.csv` | 10 | locsim_pen | 0.9140772351342509 |
| 50 | 1 | conferência contra o v1 a 1 frame em 25 | 3.1, 3.7 | `scripts/v2/rodada_test_v2/confere_v1_test.py` | 3 | — | (no texto da linha) |
| 51 | 25 | conferência contra o v1 a 1 frame em 25 | 3.1, 3.7 | `scripts/v2/rodada_test_v2/confere_v1_test.py` | 3 | — | (no texto da linha) |
| 52 | 722 | H do v1 idênticas bit a bit na série do v2 | 3.1 | `outputs/runs_v2/rodada_test_v2/conferencia_v1.json` | — | iguais_bit_a_bit | 722 |
| 53 | 290 | H novas no v2 (frames sem H no v1) | 3.1 | `outputs/runs_v2/rodada_test_v2/conferencia_v1.json` | — | novas_no_v2 | 290 |
| 54 | 0,676 | LocSim@5 pen. da propagação, jogo 7, v1 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 2 | v1_locsim_pen_6c | 0.6759710080828238 |
| 55 | 0,914 | LocSim@5 pen. da propagação, jogo 7, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 2 | locsim_pen_6c | 0.9135220326519915 |
| 56 | 0,650 | LocSim@5 pen. da propagação, jogo 8, v1 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 3 | v1_locsim_pen_6c | 0.6499967158730243 |
| 57 | 0,839 | LocSim@5 pen. da propagação, jogo 8, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 3 | locsim_pen_6c | 0.838581896876749 |
| 58 | 0,920 | LocSim@5 pen. da propagação, jogo 11, v1 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 4 | v1_locsim_pen_6c | 0.9199799820597924 |
| 59 | 0,956 | LocSim@5 pen. da propagação, jogo 11, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 4 | locsim_pen_6c | 0.9564874784910701 |
| 60 | +0,037 | ganho da propagação v1 -> v2, jogo 11 (limitações) | 5 | `derivado: T6, jogo 11: locsim_pen_6c − v1_locsim_pen_6c` | — | — | 0.0365075 |
| 61 | +0,238 | ganho da propagação v1 -> v2, jogo 7 (limitações) | 5 | `derivado: T6, jogo 7: locsim_pen_6c − v1_locsim_pen_6c` | — | — | 0.237551 |
| 62 | 0,954 | LocSim@5 pen. do teto condicionado, jogo 11, v2 | 3.2 | `outputs/runs_v2/rodada_test_v2/tabelas/T6.csv` | 4 | locsim_pen_teto | 0.954306161772318 |
| 63 | 0,946 | H_gt pelas linhas como predição: LocSim@5 nos frames com gabarito (análise posterior do v1) | 3.2 | `outputs/runs/rodada_test/pos_rodada/B1_B3_B4.csv` | 12 | locsim_cob | 0.9464115216354456 |
| 64 | 18.133 | frames do conjunto comum, v1 | 3.3 | `outputs/runs/rodada_test/tabelas/T1b.csv` | 2 | frames | 18133 |
| 65 | 25.382 | frames do conjunto comum, v2 | 3.3 | `outputs/runs_v2/rodada_test_v2/tabelas/T1b.csv` | 2 | frames | 25382 |
| 66 | 0,926 | LocSim@5 pen. da propagação no conjunto comum, v2 | 3.3, 3.5 | `outputs/runs_v2/rodada_test_v2/tabelas/T1b.csv` | 6 | locsim_pen | 0.9260317577530113 |
| 67 | 0,882 | LocSim@5 pen. do detector no conjunto comum, v2 | 3.3 | `outputs/runs_v2/rodada_test_v2/tabelas/T1b.csv` | 2 | locsim_pen | 0.8823758985723601 |
| 68 | 61,7 | HSB, (3) pipeline pen média, v1 | 3.4, 4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen média × 100 | 0.617443855691164 |
| 69 | 74,5 | HSB, (3) pipeline pen média, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 14 | (3) pipeline pen média × 100 | 0.7447292972410947 |
| 70 | 71,1 | HSB, (3) pipeline pen mediana, v1 | 3.4, 4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline pen mediana × 100 | 0.7110783802185268 |
| 71 | 81,9 | HSB, (3) pipeline pen mediana, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 14 | (3) pipeline pen mediana × 100 | 0.8191605056318045 |
| 72 | 0,829 | HSB, (3) pipeline cobertura frames com pessoas, v1 | 3.4, 4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 14 | (3) pipeline cobertura frames com pessoas | 0.8285714285714286 |
| 73 | 1,000 | HSB, (3) pipeline cobertura frames com pessoas, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 14 | (3) pipeline cobertura frames com pessoas | 1.0 |
| 74 | 81,4 | HSB, (1) só propagação pen média, v2 | 3.4, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 12 | (1) só propagação pen média × 100 | 0.8137045363350623 |
| 75 | 83,67 | AuxFlow no HSB, média (tabela 4 deles) | 3.4, 4 | `docs/00-problema.md` | 40 | — | (no texto da linha) |
| 76 | 96,15 | AuxFlow no HSB, mediana (tabela 4 deles) | 3.4 | `outputs/runs/rodada_test/tabelas_v2.out` | 49 | — | (no texto da linha) |
| 77 | 85,7 | HSB, pipeline, média, SNGS-136, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 6 | (3) pipeline pen média × 100 | 0.8570981719191836 |
| 78 | 72,6 | HSB, pipeline, média, SNGS-136, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 6 | (3) pipeline pen média × 100 | 0.7255668683761141 |
| 79 | 59,1 | HSB, pipeline, média, SNGS-123, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 3 | (3) pipeline pen média × 100 | 0.5911275246154905 |
| 80 | 45,7 | HSB, pipeline, média, SNGS-123, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 3 | (3) pipeline pen média × 100 | 0.4570200815129034 |
| 81 | 70,3 | HSB, pipeline, média, SNGS-124, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 4 | (3) pipeline pen média × 100 | 0.7029605282658911 |
| 82 | 61,9 | HSB, pipeline, média, SNGS-124, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 4 | (3) pipeline pen média × 100 | 0.6194730376440003 |
| 83 | 56,7 | HSB, pipeline, média, SNGS-150, v1 | 3.4 | `outputs/runs/rodada_test/tabelas/T2.csv` | 8 | (3) pipeline pen média × 100 | 0.5673094429201146 |
| 84 | 56,2 | HSB, pipeline, média, SNGS-150, v2 | 3.4 | `outputs/runs_v2/rodada_test_v2/tabelas/T2.csv` | 8 | (3) pipeline pen média × 100 | 0.5624648667136155 |
| 85 | 0,929 | LocSim@5 do AuxFlow, tabela 7 dele | 3.5, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T5.csv` | 3 | locsim5 | 0.929 |
| 86 | 0,885 | LocSim@5 do NBJW, tabela 7 do AuxFlow | 3.5, 4 | `outputs/runs_v2/rodada_test_v2/tabelas/T5.csv` | 2 | locsim5 | 0.885 |
| 87 | 0,027 | AuxFlow − propagação do v2 | 3.5 | `derivado: 0,929 − 0,902` | — | — | 0.0268465 |
| 88 | 0,017 | propagação do v2 − NBJW | 3.5 | `derivado: 0,902 − 0,885` | — | — | 0.0171535 |
| 89 | 85 | fração da distância entre a propagação do v1 e o AuxFlow fechada pelo v2 (%) | 3.5, 4 | `derivado: (0,902 − 0,749) / (0,929 − 0,749)` | — | — | 85.0839 |
| 90 | 958 | âncoras candidatas (n), v1 | 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 2 | n | 958 |
| 91 | 1.193 | âncoras candidatas (n), v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 2 | n | 1193 |
| 92 | 558 | âncoras aceitas (n), v1 | 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | n | 558 |
| 93 | 765 | âncoras aceitas (n), v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 4 | n | 765 |
| 94 | 12 | âncoras aceitas (erradas), v1 | 3.6 | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | erradas | 12 |
| 95 | 11 | âncoras aceitas (erradas), v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 4 | erradas | 11 |
| 96 | 557 | aceitas com gabarito, v1 | — | `outputs/runs/rodada_test/tabelas/T7.csv` | 4 | com_gabarito | 557 |
| 97 | 759 | aceitas com gabarito, v2 | — | `outputs/runs_v2/rodada_test_v2/tabelas/T7.csv` | 4 | com_gabarito | 759 |
| 98 | 2,2 | aceitas erradas entre as com gabarito, v1 (%) | 3.6 | `derivado: 12 / 557` | — | — | 2.1544 |
| 99 | 1,4 | aceitas erradas entre as com gabarito, v2 (%) | 3.6 | `derivado: 11 / 759` | — | — | 1.44928 |
| 100 | 0,035 | maior NPE das âncoras do v2 nos 5 clipes sem âncora do v1 | 3.6 | `derivado: máx. de npe_aceitas em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 0.0348 |
| 101 | 0,05 | limiar de âncora errada (NPE > 0,05) | 3.6 | `scripts/v2/rodada_test_v2/confere_v1_6c.py` | 24 | — | (no texto da linha) |
| 102 | 0,69 | menor LocSim@5 pen. da propagação, v2, nos 4 sem âncora do v1 fora o SNGS-147 | 3.6 | `derivado: mín. de c6 em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 0.693656 |
| 103 | 0,92 | maior LocSim@5 pen. da propagação, v2, nos 4 sem âncora do v1 fora o SNGS-147 | 3.6 | `derivado: máx. de c6 em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 0.916479 |
| 104 | 1 | âncoras do v2 no SNGS-147 | 3.6 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 33 | aceitas | 1 |
| 105 | 0,205 | LocSim@5 pen. da propagação no SNGS-147, v2 | 3.6 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 33 | c6 | 0.2045673097058661 |
| 106 | 36 | clipes que melhoram (Δ > 0) | 3.7 | `derivado: contagem em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 36 |
| 107 | 8 | clipes iguais (Δ = 0) | 3.7 | `derivado: contagem em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 8 |
| 108 | 5 | clipes que pioram (Δ < 0) | 3.7 | `derivado: contagem em outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | — | — | 5 |
| 109 | 0,008 | os três que pioram menos pioram menos que isto | 3.7 | `derivado: |Δ| dos três menores < 0,008` | — | — | 0.008 |
| 110 | 0,06 | os dois do HSB pioram cerca disto (|Δ| arredondado) | 3.7 | `derivado: |Δ| do SNGS-136 e do SNGS-123` | — | — | 0.06 |
| 111 | 0,883 | SNGS-136: v1_teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | v1_teto | 0.8829482446594011 |
| 112 | 0,933 | SNGS-136: teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | teto | 0.9329884794582567 |
| 113 | 0,893 | SNGS-136: v1_c6 | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | v1_c6 | 0.8928197823142751 |
| 114 | 0,832 | SNGS-136: c6 | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | c6 | 0.8319871461513194 |
| 115 | 21 | SNGS-136: aceitas | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | aceitas | 21 |
| 116 | 21 | SNGS-136: v1_aceitas | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 22 | v1_aceitas | 21 |
| 117 | 0,868 | SNGS-123: v1_teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 9 | v1_teto | 0.8680514983597761 |
| 118 | 0,819 | SNGS-123: teto | 3.7 | `outputs/runs_v2/rodada_test_v2/clipes_test_v2.csv` | 9 | teto | 0.81901897796975 |
| 119 | 0,0198 | SNGS-136, candidata f39: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 3 | npe | 0.01977759733537401 |
| 120 | 0,0317 | SNGS-136, candidata f110: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 6 | npe | 0.03173352631317232 |
| 121 | 1,63 | SNGS-136, candidata f90: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 5 | nota | 1.6325153837664015 |
| 122 | 1,65 | SNGS-136, candidata f39: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 3 | nota | 1.6498971068454633 |
| 123 | 0,0058 | SNGS-136, candidata f189: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 7 | npe | 0.0057681588338117625 |
| 124 | 0,0204 | SNGS-136, candidata f9: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 2 | npe | 0.02036185695399478 |
| 125 | 1,575 | SNGS-136, candidata f234: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 9 | nota | 1.5746137599145933 |
| 126 | 1,595 | SNGS-136, candidata f189: nota | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 7 | nota | 1.5954835994268128 |
| 127 | 0,043 | SNGS-123, candidata f51: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 28 | npe | 0.04304181575660122 |
| 128 | 0,0127 | SNGS-123, candidata f93: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 29 | npe | 0.012678433043977883 |
| 129 | 0,0049 | SNGS-123, candidata f195: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 32 | npe | 0.00487291185304517 |
| 130 | 0,094 | SNGS-123, candidata f132: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 30 | npe | 0.09360916639504269 |
| 131 | 0,064 | SNGS-123, candidata f153: npe | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 31 | npe | 0.06381018119206373 |
| 132 | 0,020 | SNGS-136, f39: menor NPE das aceitas até a f110 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 3 | npe | 0.01977759733537401 |
| 133 | 0,032 | SNGS-136, f110: maior NPE das aceitas até a f110 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 6 | npe | 0.03173352631317232 |
| 134 | 0,006 | SNGS-136, f189: menor NPE das recusadas pelo B1 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 7 | npe | 0.0057681588338117625 |
| 135 | 0,020 | SNGS-136, f9: maior NPE das recusadas pelo B1 (limitações, 3 casas) | 5 | `outputs/runs_v2/rodada_test_v2/pioras.csv` | 2 | npe | 0.02036185695399478 |
| 136 | 60 | SNGS-136: início do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 6 | inicio | 60 |
| 137 | 280 | SNGS-136: fim do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 6 | fim | 280 |
| 138 | 100 | SNGS-123: início do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 3 | inicio | 100 |
| 139 | 200 | SNGS-123: fim do intervalo do HSB | 3.7 | `data_splits/hsb.csv` | 3 | fim | 200 |
| 140 | 10 | janela de voto da verificação (±10 frames) | 3.7 | `config_v2.yaml` | 251 | — | (no texto da linha) |
| 141 | 0 | SNGS-123, vizinho f100 da candidata f93: sem H no v1 (False = 0) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 3 | v1_tem_H | 0 |
| 142 | 1 | SNGS-123, vizinho f100 da candidata f93: com H no v2 (True = 1) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 3 | v2_tem_H | 1 |
| 143 | 0 | SNGS-123, vizinho f200 da candidata f195: sem H no v1 (False = 0) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 6 | v1_tem_H | 0 |
| 144 | 1 | SNGS-123, vizinho f200 da candidata f195: com H no v2 (True = 1) | 3.7 | `outputs/runs_v2/rodada_test_v2/pioras_vizinhos.csv` | 6 | v2_tem_H | 1 |
