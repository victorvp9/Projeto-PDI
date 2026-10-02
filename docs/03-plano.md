# 03 — Plano de implementação

Oito fatias verticais. Cada uma entrega algo executável e testável. Como na outra
disciplina, **a avaliação vem antes do método**: sem métrica, ajustar um limiar de
Hough é chute.

Prazo: 8 semanas, com o trabalho dimensionado para 6.

Dados: **WC14 original** (frame a frame) e **SoccerNet-GSR** (temporal). Ver
`02-dados.md` e `decisoes.md`.

---

### Semana 0 — Antes de programar
- [x] Docs corrigidos contra os artigos (2026-09-25).
- [x] Dados decididos: WC14 original + SoccerNet-GSR (2026-09-25).
- [x] Molde e código de avaliação decididos (2026-09-25).
- [x] Download: WC14 e GSR (treino). GSR sem NDA, via Hugging Face.
- [x] Convenção do WC14 verificada (imagem → jardas 115 × 74; 3 imagens).
- [x] GSR verificado no SNGS-070: não há parâmetros de câmera; `H_gt` derivada
  das pessoas (sem a bola) e conferida contra as linhas anotadas (2,8 px);
  frames consecutivos a 25 fps, 1920×1080; sem cortes no clipe.
- [x] Download completo (2026-09-25): WC14 `train_val` (209) e `test` (186);
  GSR `train` (57), `valid` (58), `test` (49). Layout em `02-dados.md`.
- [x] Repositório: `CLAUDE.md`, `README.md` e `.gitignore` na raiz; docs
  revisados em `docs/`.
- [x] Remover as cópias antigas `docs/CLAUDE.md` e `docs/README.md` (passo 0 da
  Fatia 1).

### Fatia 1 — Modelo do campo e carregamento (semana 1)
Constantes regulamentares do campo, loaders do WC14 e do GSR, convenção de
homografia, renderizador sintético.

**Passo 0:** `uv init` com `opencv-python`, `numpy`, `scipy`, `pyyaml`,
`matplotlib` e `pytest`. Caminhos dos dados em `config.yaml`, abertos com
`pathlib` (o ambiente é Windows).

**Módulos**
- `src/pitch_model.py` — as constantes do modelo e cada elemento do campo como
  **polilinha em metros**, toda ela amostrada a cada 0,25 m — **inclusive as
  retas**. Ao projetar, amostras com `w ≤ 0` (atrás da câmera) são descartadas;
  uma reta guardada só com as duas pontas vira um segmento absurdo quando uma
  delas cai atrás da câmera (ver `02-dados.md`). Uma representação só serve
  para desenhar, renderizar e medir distância.
- `src/io/wc14.py` — lê `N.jpg`, `N.homographyMatrix` e `N_grass_gt.mat`
  (variável `grass`) pelo nome exato, sem pegar `*_seg_pred.mat`. Converte com
  `H_gt = inv(H_arquivo) @ A` (ver `decisoes.md`).
- `src/io/gsr.py` — lê o `Labels-GameState.json` de um clipe. Para cada frame,
  estima a `H_gt` por DLT (`cv2.findHomography(src, dst, 0)`) sobre as pessoas
  (`category_id` 1, 2, 3 e 7). Os pontos `bottom_left`/`middle`/`right` do
  `bbox_pitch` correspondem, na base da `bbox_image`, a `(x, y+h)`,
  `(x+w/2, y+h)` e `(x+w, y+h)`. Pessoas com `bbox_pitch` nulo ficam fora.
  Frame com menos de 4 pessoas fica com
  `H_gt = None` e é contado no resumo. O caso apareceu (2.322 frames, ver
  `decisoes.md`). **Superado na Fatia 2:** a `H_gt` do GSR passa a ser o ajuste
  pelas linhas em todos os frames, e a DLT pelas pessoas vira conferência.
- **Linhas anotadas do GSR:** coordenadas normalizadas × (1920, 1080). Mapear
  cada classe do JSON para a polilinha correspondente do modelo; **as classes
  `Goal …` ficam fora**, porque não estão no plano. Registrar o mapeamento em
  `decisoes.md`.
- **Erro contra as linhas:** para cada ponto anotado a mais de 2 px da borda,
  a distância à polilinha do modelo projetada pela `H_gt`; o erro do frame é a
  mediana dessas distâncias. Mediana > 10 px marca o frame como **gabarito
  duvidoso**.
- `src/render.py` — imagem sintética: fundo verde uniforme e polilinhas brancas
  de espessura realista, para uma `H` dada. Vem antes da hora porque custa pouco
  e dá dados de teste com gabarito exato desde o primeiro dia.
- `src/run.py`:
  - `--overlay wc14:<split>/<N>` e `--overlay gsr:<split>/<clipe>/<frame>`
    salvam o modelo desenhado sobre a imagem em `outputs/debug/`. Se isso não
    ficar perfeito, nada adiante vai funcionar.
  - `--gsr-quality` gera `outputs/gsr_gt_quality.csv`, com uma linha por clipe:
    frames, frames sem `H_gt`, frames duvidosos, mediana e p90 do erro; e
    `outputs/gsr_gt_classes.csv`, por clipe × classe, com a marca de rótulo
    suspeito. Roda nas três partições: é controle de qualidade do gabarito, não
    ajuste, então usar o teste não contamina nada.
- **Rótulos trocados** nas linhas anotadas do GSR: corrigidos na leitura por
  `gsr_label_fixes` (config), com a evidência em `decisoes.md`.

**Testes**
- As bandeirinhas ficam em `(±52.5, ±34)`.
- **WC14, conversão:** a `H_gt` aplicada a `(±52.5, ±34)` cai nos mesmos pixels
  que `inv(H_arquivo)` aplicada aos cantos do molde em jardas, de `(0, 0)` a
  `(115, 74)`. É o teste de `A`.
- **WC14, cobertura:** a fração do campo projetado com a `H_gt` que cai sobre a
  máscara `grass` é ≥ 0,99 em **todas** as 209 imagens de `train_val`; o IoU
  entre os dois é só número informativo (mediana e mínimo no log), porque a
  `grass` inclui o gramado fora das linhas (ver `decisoes.md`). Projete com
  `cv2.warpPerspective` a partir de uma máscara em vista de cima, e não com
  `fillPoly` sobre os quatro cantos projetados: se um canto cair atrás da
  câmera, o polígono se inverte. Este teste é cego a espelhamento e a uma `H`
  que encolhe o campo; quem protege a convenção é o teste de `A` e os overlays.
