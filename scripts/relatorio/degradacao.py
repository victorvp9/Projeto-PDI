"""B5, robustez a degradações sintéticas (análise posterior à rodada, pedida por Victor em
2026-10-13; protocolo gravado no docs/decisoes.md antes de rodar). Só no WC14 train_val (209
imagens), nunca no test. Nenhum parâmetro muda: o config é o congelado (SHA-1 conferido) e as
funções do src/ são chamadas sem mudança; a degradação é aplicada à imagem original antes delas.

Degradações, uma de cada vez, 3 níveis (semente fixa por imagem, degradação e nível):
- ruído gaussiano, σ = 5, 10, 20 (8 bits);
- borrão de movimento horizontal, núcleo linear de 5, 11, 21 px;
- sombra: faixa pelo centroide do gramado anotado, orientação sorteada, largura = metade da
  extensão do gramado na direção normal à faixa, bordas em rampa linear de 0,05·h; L* × 0,7,
  0,5, 0,35;
- oclusão: elipses cheias de tamanho de jogador (1,8 × 0,6 m, na escala local da H_gt) e cor
  de uma paleta de uniformes, com centro no gramado anotado, até cobrir 5%, 10%, 20% dele.

Medidas por etapa, com as funções de avaliação existentes: IoU do gramado (média por imagem);
cobertura a 2 px e precisão a 3 px das marcações (média por imagem); recall de linhas (linhas
do modelo visíveis com um segmento a tol_frac·h, somado nas imagens); cobertura do detector,
IoU do campo inteiro mediano nas cobertas e fração de aceitas com IoU do campo inteiro < 0,8.

Grava outputs/runs/rodada_test/pos_rodada/B5.csv (com o commit do método e o deste script),
a figura outputs/figures/relatorio/fig8_degradacao.png e exemplos em outputs/debug/degradacao/.
Uso (da raiz, PYTHONPATH=.): degradacao.py <trabalhadores>"""
import csv
import hashlib
import json
import subprocess
import sys

import cv2
import numpy as np

from src.config import CFG, ROOT, path

SEED = 20261013
LEVELS = {"ruído": (5, 10, 20), "borrão": (5, 11, 21), "sombra": (0.7, 0.5, 0.35), "oclusão": (0.05, 0.10, 0.20)}
KITS = [(255, 255, 255), (30, 30, 200), (180, 60, 20), (0, 220, 255), (20, 20, 20), (90, 30, 10), (230, 180, 120), (0, 120, 255)]  # BGR
WRONG_IOU = 0.8
MEASURES = ["gramado_iou", "marcas_cob2", "marcas_prec3", "recall_linhas", "det_cobertura", "det_iou_mediano", "det_aceitas_certas"]
FROZEN = json.loads((path("outputs") / "runs" / "congelamento.json").read_text(encoding="utf-8"))
OUT = path("outputs") / "runs" / "rodada_test" / "pos_rodada"


def degrade(img, kind, level, s, rng):
    """Imagem degradada (BGR, uint8); `s` é o Sample do WC14 (gramado anotado e H_gt)."""
    h, w = img.shape[:2]
    if kind == "ruído":
        return np.clip(img + rng.normal(0, level, img.shape), 0, 255).astype(np.uint8)
    if kind == "borrão":
        return cv2.filter2D(img, -1, np.full((1, level), 1.0 / level), borderType=cv2.BORDER_REFLECT)
    if kind == "sombra":
        v, u = np.nonzero(s.grass)
        theta = rng.uniform(0, np.pi)
        n = np.array([np.cos(theta), np.sin(theta)])                     # normal da faixa (imagem)
        d_grass = (np.c_[u, v] - [u.mean(), v.mean()]) @ n
        half = (d_grass.max() - d_grass.min()) / 4                       # largura = metade da extensão
        U, V = np.meshgrid(np.arange(w), np.arange(h))
        d = (U - u.mean()) * n[0] + (V - v.mean()) * n[1]
        ramp = 0.05 * h
        wgt = np.clip((half - np.abs(d)) / ramp + 0.5, 0, 1)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[..., 0] *= 1 - (1 - level) * wgt
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    if kind == "oclusão":
        from src.geometry import project
        out, cover = img.copy(), np.zeros((h, w), np.uint8)
        v, u = np.nonzero(s.grass)
        Hinv, total = np.linalg.inv(s.H_gt), s.grass.sum()
        while (cover.astype(bool) & s.grass).sum() < level * total:
            k = rng.integers(len(u))
            foot = np.array([u[k], v[k], 1.0]) @ Hinv.T
            XY = foot[:2] / foot[2]                                     # campo, m
            uv, ok = project(s.H_gt, np.array([XY, XY + [1.0, 0.0]]))
            ppm = np.linalg.norm(uv[1] - uv[0]) if ok.all() else np.nan  # px por metro ao longo de X, ali
            if not np.isfinite(ppm) or ppm <= 0:
                continue
            ax = (max(1, int(round(0.3 * ppm))), max(1, int(round(0.9 * ppm))))  # semieixos: 0,6 × 1,8 m
            center = (int(u[k]), int(v[k] - ax[1]))                     # pés no ponto sorteado
            color = KITS[rng.integers(len(KITS))]
            cv2.ellipse(out, center, ax, 0, 0, 360, color, -1)
            cv2.ellipse(cover, center, ax, 0, 0, 360, 1, -1)
        return out
    raise ValueError(kind)


