"""v2, C: resumo por jogo da discordância (scripts/v2/c_discordancia.py) só com os frames da fusão."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "v2"))
from c_discordancia import summarize                        # noqa: E402


def test_summarize_uses_only_fused_frames_of_6c_flow():
    f = lambda d, npe, var="6c fluxo", gt=True: dict(variante=var, discordancia_c=d, npe=npe, has_gt=gt)
    rows = {"4": [f(0.01, 0.02), f(0.02, 0.03), f(0.03, 0.05), f(np.nan, 0.9), f(0.5, 0.9, "detector"), f(0.04, np.nan, gt=False)]}
    r = {x["jogo"]: x for x in summarize(rows)}
    assert r["4"]["frames_entre_ancoras"] == 4 and r["4"]["frames_com_gabarito"] == 3
    assert np.isclose(r["4"]["mediana"], 0.025) and np.isclose(r["4"]["maximo"], 0.04)
    assert np.isclose(r["4"]["spearman_npe"], 1.0)
    assert r["6"]["frames_entre_ancoras"] == 0 and np.isnan(r["6"]["mediana"])
