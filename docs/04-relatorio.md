---
title: "Registro de campo de futebol em vídeo de transmissão com processamento clássico de imagens e propagação temporal por fluxo óptico"
author: "Victor Viana"
date: "Outubro de 2026"
lang: pt-BR
---

# Resumo

Este trabalho estima a homografia entre o gramado e o frame de uma transmissão de futebol só com processamento digital de imagens clássico, sem redes neurais, e mede quanto a propagação temporal por fluxo óptico recupera das falhas desse detector. O detector segmenta o gramado por matiz, realça as marcações com um filtro de linha, detecta retas por Hough e elipses, gera hipóteses a partir de duas retas de cada uma de duas famílias de paralelas, verifica-as contra a imagem e refina a melhor por um ajuste ponto-linha. A propagação parte de âncoras verificadas e leva a homografia aos frames vizinhos com Lucas–Kanade, reestimando-a com pontos rastreados e com os pixels das linhas. A avaliação foi uma rodada única, com o método congelado, no test do SoccerNet-GSR (49 clipes de 3 jogos) e do WC14 (186 imagens). No GSR, o detector produz homografia em 0,505 dos frames, com LocSim@5 penalizado de 0,419. Com a propagação, a cobertura sobe para 0,897 e o LocSim@5 penalizado para 0,749 (mín.–máx. entre os 3 jogos: 0,650–0,920), abaixo do NBJW (0,885) e do AuxFlow (0,929) na medida da tabela 7 do AuxFlow. Nos frames que o detector cobre, a propagação reduz o erro residual (1 − LocSim@5) em cerca de 40%, fração parecida com os cerca de 38% do AuxFlow sobre o NBJW: o ganho a mais sobre o detector fraco vem de preencher os frames sem homografia, e não de corrigir homografias. A comparação tem um limite: o LocSim mede contra posições que vêm da calibração do próprio dataset, e a homografia ajustada às linhas pintadas do gabarito tira só 0,946 nessa métrica. Entre as estratégias de consistência temporal, o filtro de Kalman dá a série mais lisa, e a propagação é a que melhor acompanha o movimento real da câmera e a que menos inverte a visibilidade dos jogadores. A limitação principal é a dependência de duas famílias de retas, que deixa sem âncora as vistas do meio-campo.

# 1. Introdução

Para levar um pixel de uma transmissão de futebol a uma coordenada em metros no campo, é preciso estimar a transformação entre a imagem e o gramado. Como o gramado é aproximadamente plano, essa transformação é uma homografia: uma matriz 3 × 3 com oito graus de liberdade, determinada por no mínimo quatro correspondências (Hartley & Zisserman, 2004). As marcações do campo são padronizadas, mas três dificuldades tornam o problema difícil na prática:

- as marcações são esparsas, concentradas nas grandes áreas e no círculo central, e há regiões extensas do gramado sem nada a detectar;
- as câmeras de transmissão usam zoom, e um plano fechado pode não mostrar marcação nenhuma;
- a estimativa feita frame a frame é instável, e o tremor entre frames inviabiliza usos como inserir grafismo ou derivar a velocidade de um jogador a partir da posição.

A área migrou para detectores de pontos-chave treinados. Este trabalho faz a pergunta oposta:

> Até onde chega um pipeline de registro de campo puramente clássico — cor, morfologia, Hough, ajuste de cônica, RANSAC — e quanto da diferença para o estado da arte a propagação temporal por fluxo óptico consegue fechar?

A hipótese é que a propagação tenha ganho marginal maior sobre um detector fraco do que sobre um forte: se o detector acerta metade dos frames, os frames bons podem sustentar os ruins. O resultado das âncoras ingênuas do AuxFlow indica a condição: isso só vale se as âncoras forem bem escolhidas. Se a hipótese se confirmar, um sistema leve e sem GPU pode ser viável para aplicações offline.

A segunda pergunta vem de Bassek et al. (2025):

> Qual das três estratégias de consistência temporal — suavização da série de homografias, filtragem por Kalman, propagação por fluxo óptico — entrega mais estabilidade, e a que custo?

O trabalho mede também a consequência prática do erro de registro, seguindo Bassek et al. (2025): com que frequência o registro troca o rótulo de visibilidade de um jogador, colocando fora do quadro quem está dentro.

As contribuições são: (1) um detector frame a frame sem aprendizado profundo, avaliado no WC14 e no SoccerNet-GSR, com o ganho de cada etapa medido no treino; (2) a medição do ganho da propagação de Lucas–Kanade sobre esse detector fraco, com ablações (sem fluxo, sem linhas, âncora ingênua, âncora de gabarito) e uma comparação direta com o AuxFlow no subconjunto difícil HSB; (3) a comparação das três estratégias de consistência temporal em estabilidade e em inversão de visibilidade; (4) um protocolo com calibração só no treino, congelamento do código e uma rodada única no test, com determinismo conferido bit a bit.

O texto segue a ordem: trabalhos relacionados (Seção 2), método (Seção 3), dados (Seção 4), protocolo (Seção 5), resultados (Seção 6), análise de falhas (Seção 7), limitações e trabalho futuro (Seção 8) e conclusão (Seção 9). As tabelas completas da rodada estão no Apêndice A, e o detalhe do protocolo, no Apêndice B. As medidas feitas depois da rodada, a partir dos caches e sem mudar parâmetro nenhum, vêm identificadas como **análise posterior à rodada**.

# 2. Trabalhos relacionados

**Detectores treinados.** O PnLCalib (Gutiérrez-Pérez & Agudo, 2026) usa uma rede HRNetv2 que produz mapas de calor sobre uma grade hierárquica de pontos derivada geometricamente do campo. As correspondências incluem interseções diretas de linhas, interseções de linhas prolongadas, interseções de linha com elipse, pontos de tangência e pontos auxiliares no eixo central; na ablação dos autores, cada conjunto aumenta a cobertura. O módulo de refinamento otimiza pontos e linhas em conjunto, e o ganho do refino vem das linhas: refinar só com pontos quase não muda o resultado. O BroadTrack (Magera et al., 2025) modela fisicamente a lente e o tripé da câmera de transmissão, encontra na distorção de lente o maior ganho da sua ablação no GSR e reinicia o rastreamento quando a confiança, o IoU entre as marcações detectadas e o modelo projetado, cai abaixo de 0,5. Segundo a avaliação do AuxFlow (tabela 7), no GSR o BroadTrack tem o maior IoU do campo inteiro (0,8397 contra 0,8352 do AuxFlow), mas perde no IoU da parte visível (0,9224 contra 0,9426) e no erro de reprojeção em metros (1,34 contra 0,84 m).

**Propagação temporal.** O AuxFlow (Ziegler et al., 2026) escolhe frames-âncora com uma heurística sobre os pontos-chave e uma métrica substituta de IoU, amostra uma grade regular de 2,5 × 2 m de pontos auxiliares do campo, rastreia-os com Lucas–Kanade com verificação de ida e volta (erro ≤ 1 px) e reestima a homografia com os pontos-chave e os pontos propagados. No subconjunto difícil HSB do GSR, partindo da homografia de gabarito, o AuxFlow tem LocSim médio de 83,67%; sem o fluxo, cai para 23,42%, e sem os pontos-chave do detector, para 78,30%. O Lucas–Kanade venceu o RAFT (83,67 contra 78,71), porque retém mais que o dobro de pontos. A grade regular vence a amostragem geométrica (39,68) e empata com a aleatória (83,39). A escolha das âncoras é decisiva: no GSR completo, âncoras a cada 150 frames (82,48) ficam abaixo do detector sem propagação (83,48), as heurísticas chegam a 90,65 e a âncora de gabarito a 91,88. Com a homografia inicial perturbada, a propagação ainda chega a 54,74 contra 43,15 do detector sozinho. Na tabela 7 do AuxFlow, no GSR test, o LocSim@5 é 0,885 para o NBJW (Gutiérrez-Pérez & Agudo, 2024), o detector treinado em que o AuxFlow se apoia, e 0,929 para o AuxFlow. A propagação sempre foi avaliada acoplada a um detector forte; o ganho dela sobre um detector inteiro fraco não tinha sido medido.

**Filtragem e suavização.** O BHITK (Claasen & de Villiers, 2024) relaciona a homografia de um frame à do seguinte por uma transformação afim, com um filtro de Kalman em dois estágios e a incerteza dos pontos-chave modelada. Segundo o texto do AuxFlow (seção 5.6), ele melhorou levemente no TSWC; a tabela 7 do AuxFlow, que só traz o GSR, mostra-o praticamente igual ao NBJW (0,8852 contra 0,8851). Bassek et al. (2025) usaram o TVCalib (Theiner & Ewerth, 2023) para estimar a região visível do campo em transmissões reais e suavizaram a série das homografias com um filtro de Savitzky–Golay de janela 31 e grau 3, preenchendo antes lacunas de até 25 frames por interpolação linear. Os autores registram que o efeito desse pós-processamento sobre a consistência temporal e sobre frames difíceis, como os de zoom grande, não tinha sido testado; a validação foi qualitativa. Eles contaram em média 981 cortes por partida (10,9 por minuto), e, no feed de scouting, falhas de registro deixaram só um jogador visível em 1% do material e nenhum em 3%.

**Métodos clássicos e avaliação.** Farin et al. (2004) calibram a câmera em vídeo de esporte a partir das retas da quadra: as retas detectadas por Hough são separadas em duas direções, pares de cada direção são atribuídos às linhas do modelo, e a homografia de cada atribuição é avaliada pela concordância do modelo projetado com a imagem. A geração de hipóteses deste trabalho segue essa ideia. O levantamento de Manafifard et al. (2017) sobre rastreamento de jogadores trata a detecção do gramado como a primeira etapa canônica, por histograma de cor ou mistura de gaussianas, com vantagem para a mistura. Maglo et al. (2023) observam que, com pontos em grade uniforme, o RANSAC tende a escolher pontos do lado distante do campo, concentrados na imagem, e propõem uma amostragem que acompanha a perspectiva. Citraro et al. (2020) desaconselham o IoU medido só na parte visível, porque recortar pela região visível remove justamente o que está desalinhado. Os números publicados usam moldes de campo diferentes: o PnLCalib avalia o WC14 em 115 × 74 jardas, e Chu et al. (2022), no KpSFR, e Maglo et al. (2023), em 100 × 60 m. O IoU do campo inteiro e o erro em metros dependem do molde.

# 3. Método

O pipeline tem duas partes (Figura 1): um detector que estima a homografia em cada frame, isoladamente, e uma etapa temporal que usa a série do detector num clipe. A homografia é sempre tomada no sentido campo → imagem, com o campo em metros, a origem no centro e Y positivo em direção à câmera principal. O modelo do campo tem 105 × 68 m, com as marcações das Regras do Jogo. Todas as constantes estão no `config.yaml`, cada uma com a origem: artigo, norma do campo ou calibração na partição de treino.

![Figura 1 — Esquema do pipeline. Em cima, o detector frame a frame; embaixo, a consistência temporal por clipe. A suavização S-G, a S-G robusta, o Kalman e as ablações da propagação partem da mesma série do detector.](../outputs/figures/relatorio/fig1_pipeline.png)

## 3.1 Detector frame a frame

A Figura 2 mostra as etapas num frame do treino, e a Tabela 1, o ganho medido de cada etapa na calibração.

1. **Gramado.** Converte-se o frame para Lab e mede-se o ângulo de matiz em (a\*, b\*) em relação ao pico do próprio frame, o que absorve o balanço de branco de cada transmissão. O gramado são os pixels a até 20° do pico, com croma mínimo, seguidos de abertura, fechamento, maior componente conexo e preenchimento de buracos (Gonzalez & Woods, 2018). Com os tamanhos finais dos elementos estruturantes, o IoU médio contra as máscaras anotadas do WC14 de treino é 0,9861.
2. **Marcações.** Um filtro de linha marca o pixel significativamente mais claro, em L\*, que os vizinhos a uma distância proporcional à largura esperada da linha naquela altura da imagem, dos dois lados. Venceu o top-hat morfológico (Tabela 1). O filtro só atua dentro do gramado dilatado. O limiar de contraste foi calibrado em cada base no próprio treino: 15 no WC14 e 30 no GSR.
3. **Retas.** Transformada de Hough (Duda & Hart, 1972) na versão probabilística (Matas et al., 2000), um filtro de forma que retira os componentes compactos (jogadores) e a fusão de segmentos colineares, sem a qual uma linha do campo vira vários fragmentos.
4. **Elipses.** Candidatas formadas por trios de cordas curtas vizinhas, reajustadas por mínimos quadrados (`cv2.fitEllipse`, que segue Fitzgibbon & Fisher, 1995) e aceitas por apoio, forma e uma âncora geométrica: uma reta que cruza a elipse perto do centro, no círculo central, ou as pontas do arco junto à linha da grande área. O centro da elipse projetada nunca vira correspondência, porque a perspectiva o desloca do centro do círculo.
5. **Hipóteses.** Os segmentos são agrupados em duas famílias pelos pontos de fuga. Como em Farin et al. (2004), duas retas de cada família, entre as mais longas, são atribuídas a linhas do modelo da mesma família, respeitando a ordem, e as quatro interseções dão uma homografia (Hartley & Zisserman, 2004). A simetria de 180° do campo é desfeita pela convenção de que Y cresce em direção à câmera. **Essa geração de hipóteses exige 2 + 2 retas de duas famílias de paralelas** — o ponto que mais limita o detector (Seção 7).
6. **Verificação.** Cada hipótese recebe uma nota com três termos, cada um entre zero e um, com pesos iguais: a fração dos segmentos explicada pelo modelo projetado, a fração do modelo projetado sobre o gramado que cai numa marcação e o IoU entre o campo projetado e o gramado da etapa 1. A melhor hipótese só é aceita se passar por dois portões, fração explicada ≥ 0,45 e IoU ≥ 0,85, calibrados logo abaixo do percentil 5 que a homografia de gabarito atinge no treino.
7. **Refino.** A melhor hipótese é refinada por um ajuste ponto-linha com perda robusta: os pixels da máscara de marcações numa faixa em volta de cada linha do modelo projetado são levados às linhas, e os círculos entram pela distância de Sampson à cônica projetada (Sampson, 1982; Hartley & Zisserman, 2004). Esse ajuste é a mesma função que produz o gabarito do GSR (Seção 4) e aceita só soluções bem determinadas. As elipses são conferidas depois da homografia; uma elipse rejeitada devolve as suas cordas às retas, e o frame é reclassificado uma vez.