def image_rows(image_id):
    """Medidas por etapa numa imagem, limpa e nas 12 degradações."""
    from src.assign import detect_frame
    from src.conics import detect
    from src.evaluate import _iou, coverage_precision, iou_whole, lines_target, segment_counts, segment_gt
    from src.io import wc14
    from src.render import lines_mask
    from src.segment import grass_mask, line_mask, params
    cv2.setNumThreads(1)
    s = wc14.load_sample("train_val", image_id)
    img0, size = s.image, s.size
    (name, v), = CFG["detector"]["variants"].items()
    P = params("wc14")
    Pseg, Plin = {**P, **v.get("segment", {})}, {**CFG["lines"], **v.get("lines", {})}
    target, width = lines_target(s.H_gt, size, region=s.grass), lines_mask(s.H_gt, size)
    sgt, tol = segment_gt(s.H_gt, size, region=s.grass), CFG["lines"]["tol_frac"] * size[1]
    conds = [("limpa", 0, None)] + [(k, i + 1, lv) for k, lvs in LEVELS.items() for i, lv in enumerate(lvs)]
    rows = []
    for kind, i, lv in conds:
        rng = np.random.default_rng([SEED, int(image_id), list(LEVELS).index(kind) if kind in LEVELS else 9, i])
        img = img0 if kind == "limpa" else degrade(img0, kind, lv, s, rng)
        grass = grass_mask(img, P)
        marks = line_mask(img, grass, Pseg)
        cp = coverage_precision(marks, target, [2, 3], width_target=width)
        segs, _, cid = detect(marks, Plin)
        c, _ = segment_counts(segs[cid < 0], sgt, tol)
        H, _ = detect_frame(img, "wc14")[name]
        rows.append(dict(imagem=image_id, degradacao=kind, nivel=i, valor=lv, gramado_iou=_iou(grass, s.grass),
                         marcas_cob2=cp["cobertura@2"], marcas_prec3=cp["precisao@3"], lines_vis=c["lines_vis"], lines_det=c["lines_det"],
                         tem_H=H is not None, iou_whole=iou_whole(H, s.H_gt) if H is not None else np.nan))
    return rows


def aggregate(rows):
    """Uma linha por (degradação, nível)."""
    out = []
    for key in dict.fromkeys((r["degradacao"], r["nivel"]) for r in rows):
        rs = [r for r in rows if (r["degradacao"], r["nivel"]) == key]
        iou = np.array([r["iou_whole"] for r in rs if r["tem_H"]])
        out.append(dict(degradacao=key[0], nivel=key[1], valor=rs[0]["valor"], imagens=len(rs),
                        gramado_iou=np.mean([r["gramado_iou"] for r in rs]),
                        marcas_cob2=np.nanmean([r["marcas_cob2"] for r in rs]), marcas_prec3=np.nanmean([r["marcas_prec3"] for r in rs]),
                        recall_linhas=sum(r["lines_det"] for r in rs) / sum(r["lines_vis"] for r in rs),
                        det_cobertura=np.mean([r["tem_H"] for r in rs]), det_iou_mediano=float(np.median(iou)) if len(iou) else np.nan,
                        det_aceitas_erradas=float(np.mean(iou < WRONG_IOU)) if len(iou) else np.nan,
                        det_aceitas_certas=float(np.mean(iou >= WRONG_IOU)) if len(iou) else np.nan))
    clean = out[0]
    for r in out:
        r.update({f"rel_{m}": r[m] / clean[m] for m in MEASURES})
    return out


