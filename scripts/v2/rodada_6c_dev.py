"""Rodada do 6c no dev inteiro (115 clipes, série do cache_v2) para uma mudança de propagação ou de
âncoras do v2, e a decisão pelo critério congelado (docs/05-melhorias-plano.md, seção 4):
Δ = LocSim@5 penalizado do 6c (mudança − base) por jogo; aceita se Δ > 0 em >= 4 de 6 jogos, média
dos Δ > 0 e nenhum Δ < −0,03. Relata também o teto, a cobertura, as aceitas erradas, os clipes que
perderam todas as âncoras e o LocSim que tinham antes.

- Cada clipe vai para `por_clipe.csv` (e `por_clipe_logo9.csv`) assim que o resultado sai, e cada
  tabela por jogo é gravada antes da decisão: uma falha no fim não perde o cálculo (Victor, 2026-10-16).

- Antes de rodar, os caches do 6c da base (os do cache_v2 com a chave atual de antes da mudança) são
  copiados para outputs/cache_v2/<arquivo da base>/ (só se ainda não existem), para a comparação por
  clipe e para voltar à base sem recalcular.
- `--logo9`: o B1 no jogo 9 também com o limiar leave-one-game-out (a regra do diagnóstico nos outros
  5 jogos), por _eval_clip_6c sem cache, com o limiar no config do processo e dos trabalhadores.
Uso (da raiz): PYTHONPATH=. uv run python scripts/v2/rodada_6c_dev.py <nome> <arquivo da base>
<csv da base por jogo> [--logo9] [--logo-c=<jogo>:<limiar> ...] [trabalhadores]"""
import csv
import json
import pickle
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from baseline_dev import WRONG, per_game                   # noqa: E402  (mesmas métricas da linha de base)
from src_v2.config import path                              # noqa: E402

DEV = ("train", "valid")
GAMES = ("4", "6", "9", "2", "3", "5")
MIN_GAMES, MAX_DROP = 4, -0.03


def clips_dev():
    return [c for s in DEV for c in sorted((path("gsr") / s).glob("SNGS-*"))]


def archive(name):
    """Copia os caches do 6c atuais (base) para outputs/cache_v2/<name>/, se ainda não copiados."""
    src, dst = path("cache") / "eval_6c", path("cache") / name
    if dst.exists():
        return False
    for s in DEV:
        shutil.copytree(src / s, dst / s)
    return True


def clip_locsim(r, variant="6c fluxo"):
    from src_v2.evaluate import locsim
    fr = [x for x in r[0] if x["variante"] == variant]
    n = sum(x["n_pessoas"] for x in fr)
    return sum(locsim(x["locsim_d"], 5).sum() for x in fr if "locsim_d" in x) / n if n else np.nan


def clip_row(c, r):
    from src_v2.io import gsr
    acc = np.array([a["npe"] for a in r[2] if a["aceita"]], float)
    gt = [x["has_pred"] for x in r[0] if x["variante"] == "6c fluxo" and x["has_gt"]]
    return dict(particao=c.parent.name, clipe=c.name, jogo=gsr.game_id(c), locsim_pen_6c=clip_locsim(r),
                locsim_pen_teto=clip_locsim(r, "6c âncora de gabarito"), cob_6c=float(np.mean(gt)) if gt else np.nan,
                aceitas=len(acc), aceitas_erradas=int((acc[np.isfinite(acc)] > WRONG).sum()))


def stream(out, name, clips, results):
    """Consome os resultados na ordem dos clipes e grava cada um em <name>.csv assim que sai."""
    res = {}
    with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = None
        for c, r in zip(clips, results):
            res[c] = r
            if r is None:                                    # falhou: está no manifesto
                continue
            row = clip_row(c, r)
            if w is None:
                w = csv.DictWriter(f, fieldnames=list(row))
                w.writeheader()
            w.writerow(row)
            f.flush()
    return res


