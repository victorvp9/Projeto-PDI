# 00 — O problema

## Contexto

Para transformar um pixel de uma transmissão de futebol em uma coordenada em
metros dentro do campo, é preciso estimar a transformação entre a imagem e o
gramado. Como o gramado é aproximadamente um plano e o sensor é outro plano, essa
transformação é uma **homografia** — uma matriz 3×3 com oito graus de liberdade,
determinada por no mínimo quatro correspondências.

A vantagem inicial parece enorme: campos de futebol são padronizados por
regulamento, e suas marcações são conhecidas. Na prática, três dificuldades
quebram isso:

**As marcações são esparsas e mal distribuídas.** Concentram-se nas grandes áreas
e no círculo central. Há regiões extensas do gramado — os corredores laterais no
meio-campo — sem nada para detectar.

**As câmeras têm zoom de até 25×.** Num plano fechado, pode não haver marcação
nenhuma no quadro.

**A estimativa frame a frame é instável.** Um método pode acertar em média e
tremer de um frame para o outro. Para inserir grafismo ou derivar velocidade de
jogador a partir da posição, esse tremor é fatal.

## Onde a literatura está

A área migrou para detectores de keypoint treinados. O PnLCalib, estado da arte
atual, usa uma rede HRNetv2 produzindo mapas de calor, com uma grade hierárquica
de pontos derivada geometricamente e um módulo de refinamento que otimiza pontos
e linhas em conjunto. O BroadTrack modela fisicamente a lente e o tripé da câmera
de broadcast. O AuxFlow propaga correspondências por fluxo óptico entre
frames-âncora.

Três observações desse conjunto motivam este projeto.

A primeira: o **AuxFlow mostrou que a propagação temporal é decisiva**. No
experimento controlado deles — LocSim médio (%), no subconjunto HSB de 10
sequências difíceis do SoccerNet-GSR, **partindo da homografia de gabarito** —
remover o fluxo óptico derruba o desempenho de 83,67 para 23,42. E, mais
interessante, o método clássico **Lucas–Kanade venceu o aprendido RAFT** (83,67
contra 78,71): o RAFT é mais preciso por ponto, mas o Lucas–Kanade retém mais
que o dobro de pontos, e a homografia ganha mais com quantidade do que com
precisão individual.

A segunda: a propagação foi sempre avaliada acoplada a um detector *forte* (o
NBJW, uma rede treinada). O AuxFlow chega perto da nossa pergunta, mas não a
responde: mostra que a propagação se recupera de uma inicialização ruim (54,74
contra 43,15 do detector sozinho, com a homografia inicial perturbada em até
10%) e escolhe justamente sequências onde o detector falha. Também mostra o
risco: âncoras escolhidas ingenuamente, a cada 150 frames, ficam **abaixo** do
detector sem propagação (82,48 contra 83,48 no GSR completo). O que ninguém
mediu é o ganho da propagação quando o **detector inteiro** é fraco — não só a
âncora inicial.

A terceira vem de fora da literatura de calibração. Bassek et al. (2025) usaram o
TVCalib para estimar a região visível do campo em transmissões reais, e
suavizaram a série temporal das homografias com um **filtro Savitzky–Golay de
janela 31 e polinômio de terceiro grau**. Ao descrever o método, registram uma
lacuna explícita: embora o registro tenha sido avaliado com sucesso em benchmarks
padrão, **o efeito desse pós-processamento sobre a consistência temporal e sobre
frames difíceis — grandes zooms, por exemplo — não havia sido testado**. A
validação deles foi qualitativa, por inspeção visual de sequências de amostra.

## A pergunta deste projeto

> Até onde chega um pipeline de registro de campo puramente clássico — cor,
> morfologia, Hough, ajuste de cônica, RANSAC — e quanto da diferença para o
> estado da arte a propagação temporal por fluxo óptico consegue fechar?

A hipótese é que a propagação tenha **ganho marginal maior sobre um detector
fraco** do que sobre um forte: se o detector acerta 90% dos frames, sobra pouco a
recuperar; se acerta 50%, os frames bons podem sustentar os ruins. O resultado
das âncoras ingênuas do AuxFlow indica a condição: isso só vale se as âncoras
forem bem escolhidas. Se a hipótese se confirmar, é um resultado útil —
significa que um sistema leve e sem GPU pode ser viável para aplicações offline.

