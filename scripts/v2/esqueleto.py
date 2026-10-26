"""Gera o esqueleto do v2 (docs/05-melhorias-plano.md, regra 1) a partir do v1, uma vez:
src/ -> src_v2/ e tests/ -> tests_v2/ com o pacote trocado (imports, caminhos literais e
`python -m src.run`), e config.yaml -> config_v2.yaml com saídas próprias. Os caches e os
manifestos do v2 vão para paths.cache e paths.runs (outputs/cache_v2, outputs/runs_v2), e as
outras saídas da CLI para outputs/v2, para não tocar em nenhum arquivo do v1. Recusa rodar
se o destino já existir. Uso (da raiz): scripts/v2/esqueleto.py"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = re.compile(r"\bsrc(?=[./])")              # src.x, src/x; não pega _SRC nem src_v2
ALL = [(PKG, "src_v2"), (re.compile(r"\bfrom src import\b"), "from src_v2 import"), (re.compile(r'"src"'), '"src_v2"'),
       (re.compile(r'\(ROOT / "config\.yaml"\)'), '(ROOT / "config_v2.yaml")'),
       (re.compile(r'path\("outputs"\) / "cache"'), 'path("cache")'),
       (re.compile(r'path\("outputs"\) / "runs"'), 'path("runs")')]


def convert(src_dir, dst_dir):
    assert not dst_dir.exists(), f"{dst_dir} já existe"
    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns("__pycache__"))
    n = 0
    for f in dst_dir.rglob("*.py"):
        s = f.read_text(encoding="utf-8")
        t = s
        for pat, rep in ALL:
            t = pat.sub(rep, t)
        if t != s:
            f.write_text(t, encoding="utf-8", newline="")
            n += 1
    return n


if __name__ == "__main__":
    print("src_v2:", convert(ROOT / "src", ROOT / "src_v2"), "arquivos trocados")
    print("tests_v2:", convert(ROOT / "tests", ROOT / "tests_v2"), "arquivos trocados")
    for f in sorted((ROOT / "tests_v2").glob("test_*.py")):       # nome de módulo único: o pytest coleta tests/ e tests_v2/ juntos
        f.rename(f.with_name("test_v2_" + f.name[len("test_"):]))
    cfg = (ROOT / "config.yaml").read_text(encoding="utf-8")
    old = "  outputs: outputs\n  debug: outputs/debug\n"
    assert cfg.count(old) == 1, "bloco paths do config.yaml mudou"
    new = ("  outputs: outputs/v2               # v2: saídas da CLI fora das do v1 (docs/05-melhorias-plano.md, regra 1)\n"
           "  debug: outputs/v2/debug\n"
           "  cache: outputs/cache_v2           # caches do v2 (os do v1 ficam em outputs/cache, só leitura)\n"
           "  runs: outputs/runs_v2             # manifestos do v2\n")
    dst = ROOT / "config_v2.yaml"
    assert not dst.exists()
    dst.write_text("# v2 (branch v2-melhorias): cópia do config.yaml do v1; muda só por entrada em docs/decisoes.md.\n"
                   + cfg.replace(old, new), encoding="utf-8", newline="")
    print("config_v2.yaml gravado")