- **GSR, SNGS-070** (valores de referência em `decisoes.md`, frames numerados
  pelo nome do arquivo): a mediana, sobre os frames, do erro por frame fica em
  2,8 ± 0,3 px, e ≤ 5 px só com os frames não duvidosos. Os duvidosos devem ser
  de 5 a 10, incluindo o bloco 354–359 inteiro (referência: 354–359 e 365). Se o
  resultado ficar muito longe disso, pare e investigue antes de seguir.
- **GSR, bola:** acrescente às anotações uma bola com `bbox_pitch` absurdo e
  verifique que a `H_gt` não muda.
- **Sintético:** renderize com uma `H` conhecida e confira que os pixels das
  bandeirinhas projetadas são brancos.

**Saídas**
- `outputs/debug/`: overlays de 3 imagens do WC14 e dos frames 418–424 do
  SNGS-070 (o trecho da bola no ar).
- `outputs/gsr_gt_quality.csv` e `outputs/gsr_gt_classes.csv`.

### Fatia 2 — Avaliação (semana 1)
`IoU_whole`, `IoU_part`, erro de reprojeção, taxa de cobertura; LocSim no GSR.

**Primeiro: `H_gt` do GSR pelas linhas anotadas, em todos os frames** (ver
`decisoes.md`).
- Ajuste ponto-linha (`scipy.optimize.least_squares`, perda `soft_l1` com
  `f_scale` 3 px, por causa de anotações ruins): minimizar a distância dos pontos
  anotados às linhas do modelo projetadas pela `H` (objetivo liso: reta infinita;
  círculo por polilinha densa e depois refino por Sampson à cônica; resíduo
  reportado nas polilinhas). É **a mesma função** do refinamento da Etapa 7:
  escreva uma vez só, em `src/homography.py`, e a Fatia 5 reaproveita.
- **Início:** a `H` pelas pessoas; se não houver ou o ajuste for recusado, a
  última `H` aceita (encadeamento; a distância até um frame com pessoas chega a
  374 frames).
- **Tabela à parte, "protocolo AuxFlow":** `H_gt_auxflow` = RANSAC (3 px) nas
  bases-meio das pessoas; IoU/NPE/RE contra ela só para comparar com a tabela 7
  do AuxFlow. LocSim é a métrica da comparação central.
- **Aceite só se bem determinado:** posto 8, condição ≤ 3000 e resíduo mediano
  ≤ 10 px (calibrados no treino). Frame não determinado fica **sem `H_gt`** e é
  contado no resumo. Nada de `H` inventada.
- **"Gabarito duvidoso"** passa a ser: resíduo mediano do ajuste em (5, 10] px.
- **Conferência:** a `H` pelas pessoas continua calculada; a discordância das
  duas por frame (deslocamento mediano numa grade da imagem) vira coluna no
  `gsr_gt_quality.csv`.
- **Cache** em `outputs/cache/` (no `.gitignore`).
- **Testes:** no SNGS-070, deixar-uma-classe-fora — o ajuste sem a classe prevê
  a classe melhor que a `H` pelas pessoas (a discordância das duas na grade,
  ~11 px, é só reportada: lado da câmera); no SNGS-023, frame 230, o ajuste põe
  o círculo central sobre o pintado (conferir no overlay); com `H` sintética e
  pontos ruidosos, recupera a `H` com < 1 px; o encadeamento reproduz o ajuste
  iniciado pelas pessoas.

**Métricas no GSR:** `IoU` e erro de reprojeção contra essa `H_gt` (protocolo do
AuxFlow); LocSim contra o `bbox_pitch` (oficial, não depende da `H_gt`); e o erro
da `H` estimada contra os pontos anotados, com acurácia a 5, 10 e 20 px como no
SN-Calib — a medida que não depende de nenhuma `H_gt`.

- **Teste:** `H_gt` contra `H_gt` dá IoU = 1 e erro = 0.
- **Teste:** `H_gt` perturbada por translação conhecida degrada de forma monótona.
- **Teste:** para um mesmo par de homografias, os números batem com o código de
  avaliação de referência (KpSFR) quando se usa o mesmo molde.
- **Saída:** tabela de métricas a partir de um arquivo de homografias preditas,
  com e sem os frames de gabarito duvidoso, e com a contagem de frames sem
  `H_gt`.

### Fatia 3 — Gramado e marcações (semana 2)
Etapas 1 e 2 do método.

Tamanhos em fração da altura da imagem; os que dependem da largura da linha são
função da linha da imagem, `w(v) = a + b·v/h`, ajustada às larguras projetadas
pela `H_gt` do treino (regra geral: no pipeline não há `H_gt`, e a largura real
depende do zoom).

- **Gramado** (`src/segment.py`): HSV (pico de matiz por quadro) × Lab (pico em
  a\*, b\*; L\* fora do critério). `cv2.kmeans` em Lab, K = 3, gramado = grupo
  do pico, **só se HSV e Lab ficarem fracos no subconjunto com sombra**.
  Ablação: limiar → abertura → fechamento → maior componente (ou componentes
  com área ≥ `f_min`) → preencher buracos; um passo fica se o IoU médio no WC14
  treino sobe ≥ 0,005, ou o do subconjunto com sombra sobe ≥ 0,02, sem o outro
  cair mais de 0,002.
  - **Métricas:** WC14 — IoU contra `grass` (média e mediana, 209 imagens).
    GSR (1 frame a cada 25 do treino) — fração do campo projetado pela `H_gt`
    classificada como grama (reportada, sem limiar; jogadores e linhas a
    baixam) e **vazamento**: fração da máscara a mais de `m` metros fora das
    linhas pela `H_gt`, com `m` = p99 da distância além das linhas da `grass`
    do WC14.
- **Marcações:** top-hat branco × filtro de linha, sobre L\*, dentro do gramado
  dilatado, com escala `k·w(v)` e limiar de contraste varrido.
  - **Métricas:** WC14 — alvo = polilinhas do modelo desenhadas pela `H_gt`
    (1 px) dentro da `grass`: cobertura e precisão a γ = 2, 3, 5 px. GSR —
    cobertura = fração dos pontos anotados a ≤ 2 px da máscara; precisão a
    γ = 3 px contra as linhas desenhadas pela `H_gt` (a lente desloca as
    linhas alguns px nas bordas dos planos abertos). Cobertura também por faixa
    de largura projetada `w` (medida pela `H_gt`, só para análise).
  - **Decisão top-hat × filtro:** cada um no limiar de F1 máximo a γ = 3 px no
    WC14 treino, conferido pela cobertura no GSR treino. Se os frames de linha
    larga (zoom) ficarem muito abaixo, top-hat em 2–3 escalas (máximo delas)
    entra como variante na mesma varredura.