Sem quatro retas utilizáveis, ou sem hipótese que passe nos portões, o frame é reportado como falha de cobertura: nenhuma homografia é inventada. A ablação com correspondências de pontos e RANSAC (Fischler & Bolles, 1981) antes do refino foi neutra no treino e não entrou no caminho principal.

| Etapa | Comparação | Medida, partição de treino | Resultado |
|---|---|---|---|
| Gramado: espaço de cor | ângulo de matiz em Lab × HSV × distância em Lab | IoU do gramado, WC14 (média / com sombra) | 0,9838 / 0,9797 × 0,9822 / 0,9764 × 0,9728 / 0,9319 |
| Gramado: pós-processamento | cru → + abertura → + fechamento → + maior componente → + preenchimento | IoU do gramado, WC14 | 0,9441 → 0,9492 → 0,9548 → 0,9763 → 0,9838 |
| Marcações | filtro de linha × top-hat | F1 a 3 px, WC14 (GSR) | 0,579 × 0,560 (0,634 × 0,577) |
| Retas: filtro de forma | com × sem | F1 dos segmentos, GSR | 0,641 × 0,597 |
| Retas: fusão de segmentos | com × sem | fragmentação (F1), GSR | 1,17 × 4,70 (0,641 × 0,634) |

: Tabela 1 — Contribuição de cada etapa de PDI, medida na calibração, só nas partições de treino (WC14 `train_val`, GSR `train`). A sombra é o subconjunto do WC14 com sombra, definido por regra sobre um limiar de Otsu (1979) no L\*. Fragmentação: segmentos por linha do campo detectada.

![Figura 2 — Etapas do detector num frame do treino (SNGS-099, frame 525): (a) gramado; (b) máscara de marcações; (c) retas, cada uma numa cor, e a elipse aceita, em amarelo; (d) modelo do campo projetado pela homografia do detector.](../outputs/figures/relatorio/fig2_etapas.jpg)

## 3.2 Consistência temporal

O detector roda em todos os frames de cada clipe, e a série resultante (homografia ou nada, por frame) alimenta as estratégias abaixo. Todas são comparadas a partir da mesma série.

- **Suavização S-G (Bassek).** A versão de Bassek et al. (2025): lacunas de até 25 frames preenchidas por interpolação linear dos nove elementos da matriz normalizada, seguidas de Savitzky–Golay (Savitzky & Golay, 1964) de janela 31 e grau 3. A **S-G robusta** aplica antes um filtro de Hampel (Hampel, 1974) na representação por pontos, que descarta homografias discrepantes da vizinhança; a janela e o limiar foram calibrados no treino.
- **Kalman + RTS.** Filtro de Kalman (Kalman, 1960) de velocidade constante com o suavizador RTS (Rauch et al., 1965). É uma versão simplificada, e não o BHITK. Roda sobre as coordenadas no campo de quatro pontos fixos da imagem, com uma porta de Mahalanobis contra homografias erradas; os ruídos de processo e de medição foram calibrados no treino.
- **Detecção de corte.** A distância de Bhattacharyya (1943) entre histogramas HSV de frames consecutivos, na forma de Hellinger que o OpenCV calcula, detecta os cortes, e nenhuma estratégia atravessa um corte. O limiar foi calibrado no treino com cortes sintéticos.
- **Propagação por Lucas–Kanade.** As âncoras candidatas são os máximos locais da nota do detector, em ±12 frames. Cada candidata passa por uma verificação temporal: a homografia dela, levada pelo movimento que o Lucas–Kanade mede, tem que concordar com a do detector em pelo menos 2 vizinhos, com maioria. Cada frame recebe a homografia da âncora mais próxima do mesmo plano (entre cortes), propagada nos dois sentidos do tempo. A cada frame, uma grade de 2,5 × 2 m de pontos do campo, projetada pela homografia corrente, é rastreada por Lucas–Kanade (Lucas & Kanade, 1981) piramidal (Bouguet, 2001) com verificação de ida e volta (Kalal et al., 2010; erro ≤ 1 px), sem os pontos sobre jogadores e bola (os componentes compactos de não-gramado). A homografia é reestimada com os pontos rastreados e com os pixels das marcações em volta das linhas do modelo projetado. **A saída da propagação é a homografia propagada e reestimada.** A do detector só entra na escolha e na verificação das âncoras. Um plano sem âncora fica sem homografia.

As ablações da propagação isolam cada componente: **propagação sem fluxo** (a homografia da âncora copiada até o meio do caminho entre âncoras), **propagação sem linhas** (só os pontos rastreados na reestimativa), **âncora ingênua** (a primeira homografia do detector em cada bloco de 150 frames, sem verificação) e **âncora de gabarito** (a homografia de gabarito nos mesmos frames das âncoras verificadas, com a mesma propagação). A âncora de gabarito separa o erro da âncora do erro da propagação, dado onde as âncoras estão: é um **teto condicionado às âncoras**, e não o limite do sistema, porque herda os frames escolhidos pelo detector, e um clipe sem âncora fica fora dele também. O **teto do sistema**, com âncoras de gabarito escolhidas sem o detector, é uma análise posterior à rodada (Seção 6.2).

# 4. Dados

**WC14** (Homayounfar et al., 2017): 209 imagens de treino e 186 de teste, de jogos diferentes da Copa do Mundo de 2014, em 1280 × 720, com homografia anotada à mão e máscara do gramado. As imagens não estão em sequência e servem para avaliar só o detector. A convenção do arquivo (imagem → molde em jardas) foi verificada e convertida para a interna.

**SoccerNet-GSR** (Somers et al., 2024): clipes de 750 frames consecutivos a 25 fps, em 1920 × 1080, da câmera principal, com 57 clipes de treino, 58 de validação e 49 de teste. Cada partição tem 3 jogos; o test tem os jogos 7, 8 e 11, com 16, 19 e 14 clipes. O arquivo não traz parâmetros de câmera. Traz as linhas do campo anotadas na imagem e, para cada pessoa, a caixa na imagem e a posição no campo (`bbox_pitch`), que vem da calibração do próprio dataset, e não das linhas anotadas.

- **Gabarito.** A homografia de gabarito de cada frame é um ajuste ponto-linha às linhas anotadas, com aceite só quando bem determinado. Esse gabarito é a referência do NPE, do IoU e da classificação das âncoras em certas ou erradas (NPE > 0,05).
- **O gabarito e o detector não são independentes.** O gabarito é produzido pela mesma função de ajuste ponto-linha que refina a hipótese do detector (Seção 3.1, etapa 7), e os dois usam homografia pura, sem modelo de lente. Os erros dos dois são correlacionados: onde a lente curva as linhas, os dois tendem a errar do mesmo jeito, e o NPE e o IoU contra esse gabarito favorecem o método. Por isso entra também a acurácia contra as linhas anotadas (Seção 6.3), que não usa gabarito nenhum.
- **O limite do LocSim para registro pelas linhas.** O LocSim mede contra o `bbox_pitch`, e a calibração do dataset não coincide com as linhas anotadas. A nossa homografia de gabarito, ajustada às linhas, tira só 0,946 de LocSim@5 no test (análise posterior à rodada; 0,933 no train, medido antes da rodada). O gabarito do AuxFlow tira 0,9928 (tabela 2 deles) e é, com muita probabilidade, um RANSAC sobre as próprias pessoas: a nossa reprodução dele (abaixo) tira 0,978 no test. Um método que acerte as linhas pintadas fica, portanto, perto de 0,946 nessa métrica.
- **Correções de rótulo.** Foram corrigidas trocas de classe na anotação das linhas, achadas por uma varredura do gabarito, sem nenhuma saída do método. Sete clipes do test têm correção (SNGS-119, SNGS-121, SNGS-133, SNGS-148, SNGS-149, SNGS-187 e SNGS-199). As correções não afetam o LocSim, que usa as posições anotadas das pessoas, e sim o NPE e o IoU contra o gabarito.
- **Protocolo do AuxFlow.** Para comparar com o AuxFlow, usa-se também a `H_gt_auxflow`: RANSAC (3 px) sobre os pés das pessoas e as posições delas no campo, que reproduz a mediana e a distância da tabela 2 do AuxFlow, mas não a média. É a homografia inicial da medição de "só propagação" no HSB.
- **HSB.** O subconjunto difícil do AuxFlow (tabela 3 deles) tem 10 clipes, todos no test, cada um com um intervalo de frames e o LocSim@5 do NBJW. Os intervalos foram transcritos do artigo para `data_splits/hsb.csv`, com duas suposições registradas: a numeração a partir de 0 e a leitura do intervalo "90–0" do SNGS-128 como 0–90, propagado de trás para frente.

# 5. Protocolo experimental

**Partições.** Todo parâmetro empírico foi calibrado só no treino (WC14 `train_val`, GSR `train`). A validação do GSR serviu só para relatório, com uma exceção registrada: na calibração da segmentação, ela escolheu entre variantes, e nenhuma passou. O número limpo do GSR é o do test. O WC14 test e o GSR test ficaram intocados até a rodada final.

**Métricas.**

- **LocSim@5** (protocolo do GSR): o pé de cada pessoa anotada vai ao campo pela inversa da homografia estimada, e a similaridade é exp(ln(0,05)·d²/τ²), com τ = 5 m e d a distância à posição anotada. Não depende do gabarito. O **penalizado** divide a soma das similaridades pelo total de pessoas de todos os frames: a pessoa de um frame sem homografia vale 0. É o comparável com métodos que respondem em todos os frames. O LocSim **nos cobertos** usa só os frames com homografia; é otimista, porque premia quem só responde nos frames fáceis. O **mAP-LocSim** é a média de τ = 1 a 10 m. O agregado é sobre pessoas-frame.
- **Geometria:** NPE (deslocamento na imagem, dividido pela altura, dos pontos de uma grade de 2,5 × 2 m do campo visíveis pelo gabarito), IoU do campo inteiro (vista de cima) e IoU da parte visível (na imagem). No WC14, também o erro em metros (RE) e o protocolo do KpSFR, com o código deles sem mudança.
- **Acurácia contra as linhas anotadas** (protocolo do SN-Calib, com a contagem do código deles): em 960 × 540, cada classe de linha anotada e projetada no quadro conta como acerto se todos os seus pontos anotados estão a menos de 5, 10 ou 20 px da linha projetada pela homografia estimada; classe projetada e não anotada, ou anotada e não projetada, conta como erro. É a única medida geométrica que não depende de gabarito nenhum. A **penalizada** dá 0 ao frame sem homografia.
- **Cobertura:** a fração de frames (ou imagens) com homografia.
- **Estabilidade,** medida na série estimada e nunca contra o gabarito. O **tremor** é a segunda diferença, em pixels, dos pontos visíveis de uma grade do campo. O **deslize** é a distância entre o movimento que a série implica e o movimento real da imagem, medido por ECC (Evangelidis & Psarakis, 2008): um método independente do Lucas–Kanade da propagação.
- **Visibilidade** (Bassek et al., 2025): o polígono do campo de visão é levado ao campo pela homografia estimada e pela de gabarito. Mede-se a fração de jogadores-frame que o registro joga para fora do quadro (unilateral, porque o GSR só anota quem está no quadro), a fração de pontos de uma grade do campo com rótulo trocado e a fração de frames em que o registro deixa 0 jogadores visíveis.

**Incerteza.** Clipes do mesmo jogo não são independentes, e a incerteza é tomada entre jogos, com bootstrap sorteando jogos (2.000 reamostragens, semente fixa). Com 3 jogos, há só 10 reamostragens distintas, e o intervalo de 95% desse bootstrap é o mínimo e o máximo entre os jogos. O texto o reporta como tal: "mín.–máx. entre os 3 jogos". **A leitura principal é por jogo (Tabela 3).**

