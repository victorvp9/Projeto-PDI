# 02 — Dados

Nada em `data/` entra no Git. Baixe manualmente.

> **Decidido (2026-09-25, ver `decisoes.md`):** **WC14 original** para a
> avaliação frame a frame e **SoccerNet-GSR** como conjunto temporal principal.
> TSWC e CARWC ficam fora; o TSWC só volta se o espaçamento entre imagens se
> mostrar consecutivo.

## Layout local (conferido em 2026-09-25)

```
data/
├── soccer_data_WC14/raw/
│   ├── train_val/          # 209 × (N.jpg, N.homographyMatrix, N_grass_gt.mat)
│   │                       #   + 100_seg_pred.mat (ignorar, ver abaixo)
│   └── test/               # 186 × os mesmos três arquivos
└── SoccerNet-GSR/
    ├── train/  (57 clipes) ─┐
    ├── valid/  (58 clipes)  ├─ sequences_info.json
    └── test/   (49 clipes) ─┘  SNGS-XXX/img1/000001.jpg … 000750.jpg
                                SNGS-XXX/Labels-GameState.json
```

Na raiz do repositório há também `sports_soccer_code_WC14/`, o código original
de Homayounfar et al. (MATLAB/C++). Serve só de referência, e fica fora do Git.

---

## WC14 — benchmark frame a frame (em uso)

Dataset de referência para registro de campo em futebol, de Homayounfar et al.
(CVPR 2017). Download: `https://nhoma.github.io/data/soccer_data.tar.gz`.

- **209 imagens de treino** (dez jogos) e **186 de teste** (outros dez jogos),
  da Copa do Mundo de 2014, 1280×720.
- Cada imagem tem uma **matriz de homografia anotada manualmente**.
- Só câmera central principal, **sem zoom grande**.
- **As imagens não estão em sequência** — servem para avaliar o detector, nunca a
  propagação.

**Formato verificado (2026-09-25, 3 imagens de treino):** por imagem `N`,

- `N.jpg` — o frame;
- `N.homographyMatrix` — 3×3 em texto, sentido **imagem (px) → molde em jardas
  115 × 74**, origem no canto esquerdo do lado oposto à câmera, `x` ao longo do
  comprimento, `y` crescendo em direção à câmera. Converter para o interno com
  `H_gt = inv(H_arquivo) @ A` (ver `decisoes.md` para `A`);
- `N_grass_gt.mat` — variável `grass`, máscara binária 720×1280 do gramado no
  espaço da imagem. **É gabarito pronto para a Etapa 1**: permite medir a
  segmentação do gramado com IoU, e não só por inspeção visual. A máscara inclui
  o gramado **fora** das linhas (atrás do gol, além das laterais): o molde
  projetado pelo gabarito cai sobre ela em ≥ 99,7% da área nas 209 imagens de
  treino, mas o IoU entre os dois vai de 0,72 a ~0,98 (mediana 0,93), conforme
  quanto gramado extra aparece no quadro (ver `decisoes.md`).

A pasta `train_val` é o treino (o WC14 não tem validação separada). Ela traz
um arquivo a mais, `100_seg_pred.mat`, que é uma **predição** de segmentação dos
autores, e não gabarito. O loader procura `N_grass_gt.mat` pelo nome exato.

Partições distintas por jogo. Use o treino para calibrar todo parâmetro
`[EMPÍRICO]` e o teste apenas para a medição final. Ajustar no teste invalida o
resultado.

> O TVCalib (Theiner & Ewerth) anotou adicionalmente os segmentos do split de
> teste do WC14, no formato do SN-Calib (confirmado no PnLCalib). Essa anotação
> permite avaliar as Etapas 3 a 5 isoladamente, e não só o resultado final.

---

## SoccerNet-GSR — sequências com jogadores (em uso, conjunto temporal principal)

SoccerNet Game State Reconstruction (Somers et al., 2024). **200 clipes de 30 s**
(750 frames, 25 fps, 1920×1080), câmera principal de transmissão: **57 treino,
58 validação, 49 teste** e 36 de desafio sem gabarito. A contagem vem do
`sequences_info.json` (versão 3, idêntico nas três partições); o site fala em
59 e 50, e o BroadTrack também reporta 49 no teste.

- Download direto no Hugging Face, sem conta nem NDA (licença GPL-3.0):
  `https://huggingface.co/datasets/SoccerNet/SN-GSR-2024` —
  `train.zip` (9,76 GB), `valid.zip` (11,2 GB), `test.zip` (8,85 GB);
  `challenge.zip` não tem gabarito e não é necessário. Usar a versão 2024 (a dos
  artigos); a SN-GSR-2025 tem arquivos de mesmo tamanho.
