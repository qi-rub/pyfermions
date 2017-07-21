import numpy as np
from .hilbert import *


def test_allpass():
    assert np.allclose(allpass(1 / 2, 2), [1, 2, 1 / 5])
    assert np.allclose(allpass(1 / 2, 3), [1, 5, 3, 1 / 7])


def test_leja():
    N = 100
    roots = np.exp(1j * np.arange(N) * 2 * np.pi / N)
    poly = np.poly(leja(roots))
    poly_expected = np.zeros(N + 1)
    poly_expected[0] = 1
    poly_expected[-1] = -1
    assert np.allclose(poly, poly_expected)


def test_sfact_real():
    N = 100
    g = np.random.rand(N)
    h = np.convolve(g, g[::-1])
    g = sfact(h)
    assert np.allclose(h, np.convolve(g, g[::-1]))


def test_sfact_complex():
    N = 100
    g = np.random.rand(N) + 1j * np.random.rand(N)
    h = np.convolve(g, g[::-1])
    g = sfact(h)
    assert np.allclose(h, np.convolve(g, g[::-1]), atol=1e-7)


def test_sfact_roots_of_unity():
    N = 100
    roots = np.r_[np.exp(1j * np.arange(N) * 2 * np.pi / N), [-1, +1]]
    h = np.poly(leja(roots))
    g = sfact(h)
    assert np.allclose(h, np.convolve(g, g[::-1]))


def test_sfact_vs_matlab_sfactM():
    h = [
        0.23500808, 0.40292636, 0.19767172, 0.80314786, 1.1484146, 0.6606251,
        1.12983991, 1.76151214, 1.81722044, 1.96675452, 2.03677809, 1.61807876,
        2.18016504, 3.0040162, 2.99760105, 3.02904011, 3.36237175, 2.91711583,
        3.70246132, 5.51076004, 3.70246132, 2.91711583, 3.36237175, 3.02904011,
        2.99760105, 3.0040162, 2.18016504, 1.61807876, 2.03677809, 1.96675452,
        1.81722044, 1.76151214, 1.12983991, 0.6606251, 1.1484146, 0.80314786,
        0.19767172, 0.40292636, 0.23500808
    ]
    g = sfact(h)
    assert np.allclose(h, np.convolve(g, g[::-1]))

    g_expected = [
        0.49289611, 0.87130989, 0.06518786, 0.15211069, 0.444786, 0.17963909,
        0.46867431, 0.42013943, 0.3031951, -0.11275117, 0.63739043, 0.95572241,
        0.70225929, 0.82608458, 0.20958084, 0.4269365, 0.80891174, 0.38283447,
        -0.02537196, 0.4767903
    ]
    assert np.allclose(g, g_expected)


def test_hwlet_4_2_vs_matlab():
    expected_h = [
        -0.00178533, 0.01335887, 0.03609074, -0.03472219, 0.04152506,
        0.56035837, 0.77458617, 0.22752075, -0.16040927, -0.06169425,
        0.01709941, 0.00228523
    ]
    expected_g = [
        -3.57066025e-04, -1.84753505e-04, 3.25914858e-02, 1.34499016e-02,
        -5.84667253e-02, 2.74643077e-01, 7.79566224e-01, 5.40973789e-01,
        -4.03150079e-02, -1.33201379e-01, -5.91212957e-03, 1.14261464e-02
    ]

    h, g = selesnick_hwlet(4, 2)
    assert np.allclose(h.scaling_filter, expected_h)
    assert np.allclose(g.scaling_filter, expected_g)


def test_hwlet_7_3_vs_matlab():
    expected_h = [
        -0.000008509559837, 0.000155053328906, 0.000335908682589,
        -0.003379348176989, -0.001317563525896, 0.020806061482011,
        -0.001260616026056, -0.058104797961116, 0.054771136286585,
        0.146767682794254, -0.266672541675869, -0.758239803854417,
        -0.560666055445088, -0.051046983845276, 0.089849110821292,
        -0.001431140280180, -0.023599660375478, -0.002713741951713,
        0.001462009640675, 0.000080237287438
    ]
    expected_g = [
        -0.000001215651405, 0.000002700053073, 0.000460745831039,
        -0.001019936542747, -0.004774611651203, 0.009325818768637,
        0.020111376966657, -0.037222043377477, -0.027543138327351,
        0.140004382772676, 0.005882790359188, -0.565220412816159,
        -0.752956521033365, -0.287558708554270, 0.075533433775397,
        0.046016083257261, -0.025067132737740, -0.011996325750141,
        0.001247491291702, 0.000561661012064
    ]

    h, g = selesnick_hwlet(7, 3)
    assert np.allclose(h.scaling_filter, expected_h)
    assert np.allclose(g.scaling_filter, expected_g)
