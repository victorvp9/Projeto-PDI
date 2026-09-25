"""Loader do SoccerNet-GSR (Somers et al., 2024). Formato em docs/02-dados.md.

O arquivo não traz câmera: a H_gt de cada frame é estimada por DLT sobre as
pessoas, sem a bola (docs/decisoes.md).
"""
import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from src.config import CFG
from src.geometry import point_segment_distance, project_segments
from src.io import Sample
from src.pitch_model import POLYLINES

GSR = CFG["gsr"]
PERSONS = set(GSR["person_categories"])
LABEL_FIXES = CFG.get("gsr_label_fixes") or {}
_BASE = ("bottom_left", "bottom_middle", "bottom_right")


def _persons(anns):
    """Anotações de pessoa com `bbox_pitch` válido (nulo em algumas; docs/02-dados.md)."""
    return [a for a in anns if a["category_id"] in PERSONS and a.get("bbox_pitch")]


def estimate_h_gt(anns):
    """Anotações de objeto de um frame -> H_gt (campo -> imagem) por DLT, ou None.

    Correspondências: `bbox_pitch` (campo, m) <-> base da `bbox_image` (imagem, px)
    em (x, y+h), (x+w/2, y+h), (x+w, y+h). None com menos de `min_persons` pessoas.
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


def fixed_label(clip: str, frame_idx: int, name: str) -> str:
    """Rótulo de classe das linhas anotadas, corrigido por `gsr_label_fixes` (config)."""
    fix = LABEL_FIXES.get(clip, {}).get(name)
    if fix is None:
        return name
    to, first, last = (fix, 1, float("inf")) if isinstance(fix, str) else fix
    return to if first <= frame_idx <= last else name


def class_distances(H, lines_uv, width, height):
    """Por classe, distância (px) de cada ponto anotado à polilinha do modelo
    projetada por H (campo -> imagem). Ignora pontos a até `border_margin_px` da
    borda; classes sem ponto restante ficam de fora (docs/decisoes.md).
    """
    m = GSR["border_margin_px"]
    out = {}
    for name, pts in lines_uv.items():
        u, v = pts[:, 0], pts[:, 1]
        pts = pts[(u > m) & (u < width - m) & (v > m) & (v < height - m)]
        if len(pts):
            out[name] = point_segment_distance(pts, project_segments(H, POLYLINES[name]))
    return out


def load_clip(clip_dir: Path) -> list[Sample]:
    """Um Sample por frame do clipe, com H_gt, linhas anotadas e marca de duvidoso."""
    d = json.loads((clip_dir / "Labels-GameState.json").read_text(encoding="utf-8"))
    objects, pitch = defaultdict(list), {}
    for a in d["annotations"]:
        if a["supercategory"] == "pitch":
            pitch[a["image_id"]] = a["lines"]
        else:
            objects[a["image_id"]].append(a)

    samples = []
    for im in d["images"]:
        w, h = im["width"], im["height"]
        anns = objects[im["image_id"]]
        H = estimate_h_gt(anns)
        frame_idx = int(Path(im["file_name"]).stem)
        # rótulos trocados corrigidos (config); só as classes do gramado: `Goal …` fora
        raw = defaultdict(list)
        for k, pts in pitch.get(im["image_id"], {}).items():
            raw[fixed_label(clip_dir.name, frame_idx, k)] += pts
        lines = {k: np.array([[p["x"] * w, p["y"] * h] for p in pts])
                 for k, pts in raw.items() if k in POLYLINES and pts}
        dist = class_distances(H, lines, w, h) if H is not None else {}
        err = float(np.median(np.concatenate(list(dist.values())))) if dist else np.nan
        persons = _persons(anns)
        samples.append(Sample(
            image_id=im["image_id"],
            image_path=clip_dir / d["info"]["im_dir"] / im["file_name"],
            H_gt=H,
            sequence_id=clip_dir.name,
            frame_idx=frame_idx,
            persons_XY=np.array([[a["bbox_pitch"]["x_bottom_middle"], a["bbox_pitch"]["y_bottom_middle"]]
                                 for a in persons]).reshape(-1, 2),
            boxes_uv=np.array([[a["bbox_image"][k] for k in "xywh"] for a in persons]).reshape(-1, 4),
            lines_uv=lines,
            line_err=err,
            class_err={k: float(np.median(v)) for k, v in dist.items()},
            dubious=bool(err > GSR["dubious_median_px"]),
        ))
    return samples