- Molde 105 × 68 m, origem no centro, `y` positivo em direção à câmera — o mesmo
  do modelo interno deste projeto.
- É onde **AuxFlow, BroadTrack e o baseline GSR** reportam números. O AuxFlow
  publica os IDs e intervalos de frames do subconjunto difícil (HSB), o que
  permite comparação direta.
- **HSB (Hard Sequence Benchmark do AuxFlow, tabela 3)** em
  `data_splits/hsb.csv`, versionado e fora de `data/`, transcrito por Victor
  do PDF (2026-09-30). São 10 clipes com o intervalo de frames e o LocSim@5 do
  NBJW na tabela 3:

  | clipe | início | fim | LocSim@5 do NBJW |
  |---|---|---|---|
  | SNGS-117 | 350 | 500 | 0,2784 |
  | SNGS-123 | 100 | 200 | 0,3793 |
  | SNGS-124 | 250 | 320 | 0,6801 |
  | SNGS-128 | 90 | 0 | 0,1578 |
  | SNGS-136 | 60 | 280 | 0,4573 |
  | SNGS-138 | 130 | 230 | 0,4246 |
  | SNGS-150 | 150 | 280 | 0,4462 |
  | SNGS-187 | 300 | 400 | 0,5946 |
  | SNGS-191 | 450 | 500 | 0,1302 |
  | SNGS-193 | 550 | 650 | 0,7025 |

  - **SNGS-128:** o artigo traz "90–0", e o arquivo guarda o valor do artigo.
    Lê-se como o intervalo 0–90, propagado de trás para frente a partir do
    frame 90.
  - **Numeração (suposição):** o artigo não diz se os frames contam a partir
    de 0 ou de 1, e as nossas imagens começam em `000001.jpg`. Adota-se a
    contagem a partir de 0, como no código deles: o frame N do artigo é o
    arquivo `000(N+1).jpg`.
  - **Conferido sem calcular nenhuma métrica:** os 10 clipes estão na
    partição **test** do GSR, cada um com 750 imagens, e todos os intervalos
    cabem (o maior vai até o frame 650 = `000651.jpg`).
  - O que se mede no HSB está no plano da Fatia 8 (`03-plano`, tabela T2).
- Liga suíça, poucos estádios: menos variedade visual que Copas do Mundo. Os
  parâmetros `[EMPÍRICO]` calibrados no WC14 podem não transferir — recalibre no
  treino do GSR e reporte os dois.

**Formato verificado (2026-09-25, clipe SNGS-070 do treino):** uma pasta por
clipe (`SNGS-XXX/`), com `img1/000001.jpg … 000750.jpg` (consecutivos) e
`Labels-GameState.json`:

- `info` — metadados do clipe (jogo, tempo de jogo, `frame_rate`, `seq_length`).
- `images` — um registro por frame, com `has_labeled_person`,
  `has_labeled_pitch`, `has_labeled_camera`.
- `annotations`, dois tipos:
  - **pessoas e bola** (`supercategory: object`; `category_id` 1 `player`,
    2 `goalkeeper`, 3 `referee`, 4 `ball`, 7 `other`) — `bbox_image` (px),
    `bbox_pitch` (metros: base esquerda, meio e direita da caixa projetadas no
    campo), `bbox_pitch_raw`, `track_id`, e `attributes` (papel, time, número);
  - **linhas do campo** (`supercategory: pitch`, uma por frame) — para cada uma
    das 26 classes visíveis, lista de pontos em coordenadas **normalizadas**
    (multiplicar `x` por 1920 e `y` por 1080).
- **Não há parâmetros de câmera no arquivo.** A categoria `camera` existe, mas sem
  nenhuma anotação. **A `H_gt` principal de cada frame é o ajuste ponto-linha às
  linhas anotadas** (`least_squares` com perda `soft_l1`, em todos os frames):
  acerta a geometria pintada. Para comparar com o AuxFlow há também a
  `H_gt_auxflow`, RANSAC (3 px) sobre as bases-meio das pessoas ↔ `bbox_pitch` —
  a leitura de "RANSAC over all annotated correspondences" (seção 4.1) que
  reproduz a mediana e a distância da tabela 2 deles (ver `decisoes.md`). O
  `bbox_pitch` das pessoas vem da **calibração do próprio dataset**: a DLT sobre
  as pessoas (sem a bola) só recupera essa calibração, que erra do lado da câmera
  (14 clipes) e no SNGS-023 197–523. Ela vira **início do ajuste e conferência**
  (discordância por frame no `gsr_gt_quality.csv`). Algumas pessoas vêm com
  `bbox_pitch` nulo (9 anotações no SNGS-070) e ficam fora.
