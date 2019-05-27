import numpy as np
from .utils import *


def test_convmtx():
    expected = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [-1.0, 1.0, 0.0, 0.0, 0.0],
        [0.0, -1.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, -1.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, -1.0],
    ]
    assert np.allclose(convmtx([1, -1], 5), expected)
