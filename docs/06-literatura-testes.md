# 06 — Literatura × projeto: análise técnica e testes propostos

> Documento de análise, não de decisão. Nada aqui muda o plano v2 congelado
> (`docs/05-melhorias-plano.md`). Cada teste proposto precisa, antes de rodar, da
> entrada própria em `docs/decisoes.md` e segue as regras do plano: dev = jogos 2, 3,
> 4, 5, 6 e 9; decisão por LocSim@5 penalizado por jogo; leave-one-game-out (LOGO)
> quando houver parâmetro livre; nenhuma escolha no test.

Fontes: os 15 artigos de `Topicos Av pdi/`, `docs/04-relatorio.md` (v1, test),
`outputs/runs_v2/baseline_dev/` e `outputs/runs_v2/b1_regra/` (v2, dev), e o código
de `src_v2/` (`assign.py`, `temporal.py`) e `config_v2.yaml`.

---

## 1. Onde a distância está

Decomposição do LocSim@5 penalizado no GSR test (v1, Tabela 2 do relatório):

| Degrau | LocSim@5 | Ganho | O que o degrau mede |
|---|---|---|---|
| nosso detector | 0,419 | — | — |
| nossa propagação (6c) | 0,749 | +0,330 | — |
| teto condicionado às âncoras | 0,763 | +0,014 | qualidade da propagação, com as âncoras onde estão |
| teto do sistema (âncora de gabarito a cada 150 frames) | 0,922 | **+0,159** | onde há âncora e quantos planos ficam cobertos |
| AuxFlow (tab. 7) | 0,929 | +0,007 | — |
| `H_gt` ajustada às linhas | 0,946 | +0,017 | limite de um registro planar pelas linhas |

Mais dois números que localizam a falha:

- **HSB, propagação a partir do gabarito:** 81,4 (nossa) contra 83,67 (AuxFlow, tab. 4).
  Com a mesma inicialização, o motor de fluxo clássico fica a ~2 pontos do AuxFlow.
- **Conjunto comum** (frames em que o nosso detector tem H): 0,922 contra 0,929 do AuxFlow.

**Leitura:** ~90% da distância restante está nas âncoras, que faltam nas vistas
centrais e no jogo 3, e nos planos sem âncora. A propagação contribui pouco (~0,014).
O limite de 0,946 só cai com um modelo de câmera mais rico que a homografia. No dev,
depois do B1, a mediana dos jogos é 0,635 no 6c e 0,649 no teto condicionado: o mesmo
padrão.

---

## 2. Os artigos, um a um

### 2.1 Registro de campo e consistência temporal (núcleo do projeto)

**AuxFlow (Ziegler et al., CVIU 2026).** NBJW (rede) + âncoras + grade auxiliar no
campo (2,5 × 2 m) re-identificada por Lucas–Kanade, com ida-e-volta ≤ 1 px e RANSAC
sobre a união {keypoints do detector no frame t+1} ∪ {pontos auxiliares}.
- **Âncoras:** heurística "o frame contém por inteiro o círculo central ou uma grande
  área" + IoU substituto (máscara de U-Net × campo projetado), nos máximos locais.
  Na tab. 5: ingênua /150 82,48 < NBJW 83,48; heurística 88,46; U-Net imagem 90,49;
  as duas juntas 90,65; âncora de gabarito 91,88.
- **Tab. 1:** frames com uma região inteira têm IoU_entire médio de 0,83–0,87, contra
  0,59 nos demais.
- **Máscaras:** caixas de pessoas e da bola dilatadas em 30 px (o maior fluxo medido) e
  borda de 50 px (em 1920×1080).
- **Ablações (tab. 4):**
  - grade 83,67 ≈ aleatória 83,39 ≫ geométrica 39,68;
  - LK 83,67 > RAFT 78,71: a quantidade de pontos vence a precisão;
  - sem os keypoints do detector, 78,30 (deriva); sem fluxo, 23,42;
  - inicialização ruim, 54,74.
- **Limitações declaradas:** sem distorção de lente; sem auto-correção durante a
  propagação (trabalho futuro); 2,6 FPS.