def run_6c(clips, n, out):
    import src_v2.temporal as T
    from src_v2.executor import SafeProcessPool, exit_if_failed
    pool = lambda: SafeProcessPool(n, initializer=cv2.setNumThreads, initargs=(1,), manifest_dir=out / "manifestos")
    T.build_series(pool, clips)                              # tudo em cache: só confere
    with pool() as ex:
        key = T._eval_6c_key()
        res = stream(out, "por_clipe", clips, ex.map(T._eval_clip_6c_cached, clips, [key] * len(clips)))
        ex.verify_keys(key, lambda a: pickle.loads(T._eval_6c_path(a[0]).read_bytes())[0] if T._eval_6c_path(a[0]).exists() else None)
    exit_if_failed()
    assert all(r is not None for r in res.values())
    return res


def _init_threshold(v):
    cv2.setNumThreads(1)
    from src_v2.config import CFG
    CFG["temporal"]["anchor_min_nota"] = v


def logo9(n, out):
    """B1 no jogo 9 com o limiar leave-one-game-out, sem cache."""
    import src_v2.temporal as T
    from src_v2.executor import SafeProcessPool, exit_if_failed
    from src_v2.io import gsr
    rs = list(csv.DictReader(open(path("runs") / "b1_diagnostico" / "sinais_por_candidata.csv", encoding="utf-8")))
    right = np.array([-float(r["nota"]) for r in rs if r["jogo"] in ("4", "6", "2", "3", "5") and r["errada"] == "False"])
    thr = -float(np.quantile(right, 0.98, method="higher"))
    clips = [c for c in clips_dev() if gsr.game_id(c) == "9"]
    with SafeProcessPool(n, initializer=_init_threshold, initargs=(thr,), manifest_dir=out / "manifestos") as ex:
        res = stream(out, "por_clipe_logo9", clips, ex.map(T._eval_clip_6c, clips))
    exit_if_failed()
    assert all(r is not None for r in res.values())
    return thr, res


def _init_c_threshold(v):
    cv2.setNumThreads(1)
    from src_v2.config import CFG
    CFG["temporal"]["anchor_c_max_m"] = v


def logo_c(n, out, game, thr):
    """B2 no jogo `game` com o limiar leave-one-game-out do centro da câmera (`thr`, m), sem cache."""
    import src_v2.temporal as T
    from src_v2.executor import SafeProcessPool, exit_if_failed
    from src_v2.io import gsr
    clips = [c for c in clips_dev() if gsr.game_id(c) == game]
    with SafeProcessPool(n, initializer=_init_c_threshold, initargs=(thr,), manifest_dir=out / "manifestos") as ex:
        res = stream(out, f"por_clipe_logo_c{game}", clips, ex.map(T._eval_clip_6c, clips))
    exit_if_failed()
    assert all(r is not None for r in res.values())
    return res


def decide(delta):
    d = [delta[g] for g in GAMES]
    ok = (bool(sum(x > 0 for x in d) >= MIN_GAMES), float(np.mean(d)) > 0, bool(min(d) >= MAX_DROP))   # bool: numpy.bool_ não vai para o json
    return dict(jogos_com_ganho=int(sum(x > 0 for x in d)), media=float(np.mean(d)), pior=float(min(d)),
                criterios=dict(ganho_em_4_de_6=ok[0], media_positiva=ok[1], nenhum_abaixo_de_menos_003=ok[2]), aceita=all(ok))