**Congelamento e rodada única.** Antes da rodada, o código e o config foram congelados num commit, com o SHA-1 do config e as chaves de cache registradas; cada etapa da rodada conferiu esse congelamento antes e depois. Valia a regra de que nenhum parâmetro muda depois de ver um número do test, e de que um defeito no meio obriga a refazer o test inteiro, declarando a segunda rodada. Houve uma rodada só. O determinismo foi conferido entre execuções independentes: nos 1.470 frames do GSR test a cada 25, a homografia do detector rodado numa etapa saiu bit a bit igual à da série gerada noutra etapa, outro processo e outra hora. **Houve um incidente:** a conferência de fechamento da série (`temporal.py:93`) quebrou depois que a série terminou, porque passava a tupla da tarefa no lugar do clipe. Nada foi corrigido durante a rodada. A conferência foi feita por fora, com o mesmo critério (735/735 chaves iguais à congelada), e a rodada seguiu. Não houve segunda rodada porque nenhum número do test tinha sido visto, o defeito estava numa conferência e não no cálculo, e a prova bit a bit da etapa seguinte confirmou que as séries eram as do código congelado. A correção veio depois, num commit separado, e não muda nenhuma saída (Apêndice B).

**Análises posteriores à rodada.** Depois de uma revisão externa do texto, cinco medidas foram acrescentadas: o LocSim das homografias de gabarito como predição, a suavização S-G no HSB, a acurácia contra as linhas anotadas, o teto do sistema e a robustez do detector a degradações sintéticas, esta só no WC14 de treino. Todas saem dos caches da rodada, por um script fora do código congelado, chamando as funções dele sem mudança, e nenhum parâmetro mudou (Apêndice B).

**Lição de método.** As conferências da sensibilidade e da rodada de validação acharam defeitos silenciosos antes do congelamento (lista no Apêndice B). A lição geral: estado derivado precisa de chave completa, o gabarito se carrega fora de qualquer perturbação, e uma variação exatamente nula pede prova de que o parâmetro é lido.

# 6. Resultados

Todos os números desta seção são do test, salvo indicação, e vêm da rodada única ou, quando marcados, das análises posteriores a ela. A Tabela 2 resume o GSR test; as tabelas completas, com a variação entre os jogos, estão no Apêndice A.

| Série | Cobertura | NPE mediano | LocSim@5 penalizado | Nos cobertos | Fração ao teto condicionado | Fração ao teto do sistema\* |
|---|---|---|---|---|---|---|
| detector | 0,505 | 0,0072 | 0,419 | 0,869 | — | — |
| suavização S-G (Bassek) | 0,680 | 0,0126 | 0,446 | 0,681 | 0,078 | 0,054 |
| S-G robusta | 0,665 | 0,0097 | 0,478 | 0,747 | 0,171 | 0,117 |
| Kalman + RTS | 0,680 | 0,0113 | 0,490 | 0,749 | 0,207 | 0,142 |
| **propagação** | 0,897 | 0,0105 | **0,749** | 0,833 | **0,959** | **0,656** |
| propagação sem linhas | 0,897 | 0,0122 | 0,715 | 0,796 | 0,861 | 0,588 |
| propagação sem fluxo | 0,897 | 0,1248 | 0,366 | 0,407 | −0,155 | −0,106 |
| âncora ingênua | 1,000 | 0,0262 | 0,571 | 0,571 | 0,442 | 0,303 |
| teto condicionado às âncoras | 0,897 | 0,0064 | 0,763 | 0,849 | — | 0,684 |
| teto do sistema\* | 1,000 | 0,0058 | 0,922 | 0,922 | — | — |

: Tabela 2 — GSR test (49 clipes, 3 jogos). A fração ao teto é (série − detector) / (teto − detector), no LocSim@5 penalizado. O teto condicionado às âncoras parte da homografia de gabarito nos frames das âncoras verificadas. \* Análise posterior à rodada: o teto do sistema parte da homografia de gabarito no primeiro frame com gabarito de cada bloco de 150 frames, com a mesma propagação.

## 6.1 O detector sozinho

**No WC14 test,** o detector produz homografia em 0,575 das 186 imagens. No protocolo do KpSFR, que a literatura reporta sobre todas as imagens, o IoU do campo inteiro tem média de 0,5155 e mediana de 0,8634 contando como 0 as 79 imagens sem homografia; nas 107 imagens com homografia, média de 0,8962 e mediana de 0,9534. No nosso molde de 105 × 68 m, nas imagens com homografia, o IoU do campo inteiro tem mediana de 0,913 (média 0,864) e o erro em metros, mediana de 0,380 m; a média do erro em metros (1,615 m) revela a cauda de homografias erradas aceitas. O IoU da parte visível, que Citraro et al. (2020) desaconselham, fica como complemento: mediana de 0,995 nas imagens com homografia.

**No GSR test,** o detector cobre 0,505 dos frames, com NPE mediano de 0,0072 e LocSim@5 de 0,869 nos frames cobertos. O LocSim@5 penalizado é 0,419. O detector "pisca": responde em trechos curtos, separados por lacunas curtas e longas (Tabela 7).

## 6.2 A propagação no GSR test

**Por jogo** (Tabela 3), a propagação sobe o LocSim@5 penalizado de 0,341 para 0,676 no jogo 7, de 0,360 para 0,650 no jogo 8 e de 0,555 para 0,920 no jogo 11. Nos três jogos, ela fica a menos de 0,03 do teto condicionado às âncoras. A cobertura da propagação vai de 0,838 a 1,000.

| Jogo | Clipes (com âncora) | Cobertura: detector / propagação | LocSim@5 pen.: detector | propagação | teto condicionado | teto do sistema |
|---|---|---|---|---|---|---|
| 7 | 16 (14) | 0,472 / 0,874 | 0,341 | 0,676 | 0,703 | 0,919 |
| 8 | 19 (16) | 0,447 / 0,838 | 0,360 | 0,650 | 0,661 | 0,899 |
| 11 | 14 (14) | 0,617 / 1,000 | 0,555 | 0,920 | 0,925 | 0,949 |

: Tabela 3 — GSR test por jogo. Com 3 jogos, esta é a leitura principal. O teto do sistema é análise posterior à rodada.

No agregado, a propagação sobe o LocSim@5 penalizado de 0,419 para 0,749, com ganho de +0,330 (mín.–máx. entre os 3 jogos: 0,290–0,365).

**Teto condicionado às âncoras.** A âncora de gabarito chega a 0,763, e a propagação fecha 0,959 da distância entre o detector e esse teto (mín.–máx. entre os 3 jogos: 0,925–0,986). Esse teto usa a homografia de gabarito nos mesmos frames das âncoras verificadas: mede a perda da propagação dado onde as âncoras estão, e não o limite do sistema, e os 5 clipes sem âncora ficam fora dele também. Nos 19 clipes de calibração do treino, a mesma fração era de 85%, e na validação, de 74%. Os 95,9% do test não indicam generalização: o test foi mais fácil para as âncoras, com 2,2% das âncoras aceitas erradas, contra 10% na validação, e 5 de 49 clipes sem âncora, contra 18 de 58 na validação.

**Teto do sistema (análise posterior à rodada).** Com âncoras de gabarito escolhidas sem o detector, no primeiro frame com gabarito de cada bloco de 150 frames, e a mesma propagação, o LocSim@5 penalizado chega a 0,922 (mín.–máx. entre os 3 jogos: 0,899–0,949), com cobertura de 1,000 e NPE mediano de 0,0058. A propagação com as nossas âncoras fecha 0,656 da distância entre o detector e esse teto, e o teto condicionado às âncoras, 0,684. **Quase toda a perda está em onde há âncora, e não na propagação:** com uma âncora a cada 150 frames, todos os planos ganham homografia, inclusive os dos 5 clipes sem âncora; no conjunto comum, a propagação com as nossas âncoras fica perto desse teto (0,922 contra 0,934).

As ablações respondem a duas perguntas.

- **O fluxo é a parte que importa.** Sem fluxo, com a homografia da âncora copiada, o LocSim@5 penalizado cai para 0,366, abaixo do próprio detector, e o NPE mediano sobe para 0,1248.
- **As linhas pesam pouco no agregado:** 0,715 sem elas, contra 0,749. Pesam nas lacunas longas (Seção 6.7).

**No conjunto comum** (os 18.133 frames em que o detector tem homografia), a homografia propagada e reestimada é melhor que a do próprio detector: LocSim@5 penalizado de 0,922 contra 0,869 e NPE mediano de 0,0066 contra 0,0072. Em erro residual (1 − LocSim@5), vai de 0,131 a 0,078, uma redução de cerca de 40% (Seção 6.5). Nesses frames, a âncora ingênua (0,818) fica abaixo do detector, como no AuxFlow. No conjunto inteiro, porém, ela fica acima (0,571 contra 0,419), porque cobre todos os frames: com um detector que cobre metade do clipe, até a âncora ingênua ganha pela cobertura.

## 6.3 Acurácia contra as linhas anotadas

A acurácia contra as linhas anotadas (Seção 5) é a única medida geométrica que não passa pelo gabarito. Foi gravada por frame na rodada e agregada depois dela (análise posterior à rodada). A Tabela 4 traz a acurácia a 5 px; as de 10 e 20 px estão no Apêndice A (T10).

| Série | Test inteiro, penalizada | Test inteiro, nos cobertos | Conjunto comum, penalizada |
|---|---|---|---|
| detector | 0,387 | 0,784 | 0,784 |
| suavização S-G (Bassek) | 0,398 | 0,599 | 0,735 |
| S-G robusta | 0,430 | 0,662 | 0,779 |
| Kalman + RTS | 0,419 | 0,631 | 0,760 |
| propagação | 0,551 | 0,613 | 0,807 |
| propagação sem linhas | 0,508 | 0,566 | 0,787 |
| teto condicionado às âncoras | 0,576 | 0,641 | 0,829 |
| teto do sistema | 0,733 | 0,733 | 0,794 |
| gabarito pelas linhas | 0,849 | 0,869 | 0,904 |
| `H_gt_auxflow` | 0,515 | 0,533 | 0,545 |

: Tabela 4 — Acurácia contra as linhas anotadas a 5 px (contagem do SN-Calib, 960 × 540), GSR test. Penalizada: frame com linhas anotadas e sem homografia vale 0. Análise posterior à rodada.

- **A ordem das séries se mantém.** No test inteiro, a propagação sobe a acurácia penalizada de 0,387 para 0,551, e as suavizações e o Kalman ficam perto do detector. Nos frames cobertos por cada série, a propagação fica abaixo do detector (0,613 contra 0,784), porque cobre também os frames difíceis, como no LocSim.
- **A correção nos frames comuns é menor contra as linhas que no LocSim.** No conjunto comum, a acurácia vai de 0,784 para 0,807: o erro (1 − acurácia) cai cerca de 11%, contra cerca de 40% no LocSim. As suavizações S-G pioram esses frames (0,735 na de Bassek).
- **O LocSim e as linhas discordam.** A `H_gt_auxflow`, ajustada às próprias pessoas, tira 0,978 de LocSim@5 e acerta só 0,533 das linhas a 5 px; o gabarito pelas linhas acerta 0,869 e tira 0,946 (Seção 4). Nem o gabarito pelas linhas chega a 1: a métrica exige todos os pontos de uma linha a menos de 5 px, e uma homografia sem lente não segue a linha curvada.

## 6.4 O subconjunto difícil (HSB)

A Tabela 5 traz as três medições definidas no protocolo, nos mesmos frames dos intervalos do HSB (1.120 frames com pessoas), ao lado das tabelas 3 e 4 do AuxFlow, e as duas suavizações S-G, medidas depois da rodada.

| Medição | Média | Mediana | Cobertura (frames com pessoas) |
|---|---|---|---|
| (1) só propagação, a partir da `H_gt_auxflow` | 81,4 | 92,7 | 1,000 |
| (2) o nosso detector | 17,7 | 0,0 | 0,221 |
| (3) pipeline completo (propagação com as nossas âncoras) | 61,7 | 71,1 | 0,829 |
| suavização S-G (Bassek) sobre o nosso detector | 20,9 | 0,0 | 0,396 |
| S-G robusta sobre o nosso detector | 24,5 | 0,0 | 0,371 |
| NBJW sozinho (AuxFlow, tabela 4) | 43,15 | 35,93 | — |
| AuxFlow (tabela 4) | 83,67 | 96,15 | — |

: Tabela 5 — HSB: LocSim@5 por frame (%), penalizado. As medições nossas são médias e medianas sobre os frames com pessoas; a pessoa de frame sem homografia vale 0. As suavizações S-G são análise posterior à rodada.

- **(1) A propagação isolada é comparável à do AuxFlow:** 81,4 contra 83,67 na média e 92,7 contra 96,15 na mediana. As duas medições não são iguais. A homografia inicial é a nossa reprodução do gabarito do AuxFlow (Seção 4), que reproduz a mediana do gabarito deles, mas não a média; a nossa reestimativa usa as linhas detectadas, e a deles, os pontos-chave do NBJW; e são só 10 clipes, com médias de 50,8 a 97,4 entre eles.
- **(2) O nosso detector é muito mais fraco que o NBJW** nesses frames: 17,7 de média, contra 43,15. A mediana é 0,0, porque ele responde em 0,221 dos frames com pessoas. Nos frames em que responde, o LocSim@5 médio é 79,7.
- **(3) O pipeline completo fica entre os dois:** 61,7 de média, acima do NBJW sozinho (43,15) e abaixo do AuxFlow (83,67). Dois dos dez clipes, o SNGS-128 e o SNGS-138, não têm âncora aceita e valem 0 no intervalo inteiro, embora a propagação a partir do gabarito chegue a 97,4 e 96,5 neles.