**BroadTrack (Magera et al., 2024).** Câmera de broadcast como pinhole +
**1 coeficiente radial k₁** + **modelo de tripé**: a cabeça pan-tilt tem centro de
rotação T fixo, e o centro óptico desliza no eixo óptico com o zoom. Rastreio por LM
com três termos: marcações (distância ao elemento projetado, perda de Cauchy), fluxo
LK (sem as caixas de pessoas) e tripé.
- **Confiança online:** Jaccard entre a máscara de marcações e o modelo projetado;
  abaixo de 0,5, reinicia.
- **Reinicialização com 2 pontos:** foco, pan e tilt com o centro da câmera conhecido
  (Gedikli).
- **Números:** no sn-gamestate, JaC5 56,88 contra 37,14 do NBJW; "C fixo" dá 50,97.
  O maior ganho da ablação vem da distorção radial. Reinicializou 33 vezes em 49
  sequências, com 15 frames de perda em média.
- **Ressalva:** na avaliação do AuxFlow (tab. 7), o BroadTrack perde no LocSim (0,860)
  e no RE (1,34 m): acerta as linhas, mas não a superfície.

**PnLCalib (Gutiérrez-Pérez & Agudo, CVIU 2026).** HRNet → grade hierárquica de
pontos: interseções (p), prolongadas (pe, até 50% além da imagem), linha × elipse
(p1), tangências (p2) e eixo central (p3).
- O **p2** dá o maior salto de cobertura, exatamente quando o círculo central aparece
  sem as interseções da linha do meio.
- Refino PnL com α = 0,6 para as linhas. No WC14, o refino só por linhas piora, e o
  conjunto pontos + linhas melhora (JaC5 77,6 → 85,9).
- Grade de limiares de RANSAC × subconjuntos de pontos, com voto heurístico (164 → 439 ms).
- Desambiguação de configurações espelhadas por sinal de produto vetorial.

**Citraro et al. (MVA 2020), *Real-time camera pose estimation*.**
- Keypoints semânticos + **posições dos jogadores** como correspondências sem
  identidade: no WC14, IoU 0,905 → 0,939. A ressalva: as posições vêm de um sistema
  multicâmera externo.
- Decomposição H → K, R, t com ponto principal no centro.
- **Mediana móvel com rejeição de outliers da focal** nos k frames anteriores.
- Filtro de partículas na pose, reiniciado quando a pose por frame explica mais inliers.
- Desaconselham o IoU_part, como fazemos.

**Maglo et al. (Sensors 2023).**
- Grade de keypoints **perspective-aware**: espaçamento em progressão aritmética, w₀ =
  6,4 m. Com grade uniforme, o RANSAC prefere o lado distante, onde os pontos se
  aglomeram na imagem. Erro de projeção no TSWC: 0,32 → 0,26 m.
- RANSAC a 8 px em 720p (é o nosso `ransac_frac`).
- Compensação do movimento da câmera por GFTT + LK + RANSAC de homografia entre frames.

**Golovkin et al. (Constructor, 1º no GSR 2024).**
- Câmera regredida por rede, refinada por **busca exaustiva numa grade de deltas** dos
  parâmetros. A perda é medida no plano do campo (linhas projetadas × modelo).
- Os keypoints incluem **interseções das linhas pintadas com as faixas de corte da
  grama** (74 pontos).
- **Savitzky–Golay nos parâmetros da câmera,** com correção limitada a ±2° e ±2 m e
  atraso de 15 frames.

**SoccerNet-GSR (Somers et al., 2024), material suplementar.** O gabarito de câmera
(de onde sai o `bbox_pitch` do LocSim) é:
- pinhole + **1 coeficiente radial**;
- homografia nos frames com marcações suficientes;
- nos demais, **posição da câmera fixa por sequência** (mediana) e o algoritmo
  **Two-Point PTZ** para foco, pan e tilt;
- ferramenta industrial no que sobra.

Isso explica o nosso limite de 0,946: o `bbox_pitch` vem de um modelo com lente e C
fixo, e a nossa `H_gt` planar pelas linhas não o reproduz nas bordas do quadro.

**Survey (Manafifard et al., CVIU 2017).** Gramado por cor dominante. A mistura de
gaussianas supera o histograma, e a remoção de sombra e a atualização do modelo são
"negligenciadas pela maioria". Para a sombra: imagem intrínseca ou restrição multicâmera.

### 2.2 Continuação (uso a jusante do registro)

