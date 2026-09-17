# 01 — Método (especificação normativa)

Fonte única de verdade para o pipeline. Cada etapa declara **entrada, saída,
parâmetros e origem**. Parâmetros marcados `[EMPÍRICO]` devem ser calibrados na
partição de **treino** e nunca na de teste.

Referências: Gutiérrez-Pérez & Agudo (PnLCalib), Ziegler et al. (AuxFlow),
Citraro et al. (2020), Magera et al. (BroadTrack), Manafifard et al. (survey).

---

## Modelo do campo

Sistema de coordenadas *campo*: metros, origem no centro, `X` no sentido do
comprimento, `Y` no sentido da largura.

Campo de **105 × 68 m**. Elementos e suas posições vêm das Regras do Jogo:
linhas laterais, linhas de fundo, linha do meio-campo, círculo central de raio
9,15 m, grandes áreas (16,5 m de profundidade, 40,32 m de largura), pequenas
áreas (5,5 m e 18,32 m), marcas de pênalti a 11 m, arcos da grande área.

O modelo é um dado, não um cálculo: defina em `src/pitch_model.py` como
constantes nomeadas, cada uma com o valor regulamentar.

> **Teste obrigatório:** as quatro bandeirinhas de escanteio devem estar em
> `(±52.5, ±34)`. É o teste que pega inversão de eixo.

---

## Etapa 1 — Segmentação do gramado

**Entrada:** frame BGR. **Saída:** máscara binária do gramado.

1. Converter para **HSV** (ou Lab — avaliar os dois e escolher com número, não
   com opinião).
2. Limiarizar a faixa de verde. Os limites são `[EMPÍRICO]` e variam com
   iluminação de estádio, sombra atravessando o campo e horário do jogo.
   Considere estimar o pico de matiz por histograma em vez de fixar a faixa.
3. **Abertura** morfológica para remover ruído, **fechamento** para preencher
   buracos deixados por jogadores e marcações.
4. Manter o **maior componente conexo**. Preencher buracos internos.

> O survey do Manafifard trata detecção de gramado como a primeira etapa
> canônica, tipicamente por histograma de cor ou mistura de gaussianas. Vale ler
> a seção antes de implementar.

**Depuração:** salvar máscara sobreposta ao frame.

---

## Etapa 2 — Realce das marcações

**Entrada:** frame + máscara do gramado. **Saída:** máscara binária das linhas.

Marcações são faixas **claras sobre fundo escuro**, de largura conhecida e
pequena. Duas estratégias, avaliar ambas:

- **Top-hat morfológico** com elemento estruturante maior que a largura esperada
  da linha em pixels. Realça estruturas claras finas.
- **Filtro de linha** explícito: para cada pixel, testar se é significativamente
  mais claro que os vizinhos a uma distância `d` de ambos os lados, em ambas as
  direções. `d` depende da escala e portanto da posição vertical na imagem —
  linhas distantes são mais finas.

Aplicar **apenas dentro da máscara do gramado**, para eliminar arquibancada,
placar e jogadores de uniforme claro.

Parâmetros: largura esperada da linha em pixels `[EMPÍRICO]`, limiar de contraste
`[EMPÍRICO]`.

**Depuração:** salvar a máscara de marcações.

---

## Etapa 3 — Detecção de segmentos de reta

**Entrada:** máscara de marcações. **Saída:** lista de segmentos em coordenadas
de imagem.

1. Afinar a máscara — esqueletonização ou supressão de não-máximos.
2. **Transformada de Hough probabilística** (`HoughLinesP`).
3. **Fusão de colineares:** agrupar segmentos com ângulo e distância à origem
   próximos, e uni-los. Sem essa fusão, uma única linha do campo vira dezenas de
   fragmentos e o passo seguinte quebra.

Parâmetros: resolução angular e radial do acumulador, limiar de votos,
comprimento mínimo, gap máximo, tolerâncias de fusão — todos `[EMPÍRICO]`.

> Atenção: linhas perto da borda do quadro e linhas quase paralelas à direção de
> varredura são os casos que mais geram fragmentação.

**Depuração:** desenhar os segmentos sobre o frame, coloridos por grupo.

---

## Etapa 4 — Cônicas

**Entrada:** máscara de marcações menos os pixels já atribuídos a retas.
**Saída:** elipses ajustadas.

O círculo central e os arcos da grande área projetam-se como **elipses**. Ajustar
com `cv2.fitEllipse` sobre os contornos remanescentes, filtrando por área mínima
e por razão de eixos plausível.

