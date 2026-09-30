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


def test_hampel_drops_spike_keeps_ramp():
    from src.temporal import hampel_outliers
    t = np.arange(60.0)
    X = np.c_[0.2 * t, -0.4 * t] + np.random.default_rng(0).normal(0, 0.1, (60, 2))   # panorâmica lenta
    X[30] += 5                                                  # H errada aceita: salto isolado
    X[40:43] = np.nan                                           # lacuna: não julga nem quebra
    bad = hampel_outliers(X, 7, 3)
    assert bad[30] and bad.sum() == 1


def test_kalman_smooths_bridges_and_gates():
    """Trajetória de velocidade constante com ruído: o Kalman + RTS reduz o erro, cobre a
    lacuna de 10 frames e a porta de Mahalanobis descarta um salto de 20 m."""
    from src.temporal import kalman_series
    rng = np.random.default_rng(0)
    truth = np.stack([np.linspace(0, 30, 120) * (k + 1) / 4 for k in range(8)], 1)
    X = truth + rng.normal(0, 0.3, truth.shape)
    X[50:60] = np.nan
    X[80] += 20
    Y = kalman_series(X, 0.01, 0.1)
    assert np.median(np.abs(Y - truth)) < 0.5 * np.nanmedian(np.abs(X - truth))
    assert np.isfinite(Y[50:60]).all()
    assert np.abs(Y[80] - truth[80]).max() < 1


def test_cut_distance_separates_cut_from_noise():
    from src.config import CFG
    from src.render import render_synthetic
    from src.temporal import frame_hist, hist_distance
    H = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])
    a = render_synthetic(H, (1280, 720))
    rng = np.random.default_rng(0)
    b = np.clip(a.astype(int) + rng.normal(0, 3, a.shape), 0, 255).astype(np.uint8)   # mesmo plano, ruído de câmera
    c = rng.integers(0, 256, a.shape, dtype=np.uint8)                                  # outra cena (torcida, close)
    thr = CFG["temporal"]["cut_thr"]
    assert hist_distance(frame_hist(a), frame_hist(b)) < thr < hist_distance(frame_hist(a), frame_hist(c))


def _synthetic_frame():
    """Frame sintético (imagem, BGR) com ruído e 'jogadores': manchas compactas escuras e
    claras sobre o gramado, para exercitar o filtro de forma e os componentes."""
    import cv2
    from src.render import render_synthetic
    H = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])
    rng = np.random.default_rng(1)
    img = np.clip(render_synthetic(H, (1280, 720)) + rng.normal(0, 6, (720, 1280, 3)), 0, 255).astype(np.uint8)
    for _ in range(15):
        u, v = int(rng.integers(50, 1230)), int(rng.integers(200, 700))
        color = (40, 40, 180) if rng.random() < 0.5 else (230, 230, 230)
        cv2.ellipse(img, (u, v), (int(rng.integers(4, 10)), int(rng.integers(12, 30))), 0, 0, 360, color, -1)
    return H, img


def test_propagation_survives_degenerate_homography():
    """Uma âncora com H singular (SNGS-049 derrubou o 6c na valid assim) não pode
    quebrar a propagação: a H degenerada não é aceita e o ajuste que passa por ela falha
    sem exceção."""
    from types import SimpleNamespace
    from src.temporal import ClipFrames, propagate
    H, img = _synthetic_frame()
    singular = H.copy()
    singular[2] = 0.5 * singular[0] + 0.5 * singular[1]            # terceira linha dependente: posto 2
    samples = [SimpleNamespace(image=img, size=(1280, 720), sequence_id="sint") for _ in range(3)]
    out = propagate(ClipFrames(samples), 0, singular, 3, 1)
    assert sorted(out) == [1, 2]


