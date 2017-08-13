import numpy as np
from .signal import *
from .wavelets import *


def random_signal():
    N = 100
    return signal(
        np.random.rand(N) + 1j * np.random.rand(N), np.random.randint(-N, N))


def test_analyze_and_reconstruct():
    a = random_signal()
    assert DAUBECHIES_D4.reconstruct(*DAUBECHIES_D4.analyze(a)).isclose(a)


def test_reconstruct_and_analyze():
    a = random_signal()
    b = random_signal()
    A, B = DAUBECHIES_D4.analyze(DAUBECHIES_D4.reconstruct(a, b))
    assert a.isclose(A)
    assert b.isclose(B)


def test_scaling_from_reconstruct():
    scaling_filter = DAUBECHIES_D4.reconstruct(signal([1]), signal())
    assert scaling_filter.isclose(DAUBECHIES_D4.scaling_filter)


def test_from_scaling_filter():
    assert orthogonal_wavelet.from_scaling_filter(
        DAUBECHIES_D4.scaling_filter).wavelet_filter.isclose(
            DAUBECHIES_D4.wavelet_filter)


def test_from_wavelet_filter():
    assert orthogonal_wavelet.from_wavelet_filter(
        DAUBECHIES_D4.wavelet_filter).scaling_filter.isclose(
            DAUBECHIES_D4.scaling_filter)
