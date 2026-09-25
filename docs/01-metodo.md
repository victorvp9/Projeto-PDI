# 01 — Método (especificação normativa)

Fonte única de verdade para o pipeline. Cada etapa declara **entrada, saída,
parâmetros e origem**. Parâmetros marcados `[EMPÍRICO]` devem ser calibrados na
partição de **treino** e nunca na de teste.

Referências: Gutiérrez-Pérez & Agudo (PnLCalib), Ziegler et al. (AuxFlow),
Citraro et al. (2020), Magera et al. (BroadTrack), Manafifard et al. (survey),
Maglo et al. (2023), Bassek et al. (2025).

---

## Modelo do campo

Sistema de coordenadas *campo*: metros, origem no centro, `X` no sentido do
comprimento, `Y` no sentido da largura, **positivo em direção à câmera
principal** (mesma orientação do WC14 e do GSR; ver `decisoes.md`).

Campo de **105 × 68 m**. Elementos e suas posições vêm das Regras do Jogo:
linhas laterais, linhas de fundo, linha do meio-campo, círculo central de raio
9,15 m, grandes áreas (16,5 m de profundidade, 40,32 m de largura), pequenas
áreas (5,5 m e 18,32 m), marcas de pênalti a 11 m, arcos da grande área.

O modelo é um dado, não um cálculo: defina em `src/pitch_model.py` como
constantes nomeadas, cada uma com o valor regulamentar.

> **Teste obrigatório:** as quatro bandeirinhas de escanteio devem estar em
> `(±52.5, ±34)`. É o teste que pega inversão de eixo.

> **Atenção — modelo de campo na avaliação.** O modelo interno é 105 × 68 m, mas
> os números publicados usam outros moldes: PnLCalib avalia WC14/TSWC com
> **115 × 74 jardas**; Chu et al. (KpSFR) e Maglo et al. com **100 × 60 m**. O
> `IoU_whole` e o erro em metros **dependem do molde**. Para comparar com a
> literatura, avalie também com o molde e o código de avaliação dela (ver
> `02-dados.md`), e declare qual foi usado em cada tabela.

---

## Etapa 1 — Segmentação do gramado

**Entrada:** frame BGR. **Saída:** máscara binária do gramado.

1. Converter para **HSV** (ou Lab — avaliar os dois e escolher com número, não
   com opinião; no WC14, o número é o IoU contra `N_grass_gt.mat`).
2. Limiarizar a faixa de verde. Os limites são `[EMPÍRICO]` e variam com
   iluminação de estádio, sombra atravessando o campo e horário do jogo.
   Considere estimar o pico de matiz por histograma em vez de fixar a faixa.
3. **Abertura** morfológica para remover ruído, **fechamento** para preencher
   buracos deixados por jogadores e marcações.
4. Manter o **maior componente conexo**. Preencher buracos internos.

> O survey do Manafifard trata detecção de gramado como a primeira etapa
> canônica, tipicamente por histograma de cor ou mistura de gaussianas, e relata
> que a mistura de gaussianas superou o histograma. Vale ler a seção 3 antes de
> implementar.

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

A elipse do círculo central é uma fonte de correspondências de altíssimo valor,
porque fica no meio do campo, região tipicamente pobre em interseções de linha.

> Cuidado: o centro da **elipse projetada** não é a projeção do **centro do
> círculo** (a perspectiva desloca um em relação ao outro). Use como
> correspondência a interseção da linha do meio-campo com a elipse, ou os pontos
> de tangência (conjunto `p2` do PnLCalib), e não o centro geométrico da elipse.

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

> O PnLCalib faz exatamente isso, mas de forma hierárquica e mais rica: além das
> interseções diretas (`p`), usa interseções de linhas estendidas (`pe`, só
> dentro da imagem ou até 50% além dela), interseções linha-elipse (`p1`),
> pontos de tangência (`p2`) e pontos auxiliares no eixo central (`p3`). A
> ablação deles mostra que cada conjunto aumenta a cobertura. Vale imitar a
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

> A função de ajuste ponto-linha é **a mesma** que produz a `H_gt` do GSR
> (Fatia 2, `src/homography.py`): escrita uma vez, aqui reaproveitada.