Bassek et al. (2025) deixaram sem teste o efeito da suavização S-G sobre frames difíceis, como os de zoom grande. O HSB não é exatamente esse conjunto: é o subconjunto difícil para o NBJW. Nele, a suavização S-G sobre o nosso detector sobe a cobertura dos frames com pessoas de 0,221 para 0,396, porque interpola as lacunas, mas o LocSim@5 médio nos frames cobertos cai de 79,7 para 52,9: a média penalizada vai só de 17,7 para 20,9 (24,5 na S-G robusta), contra 61,7 da propagação (análise posterior à rodada; T2 c, no Apêndice A). A Figura 3 mostra um clipe, escolhido por regra fixa (o intervalo mais longo do HSB). A propagação a partir do gabarito começa perto de 1 e se degrada ao se afastar do frame inicial. O pipeline completo segue as âncoras do fim do intervalo e se degrada ao propagar para trás.

![Figura 3 — LocSim@5 por frame no SNGS-136 (intervalo 60–280 do HSB). Só propagação a partir da `H_gt_auxflow` no frame 60 (azul), pipeline completo com as nossas âncoras (vermelho) e o detector nos frames em que responde (pontos); as marcas cinza embaixo são os frames sem homografia do detector. Médias no intervalo: 87,2, 85,7 e 44,2 (penalizado).](../outputs/figures/relatorio/fig3_hsb_curva.png)

## 6.5 Comparação com o AuxFlow

A comparação com a tabela 7 do AuxFlow (Tabela 6) precisa ser lida nos dois sentidos.

| | LocSim@5 | Erro residual (1 − LocSim@5) | Redução do erro residual |
|---|---|---|---|
| NBJW (AuxFlow, tabela 7) | 0,885 | 0,115 | — |
| AuxFlow (tabela 7) | 0,929 | 0,071 | 38% sobre o NBJW |
| nosso detector, penalizado | 0,419 | 0,581 | — |
| nossa propagação, penalizado | 0,749 | 0,251 | 57% sobre o detector |
| nosso detector, conjunto comum | 0,869 | 0,131 | — |
| nossa propagação, conjunto comum | 0,922 | 0,078 | 40% sobre o detector |

: Tabela 6 — GSR test, comparação com a tabela 7 do AuxFlow. O LocSim deles não tem frames sem homografia; o nosso penalizado dá 0 à pessoa de frame sem homografia. O conjunto comum são os 18.133 frames com homografia do nosso detector, com o LocSim penalizado.

- **A favor do método:** a propagação isolada é comparável à do AuxFlow (Seção 6.4), e o ganho da propagação sobre o detector é muito maior (+0,330 contra +0,044).
- **Contra:** o ganho maior parte de uma base muito mais baixa. O nosso detector é bem mais fraco que o NBJW (0,419 contra 0,885), e o pipeline completo, com 0,749, fica abaixo do NBJW sozinho na medida deles. Da distância entre o nosso detector e o AuxFlow, a propagação fecha cerca de 65%.
- **O ganho a mais vem da cobertura, e não da correção.** No conjunto inteiro, a propagação tira 57% do erro residual do detector; nos frames que o detector cobre, tira cerca de 40%, fração parecida com os cerca de 38% que o AuxFlow tira do NBJW. Nos frames que os dois cobrem, a propagação remove uma fração parecida do erro sobre um detector fraco e sobre um forte; o ganho a mais sobre o detector fraco vem de preencher os frames sem homografia. Nos frames cobertos por cada série, a propagação fica até 0,035 abaixo do detector (mín.–máx. entre os 3 jogos: de −0,078 a −0,003), porque cobre também os frames difíceis. **Ressalva:** o nosso conjunto comum são os frames fáceis do nosso detector, e o do AuxFlow é o test inteiro.
- **O limite do LocSim.** O `bbox_pitch` vem da calibração do próprio dataset (Seção 4). A homografia de gabarito pelas linhas tira 0,946 de LocSim@5 nos frames com gabarito, e a reprodução do gabarito do AuxFlow, ajustada às próprias pessoas, tira 0,978, mas acerta só 0,533 das linhas anotadas a 5 px (Seção 6.3; análise posterior à rodada). Um método que acerte as linhas pintadas fica perto de 0,946 nessa métrica, e parte da diferença para o NBJW (0,885) e o AuxFlow (0,929) pode vir daí. No conjunto comum, a propagação chega a 0,930 nos frames que cobre.

## 6.6 Estabilidade e visibilidade

O ECC convergiu em 100% dos 36.701 pares de frames consecutivos, com correlação mediana de 0,987. Como as séries cobrem conjuntos diferentes de frames, a comparação justa é na interseção dos frames cobertos pelas cinco séries (17.828 de 36.750 frames; T4b, no Apêndice A).

- **Tremor:** o Kalman dá a série mais lisa, com mediana de 0,13 px e p90 de 0,57 px na interseção. A propagação fica em 0,40 / 1,43 px, e o detector em 1,29 / 15,50 px.
- **Deslize:** a propagação é a que melhor acompanha o movimento real, com 1,38 / 4,33 px, contra 1,71 / 5,45 px do Kalman e 1,90 / 8,31 px da suavização S-G (Bassek). No conjunto de cada série, o p90 do deslize é 4,17 px na propagação, contra 23,51 no Kalman e 72,61 na suavização S-G (Bassek): a suavização atrasa a homografia nas panorâmicas.
- **Inversão de visibilidade:** na interseção, a propagação joga para fora do quadro 0,8% dos jogadores-frame, contra 4,4% do Kalman e 5,0% do detector. Na versão penalizada, sobre todos os frames, a inversão cai de 53,5% no detector para 11,8% na propagação, puxada pela cobertura; nos frames cobertos, cai de 5,6% para 2,1%.
- **Frames com 0 jogadores visíveis** (o indicador de Bassek et al., 2025): 0,1% na propagação, nos frames cobertos, contra 3% no feed de scouting deles. Os dados e os sistemas são diferentes, e a comparação vale só como ordem de grandeza.

A homografia congelada da propagação sem fluxo tem tremor zero e deslize de 4,25 px: tremor e deslize medem coisas diferentes, e nenhuma das duas basta sozinha.

## 6.7 Âncoras e lacunas

Das 958 âncoras candidatas, 28,3% das que têm gabarito estão erradas (NPE > 0,05). A verificação temporal aceita 558, das quais 2,2% erradas (12 âncoras). Em 5 clipes nenhuma âncora é aceita (Seção 7).

| Lacuna | Frames | Suavização S-G (Bassek) | S-G robusta | Propagação | Propagação sem linhas |
|---|---|---|---|---|---|
| 1–3 | 1.665 | 0,0974 | 0,0324 | 0,0095 | 0,0115 |
| 4–25 | 4.624 | 0,8994 | 0,7960 | 0,0168 | 0,0247 |
| > 25 | 8.391 | — | — | 0,0551 | 0,0785 |
| pontas | 3.088 | — | — | 0,1221 | 0,1355 |

: Tabela 7 — NPE mediano nas lacunas do detector, por comprimento. As pontas são lacunas que tocam o começo ou o fim do clipe; as suavizações S-G não as preenchem.

Nas lacunas do detector (Tabela 7), a propagação tem NPE mediano de 0,0095 a 0,0168 nas curtas. A suavização S-G (Bassek), que interpola entre as bordas, chega a 0,8994 nas lacunas de 4 a 25 frames. **A causa é a homografia do detector nas bordas da lacuna**: em 62% dessas lacunas, as duas bordas estão erradas. O detector alterna entre uma homografia errada e nenhuma nos trechos difíceis, e a interpolação dos elementos da matriz herda o erro (Seção 7). Quando as duas bordas estão certas, o NPE mediano da suavização S-G (Bassek) é 0,0242. Nas lacunas longas e nas pontas, a propagação sem linhas erra mais (0,0785 contra 0,0551 acima de 25 frames): as linhas seguram a deriva onde a âncora está longe.

## 6.8 Custo

O hardware foi um AMD Ryzen 7 5700X (8 núcleos, 16 threads) com uma RTX 5060. O detector roda inteiro na CPU; só as máscaras da propagação usam a GPU, e com saída idêntica à da CPU. O AuxFlow usou um i7-8700K com uma RTX 4090, com as redes na GPU.

- **Máquina inteira, na rodada:** a série do detector levou 8,58 h para os 49 clipes com 15 processos (1,19 frames/s), ou cerca de 630 s de parede por clipe de 750 frames. A propagação, com todas as ablações, acrescenta cerca de 126 s por clipe com 10 processos (1,71 h no total).
- **AuxFlow (tabela 6):** 292 s por clipe para o método inteiro, com GPU, ou 2,6 FPS.
- **Por núcleo, como complemento** (perfil sem concorrência): o detector custa 4,76 s por frame no GSR, cerca de 3.570 s por clipe, e 2,90 s no WC14. O gargalo é a verificação das hipóteses em Python, e as operações de imagem são uma fração pequena. A propagação custa 127 ms por frame.

**Máquina inteira contra máquina inteira, só a série do detector leva mais que o dobro do AuxFlow inteiro (630 s contra 292 s por clipe).** O pipeline é viável offline e roda sem GPU, mas não é leve: quase todo o custo é o detector, que precisa rodar em todo frame para escolher as âncoras.

## 6.9 Robustez a degradações

Análise posterior à rodada, no WC14 de treino (209 imagens), nunca no test. Cada degradação sintética foi aplicada sozinha à imagem original, em três níveis, e cada etapa foi medida com as funções de avaliação da calibração (protocolo no Apêndice B; tabela completa na T11, no Apêndice A). A etapa que "quebra primeiro" é, no menor nível em que alguma medida cai mais de 10% em relação à imagem limpa, a primeira na ordem do pipeline (Figura 8). Na imagem limpa, o gramado tem IoU de 0,9861, a cobertura das marcações a 2 px é 0,612 e o detector cobre 0,517 das imagens.

- **Ruído gaussiano:** quebra primeiro o gramado, em σ = 10 (IoU de 0,708), e o detector cobre 0,244 das imagens. Em σ = 20, o gramado desaparece (IoU de 0,004), e o detector não responde em nenhuma imagem.
- **Borrão de movimento horizontal:** quebra primeiro a cobertura das marcações, com núcleo de 11 px (0,543). Com 21 px, o detector responde em 0,077 das imagens. O gramado não muda.
- **Sombra sintética:** quebra primeiro a cobertura das marcações, com o L\* multiplicado por 0,5 (0,526). O gramado por matiz quase não muda (IoU de 0,969 com o L\* × 0,35), porque escurecer não muda o matiz. A sombra real do jogo 3 da validação também tira croma, o que esta sombra sintética não reproduz.
- **Oclusão por elipses do tamanho de jogadores:** só com 20% do gramado coberto uma medida passa do limite, de novo a cobertura das marcações (0,533); a cobertura do detector cai para 0,478.

**Fora do ruído, o elo fraco é o limiar global das marcações**, o mesmo que a sensibilidade apontou (Seção 8). Quando o detector responde, a homografia continua boa: o IoU do campo inteiro mediano nas imagens cobertas fica entre 0,889 e 0,930 em todos os níveis com resposta. O que se perde primeiro é a cobertura, e a fração de aceitas erradas (IoU do campo inteiro < 0,8) sobe com o borrão e o ruído: de 0,102 na imagem limpa para 0,375 com o núcleo de 21 px, sobre só 16 imagens aceitas.

![Figura 8 — Robustez a degradações sintéticas no WC14 de treino (análise posterior à rodada): cada medida por etapa dividida pelo seu valor na imagem limpa, por degradação e nível. A linha tracejada marca a queda de 10%.](../outputs/figures/relatorio/fig8_degradacao.png)

# 7. Análise de falhas

**Inspeção visual.** As figuras de todos os casos citados nesta seção foram inspecionadas uma a uma: os 6 piores clipes da propagação, as 12 âncoras erradas aceitas, os 5 clipes sem âncora e as 3 lacunas de exemplo (`outputs/figures/falhas_test/`). As causas abaixo vêm dessa inspeção e dos números das âncoras e do teto condicionado de cada clipe.

**Piores clipes da propagação.** Entre os clipes com âncora, os seis de menor LocSim@5 penalizado na propagação são o SNGS-149 (0,252), o SNGS-119 (0,458), o SNGS-143 (0,495), o SNGS-144 (0,506), o SNGS-148 (0,587) e o SNGS-126 (0,635).

- Em quatro deles (SNGS-149, SNGS-119, SNGS-143 e SNGS-144), nenhuma âncora aceita está errada, e o pior frame é uma vista do meio-campo ou da zona entre o meio e a área. Nesses frames, a propagação projeta a grande área sobre o círculo central ou desloca o círculo e o canto da área. No SNGS-143 e no SNGS-144, a propagação coincide com o teto condicionado às âncoras (0,495 contra 0,495; 0,506 contra 0,508): o limite é a propagação, e não a âncora.
- O SNGS-148 tem uma âncora errada (f109), e o pior frame, no começo do clipe, é uma vista do círculo central com o círculo do modelo deslocado.
- O SNGS-126 tem a âncora errada de maior NPE do test (f588, NPE 1,355; Figura 4): a propagação fica em 0,635, contra 0,954 do teto condicionado.

