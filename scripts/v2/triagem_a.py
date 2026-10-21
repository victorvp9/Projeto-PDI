"""v2, A, checagem barata (docs/05-melhorias-plano.md, seção 5): o detector a 1 frame em 25 nos 115
clipes do dev, com o A (assign.central_view) contra a base.

O A só roda nos frames em que a 2 + 2 não deu H aceita (assign.detect_frame): nos frames em que a série
da base tem H, a saída do A é a mesma, e só os outros são rodados. A série da base é lida direto do
cache (a chave dela é a do código sem o A).
Por jogo: cobertura (frames com H_gt), fração de H aceitas erradas (NPE > 0,05 contra a H_gt) e NPE
mediano das aceitas, na base e com o A; e as H novas do A (quantas, quantas erradas, NPE mediano).
Regra do plano: o A para aqui se, em algum jogo, a fração de aceitas erradas piorar mais que 0,02 em
termos absolutos, ou se não aparecer H nova (a medida-alvo não muda).
Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/triagem_a.py [trabalhadores]"""
import csv
import sys
from collections import defaultdict

import cv2
import numpy as np

from src_v2.config import CFG, path

STEP, WRONG, MAX_WORSE = 25, 0.05, 0.02
GAMES = ("4", "6", "9", "2", "3", "5")


def clips_dev():
    return [c for s in ("train", "valid") for c in sorted((path("gsr") / s).glob("SNGS-*"))]


def clip_rows(clip):
    from src_v2.assign import detect_frame
    from src_v2.evaluate import npe_re
    from src_v2.io import gsr
    from src_v2.temporal import _series_path
    assert CFG["assign"]["central_view"], "a triagem mede o A: assign.central_view tem que estar ligado"
    cv2.setNumThreads(1)
    ser = np.load(_series_path(clip))
    samples, game, rows = gsr.load_clip(clip), gsr.game_id(clip), []
    for t in range(0, len(samples), STEP):
        s, Hb = samples[t], ser["H"][t]
        base_ok = bool(np.isfinite(Hb).all())
        Ha, info = (Hb, {}) if base_ok else next(iter(detect_frame(s.image, "gsr").values()))
        a_ok = Ha is not None and bool(np.isfinite(Ha).all())
        npe = lambda H, ok: npe_re(H, s.H_gt, s.size)[0] if ok and s.H_gt is not None else np.nan
        rows.append(dict(clipe=clip.name, jogo=game, t=t, tem_gt=s.H_gt is not None, base_ok=base_ok, a_ok=a_ok,
                         nova=a_ok and not base_ok, central=bool(info.get("vista_central")),
                         hip_centrais=info.get("hipoteses_centrais", 0), npe_base=npe(Hb, base_ok), npe_a=npe(Ha, a_ok)))
    return rows


def summary(rows):
    out = []
    for g in GAMES:
        rs = [r for r in rows if r["jogo"] == g and r["tem_gt"]]
        row = dict(jogo=g, frames=len(rs))
        for v in ("base", "a"):
            acc = np.array([r[f"npe_{v}"] for r in rs if r[f"{v}_ok"]], float)
            row |= {f"cob_{v}": float(np.mean([r[f"{v}_ok"] for r in rs])), f"aceitas_{v}": len(acc),
                    f"frac_erradas_{v}": float(np.mean(acc > WRONG)) if len(acc) else np.nan,
                    f"npe_med_{v}": float(np.median(acc)) if len(acc) else np.nan}
        new = np.array([r["npe_a"] for r in rs if r["nova"]], float)
        row |= dict(novas=len(new), novas_erradas=int((new > WRONG).sum()), npe_med_novas=float(np.median(new)) if len(new) else np.nan,
                    piora_erradas=row["frac_erradas_a"] - row["frac_erradas_base"])
        out.append(row)
    return out


if __name__ == "__main__":
    from src_v2.executor import SafeProcessPool, exit_if_failed
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    out = path("runs") / "a_triagem"
    out.mkdir(parents=True, exist_ok=True)
    clips, rows = clips_dev(), []
    with SafeProcessPool(n, initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=out / "manifestos") as ex:
        for r in ex.map(clip_rows, clips):
            if r is not None:
                rows += r
    exit_if_failed()
    for name, data in (("frames", rows), ("por_jogo", summary(rows))):
        with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    s = summary(rows)
    worse = [r["jogo"] for r in s if np.isfinite(r["piora_erradas"]) and r["piora_erradas"] > MAX_WORSE]
    novas = sum(r["novas"] for r in s)
    for r in s:
        print(f"jogo {r['jogo']}: cobertura {r['cob_base']:.3f} -> {r['cob_a']:.3f}; aceitas erradas {r['frac_erradas_base']:.3f} -> "
              f"{r['frac_erradas_a']:.3f}; NPE mediano {r['npe_med_base']:.4f} -> {r['npe_med_a']:.4f}; "
              f"novas {r['novas']} ({r['novas_erradas']} erradas, NPE mediano {r['npe_med_novas']:.4f})")
    print("PARA (regra do plano): " + (f"aceitas erradas pioram > {MAX_WORSE} nos jogos {worse}" if worse else "nenhuma H nova")
          if worse or not novas else "passa na triagem: segue para a confirmação na metade fixa")
