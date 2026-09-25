"""Loader do SoccerNet-GSR (Somers et al., 2024). Formato em docs/02-dados.md.

O arquivo não traz câmera. A H_gt de cada frame é o ajuste ponto-linha às linhas
anotadas (como o AuxFlow, seção 4.1), iniciado pela DLT sobre as pessoas — que só
recupera a calibração do dataset e fica como conferência (docs/decisoes.md).
"""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from src.config import CFG, ROOT, path
from src.evaluate import image_grid_displacement
from src.homography import Fit, class_distances, fit_point_line
from src.io import Sample
from src.pitch_model import POLYLINES

GSR = CFG["gsr"]
PERSONS = set(GSR["person_categories"])
LABEL_FIXES = CFG.get("gsr_label_fixes") or {}
_BASE = ("bottom_left", "bottom_middle", "bottom_right")
# o cache do ajuste depende destes fontes e das seções do config em _cache_key
_CACHE_SOURCES = ("src/homography.py", "src/io/gsr.py", "src/geometry.py", "src/pitch_model.py")


def _persons(anns):
    """Anotações de pessoa com `bbox_pitch` válido (nulo em algumas; docs/02-dados.md)."""
    return [a for a in anns if a["category_id"] in PERSONS and a.get("bbox_pitch")]


def estimate_h_persons(anns):
    """Anotações de objeto de um frame -> H (campo -> imagem) por DLT, ou None.

    Correspondências: `bbox_pitch` (campo, m) <-> base da `bbox_image` (imagem, px)
    em (x, y+h), (x+w/2, y+h), (x+w, y+h). None com menos de `min_persons` pessoas.
    Recupera a calibração do dataset, da qual o `bbox_pitch` foi derivado.
    """
    persons = _persons(anns)
    if len(persons) < GSR["min_persons"]:
        return None
    XY, uv = [], []
    for a in persons:
        b, p = a["bbox_image"], a["bbox_pitch"]
        v = b["y"] + b["h"]
        uv += [(b["x"], v), (b["x"] + b["w"] / 2, v), (b["x"] + b["w"], v)]
        XY += [(p[f"x_{k}"], p[f"y_{k}"]) for k in _BASE]
    H, _ = cv2.findHomography(np.float64(XY), np.float64(uv), 0)
    return H


def fixed_label(clip: str, frame_idx: int, name: str) -> str | None:
    """Rótulo de classe das linhas anotadas, corrigido por `gsr_label_fixes` (config).
    None = classe descartada nesse frame."""
    if name not in (fixes := LABEL_FIXES.get(clip, {})):
        return name
    fix = fixes[name]
    to, first, last = (fix, 1, float("inf")) if isinstance(fix, str) else fix
    return to if first <= frame_idx <= last else name


def inner_points(lines_uv, size):
    """Pontos anotados (imagem, px) a mais de `border_margin_px` da borda: os rentes
    à borda são o recorte da linha pelo quadro, não a linha (docs/decisoes.md)."""
    m, (w, h) = GSR["border_margin_px"], size
    out = {}
    for k, p in lines_uv.items():
        p = p[(p[:, 0] > m) & (p[:, 0] < w - m) & (p[:, 1] > m) & (p[:, 1] < h - m)]
        if len(p):
            out[k] = p
    return out


def fit_clip(samples: list[Sample]) -> list[Fit]:
    """Ajuste pelas linhas de cada frame do clipe (ordenado por frame).

    Início: a H pelas pessoas; se não houver ou o ajuste for recusado, a última H
    aceita (passada para frente). Frames que sobrarem tentam a partir da próxima H
    aceita (passada para trás).
    """
    def attempt(s, inits):
        fit = None
        for H0 in inits:
            if H0 is not None:
                fit = fit_point_line(H0, inner_points(s.lines_uv, s.size), s.size)
                if fit.ok:
                    break
        return fit

    fits = [None] * len(samples)
    last = None
    for i, s in enumerate(samples):
        fits[i] = attempt(s, [s.H_persons, last])
        if fits[i] is not None and fits[i].ok:
            last = fits[i].H
    nxt = None
    for i in reversed(range(len(samples))):
        if fits[i] is not None and fits[i].ok:
            nxt = fits[i].H
        elif nxt is not None:
            fit = attempt(samples[i], [nxt])
            if fits[i] is None or fit.ok:
                fits[i] = fit
            if fit.ok:
                nxt = fit.H
    n_pts = [sum(len(p) for p in inner_points(s.lines_uv, s.size).values()) for s in samples]
    return [f if f is not None else Fit(None, np.nan, 0, np.inf, n, False) for f, n in zip(fits, n_pts)]


