# v2: melhorias do pipeline clássico — plano (CONGELADO)

> Estado: congelado na tag `plano-v2-congelado`, antes de qualquer experimento.
> As decisões D1–D4 estão resolvidas na seção 9. A partir daqui, o plano só muda
> por uma entrada nova em `docs/decisoes.md` que diga o quê e por quê. Nenhum
> resultado reabre o plano.

## 1. Objetivo e ponto de partida

Reduzir a distância ao AuxFlow (LocSim@5 0,929 no GSR test, tabela 7 dele) sem rede
neural e, se possível, superá-lo num recorte declarado. O ponto de partida é o v1
congelado (`src/` em `418a3be` + `b3bcd98` + `38512a5`, `config.yaml` sem mudança):

| GSR test, v1 | LocSim@5 penalizado |
|---|---|
| detector | 0,419 |
| propagação (6c) | 0,749 (0,650–0,920 entre os 3 jogos) |
| teto condicionado às âncoras | 0,763 |
| AuxFlow | 0,929 |

Distância fechada hoje: (0,749 − 0,419) / (0,929 − 0,419) ≈ 65%.

**Limite que vale para qualquer melhoria:** a `H_gt` ajustada às linhas pintadas do
gabarito tira só 0,946 de LocSim@5 (relatório v1), porque o LocSim mede contra
posições da calibração do próprio dataset. Um método que acerta as linhas fica,
portanto, abaixo de ~0,946 mesmo com cobertura total. Passar de 0,929 exige chegar a
menos de 0,017 desse limite, o que no completo é improvável. Os recortes plausíveis
são os cobertos e o conjunto comum. Isso será dito no resultado.

## 2. Regras (do pedido de Victor; inegociáveis)

1. **v1 imutável.** Nada muda em `src/`, `config.yaml`, nos caches do v1
   (`outputs/cache/`), nas tabelas nem no relatório do v1. O v2 vive na branch
   `v2-melhorias`:
   - código em `src_v2/`, uma cópia do `src/` com os imports trocados para `src_v2`;
   - `config_v2.yaml`, com caminhos de saída próprios: `outputs/runs_v2/` para os
     manifestos e `outputs/cache_v2/` para os caches, para não tocar nos do v1;
   - testes em `tests_v2/`.

   A impressão digital do executor e as chaves de cache do v2 cobrem os bytes de
   `src_v2/`. Os defeitos de chave achados na revisão de 2026-10-14 (achados 2 e 3)
   são corrigidos no `src_v2/` **antes** do primeiro experimento, com teste, porque
   o v2 roda em dados com config e código mudando.
2. **O test está contaminado:** a análise de falhas inspecionou clipes do test um a
   um. Nenhuma escolha usa o test, nem clipes do test como alvo. As categorias de
   falha são reproduzidas em clipes do treino e da validação.
3. **Uma mudança por vez**, cada uma num commit com a tabela antes/depois por jogo.
   Não se varre parâmetro no dev para escolher o melhor sem validar fora (seção 4).
4. **Uma rodada única no test, no fim,** com a configuração final, rotulada
   "v2 exploratória (test já visto)". Ela vai lado a lado com o v1, por jogo, e não é
   apresentada como estimativa limpa de generalização.
5. Determinismo bit a bit, chaves por hash de bytes, executor seguro com manifesto,
   `uv sync` / `uv run`, e `uv run pytest -m "not slow"` antes de cada commit.
6. **Resultado negativo vai para `docs/decisoes.md`, com os números,** e o
   experimento não se repete com outro nome.

## 3. Dados de desenvolvimento

Dev = GSR train (jogos 4, 6 e 9; 57 clipes) + GSR valid (jogos 2, 3 e 5; 58 clipes),
ou seja, **6 jogos**. Os dois já foram vistos no v1 (a valid inspirou a histerese do
gramado), o que é aceito: o test é que precisaria estar limpo, e não está.

O v1 tem a série do detector em cache só em parte do treino: train[::3] (19 clipes)
mais o subconjunto, que somam 23 clipes. A valid inteira (58) tem série. A linha de
base nos 6 jogos pede antes a série e o 6c dos ~34 clipes de treino que faltam, com o
código do v1 (custo na seção 6).

Categorias de falha do test reproduzidas no dev (os nomes de clipes do test não
entram):

- **sem âncora em vista central:** clipes do dev sem âncora aceita. A valid tem 18,
  13 deles do jogo 3, por causa do gramado;
- **âncora errada por encaixe parcial:** âncoras aceitas com NPE > 0,05. Na valid
  são 29 de 290 (10,0%); no train[::3], 3 de 189 (1,6%);
- **deriva longe da âncora e lacunas longas:** frames a mais de 250 frames da âncora
  e lacunas de mais de 25 frames.

## 4. Protocolo de decisão

**Métrica de decisão:** LocSim@5 penalizado **por jogo**, nos 6 jogos de dev, e a
**mediana entre os jogos** do ganho Δ = v2 − v1.