- **Sombra:** subconjunto por bimodalidade do L\* dentro do gramado (Otsu:
  `ΔL` entre as classes e fração `f_esc` do maior componente escuro ≥ 0,10),
  com `ΔL_min` fixado por folha de contato e confirmado por Victor; lista no
  config (por imagem no WC14, por clipe no GSR). Todas as métricas também nele
  e no complemento.
- **Partições:** ajuste e escolha de variante só no treino (WC14 `train_val`,
  GSR `train`). Medição única, ao fim da fatia, **só na GSR `valid`**. **O WC14
  `test` fica intocado até a rodada final (Fatia 8)**: sem validação no WC14,
  o test é o único número limpo dele, e a Fatia 7 ainda pode recalibrar a
  segmentação.
- **Testes:** sintéticos (gramado com e sem meia sombra; marcações; pontuação
  de sombra) e de regressão com dados (IoU no WC14 treino e cobertura no GSR
  treino ≥ valor calibrado − 0,01, fixados com aprovação).
- **Saídas:** `outputs/segment_wc14.csv`, `outputs/segment_gsr.csv`, tabelas
  da varredura e da ablação, curvas precisão × cobertura, e
  `outputs/debug/segment/` (melhores, piores e com sombra).
- **Fechada (2026-09-27), com duas limitações documentadas** (detalhe em
  `decisoes.md`): (1) **sombra azulada e sem croma** (GSR valid, jogo 3, de
  dia): o gramado cobre ~52% do campo nesse jogo; a histerese recuperaria até
  ~72%, mas piorou o jogo 5 além do ruído e ficou de fora. (2) **Contraste
  das linhas por jogo contra um limiar global**: nos jogos de contraste baixo
  (treino 4; valid 2 e 5) a cobertura fica em 0,59–0,67 contra 0,88 nos de
  contraste alto; o limiar relativo sobe a cobertura em ~0,11–0,12, mas perdeu
  precisão no jogo 2 além do ruído. As duas afetam a Fatia 4 (menos linhas
  detectadas nesses jogos) e voltam na análise de erro da Fatia 8. A GSR
  `valid` foi usada para escolher variante: **o número limpo do GSR é o do
  `test`, na Fatia 8.**

### Fatia 4 — Linhas e cônicas (semana 3)
Etapas 3 e 4. Plano aprovado por Victor em 2026-09-28, com os ajustes dele
(`decisoes.md`). Entrada fixa: a máscara de marcações da Fatia 3 (config atual),
sem recalibrar nada dela.

- **Tolerâncias em pixels como fração da altura** (convenção da Fatia 3): o
  casamento a "3 px" é 3/720 da altura (3 px no WC14, 4,5 px no GSR); a mesma
  regra vale para td, G e os limiares das elipses. Com pixels fixos, o GSR
  ficaria 1,5× mais apertado e as linhas curvadas pela lente na borda deixariam
  de casar.
- **Parâmetros comuns às duas bases**, separados por base só se os ótimos
  diferirem além do ruído (como o limiar das marcações na Fatia 3).
- **1. Falsos positivos da máscara, antes de filtrar** (precisão ~0,5 na Fatia
  3): falso positivo = pixel da máscara a mais de 3/720·h da linha com largura
  da `H_gt`. Amostra de 100 pixels sorteados uniformemente (semente fixa) no
  WC14 `train_val` e 100 no GSR `train` (1 frame a cada 25); estimativa
  ponderada por pixel, erro-padrão ~5 p.p. Folhas de contato (contexto, recorte
  cru, recorte com a máscara) classificadas por mim e auditadas por Victor, em:
  pessoa (jogador, árbitro, staff, fotógrafo); bola; trave, rede ou
  bandeirinha; publicidade pintada no gramado; textura ou faixa de corte da
  grama; linha do modelo desalinhada (erro da `H_gt` ou lente: não é falso
  positivo de verdade); marca não modelada (pênalti, tracejados, área
  técnica); fora do campo (placas, torcida, bancos, equipamento); grafismo da
  transmissão; outros (`outputs/lines_fp_classes.csv`). Forma do
  componente da máscara que contém o pixel (área, alongamento pelos momentos,
  espessura em larguras de linha) no CSV. **Parada:** tabela por categoria e
  base.
- **2. Filtro de forma (condicional):** tirar da máscara os componentes
  compactos. Só entra se melhorar o F1 de segmentos (item 5) no treino além do
  ruído (0,01) sem perder recall de linhas além do ruído — o Hough com
  comprimento mínimo já é um filtro de forma.
- **3. Etapa 3:** **sem afinamento** de início; se a ablação pedir, esqueleto
  morfológico com erode/dilate do OpenCV. `HoughLinesP` (ρ 1 px, θ 0,5°; votos,
  comprimento mínimo e vão `[EMPÍRICO]`, em fração da altura). **Fusão de
  colineares** por union-find: Δθ ≤ tθ, extremos de um a ≤ td da reta do outro
  (td em larguras de linha w(v): ao longe as paralelas ficam próximas) e vão ao
  longo da reta ≤ G (as linhas de cima das duas grandes áreas são colineares no
  campo). Reajuste por mínimos quadrados totais nos pixels do grupo, extremos
  pelas projeções; repetir até estabilizar.
- **4. Etapa 4:** pixels da máscara a mais de td das retas aceitas; RANSAC de
  cônica (5 pontos de até dois componentes curvos; consenso por distância de
  Sampson ≤ τ) e reajuste com `cv2.fitEllipse`; aceite por arco ≥ S e razão de
  eixos plausível; até 2 elipses por quadro. O centro da elipse não vira
  correspondência (nota do método).
- **5. Gabarito e métricas:** polilinhas do modelo projetadas pela `H_gt`
  (as duas bases), recortadas à imagem e ao gramado; visível = comprimento
  projetado ≥ Lmin. Segmento casa com a classe c se ≥ 80% dos seus pontos estão
  a ≤ 3/720·h da polilinha de c. Recall de linhas (≥ 1 segmento casado) e por
  comprimento; precisão por comprimento; fragmentação (segmentos por linha
  casada, alvo 1); erros angular e de distância. Elipses: recall do círculo
  central com ≥ 50% do arco visível, e precisão. No GSR, distância mediana dos
  pontos anotados ao segmento casado da mesma classe. GSR por jogo.