- **Crang et al. (JSA 2026):** posição de provedores comerciais por broadcast contra o
  TRACAB, com RMSE de 1,68 a 16,39 m. O feed tático é o melhor, e a velocidade é
  filtrada em Butterworth de 1 Hz. A acurácia depende de o jogador estar
  **detectado/visível**.
- **Mills et al. (Sports Eng. 2026):** eventos automáticos a partir de tracking de
  broadcast; a maioria fica a ≤ 0,05 de F1 do multicâmera, e a Camera 1 é a melhor
  fonte. Os limites vêm da visibilidade e do erro da bola.
- **Vidal-Codina et al. (2022):** eventos por árvore de decisão determinística sobre
  posse de bola e regras, com mais de 90% de detecção. Não usa rede: compatível com o
  espírito do projeto, se houver tracking.
- **Hughes et al. (CVIU 2026):** "oclusão total" em mais de 10% dos frames com bola em
  jogo, porque a calibração falha quando as linhas somem. O preenchimento é por
  transformer + difusão, com eventos.
- **FOOTPASS, *Once Upon a Goal* (xGHub), SoccerNet-v3:** datasets a jusante
  (play-by-play, xG com pose, multi-vista). Não mudam o registro, mas definem o que um
  registro "bom o bastante" precisa entregar.

---

## 3. Comparação técnica, componente a componente

| Componente | Nós (`src_v2`) | Literatura | Diferença que importa |
|---|---|---|---|
| Hipótese de H no detector | só **2 + 2 retas** (2 longitudinais × 2 transversais), `assign.hypotheses` | PnLCalib: p, pe, p1, p2, p3; BroadTrack: 2 pontos com C conhecido | vista central (1 transversal + círculo) **não gera hipótese**; p1 só existe na ablação com RANSAC, depois da 2 + 2 |
| Modelo de câmera | homografia livre (8 GL) | BroadTrack e gabarito do GSR: pinhole + k₁, C fixo/tripé | não reproduz a lente: limite de 0,946 |
| Âncoras | máximo local de (IoU gramado + fração explicada) em ±12, verificação por maioria, B1 (`nota` ≥ 1,615) | AuxFlow: estrutura inteira visível + IoU substituto (imagem e campo) | sem o critério "estrutura completa"; sem sinal **independente do detector** contra erro sistemático |
| H dos pontos rastreados | `cv2.findHomography(..., 0)`: **mínimos quadrados, sem RANSAC** (`temporal.py:563`), depois o ajuste robusto com as linhas | AuxFlow: RANSAC | um ponto que o LK prende num jogador entra no H₀ |
| Exclusão de pessoas | componentes compactos de não-gramado dilatados 0,01·h (~11 px) | AuxFlow: caixas + 30 px, borda 50 px | máscara menor e sem caixas; borda 0,02·h (~22 px) |
| Reamostragem da grade | abaixo de 20 pontos ou a cada 25 frames | AuxFlow: a cada passo, pela H atual | mais pontos perdidos entre reamostragens |
| Termo do frame atual | pixels das linhas guiados pela H propagada (`alpha_points` = 1) | AuxFlow: keypoints do detector **independentes** da H propagada | o guiado reforça a própria H (auto-consistente), sem correção externa |
| Auto-correção durante a propagação | nenhuma; com C (v2), fusão por distância entre âncoras | BroadTrack: confiança por Jaccard e reinício; Citraro: reinício por inliers | nas pontas a mais de 250 frames, NPE mediano 0,208 |
| Suavização | 6a e 7b no detector; **nada depois do 6c** | Golovkin: SG nos parâmetros, com correção limitada | tremor do 6c 0,48 px contra 0,16 do Kalman |
| Gramado | pico de matiz em Lab (k-means e histerese reprovados) | survey: GMM > histograma, modelo atualizado por frame | jogo 3 (sombra azulada): 13 clipes sem âncora |
| Faixas de corte | não usadas (só filtradas no detector de sombra) | Golovkin, Cuevas: pontos com as linhas | fonte de pontos e de ponto de fuga nas vistas centrais |

---

## 4. Testes propostos

Ordenados por alavanca estimada sobre a seção 1 e por custo. Os "diagnósticos" (D)
não mudam o pipeline: leem caches ou o gabarito e decidem se vale implementar. Custos
pelas medidas do plano v2 (seção 6): 6c no dev ≈ 4 h; checagem barata do detector ≈ 1 h.

