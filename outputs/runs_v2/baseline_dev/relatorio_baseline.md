# Linha de base do v2 nos 6 jogos de dev

Código: `src_v2/` no commit `34c7307` (tag `baseline-dev`), bit a bit idêntico ao v1 nos 6 clipes conferidos (`docs/decisoes.md`, 2026-10-15). Dados: GSR train (jogos 4, 6, 9; 57 clipes) e valid (jogos 2, 3, 5; 58 clipes), 115 clipes. Script: `scripts/v2/baseline_dev.py`.

- **Caches:** a série e o 6c de 81 clipes vieram do `cache_v2`, regravados do v1 com as chaves do v2. Os 34 clipes do treino que o v1 nunca calculou foram calculados aqui, e os caches deles ficaram no `cache_v2`, reaproveitáveis pelas hipóteses C e D. Nada foi gravado em `outputs/cache` nem em `outputs/runs` do v1. A depuração do 6c foi para `outputs/v2/debug`.
- **Manifestos** (`manifestos/`): a série fechou com 510/510 trechos e 0 falhas; o 6c, com 115/115 clipes e 0 falhas, com a chave gravada de cada clipe conferida pelo `verify_keys`. A rodada foi pausada duas vezes a pedido de Victor, com os processos congelados e retomados sem perda.

## Tabela por jogo

| Jogo | Partição | Clipes | Sem âncora aceita | Cobertura: detector / 6c | Aceitas erradas (NPE > 0,05) | LocSim@5 pen.: detector / 6c / teto | NPE mediano do 6c nas lacunas: 1–3 / 4–25 / > 25 / pontas | Vizinhos concordam e todos errados |
|---|---|---|---|---|---|---|---|---|
| 4 | train | 18 | 4 | 0,281 / 0,774 | 4 de 86 (4,7%) | 0,215 / 0,488 / 0,604 | 0,0135 / 0,0255 / 0,0644 / 0,1378 | 4 de 4 |
| 6 | train | 19 | 0 | 0,495 / 1,000 | 4 de 258 (1,6%) | 0,421 / 0,825 / 0,897 | 0,0104 / 0,0120 / 0,0207 / 0,0183 | 4 de 4 |
| 9 | train | 20 | 1 | 0,447 / 0,950 | 8 de 206 (3,9%) | 0,360 / 0,810 / 0,827 | 0,0068 / 0,0094 / 0,0231 / 0,0125 | 7 de 8 |
| 2 | valid | 18 | 2 | 0,425 / 0,893 | 4 de 133 (3,0%) | 0,304 / 0,665 / 0,675 | 0,0165 / 0,0158 / 0,0324 / 0,1752 | 4 de 4 |
| 3 | valid | 21 | 13 | 0,100 / 0,390 | 19 de 47 (40,4%) | 0,041 / 0,139 / 0,315 | 0,1879 / 0,1872 / 0,1411 / 0,1068 | 19 de 19 |
| 5 | valid | 19 | 3 | 0,322 / 0,839 | 6 de 110 (5,5%) | 0,223 / 0,601 / 0,666 | 0,0146 / 0,0185 / 0,0569 / 0,0575 | 4 de 6 |
| **mediana dos 6 jogos** | | | 2,5 | 0,373 / 0,866 | 4,3% | **0,263 / 0,633 / 0,670** | 0,0141 / 0,0171 / 0,0447 / 0,0822 | |

O teto é o teto condicionado às âncoras: a propagação a partir da `H_gt` nos frames das âncoras verificadas. A cobertura é contada nos frames com `H_gt`. O LocSim@5 penalizado agrega por pessoa-frame, e a pessoa de um frame sem H vale 0. Os dados estão em `baseline_por_jogo.csv`.

**Conferência com o v1:** a valid soma 18 clipes sem âncora e 29 de 290 âncoras aceitas erradas, os números que o v1 tinha registrado.

## Vizinhos concordam e todos errados

O que a verificação temporal confirma por maioria, mesmo errado. Para cada âncora aceita errada, a verificação (`temporal.anchors`) foi refeita a partir da série em cache, dos cortes e do Lucas–Kanade, sem rodar o detector. Em todas as 45, a verificação refeita aceita a âncora de novo. Os dados estão em `vizinhos_aceitas_erradas.csv`, com uma linha por âncora: vizinhos, quantos concordaram, quantos dos que concordaram estavam errados e quantos não tinham gabarito (nenhum).

- **42 das 45 âncoras aceitas erradas** (93%) têm **todos** os vizinhos que concordaram também errados (NPE > 0,05 contra a `H_gt`). O detector repete o mesmo erro em frames seguidos, e a maioria o confirma.
- **As 3 exceções** estão no limite do critério de erro: SNGS-163 f6 (NPE 0,056; 3 dos 7 que concordaram errados), SNGS-080 f459 (0,056; 11 de 19) e SNGS-081 f78 (0,050; 2 de 11).
- **As erradas se concentram em poucos clipes:** as 45 estão em 20 clipes. Só o jogo 3 tem 19, em 5 clipes.

## Leitura

- **O jogo 3 (valid, sombra azulada) domina as falhas.** Ele tem 13 dos 23 clipes sem âncora, 40% de aceitas erradas e LocSim@5 do 6c de 0,139. Nele, até as lacunas curtas têm NPE mediano de 0,19, porque as âncoras estão erradas.
- **Distância do 6c ao teto:** é pequena nos jogos 9 (0,017), 2 (0,010) e 6 (0,073), e grande nos jogos 4 (0,116) e 3 (0,176). Nos jogos de contraste baixo (2, 4 e 5), o que limita é o próprio teto: a falta de âncoras e de cobertura.
- **A mediana entre os jogos** do LocSim@5 penalizado é 0,263 no detector, 0,633 no 6c e 0,670 no teto. É a referência da regra de aceite (seção 4 do plano). As mudanças de detector (A, B, E) se medem na metade fixa, com a linha de base da mesma metade, que sai dos mesmos caches.
