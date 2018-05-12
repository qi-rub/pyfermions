import numpy as np
import scipy.fftpack

__all__ = ['convmtx', 'ctft', 'dtft', 'dtft2d']


def convmtx(h, N):
    """Return convolution matrix for kernel h and input signals of length N."""
    return scipy.linalg.toeplitz(np.r_[h, [0] * (N - 1)], np.zeros(N))


def ctft(x, f, domega=0.01, omega_max=None):
    """
    Approximate Fourier transform of a compactly-supported continuous signal.

    We assume that the samples x[n] are equally spaced.
    """
    dx = x[1] - x[0]
    if omega_max is None:
        # use Nyquist frequency as cut-off
        omega_max = 1 / (2 * dx)
    else:
        # downsample (this is an optimization)
        target_dx = 1 / (2 * omega_max)
        if target_dx >= 2 * dx:
            s = int(target_dx / dx)
            x = x[::s]
            f = f[::s]
            dx = s * dx

    # pad by zeros so that we obtain the desired frequency resolution
    target_size = max(int(1 / (domega * dx) + 1), f.size)
    pad_left = (target_size - f.size) // 2
    pad_right = target_size - f.size - pad_left
    x = np.r_[x[0] + np.arange(-pad_left, 0) * dx, x,
              x[-1] + np.arange(1, pad_right + 1) * dx]
    f = np.r_[np.zeros(pad_left), f, np.zeros(pad_right)]

    # approximate the continuous-time Fourier transform
    omega = np.fft.fftfreq(f.size, dx) * 2 * np.pi
    g = np.fft.fft(f)
    g *= dx * np.exp(-1j * omega * x[0]) / np.sqrt(2 * np.pi)

    # reshuffle so that the omega-coordinates are contiguous
    half = (f.size + 1) // 2
    omega = np.r_[omega[half:], omega[:half]]
    g = np.r_[g[half:], g[:half]]

    mask = (-omega_max <= omega) & (omega <= omega_max)
    return (omega[mask], g[mask])


def dtft(n, s, omega):
    """Periodic Fourier transform of a discrete signal s[n]."""
    return np.sum(
        s[:, np.newaxis] * np.exp(
            -1j * n[:, np.newaxis] * omega[np.newaxis, :]),
        axis=0)


def dtft2d(n, m, s, omega):
    """Periodic 2D Fourier transform of a discrete signal s[n,m]."""
    # sample discrete-time Fourier transform
    f_half = np.sum(
        s[:, :, np.newaxis] * np.exp(-1j * m[np.newaxis, :, np.newaxis] *
                                     omega[np.newaxis, np.newaxis, :]),
        axis=1)
    f = np.sum(
        f_half[:, np.newaxis, :] * np.exp(-1j * n[:, np.newaxis, np.newaxis] *
                                          omega[np.newaxis, :, np.newaxis]),
        axis=0)
    return f
