"""Leitura única do config.yaml."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))


def path(key: str) -> Path:
    """Caminho absoluto de `paths.<key>` do config."""
    return ROOT / CFG["paths"][key]