**Âncoras erradas aceitas.** São 12, de três tipos:

- **Encaixe parcial** (10 âncoras: seis do SNGS-190, duas do SNGS-187, a do SNGS-122 e a do SNGS-148; NPE de 0,060 a 0,235). A homografia acerta a grande e a pequena área do lado do gol e erra a profundidade e a perspectiva fora delas, com o arco da área ou a lateral próxima deslocados.
- **Troca de reta grosseira** (SNGS-126 f588): as linhas da área atribuídas a retas erradas do modelo.
- **Quase certa** (SNGS-132 f721, NPE 0,063, logo acima do limiar).

As seis do SNGS-190 mostram o limite da verificação temporal: o erro é sistemático, os vizinhos concordam entre si, e a verificação o confirma em vez de recusá-lo. Não houve, no test, simetria de 180° nem o friso das placas tomado pela lateral, que apareceu no treino.

![Figura 4 — Âncora errada aceita (SNGS-126, frame 588, NPE 1,355): o modelo projetado pela homografia do detector (vermelho) contra os pontos anotados das linhas (amarelo). A propagação leva esse erro aos vizinhos.](../outputs/figures/falhas_test/ancora_errada_SNGS-126_f588.jpg)

**Clipes sem âncora: o enquadramento, e não a segmentação.** Cinco clipes do test não têm nenhuma âncora aceita: SNGS-127, SNGS-128, SNGS-134, SNGS-138 e SNGS-147. Na validação, 13 dos 18 clipes sem âncora eram do jogo diurno com sombra azulada, e a causa era a segmentação. **No test, ao contrário, a segmentação não explica a falta de âncora** (medida em 1 frame a cada 75, com as métricas da avaliação da segmentação):

- o gramado está normal (fração do campo classificada como grama de pelo menos 0,988), e não há sombra;
- a cobertura das marcações a 2 px vai de 0,81 a 0,98, acima da referência do treino (0,79). Nos dois clipes do jogo 7, fica um pouco abaixo da dos clipes com âncora do mesmo jogo (0,81 e 0,85, contra 0,89), mas o contraste das linhas ali é maior;
- o contraste das linhas é igual ou maior que o dos clipes com âncora do mesmo jogo em quatro dos cinco clipes.

A causa é o enquadramento.

- **Vistas do círculo central e da linha do meio** (SNGS-127, SNGS-128 e SNGS-134; Figura 5): há uma única reta transversal, a linha do meio, e as laterais. Sem duas retas em cada família, o detector não forma a hipótese certa.
- **Zona entre o meio e a área** (SNGS-138): uma lateral, o canto da grande área e o arco.
- **O SNGS-147 é a exceção.** Mostra a grande e a pequena área, oblíquas e comprimidas no alto do quadro, e nenhuma das 11 candidatas verificáveis é aceita. É também o único em que a segmentação pode contribuir: o contraste das linhas é menor que nos clipes com âncora do jogo 8 (52% dos pontos anotados acima do limiar, contra 68%), e o vazamento do gramado é maior.

O detector cobre de 0,7% a 15,9% dos frames desses clipes. **É uma limitação do método, e não um defeito de implementação:** o detector depende de 2 + 2 retas de duas famílias de paralelas.

![Figura 5 — Clipe sem âncora (SNGS-134, frame 375). À esquerda, o modelo pela homografia de gabarito e os pontos anotados; à direita, o gramado (verde) e as marcações (magenta) da segmentação. A segmentação acha o círculo e a linha do meio, mas a vista tem uma única reta transversal.](../outputs/figures/falhas_test/sem_ancora_SNGS-134_f375.jpg)

**Deriva com a distância à âncora.** O erro da propagação cresce com a distância, em frames, à âncora aceita mais próxima (Figura 6). Nos frames a até 25 frames de uma âncora, o NPE mediano fica entre 0,0059 e 0,0101. Nas pontas do clipe a mais de 250 frames da âncora, chega a 0,208. O NPE alto das pontas (0,1221 na Tabela 7) vem de frames longe das âncoras, e não da ponta em si.

![Figura 6 — NPE mediano da propagação (à esquerda, em escala logarítmica) e fração de frames com NPE > 0,05 (à direita), pela distância à âncora aceita mais próxima, separados pela situação do detector naquele frame.](../outputs/figures/relatorio/fig4_deriva.png)

**A suavização S-G entre bordas erradas.** A Figura 7 mostra uma lacuna de 4 a 25 frames com as duas bordas erradas: o detector toma o arco da grande área pelo círculo central dos dois lados, e a interpolação no meio da lacuna dá NPE de 7,1. Das 537 lacunas de 4 a 25 frames do test, 331 têm as duas bordas erradas, 106 têm uma e 99 têm as duas certas.

![Figura 7 — A suavização S-G (Bassek) numa lacuna de 4 a 25 frames com as duas bordas erradas (SNGS-121, lacuna 2–26): borda esquerda (detector), meio da lacuna (suavização S-G) e borda direita (detector).](../outputs/figures/relatorio/fig7_lacuna.jpg)

# 8. Limitações e trabalho futuro

**Sensibilidade: os ganhos medidos nos subconjuntos pequenos não se sustentam.** A sensibilidade perturbou um parâmetro de cada vez, a ±25% e ±50%, em subconjuntos em que um frame ou uma imagem vale de 0,017 a 0,029 da métrica. Os 15 candidatos com ganho ≥ 0,02 nesses subconjuntos foram confirmados num subconjunto maior, com intervalo por bootstrap. Só um passou: o limiar de contraste das marcações no GSR reduzido de 30 para 15, com +0,034 [+0,003; +0,065]. Os outros ganhos não se sustentaram, e dois trocaram de sinal. **O candidato foi recusado:** o intervalo sorteava clipes, que não são independentes, e por jogo o efeito tem sinal oposto (+0,127 no jogo 4, de contraste baixo; −0,046 no jogo 9, com o NPE mediano indo de 0,0056 para 0,0130). Com 3 jogos no treino, não há como prever o efeito nos jogos do test. Nenhum parâmetro mudou.

**Segmentação e iluminação.** O gramado por matiz falha na sombra azulada e sem croma de um jogo diurno da validação (jogo 3), em que a máscara cobre cerca de 52% do campo; 13 dos 18 clipes sem âncora da validação são desse jogo. Só pela cor, calibrada no treino, não há como aceitar aquela sombra sem aceitar a arquibancada, cujo croma é o mesmo. O limiar global das marcações também enfrenta o contraste de cada jogo, como mostra o próprio candidato recusado. Duas variantes foram testadas na calibração da segmentação e reprovadas: a histerese no gramado, que recuperou parte do jogo 3 mas vazou e perdeu precisão num jogo de contraste baixo, e o limiar relativo nas marcações, que não recuperou o jogo 3 e perdeu precisão noutro jogo. **Trabalho futuro:** um limiar adaptativo local para as marcações (Niblack, 1986; Sauvola & Pietikäinen, 2000), no lugar do limiar global por base; a filtragem homomórfica (Gonzalez & Woods, 2018) ou o Retinex (Land & McCann, 1971), para separar a iluminação da refletância; e, para a sombra do jogo 3, um espaço invariante a sombra (Finlayson et al., 2006).

**Enquadramento central.** O detector depende de duas retas em cada uma de duas famílias de paralelas e não fecha a homografia nas vistas do meio-campo, onde há uma reta transversal só. Isso deixa clipes inteiros sem âncora (Seção 7). O círculo central com uma reta não basta: é uma configuração degenerada, porque sobra uma família de um parâmetro de homografias que preservam a cônica e a reta, como se viu no ajuste do gabarito antes da rodada. **Trabalho futuro:** fechar a homografia com o círculo central, a linha do meio e uma lateral, que essas vistas mostram, usando correspondências como as do PnLCalib (Gutiérrez-Pérez & Agudo, 2026): interseções de linha com elipse e pontos de tangência. A ablação com correspondências de pontos e RANSAC foi neutra no treino, mas entrava depois da hipótese 2 + 2; as vistas do meio-campo são justamente o caso em que essa hipótese não existe.

**Deriva.** A propagação a partir de uma âncora se degrada com a distância: as pontas a mais de 250 frames de uma âncora têm NPE mediano de 0,208. As linhas guiadas reduzem a deriva, mas não a eliminam.

**Erro sistemático do detector.** A verificação temporal por maioria de poucos vizinhos não pega um erro que o detector repete em frames seguidos, como nas seis âncoras erradas do SNGS-190.

**O gabarito do GSR.** O gabarito é ele mesmo um ajuste às linhas anotadas, feito pela mesma função do refino do detector (Seção 4), e falha onde as linhas anotadas não determinam a homografia; na geração do gabarito, antes da rodada, 2,33% dos frames do test ficaram sem homografia de gabarito. No intervalo do HSB do SNGS-150, a cobertura do detector é 0,64 contra os frames com gabarito e 0,07 contra os frames com pessoas: a maioria dos frames do intervalo não tem gabarito. O LocSim e a acurácia contra as linhas, que não dependem do gabarito, não são afetados; o NPE e o IoU são medidos só onde o gabarito existe. As correções de rótulo da anotação (Seção 4) vieram de uma varredura do gabarito, sem nenhuma saída do método.

**Três jogos.** O test tem 3 jogos. A variação reportada é o mínimo e o máximo entre eles, e a generalização para outros estádios e condições de luz fica sem medida.

# 9. Conclusão

**Até onde chega o pipeline clássico?** Frame a frame, chega a uma homografia boa quando responde, mas responde pouco. No WC14 test, no protocolo do KpSFR, o IoU do campo inteiro tem média de 0,5155 e mediana de 0,8634 contando como 0 as imagens sem homografia, contra 0,8962 e 0,9534 só nas 107 imagens com homografia (0,575 das 186); o IoU da parte visível fica como complemento (mediana de 0,995 nas imagens com homografia, no nosso molde). No GSR test, o detector cobre 0,505 dos frames, com LocSim@5 de 0,869 nos cobertos e 0,419 penalizado. Com a propagação, o LocSim@5 penalizado chega a 0,749.

**Quanto da diferença para o estado da arte a propagação fecha?** Cerca de 65% da distância entre o nosso detector e o AuxFlow, mas não toda: o pipeline completo (0,749) fica abaixo do NBJW sozinho (0,885) e do AuxFlow (0,929). A resposta é **não**, o pipeline clássico com propagação não alcança o estado da arte no GSR completo, numa métrica em que o próprio gabarito pelas linhas fica em 0,946. O que falta está sobretudo em onde há âncora: com âncoras de gabarito escolhidas sem o detector, a mesma propagação chegaria a 0,922 (análise posterior à rodada). No HSB, onde o NBJW falha, o pipeline completo fica acima dele (61,7 contra 43,15), e a propagação isolada é comparável à do AuxFlow (81,4 contra 83,67), com as diferenças de protocolo da Seção 6.4.

**A propagação ganha mais sobre um detector fraco?** **No valor absoluto, sim; no sentido de correção, a hipótese não se confirma.** O ganho é de +0,330, contra +0,044 do AuxFlow sobre o NBJW, mas vem de preencher os frames sem homografia. Nos frames que os dois cobrem, a propagação tira cerca de 40% do erro residual (1 − LocSim@5) do nosso detector, e o AuxFlow, cerca de 38% do erro do NBJW: uma fração parecida, sobre um detector fraco e sobre um forte. Contra as linhas anotadas, a correção nesses frames é ainda menor (acurácia a 5 px de 0,784 para 0,807). A ressalva é que o nosso conjunto comum são os frames fáceis do nosso detector, e o do AuxFlow é o test inteiro. A condição das âncoras se confirmou: a verificação temporal baixa as âncoras erradas de 28,3% das candidatas para 2,2% das aceitas, e a propagação com âncoras verificadas (0,749) supera a âncora ingênua (0,571). **Um sistema sem GPU é viável para uso offline, mas não é leve:** com a máquina inteira, só a série do detector leva cerca de 630 s por clipe de 750 frames, contra 292 s do AuxFlow inteiro com GPU; por núcleo, são 4,76 s por frame, cerca de 3.570 s por clipe.

**Qual estratégia temporal entrega mais estabilidade?** **Depende da medida.** O Kalman dá a série mais lisa, com o menor tremor. A propagação é a que melhor acompanha o movimento real da câmera, com o menor deslize, e a que menos inverte a visibilidade dos jogadores: 0,8% dos jogadores-frame na interseção das séries, contra 4,4% do Kalman. A suavização S-G, com a interpolação das lacunas, herda as homografias erradas do detector e desliza mais que as outras. O custo da propagação é 127 ms por frame, pequeno frente ao detector, do qual todas as estratégias dependem.