- **6. Calibração das retas só no GSR train** (decisão de Victor, depois da
  classificação dos falsos positivos): o gabarito do WC14 está deslocado 5–8 px
  em trechos, e o do GSR (ajuste pelas linhas) tem resíduo de ~0,5 px. O WC14
  vira verificação, a 3 px e a 8 px (p75 do deslocamento; declarado
  conservador); se a escolhida no GSR ficar muito abaixo da melhor do WC14 a
  8 px, discutir. Grade modesta: F1 entre recall e
  precisão por comprimento, média das duas bases, fragmentação como desempate;
  ablação (fusão, filtro de forma, afinamento se entrar) exige +0,01 de F1 ou
  menos fragmentação. **O número que decide é o erro da homografia na Fatia 5:**
  com métricas de segmentos razoáveis, sem rodadas extras aqui. **Parada:**
  tabelas antes de fixar os testes de regressão.
- **7. Partições:** ajuste e escolha só no treino; uma medição no fim na GSR
  `valid`, só relatório; WC14 `test` e GSR `test` intocados até a Fatia 8.
- **Testes:** sintéticos (plano fechado e aberto: cada linha visível ≥ Lmin
  sai como um segmento a ≤ 1 px e ≤ 0,5° da projeção, nenhum a mais; círculo
  central a ≤ 1 px da elipse); unitários da fusão (reta quebrada com vãos vira
  um segmento; paralelas a mais de td e colineares com vão > G não se fundem);
  com dados (`skipif`), limites fixados com aprovação (folga 0,003 no WC14, 0,01
  no GSR).
- **Saídas:** `outputs/debug/lines/` (segmentos por grupo, elipses, folhas dos
  falsos positivos); `outputs/lines_fp_*.csv`, `lines_sweep*.csv`,
  `lines_wc14.csv`, `lines_gsr_<split>.csv`; `--lines-fp-sheet`,
  `--lines-sweep`, `--lines-eval`. Código em `src/lines.py`, `src/conics.py`,
  métricas em `src/evaluate.py`, varredura em `src/sweep_lines.py`.
- **Riscos:** lente no GSR (linhas longas curvas: fragmentação ou fusão errada);
  paralelas próximas ao longe; recall menor nos jogos das limitações da Fatia 3
  (jogo 3; contraste baixo), por isso o relatório por jogo.

### Fatia 5 — Classificação e homografia (semana 4)
Etapas 5, 6 e 7. É a semana mais difícil. Plano aprovado por Victor em 2026-09-28,
com os ajustes dele (`decisoes.md`).

- **Ordem:** primeiro um pipeline mínimo de ponta a ponta (hipóteses →
  verificação → refinamento), sem calibrar nada, num subconjunto do GSR train;
  trazer o primeiro NPE, a cobertura, o número de hipóteses e o tempo por frame
  antes de qualquer varredura.
- **Classificação (Etapa 5) por hipótese e verificação:** duas famílias de
  segmentos pelo ponto de fuga (sem as cordas marcadas); 2 retas de cada família
  (das mais longas) atribuídas a linhas do modelo da família respeitando a ordem;
  H pelo retângulo das 4 interseções; poda por plausibilidade; verificação pelo
  modelo inteiro projetado contra a máscara (apoio − penalidade por linha
  projetada sobre gramado sem marca). A melhor dá a H₀ e as classes. Friso das
  placas de LED: segmento com não-gramado logo acima não pode ser a lateral do
  fundo.
- **Simetria de 180°:** o modelo é invariante a (X, Y) → (−X, −Y), então H e
  H·R180 empatam; desempate pela convenção Y+ = lado da câmera (um ponto no pé
  da imagem cai em Y maior que um mais acima), e descarte das espelhadas pelo
  sinal do determinante. Teste unitário.
- **Caminho principal:** H₀ da melhor hipótese → `fit_point_line`. Refinamento
  com os pontos dos segmentos classificados **e**, como variante, com os pixels
  da máscara numa faixa em volta de todas as linhas do modelo projetadas pela H
  atual (recupera linhas que o Hough perdeu); ablação pelo NPE. Círculos pelo
  caminho guiado nos dois casos.
- **Correspondências (Etapa 6) + RANSAC viram ablação** ("com × sem"): p, pe
  (até 50% além da imagem) e p1 (linha do meio × círculo).
- **Aceite** pelo critério da `H_gt` (posto 8, condição ≤ 3000, resíduo ≤ 10 px);
  fora disso, falha de cobertura. Vistas com uma família só e meio-campo sem
  círculo: falha de cobertura é aceitável (alvo da Fatia 6), sem rodadas nelas.
- **Elipses conferidas depois da H:** a rejeitada devolve as cordas e o frame é
  reclassificado uma vez.
- **Avaliação:** predições em `.npz` para o `--evaluate` (estendido ao WC14);
  cobertura, NPE, `IoU_whole`, SN-Calib e LocSim no GSR, por jogo. Marco:
  detector sozinho no WC14 `train_val` e no GSR `train`; uma medição no fim na
  GSR `valid`, só relatório.
- **Resolvido (2026-09-28): td 6/720 e escala única**, pelo NPE mediano com a
  cobertura dentro do ruído (`decisoes.md`). Os dois itens abaixo ficam como
  registro.
- **Decisão pendente da Fatia 3: marcações em escala única × multiescala "1+2".**
  A escala única ficou pelo F1 por pixel, que é só uma aproximação; a "1+2"
  recupera as linhas largas (WC14, 6–8 px: 0,32 → 0,57), que são as do lado da
  câmera, ao custo de F1 −0,024. Decidir aqui pelo erro da homografia (as duas
  estão no config: `line_scales`).
- **Decisão pendente da Fatia 4: td da fusão, 3/720 × 6/720 da altura.** A
  varredura escolheu 6/720 (fragmentação 1,56 → 1,17, mesmo F1), mas a
  fragmentação quase não custa depois da classificação, e uma linha perdida ou
  uma fusão de paralelas custa. Decidir aqui pelo erro da homografia
  (`lines.fuse_d_frac`). A conferência da Fatia 4 mostrou que as perdas de td
  6/720 não são fusões de paralelas: são retas únicas ajustadas sobre linhas
  curvadas pela lente; td 3/720 as deixa em pedaços que acompanham a curva.
- **Círculo pelo caminho guiado** (decisão de Victor): com a H inicial das
  retas, projetar o círculo central (e os arcos) e ajustar com os pixels da
  máscara perto dele — o termo de Sampson do `fit_point_line` já faz isso. A
  detecção às cegas da Fatia 4 (recall 0,74 no central, 0,20 nos arcos,
  precisão 0,67) só é indispensável no meio-campo, onde há poucas retas.
