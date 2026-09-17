# CLAUDE.md

## O que é este projeto

Registro de campo de futebol a partir de vídeo de broadcast, usando **apenas
processamento digital de imagens clássico** — sem redes neurais. Estima a
homografia entre o frame e o modelo do campo, e mede quanto a propagação
temporal por fluxo óptico recupera dos erros do detector.

Disciplina: Processamento Digital de Imagens.
Entregável: sistema funcionando, rodável com um comando, que produz as métricas
e as figuras.

## Leia antes de qualquer coisa

- `docs/00-problema.md` — o quê e o porquê
- `docs/01-metodo.md` — **especificação normativa** do pipeline
- `docs/02-dados.md` — datasets, formatos, sistema de coordenadas do modelo
- `docs/03-plano.md` — fatias de implementação, em ordem

## Regra de ouro

**Nada de aprendizado profundo.** Sem CNN, sem detector de keypoint treinado, sem
pesos pré-treinados. A pergunta do projeto é justamente quanto se consegue sem
isso. Se você achar que precisa de uma rede, está resolvendo o problema errado —
pare e discuta.

Métodos clássicos de aprendizado que são parte do ferramental de PDI (k-means
para quantização de cor, RANSAC, mínimos quadrados) são permitidos e esperados.

**Toda constante vai para `config.yaml`**, com comentário citando a origem:
artigo, norma do campo, ou "empírico, calibrado na partição de treino". Nunca
hardcode um limiar no meio de uma função.

## Stack

- Python 3.11+, `uv` para dependências
- OpenCV, numpy, scipy, matplotlib, pytest
- **Sem** torch, tensorflow, ultralytics ou equivalentes
- CLI única: `python -m src.run`

## Convenções

- **Dois espaços de coordenadas, nunca confundidos:**
  - *imagem* — pixels, origem no canto superior esquerdo, `(u, v)`
  - *campo* — metros, origem no centro do gramado, `(X, Y)`
  - Toda função declara no docstring em qual espaço opera. Variáveis de imagem
    usam `u, v`; de campo, `X, Y`. Nunca `x, y` sozinho.
- Homografia sempre no sentido **campo → imagem** (`H @ [X, Y, 1]`). A inversa é
  calculada onde for preciso, nunca armazenada em paralelo.
- Imagens em BGR quando vêm do OpenCV. Converta explicitamente e nomeie a
  variável com o espaço de cor (`frame_hsv`, `mask_grass`).
- Nomes de variáveis em inglês, comentários e docs em português.

## O que NÃO fazer

- Não criar abstração antes de ter dois casos de uso reais.
- Não empilhar operações morfológicas "para melhorar" sem medir o efeito na
  métrica final. Cada etapa do pipeline precisa justificar sua existência com
  número.
- Não ajustar limiar olhando uma imagem. Ajuste na partição de treino, meça na de
  teste.
- Não mexer em `data/` — somente leitura, e está no `.gitignore`.
- Resultado ruim é resultado. Não conserte a métrica, investigue a causa.

## Fluxo de trabalho

1. Antes de codar uma fatia, escreva o plano e espere aprovação.
2. Uma fatia por vez, cada uma com teste.
3. `pytest` tem que passar antes de seguir.
4. **Toda etapa visual precisa de um modo de depuração** que salve a imagem
   intermediária em `outputs/debug/`. Em PDI, olhar o resultado é parte do
   método, não luxo.
5. Registre decisões não óbvias em `docs/decisoes.md`.
6. Atalho consciente recebe `# TODO(divida):` com a razão.
