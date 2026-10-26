"""v2, B2: centro da câmera da H (src_v2/camera.py) e a regra da âncora (temporal.camera_ok)."""
import numpy as np

import src_v2.temporal as T
from src_v2.camera import center, compose, decompose

SIZE = (1920, 1080)


def _rot(pan, tilt, roll=0.0):
    """Mundo -> câmera: olhando para -Y (X à direita, Z para baixo), pan na vertical, tilt para baixo."""
    cp, sp, ct, st, cr, sr = np.cos(pan), np.sin(pan), np.cos(tilt), np.sin(tilt), np.cos(roll), np.sin(roll)
    R0 = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0.0]])
    Rz = np.array([[cp, -sp, 0], [sp, cp, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]])
    Rr = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
    return Rr @ Rx @ R0 @ Rz


def test_decompose_inverts_compose_for_broadcast_cameras():
    rng = np.random.default_rng(0)
    for _ in range(200):
        C = np.array([rng.uniform(-10, 10), rng.uniform(40, 90), -rng.uniform(8, 40)])
        f = rng.uniform(1200, 9000)
        R = _rot(rng.uniform(-0.8, 0.8), rng.uniform(0.1, 0.6), rng.uniform(-0.03, 0.03))
        H = compose(f, R, C, SIZE) * rng.choice([-1, 1]) * rng.uniform(0.1, 10)    # escala e sinal arbitrários
        f2, R2, C2 = decompose(H, SIZE)
        assert abs(f2 - f) / f < 1e-6 and np.allclose(R2, R, atol=1e-6) and np.allclose(C2, C, atol=1e-4)


def test_homography_without_real_focal_has_no_center():
    # afim (sem perspectiva): as duas restrições dão 1/f² = 0, nenhuma câmera pinhole finita
    assert center(np.array([[10.0, 0, 960], [0, 10, 540], [0, 0, 1]]), SIZE) is None


def test_anchors_apply_the_camera_rule_only_with_a_reference(monkeypatch):
    from types import SimpleNamespace
    import src_v2.evaluate as E
    n, ref = 60, np.array([0.0, 50.0, -10.0])
    near, far = compose(3000, _rot(0.1, 0.3), ref + [0, 2.0, 0], SIZE), compose(3000, _rot(0.1, 0.3), ref + [0, 15.0, 0], SIZE)
    ser = {"H": np.repeat(near[None], n, axis=0), "img": np.full(n, 0.5), "iou": np.full(n, 0.5)}
    ser["img"][10], ser["iou"][10] = 0.8, 0.9
    ser["img"][40], ser["iou"][40], ser["H"][40] = 0.8, 0.9, far
    monkeypatch.setattr(T, "propagate", lambda cf, a, H, stop, step, lines=True: {u: H for u in range(a + step, stop, step)})
    monkeypatch.setattr(E, "image_grid_displacement", lambda Ha, Hb, size: 0.0)
    monkeypatch.setitem(T.T, "anchor_min_nota", 1.6)
    monkeypatch.setitem(T.T, "anchor_c_max_m", 6.9)
    cf, seg = SimpleNamespace(size=SIZE), np.zeros(n, int)
    assert set(T.anchors(ser, cf, seg)[0]) >= {10, 40}                   # sem referência: o B1 só
    anc = T.anchors(ser, cf, seg, c_ref=ref)[0]
    assert 10 in anc and 40 not in anc                                  # câmera a 15 m da do jogo


def test_camera_ok_uses_the_threshold_and_rejects_impossible_cameras(monkeypatch):
    monkeypatch.setitem(T.T, "anchor_c_max_m", 6.9)
    ref = np.array([0.0, 50.0, -10.0])
    R = _rot(0.1, 0.3)
    assert T.camera_ok(compose(3000, R, ref + [0, 6.0, 0], SIZE), ref, SIZE)          # 6 m: aceita
    assert not T.camera_ok(compose(3000, R, ref + [0, 8.0, 0], SIZE), ref, SIZE)      # 8 m: recusa
    assert not T.camera_ok(np.array([[10.0, 0, 960], [0, 10, 540], [0, 0, 1]]), ref, SIZE)