### Bloco 0 — diagnósticos baratos (sem mudar o método)

**D1. Teto com distorção radial.** *(BroadTrack, gabarito do GSR, AuxFlow tab. 2)*
- **Pergunta:** quanto do limite de 0,946 é lente?
- **Como:** no ajuste de `src_v2/homography.py` às linhas anotadas, acrescentar 1
  parâmetro k₁ (modelo de divisão, com centro de distorção no centro da imagem). Os
  pontos anotados e a base das caixas são corrigidos pelo k₁ antes de H⁻¹.
- **Medida:** LocSim@5 do gabarito pelas linhas, dev (train + valid), com e sem k₁,
  por jogo. Mais a acurácia contra as linhas a 5 px.
- **Leitura:**
  - se subir para perto de 0,98–0,99, o limite é a lente, e D1 abre T9 e T12 (k₁ no
    pipeline);
  - se não subir, o limite é o C fixo do gabarito, e a lente fica fora.
- **Bônus para o relatório:** resolve com número a divergência da literatura (AuxFlow
  diz que a distorção é desprezível; BroadTrack diz que é o maior ganho).
- **Custo:** só o gabarito, sem detector; ~1 h.

**D2. Estabilidade do centro da câmera C.** *(gabarito do GSR, BroadTrack, Citraro)*
- **Pergunta:** C é fixo por clipe? Por jogo?
- **Como:** decompor H em K, R, t, com ponto principal no centro e a focal pelas
  fórmulas do apêndice A de Citraro; C = −Rᵀt.
- **Medida:** dispersão de C (mediana e p90 da distância à mediana, em metros) nos
  frames com `H_gt` de cada clipe do dev; depois entre os clipes do mesmo jogo.
- **Leitura:**
  - C estável por jogo (dispersão de poucos metros): T5 e B2 ficam viáveis;
  - estável só por clipe: T5 vale dentro do clipe.
- **Custo:** minutos (só o gabarito).

**D3. Âncoras erradas pelo centro da câmera ("B2").** *(novo sinal independente dos
vizinhos; ataca "vizinhos concordam e todos errados")*
- **Pergunta:** um encaixe parcial do detector (área deslocada, lado trocado) produz
  uma H coerente com o movimento, e a maioria a confirma (42 de 45 aceitas erradas
  no dev). Essa H implica um centro de câmera fisicamente impossível?
- **Como:** para cada candidata do `sinais_por_candidata.csv`, calcular C e a distância
  dele à mediana robusta do C das candidatas aceitas do mesmo jogo.
- **Medida:**
  - AUC certas × erradas;
  - taxa de erradas recusadas com no máximo 2% das certas recusadas;
  - escolha no treino (4, 6, 9) e conferência na valid (2, 3, 5): o mesmo protocolo
    do B1, etapa 1.
- **Atenção:** no jogo 3, a maioria das aceitas está errada. A mediana do jogo precisa
  ser robusta, ou ponderada pela `nota`.
- **Custo:** minutos (caches).

**D4. "HSB-dev": propagação isolada, contra a tab. 4 do AuxFlow.** *(AuxFlow)*
- **Por quê:** o HSB é do test, que está contaminado.
- **Seleção:** por regra fixada antes de olhar, os 10 trechos de dev com menor LocSim
  do detector (um por clipe, janela de 100–200 frames).
- **Medida:** propagação a partir da `H_gt` (não depende das âncoras), com as
  variantes do T7, uma de cada vez.
- **Uso:** isola o motor de fluxo e dá a comparação direta com os 83,67 do AuxFlow.
- **Custo:** < 1 h por variante.

### Bloco 1 — mais âncoras (a maior alavanca: ~0,16 no test)

**T4. Hipótese A: círculo central + linha do meio + uma lateral, em forma fechada.**
*(PnLCalib p1/p2; relatório v1, seção 8)*

O relatório já mostrou que círculo + 1 reta é degenerado: sobra uma família de 1
parâmetro, as homografias que fixam a cônica e os dois pontos (0, ±9,15). Um terceiro
ponto na linha do meio fecha. Construção, toda projetiva e sem rede:
1. P₁, P₂ = linha do meio ∩ elipse, que correspondem a (0, ±9,15). Isso já existe em
   `assign.correspondences`.