O centro da elipse do círculo central é uma correspondência de altíssimo valor,
porque fica no meio do campo, região tipicamente pobre em interseções de linha.

Parâmetros: área mínima `[EMPÍRICO]`, tolerância de ajuste `[EMPÍRICO]`.

---

## Etapa 5 — Classificação semântica

**Entrada:** segmentos e elipses. **Saída:** rótulo de cada um no modelo do campo.

Esta é a etapa mais difícil do pipeline clássico e a que mais merece cuidado.

Heurísticas disponíveis, a combinar:
- **Orientação.** Sob a câmera principal, linhas laterais e de fundo têm
  orientações características na imagem.
- **Ponto de fuga.** Linhas paralelas no campo convergem na imagem; agrupar por
  ponto de fuga separa as duas famílias de paralelas.
- **Posição relativa.** A linha de fundo está além da grande área, que está além
  da pequena área, na mesma direção.
- **A elipse do círculo central** ancora o meio-campo e desambigua qual metade do
  campo está em vista.

> Registre em `docs/decisoes.md` cada heurística adotada e em que casos ela
> falha. A análise de falhas desta etapa é conteúdo de relatório.

---

## Etapa 6 — Correspondências

**Entrada:** segmentos classificados. **Saída:** pares (ponto no campo, ponto na
imagem).

Gerar keypoints por **interseção** dos segmentos classificados — cada par de
linhas cujo cruzamento é um ponto conhecido no modelo do campo.

> O PnLCalib faz exatamente isso, mas de forma hierárquica e mais rica: constrói
> conjuntos adicionais de pontos a partir de extração de linhas e ajuste de
> elipses, porque as interseções anotadas sozinhas são poucas demais. A ablação
> deles mostra que cada conjunto adicional aumenta a cobertura. Vale imitar a
> ideia, sem a rede.

Se houver menos de quatro correspondências, o frame é reportado como **falha de
cobertura** — não invente homografia.

---

## Etapa 7 — Homografia

**Entrada:** correspondências. **Saída:** matriz `H` no sentido campo → imagem.

1. **DLT dentro de RANSAC** (`cv2.findHomography` com `RANSAC`). O RANSAC existe
   porque uma única correspondência errada destrói uma solução por mínimos
   quadrados.
2. **Refinamento não-linear** (Levenberg–Marquardt) minimizando o erro de
   reprojeção. Além dos pontos, incluir um termo de **distância ponto-linha**:
   projetar pontos amostrados ao longo das linhas do modelo e medir sua distância
   às linhas detectadas na imagem.

> O termo de linha é a contribuição central do PnLCalib — o módulo PnL otimiza
> pontos **e** linhas conjuntamente, o que ajuda justamente nas regiões distantes
> da grande área, onde os keypoints são escassos. É o que separa uma
> implementação ingênua de uma boa.

Parâmetros: limiar de inlier do RANSAC `[EMPÍRICO]`, peso relativo dos termos
ponto e linha `[EMPÍRICO]`.

---

## Etapa 8 — Consistência temporal

**Entrada:** sequência de frames e as homografias frame a frame.
**Saída:** homografias refinadas.

Três estratégias, a implementar e comparar. São independentes e podem ser
combinadas.

### 8a — Suavização da série de homografias (a mais barata)

Aplicar um filtro **Savitzky–Golay** diretamente sobre a série temporal das
matrizes de homografia. Bassek et al. usam **janela 31 e polinômio de terceiro
grau**, e registram um efeito colateral relevante: a suavização **impede que
jogadores saiam e reentrem no campo de visão em poucos frames** por causa de
imprecisões do método, e não de movimento real da câmera.

Implemente primeiro — é vinte linhas e estabelece a referência contra a qual as
outras duas precisam justificar sua complexidade.

> Cuidado: a homografia vive num espaço projetivo, não euclidiano. Suavizar as
> nove entradas da matriz independentemente é o que o artigo faz, mas não é
> obviamente correto. Uma alternativa é suavizar a posição projetada dos quatro
> cantos do campo e reestimar a matriz. Compare as duas e registre em
> `docs/decisoes.md` — essa discussão é boa seção de relatório.

### 8b — Filtragem por Kalman

Referência: BHITK (Claasen & de Villiers), que relaciona a homografia de um frame
à do seguinte por transformação afim, com filtro de Kalman em dois estágios e
modelagem explícita da incerteza dos keypoints.

> Achado relevante para calibrar expectativa: o BHITK melhorou no TSWC dos
> próprios autores e **não melhorou nada** no SoccerNet GSR, segundo a tabela do
> AuxFlow. Ganhos de consistência temporal parecem depender de dataset. Se você
> observar o mesmo, é resultado, não fracasso.

