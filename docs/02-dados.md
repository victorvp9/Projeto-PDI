# 02 — Dados

Nada em `data/` entra no Git. Baixe manualmente.

---

## WC14 — benchmark principal, frame a frame

Dataset de referência para registro de campo em futebol, de Homayounfar et al.

- **209 imagens de treino** (dez jogos) e **186 de teste** (outros dez jogos),
  da Copa do Mundo de 2014.
- Cada imagem tem uma **matriz de homografia anotada manualmente**.
- Só câmera central principal, **sem zoom grande**.
- **As imagens não estão em sequência** — servem para avaliar o detector, nunca a
  propagação.

Partições distintas por jogo. Use o treino para calibrar todo parâmetro
`[EMPÍRICO]` e o teste apenas para a medição final. Ajustar no teste invalida o
resultado.

> O TVCalib anotou adicionalmente os segmentos do split de teste do WC14, no
> formato do SN-Calib. Se você encontrar essa anotação, ela permite avaliar as
> Etapas 3 a 5 isoladamente, e não só o resultado final. Vale procurar.

---

## TS-WorldCup — sequências, para a propagação

Contém **3.812 imagens de campo, de 43 vídeos** das Copas de 2014 e 2018, em
formato de sequência temporal. Dez vezes maior que o WC14.

É o único dataset deste projeto onde a Etapa 8 pode ser avaliada. Sem ele, não há
como medir estabilidade temporal nem ganho de propagação.

---

## CARWC — versão refinada

Claasen & de Villiers refinaram as anotações de homografia do WorldCup e do
TS-WorldCup com uma ferramenta própria de anotação, liberada publicamente, e
consolidaram os dois no **CARWC** (*consolidated and refined WorldCup*).

**Recomendação:** prefira o CARWC como fonte, e registre essa escolha em
`docs/decisoes.md`. Gabarito com menos ruído significa que a métrica mede o seu
método, não a anotação. Se usar o CARWC, diga isso explicitamente ao reportar
números — eles não são diretamente comparáveis aos publicados sobre a versão
original.

---

## SN-Calib — opcional, só se sobrar tempo

SoccerNet-Calibration: cerca de 20.000 imagens de 500 partidas, com anotação de
todos os segmentos do campo — linhas, segmentos de círculo e traves — em formato
de polilinha, com pelo menos duas posições por segmento visível. As cônicas são
anotadas como lista de pontos que aproximam o formato do círculo.

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
    sequence_id: str | None # None para WC14; id do vídeo no TSWC
    frame_idx: int | None   # None para WC14
)
```

**Confira a convenção da homografia do dataset antes de qualquer coisa.** Os
gabaritos podem vir no sentido imagem → campo, em coordenadas normalizadas, ou
com o campo em jardas. Não assuma: projete os quatro cantos do modelo com `H_gt`
e verifique visualmente que caem sobre os cantos do campo na imagem. Esse é o
primeiro teste a escrever.

---

## Código e dados de referência

Não são datasets de treino, mas poupam tempo e dão comparabilidade.

**Bassek et al. (2025)** liberaram o código de análise estatística, estimativa de
visibilidade e detecção de formação em `github.com/spoho-datascience/broadcast-analytics`.
Os dados brutos de tracking e vídeo não são públicos por licença, mas **todos os
dados intermediários pré-processados necessários para reproduzir as análises estão
no material suplementar** do artigo. É de lá que sai a possibilidade de comparar
sua taxa de inversão de visibilidade com a deles.

**TVCalib** — o pipeline de registro que eles usaram (`vid2pos` e calibração)
está em `mm4spa.github.io/tvcalib`. Serve como a linha de base "aprendida" contra
a qual reportar seus números. O PnLCalib e o BroadTrack também publicam resultados
contra ele, então os três pontos de comparação já existem na literatura.

As bibliotecas que eles usam valem imitar: `floodlight` para tracking,
`shapely` para os polígonos de campo de visão, `scipy` para o problema de
atribuição linear.

---

## Armadilhas registradas

- **Sentido da homografia** invertido entre convenções.
- **Unidades do modelo de campo** — metros vs. jardas vs. normalizado.
- **Dimensões do campo** — o modelo padrão é 105 × 68 m, mas campos reais variam.
  Os gabaritos assumem o padrão; não tente "corrigir".
- **Resolução das imagens** difere entre WC14 e TSWC. Toda constante em pixels
  precisa escalar com a resolução, ou ser definida em fração da altura da imagem.
- **Sombra atravessando o campo** parte a máscara de gramado em dois componentes.
  O "maior componente conexo" da Etapa 1 então descarta metade do campo. É a
  falha mais comum; trate explicitamente.
- **Padrão de corte da grama** gera faixas de luminância alternadas que o realce
  de marcações pode confundir com linhas.
