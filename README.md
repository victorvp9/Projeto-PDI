# Registro de campo de futebol com PDI clássico

Estima a homografia entre frames de broadcast e o modelo do campo usando apenas
processamento digital de imagens clássico — cor, morfologia, Hough, ajuste de
cônica, RANSAC — e mede quanto a propagação temporal por fluxo óptico recupera
dos erros do detector.

```bash
uv sync
python -m src.run --all
```

Comece por `docs/00-problema.md`. Dados não versionados — ver `docs/02-dados.md`.