As métricas e as tabelas do test saem de um comando, `python -m src.run --all --splits test --wc14-split test`; as figuras e as análises posteriores à rodada, de scripts à parte (Apêndice B). O `--all` reaproveita os caches quando as chaves batem. Do zero, nesta máquina, leva mais de 10 h só no test e mais de 30 h nas três partições do GSR, o padrão do `--all`: a série do detector e a propagação custam, juntas, cerca de 756 s de parede por clipe. O determinismo do detector foi conferido bit a bit entre execuções independentes.

# Referências

- Bassek, M., Theiner, J., Ewerth, R., Memmert, D., Raabe, D. (2025). Broadcast analytics – an evaluation of video-based tracking systems with constrained player visibility. Science and Medicine in Football. doi:10.1080/24733938.2025.2533808. Código: github.com/spoho-datascience/broadcast-analytics.
- Bhattacharyya, A. (1943). On a measure of divergence between two statistical populations defined by their probability distributions. Bulletin of the Calcutta Mathematical Society, 35, 99–109.
- Bouguet, J.-Y. (2001). Pyramidal implementation of the affine Lucas Kanade feature tracker. Intel Corporation, relatório técnico.
- Chu, Y.-J., Su, J.-W., Hsiao, K.-W., Lien, C.-Y., Fan, S.-H., Hu, M.-C., Lee, R.-R., Yao, C.-Y., Chu, H.-K. (2022). Sports field registration via keypoints-aware label condition. IEEE/CVF CVPR Workshops (CVPRW), p. 3522–3529. [KpSFR] Código de avaliação: github.com/ericsujw/KpSFR.
- Citraro, L., Márquez-Neila, P., Savarè, S., Jayaram, V., Dubout, C., Renaut, F., Hasfura, A., Ben Shitrit, H., Fua, P. (2020). Real-time camera pose estimation for sports fields. Machine Vision and Applications, 31(3), 16.
- Claasen, P. J., de Villiers, J. P. (2024). Video-based sequential Bayesian homography estimation for soccer field registration. Expert Systems with Applications, 252, 124156. [BHITK; o nome é o usado pelo AuxFlow]
- Duda, R. O., Hart, P. E. (1972). Use of the Hough transformation to detect lines and curves in pictures. Communications of the ACM, 15(1), 11–15.
- Evangelidis, G. D., Psarakis, E. Z. (2008). Parametric image alignment using enhanced correlation coefficient maximization. IEEE Transactions on Pattern Analysis and Machine Intelligence, 30(10), 1858–1865.
- Farin, D., Krabbe, S., de With, P. H. N., Effelsberg, W. (2004). Robust camera calibration for sport videos using court models. Proc. SPIE 5307, Storage and Retrieval Methods and Applications for Multimedia, 80–91.
- Finlayson, G. D., Hordley, S. D., Lu, C., Drew, M. S. (2006). On the removal of shadows from images. IEEE Transactions on Pattern Analysis and Machine Intelligence, 28(1), 59–68.
- Fischler, M. A., Bolles, R. C. (1981). Random sample consensus: a paradigm for model fitting with applications to image analysis and automated cartography. Communications of the ACM, 24(6), 381–395.
- Fitzgibbon, A. W., Fisher, R. B. (1995). A buyer's guide to conic fitting. Proc. British Machine Vision Conference (BMVC), 513–522.
- Gonzalez, R. C., Woods, R. E. (2018). Digital Image Processing, 4ª ed. Pearson.
- Gutiérrez-Pérez, M., Agudo, A. (2024). No bells, just whistles: Sports field registration by leveraging geometric properties. IEEE/CVF CVPR Workshops (CVPRW), p. 3325–3334. [NBJW]
- Gutiérrez-Pérez, M., Agudo, A. (2026). PnLCalib: Sports field registration via points and lines optimization. Computer Vision and Image Understanding, 267, 104712.
- Hampel, F. R. (1974). The influence curve and its role in robust estimation. Journal of the American Statistical Association, 69(346), 383–393.
- Hartley, R., Zisserman, A. (2004). Multiple View Geometry in Computer Vision, 2ª ed. Cambridge University Press.
- Homayounfar, N., Fidler, S., Urtasun, R. (2017). Sports field localization via deep structured models. IEEE/CVF CVPR, p. 4012–4020. [WC14]
- Kalal, Z., Mikolajczyk, K., Matas, J. (2010). Forward-backward error: automatic detection of tracking failures. International Conference on Pattern Recognition (ICPR), p. 2756–2759.
- Kalman, R. E. (1960). A new approach to linear filtering and prediction problems. Journal of Basic Engineering, 82(1), 35–45.
- Land, E. H., McCann, J. J. (1971). Lightness and Retinex theory. Journal of the Optical Society of America, 61(1), 1–11.
- Lucas, B. D., Kanade, T. (1981). An iterative image registration technique with an application to stereo vision. International Joint Conference on Artificial Intelligence (IJCAI), p. 674–679.
- Maglo, A., Orcesi, A., Denize, J., Pham, Q. C. (2023). Individual locating of soccer players from a single moving view. Sensors, 23(18), 7938.
- Magera, F., Hoyoux, T., Barnich, O., Van Droogenbroeck, M. (2025). BroadTrack: Broadcast camera tracking for soccer. IEEE/CVF WACV, p. 6177–6187.
- Manafifard, M., Ebadi, H., Abrishami Moghaddam, H. (2017). A survey on player tracking in soccer videos. Computer Vision and Image Understanding, 159, 19–46.
- Matas, J., Galambos, C., Kittler, J. (2000). Robust detection of lines using the progressive probabilistic Hough transform. Computer Vision and Image Understanding, 78(1), 119–137.
- Niblack, W. (1986). An Introduction to Digital Image Processing. Prentice-Hall.
- Otsu, N. (1979). A threshold selection method from gray-level histograms. IEEE Transactions on Systems, Man, and Cybernetics, 9(1), 62–66.
- Rauch, H. E., Tung, F., Striebel, C. T. (1965). Maximum likelihood estimates of linear dynamic systems. AIAA Journal, 3(8), 1445–1450.
- Sampson, P. D. (1982). Fitting conic sections to "very scattered" data: an iterative refinement of the Bookstein algorithm. Computer Graphics and Image Processing, 18(1), 97–108.
- Sauvola, J., Pietikäinen, M. (2000). Adaptive document image binarization. Pattern Recognition, 33(2), 225–236.
- Savitzky, A., Golay, M. J. E. (1964). Smoothing and differentiation of data by simplified least squares procedures. Analytical Chemistry, 36(8), 1627–1639.
- Somers, V., Joos, V., Cioppa, A., Giancola, S., et al. (2024). SoccerNet Game State Reconstruction: End-to-end athlete tracking and identification on a minimap. IEEE/CVF CVPR Workshops (CVPRW).
- Theiner, J., Ewerth, R. (2023). TVCalib: Camera calibration for sports field registration in soccer. IEEE/CVF WACV, p. 1166–1175.
- Ziegler, J., Matthes, D., Frenzel, P., Fuchs, M. (2026). AuxFlow: Anchor-grounded homography estimation through flow-guided auxiliary points for soccer field registration and player localization. Computer Vision and Image Understanding, 264, 104662.

# Apêndice A — Tabelas completas da rodada do test

Geradas por `scripts/relatorio/numeros.py` a partir dos CSVs da rodada (`outputs/runs/rodada_test/tabelas/`), cada um com o commit do método e o dos scripts das tabelas, e, nas tabelas marcadas, das análises posteriores à rodada (`outputs/runs/rodada_test/pos_rodada/`). A coluna "mín.–máx. por jogo (bootstrap de 3 jogos)" é o intervalo de 95% do bootstrap que sorteia jogos (2.000 reamostragens): com 3 jogos, há só 10 reamostragens distintas, e o intervalo é o mínimo e o máximo entre os jogos (T6). O teto condicionado às âncoras é a propagação a partir da homografia de gabarito nos frames das âncoras verificadas.

| Série | Cobertura | mín.–máx. por jogo (bootstrap de 3 jogos) | NPE mediano (média) | IoU_whole mediano | mAP-LocSim penalizado | mín.–máx. por jogo (bootstrap de 3 jogos) |
|---|---|---|---|---|---|---|
| detector | 0,505 | 0,447–0,617 | 0,0072 (0,636) | 0,941 | 0,397 | 0,322–0,527 |
| suavização S-G (Bassek) | 0,680 | 0,639–0,750 | 0,0126 (2,748) | 0,910 | 0,425 | 0,334–0,571 |
| S-G robusta | 0,665 | 0,624–0,734 | 0,0097 (4,278) | 0,924 | 0,453 | 0,354–0,599 |
| Kalman + RTS | 0,680 | 0,639–0,750 | 0,0113 (3,569) | 0,920 | 0,464 | 0,357–0,616 |
| propagação | 0,897 | 0,838–1,000 | 0,0105 (0,066) | 0,916 | 0,710 | 0,616–0,871 |
| propagação sem linhas | 0,897 | 0,838–1,000 | 0,0122 (0,079) | 0,888 | 0,678 | 0,583–0,844 |
| propagação sem fluxo | 0,897 | 0,838–1,000 | 0,1248 (0,825) | 0,827 | 0,350 | 0,265–0,480 |
| âncora ingênua /150 | 1,000 | 1,000–1,000 | 0,0262 (3,608) | 0,814 | 0,544 | 0,445–0,736 |
| teto condicionado às âncoras | 0,897 | 0,838–1,000 | 0,0064 (0,040) | 0,944 | 0,725 | 0,629–0,876 |

: Tabela T1 (a) — GSR test, 49 clipes, 3 jogos: cobertura e geometria.

| Série | LocSim@5 penalizado | mín.–máx. por jogo (bootstrap de 3 jogos) | Nos cobertos | mín.–máx. por jogo (bootstrap de 3 jogos) |
|---|---|---|---|---|
| detector | 0,419 | 0,341–0,555 | 0,869 | 0,810–0,931 |
| suavização S-G (Bassek) | 0,446 | 0,352–0,601 | 0,681 | 0,568–0,816 |
| S-G robusta | 0,478 | 0,374–0,632 | 0,747 | 0,619–0,876 |
| Kalman + RTS | 0,490 | 0,378–0,651 | 0,749 | 0,611–0,884 |
| propagação | 0,749 | 0,650–0,920 | 0,833 | 0,759–0,920 |
| propagação sem linhas | 0,715 | 0,614–0,892 | 0,796 | 0,716–0,892 |
| propagação sem fluxo | 0,366 | 0,276–0,504 | 0,407 | 0,330–0,504 |
| âncora ingênua /150 | 0,571 | 0,470–0,772 | 0,571 | 0,470–0,772 |
| teto condicionado às âncoras | 0,763 | 0,661–0,925 | 0,849 | 0,771–0,925 |

: Tabela T1 (b) — GSR test: LocSim@5.

| Série | Penalizado, clipes com âncora | mín.–máx. por jogo (bootstrap de 3 jogos) | Fração ao teto condicionado | mín.–máx. por jogo (bootstrap de 3 jogos) |
|---|---|---|---|---|
| detector | 0,465 | 0,407–0,555 | — | — |
| suavização S-G (Bassek) | 0,495 | 0,420–0,601 | 0,078 | 0,029–0,124 |
| S-G robusta | 0,530 | 0,446–0,632 | 0,171 | 0,091–0,216 |
| Kalman + RTS | 0,544 | 0,451–0,651 | 0,207 | 0,102–0,262 |
| propagação | 0,833 | 0,759–0,920 | 0,959 | 0,925–0,986 |
| propagação sem linhas | 0,796 | 0,716–0,892 | 0,861 | 0,821–0,911 |
| propagação sem fluxo | 0,407 | 0,330–0,504 | −0,155 | −0,180 a −0,137 |
| âncora ingênua /150 | 0,618 | 0,519–0,772 | 0,442 | 0,355–0,586 |
| teto condicionado às âncoras | 0,849 | 0,771–0,925 | — | — |

: Tabela T1 (c) — GSR test: LocSim@5 penalizado nos 44 clipes com âncora e fração da distância ao teto condicionado às âncoras, (série − detector) / (teto − detector).

| Série | NPE mediano | LocSim@5 penalizado | Nos cobertos |
|---|---|---|---|
| detector | 0,0072 | 0,869 | 0,869 |
| suavização S-G (Bassek) | 0,0081 | 0,827 | 0,827 |
| S-G robusta | 0,0073 | 0,868 | 0,873 |
| Kalman + RTS | 0,0081 | 0,873 | 0,873 |
| propagação | 0,0066 | 0,922 | 0,930 |
| propagação sem linhas | 0,0069 | 0,916 | 0,924 |
| propagação sem fluxo | 0,0294 | 0,665 | 0,671 |
| âncora ingênua /150 | 0,0087 | 0,818 | 0,818 |
| teto condicionado às âncoras | 0,0032 | 0,926 | 0,935 |

: Tabela T1b — Conjunto comum: os 18.133 frames com homografia do detector.

