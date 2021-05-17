import numpy as np
import scipy.signal, scipy.linalg
from .utils import *
from .signal import *
from .wavelets import *

__all__ = ["allpass", "leja", "sfact", "selesnick_hwlet", "evenbly_white_hwlet"]


def allpass(tau, L):
    """
    Return the filter d[n] such that

      A(z) = z^{-L} D(1/z) / D(z)

    approximates A(z) = z^{-tau}.

    The length of the filter d[n] is L+1.
    """
    n = np.arange(L)
    x = np.r_[1, (L - n) * (L - n - tau) / (n + 1) / (n + 1 + tau)]
    return np.cumprod(x)


def leja(a):
    """
    Leja ordering of given numbers:

    * |a[0]| = max_j |a[j]|
    * prod_{i=0}^{k-1} |a[k] - a[i]| = max_j prod_{i=0}^{k-1} |a[j] - a[i]|

    When used as a preprocessing for np.poly it increases its numerical precision.
    """
    n = len(a)
    c = np.argmax(np.abs(a))
    a[[c, 0]] = a[[0, c]]
    for k in range(1, n):
        A = np.abs(a[:, np.newaxis][:, [0] * k] - a[np.newaxis, :k][[0] * n, :])
        A = np.prod(A, -1)
        c = np.argmax(A)
        a[[k, c]] = a[[c, k]]
    return a


def sfact(h, min_phase=False, eps=1e-5):
    """
    Return a mid-phase (or min-phase) spectral factorization of the polynomial h of degree 2n; i.e., a polynomial g of degree n such that

      h(X) = X^n g(X) g(1/X)

    The min_phase parameter is ignored if h is a complex signal.
    This code is inspired by Selesnick's sfactM.m and sfact.m.
    """
    assert len(h) % 2 == 1, "Polynomial should have even degree."
    h = np.array(h)
    assert np.isclose(
        np.linalg.norm(h - h[::-1]) / np.linalg.norm(h), 0
    ), "Coefficient sequence should be symmetric."
    isreal = np.all(np.isreal(h))

    # find roots of original polynomials
    roots = np.roots(h)

    # classify roots on unit circle
    roots_circ = roots[np.abs(np.abs(roots) - 1) < eps]
    if min_phase and len(roots_circ) > 0:
        raise NotImplementedError

    plus_one = np.abs(roots_circ - 1) < eps
    minus_one = np.abs(roots_circ + 1) < eps
    others = ~(plus_one | minus_one)
    pos_angle = (np.angle(roots_circ) > 0) & others
    neg_angle = (np.angle(roots_circ) < 0) & others

    num_plus_one = sum(plus_one)
    num_minus_one = sum(minus_one)
    num_pos_angle = sum(pos_angle)
    num_neg_angle = sum(neg_angle)
    assert num_plus_one % 2 == 0, "The root +1 should appear an even number of times."
    assert num_minus_one % 2 == 0, "The root -1 should appear an even number of times."
    assert (
        num_pos_angle == num_neg_angle
    ), "Should have as many eigenvalues e^{i phi} as e^{-i phi}."
    assert num_plus_one + num_minus_one + num_pos_angle + num_neg_angle == len(
        roots_circ
    )

    # collect half the +1's, half the -1's, and the intersperse positive with negative ones (to increase numerical stability)
    roots_pos_angle = roots_circ[pos_angle]
    roots_circ = np.r_[
        roots_pos_angle[::2],
        1 / roots_pos_angle[1::2],
        [+1] * (num_plus_one // 2),
        [-1] * (num_minus_one // 2),
    ]

    # roots inside unit disk
    roots_int = roots[np.abs(roots) <= 1 - eps]
    if isreal and not min_phase:
        pos_imags, reals = scipy.signal.filter_design._cplxreal(roots_int)
        A1 = np.r_[pos_imags[::2], pos_imags[::2].conj()]
        A2 = np.r_[pos_imags[1::2], pos_imags[1::2].conj()]
        imags = np.r_[1 / A1, A2]
        reals = np.r_[1 / reals[::2], reals[1::2]]
        roots_int = np.r_[imags, reals]

    # roots of the spectral factorization
    roots = np.r_[roots_circ, roots_int]
    roots = leja(roots)

    # build corresponding polynomial
    g = np.poly(roots)
    # if isreal:
    #     g = np.real(g)
    g = g * np.sqrt(h[-1] / (g[0] * g[-1]))
    if min(g) + max(g) < 0:
        g = -g

    # check that g is indeed a spectral factor of h
    assert signal(h).isclose(signal(np.convolve(g, g[::-1])))
    return g


def selesnick_hwlet(K, L, min_phase=False):
    """
    Return Selesnick's Hilbert transform wavelet pair (h, g).

    The parameter K determines the number of zeros at z=-1.
    The parameter L determines the support of the filter implementing the fractional delay.

    The length of both scaling filters is 2(K+L).
    This code is inspired by Selesnick's hwlet.m.
    """
    d = allpass(1 / 2, L)

    # filter for z^(K+L) S(z)
    s1 = scipy.special.binom(2 * K, np.arange(2 * K + 1))
    s2 = np.convolve(d, d[::-1])
    s = np.convolve(s1, s2)

    # solve convolution system for z^(K+L-1) R(z)
    A = convmtx(s, 2 * (K + L) - 1)
    A = A[1::2]
    b = np.zeros(2 * (K + L) - 1)
    b[K + L - 1] = 1
    r = np.linalg.solve(A, b)
    r = (r + r[::-1]) / 2
    assert np.allclose(A @ r, b)

    # find spectral factor Q(z) and compute filter for z^K F(z)
    q = sfact(r, min_phase=min_phase)
    b = scipy.special.binom(K, np.arange(K + 1))
    f = np.convolve(q, b)
    h = np.convolve(f, d)
    g = np.convolve(f, d[::-1])

    # build orthogonal wavelet
    h = orthogonal_wavelet.from_scaling_filter(signal(h))
    g = orthogonal_wavelet.from_scaling_filter(signal(g))
    return h, g


def evenbly_white_hwlet():
    """
    Return Evenbly-White's filter pair of length 4.
    """
    h_s = signal(
        np.array([-0.129_409_52, 0.224_143_87, 0.836_516_3, 0.482_962_91]), start=-2
    )
    g_s = signal(
        np.array([0.482_962_91, 0.836_516_3, 0.224_143_87, -0.129_409_52]), start=0
    )
    h = orthogonal_wavelet.from_scaling_filter(h_s)
    g = orthogonal_wavelet.from_scaling_filter(g_s)
    return h, g
