import numpy as np

from src.assign import R180, estimate, valid_orientation
from src.config import CFG
from src.conics import detect
from src.evaluate import image_grid_displacement
from src.render import lines_mask, pitch_mask

SIZE = (1920, 1080)
H_BROADCAST = np.array([[90.993262, -18.046952, 1006.07514],       # H_gt do SNGS-070/101
                        [-0.342962, 4.600815, 752.869136], [-0.000443, -0.018014, 1.0]])


def test_orientation_rejects_rotated_and_mirrored():
    # o modelo é simétrico por (X, Y) -> (-X, -Y): H e H·R180 projetam as mesmas linhas
    assert valid_orientation(H_BROADCAST, SIZE)
    assert not valid_orientation(H_BROADCAST @ R180, SIZE)                  # Y+ do lado oposto à câmera
    assert not valid_orientation(H_BROADCAST @ np.diag([-1.0, 1, 1]), SIZE)  # espelhada em X
    assert not valid_orientation(H_BROADCAST @ np.diag([1.0, -1, 1]), SIZE)  # espelhada em Y


def test_gate_rejects_wrong_midfield_h():
    # meio-campo sintético (só a lateral do fundo, a linha do meio e o círculo): o pipeline
    # mínimo aceitava uma H a ~3000 px da certa com resíduo de 4,5 px; o portão tem de barrá-la
    marks, grass = lines_mask(H_BROADCAST, SIZE), pitch_mask(H_BROADCAST, SIZE)
    segs, _, cid = detect(marks, {**CFG["lines"], "shape_filter": False})
    for mode in (None, "segments", "guided"):
        H, _ = estimate(marks, grass, segs[cid < 0], refine=mode)
        assert H is None or image_grid_displacement(H, H_BROADCAST, SIZE) <= 5, mode
