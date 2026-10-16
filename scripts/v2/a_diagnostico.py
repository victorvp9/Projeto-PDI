"""A, diagnóstico (decisoes.md, 2026-10-15): causa da falta de âncora nos clipes de dev sem
âncora aceita fora do jogo 3, com o método da Seção 7 do relatório v1 (1 frame a cada 75 com
H_gt): segmentação e enquadramento.

- Segmentação, com as funções de avaliação do v1 (scripts/rodada_test/analise_falhas.seg_diag,
  aqui pelo src_v2): campo projetado como grama, vazamento, cobertura das marcações a 2 px dos
  pontos anotados, resposta do filtro de linha e fração acima do limiar. Comparada com a mediana
  dos clipes com âncora do mesmo jogo.
- Enquadramento, pelas classes anotadas em cada frame amostrado (regra fixada antes de olhar):
  retas transversais (linhas de fundo, linhas principais das áreas, linha do meio) e
  longitudinais (laterais, lados das áreas) com >= 2 pontos anotados.
    vista central: linha do meio ou círculo central anotados e < 2 transversais;
    zona meio-área: sem linha do meio nem círculo central, < 2 transversais, com elementos da
      grande área ou o arco;
    2 + 2 disponível: >= 2 transversais e >= 2 longitudinais;
    outra: o resto.
  O clipe leva a classe da maioria dos frames amostrados; se a maioria é "2 + 2 disponível" e a
  segmentação está abaixo da dos clipes com âncora do jogo (cobertura a 2 px ou fração acima do
  limiar mais de 0,05 abaixo), a causa é "segmentação"; senão, "outra".
- Figuras para a inspeção visual (como no v1): modelo pela H_gt e pontos anotados | gramado e
  marcações, em outputs/runs_v2/a_diagnostico/figuras/.
Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/a_diagnostico.py <trabalhadores>"""
import csv
import json
import pickle
import sys
from collections import Counter

import cv2
import numpy as np

from src_v2.config import CFG, path

OUT = path("runs") / "a_diagnostico"
DEV = ("train", "valid")
STEP = 75
TRANSV = ("Side line left", "Side line right", "Middle line", "Big rect. left main", "Big rect. right main", "Small rect. left main", "Small rect. right main")
LONGIT = ("Side line top", "Side line bottom", "Big rect. left top", "Big rect. left bottom", "Big rect. right top", "Big rect. right bottom",
          "Small rect. left top", "Small rect. left bottom", "Small rect. right top", "Small rect. right bottom")
BIG = ("Big rect. left top", "Big rect. left bottom", "Big rect. left main", "Big rect. right top", "Big rect. right bottom",
       "Big rect. right main", "Circle left", "Circle right")
SEG_DROP = 0.05


def framing(classes):
    tv = [k for k in TRANSV if k in classes]
    lg = [k for k in LONGIT if k in classes]
    central = "Middle line" in classes or "Circle central" in classes
    if len(tv) >= 2 and len(lg) >= 2:
        return "2 + 2 disponível"
    if central and len(tv) < 2:
        return "vista central"
    if not central and len(tv) < 2 and any(k in classes for k in BIG):
        return "zona meio-área"
    return "outra"


def clip_diag(clip, figures):
    """Segmentação e enquadramento em 1 frame a cada 75 com H_gt e linhas anotadas."""
    from src_v2.evaluate import field_grass_and_leak, point_coverage
    from src_v2.io import gsr
    from src_v2.render import draw_overlay
    from src_v2.segment import debug_overlay, grass_mask, line_mask, line_response, params
    cv2.setNumThreads(1)
    P = params("gsr")
    out, tiles = [], []
    for s in gsr.load_clip(clip)[::STEP]:
        if s.H_gt is None or not s.lines_uv:
            continue
        img = s.image
        grass = grass_mask(img, P)
        resp = line_response(img, P)
        lines = line_mask(img, grass, P, response=resp)
        pts = np.concatenate(list(s.lines_uv.values()))
        u = np.clip(np.round(pts[:, 0]).astype(int), 0, img.shape[1] - 1)
        v = np.clip(np.round(pts[:, 1]).astype(int), 0, img.shape[0] - 1)
        frac, leak = field_grass_and_leak(grass, s.H_gt, s.size)
        classes = {k for k, p in s.lines_uv.items() if len(p) >= 2}
        out.append(dict(clipe=clip.name, frame=s.frame_idx, campo_grama=frac, vazamento=leak,
                        cobertura_2px=point_coverage(lines, pts, CFG["eval_segment"]["gsr_coverage_px"]),
                        resposta_mediana=float(np.median(resp[v, u])), acima_limiar=float(np.mean(resp[v, u] > P["line_thr"])),
                        transversais=sum(k in classes for k in TRANSV), longitudinais=sum(k in classes for k in LONGIT),
                        classes=" | ".join(sorted(classes)), enquadramento=framing(classes)))
        if figures:
            a = draw_overlay(img, s.H_gt, s.lines_uv)
            b = debug_overlay(img, grass, lines)
            t = np.hstack([cv2.resize(a, (640, 360)), cv2.resize(b, (640, 360))])
            cv2.putText(t, f"{clip.name} f{s.frame_idx}: {out[-1]['enquadramento']}".encode("ascii", "replace").decode(),
                        (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            tiles.append(t)
    if figures and tiles:
        d = OUT / "figuras"
        d.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / f"{clip.parent.name}_{clip.name}.jpg"), np.vstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 80])
    return out