> O termo de linha é a contribuição central do PnLCalib — o módulo PnL otimiza
> pontos **e** linhas conjuntamente, o que ajuda justamente nas regiões distantes
> da grande área, onde os keypoints são escassos. Peso dos termos no artigo:
> `α = 0,6` para as linhas (ponto de partida; recalibrar no treino). Na ablação
> deles, refinar só com pontos quase não muda nada; o ganho vem das linhas.

> Nota do Maglo et al.: com keypoints em grade uniforme, o RANSAC tende a
> escolher pontos do lado distante do campo, que ficam concentrados na imagem, e
> a homografia piora. Amostragem com espaçamento crescente com a distância à
> câmera ("perspective-aware") corrigiu isso. Relevante para a grade de pontos
> auxiliares da Etapa 8c.

Parâmetros: limiar de inlier do RANSAC `[EMPÍRICO]` (Maglo usa 8 px em 1280×720,
referência), peso relativo dos termos ponto e linha `[EMPÍRICO]`.

---

## Etapa 8 — Consistência temporal

**Entrada:** sequência de frames e as homografias frame a frame.
**Saída:** homografias refinadas.

Três estratégias, a implementar e comparar. São independentes e podem ser
combinadas.

### 8a — Suavização da série de homografias (a mais barata)

Aplicar um filtro **Savitzky–Golay** diretamente sobre a série temporal das
matrizes de homografia. Bassek et al. usam **janela 31 e polinômio de terceiro
grau**, com lacunas de até 25 frames preenchidas por interpolação linear antes,
e registram um efeito colateral relevante: a suavização **impede que jogadores
saiam e reentrem no campo de visão em poucos frames** por causa de imprecisões
do método, e não de movimento real da câmera.

Implemente primeiro — é vinte linhas e estabelece a referência contra a qual as
outras duas precisam justificar sua complexidade.

> Cuidado: a homografia vive num espaço projetivo, não euclidiano. Suavizar as
> nove entradas da matriz independentemente é o que o artigo faz, mas não é
> obviamente correto (a escala da matriz é arbitrária: normalize antes, por
> exemplo `H[2,2] = 1`). Uma alternativa é suavizar a posição projetada dos
> quatro cantos do campo e reestimar a matriz. Compare as duas e registre em
> `docs/decisoes.md` — essa discussão é boa seção de relatório.

### 8b — Filtragem por Kalman

Referência: BHITK (Claasen & de Villiers), que relaciona a homografia de um frame
à do seguinte por transformação afim, com filtro de Kalman em dois estágios e
modelagem explícita da incerteza dos keypoints.

> Achado relevante para calibrar expectativa: o BHITK melhorou levemente no TSWC
> e **não melhorou nada** no SoccerNet GSR, segundo a tabela 7 do AuxFlow
> (implementação deles sobre o NBJW). Ganhos de consistência temporal parecem
> depender de dataset. Se você observar o mesmo, é resultado, não fracasso.

### 8c — Propagação por fluxo óptico (a contribuição principal)

Replica a estratégia do AuxFlow, sem o detector treinado.

1. **Seleção de frames-âncora.** Identificar os frames em que o pipeline
   funcionou bem. O AuxFlow usa uma heurística sobre os keypoints como
   pré-filtro (a âncora precisa conter por inteiro o círculo central ou uma das
   grandes áreas), mais uma métrica substituta de IoU no espaço da imagem —
   comparando a máscara do campo projetada com a segmentação — e toma os máximos
   locais. **Aqui isso é quase de graça:** a máscara da Etapa 1 já é a
   segmentação do gramado. Use-a.
2. **Amostragem de pontos auxiliares.** A partir da âncora, projetar pontos do
   modelo do campo para a imagem, criando correspondências onde não há marcação
   nenhuma. **Grade regular** (2,5 m × 2 m no AuxFlow), excluindo caixas de
   jogador **e da bola** dilatadas e uma borda da imagem. O AuxFlow mostra que a
   grade vence com folga a amostragem geométrica (83,67 contra 39,68) e empata
   na prática com a aleatória (83,39).
3. **Reidentificação por Lucas–Kanade** nos frames vizinhos, com verificação
   ida-e-volta (erro ida-e-volta ≤ 1 px no AuxFlow).
