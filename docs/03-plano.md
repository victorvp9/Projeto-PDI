# 03 — Plano de implementação

Oito fatias verticais. Cada uma entrega algo executável e testável. Como na outra
disciplina, **a avaliação vem antes do método**: sem métrica, ajustar um limiar de
Hough é chute.

Prazo: 8 semanas, com o trabalho dimensionado para 6.

---

### Fatia 1 — Modelo do campo e carregamento (semana 1)
Constantes regulamentares do campo, loader do WC14/CARWC, convenção de homografia.

- **Teste:** as bandeirinhas de escanteio ficam em `(±52.5, ±34)`.
- **Teste:** projetar os quatro cantos do modelo com `H_gt` e conferir que caem
  dentro da imagem, perto dos cantos visíveis.
- **Saída:** `--overlay <id>` desenha o modelo do campo sobre a imagem usando o
  gabarito. Se isso não ficar perfeito, nada adiante vai funcionar.

### Fatia 2 — Avaliação (semana 1)
`IoU_whole`, `IoU_part`, erro de reprojeção, taxa de cobertura.

- **Teste:** `H_gt` contra `H_gt` dá IoU = 1 e erro = 0.
- **Teste:** `H_gt` perturbada por translação conhecida degrada de forma monótona.
- **Saída:** tabela de métricas a partir de um arquivo de homografias preditas.

### Fatia 3 — Gramado e marcações (semana 2)
Etapas 1 e 2 do método.

- Comparar HSV e Lab com número. Comparar top-hat e filtro de linha.
- **Tratar a sombra atravessando o campo** — é a falha mais comum e vale
  enfrentá-la já.
- **Teste:** em imagens de treino, a máscara de gramado cobre uma fração
  plausível do quadro; a de marcações é esparsa.
- **Saída:** `outputs/debug/` com as máscaras de uma amostra.

### Fatia 4 — Linhas e cônicas (semana 3)
Etapas 3 e 4.

- Hough probabilística e, sobretudo, **fusão de colineares**. Sem fusão, o resto
  quebra.
- Ajuste de elipse no círculo central.
- **Teste:** numa imagem sintética renderizada a partir do modelo com homografia
  conhecida, o pipeline recupera as linhas esperadas. **Renderize essa imagem
  sintética** — é o melhor teste do projeto, porque isola o método de todo o
  ruído do mundo real.
- **Saída:** segmentos desenhados sobre o frame.

### Fatia 5 — Classificação e homografia (semana 4)
Etapas 5, 6 e 7. É a semana mais difícil.

- Classificação semântica dos segmentos, correspondências, RANSAC + DLT.
- Refinamento não-linear com termo ponto-linha.
- **Teste:** na imagem sintética, a homografia recuperada bate com a usada para
  renderizar.
- **Marco:** primeiro número real no WC14. Fim da primeira metade do projeto.

### Fatia 6 — Consistência temporal (semana 5)
Etapa 8. É a contribuição do projeto. Três braços, nesta ordem de esforço.

- **6a — Savitzky-Golay** sobre a série de homografias (janela 31, grau 3, como
  em Bassek et al.). Vinte linhas. Faça primeiro: é a referência que as outras
  precisam superar para justificar sua complexidade.
- **6b — Detecção de corte.** Descontinuidade por diferença de histograma ou
  salto na homografia, reiniciando a série. Sem isso, 6a e 6c suavizam através de
  cortes e pioram o resultado. Referência: 10,9 cortes por minuto.
- **6c — Propagação por fluxo óptico.** Seleção de âncora usando a máscara de
  gramado da Fatia 3 como métrica substituta; grade regular de pontos auxiliares;
  Lucas-Kanade; reestimativa.
- **Teste:** com tudo desligado, o resultado é idêntico ao da Fatia 5.
- **Ablação obrigatória:** com e sem fluxo óptico. É a comparação que responde à
  pergunta do projeto.
- Kalman (BHITK) fica como opcional, se sobrar tempo.

### Fatia 7 — Estabilidade, visibilidade e calibração (semana 6)
- Métrica de estabilidade temporal pelos cantos projetados.
- **Taxa de inversão de visibilidade**: polígono de campo de visão projetado no
  gramado com `shapely`, comparando gabarito e estimativa. É a métrica que
  traduz erro geométrico em consequência prática.
- Calibração sistemática dos parâmetros `[EMPÍRICO]` na partição de treino.
- Registrar a sensibilidade de cada parâmetro — quais importam e quais não.

### Fatia 8 — Experimento e relatório (semanas 7-8)
- Rodada completa em WC14 e TSWC, com e sem propagação.
- Comparação do ganho relativo com o que o AuxFlow reporta sobre detector
  treinado, e da taxa de inversão de visibilidade com a de Bassek et al.
- **Frames difíceis isolados.** Bassek et al. apontam que o efeito do
  pós-processamento temporal sobre frames com grande zoom nunca foi testado.
  Separe esse subconjunto e reporte-o à parte — é a lacuna declarada que este
  projeto pode fechar.
- Análise de falhas com imagens: os piores casos, e a causa de cada um.
- **Saída:** `python -m src.run --all` reproduz tudo do zero.

---

## Estrutura

```
.
├── CLAUDE.md
├── config.yaml              # todos os parâmetros, cada um com origem
├── docs/
│   ├── 00-problema.md
│   ├── 01-metodo.md
│   ├── 02-dados.md
│   ├── 03-plano.md
│   └── decisoes.md
├── data/                    # gitignored
├── src/
│   ├── pitch_model.py       # constantes regulamentares
│   ├── io/                  # loaders WC14 / TSWC / CARWC
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