E uma segunda pergunta, derivada do Bassek et al.:

> Qual das três estratégias de consistência temporal — suavização da série de
> homografias, filtragem por Kalman, propagação por fluxo óptico — entrega mais
> estabilidade, e a que custo?

## Medir a consequência, não só a geometria

`IoU` e erro de reprojeção medem a geometria, mas não dizem o que o erro
*provoca*. Bassek et al. dão o elo que faltava: eles projetam a região visível do
frame sobre o modelo do campo e marcam como **não observado** todo jogador que
cai fora desse polígono. O erro de registro, portanto, vira **erro de rótulo de
visibilidade** — e eles reportam a taxa de artefato do próprio pipeline no
**feed de scouting** (câmera aberta): em 1% do material apenas um jogador
aparecia visível, em 3% nenhum, ambos causados por falhas do registro e não pela
edição.

Isso dá a este projeto uma métrica com significado prático, e é o argumento mais
forte que ele pode apresentar: não "meu IoU foi 0,85", mas "meu registro
classifica errado a visibilidade de X% dos jogadores-frame". Um relatório de PDI
que fecha assim vale mais que um que para na geometria.

## A estratégia

1. **Pipeline clássico frame a frame.** Segmentar gramado, realçar marcações,
   detectar linhas e cônicas, classificar semanticamente os segmentos,
   corresponder ao modelo do campo, estimar homografia por RANSAC + DLT e
   refinar por otimização não-linear.
2. **Medir no WC14.** Benchmark tradicional, imagens isoladas. Estabelece o
   desempenho do detector sozinho.
3. **Propagação temporal.** Seleção de frames-âncora, amostragem de pontos
   auxiliares em grade regular sobre o modelo do campo, reidentificação por
   Lucas–Kanade, reestimativa conjunta.
4. **Medir no SoccerNet-GSR.** Clipes de 750 frames consecutivos a 25 fps, com
   posição dos jogadores no campo e linhas anotadas na imagem (a homografia de
   gabarito é derivada delas; o arquivo não traz câmera — ver `decisoes.md`). Só
   em sequências a propagação pode ser avaliada, e é o mesmo teste em que o
   AuxFlow reporta seus números.
5. **Comparar o ganho** com o que o AuxFlow reporta sobre um detector treinado.

## Escopo

**Dentro:** vistas da câmera principal, com zoom moderado. É o que o WC14 e o GSR
contêm por construção.

**Fora:** câmeras atrás do gol, lentes olho-de-peixe, close-ups sem marcação
visível, e calibração 3D completa (parâmetros intrínsecos e extrínsecos). Este
projeto para na homografia planar — traves e bola no ar ficam fora.

> Sobre a distorção de lente: o BroadTrack encontrou nela o maior ganho da sua
> ablação no GSR; o AuxFlow, no mesmo dataset, mediu que uma homografia pura
> derivada das marcações de gabarito já dá LocSim de 0,9928. Para localizar
> jogadores com tolerância de metros, a homografia basta; para reprojeção em
> pixels, a distorção pode aparecer como erro residual. Registre se observar.

## Critério de sucesso

O projeto está pronto quando `uv run python -m src.run --all --splits test --wc14-split test`
produz, do zero, as métricas e as tabelas do test (as figuras saem de
`scripts/relatorio/figuras.py` e `scripts/rodada_test/analise_falhas.py`; o `--all`
padrão, com todas as partições do GSR, leva mais de 30 h e não produz as tabelas do test):

- `IoU_whole`, `IoU_part` e erro de reprojeção no WC14, com média e mediana;
- as mesmas métricas e o LocSim no GSR, com e sem propagação;
- uma medida de **estabilidade temporal** — variação da homografia entre frames
  consecutivos — que é onde a propagação deve aparecer mais forte;
- a **taxa de inversão de visibilidade**: com que frequência o erro de registro
  muda o rótulo dentro/fora do quadro, comparado ao gabarito;
- taxa de cobertura: em quantas imagens o pipeline conseguiu produzir alguma
  homografia;
- imagens de depuração de cada etapa, para um punhado de casos bons e ruins.

Não é necessário bater o estado da arte. É necessário que os números sejam
corretos, reprodutíveis, e que cada etapa do pipeline justifique sua existência
com uma medição.