- **Segmentos marcados como corda** (decisão de Victor): a Fatia 4 não apaga as
  cordas; cada segmento sobre uma elipse aceita fica na lista com o id dela
  (`conics.chord_ids`). Aqui, por padrão, ficam fora das retas, mas **voltam se
  a elipse for rejeitada pela consistência com a homografia** — 1/3 das
  elipses é falso, e uma falsa encostada em retas marcaria uma reta de verdade
  (sintético: a lateral esquerda).
- **Risco (achado na Fatia 4):** no GSR, o friso claro da base das placas de
  LED é uma reta longa, paralela e logo além da lateral do fundo, e pode ser
  confundido com ela na classificação semântica. Ele entra na máscara porque o
  gramado é dilatado em uma largura de linha antes de restringir as marcações.
- **Teste:** na imagem sintética, a homografia recuperada bate com a usada para
  renderizar.
- **Marco:** primeiro número real no WC14, com taxa de cobertura, e o mesmo
  pipeline frame a frame no GSR (é o "detector sozinho" das ablações). Fim da
  primeira metade do projeto.

### Fatia 6 — Consistência temporal (semana 5)
Etapa 8, no GSR. É a contribuição do projeto. Plano aprovado por Victor em
2026-09-28, com os ajustes dele (`decisoes.md`).

- **0. Série do detector em todos os frames**, em cache por clipe
  (`outputs/cache/detector/`): H (ou NaN), termos da nota, margem, aceite.
  ~3 h por partição, uma vez; começa pelo subconjunto de 6 clipes do treino
  (SNGS-060, 070, 099, 109, 154, 164; 4.500 frames).
- **6a — Savitzky–Golay** (janela 31, grau 3, Bassek) sobre a série do detector;
  lacunas ≤ 25 frames por interpolação linear, as maiores cortam a série;
  comparar entradas da matriz (H[2,2] = 1) × pontos projetados com a H
  reestimada. Referência que 6c precisa superar.
- **6b — Detecção de corte:** diferença de histograma HSV (primária) + salto da H
  (auxiliar; sozinho é erro do detector); reinicia as séries; testada com cortes
  sintéticos (clipes emendados), limiar calibrado no treino.
- **6c — Propagação por Lucas–Kanade** a partir de âncoras, nos dois sentidos do
  tempo: grade do campo 2,5 × 2 m projetada pela âncora, sobre o gramado, **sem
  os componentes compactos de não-gramado** (jogadores, bola; mesmo filtro de
  forma da Fatia 4 — as linhas do campo ficam na grade: estáticas, borda
  forte); ida-e-volta ≤ 1 px; reestimativa com o `fit_point_line` (pontos
  propagados + pixels guiados das linhas). **A saída é a H propagada e
  reestimada**; a H do detector só entra na escolha e na verificação das
  âncoras (a nota não separa H certas de erradas aceitas).
- **Âncoras:** máximos locais da nota da Fatia 5 (IoU com o gramado + fração
  explicada), com **verificação temporal obrigatória** (a H da âncora, levada
  pelo movimento medido por Lucas–Kanade, concorda com a do detector nos
  vizinhos). Medir a fração de candidatas verificáveis; se for baixa, verificar
  também no encontro de âncoras consecutivas (a H propagada de A até B concorda
  com a de B).
- **Ablações:** detector sozinho × 6a × 6c com fluxo × 6c sem fluxo (H da âncora
  copiada); âncora ingênua a cada 150 frames; âncora de gabarito (`H_gt`, teto,
  tabela 4 do AuxFlow); opcional "sem linhas" (só pontos propagados na
  reestimativa: o 83,67 → 78,30 do AuxFlow). Kalman (8b) só se sobrar tempo.
- **Métricas:** LocSim@5 e mAP penalizados (principal), NPE, cobertura,
  `IoU_whole`, por jogo; estabilidade temporal medida na série estimada, nunca
  contra a `H_gt`.
- **Partições:** calibração só no GSR train; valid só relatório; test e HSB
  intocados até a Fatia 8.
- **Testes:** "tudo desligado" = Fatia 5; sintéticos (Lucas–Kanade propaga uma
  panorâmica/zoom conhecida; Savitzky–Golay reduz o tremor; corte sintético
  detectado); regressão depois da calibração.
- **Paradas:** série no subconjunto + tabela do 6a; calibração do corte; 6c de
  ponta a ponta no subconjunto; tabelas de calibração antes da regressão.
- **Risco principal (achado na Fatia 5): H erradas aceitas pelo detector** — a
  cauda do NPE médio (0,58 com mediana 0,0064 no GSR train), quase sempre uma
  troca de reta (grande × pequena área) ou o friso das placas tomado pela
  lateral. Na propagação, uma âncora errada espalha o erro para os vizinhos.
  Candidato: **verificação temporal da âncora**, rejeitando H inconsistente com o
  movimento medido por Lucas–Kanade em relação aos vizinhos (anotação de Victor).

### Fatia 7 — Estabilidade, visibilidade e sensibilidade (semana 6)
Plano aprovado por Victor em 2026-09-30 (`decisoes.md`). Roda sobre as séries em
cache (detector, 6a, 6c), sem mexer no detector congelado. O desenvolvimento usa o
train[::3], o relatório usa a `valid`, e o test fica intocado até a Fatia 8.

- **7a. Estabilidade** na série estimada, pela grade de pontos visíveis
  (alteração do `01-metodo`): tremor (segunda diferença) e deslize contra o
  movimento real da imagem, medido por ECC (independente do Lucas–Kanade do
  6c), com a taxa de convergência do ECC. Pares em que o ECC não converge ficam
  fora do deslize. Variantes: detector, 6a Bassek, 6a robusto, Kalman, 6c com e
  sem fluxo.
- **7b. Kalman de velocidade constante + RTS (simplificado)** — **não é o
  BHITK** do Bassek et al. É a terceira estratégia da pergunta 2 do
  `00-problema`. Roda na representação por pontos, com porta de Mahalanobis
  contra H erradas e predição nas lacunas. Uma rodada de calibração dos ruídos
  de processo e de medição no train[::3], com a regra fixada antes: maior
  LocSim@5 penalizado; empate a 0,01 pelo menor tremor mediano.
- **7c. Taxa de inversão de visibilidade** com `shapely`:
  - o polígono do campo de visão é a borda da imagem cortada no horizonte,
    levada ao campo e recortada no campo mais uma margem;
  - **medida principal:** jogadores reais do GSR, unilateral;
  - **complemento:** grade de 1 m no campo, nos dois sentidos;
  - duas versões, penalizada e só frames cobertos;
  - o indicador na linha do Bassek: frames em que o registro deixa 0 jogadores
    visíveis com pelo menos 1 no gabarito;
  - depuração em vista de cima (`outputs/debug/visibilidade/`).