- **Qualidade do gabarito:** frame cujo ajuste não é bem determinado (jacobiano
  sem posto 8, condição > 3000, ou resíduo mediano > 10 px) fica **sem `H_gt`** e
  é contado — nada de `H` inventada. Frame com resíduo mediano em (5, 10] px é
  **"gabarito duvidoso"**: o ajuste está certo, mas uma homografia pura só
  aproxima o campo (distorção de lente); as métricas saem com e sem eles.
  Os números antigos (DLT pelas pessoas; SNGS-070 com 2,8 px e 7 duvidosos) estão
  em `decisoes.md`.
- **Cache:** o ajuste em 123 mil frames não é de graça; o resultado fica em
  `outputs/cache/` (fora do Git).

**Partições:** calibrar no **treino**, escolher variantes na **validação**,
medir uma vez no **teste**. As comparações com o AuxFlow usam o teste (tabelas 5
e 7) e o HSB, que é um subconjunto do teste.

---

## TS-WorldCup — fora (volta só se for consecutivo)

**3.812 imagens de campo, de 43 vídeos** das Copas de 2014 e 2018: **2.925 de
treino e 887 de teste**. Download:
`cgv.cs.nthu.edu.tw/KpSFR_data/TS-WorldCup.zip`.

- O artigo do KpSFR avalia com molde de campo de **100 × 60 m**.
- **Não documentado:** o espaçamento temporal entre imagens consecutivas. Com ~88
  imagens por vídeo, é provável que sejam frames amostrados, não consecutivos —
  o que inviabiliza o Lucas–Kanade (o AuxFlow mediu até ~30 px entre frames
  consecutivos a 25 fps). Se houver tempo, medir o deslocamento entre imagens
  vizinhas com o gabarito decide se ele volta.
- Sem posições de jogador.

---

## CARWC — fora

Claasen & de Villiers (*Video-based sequential Bayesian homography estimation
for soccer field registration*, Expert Systems with Applications, 2024, seção
4.2.3) refinaram as anotações de homografia do WC14 e do TS-WorldCup e
consolidaram os dois no **CARWC** (*consolidated and refined WorldCup*). A
ferramenta de refinamento está em `github.com/Paulkie99/KeypointAnnotator`.

Não usado: números sobre ele não são comparáveis aos publicados sobre o WC14
original, e com o GSR no papel temporal o ganho do TSWC refinado some. Pode
entrar como verificação de robustez ao ruído do gabarito, se sobrar tempo.

---

## SN-Calib — opcional, só se sobrar tempo

SoccerNet-Calibration: cerca de 20 mil imagens (20.028 na versão de 2022,
segundo Maglo et al.; 22.816 na de 2023, segundo o PnLCalib), extraídas dos
jogos do SoccerNet, com anotação de todos os segmentos do campo — linhas,
segmentos de círculo e traves — em formato de polilinha, com pelo menos duas
posições por segmento visível.

Cobre **muito mais tipos de câmera** que o WC14: atrás do gol, dentro do gol,
laterais, spider cam. É por isso que fica fora do escopo — este projeto trata
apenas da câmera principal, e o SN-Calib puniria o pipeline por casos que ele não
se propõe a resolver.

Se sobrar tempo, use-o para uma **análise de limites**: em que tipos de câmera o
pipeline clássico degrada, e por quê. Isso é boa seção de discussão.

---

## Formato interno

Todo loader devolve:

```python
Sample(
    image_id: str,
    image: np.ndarray,      # BGR
    H_gt: np.ndarray,       # 3x3, campo -> imagem, metros -> pixels
    sequence_id: str | None # None para WC14; id do clipe no GSR
    frame_idx: int | None   # None para WC14
)
```

No WC14, o loader também expõe a máscara `grass` (gabarito da Etapa 1). No GSR,
`H_gt` é o ajuste pelas linhas (ou `None`), e o loader expõe também a `H` pelas
pessoas e a discordância entre as duas, as posições de atleta do frame (campo,
metros), as caixas (imagem, pixels), os pontos das linhas anotadas (imagem,
pixels) e a marca de "gabarito duvidoso" — as caixas servem para excluir jogadores da amostragem de pontos auxiliares
(Etapa 8c) e para o LocSim; as linhas permitem avaliar as Etapas 3 a 5
isoladamente.

**Convenções de homografia:** ambas verificadas (ver `decisoes.md`). Mantenha os
testes que as verificam — projetar o molde com `H_gt` e conferir que cai sobre as
marcações — porque um loader novo ou uma refatoração pode quebrá-las em silêncio.

---

## Código e dados de referência

Não são datasets de treino, mas poupam tempo e dão comparabilidade.