2. S = linha do meio ∩ lateral, que corresponde a (0, ±34).
3. Com 3 pontos na reta, a projetividade 1D da linha do meio fica determinada. Ela dá
   a imagem do centro (0, 0) e o ponto de fuga V_Y da direção da linha do meio.
4. A polar de V_Y em relação à elipse é a imagem do diâmetro Y = 0. A interseção
   dessa polar com a elipse dá (±9,15, 0).
5. Com 6 correspondências, DLT. Em seguida, o mesmo refino guiado e o mesmo portão
   (`verify`, `accept`) das hipóteses 2 + 2.
6. As ambiguidades (qual lateral, qual lado) se resolvem pela regra de orientação
   atual (`valid_orientation`) e pela nota.

Regras e medidas:
- **Regra do desenho já aprovado:** só entra nos frames em que a 2 + 2 não dá
  candidata que passe nos portões.
- **Medidas:**
  - checagem barata (1 frame em 25), com cobertura e aceitas erradas por jogo;
  - fração de clipes sem âncora;
  - NPE das âncoras novas.
- **Onde atua:** a inspeção do A mostrou que 63 de 100 frames dos clipes sem âncora
  são vistas centrais.

**T5. Reinicialização PTZ com C do jogo ("D′", a hipótese D usada como gerador).**
*(BroadTrack 2 pontos, gabarito do GSR "Two-Point PTZ", Golovkin com a busca em grade)*
- **Depende de:** D2 positivo.
- **C por jogo:** mediana robusta dos C das âncoras aceitas (B1) do próprio jogo, sem
  gabarito. Com C conhecido e roll ≈ 0, sobram 3 graus de liberdade (pan, tilt, f).
- **Dois usos:**
  - **(a) Planos sem âncora:** busca em grade grossa de (pan, tilt, f), pontuada pela
    `verify` atual, como a grade de deltas do Golovkin. Depois o refino. Basta uma
    reta e o círculo, ou 2 interseções.
  - **(b) Vistas centrais:** os 2 pontos P₁, P₂ da linha do meio com o círculo já
    fecham pan, tilt e f, sem a lateral. Complementa o T4.
- **Medidas:**
  - planos e clipes sem âncora recuperados;
  - LocSim@5 penalizado no dev pelo critério congelado.
- **Risco:** C errado no jogo 3, onde as âncoras estão erradas. Medir à parte.

**T6. B1b com o critério do AuxFlow.** *(AuxFlow, heurística da tab. 1)*
- **Ideia:** quando o B1 deixa um clipe sem âncora, recuperar a candidata de maior nota
  **só se** a H dela mostra uma estrutura inteira (círculo central ou grande área
  projetados inteiros dentro da imagem e com apoio nas marcas ≥ limiar do treino).
- **Por quê:** o caso que motivou o B1b é o SNGS-033 (jogo 2), que perdeu a única
  âncora, e ela era certa. A exigência de estrutura completa é o filtro que o AuxFlow
  mediu como mais preditivo.
- **Medida:** o Δ do jogo 2 e se o jogo 3 não volta a aceitar as erradas
  (SNGS-042, -044, -049).
- **Custo:** 6c no dev (~4 h).

### Bloco 2 — propagação (alavanca menor, ~0,014 no test, mas barata)

**T7. Três ajustes do AuxFlow no motor de fluxo**, cada um isolado no D4 e depois no dev:
- **(a)** H₀ dos pontos rastreados por `cv2.USAC_MAGSAC` (ou RANSAC a `ransac_frac`·h)
  no lugar de mínimos quadrados (`temporal.py:563`);
- **(b)** reamostragem da grade a cada frame (`resample_every` 25 → 1);
- **(c)** exclusão de pessoas com a dilatação equivalente a 30 px e a borda equivalente
  a 50 px em 1080p (`compact_dilate_frac` 0,01 → 0,028; `border_frac` 0,02 → 0,046).

Os valores (a) e (c) vêm do artigo, não de varredura, e então valem como mudança "sem
parâmetro livre" pelo plano. Medida-alvo: NPE nas lacunas > 25 e nas pontas.

**T8. Correção externa durante a propagação (âncoras suaves + confiança online).**
*(AuxFlow K_{t+1}; BroadTrack, confiança por Jaccard; Citraro, reinício por inliers)*
- **Situação hoje:** entre âncoras, o termo do frame atual é guiado pela própria H
  propagada.