- **7d. Sensibilidade descritiva, no lugar da calibração sistemática.** Os
  parâmetros já foram calibrados fatia a fatia, e recalibrar o detector
  refaria ~11 h de série por partição.
  - Um parâmetro de cada vez, a ±25% e ±50%.
  - Detector nos subconjuntos da regressão (GSR e WC14); parâmetros temporais
    no subconjunto de 6 clipes, só com a variante 6c com fluxo.
  - Resultado: gráficos de tornado, a tabela "importa / não importa" (|Δ| ≥
    0,01 de LocSim@5 ou de cobertura) e a auditoria das constantes do config
    ainda marcadas como "escolha".
  - **Ganho ≥ 0,02 de LocSim vira proposta para Victor, sem mudar nada.**
- **Paradas:**
  1. definições, testes sintéticos e primeiros números no subconjunto;
  2. calibração do Kalman;
  3. tabelas de sensibilidade;
  4. números da regressão.

### Fatia 8 — Rodada final e relatório (semanas 7-8)
Plano detalhado para revisão de Victor (2026-09-30). **Nada do test roda antes da
aprovação e do congelamento.**

#### 8.0 Antes do congelamento
- **Sensibilidade (7d): feita** (2026-10-01). Os candidatos foram confirmados
  num subconjunto maior, com intervalo por bootstrap (`decisoes.md`). Só o
  `segment.gsr.line_thr` 15 passou no critério, e **foi recusado por Victor**:
  o efeito tem sinal oposto entre os 3 jogos do train. Nenhum parâmetro mudou,
  e a série do detector, a do 6c e os números das Fatias 5 a 7 ficam como estão.
- **Pendências resolvidas antes do congelamento** (2026-10-01):
  - o LocSim@5 penalizado dava NaN quando nenhum frame tinha H; o `summarize`
    foi corrigido e a chave do 6c foi regravada com conferência. Os valores que
    não eram NaN ficaram idênticos;
  - `OPENBLAS_NUM_THREADS=1` nos trabalhadores: adotado só se as H saírem
    idênticas bit a bit com e sem a variável (`decisoes.md`).
- **HSB:** feito. Transcrito por Victor da tabela 3 do AuxFlow para
  `data_splits/hsb.csv` (`02-dados`). Os 10 clipes estão no test e os
  intervalos cabem; as suposições registradas são a leitura do SNGS-128 e a
  numeração a partir de 0.
- **Chave do cache da `H_gt` (`gsr._cache_key`): feita** (2026-10-01). Os 115
  caches do train e da valid foram recalculados e saíram idênticos em 86.250
  frames. O procedimento seguiu o da troca da chave do 6c:
  - hash dos bytes dos módulos lido na importação, conferido no trabalhador;
  - regravação da chave dos caches de gabarito do train e da valid, sem
    recalcular, só depois de conferir o código que os gerou;
  - a conferência exige as duas condições juntas: o `git diff` vazio contra a
    fotografia do código da rodada que gerou o cache **e** o hash guardado
    igual ao dos bytes atuais. O hash guardado é complemento, não prova: foi
    lido na hora da gravação, que é o próprio defeito;
  - se qualquer uma divergir, recalcula-se só esse cache, comparando frame a
    frame com o antigo.

  Não se mantém o defeito contando com uma rodada sem edições no meio.
- **Suíte completa verde e árvore limpa** no commit do congelamento.

#### 8.1 Congelamento
- **Registrar antes da rodada**, em `outputs/runs/congelamento.json` e no
  `decisoes.md`:
  - o hash do commit (`git rev-parse HEAD`, árvore limpa);
  - o SHA-1 do `config.yaml`;
  - as chaves de cache em vigor (série do detector, 6c, ECC).

  O executor confere essas chaves em cada tarefa.
- **Uma rodada só no test e no HSB.** Nenhum parâmetro muda depois de ver um
  número do test.
- **Se um defeito aparecer no meio:** corrigir, registrar e refazer o test
  inteiro, dizendo no relatório que houve uma segunda rodada e por quê. O
  número da primeira não é descartado em silêncio.

#### 8.2 Ordem e custo
1. Sensibilidade (em andamento) → decisão de Victor sobre as propostas.
2. Pendências do 8.0 → congelamento (8.1).
3. **Série do detector no GSR test** (49 clipes, ~7–8,5 h; checkpoint por
   clipe, pausável) e **detector no WC14 test** (186 imagens, frame a frame).
   Só começam depois do congelamento.
4. `H_gt` do GSR test (ajuste ponto-linha, em cache).
5. 6a (Bassek e robusto), Kalman + RTS e 6c no GSR test (~3–4 h com a GPU).
6. Estabilidade (ECC) e visibilidade no GSR test.
7. Tabelas (8.3), análise de falhas (8.6), `--all`.

#### 8.3 Tabelas do relatório (definidas antes; preenchidas só na rodada)
As séries das linhas são sempre as mesmas: detector, 6a Bassek, 6a robusto,
Kalman + RTS, 6c com fluxo, 6c sem linhas, 6c sem fluxo, âncora ingênua e âncora
de gabarito (teto).

| tabela | conteúdo | colunas |
|---|---|---|
| T1 | GSR test, 49 clipes | cobertura; NPE mediano (média); IoU_whole mediano; LocSim@5 penalizado; LocSim@5 nos cobertos; mAP-LocSim penalizado; **LocSim@5 penalizado só nos clipes com ≥ 1 âncora aceita**; fração da distância ao teto |
| T1b | GSR test, conjunto comum (frames com H do detector) | NPE mediano; LocSim@5 |
| T2 | HSB à parte: 10 clipes do test, intervalos de `data_splits/hsb.csv`; ver abaixo | LocSim@5 por frame (**média e mediana**), penalizado e só nos frames cobertos; cobertura |
| T3 | WC14 test, 186 imagens, só o detector (sem série temporal) | cobertura; IoU_whole; IoU_part; NPE; RE (média e mediana) |
| T3b | WC14 test no **protocolo KpSFR** (`src/eval_kpsfr.py` sem mudança, molde 100 × 60 m declarado) | as colunas do protocolo |
| T4 | Estabilidade e visibilidade no GSR test (detector, 6a Bassek, 6a robusto, Kalman, 6c com e sem fluxo) | tremor e deslize (mediana, p90; convergência e correlação do ECC); jogadores invertidos, grade e 0 visíveis (penalizada e só cobertos) |
| T4b | Idem, na interseção dos frames cobertos pelas cinco séries | as mesmas; nº de frames, trios e pares |
| T5 | Comparação com a tabela 7 do AuxFlow | linhas NBJW (0,885) e AuxFlow (0,929), nosso detector e nosso 6c; LocSim@5 deles; nosso penalizado, nos cobertos e no conjunto comum; ganho (6c − detector) ao lado de (AuxFlow − NBJW) |
| T6 | GSR test, por jogo | cobertura; LocSim@5 penalizado do detector e do 6c |
| T7 | Âncoras no test | candidatas; verificáveis; aceitas; erradas (NPE > 0,05); clipes sem âncora |
| T8 | Lacunas do detector no test (1–3, 4–25, > 25 frames, pontas) | cobertura e NPE mediano do 6a, do 6c e do 6c sem linhas |
| T9 | Custo, ao lado da tabela 6 do AuxFlow | perfil por etapa (detector 4,76 s por frame num núcleo no GSR e 2,90 s no WC14; 6c 127 ms por frame); vazão real da rodada do test com 15 processos; tempo por clipe de 750 frames; hardware de cada lado, com a ressalva de CPU contra GPU |

