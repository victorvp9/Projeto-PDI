# Registro de campo de futebol com PDI clássico

Estima a homografia entre frames de broadcast e o modelo do campo usando apenas
processamento digital de imagens clássico — cor, morfologia, Hough, ajuste de
cônica, RANSAC — e mede quanto a propagação temporal por fluxo óptico recupera
dos erros do detector.

## Instalação e reprodução

Instale com `uv sync` e rode tudo com `uv run`:

```bash
uv sync                  # CPU
uv sync --extra gpu      # opcional: máscaras do 6c na GPU NVIDIA (CuPy), mesmo resultado
uv run python -m src.run --all --splits test --wc14-split test
```

Esse comando produz as métricas e as tabelas do test (T1–T9). As figuras saem de
`scripts/relatorio/figuras.py` e `scripts/rodada_test/analise_falhas.py` (da raiz, com `PYTHONPATH=.`).
O `--all` padrão, sem `--splits`/`--wc14-split`, roda as três partições do GSR, leva mais de 30 h e não produz as tabelas do test.

Os resultados foram produzidos com o OpenCV fixado no `uv.lock`. Outra versão do OpenCV
pode mudar a detecção das linhas: com o OpenCV 4.9, a revisão de código viu 2 falhas em
`tests/test_lines.py`.

Com o extra `gpu` e uma placa NVIDIA, as máscaras da propagação temporal (6c) rodam
na GPU sozinhas (`temporal.use_gpu` no `config.yaml`); sem ele, na CPU. A saída é a
mesma pixel a pixel (`tests/test_temporal.py::test_gpu_masks_equal_cpu`).

Processos longos podem ser congelados e retomados:
`powershell -ExecutionPolicy Bypass -File pausa.ps1 pausar|continuar|estado`.
A série do detector e o 6c gravam cada clipe ao terminar, e o mesmo comando retoma
dos que faltam.

Comece por `docs/00-problema.md`. Dados não versionados — ver `docs/02-dados.md`.

## Limitações conhecidas

Dois defeitos dos caches, achados na revisão de código de 2026-10-14 e não corrigidos
(o `src/` está congelado; registro em `docs/decisoes.md`):

- **A série do detector é lida sem conferir a chave.** O 6c e a Fatia 7 carregam
  `outputs/cache/detector/` sem olhar a chave gravada. Se um trecho da série falhar e
  sobrar o arquivo antigo do clipe, o 6c usa a série velha e grava o resultado com a
  chave atual, e uma nova rodada não o refaz.
- **Chaves incompletas.** A da série não inclui `eval.quality_grid_px`, a seção `pitch`,
  nem `evaluate.py`/`pitch_model.py`. A do 6c não inclui as seções `eval`, `gsr`,
  `gsr_label_fixes` e `pitch`. A do ECC não inclui `temporal.compact_dilate_frac`, as
  seções `segment`/`lines`, nem `segment.py`/`lines.py`.

**Regra:** mudou algum desses itens, apague os caches correspondentes antes de rodar de novo:

| mudou | apagar |
|---|---|
| `eval.quality_grid_px`, `pitch`, `evaluate.py`, `pitch_model.py` | `outputs/cache/detector/` e `outputs/cache/eval_6c/` |
| `eval`, `gsr`, `gsr_label_fixes` | `outputs/cache/eval_6c/` |
| `temporal.compact_dilate_frac`, `segment`, `lines`, `segment.py`, `lines.py` | `outputs/cache/ecc/` |
| falhou um trecho da série | o `.pkl` do clipe em `outputs/cache/eval_6c/<partição>/`, depois de refazer a série |

Antes de qualquer rodada nova em dados novos, corrija os dois defeitos num lote só, com
a regravação conferida das chaves.

**Os números relatados não são afetados.** Na rodada do test, todas as chaves foram conferidas:
as da série (735/735) e as do 6c (49/49). O `config.yaml` não mudou desde o congelamento (`418a3be`).
