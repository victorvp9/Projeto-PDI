"""D1 (docs/06-literatura-testes.md, seção 4): quanto do limite de LocSim@5 do gabarito pelas
linhas (0,946 no test, 0,933 no train) é distorção de lente?

Só o gabarito, sem detector. Nos frames de dev (GSR train + valid) com H_gt e com pessoas, a
1 frame a cada `passo`, compara o LocSim@5 do `bbox_pitch` contra:
  - H_gt         : o ajuste ponto-linha do projeto (cache do loader), sem lente;
  - H+k1 frame   : o mesmo ajuste com 1 coeficiente radial (modelo de divisão, centro no meio da
                   imagem, raio em alturas), H e k1 livres por frame, partindo da H_gt e k1 = 0;
  - H+k1 clipe   : k1 fixo na mediana do clipe, H reajustada.
Os pontos das linhas e a base das caixas passam pela mesma correção antes de H⁻¹.
Mesma perda, escala e aceite do ajuste do gabarito (config_v2.yaml, seção fit).
Uso (da raiz): PYTHONPATH=. uv run python scripts/literatura/d1_lente.py <saída> [passo] [clipes...]"""
import csv
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from src_v2.config import path
from src_v2.evaluate import locsim, locsim_distances
from src_v2.homography import F, N_FIELD, _img_norm, smooth_distances
from src_v2.io import gsr


def undistort(p, k, size):
    """Modelo de divisão: p_u = c + (p - c) / (1 + k r²), r = |p - c| / h (imagem, px)."""
    c = np.array(size) / 2.0
    q = (p - c) / size[1]
    return c + (p - c) / (1 + k * (q * q).sum(1, keepdims=True))


def fit_k(H0, lines, size, k0=0.0, k_fixed=None):
    """H (campo -> imagem não distorcida) e k1 por mínimos quadrados robustos. Devolve (H, k, ok)."""
    n = sum(len(p) for p in lines.values())
    if n < F["min_points"] + 1:
        return None, np.nan, False
    Ni = _img_norm(size)
    Ni_inv = np.linalg.inv(Ni)
    H_of = lambda g: Ni_inv @ np.append(g[:8], 1.0).reshape(3, 3) @ N_FIELD

    def resid(x):
        k = k_fixed if k_fixed is not None else x[8]
        und = {c: undistort(p, k, size) for c, p in lines.items()}
        return np.minimum(smooth_distances(H_of(x), und, True), F["resid_cap_px"])
    G0 = Ni @ H0 @ np.linalg.inv(N_FIELD)
    x0 = (G0 / G0[2, 2]).ravel()[:8]
    if k_fixed is None:
        x0 = np.r_[x0, k0]
    r = least_squares(resid, x0, loss=F["loss"], f_scale=F["f_scale_px"], x_scale="jac")
    s = np.linalg.svd(r.jac, compute_uv=False)
    rank = int((s > s[0] * np.sqrt(np.finfo(float).eps)).sum())
    k = k_fixed if k_fixed is not None else float(r.x[8])
    ok = rank == len(x0) and np.median(np.abs(r.fun)) <= F["max_resid_px"]
    return H_of(r.x), k, bool(ok)


def loc5(H, s, k):
    base = np.c_[s.boxes_uv[:, 0] + s.boxes_uv[:, 2] / 2, s.boxes_uv[:, 1] + s.boxes_uv[:, 3]]
    b = undistort(base, k, s.size) if k else base
    d = locsim_distances(H, np.c_[b, np.zeros((len(b), 2))], s.persons_XY)
    return locsim(d, 5)


def clip_rows(args):
    clip, step = args
    game = gsr.game_id(clip)
    rows, frames = [], []
    for s in gsr.load_clip(clip)[::step]:
        if s.H_gt is None or not len(s.persons_XY):
            continue
        lines = gsr.inner_points(s.lines_uv, s.size)
        Hk, k, ok = fit_k(s.H_gt, lines, s.size)
        frames.append((s, lines, Hk, k, ok))
    ks = [k for *_, k, ok in frames if ok]
    k_clip = float(np.median(ks)) if ks else 0.0
    for s, lines, Hk, k, ok in frames:
        Hc, _, okc = fit_k(s.H_gt, lines, s.size, k_fixed=k_clip)
        base = loc5(s.H_gt, s, 0.0)
        rows.append(dict(particao=clip.parent.name, clipe=clip.name, jogo=game, frame=s.frame_idx,
                         n_pessoas=len(base), k1=k, k1_ok=ok, k1_clipe=k_clip,
                         soma_hgt=float(base.sum()),
                         soma_k1_frame=float(loc5(Hk, s, k).sum()) if ok else np.nan,
                         soma_k1_clipe=float(loc5(Hc, s, k_clip).sum()) if okc else np.nan))
    return rows


def main():
    out = Path(sys.argv[1])
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    names = set(sys.argv[3:])
    clips = [c for sp in ("train", "valid") for c in sorted((path("gsr") / sp).glob("SNGS-*")) if not names or c.name in names]
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor() as ex:
        for r in ex.map(clip_rows, [(c, step) for c in clips]):
            rows += r
            print(f"{r[0]['clipe'] if r else '?'}: {len(r)} frames", flush=True)
    with open(out / "d1_frames.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # LocSim@5 por pessoa-frame, nos frames em que as três variantes têm ajuste aceito (conjunto comum)
    lines = ["| jogo | frames | LocSim@5 H_gt | H+k1 por frame | H+k1 do clipe | k1 mediano (p10, p90) |", "|---|---|---|---|---|---|"]
    games = sorted({r["jogo"] for r in rows}, key=lambda g: [r["jogo"] for r in rows].index(g)) + ["todos"]
    for g in games:
        rs = [r for r in rows if (g == "todos" or r["jogo"] == g) and np.isfinite(r["soma_k1_frame"]) and np.isfinite(r["soma_k1_clipe"])]
        n = sum(r["n_pessoas"] for r in rs)
        if not n:
            continue
        ks = np.array([r["k1"] for r in rs])
        lines.append(f"| {g} | {len(rs)} | {sum(r['soma_hgt'] for r in rs) / n:.4f} | {sum(r['soma_k1_frame'] for r in rs) / n:.4f} | "
                     f"{sum(r['soma_k1_clipe'] for r in rs) / n:.4f} | {np.median(ks):.4f} ({np.percentile(ks, 10):.4f}, {np.percentile(ks, 90):.4f}) |")
    txt = "\n".join(lines)
    print(txt)
    (out / "d1_resumo.md").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