- **Proposta:** em cada frame t propagado,
  - se o detector tem H em t, com `nota` ≥ limiar do B1 e concordância com a H
    propagada a ≤ `verify_tol_frac`·h, a H do detector entra como âncora local e
    reinicia a deriva;
  - se a fração explicada da H propagada cai abaixo do `gate_img` por k frames
    seguidos, a propagação para de ganhar peso na fusão do C.
- **Medida-alvo:** NPE nas pontas (0,12) e nas lacunas > 25 (0,055).
- **Parâmetro k:** LOGO, com a grade {5, 10, 25} fixada antes.

**T9. Hipótese D: propagação com modelo PTZ (+ k₁, se o D1 confirmar).**
*(BroadTrack, gabarito do GSR)*
- **Como:** C fixo no jogo ou no clipe (D2), com pan, tilt e f por frame por LM nos
  pontos rastreados e nas linhas guiadas. Opcional: termo de suavidade em pan, tilt e
  f, como a SG do Golovkin.
- **Ganho esperado:**
  - 3 graus de liberdade por frame em vez de 8, então menos deriva nas pontas;
  - é o modelo com que o `bbox_pitch` foi gerado.
- **Medida-alvo:** deriva (NPE × distância à âncora) e tremor.
- **Custo:** 6c no dev (~4 h).

**T10. Peso pontos × linhas na reestimativa** (`alpha_points`, hoje "escolha" = 1,0).
*(PnLCalib α = 0,6)*
- Grade {0,5; 1; 2; 4} pontos/linhas, fixada antes, LOGO.
- Custo: 4 × ~4 h. Prioridade baixa: o "sem linhas" já perde 0,034 no test, e o
  ótimo deve estar perto do atual.

**T11. Suavização depois do 6c.** *(Bassek; Golovkin, com correção limitada)*
- **Como:** Hampel + SG (31, 3) sobre a série do 6c, na representação por pontos (a
  do 6a), com a correção por frame limitada a 1/720·h na grade da imagem: só tira o
  tremor, sem mover a H.
- **Medida:** LocSim@5 penalizado, tremor e deslize.
- **Por quê:** o 6c tem tremor de 0,48 px, contra 0,16 do Kalman.
- **Custo:** minutos, em cima dos caches do 6c.

### Bloco 3 — detector e segmentação (hipótese E e lente)

**T12. k₁ pelo método do fio de prumo (plumb-line), no pipeline.** *(depende do D1)*
- **Como:** estimar k₁ por clipe endireitando os pontos das retas longas aceitas
  (laterais) nas âncoras. Desfazer a distorção da máscara de marcações antes do Hough
  e das cônicas.
- **Por quê:** é PDI clássico puro (Devernay & Faugeras), e as retas curvas nas bordas
  quebram a fusão de colineares e o ajuste.
- **Medida:** checagem barata, depois a metade fixa.

**T13. Faixas de corte como fonte de retas.** *(Golovkin; Cuevas et al.)*
- **Diagnóstico primeiro:** em que fração dos frames de dev há faixas detectáveis?
  Bandas de L* paralelas, com periodicidade estimada pelo espectro da projeção ao longo
  da direção de uma família.
- **Ressalva:** o AuxFlow diz que grande parte do GSR não tem faixas.
- **Uso, se houver:** as bordas das faixas transversais dão o ponto de fuga da família
  da linha do meio, justamente o que falta nas vistas centrais. Isso reduz a hipótese
  central a 1 reta + ponto de fuga + círculo.

**T14. Gramado por GMM adaptativa de 2 componentes (sol e sombra) por frame.** *(survey)*
- **Como:** sementes pelo `lab_hue` atual. EM de 2 gaussianas em (L*, a*, b*), só nos
  pixels conexos às sementes, para não repetir o vazamento para a arquibancada que
  reprovou o k-means.
- **Critério próprio,** registrado antes (o plano já exige isso para E): o efeito é
  concentrado no jogo 3.

**T15. IoU no espaço do campo como nota de âncora.** *(AuxFlow, métrica substituta 2)*
- **Como:** gramado e campo projetados levados à vista de cima por H⁻¹, com o IoU
  dentro do polígono do campo de visão (`visibility.py` já o calcula).
