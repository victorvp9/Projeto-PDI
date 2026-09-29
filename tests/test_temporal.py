import numpy as np

from src.temporal import _runs, smooth_series


def test_runs_split_on_long_gaps():
    valid = np.zeros(100, bool)
    valid[0:10] = valid[20:30] = valid[70:80] = True          # lacunas de 10 e de 40 frames
    assert _runs(valid, 25) == [(0, 29), (70, 79)]


def test_savgol_keeps_cubic_and_reduces_noise():
    t = np.arange(200.0)
    x = 1e-4 * (t - 100) ** 3 + 0.5 * t                        # cúbica: o grau 3 a preserva
    X = np.c_[x, 2 * x]
    assert np.allclose(smooth_series(X), X, atol=1e-6)
    noisy = X + np.random.default_rng(0).normal(0, 1, X.shape)
    assert np.std(smooth_series(noisy) - X) < 0.5 * np.std(noisy - X)


def test_gaps_filled_only_up_to_max_gap():
    X = np.c_[np.arange(100.0)]
    X[40:60] = np.nan                                          # lacuna de 20 frames
    assert np.isfinite(smooth_series(X, max_gap=25)).all()
    assert np.isnan(smooth_series(X, max_gap=10)[40:60]).all()