4. **Reestimativa** da homografia usando keypoints **e** pontos propagados.
   Sem os keypoints do detector, a propagação deriva (AuxFlow: 83,67 → 78,30).

> Contexto dos números acima: LocSim médio (%), subconjunto HSB do SoccerNet-GSR,
> **inicializado com a homografia de gabarito**. Sem o passo de fluxo, cai de
> 83,67 para 23,42 — a reidentificação é o que impede a deriva. Implemente o modo
> "sem fluxo" como ablação; é a comparação mais informativa do projeto.

> A escolha da âncora é decisiva: no GSR completo, âncoras a cada 150 frames
> (82,48) ficaram **abaixo** do detector sem propagação (83,48); as heurísticas
> levaram a 90,65 e a âncora de gabarito a 91,88. Inclua a âncora ingênua como
> ablação.

Parâmetros: densidade da grade, janela e níveis de pirâmide do Lucas–Kanade,
critério de seleção de âncora, distância máxima de propagação — `[EMPÍRICO]`.

### Detecção de corte

As três estratégias assumem continuidade temporal, e uma transmissão real não é
contínua. Bassek et al. contaram em média **981 cortes por partida, ou 10,9 por
minuto**, e reportam que em **38% dos frames de TV (resultados; 41% na
discussão — o artigo se contradiz)** nenhum jogador está visível, por decisão
editorial — close-ups, replays, cortes para outras câmeras.

Suavizar através de um corte é pior que não suavizar. Detecte descontinuidade
(diferença de histograma entre frames consecutivos, ou salto grande na
homografia) e **reinicie a série**. O BroadTrack faz exatamente isso: reinicializa
quando a confiança (IoU entre marcações detectadas e modelo projetado) cai abaixo
de 0,5.

> Um salto na homografia sozinho não prova corte: pode ser erro da estimativa
> (no SNGS-070, um salto de ~104 px na `H_gt` vinha da bola no ar entrando no
> ajuste — ver `decisoes.md`). Confirme com a diferença de histograma antes de
> reiniciar.

---

## Etapa 9 — Avaliação

Métricas consolidadas na literatura. Implemente as três. Definições do
protocolo do AuxFlow (seção 4.2), em `src/evaluate.py`; o que o artigo não diz
está em `decisoes.md`.

- **`IoU_whole`** — na vista de cima, IoU entre o molde do campo e o molde
  levado por `H_est⁻¹·H_gt` (campo → imagem pelo gabarito → campo pela
  estimativa). **É a métrica principal.**
- **`IoU_part`** — o molde reprojetado **na imagem** pela `H_gt` e pela `H_est`,
  com o IoU no espaço da imagem, dentro do quadro. Reporte também, mas com
  ressalva: Citraro et al. desaconselham esta versão, porque recortar pela região
  visível remove justamente o que está desalinhado — num quadro só de grama,
  qualquer estimativa que cubra o gabarito tira nota perfeita. A divergência
  entre as duas é informativa.
- **Erro de reprojeção** — sobre a grade do **campo** de 2,5 m em X × 2 m em Y,
  só os pontos cuja projeção pela `H_gt` cai dentro do quadro e à frente da
  câmera: **NPE** = ‖`H_est·X − H_gt·X`‖ / altura da imagem; **RE** (m) =
  ‖`H_est⁻¹(H_gt·X) − X`‖. Média por frame. No GSR, o BroadTrack tem o maior
  `IoU_entire` (0,8397 contra 0,8352 do AuxFlow), mas perde no `IoU_part`
  (0,9224 contra 0,9426) e sobretudo no erro de reprojeção em metros (1,34 contra
  0,84 m): otimizar contra as marcações negligencia a superfície como um todo.
  Uma métrica só nunca basta.

> **WC14, tabela à parte no "protocolo KpSFR":** as funções de avaliação do
> KpSFR copiadas sem mudança (`src/eval_kpsfr.py`, licença MIT), para comparar
> com quem usa esse código. As definições delas diferem das acima (ver
> `decisoes.md`); declare o protocolo em cada tabela.

