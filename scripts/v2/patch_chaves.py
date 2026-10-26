"""Aplica uma vez, no src_v2/, a correção dos achados 2 e 3 da revisão de 2026-10-14
(docs/decisoes.md). Só chaves e leitura conferida da série: nenhuma conta muda."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src_v2"


def sub(f, old, new, n=1):
    p = ROOT / f
    s = p.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in s else "\n"                 # mantém o fim de linha do arquivo (as chaves são hash dos bytes)
    old, new = old.replace("\n", eol), new.replace("\n", eol)
    assert s.count(old) == n, (f, old[:70], s.count(old))
    p.write_bytes(s.replace(old, new).encode("utf-8"))


# achado 3: bytes do evaluate.py e do pitch_model.py lidos na importação, para a chave da série
sub("temporal.py", '_SRC = {f: (ROOT / "src_v2" / f).read_bytes() for f in _KEY_SOURCES + ("temporal.py", "evaluate.py", "io/gsr.py")}',
    '_SRC = {f: (ROOT / "src_v2" / f).read_bytes() for f in _KEY_SOURCES + ("temporal.py", "evaluate.py", "io/gsr.py", "pitch_model.py")}')
sub("temporal.py", '''def _series_key():
    """Hash do config e do código de que a série do detector depende (bytes lidos na
    importação; mesmo valor da fórmula anterior)."""
    h = hashlib.sha1(json.dumps({k: CFG[k] for k in ("segment", "lines", "assign", "detector", "fit")}, sort_keys=True).encode())
    for f in _KEY_SOURCES:
        h.update(_SRC[f])
    return h.hexdigest()''', '''def _series_key():
    """Hash do config e do código de que a série do detector depende (bytes lidos na
    importação). v2 (achado 3 da revisão de 2026-10-14): entram também a seção `pitch`, o
    `eval.quality_grid_px` (margem de ambiguidade por evaluate.image_grid_displacement) e os
    bytes do evaluate.py e do pitch_model.py."""
    cfg = {k: CFG[k] for k in ("segment", "lines", "assign", "detector", "fit", "pitch")}
    cfg["eval.quality_grid_px"] = CFG["eval"]["quality_grid_px"]
    h = hashlib.sha1(json.dumps(cfg, sort_keys=True).encode())
    for f in _KEY_SOURCES + ("evaluate.py", "pitch_model.py"):
        h.update(_SRC[f])
    return h.hexdigest()


def load_series(clip, key=None):
    """Série do detector de um clipe, só se gravada com a chave do código e do config atuais
    (`key`, padrão `_series_key()`); senão, erro. v2, achado 2 da revisão de 2026-10-14: a
    série era lida sem conferir a chave, e um trecho com falha deixava a série velha valer."""
    p = _series_path(clip)
    if not p.exists():
        raise FileNotFoundError(f"sem a série do detector de {clip.name}: rode --detect-series")
    ser, key = dict(np.load(p)), key or _series_key()
    if str(ser["key"]) != key:
        raise RuntimeError(f"série de {clip.name} gravada com a chave {str(ser['key'])[:12]}, a atual é {key[:12]}: rode --detect-series")
    return ser''')
# achado 2: toda leitura da série passa pela conferência da chave
sub("temporal.py", "    return {c: dict(np.load(_series_path(c))) for c in clips}",
    "    return {c: load_series(c, key) for c in clips if _series_path(c).exists() and str(np.load(_series_path(c))[\"key\"]) == key}")
sub("temporal.py", "    ser = dict(np.load(_series_path(clip)))", "    ser = load_series(clip)", n=4)
sub("sensitivity.py", "    ser = dict(np.load(T._series_path(clip)))", "    ser = T.load_series(clip)")
sub("sensitivity.py", '    ser = dict(np.load(TM._series_path(path("gsr") / "train" / clip)))', '    ser = TM.load_series(path("gsr") / "train" / clip)')
sub("consequence.py", "    ser = dict(np.load(T._series_path(clip)))", "    ser = T.load_series(clip)")
# achado 3: chave do 6c com as seções eval, gsr, gsr_label_fixes e pitch
sub("temporal.py", '''    h = hashlib.sha1(json.dumps(T, sort_keys=True).encode() + _series_key().encode())
    for f in ("temporal.py", "evaluate.py", "io/gsr.py"):''', '''    h = hashlib.sha1(json.dumps(T, sort_keys=True).encode() + _series_key().encode())
    # v2, achado 3: as métricas (eval), o gabarito (gsr, gsr_label_fixes) e o molde (pitch)
    h.update(json.dumps({k: CFG[k] for k in ("eval", "gsr", "gsr_label_fixes", "pitch")}, sort_keys=True).encode())
    for f in ("temporal.py", "evaluate.py", "io/gsr.py"):''')
# achado 3: chave do ECC com o que forma a máscara "keep" (compact_dilate_frac, segment, lines e os bytes)
sub("consequence.py", '''    return hashlib.sha1(json.dumps(S, sort_keys=True).encode() + _SRC_ECC + T._SRC["temporal.py"]).hexdigest()''',
    '''    mask = {"temporal.compact_dilate_frac": T.T["compact_dilate_frac"], "segment": CFG["segment"], "lines": CFG["lines"]}  # v2, achado 3
    return hashlib.sha1(json.dumps(S, sort_keys=True).encode() + _SRC_ECC + T._SRC["temporal.py"]
                        + json.dumps(mask, sort_keys=True).encode() + T._SRC["segment.py"] + T._SRC["lines.py"]).hexdigest()''')
print("ok")