def write(out, name, rows):
    with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    name, base_dir, base_csv = sys.argv[1:4]
    flags = sys.argv[4:]
    n = int(next((a for a in flags if a.isdigit()), 10))
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    assert not git("status", "--porcelain", "--", "src_v2", "config_v2.yaml", "scripts/v2"), "código do v2 com alteração sem commit"
    out = path("runs") / name
    out.mkdir(parents=True, exist_ok=True)
    print("caches da base guardados agora" if archive(base_dir) else "caches da base já guardados", flush=True)
    from src_v2.io import gsr
    clips = clips_dev()
    game = {c: gsr.game_id(c) for c in clips}
    res = run_6c(clips, n, out)
    rows, med = per_game(res)
    base = {r["jogo"]: r for r in csv.DictReader(open(base_csv, encoding="utf-8")) if r["particao"] != "mediana"}
    for r in rows:
        b = base[r["jogo"]]
        r |= {f"base_{k}": float(b[k]) for k in ("locsim_pen_6c", "locsim_pen_teto", "cob_6c", "sem_ancora", "aceitas_erradas")}
        r["delta_6c"], r["delta_teto"] = r["locsim_pen_6c"] - r["base_locsim_pen_6c"], r["locsim_pen_teto"] - r["base_locsim_pen_teto"]
    write(out, "por_jogo", rows + [med])
    dec = decide({r["jogo"]: r["delta_6c"] for r in rows})
    lost = []                                                # clipes que tinham âncora na base e ficaram sem nenhuma
    for c, r in res.items():
        k, rb = pickle.loads((path("cache") / base_dir / c.parent.name / f"{c.name}.pkl").read_bytes())
        if any(a["aceita"] for a in rb[2]) and not any(a["aceita"] for a in r[2]):
            lost.append(dict(particao=c.parent.name, clipe=c.name, jogo=game[c], locsim_pen_6c_antes=clip_locsim(rb),
                             aceitas_antes=sum(a["aceita"] for a in rb[2]),
                             aceitas_erradas_antes=sum(a["aceita"] and np.isfinite(a["npe"]) and a["npe"] > 0.05 for a in rb[2])))
    write(out, "clipes_que_perderam_ancora", lost or [dict(clipe="nenhum")])
    meta = dict(commit=git("rev-parse", "HEAD"), base=base_csv, decisao=dec)
    if "--logo9" in flags:
        thr, r9 = logo9(n, out)
        rows9, _ = per_game(r9)
        d9 = rows9[0]["locsim_pen_6c"] - float(base["9"]["locsim_pen_6c"])
        write(out, "por_jogo_logo9", [rows9[0] | dict(limiar=thr, delta_6c=d9)])
        meta["logo_jogo9"] = dict(limiar=thr, locsim_pen_6c=rows9[0]["locsim_pen_6c"], locsim_pen_teto=rows9[0]["locsim_pen_teto"], delta_6c=d9,
                                  aceitas_erradas=rows9[0]["aceitas_erradas"], aceitas=rows9[0]["aceitas"], sem_ancora=rows9[0]["sem_ancora"],
                                  decisao=decide({r["jogo"]: (d9 if r["jogo"] == "9" else r["delta_6c"]) for r in rows}))
    # v2, B2: `--logo-c=<jogo>:<limiar>` (um por jogo em que o limiar LOGO recusa âncoras diferentes das
    # do limiar do treino); a decisão usa o Δ LOGO nesses jogos e o da rodada nos outros
    logo = dict(a.split("=", 1)[1].split(":") for a in flags if a.startswith("--logo-c="))
    if logo:
        dl, meta["logo_c"] = {}, {}
        for g, thr in logo.items():
            rg, _ = per_game(logo_c(n, out, g, float(thr)))
            dl[g] = rg[0]["locsim_pen_6c"] - float(base[g]["locsim_pen_6c"])
            write(out, f"por_jogo_logo_c{g}", [rg[0] | dict(limiar=float(thr), delta_6c=dl[g])])
            meta["logo_c"][g] = dict(limiar=float(thr), locsim_pen_6c=rg[0]["locsim_pen_6c"], delta_6c=dl[g],
                                     locsim_pen_teto=rg[0]["locsim_pen_teto"], aceitas=rg[0]["aceitas"],
                                     aceitas_erradas=rg[0]["aceitas_erradas"], sem_ancora=rg[0]["sem_ancora"])
        meta["decisao_logo"] = decide({r["jogo"]: dl.get(r["jogo"], r["delta_6c"]) for r in rows})
    (out / "decisao.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(f"jogo {r['jogo']}: 6c {r['base_locsim_pen_6c']:.4f} -> {r['locsim_pen_6c']:.4f} (Δ {r['delta_6c']:+.4f}); teto {r['base_locsim_pen_teto']:.4f} -> "
              f"{r['locsim_pen_teto']:.4f}; aceitas erradas {int(r['base_aceitas_erradas'])} -> {r['aceitas_erradas']}; sem âncora {int(r['base_sem_ancora'])} -> {r['sem_ancora']}")
    print(json.dumps(meta, ensure_ascii=False, indent=1))