> **Gabarito no GSR.** A `H_gt` é o **ajuste ponto-linha às linhas anotadas**
> (ver `02-dados.md`), no espírito do AuxFlow (seção 4.1: gabarito por RANSAC
> sobre as linhas anotadas); `IoU` e erro de reprojeção no GSR são medidos
> contra ela. O gabarito não é perfeito: reporte com e sem os frames de
> "gabarito duvidoso" (resíduo mediano do ajuste em (5, 10] px: a homografia só
> aproxima o campo) e declare quantos frames ficaram sem `H_gt` (ajuste mal
> determinado, ou resíduo > 10 px).

Adicionalmente, e específico deste projeto:

- **Taxa de cobertura** — fração de imagens em que o pipeline produziu
  homografia. Um método que acerta muito em poucos frames não serve.
- **Estabilidade temporal** — variação da homografia entre frames consecutivos,
  medida pelo deslocamento dos quatro cantos do campo projetados. É onde a
  propagação deve aparecer. Medida **na série estimada** (e, quando útil,
  comparada ao movimento real da imagem medido por Lucas–Kanade), **nunca como
  diferença contra a `H_gt`**: o gabarito do GSR tem tremor e desvios locais
  próprios, e comparar contra ele puniria o método por não reproduzi-los.
- **LocSim** (se o conjunto temporal for o SoccerNet-GSR) — similaridade de
  localização do GS-HOTA, `exp(ln(0,05)·d²/τ²)`: o centro da base da caixa de
  gabarito (imagem) vai para o campo pela **inversa da homografia estimada** e
  `d` é a distância ao `bbox_pitch` do dataset. **Não depende da `H_gt`** — é o
  protocolo oficial. Reporte τ = 5 m, τ = 2 m e o **mAP-LocSim** (média de
  τ = 1..10 m), como na tabela 7 do AuxFlow, que permite a comparação direta.
  Use só as pessoas: a caixa da bola no ar não está no chão.
- **Erro contra as linhas anotadas** (GSR) — distância dos pontos anotados às
  linhas do modelo projetadas pela homografia **estimada**, e acurácia a 5, 10 e
  20 px como no SN-Calib. É a única medida geométrica que **não depende de
  nenhuma `H_gt`**. Contagem do código do SN-Calib (`evaluate_camera.py`),
  **por classe**, em 960×540: classe anotada e projetada no quadro é TP se todos
  os seus pontos ficam a menos de γ da polilinha projetada, senão FP; projetada e
  não anotada, FP; anotada e não projetada, FN. Acurácia do frame =
  TP/(TP+FP+FN); resultado = média × completude. **Sem espelhamento**
  esquerda/direita (o código deles fica com o melhor dos dois; nós não).

### Taxa de inversão de visibilidade

A métrica que traduz erro geométrico em consequência prática, seguindo o
procedimento de Bassek et al.

1. Projetar a **região visível do frame** sobre o modelo do campo, obtendo um
   polígono de campo de visão no espaço do gramado. Use `shapely` para a
   geometria — é o que eles usam.
2. Fazer isso duas vezes: com a homografia de gabarito e com a estimada.
3. Para um conjunto de pontos de teste no campo (grade densa), comparar o rótulo
   dentro/fora dos dois polígonos. A fração que diverge é a **taxa de inversão**.

Se o conjunto temporal for o SoccerNet-GSR, repita com as **posições reais dos
jogadores**. Ressalva: o GSR só anota quem está no quadro, então todo jogador de
gabarito está "dentro" por construção — a medida com jogadores reais é
**unilateral** (só captura quem o registro jogaria para fora). A grade de pontos
de teste continua necessária para o lado oposto.

> Referência de ordem de grandeza: no pipeline do Bassek et al. com TVCalib, no
> **feed de scouting**, falhas de registro produziram material em que apenas um
> jogador aparecia visível em 1% do tempo, e nenhum em 3% — artefatos do método,
> não da edição. Não é a mesma grandeza que a taxa de inversão (é contagem por
> frame, não fração de pontos), então sirva-se dela como ordem de grandeza, não
> como comparação direta.

Reportar **média e mediana** de cada métrica. A mediana esconde os desastres e a
média os revela; a diferença entre as duas é diagnóstico.
