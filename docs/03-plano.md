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
  `decisoes.md`); o recurso pelas linhas entra no começo da Fatia 2.
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

**Primeiro: `H_gt` pelas linhas nos frames do GSR sem pessoas suficientes.**
- Ajuste ponto-linha (`scipy.optimize.least_squares`): minimizar a distância dos
  pontos anotados às polilinhas do modelo projetadas pela `H`, iniciando pela
  `H_gt` do vizinho mais próximo com `H` por pessoas. É **a mesma função** do
  refinamento da Etapa 7 (termo ponto-linha): escreva uma vez só, em
  `src/homography.py`, e a Fatia 5 reaproveita.
- **Teste:** em frames com `H` por pessoas, partir da `H` do vizinho e recuperar
  essa `H`.
- Esses frames ganham a marca **"gabarito pelas linhas"**, e as métricas saem com
  e sem eles (como os duvidosos).
- Risco medido: a distância até o vizinho com `H` chega a 374 frames (mediana
  69). Se o ajuste não convergir partindo de longe, encadear — cada frame
  iniciado pela `H` recém-ajustada do frame adjacente — e medir as duas formas.

- **Teste:** `H_gt` contra `H_gt` dá IoU = 1 e erro = 0.
- **Teste:** `H_gt` perturbada por translação conhecida degrada de forma monótona.
- **Teste:** para um mesmo par de homografias, os números batem com o código de
  avaliação de referência (KpSFR) quando se usa o mesmo molde.
- **Saída:** tabela de métricas a partir de um arquivo de homografias preditas,
  com e sem os frames de gabarito duvidoso.

### Fatia 3 — Gramado e marcações (semana 2)
Etapas 1 e 2 do método.

- Comparar HSV e Lab com número: **IoU contra `N_grass_gt.mat` do treino do
  WC14**. Comparar top-hat e filtro de linha.
- **Tratar a sombra atravessando o campo** — é a falha mais comum e vale
  enfrentá-la já.
- **Teste:** IoU médio da máscara de gramado contra o gabarito acima de um
  limiar fixado no treino; a máscara de marcações é esparsa.
- **Saída:** `outputs/debug/` com as máscaras de uma amostra.

### Fatia 4 — Linhas e cônicas (semana 3)
Etapas 3 e 4.

- Hough probabilística e, sobretudo, **fusão de colineares**. Sem fusão, o resto
  quebra.
- Ajuste de elipse no círculo central.
- **Teste:** na imagem sintética, o pipeline recupera as linhas esperadas.
- **Teste (GSR):** as linhas detectadas caem sobre as linhas anotadas do JSON.
- **Saída:** segmentos desenhados sobre o frame.

### Fatia 5 — Classificação e homografia (semana 4)
Etapas 5, 6 e 7. É a semana mais difícil.

- Classificação semântica dos segmentos, correspondências, RANSAC + DLT.
- Refinamento não-linear com termo ponto-linha — reaproveita a função escrita na
  Fatia 2 para a `H_gt` pelas linhas.
- **Teste:** na imagem sintética, a homografia recuperada bate com a usada para
  renderizar.
- **Marco:** primeiro número real no WC14, com taxa de cobertura, e o mesmo
  pipeline frame a frame no GSR (é o "detector sozinho" das ablações). Fim da
  primeira metade do projeto.

### Fatia 6 — Consistência temporal (semana 5)
Etapa 8, no GSR. É a contribuição do projeto. Três braços, nesta ordem de
esforço.

- **6a — Savitzky-Golay** sobre a série de homografias (janela 31, grau 3, como
  em Bassek et al.). Vinte linhas. Faça primeiro: é a referência que as outras
  precisam superar para justificar sua complexidade.
- **6b — Detecção de corte.** Descontinuidade por diferença de histograma ou
  salto na homografia, reiniciando a série. Sem isso, 6a e 6c suavizam através de
  cortes e pioram o resultado. Referência: 10,9 cortes por minuto (em
  transmissão). Os clipes do GSR são da câmera principal e o SNGS-070 não tem
  corte; o teste de 6b usa **cortes sintéticos**, concatenando clipes. Cuidado com
  falso positivo: um salto na homografia estimada pode ser erro do detector, e
  não corte — a diferença de histograma distingue os dois.
- **6c — Propagação por fluxo óptico.** Seleção de âncora usando a máscara de
  gramado da Fatia 3 como métrica substituta; grade regular de pontos auxiliares
  (excluindo as caixas de jogador e da bola); Lucas-Kanade; reestimativa.
- **Teste:** com tudo desligado, o resultado é idêntico ao da Fatia 5.
- **Ablação obrigatória:** com e sem fluxo óptico. É a comparação que responde à
  pergunta do projeto. Incluir também âncora ingênua (a cada N frames), que no
  AuxFlow ficou abaixo do detector sozinho.
- Kalman (BHITK) fica como opcional, se sobrar tempo.

### Fatia 7 — Estabilidade, visibilidade e calibração (semana 6)
- Métrica de estabilidade temporal pelos cantos projetados, **na série estimada**
  — nunca como diferença contra a `H_gt`, que tem tremor próprio (ver
  `01-metodo.md`).
- **Taxa de inversão de visibilidade**: polígono de campo de visão projetado no
  gramado com `shapely`, comparando gabarito e estimativa, sobre grade de pontos
  de teste e sobre as posições reais dos jogadores do GSR (medida unilateral,
  ver `01-metodo.md`).
- Calibração sistemática dos parâmetros `[EMPÍRICO]` nas partições de treino
  (WC14 e GSR separadamente).
- Registrar a sensibilidade de cada parâmetro — quais importam e quais não.

### Fatia 8 — Experimento e relatório (semanas 7-8)
- Rodada completa em WC14 e GSR, com e sem propagação.
- Comparação do ganho relativo com o que o AuxFlow reporta sobre detector
  treinado (tabelas 4, 5 e 7 dele, no mesmo teste do GSR).
- **Frames difíceis isolados.** Bassek et al. apontam que o efeito do
  pós-processamento temporal sobre frames com grande zoom nunca foi testado.
  Reporte o subconjunto HSB do AuxFlow (IDs e intervalos na tabela 3 dele) à
  parte — é a lacuna declarada que este projeto pode fechar.
- **Qualidade do gabarito do GSR** como seção curta: quantos frames discordam
  das linhas, e o caso da bola no ar como exemplo de correspondência falsa.
- Análise de falhas com imagens: os piores casos, e a causa de cada um.
- **Saída:** `python -m src.run --all` reproduz tudo do zero.

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