def write(name, rows):
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    import src_v2.temporal as T
    from src_v2.executor import SafeProcessPool, exit_if_failed
    from src_v2.io import gsr
    OUT.mkdir(parents=True, exist_ok=True)
    clips = [c for s in DEV for c in sorted((path("gsr") / s).glob("SNGS-*"))]
    game = {c: gsr.game_id(c) for c in clips}
    has_anchor = {}
    for c in clips:
        k, r = pickle.loads(T._eval_6c_path(c).read_bytes())
        assert k == T._eval_6c_key()
        has_anchor[c] = any(a["aceita"] for a in r[2])
    target = [c for c in clips if not has_anchor[c] and game[c] != "3"]
    ref = [c for c in clips if has_anchor[c] and game[c] in {game[t] for t in target}]
    print(f"{len(target)} clipes sem âncora fora do jogo 3; {len(ref)} clipes com âncora dos mesmos jogos (referência)")
    jobs = target + ref
    with SafeProcessPool(int(sys.argv[1]), initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=OUT / "manifestos") as ex:
        res = dict(zip(jobs, ex.map(clip_diag, jobs, [c in target for c in jobs])))
    exit_if_failed()
    frames = [x | dict(jogo=game[c], grupo="sem âncora" if c in target else "com âncora") for c, rs in res.items() for x in rs]
    write("frames", frames)
    med = lambda rs, k: float(np.nanmedian([x[k] for x in rs])) if rs else np.nan
    keys = ("campo_grama", "vazamento", "cobertura_2px", "resposta_mediana", "acima_limiar")
    refg = {g: {k: med([x for c in ref if game[c] == g for x in res[c]], k) for k in keys} for g in {game[c] for c in ref}}
    out = []
    for c in target:
        rs = res[c]
        cnt = Counter(x["enquadramento"] for x in rs)
        main, _ = cnt.most_common(1)[0] if cnt else ("sem frames", 0)
        m = {k: med(rs, k) for k in keys}
        low = (m["cobertura_2px"] < refg[game[c]]["cobertura_2px"] - SEG_DROP) or (m["acima_limiar"] < refg[game[c]]["acima_limiar"] - SEG_DROP)
        cause = main if main in ("vista central", "zona meio-área") else ("segmentação" if main == "2 + 2 disponível" and low else "outra")
        out.append(dict(particao=c.parent.name, clipe=c.name, jogo=game[c], frames=len(rs), enquadramento_maioria=main,
                        enquadramentos=json.dumps(dict(cnt), ensure_ascii=False), segmentacao_abaixo_da_ref=low, causa_pela_regra=cause,
                        **m, **{f"ref_{k}": refg[game[c]][k] for k in keys}))
    write("clipes_sem_ancora", out)
    for r in out:
        print(r["particao"], r["clipe"], r["jogo"], r["enquadramento_maioria"], r["enquadramentos"], "| seg abaixo:", r["segmentacao_abaixo_da_ref"],
              "| causa:", r["causa_pela_regra"], f"| cob2 {r['cobertura_2px']:.2f} (ref {r['ref_cobertura_2px']:.2f}) acima {r['acima_limiar']:.2f} (ref {r['ref_acima_limiar']:.2f})")
