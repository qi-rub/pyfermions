import numpy as np
from .signal import *


def test_vdot():
    assert signal([1, 2j], start=-1).vdot(signal([3, 4])) == -6j


def test_add():
    a = signal([1, 2j], start=-1) + signal([3, 4])
    assert a.isclose(signal([1, 3 + 2j, 4], start=-1))


def test_sub():
    a = signal([1, 2j], start=-1) - signal([3, 4])
    assert a.isclose(signal([1, -3 + 2j, -4], start=-1))


def test_pow():
    a = signal([2, 2j], start=2) ** 2
    assert a.isclose(signal([4, -4], start=2))


def test_abs():
    a = signal([-3, 2j, 1 - 1j], start=1).abs()
    assert a.isclose(signal([3, 2, np.sqrt(2)], start=1))


def test_modulate():
    a = signal([-3, -2, -1, 0, 1, 2, 3, 4], start=-3)
    A = signal([3, -2, 1, 0, -1, 2, -3, 4], start=-3)
    assert a.modulate(-1 + 0j).isclose(A)
    assert a.modulate(-1.0).isclose(A)


def test_reverse():
    N = 100
    a = signal(np.random.rand(N), np.random.randint(-N, N))
    a_rev = a.reverse()

    assert a_rev.reverse().isclose(a)
    assert all(a[n] == a_rev[-n] for n in a.range)
    assert all(a_rev[n] == a[-n] for n in a_rev.range)


def test_downsample():
    a = signal([0, 1, 2, 3, 4, 5])
    assert a.downsample().isclose(signal([0, 2, 4]))

    a = signal([-3, -2, -1, 0, 1, 2], start=-3)
    assert a.downsample().isclose(signal([-2, 0, 2], start=-1))

    N = 100
    a = signal(np.random.rand(N), np.random.randint(-N, N))
    b = a.downsample()
    for n in a.range:
        if n % 2 == 0:
            assert b[n // 2] == a[n]


def test_upsample():
    a = signal([0, 1, 2, 3, 4, 5])
    assert a.upsample().isclose(signal([0, 0, 1, 0, 2, 0, 3, 0, 4, 0, 5]))

    a = signal([-3, -2, -1, 0, 1, 2], start=-3)
    assert a.upsample().isclose(signal([-3, 0, -2, 0, -1, 0, 0, 0, 1, 0, 2], start=-6))

    N = 100
    a = signal(np.random.rand(N), np.random.randint(-N, N))
    b = a.upsample()
    for n in b.range:
        assert b[n] == (a[n // 2] if n % 2 == 0 else 0)
