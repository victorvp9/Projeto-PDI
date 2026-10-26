"""v2, achados 2 e 3 da revisão de 2026-10-14 (docs/decisoes.md): a série do detector só é
lida com a chave atual, e as chaves da série, do 6c e do ECC mudam com cada item que faltava."""
import numpy as np
import pytest

from src_v2 import consequence as C
from src_v2 import temporal as T
from src_v2.config import CFG


def test_series_is_read_only_with_the_current_key(tmp_path, monkeypatch):
    """Achado 2: a série gravada com outra chave (trecho com falha que deixou a série velha)
    não é usada; a da chave atual é."""
    monkeypatch.setattr(T, "_series_path", lambda c: tmp_path / f"{c.name}.npz")
    clip = tmp_path / "SNGS-000"
    np.savez(T._series_path(clip), key="chave-velha", H=np.eye(3)[None])
    with pytest.raises(RuntimeError):
        T.load_series(clip)
    np.savez(T._series_path(clip), key=T._series_key(), H=np.eye(3)[None])
    assert np.array_equal(T.load_series(clip)["H"], np.eye(3)[None])
    with pytest.raises(FileNotFoundError):
        T.load_series(tmp_path / "SNGS-001")


CONFIG_ITEMS = [  # (chave, seção do config, item): o que faltava em cada chave (achado 3)
    ("série", "eval", "quality_grid_px"), ("série", "pitch", "sample_step_m"),
    ("6c", "eval", "grid_dx_m"), ("6c", "gsr", "min_persons"), ("6c", "gsr_label_fixes", "SNGS-038"), ("6c", "pitch", "sample_step_m"),
    ("ECC", "temporal", "compact_dilate_frac"), ("ECC", "segment", "common"), ("ECC", "lines", "tol_frac"),
]
KEYS = {"série": lambda: T._series_key(), "6c": lambda: T._eval_6c_key(), "ECC": lambda: C._ecc_key()}


@pytest.mark.parametrize("key, section, item", CONFIG_ITEMS)
def test_key_covers_config_item(monkeypatch, key, section, item):
    before = KEYS[key]()
    monkeypatch.setitem(CFG[section], item, ["mudado"])
    assert KEYS[key]() != before, f"a chave {key} não cobre {section}.{item}"


@pytest.mark.parametrize("key, source", [("série", "evaluate.py"), ("série", "pitch_model.py"), ("6c", "evaluate.py"),
                                         ("ECC", "segment.py"), ("ECC", "lines.py")])
def test_key_covers_source_bytes(monkeypatch, key, source):
    before = KEYS[key]()
    monkeypatch.setitem(T._SRC, source, T._SRC[source] + b"\n# mudado\n")
    assert KEYS[key]() != before, f"a chave {key} não cobre os bytes de {source}"