def first_break(agg):
    """Por degradação: o menor nível em que alguma medida cai mais de 10% em relação à imagem
    limpa e, nele, a primeira etapa na ordem do pipeline (MEASURES)."""
    out = {}
    for kind in LEVELS:
        out[kind] = ("nenhuma", None)
        for r in sorted((r for r in agg if r["degradacao"] == kind), key=lambda r: r["nivel"]):
            hit = [m for m in MEASURES if r[f"rel_{m}"] < 0.9]
            if hit:
                out[kind] = (hit[0], r["nivel"])
                break
    return out


def figure(agg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    lab = {"gramado_iou": "gramado: IoU", "marcas_cob2": "marcações: cobertura a 2 px", "marcas_prec3": "marcações: precisão a 3 px",
           "recall_linhas": "retas: recall de linhas", "det_cobertura": "detector: cobertura", "det_iou_mediano": "detector: IoU do campo inteiro mediano",
           "det_aceitas_certas": "detector: aceitas certas (IoU ≥ 0,8)"}
    unit = {"ruído": "σ", "borrão": "núcleo (px)", "sombra": "fator de L*", "oclusão": "fração do gramado"}
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
    clean = agg[0]
    for ax, kind in zip(axs, LEVELS):
        rs = [clean] + sorted((r for r in agg if r["degradacao"] == kind), key=lambda r: r["nivel"])
        for m in MEASURES:
            ax.plot(range(4), [r[f"rel_{m}"] for r in rs], marker="o", ms=3, label=lab[m])
        ax.axhline(0.9, color="0.5", ls="--", lw=0.8)
        ax.set_xticks(range(4), ["limpa"] + [f"{x:g}".replace(".", ",") for x in LEVELS[kind]])
        ax.set_title(kind)
        ax.set_xlabel(unit[kind])
        ax.grid(alpha=0.3)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
    axs[0].set_ylabel("medida / medida na imagem limpa")
    axs[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(path("outputs") / "figures" / "relatorio" / "fig8_degradacao.png", dpi=200, bbox_inches="tight")


def debug_examples(image_id):
    """Depuração: a imagem limpa e as 12 degradações de uma imagem, numa folha."""
    from src.io import wc14
    s = wc14.load_sample("train_val", image_id)
    tiles = [cv2.resize(s.image, (480, 270))]
    for kind, lvs in LEVELS.items():
        for i, lv in enumerate(lvs):
            rng = np.random.default_rng([SEED, int(image_id), list(LEVELS).index(kind), i + 1])
            t = cv2.resize(degrade(s.image, kind, lv, s, rng), (480, 270))
            cv2.putText(t, f"{kind} {lv}".encode("ascii", "replace").decode(), (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            tiles.append(t)
    tiles += [np.zeros_like(tiles[0])] * 3
    d = path("debug") / "degradacao"
    d.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(d / f"wc14_{image_id}.jpg"), np.vstack([np.hstack(tiles[k:k + 4]) for k in range(0, 16, 4)]))


if __name__ == "__main__":
    from src.executor import SafeProcessPool, exit_if_failed
    from src.io import wc14
    here = "scripts/relatorio/degradacao.py"
    assert not subprocess.run(["git", "status", "--porcelain", "--", here], capture_output=True, text=True).stdout.strip(), "script sem commit"
    commit = subprocess.run(["git", "log", "-1", "--format=%H", "--", here], capture_output=True, text=True).stdout.strip()
    assert hashlib.sha1((ROOT / "config.yaml").read_bytes()).hexdigest() == FROZEN["config_sha1"], "config diferente do congelado"
    ids = wc14.split_ids("train_val")
    assert len(ids) == 209
    for i in ids[:3]:
        debug_examples(i)
    with SafeProcessPool(int(sys.argv[1]), initializer=cv2.setNumThreads, initargs=(1,)) as ex:
        res = list(ex.map(image_rows, ids))
    exit_if_failed()
    assert all(r is not None for r in res)
    agg = aggregate([x for r in res for x in r])
    fb = first_break(agg)
    for kind, (m, lv) in fb.items():
        agg.append(dict(degradacao=kind, nivel="quebra", quebra_primeiro=m, nivel_quebra=lv))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [r | dict(analise="posterior à rodada, WC14 train_val", commit_metodo=FROZEN["commit"], commit_script=commit) for r in agg]
    with (OUT / "B5.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)
    figure([r for r in agg if r["nivel"] != "quebra"])
    print("degradação nível valor | " + " | ".join(MEASURES) + " | aceitas erradas")
    for r in agg:
        if r["nivel"] != "quebra":
            print(f"{r['degradacao']:8} {r['nivel']} {r['valor']!s:5} | " + " | ".join(f"{r[m]:.4f}" for m in MEASURES) + f" | {r['det_aceitas_erradas']:.4f}")
    print("quebra primeiro:", fb)