- **T2 (HSB), três medições nos mesmos frames** (decisão de Victor):
  1. **Só propagação:** o passo normal do 6c (pontos de Lucas–Kanade mais as
     linhas detectadas em cada frame), a partir da `H_gt_auxflow` no frame
     inicial do intervalo, **sem nenhuma âncora do detector**. No SNGS-128,
     parte do frame 90 e vai para trás até o 0.
     - É o análogo da tabela 4 do AuxFlow (pontos-chave + auxiliares): NBJW
       sozinho com 43,15% de média e 35,93% de mediana; AuxFlow com 83,67% e
       96,15%.
     - A H inicial é a `H_gt_auxflow` (RANSAC sobre as pessoas), a mesma das
       métricas comparáveis ao AuxFlow, e a tabela diz isso.
  2. **O nosso detector puro** nos mesmos frames, lado a lado com a coluna do
     NBJW da tabela 3 (`locsim5_nbjw`).
  3. **O pipeline completo:** o 6c com as nossas âncoras, rodado no **clipe
     inteiro**; só a avaliação fica restrita ao intervalo.
- **Ressalva obrigatória na T5:** o LocSim deles não tem frames sem H (os dois
  métodos devolvem H em todo frame). O nosso é penalizado (a pessoa de frame
  sem H vale 0), e boa parte do ganho vem da cobertura. Por isso, as colunas
  nos cobertos e no conjunto comum ficam ao lado.
- **Agregação, dita na T5:** o nosso LocSim é agregado sobre pessoas-frame.
  Agregar por frame quase não muda a média (conferência de 2026-09-25).
- **Incerteza** (decisão de Victor): T1, T5 e a fração da distância ao teto
  levam intervalo de 95% por bootstrap **sorteando jogos** (2.000
  reamostragens, semente fixa), porque clipes do mesmo jogo não são
  independentes (o caso do `line_thr`). A tabela diz o número de jogos do test.
  Com menos de 5 jogos, os números por jogo (T6) vão ao lado, em vez de
  confiar só no intervalo.
- **Comparação com o Bassek** (indicador de 0 visíveis): só ordem de grandeza,
  porque os dados e o sistema são diferentes.
- **T9, o lado do AuxFlow** (tabela 6 deles, transcrita por Victor): tempo por
  clipe de 750 frames, num i7-8700K com RTX 4090. O "lote" é o tamanho do lote
  na GPU ou o número de threads.

  | etapa | lote | tempo | FPS |
  |---|---|---|---|
  | NBJW keypoints | 8 | 54 s | 13,9 |
  | NBJW H estimation | 1 | 27 s | 27,8 |
  | U-Net initialization | 1 | 61 s | 12,3 |
  | Propagation | 1 | 150 s | 5 |
  | Overall | – | 292 s | 2,6 |

  Do nosso lado: o detector roda em CPU, em todo frame. Num núcleo, um clipe
  de 750 frames custa ~3.570 s no detector (4,76 s por frame) mais ~95 s no 6c
  (127 ms por frame, com GPU). A vazão real com 15 processos sai da rodada do
  test.

#### 8.4 Números de referência (calibração)
- **A referência são os 19 clipes do train[::3]**, o conjunto de calibração da
  Fatia 6. O subconjunto de 6 clipes serviu só para desenvolvimento e não entra
  nas comparações.
- **Nos 19 clipes:** LocSim@5 penalizado 0,364 (detector) → **0,708** (6c),
  teto 0,771. **Fração da distância fechada: (0,708 − 0,364) / (0,771 −
  0,364) ≈ 85%.**
- **No conjunto comum:** o 6c supera o detector também em NPE (0,0049 ×
  0,0052).
- **O ganho a comparar com o AuxFlow no test** é o do 6c sobre o nosso
  detector. Nos 19 clipes, +0,344 em LocSim@5 penalizado. O deles é +0,044
  sobre o NBJW, tabela 7.
- **Linhas:** pesam nas lacunas longas (+53% de NPE sem elas acima de 25
  frames; 1,8× nas pontas) e quase nada nas curtas. Como o nosso detector
  pisca, a maioria das lacunas é curta; isso explica a diferença em relação ao
  AuxFlow, onde tirar as linhas custa 5,4 pontos.

#### 8.5 "Sem âncora" × "propagação pior" (valid e test)
- Reportar o LocSim@5 penalizado completo e, ao lado, só nos clipes com ≥ 1
  âncora aceita (coluna da T1).
- **Na valid, já medido** (`decisoes.md`):

  | conjunto | detector | 6c | teto | fração da distância |
  |---|---|---|---|---|
  | 58 clipes | 0,173 | 0,436 | — | — |
  | 40 com âncora | 0,253 | 0,639 | 0,776 | 74% |
  | 18 sem âncora | 0,002 | sem H | — | — |

  Nos clipes sem âncora, o detector quase nunca acerta.

#### 8.6 Análise de falhas
- **Piores casos por clipe** (LocSim@5 do 6c e distância ao teto) e **por
  frame** (NPE e jogadores invertidos), com a causa de cada um e figuras (vista
  de cima dos campos de visão, sobreposição na imagem e a M = H_gt⁻¹·H_det das
  âncoras).