### 8c — Propagação por fluxo óptico (a contribuição principal)

Replica a estratégia do AuxFlow, sem o detector treinado.

1. **Seleção de frames-âncora.** Identificar os frames em que o pipeline
   funcionou bem. O AuxFlow usa uma heurística sobre os keypoints como
   pré-filtro, mais uma métrica substituta de IoU no espaço da imagem —
   comparando a máscara do campo projetada com a segmentação. **Aqui isso é
   quase de graça:** a máscara da Etapa 1 já é a segmentação do gramado. Use-a.
2. **Amostragem de pontos auxiliares.** A partir da âncora, projetar pontos do
   modelo do campo para a imagem, criando correspondências onde não há marcação
   nenhuma. **Grade regular** — o AuxFlow mostra que vence com folga a amostragem
   geométrica (83,67 contra 39,68) e empata na prática com a aleatória (83,39).
3. **Reidentificação por Lucas–Kanade** nos frames vizinhos.
4. **Reestimativa** da homografia usando keypoints **e** pontos propagados.

> Sem o passo de fluxo, o desempenho no experimento controlado do AuxFlow cai de
> 83,67 para 23,42 — a reidentificação é o que impede a deriva. Implemente o modo
> "sem fluxo" como ablação; é a comparação mais informativa do projeto.

Parâmetros: densidade da grade, janela e níveis de pirâmide do Lucas–Kanade,
critério de seleção de âncora, distância máxima de propagação — `[EMPÍRICO]`.

### Detecção de corte

As três estratégias assumem continuidade temporal, e uma transmissão real não é
contínua. Bassek et al. contaram em média **981 cortes por partida, ou 10,9 por
minuto**, e reportam que em **41% do material de TV nenhum jogador está visível**,
por decisão editorial — close-ups, replays, cortes para outras câmeras.

Suavizar através de um corte é pior que não suavizar. Detecte descontinuidade
(diferença de histograma entre frames consecutivos, ou salto grande na
homografia) e **reinicie a série**. O BroadTrack faz exatamente isso: reinicializa
quando a confiança cai.

---

## Etapa 9 — Avaliação

Métricas consolidadas na literatura. Implemente as três.

- **`IoU_whole`** — projeta o modelo do campo para a vista de cima usando a
  homografia de gabarito e a estimada, e mede a interseção sobre união na **área
  inteira do modelo**. Convenção do Homayounfar.
- **`IoU_part`** — o mesmo, restrito à **área visível na imagem**. Convenção do
  Sharma. Reporte as duas: um método pode ser bom numa e ruim na outra, e a
  divergência é informativa.
- **Erro de reprojeção** — em pixels e em metros. O AuxFlow mostra que o
  BroadTrack vence em IoU mas perde feio em erro de reprojeção em metros, porque
  otimizar contra as marcações negligencia a superfície como um todo. Uma métrica
  só nunca basta.

Adicionalmente, e específico deste projeto:

- **Taxa de cobertura** — fração de imagens em que o pipeline produziu
  homografia. Um método que acerta muito em poucos frames não serve.
- **Estabilidade temporal** — variação da homografia entre frames consecutivos,
  medida pelo deslocamento dos quatro cantos do campo projetados. É onde a
  propagação deve aparecer.

### Taxa de inversão de visibilidade

A métrica que traduz erro geométrico em consequência prática, seguindo o
procedimento de Bassek et al.

1. Projetar a **região visível do frame** sobre o modelo do campo, obtendo um
   polígono de campo de visão no espaço do gramado. Use `shapely` para a
   geometria — é o que eles usam.
2. Fazer isso duas vezes: com a homografia de gabarito e com a estimada.
3. Para um conjunto de pontos de teste no campo, comparar o rótulo
   dentro/fora dos dois polígonos. A fração que diverge é a **taxa de inversão**.

Se você tiver posições reais de jogador — e no TSWC não tem, mas o material
suplementar do Bassek et al. traz dados intermediários pré-processados — use as
posições reais em vez de pontos de teste. O número fica diretamente comparável ao
deles.

> Referência de ordem de grandeza: no pipeline com TVCalib, falhas de registro
> produziram material em que apenas um jogador aparecia visível em 1% do tempo, e
> nenhum em 3% — artefatos do método, não da edição. Esses são os números que um
> pipeline clássico precisa perseguir.

Reportar **média e mediana** de cada métrica. A mediana esconde os desastres e a
média os revela; a diferença entre as duas é diagnóstico.