def _cache_key(clip: str) -> str:
    """Hash dos fontes e da configuração de que o ajuste depende."""
    h = hashlib.sha1()
    for src in _CACHE_SOURCES:
        h.update((ROOT / src).read_bytes())
    cfg = {k: CFG[k] for k in ("pitch", "gsr", "fit")} | {"fixes": LABEL_FIXES.get(clip)}
    h.update(json.dumps(cfg, sort_keys=True, default=str).encode())
    return h.hexdigest()


def _cached_fits(clip_dir: Path, samples: list[Sample]) -> list[Fit]:
    """fit_clip com cache em outputs/cache/gsr/<split>/<clipe>.npz."""
    f = path("outputs") / "cache" / "gsr" / clip_dir.parent.name / f"{clip_dir.name}.npz"
    key = _cache_key(clip_dir.name)
    if f.exists():
        c = np.load(f)
        if str(c["key"]) == key:
            return [Fit(None if np.isnan(H).any() else H, float(r), int(k), float(cd), int(n), bool(ok))
                    for H, r, k, cd, n, ok in zip(c["H"], c["resid"], c["rank"], c["cond"], c["n"], c["ok"])]
    fits = fit_clip(samples)
    f.parent.mkdir(parents=True, exist_ok=True)
    np.savez(f, key=key, H=np.array([x.H if x.H is not None else np.full((3, 3), np.nan) for x in fits]),
             resid=[x.resid_px for x in fits], rank=[x.rank for x in fits], cond=[x.cond for x in fits],
             n=[x.n_points for x in fits], ok=[x.ok for x in fits])
    return fits


def load_clip(clip_dir: Path, fit: str = "cache") -> list[Sample]:
    """Um Sample por frame do clipe, com H_gt pelas linhas (ou None), H pelas
    pessoas, linhas anotadas, discordância entre as duas e marca de duvidoso.
    fit: "cache" (padrão), "fresh" (ignora o cache) ou "none" (sem ajuste, H_gt None)."""
    d = json.loads((clip_dir / "Labels-GameState.json").read_text(encoding="utf-8"))
    objects, pitch = defaultdict(list), {}
    for a in d["annotations"]:
        if a["supercategory"] == "pitch":
            pitch[a["image_id"]] = a["lines"]
        else:
            objects[a["image_id"]].append(a)

    samples = []
    for im in sorted(d["images"], key=lambda im: im["file_name"]):
        w, h = im["width"], im["height"]
        anns = objects[im["image_id"]]
        frame_idx = int(Path(im["file_name"]).stem)
        # rótulos trocados corrigidos (config); só as classes do gramado: `Goal …` fora
        raw = defaultdict(list)
        for k, pts in pitch.get(im["image_id"], {}).items():
            raw[fixed_label(clip_dir.name, frame_idx, k)] += pts
        persons = _persons(anns)
        samples.append(Sample(
            image_id=im["image_id"],
            image_path=clip_dir / d["info"]["im_dir"] / im["file_name"],
            H_gt=None,
            sequence_id=clip_dir.name,
            frame_idx=frame_idx,
            size=(w, h),
            H_persons=estimate_h_persons(anns),
            persons_XY=np.array([[a["bbox_pitch"]["x_bottom_middle"], a["bbox_pitch"]["y_bottom_middle"]]
                                 for a in persons]).reshape(-1, 2),
            boxes_uv=np.array([[a["bbox_image"][k] for k in "xywh"] for a in persons]).reshape(-1, 4),
            lines_uv={k: np.array([[p["x"] * w, p["y"] * h] for p in pts])
                      for k, pts in raw.items() if k in POLYLINES and pts},
        ))

    if fit == "none":
        return samples
    fits = _cached_fits(clip_dir, samples) if fit == "cache" else fit_clip(samples)
    for s, f in zip(samples, fits):
        s.fit = f
        if f.ok:
            s.H_gt = f.H
            s.line_err = f.resid_px
            s.class_err = {k: float(np.median(v))
                           for k, v in class_distances(f.H, inner_points(s.lines_uv, s.size)).items()}
            s.dubious = bool(f.resid_px > GSR["dubious_median_px"])
            if s.H_persons is not None:
                s.gt_disagree_px = image_grid_displacement(f.H, s.H_persons, s.size)
    return samples