def test_masks_equal_reference_formula():
    """_masks com o gramado bruto uma vez só = a composição original (grass_mask etc.)."""
    import cv2
    from src.config import CFG
    from src.lines import shape_filter
    from src.segment import _grass_raw, grass_mask, line_mask, params
    from src.temporal import T, _masks
    _, img = _synthetic_frame()
    P = params("gsr")
    grass = grass_mask(img, P)
    marks = line_mask(img, grass, P)
    nong = grass & ~_grass_raw(img, P)
    compact = nong & ~shape_filter(nong, CFG["lines"])
    k = 2 * int(T["compact_dilate_frac"] * img.shape[0]) + 1
    compact = cv2.dilate(compact.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    for a, b in zip(_masks(img), (grass, marks, grass & ~compact)):
        assert np.array_equal(a, b)


def test_guided_points_equal_assign():
    from src.assign import guided_points
    from src.pitch_model import POLYLINES
    from src.render import lines_mask
    from src.temporal import _guided_points
    H, _ = _synthetic_frame()
    marks = lines_mask(H, (1280, 720))
    H2 = np.array([[1, 0, 4], [0, 1, -3], [0, 0, 1]]) @ H          # H levemente errada, como na propagação
    a, b = guided_points(H2, marks, list(POLYLINES)), _guided_points(H2, marks, list(POLYLINES))
    assert a.keys() == b.keys() and len(a) > 3
    assert all(np.array_equal(a[k], b[k]) for k in a)


def test_gpu_masks_equal_cpu():
    """GPU (src/gpu.py) = CPU (temporal._masks), pixel a pixel, no sintético e em 3 frames
    reais do GSR se estiverem no disco."""
    import cv2
    import pytest
    from src import gpu
    from src.temporal import _masks
    if not gpu.AVAILABLE:
        pytest.skip("sem GPU ou sem o extra gpu")
    _, img = _synthetic_frame()
    frames = [img]
    from src.config import path
    clip = path("gsr") / "train" / "SNGS-099"
    if clip.exists():
        from src.io import gsr
        s = gsr.load_clip(clip, fit="none")
        frames += [s[i].image for i in (100, 400, 700)]
    for img in frames:
        h, w = img.shape[:2]
        got = gpu.GPUMasks((w, h))(cv2.cvtColor(img, cv2.COLOR_BGR2LAB))
        for packed, ref in zip(got, _masks(img)):
            assert np.array_equal(np.unpackbits(packed)[:w * h].reshape(h, w).astype(bool), ref)


def test_lk_propagates_known_pan_and_zoom():
    """Gramado com textura presa ao campo, panorâmica de 3 px/frame e zoom de 0,4%/frame
    conhecidos: a H propagada por 9 frames concorda com a verdadeira a < 1 px."""
    from types import SimpleNamespace

    import cv2
    from src.evaluate import image_grid_displacement
    from src.pitch_model import LINE_WIDTH, POLYLINES
    from src.render import R, TOP_SIZE, _to_top, _warp
    from src.temporal import ClipFrames, propagate
    noise = cv2.GaussianBlur(np.random.default_rng(0).normal(0, 1, TOP_SIZE[::-1]).astype(np.float32), (0, 0), 4)
    top = np.clip(np.float32(R["grass_bgr"]) + 20 * noise[..., None] / noise.std(), 0, 255).astype(np.uint8)
    for poly in POLYLINES.values():
        cv2.polylines(top, [_to_top(poly)], False, (255, 255, 255), int(round(LINE_WIDTH * R["px_per_m"])))
    size = (1280, 720)
    H0 = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])
    Hs = [np.array([[1 + 0.004 * t, 0, 3 * t - 0.004 * t * 640], [0, 1 + 0.004 * t, -0.004 * t * 360], [0, 0, 1]]) @ H0
          for t in range(10)]
    samples = [SimpleNamespace(image=_warp(top, H, size, cv2.INTER_LINEAR, tuple(R["grass_bgr"])), size=size, sequence_id="sint")
               for H in Hs]
    out = propagate(ClipFrames(samples), 0, Hs[0], 10, 1)
    assert image_grid_displacement(Hs[0], Hs[9], size) > 20            # sem fluxo, erraria muito
    assert image_grid_displacement(out[9], Hs[9], size) < 1.0


def test_ecc_recovers_known_motion_and_slip_of_true_series_is_small():
    """Panorâmica de 3 px/frame com zoom de 0,4%/frame sobre gramado texturizado: o ECC
    recupera o movimento, o deslize da série verdadeira é ~0 e o de uma série com tremor
    de 2 px aparece."""
    import cv2
    from src.pitch_model import LINE_WIDTH, POLYLINES
    from src.render import R, TOP_SIZE, _to_top, _warp
    from src.stability import ecc_motion, slip
    from src.temporal import _stability_grid
    noise = cv2.GaussianBlur(np.random.default_rng(0).normal(0, 1, TOP_SIZE[::-1]).astype(np.float32), (0, 0), 4)
    top = np.clip(np.float32(R["grass_bgr"]) + 20 * noise[..., None] / noise.std(), 0, 255).astype(np.uint8)
    for poly in POLYLINES.values():
        cv2.polylines(top, [_to_top(poly)], False, (255, 255, 255), int(round(LINE_WIDTH * R["px_per_m"])))
    size = (1280, 720)
    H0 = np.array([[7, -6.4, 640], [0, 4, 300], [0, -0.01, 1]])
    Hs = np.array([np.array([[1 + 0.004 * t, 0, 3 * t - 0.004 * t * 640], [0, 1 + 0.004 * t, -0.004 * t * 360], [0, 0, 1]]) @ H0
                   for t in range(6)])
    gray = [cv2.cvtColor(_warp(top, H, size, cv2.INTER_LINEAR, tuple(R["grass_bgr"])), cv2.COLOR_BGR2GRAY) for H in Hs]
    motions, usable = [np.full((3, 3), np.nan)], [False]
    for t in range(1, len(Hs)):
        W, ok, _ = ecc_motion(gray[t - 1], gray[t], np.ones_like(gray[t], bool))
        motions.append(W)
        usable.append(ok)
    assert all(usable[1:])
    grid = _stability_grid()
    assert np.nanmax(slip(Hs, motions, usable, size, grid)) < 1.0
    shaky = Hs.copy()
    shaky[2] = np.array([[1, 0, 2.0], [0, 1, 0], [0, 0, 1]]) @ Hs[2]
    assert np.nanmax(slip(shaky, motions, usable, size, grid)) > 1.5