- **Categorias de causa:**
  1. âncora errada aceita, com o tipo:
     - troca de reta, como o SNGS-164 (171 e 187: grande área + linha do meio
       encaixadas como pequena área + grande área, com o círculo central tomado
       como o arco);
     - simetria de 180°;
     - friso da placa.
  2. clipe sem âncora: SNGS-060 e 066 no treino, os 18 da valid e os do test.
     Na valid, 13 dos 18 são do jogo 3 (diurno, sombra azulada, 62% dos clipes
     do jogo), 2 do jogo 2 e 3 do jogo 5 (contraste baixo). **A queda da valid
     se explica, na maior parte, pelas limitações de segmentação já conhecidas
     da Fatia 3.** Sem gramado e marcações confiáveis, o detector erra quase
     sempre (LocSim@5 0,002 nos 18 clipes), e a verificação não aceita âncora
     nenhuma.
     O detector erra de forma sistemática, e a verificação rejeita tudo.
  3. deriva da propagação em lacunas longas e nas pontas.
  4. gabarito duvidoso.

#### 8.7 Demais seções do relatório
- **Incidente da rodada do test** (2026-10-02, `decisoes.md`): a conferência de
  fechamento da série (`ex.verify_keys` em `src/temporal.py:93`) quebrou depois
  de a série terminar, porque a lambda usa `a[0]`, que é a tupla da tarefa, e não
  o clipe. Nada foi corrigido durante a rodada. A conferência foi feita por fora,
  com o mesmo critério: 735/735 chaves iguais à congelada. A rodada seguiu da
  etapa 2. Motivo: nenhum número do test tinha sido visto, o defeito está numa
  conferência e não no cálculo, e a etapa 2 prova bit a bit que as séries são as
  do código congelado. A correção vem depois da rodada, num commit separado, e
  não muda nenhuma saída.
- **Prova de determinismo entre rodadas** (2026-10-02, `conferencia_det.json` e
  campo `conferencia_serie` dos manifestos das etapas 1 e 2): nos 1.470 frames do
  GSR test a cada 25 (49 clipes), a H do detector rodado pelo `--detect` (etapa 2,
  outro processo e outra hora) saiu **bit a bit igual** à da série da etapa 1
  (`--detect-series`). O código congelado dá a mesma H em execuções independentes.
  É também a prova de que as séries do test são as do código congelado, apesar do
  incidente da conferência de fechamento.
- **Frames difíceis isolados.** Bassek et al. apontam que o efeito do
  pós-processamento temporal sobre frames com grande zoom nunca foi testado. O
  HSB (T2) reportado à parte é a lacuna declarada que este projeto pode
  fechar.
- **Qualidade do gabarito do GSR,** como seção curta: quantos frames discordam
  das linhas, e o caso da bola no ar como exemplo de correspondência falsa.
  - **Correções de rótulo** (`gsr_label_fixes`, Fatia 1): 7 clipes do test têm
    correção, e por isso uma chave própria da H de gabarito (SNGS-119, 121, 133,
    148, 149, 187, 199). Dizer no texto que essas correções vieram da varredura do
    gabarito, sem nenhuma saída do método, e que não afetam o LocSim (que usa as
    posições anotadas das pessoas), só o NPE e o IoU contra a `H_gt` das linhas.
- **Ablação de limitações da segmentação por cor:** a tabela da rodada das
  variantes da Fatia 3 na GSR `valid` (atual, histerese, limiar relativo e a
  combinação, por jogo; `outputs/segment_variantes_gsr_train+valid.csv`),
  com a nota de que a `valid` serviu para escolha e o número da histerese é
  otimista.
  - **Confirmação de ponta a ponta** (sensibilidade, 2026-10-01): o
    `line_thr` 15 no GSR dá +0,127 de LocSim no jogo 4 (contraste baixo) e
    −0,046 no jogo 9, onde o NPE mediano vai de 0,0056 para 0,0130. É o que a
    Fatia 3 viu na segmentação: um limiar global contra o contraste de cada
    jogo. **Trabalho futuro:** um limiar adaptado ao jogo ou ao frame.
- **Saída e reprodução** (decisão de Victor): o método é o do commit congelado
  `418a3be` **mais a correção da conferência de fechamento da série no commit
  `b3bcd98`** (`temporal.py:93`, `a[0]` → `a[0][0]`). Nenhuma saída muda: a chave
  da série não inclui o `temporal.py`, e as H são as mesmas. Roda com
  `python -m src.run`. As tabelas do test saem dos
  scripts versionados em `scripts/rodada_test/`, fora do `src/` para não mudar
  a impressão digital do código congelado, no commit deles. O hash desse commit
  vai em cada tabela (colunas `commit_metodo` e `commit_tabelas`), no manifesto
  dos extras e em `outputs/runs/rodada_test/tabelas/fechamento.json`. O `--all`
  chama esses scripts no fim.

---

## Estrutura

```
.
├── CLAUDE.md
├── README.md
├── .gitignore               # data/, sports_soccer_code_WC14/, outputs/debug/
├── pyproject.toml
├── config.yaml              # todos os parâmetros, cada um com origem
├── docs/
│   ├── 00-problema.md
│   ├── 01-metodo.md
│   ├── 02-dados.md
│   ├── 03-plano.md
│   └── decisoes.md
├── data/                    # gitignored (layout em 02-dados.md)
├── sports_soccer_code_WC14/ # gitignored, código original, só referência
├── src/
│   ├── pitch_model.py       # constantes regulamentares e polilinhas
│   ├── render.py            # imagem sintética
│   ├── io/                  # loaders WC14 / GSR
│   ├── segment.py           # gramado e marcações
│   ├── lines.py             # Hough e fusão
│   ├── conics.py            # elipses
│   ├── assign.py            # classificação semântica
│   ├── homography.py        # RANSAC, DLT, refinamento
│   ├── propagate.py         # âncoras e fluxo óptico
│   ├── evaluate.py
│   └── run.py
├── tests/
└── outputs/
    ├── debug/               # imagens intermediárias
    └── figures/
```

## O teste da imagem sintética

Vale destacar, porque é o que mais economiza tempo neste tipo de projeto.

Renderize o modelo do campo com uma homografia conhecida, em cima de um fundo
verde uniforme, com linhas brancas de espessura realista. O pipeline inteiro deve
recuperar aquela homografia com erro quase nulo.

Depois degrade a imagem sintética progressivamente: ruído gaussiano, borrão de
movimento, sombra sintética, oclusão parcial. Cada degradação mostra qual etapa
quebra primeiro. Isso é conteúdo de relatório de PDI e custa pouco para fazer.

## Se atrasar, corte nesta ordem

1. O SN-Calib (nem estava no escopo).
2. O braço de Kalman da Fatia 6 (já entra como opcional).
3. O termo ponto-linha do refinamento (Fatia 5) — fica só o RANSAC + DLT.
4. A calibração sistemática da Fatia 7 — fixe parâmetros razoáveis e reporte.

**Nunca corte a Fatia 2, nem a ablação com e sem fluxo da Fatia 6.** A primeira é
o instrumento de medida; a segunda é a pergunta do projeto.