**Validação cruzada por jogo:**

- **Mudança sem parâmetro livre** (estrutural, com os parâmetros herdados do v1 ou
  fixados por norma ou geometria): é avaliada uma vez, por jogo.
- **Mudança com parâmetro a escolher:**
  - a escolha é leave-one-game-out: para cada jogo g, o parâmetro sai da regra
    pré-registrada aplicada aos outros 5 jogos e é medido em g;
  - o Δ de g é o da escolha feita sem g;
  - a grade e a regra de escolha entram no commit do experimento antes de rodar;
  - se as 6 escolhas divergirem, o valor final é a regra aplicada aos 6 jogos, e a
    divergência é registrada.

**Critério de aceite** (todos; decisões D1 e D2):

1. Δ > 0 em pelo menos 4 dos 6 jogos, com o Δ de cada jogo medido fora da escolha
   (validação cruzada por jogo, acima);
2. média dos Δ por jogo > 0;
3. nenhum jogo com Δ < −0,03 de LocSim@5 penalizado.

O intervalo de 95% do bootstrap **de jogos** para a média dos Δ é relatado ao lado
de cada decisão, mas não decide. São 2.000 reamostragens com semente fixa; com 6
jogos há 462 reamostragens distintas.

**Onde se mede cada tipo de mudança** (decisão D3):

- **No detector (A, B, E):**
  1. checagem barata em todo o dev: o detector sozinho, a 1 frame em 25 (ver
     "Triagem barata", seção 5);
  2. confirmação na **metade fixa** do dev, com série e 6c: em cada jogo, os clipes
     ordenados pelo ID (SNGS-NNN, ordem numérica) e numerados a partir de 0; ficam os
     de índice par (0, 2, 4, …). Regra escrita aqui antes de qualquer resultado.
     A linha de base e o critério de aceite são os da mesma metade.
- **Na propagação (C, D):** dev inteiro, com a série reaproveitada.
- **Rodada completa no dev** (série e 6c nos 115 clipes): só para a combinação final
  das mudanças aceitas, no máximo 3 no ciclo.

**Métricas secundárias** (relatadas, não decidem): cobertura; fração de clipes sem
âncora aceita; âncoras aceitas erradas (NPE > 0,05); NPE mediano; LocSim@5 nos
cobertos e no conjunto comum; e as medidas específicas de cada hipótese.

**Aceitas em sequência:** cada hipótese aceita entra na base, e a seguinte é medida
contra a nova base. A ordem é a da seção 5, fixada aqui.

## 5. Hipóteses, na ordem de execução

Cada hipótese tem uma medida-alvo, que diz se a mudança fez o que pretendia, e a
decisão pela métrica da seção 4.

| # | hipótese | toca | medida-alvo |
|---|---|---|---|
| B | menos âncoras erradas por encaixe parcial: refinamento guiado em toda a imagem antes de pontuar; termo que penaliza linha do modelo visível sem suporte; verificação de profundidade (arco da área, lateral próxima) | detector (pontuação) e verificação das âncoras | âncoras aceitas erradas, por jogo; à parte, o caso "vizinhos concordam e todos errados" |
| A | mais âncoras em vista central: (a) círculo central (cônica → círculo) + linha do meio + laterais; (b) 1 reta transversal + elipse + 1–2 laterais (DLT misto de retas e cônica); (c) grande/pequena área oblíquas | detector (geração de hipóteses) | fração de clipes sem âncora aceita; NPE das âncoras novas antes da verificação temporal |
| C | propagação bidirecional entre âncoras: fusão direta + reversa ponderada, ou ajuste global da cadeia com âncoras fixas | só propagação (a série é reaproveitada) | NPE mediano a mais de 250 frames da âncora; lacunas > 25 frames |
| D | câmera PTZ: H = K R [I \| −C], com C fixo por clipe e pan/tilt/zoom por frame, como alternativa ao fluxo livre | só propagação | deriva (NPE contra a distância à âncora); tremor |
| E | segmentação adaptativa: limiar das marcações pela estatística de contraste do frame; pré-filtro de mediana ou bilateral | detector (segmentação) | cobertura e NPE do detector por jogo, sobretudo nos jogos 2, 4 e 5 (contraste baixo) |
| F | sinal das pessoas para escolher ou rejeitar âncoras | **fora deste ciclo** (decisão D4): mudaria a natureza do método; registrada como trabalho futuro em `docs/decisoes.md` | — |

**Por que esta ordem:**

- **B antes de A:** cada âncora nova de A passa pela mesma verificação, e com a B
  ruim as âncoras novas trazem encaixes parciais junto.
- **A tem a maior alavanca,** porque sobe o teto: clipe sem âncora vale 0.
- **C e D são baratas:** reaproveitam a série. Elas também sobem o teto, que é a
  propagação a partir da `H_gt` nas âncoras, e por isso não ficam presas aos 0,959.
