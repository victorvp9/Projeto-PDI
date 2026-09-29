# Registro de campo de futebol com PDI clássico

Estima a homografia entre frames de broadcast e o modelo do campo usando apenas
processamento digital de imagens clássico — cor, morfologia, Hough, ajuste de
cônica, RANSAC — e mede quanto a propagação temporal por fluxo óptico recupera
dos erros do detector.

```bash
uv sync                  # CPU
uv sync --extra gpu      # opcional: máscaras do 6c na GPU NVIDIA (CuPy), mesmo resultado
python -m src.run --all
```

Com o extra `gpu` e uma placa NVIDIA, as máscaras da propagação temporal (6c) rodam
na GPU sozinhas (`temporal.use_gpu` no `config.yaml`); sem ele, na CPU. A saída é a
mesma pixel a pixel (`tests/test_temporal.py::test_gpu_masks_equal_cpu`).

Processos longos podem ser congelados e retomados:
`powershell -ExecutionPolicy Bypass -File pausa.ps1 pausar|continuar|estado`.
A série do detector e o 6c gravam cada clipe ao terminar, e o mesmo comando retoma
dos que faltam.

Comece por `docs/00-problema.md`. Dados não versionados — ver `docs/02-dados.md`.