- **Por quê:** compensa o viés do IoU na imagem, que pesa a parte de baixo.
- **Medida:** AUC nas candidatas (D3 e B1 como referência). Entra só se separar melhor
  que a `nota`.

### Bloco 4 — continuação (consequência a jusante)

**T16. Erro de velocidade e de distância percorrida induzido pelo registro.** *(Crang; Mills)*
- **Como:** com as caixas de gabarito, a posição de cada pessoa ao longo do tempo pela
  nossa H contra o `bbox_pitch`. Velocidade com Butterworth de 1 Hz, como em Crang.
- **Medida:** RMSE de posição e de velocidade, e o viés de distância total, por série
  (detector, 6a, 7b, 6c).
- **Por quê:** a identidade é do gabarito, então o teste isola o erro do registro.
  Vale porque o tremor e a deriva viram velocidade espúria. Dá o número que fecha com
  Crang (RMSE de 1,68 a 16 m nos provedores comerciais).
- **Custo:** caches.

**T17. "Oclusão total" e erro por região do campo.** *(Hughes; AuxFlow fig. 10)*
- **Como:**
  - a fração de frames sem H ou com 0 visível, comparada aos mais de 10% de Hughes;
  - o mapa de RE mediano por ponto da grade do campo para o detector e o 6c, como a
    fig. 10 do AuxFlow.
- **Por quê:** mostra onde no campo a falta de marcação dói, e serve de figura de
  relatório.
- **Custo:** caches.

---

## 5. Ordem sugerida

1. **D1, D2, D3, D4 e T11** (horas, só caches e gabarito). Eles decidem se T5, T9 e
   T12 valem o custo.
2. **C** (já implementado, na fila do plano) → **T7** (três ajustes, no D4 e depois
   no dev) → **T8**.
3. **T4 (A)**, com T5(b) como variante, se o D2 der C estável.
4. **T6 (B1b com estrutura completa)** e **T5(a)** (planos sem âncora).
5. **T9 (D)**, com k₁ se o D1 confirmar; **T12** se o D1 confirmar.
6. **E (T14, T13)** por último, com critério próprio.
7. **T16 e T17** a qualquer momento: não decidem nada, alimentam o relatório.

**Orçamento:** os diagnósticos somam algumas horas. Os testes de propagação (T6–T11)
são ~4 h cada no dev; os de detector (T4, T12, T14) seguem a triagem barata + metade
fixa do plano. O conjunto cabe nas ~180 h do plano, se a rodada completa ficar só
para a combinação final.

## 6. O que fica fora, e por quê

- **RAFT, U-Net, HRNet** (as redes do AuxFlow, do PnLCalib e do BroadTrack): a regra do
  projeto proíbe. O próprio AuxFlow mostra que o LK vence o RAFT na propagação.
- **Posições dos jogadores como correspondências** (Citraro): é a trilha F, fora deste
  ciclo pela decisão D4. Ela exigiria uma fonte de posições que não seja o gabarito.
- **Amostragem geométrica do AuxFlow:** perdeu feio (39,68 no HSB).
- **Line-RANSAC sobre a grade:** neutro ou negativo no AuxFlow (82,84 contra 83,67).
- **Kalman do BHITK:** o AuxFlow não mediu ganho no GSR (0,8852 contra 0,8851). No
  conjunto comum, o nosso Kalman + RTS também quase não muda (0,873 contra 0,869).

## 7. Expectativa franca

- **Passar o AuxFlow no GSR completo** exige subir o teto do sistema (0,922) e
  aproximar o 6c dele. A seção 1 diz que isso é quase todo âncora. O T4 e o T5 são os
  únicos testes com alavanca dessa ordem.
- **Recortes plausíveis para empatar ou superar:**
  - o **conjunto comum** (0,922 contra 0,929);
  - a **propagação a partir do gabarito** no HSB-dev (81,4 contra 83,67 no test).
  - Em ambos, T7 e T9 são o caminho.
- **Se o D1 mostrar que o limite de 0,946 é lente,** o T9 e o T12 sobem o teto de
  todos os números, inclusive acima do que um registro planar pelas linhas consegue.
  Esse seria o resultado mais original do projeto: o AuxFlow e o BroadTrack discordam
  justamente sobre isso.
