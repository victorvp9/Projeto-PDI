import numpy as np

from src.sweep_lines import pick_uniform


def test_pick_uniform_maps_global_index_to_item():
    # sorteando todos os pixels, cada item aparece com todos os seus índices (e o vazio, nenhum)
    counts = [("a", 3), ("b", 0), ("c", 5), ("d", 2)]
    picks = pick_uniform(counts, 10, np.random.default_rng(0))
    assert sorted(picks) == [("a", i) for i in range(3)] + [("c", i) for i in range(5)] + [("d", i) for i in range(2)]