| Clipe | Intervalo | NBJW (tab. 3) | (1) só propagação: penalizado / cobertura | (2) detector: penalizado / nos cobertos / cobertura | (3) pipeline: penalizado / nos cobertos / cobertura |
|---|---|---|---|---|---|
| SNGS-117 | 350–500 | 27,8 | 91,7 / 1,00 | 0,0 / — / 0,00 | 59,4 / 59,4 / 1,00 |
| SNGS-123 | 100–200 | 37,9 | 59,9 / 1,00 | 10,1 / 39,1 / 0,26 | 59,1 / 59,1 / 1,00 |
| SNGS-124 | 250–320 | 68,0 | 50,8 / 1,00 | 40,6 / 82,4 / 0,49 | 70,3 / 70,3 / 1,00 |
| SNGS-128 | 90–0 | 15,8 | 97,4 / 1,00 | 0,0 / 0,0 / 0,05 | 0,0 / — / 0,00 |
| SNGS-136 | 60–280 | 45,7 | 87,2 / 1,00 | 44,2 / 94,0 / 0,47 | 85,7 / 85,7 / 1,00 |
| SNGS-138 | 130–230 | 42,5 | 96,5 / 1,00 | 0,0 / 0,0 / 0,01 | 0,0 / — / 0,00 |
| SNGS-150 | 150–280 | 44,6 | 55,4 / 1,00 | 6,6 / 96,2 / 0,07 | 56,7 / 56,7 / 1,00 |
| SNGS-187 | 300–400 | 59,5 | 94,7 / 1,00 | 21,8 / 88,0 / 0,25 | 95,0 / 95,0 / 1,00 |
| SNGS-191 | 450–500 | 13,0 | 82,5 / 1,00 | 0,0 / 0,0 / 0,20 | 77,6 / 77,6 / 1,00 |
| SNGS-193 | 550–650 | 70,2 | 86,2 / 1,00 | 30,0 / 91,7 / 0,33 | 92,1 / 92,1 / 1,00 |

: Tabela T2 (a) — HSB por clipe: LocSim@5 médio por frame (%), penalizado e nos cobertos, e cobertura nos frames com pessoas. Os intervalos seguem a numeração do artigo do AuxFlow, a partir de 0.

| Medição | Penalizado: média / mediana | Cobertos: média / mediana | Cobertura (frames com H_gt) | Cobertura (frames com pessoas) | Cobertura (por pessoa) | Por pessoa-frame: pen. / cob. |
|---|---|---|---|---|---|---|
| (1) só propagação | 81,4 / 92,7 | 81,4 / 92,7 | 1,000 | 1,000 | 1,000 | 82,9 / 82,9 |
| (2) detector | 17,7 / 0,0 | 79,7 / 95,6 | 0,267 | 0,221 | 0,252 | 20,3 / 80,5 |
| (3) pipeline | 61,7 / 71,1 | 74,5 / 86,3 | 0,831 | 0,829 | 0,827 | 64,3 / 77,7 |

: Tabela T2 (b) — HSB, todos os frames dos intervalos (%). AuxFlow, tabela 4 (média / mediana): NBJW 43,15 / 35,93; AuxFlow 83,67 / 96,15.

| Série | Penalizado: média / mediana | Cobertos: média / mediana | Cobertura (frames com H_gt) | Cobertura (frames com pessoas) | Cobertura (por pessoa) | Por pessoa-frame: pen. / cob. |
|---|---|---|---|---|---|---|
| suavização S-G (Bassek) | 20,9 / 0,0 | 52,9 / 62,7 | 0,477 | 0,396 | 0,444 | 24,0 / 54,1 |
| S-G robusta | 24,5 / 0,0 | 65,9 / 93,5 | 0,448 | 0,371 | 0,416 | 27,8 / 66,7 |

: Tabela T2 (c) — Análise posterior à rodada: as suavizações S-G sobre a série do detector, nos mesmos frames do HSB e com as colunas da T2 (b) (%).

| Cobertura | IoU_whole (média / mediana) | IoU_part (média / mediana) | NPE (média / mediana) | RE em m (média / mediana) |
|---|---|---|---|---|
| 0,575 | 0,864 / 0,913 | 0,986 / 0,995 | 0,3614 / 0,0119 | 1,615 / 0,380 |

: Tabela T3 — WC14 test, 186 imagens, só o detector, molde 105 × 68 m.

| Métrica | Média | Mediana | Imagens |
|---|---|---|---|
| iou_part | 0,9370 | 0,9800 | 107 |
| iou_whole | 0,8962 | 0,9534 | 107 |
| proj_error_m | 1,7522 | 0,3602 | 107 |
| reproj_error | 0,0439 | 0,0111 | 107 |
| iou_part (nossa convenção: imagem sem H vale 0) | 0,5390 | 0,9432 | 186 |
| iou_whole (nossa convenção: imagem sem H vale 0) | 0,5155 | 0,8634 | 186 |

: Tabela T3b — WC14 test no protocolo KpSFR (código deles sem mudança, molde 100 × 60 m). O protocolo foi aplicado só nas imagens com homografia; a literatura o reporta sobre todas. As duas últimas linhas seguem a nossa convenção: imagem sem homografia vale 0.

| Série | Cobertura | Tremor mediano / p90 (px) | Deslize mediano / p90 (px) | Pares |
|---|---|---|---|---|
| detector | 0,493 | 1,30 / 15,87 | 2,17 / 12,41 | 16.248 |
| suavização S-G (Bassek) | 0,665 | 0,47 / 16,13 | 2,86 / 72,61 | 23.879 |
| S-G robusta | 0,650 | 0,30 / 6,62 | 2,18 / 35,92 | 23.015 |
| Kalman + RTS | 0,664 | 0,16 / 2,39 | 2,21 / 23,51 | 23.895 |
| propagação | 0,898 | 0,48 / 1,85 | 1,31 / 4,17 | 32.956 |
| propagação sem fluxo | 0,898 | 0,00 / 0,00 | 4,25 / 18,92 | 32.956 |

: Tabela T4 (a) — Estabilidade no GSR test, cada série no próprio conjunto de frames. O ECC convergiu em todos os pares.

| Série | Jogadores invertidos: pen. / cobertos | Grade: pen. / cobertos | 0 visíveis: pen. / cobertos |
|---|---|---|---|
| detector | 0,535 / 0,056 | 0,562 / 0,095 | 0,514 / 0,031 |
| suavização S-G (Bassek) | 0,441 / 0,163 | 0,475 / 0,234 | 0,381 / 0,088 |
| S-G robusta | 0,439 / 0,140 | 0,469 / 0,202 | 0,395 / 0,088 |
| Kalman + RTS | 0,429 / 0,144 | 0,457 / 0,201 | 0,387 / 0,096 |
| propagação | 0,118 / 0,021 | 0,196 / 0,099 | 0,105 / 0,001 |
| propagação sem fluxo | 0,351 / 0,279 | 0,509 / 0,460 | 0,229 / 0,139 |

: Tabela T4 (b) — Visibilidade no GSR test: fração de jogadores-frame jogados para fora do quadro, de pontos da grade com rótulo trocado e de frames com 0 jogadores visíveis, penalizada (frame sem homografia conta como erro) e só nos frames cobertos.

| Série | Tremor mediano / p90 (px), trios | Deslize mediano / p90 (px), pares | Jogadores invertidos | 0 visíveis |
|---|---|---|---|---|
| detector | 1,29 / 15,50 (15.355) | 2,15 / 12,07 (16.146) | 0,050 | 0,024 |
| suavização S-G (Bassek) | 0,26 / 2,23 (15.373) | 1,90 / 8,31 (16.175) | 0,055 | 0,018 |
| S-G robusta | 0,21 / 1,12 (15.368) | 1,68 / 5,69 (16.156) | 0,044 | 0,019 |
| Kalman + RTS | 0,13 / 0,57 (15.373) | 1,71 / 5,45 (16.173) | 0,044 | 0,020 |
| propagação | 0,40 / 1,43 (15.374) | 1,38 / 4,33 (16.182) | 0,008 | 0,000 |
| propagação sem fluxo | 0,00 / 0,00 (15.374) | 3,72 / 14,77 (16.182) | 0,075 | 0,027 |

: Tabela T4b — Estabilidade e visibilidade na interseção dos frames cobertos pelas cinco séries (detector, suavização S-G (Bassek), S-G robusta, Kalman + RTS e propagação).

| Linha | LocSim@5 (penalizado, no nosso caso) | mín.–máx. por jogo (bootstrap de 3 jogos) | Nos cobertos | mín.–máx. por jogo (bootstrap de 3 jogos) | Conjunto comum (nos cobertos) |
|---|---|---|---|---|---|
| NBJW (AuxFlow, tab. 7) | 0,885 | — | — | — | — |
| AuxFlow (tab. 7) | 0,929 | — | — | — | — |
| ganho AuxFlow − NBJW | +0,044 | — | — | — | — |
| nosso detector | 0,419 | 0,341–0,555 | 0,869 | 0,810–0,931 | 0,869 |
| nossa propagação | 0,749 | 0,650–0,920 | 0,833 | 0,759–0,920 | 0,930 |
| ganho propagação − detector | +0,330 | 0,290–0,365 | −0,035 | −0,078 a −0,003 | — |

: Tabela T5 — Comparação com a tabela 7 do AuxFlow. O LocSim deles não tem frames sem homografia; o nosso é agregado sobre pessoas-frame, e a pessoa de frame sem homografia vale 0.

| Jogo | Clipes | Com âncora | Frames | Cobertura detector / propagação | LocSim@5 pen.: detector / propagação / teto condicionado |
|---|---|---|---|---|---|
| 7 | 16 | 14 | 12.000 | 0,472 / 0,874 | 0,341 / 0,676 / 0,703 |
| 8 | 19 | 16 | 14.250 | 0,447 / 0,838 | 0,360 / 0,650 / 0,661 |
| 11 | 14 | 14 | 10.500 | 0,617 / 1,000 | 0,555 / 0,920 / 0,925 |

: Tabela T6 — GSR test por jogo.

| Conjunto | Número | Com gabarito | Erradas (NPE > 0,05) |
|---|---|---|---|
| candidatas | 958 | 955 | 270 (28,3%) |
| verificáveis | 814 | 813 | 152 (18,7%) |
| aceitas | 558 | 557 | 12 (2,2%) |
| clipes sem âncora aceita | 5 | — | SNGS-127, SNGS-128, SNGS-134, SNGS-138, SNGS-147 |

: Tabela T7 — Âncoras no GSR test.

| Lacuna | Frames | suavização S-G (Bassek) | S-G robusta | propagação | propagação sem linhas |
|---|---|---|---|---|---|
| 1–3 | 1.665 | 1,000 / 0,0974 | 0,968 / 0,0324 | 0,943 / 0,0095 | 0,943 / 0,0115 |
| 4–25 | 4.624 | 1,000 / 0,8994 | 0,913 / 0,7960 | 0,886 / 0,0168 | 0,886 / 0,0247 |
| > 25 | 8.391 | 0,000 / — | 0,000 / — | 0,733 / 0,0551 | 0,733 / 0,0785 |
| pontas | 3.088 | 0,000 / — | 0,000 / — | 0,801 / 0,1221 | 0,801 / 0,1355 |

: Tabela T8 — Lacunas do detector no GSR test: cobertura / NPE mediano. As pontas são lacunas que tocam o começo ou o fim do clipe.

| Etapa | Processos | Parede (h) | Vazão (frames/s) | ms por frame num processo | s por clipe num processo | s por clipe de parede |
|---|---|---|---|---|---|---|
| série do detector (todos os frames) | 15 | 8,58 | 1,19 | 12.459 | 9.344 | 630 |
| propagação com as ablações | 10 | 1,71 | 5,97 | 1.589 | 1.192 | 126 |

: Tabela T9 (a) — Custo na rodada do test (AMD Ryzen 7 5700X, 8 núcleos e 16 threads, com RTX 5060; o detector em CPU, as máscaras da propagação em GPU). Com 15 processos em 8 núcleos, o custo por frame num processo é maior que o do perfil num núcleo sem concorrência (4,76 s por frame no detector; 127 ms na propagação).

| Etapa (AuxFlow) | Lote | Tempo por clipe (s) | FPS |
|---|---|---|---|
| NBJW keypoints | 8 | 54 | 13,9 |
| NBJW H estimation | 1 | 27 | 27,8 |
| U-Net initialization | 1 | 61 | 12,3 |
| Propagation | 1 | 150 | 5,0 |
| Overall | – | 292 | 2,6 |

: Tabela T9 (b) — Tabela 6 do AuxFlow, por clipe de 750 frames (i7-8700K com RTX 4090; o lote é o tamanho do lote na GPU ou o número de threads).