- **E vem no fim,** porque é a mais sensível ao jogo (o candidato 30 → 15 teve sinal
  oposto nos jogos 4 e 9) e exige a validação cruzada por jogo completa.

**Triagem barata:** antes do custo cheio, as hipóteses de detector (A, B, E) passam
por uma triagem com o detector sozinho, a 1 frame em 25 nos 115 clipes do dev:

- medidas: cobertura, aceitas erradas (contra a `H_gt`) e NPE das aceitas, por jogo;
- quem piora, em algum jogo, a fração de H aceitas erradas (NPE > 0,05) em mais de
  0,02 em termos absolutos, ou não muda a medida-alvo, para aí e vai para o registro como negativo;
- a triagem não escolhe parâmetro: isso é sempre leave-one-game-out (seção 4).

## 6. Orçamento

**Custos medidos no v1** (relatório, máquina inteira):

- série do detector: ~630 s de parede por clipe (15 processos);
- propagação com as ablações: ~126 s por clipe (10 processos).

**Custo de cada medição** (decisão D3; o dev tem 115 clipes, e a metade fixa, ~58):

| medição | custo por execução |
|---|---|
| checagem barata do detector (1 frame em 25, dev inteiro) | ~1 h |
| confirmação no detector (série + 6c na metade fixa) | ~10 h de série + ~2 h de 6c |
| mudança de propagação (C, D; 6c no dev inteiro, série reaproveitada) | ~4 h |
| rodada completa no dev (série + 6c nos 115 clipes) | ~20 h + ~4 h |

**Execuções:**

| item | execuções | horas |
|---|---|---|
| linha de base v1 nos 6 jogos (série e 6c dos ~34 clipes de treino que faltam; a metade fixa sai dela) | 1 | ~7 |
| checagens baratas de A, B, E | até 6 | ~6 |
| confirmações de A, B, E na metade fixa; uma segunda só se a primeira der erro de implementação, registrado | até 6 | ~72 |
| C, D completas | até 4 | ~16 |
| rodadas completas no dev, só para a combinação final | **no máximo 3** | ~72 |
| rodada v2 no test | 1 | ~10 |

**Limite:** são cerca de 180 h de máquina. Experimento que não cabe nessas contagens
fica como trabalho futuro, registrado.

## 7. Linha de base (antes de qualquer hipótese)

O código v1 é rodado sem mudança nos 6 jogos de dev. Por jogo, mede-se:

- cobertura;
- fração de clipes sem âncora aceita;
- % de âncoras aceitas erradas (NPE > 0,05);
- LocSim@5 penalizado: detector, 6c e teto;
- mediana entre os jogos.

Também vai o caso "vizinhos concordam e todos errados", que a verificação por maioria
confirma: entre as âncoras aceitas erradas, a fração em que a maioria dos vizinhos
concordou.

**Já registrado no v1** (agregado, não por jogo):

| conjunto | clipes sem âncora | aceitas erradas | LocSim@5 pen. detector / 6c / teto |
|---|---|---|---|
| train[::3], 19 clipes | 2 de 19 | 3 de 189 (1,6%) | 0,364 / 0,708 / 0,771 |
| valid, 58 clipes | 18 de 58 | 29 de 290 (10,0%) | 0,173 / 0,436 / 0,529 |

## 8. Entregas

1. Este plano, congelado em commit antes do primeiro experimento.
2. Um commit por hipótese, com a tabela antes/depois por jogo e a entrada em
   `docs/decisoes.md`, aceita ou recusada.
3. O quadro de decisão: hipótese, Δ por jogo no dev, intervalo de jogos, aceita ou
   recusada.
4. Se alguma for aceita: a rodada v2 exploratória no test e o adendo
   `docs/04-relatorio-v2.md`, sem reescrever o v1.
5. A resposta franca: quanto da distância ao AuxFlow foi fechada, em que recorte
   (completo, HSB, cobertos, conjunto comum) e o que impede de passar, com o limite
   de ~0,946 da seção 1.

## 9. Decisões resolvidas (Victor, 2026-10-14)

- **D1. Critério de aceite:** Δ > 0 em ≥ 4 dos 6 jogos de dev, com validação cruzada
  por jogo, **e** média dos Δ por jogo > 0 (seção 4).
- **D2. Queda máxima tolerada num jogo:** −0,03 de LocSim@5 penalizado (seção 4).
- **D3. Medição das mudanças:**
  - **no detector (A, B, E):** checagem barata em todo o dev (detector sozinho, 1
    frame em 25), depois confirmação na metade fixa de cada jogo (índices pares na
    ordem de ID);
  - **rodada completa no dev:** só para a combinação final, no máximo 3 no ciclo;
  - **na propagação (C, D):** podem rodar completas;
  - orçamento ajustado na seção 6.
- **D4. Trilha F (pessoas):** fora do ciclo; registrada como trabalho futuro em
  `docs/decisoes.md`.
