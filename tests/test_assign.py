import numpy as np

from src.assign import R180, valid_orientation

SIZE = (1920, 1080)
H_BROADCAST = np.array([[90.993262, -18.046952, 1006.07514],       # H_gt do SNGS-070/101
                        [-0.342962, 4.600815, 752.869136], [-0.000443, -0.018014, 1.0]])


def test_orientation_rejects_rotated_and_mirrored():
    # o modelo é simétrico por (X, Y) -> (-X, -Y): H e H·R180 projetam as mesmas linhas
    assert valid_orientation(H_BROADCAST, SIZE)
    assert not valid_orientation(H_BROADCAST @ R180, SIZE)                  # Y+ do lado oposto à câmera
    assert not valid_orientation(H_BROADCAST @ np.diag([-1.0, 1, 1]), SIZE)  # espelhada em X
    assert not valid_orientation(H_BROADCAST @ np.diag([1.0, -1, 1]), SIZE)  # espelhada em Y