| Série | Cobertura | NPE mediano | LocSim@5 pen. | Nos cobertos | Acurácia 5 / 10 / 20 px, pen. | Acurácia 5 / 10 / 20 px, cobertos | Fração ao teto do sistema |
|---|---|---|---|---|---|---|---|
| detector | 0,505 | 0,0072 | 0,419 | 0,869 | 0,387 / 0,436 / 0,451 | 0,784 / 0,884 / 0,914 | — |
| suavização S-G (Bassek) | 0,680 | 0,0126 | 0,446 | 0,681 | 0,398 / 0,462 / 0,494 | 0,599 / 0,695 / 0,743 | 0,054 |
| S-G robusta | 0,665 | 0,0097 | 0,478 | 0,747 | 0,430 / 0,492 / 0,518 | 0,662 / 0,757 / 0,797 | 0,117 |
| Kalman + RTS | 0,680 | 0,0113 | 0,490 | 0,749 | 0,419 / 0,490 / 0,520 | 0,631 / 0,737 / 0,783 | 0,142 |
| propagação | 0,897 | 0,0105 | 0,749 | 0,833 | 0,551 / 0,650 / 0,707 | 0,613 / 0,724 / 0,787 | 0,656 |
| propagação sem linhas | 0,897 | 0,0122 | 0,715 | 0,796 | 0,508 / 0,598 / 0,656 | 0,566 / 0,666 / 0,731 | 0,588 |
| propagação sem fluxo | 0,897 | 0,1248 | 0,366 | 0,407 | 0,202 / 0,273 / 0,347 | 0,225 / 0,304 / 0,386 | −0,106 |
| âncora ingênua /150 | 1,000 | 0,0262 | 0,571 | 0,571 | 0,461 / 0,547 / 0,581 | 0,461 / 0,547 / 0,581 | 0,303 |
| teto condicionado às âncoras | 0,897 | 0,0064 | 0,763 | 0,849 | 0,576 / 0,671 / 0,727 | 0,641 / 0,748 / 0,809 | 0,684 |
| teto do sistema (âncora de gabarito /150) | 1,000 | 0,0058 | 0,922 | 0,922 | 0,733 / 0,853 / 0,902 | 0,733 / 0,853 / 0,902 | — |
| H_gt pelas linhas | 1,000 | 0,0000 | 0,929 | 0,946 | 0,849 / 0,930 / 0,949 | 0,869 / 0,952 / 0,972 | — |
| H_gt_auxflow | 0,966 | 0,0136 | 0,975 | 0,978 | 0,515 / 0,746 / 0,852 | 0,533 / 0,772 / 0,882 | — |

: Tabela T10 (a) — Análise posterior à rodada, GSR test inteiro: o teto do sistema (âncora de gabarito no primeiro frame com gabarito de cada bloco de 150 frames, com a mesma propagação), as duas homografias de gabarito como predição e a acurácia contra as linhas anotadas (contagem do SN-Calib, 960 × 540). Acurácia penalizada: frame com linhas anotadas e sem homografia vale 0. A fração ao teto do sistema é (série − detector) / (teto do sistema − detector), no LocSim@5 penalizado.

| Série | Cobertura | NPE mediano | LocSim@5 pen. | Nos cobertos | Acurácia 5 / 10 / 20 px, pen. | Acurácia 5 / 10 / 20 px, cobertos |
|---|---|---|---|---|---|---|
| detector | 1,000 | 0,0072 | 0,869 | 0,869 | 0,784 / 0,884 / 0,914 | 0,784 / 0,884 / 0,914 |
| suavização S-G (Bassek) | 1,000 | 0,0081 | 0,827 | 0,827 | 0,735 / 0,838 / 0,880 | 0,735 / 0,838 / 0,880 |
| S-G robusta | 0,995 | 0,0073 | 0,868 | 0,873 | 0,779 / 0,879 / 0,912 | 0,783 / 0,883 / 0,917 |
| Kalman + RTS | 1,000 | 0,0081 | 0,873 | 0,873 | 0,760 / 0,871 / 0,909 | 0,760 / 0,871 / 0,910 |
| propagação | 0,988 | 0,0066 | 0,922 | 0,930 | 0,807 / 0,906 / 0,937 | 0,817 / 0,917 / 0,949 |
| propagação sem linhas | 0,988 | 0,0069 | 0,916 | 0,924 | 0,787 / 0,895 / 0,931 | 0,797 / 0,906 / 0,942 |
| propagação sem fluxo | 0,988 | 0,0294 | 0,665 | 0,671 | 0,377 / 0,501 / 0,616 | 0,382 / 0,507 / 0,623 |
| âncora ingênua /150 | 1,000 | 0,0087 | 0,818 | 0,818 | 0,720 / 0,814 / 0,844 | 0,720 / 0,814 / 0,844 |
| teto condicionado às âncoras | 0,988 | 0,0032 | 0,926 | 0,935 | 0,829 / 0,920 / 0,948 | 0,839 / 0,931 / 0,960 |
| teto do sistema (âncora de gabarito /150) | 1,000 | 0,0052 | 0,934 | 0,934 | 0,794 / 0,897 / 0,933 | 0,794 / 0,897 / 0,933 |
| H_gt pelas linhas | 1,000 | 0,0000 | 0,947 | 0,947 | 0,904 / 0,964 / 0,978 | 0,904 / 0,965 / 0,979 |
| H_gt_auxflow | 0,959 | 0,0147 | 0,981 | 0,984 | 0,545 / 0,762 / 0,867 | 0,568 / 0,794 / 0,904 |

: Tabela T10 (b) — O mesmo, no conjunto comum: os frames com homografia do detector.

| Degradação | Nível | Gramado: IoU | Marcações: cobertura a 2 px | Marcações: precisão a 3 px | Retas: recall de linhas | Detector: cobertura | IoU do campo inteiro mediano | Aceitas erradas (IoU < 0,8) |
|---|---|---|---|---|---|---|---|---|
| limpa | — | 0,986 | 0,612 | 0,487 | 0,658 | 0,517 | 0,929 | 0,102 |
| ruído | 5 | 0,950 | 0,626 | 0,471 | 0,652 | 0,498 | 0,930 | 0,106 |
| ruído | 10 | 0,708 | 0,591 | 0,161 | 0,560 | 0,244 | 0,890 | 0,235 |
| ruído | 20 | 0,004 | 0,008 | 0,036 | 0,008 | 0,000 | — | — |
| borrão | 5 | 0,986 | 0,599 | 0,522 | 0,676 | 0,531 | 0,919 | 0,144 |
| borrão | 11 | 0,986 | 0,543 | 0,541 | 0,634 | 0,445 | 0,916 | 0,129 |
| borrão | 21 | 0,986 | 0,402 | 0,525 | 0,445 | 0,077 | 0,889 | 0,375 |
| sombra | 0,7 | 0,985 | 0,580 | 0,498 | 0,646 | 0,522 | 0,918 | 0,165 |
| sombra | 0,5 | 0,980 | 0,526 | 0,503 | 0,624 | 0,488 | 0,922 | 0,108 |
| sombra | 0,35 | 0,969 | 0,455 | 0,503 | 0,611 | 0,445 | 0,908 | 0,183 |
| oclusão | 0,05 | 0,982 | 0,592 | 0,484 | 0,673 | 0,522 | 0,929 | 0,119 |
| oclusão | 0,1 | 0,976 | 0,574 | 0,476 | 0,672 | 0,502 | 0,927 | 0,143 |
| oclusão | 0,2 | 0,956 | 0,533 | 0,454 | 0,674 | 0,478 | 0,916 | 0,150 |

: Tabela T11 — Análise posterior à rodada, WC14 train_val (209 imagens): robustez a degradações sintéticas, uma de cada vez (ruído: σ em 8 bits; borrão horizontal: núcleo em px; sombra: fator do L* na faixa; oclusão: fração do gramado coberta). Médias por imagem no gramado e nas marcações; recall de linhas somado nas imagens.


# Apêndice B — Protocolo, incidente e reprodução

**Congelamento.** O código congelado é o commit `418a3be`, com o SHA-1 do `config.yaml` e as chaves de cache em vigor registrados em `outputs/runs/congelamento.json` e no `docs/decisoes.md`. As chaves são as da série do detector, da propagação e do ECC, e a impressão digital do código. Cada etapa da rodada conferiu o congelamento antes e depois: o `git diff` vazio do `src/` e do config contra o `418a3be`, na árvore e no HEAD, o SHA-1 do config e as chaves. Cada etapa gravou um manifesto com a duração, o erro e a chave de cada tarefa. Todas as etapas fecharam com 0 falhas.

**Etapas.** (1) série do detector no GSR test, em todos os frames; (2) detector no WC14 test e no GSR test a cada 25 frames; (3) homografia de gabarito do test, com a chave registrada; (4) avaliação do detector; (5) propagação, com as suavizações S-G e as ablações; (6) estabilidade, visibilidade e Kalman. No fechamento, os extras (Kalman por frame, a medição de só propagação do HSB) e as tabelas T1–T9, só a partir dos caches da rodada.

**Determinismo.** Nos 1.470 frames do GSR test a cada 25, a homografia da etapa 2 saiu bit a bit igual à da série da etapa 1. É a prova de que o código congelado dá a mesma homografia em execuções independentes.

**Incidente.** A conferência de fechamento da série (`ex.verify_keys` em `src/temporal.py:93`) quebrou depois que a série terminou, com `AttributeError`: a lambda usava `a[0]`, que é a tupla da tarefa, e não o clipe. Essa conferência nunca tinha rodado antes. Nada foi corrigido durante a rodada; a conferência foi feita por fora, com o mesmo critério, e deu 735/735 chaves iguais à congelada. A rodada seguiu da etapa 2. A regra de refazer o test existe para impedir mudança do método depois de ver números do test. Aqui nenhum número tinha sido visto, o defeito estava numa conferência e não no cálculo, e a conferência de determinismo da etapa 2 provou de novo, bit a bit, que as séries eram as do código congelado. A correção (`a[0]` → `a[0][0]`) veio depois da rodada, no commit `b3bcd98`, com um teste que executa o fechamento da série.

**Defeitos achados antes do congelamento.** As conferências da sensibilidade e da rodada de validação acharam cinco defeitos silenciosos, todos corrigidos antes do congelamento:

- a chave de cache da propagação era lida do arquivo-fonte na hora da gravação, e uma edição no meio da rodada gravou 47 caches da validação com a chave errada (recalculados);
- a sensibilidade perturbava um parâmetro de fusão de retas que o detector não lia, porque a variante do detector o sobrescrevia;
- um objeto da GPU guardado por processo ignorava a perturbação de outro parâmetro;
- a perturbação do ajuste chegava ao próprio gabarito, carregado dentro da troca de parâmetros;
- o LocSim penalizado virava NaN num recorte sem nenhuma homografia, quando pela definição vale 0.

Dois foram denunciados por uma variação exatamente nula.

**Análises posteriores à rodada.** Pedidas numa revisão externa do texto, depois da rodada e sem mudar parâmetro nenhum: (1) o LocSim@5 da homografia de gabarito pelas linhas e da `H_gt_auxflow` como predição; (2) a suavização S-G (Bassek) e a S-G robusta no HSB; (3) a acurácia contra as linhas anotadas, já gravada por frame nos caches da rodada; (4) o teto do sistema, com âncoras de gabarito no primeiro frame com gabarito de cada bloco de 150 frames e a mesma propagação; (5) a robustez a degradações sintéticas, só no WC14 `train_val`, com o protocolo gravado antes de rodar e nada ajustado depois. Saem de `scripts/relatorio/pos_rodada.py`, fora do `src/`, a partir dos caches da série, da propagação e do gabarito, com as chaves conferidas contra o congelamento, chamando as funções do `src/` sem mudança. Os CSVs (`outputs/runs/rodada_test/pos_rodada/`) gravam o commit do método e o do script.

**Protocolo da robustez a degradações.** Script `scripts/relatorio/degradacao.py`, com o config congelado (SHA-1 conferido) e semente fixa por imagem, degradação e nível. As degradações, uma de cada vez, sobre a imagem original:

- ruído gaussiano de σ = 5, 10 e 20, em 8 bits;
- borrão de movimento horizontal, com núcleo linear de 5, 11 e 21 px;
- sombra: uma faixa pelo centroide do gramado anotado, com orientação sorteada e largura igual a metade da extensão do gramado na direção normal a ela, em que o L\* é multiplicado por 0,7, 0,5 e 0,35, com bordas em rampa de 0,05 da altura;
- oclusão: elipses cheias de 0,6 × 1,8 m na escala local da homografia de gabarito, com cores de uniforme, sobre o gramado, até cobrir 5%, 10% e 20% dele. Na folha de depuração, as elipses saem maiores que os jogadores da imagem; como o nível controla a fração coberta, isso muda o número de elipses, e não a área coberta.

As medidas são a média por imagem do IoU do gramado, a cobertura a 2 px e a precisão a 3 px das marcações, o recall de linhas (linhas do modelo visíveis com um segmento casado) e, no detector, a cobertura, o IoU do campo inteiro mediano nas cobertas e a fração de aceitas com IoU < 0,8. As aceitas erradas entram na regra da "etapa que quebra primeiro" pelo complemento, a fração de aceitas certas.

**Reprodução.** O código vem de três commits: o método congelado (`418a3be`), a correção da conferência (`b3bcd98`) e o `--all` (`38512a5`). Nenhum dos dois últimos muda saídas: a chave da série não inclui o `temporal.py`, o `run.py` não entra em nenhuma chave, e o teste de fumaça do `--all` usou os caches da série e da propagação com as chaves batendo. O caminho inteiro do test roda com `python -m src.run --all --splits test --wc14-split test`. As tabelas saem dos scripts versionados em `scripts/rodada_test/`, fora do `src/` para não mudar a impressão digital do código congelado, e cada tabela grava o commit do método e o dos scripts. As figuras novas deste relatório saem de `scripts/relatorio/figuras.py`, e as de falha, de `scripts/rodada_test/analise_falhas.py`.