**Código de avaliação.** No WC14, use também o código público do Chu et al.
(`github.com/ericsujw/KpSFR`) sem modificação — foi o que Maglo et al. usaram. No
GSR, o `sn-gamestate` traz a avaliação GS-HOTA / LocSim, e o código de avaliação
do SN-Calib (`github.com/SoccerNet/sn-calibration`) define a acurácia a 5, 10 e
20 px contra as linhas anotadas.

**Bassek et al. (2025)** liberaram o código de análise estatística, estimativa de
visibilidade e detecção de formação em
`github.com/spoho-datascience/broadcast-analytics`. Os dados brutos de tracking e
vídeo não são públicos por licença; o material suplementar traz os dados
intermediários pré-processados das análises deles. São de outras partidas, sem
imagens — servem para imitar o procedimento de visibilidade, não para cruzar com
o GSR.

**TVCalib** — o pipeline de registro que eles usaram está em
`mm4spa.github.io/tvcalib`. Serve como a linha de base "aprendida" contra a qual
reportar seus números. O PnLCalib e o BroadTrack também publicam resultados
contra ele, então os três pontos de comparação já existem na literatura.

As bibliotecas que eles usam valem imitar: `shapely` para os polígonos de campo
de visão, `scipy` para otimização.

---

## Armadilhas registradas

- **Sentido da homografia** invertido entre convenções. No WC14, o arquivo é
  imagem → molde; o interno é campo → imagem.
- **Unidades do modelo de campo** — metros vs. jardas vs. normalizado. O WC14 está
  em jardas (115 × 74), que não é exatamente 105 × 68 m: converter por afim por
  eixo, não por um fator único de 0,9144. As linhas do GSR vêm normalizadas
  (0–1).
- **GSR sem câmera** — não procure parâmetros de câmera no JSON; a `H_gt` vem do
  ajuste às linhas anotadas. O `bbox_pitch` vem da calibração do dataset: a DLT
  pelas pessoas herda os erros dela, então serve de conferência, não de
  gabarito.
- **A bola não é correspondência de chão.** Quando está no ar, a base da caixa
  dela não toca o gramado; incluí-la na estimativa da `H_gt` criou um falso
  "corte" de ~104 px no SNGS-070. Vale também para qualquer uso futuro de caixas
  como pontos no plano (Etapa 8c, LocSim).
- **Rótulos de classe trocados nas linhas do GSR** (ex.: o círculo central
  anotado como `Circle right` no SNGS-149), às vezes só num trecho do clipe.
  Corrigidos na leitura por `gsr_label_fixes`; a varredura que os acha está no
  `--gsr-quality` (`gsr_gt_classes.csv`). Nem toda classe com erro alto é rótulo:
  a `H` pelas pessoas erra do lado da câmera, e há anotação congelada
  (SNGS-153, descartada em 479–750).
- **Traves e travessão também não estão no plano.** As classes `Goal …` das
  linhas anotadas do GSR ficam fora de qualquer ajuste ou erro medido no
  gramado.
- **Reta com uma ponta atrás da câmera.** Projetar só as duas pontas de uma
  linha e ligá-las na imagem dá um segmento absurdo quando uma delas tem
  `w ≤ 0`: no SNGS-070, a `Side line bottom` saiu a ~1.800 px das marcações em
  64 frames. Amostre toda polilinha densamente em metros e descarte as amostras
  com `w ≤ 0` antes de ligar.
- **`100_seg_pred.mat` no WC14** não é gabarito. Um `glob("*.mat")` o
  misturaria às máscaras.
- **Molde de campo na avaliação** — 105 × 68 m (interno, GSR), 115 × 74 jardas
  (PnLCalib no WC14/TSWC), 100 × 60 m (KpSFR, Maglo). O `IoU_whole` e o erro em
  metros mudam com o molde. Declare o molde em cada tabela.
- **Dimensões do campo** — o modelo padrão é 105 × 68 m, mas campos reais variam.
  Os gabaritos assumem o padrão; não tente "corrigir".
- **Resolução das imagens** difere entre WC14 (1280×720) e GSR (1920×1080). Toda
  constante em pixels precisa escalar com a resolução, ou ser definida em fração
  da altura da imagem.
- **Gabarito do GSR não é perfeito** — há frames em que ele discorda das linhas
  anotadas. Não meça estabilidade temporal contra ele (ver `01-metodo.md`).
- **Sombra atravessando o campo** parte a máscara de gramado em dois componentes.
  O "maior componente conexo" da Etapa 1 então descarta metade do campo. É a
  falha mais comum; trate explicitamente.
- **Padrão de corte da grama** gera faixas de luminância alternadas que o realce
  de marcações pode confundir com linhas.
