import numpy as np
from .utils import *

__all__ = ['signal']


class signal:
    """A discrete signal self[n] with finite support."""

    def __init__(self, data=None, start=0):
        #: First index where signal is defined.
        self.start = start

        #: Signal data.
        self.data = np.array(data if data is not None else [])

    @property
    def stop(self):
        """Index after last index where the signal is defined."""
        return self.start + len(self.data)

    @property
    def range(self):
        """Indices where the signal is defined (and hence potentially nonzero)."""
        return np.arange(self.start, self.stop)

    def __getitem__(self, n):
        """Return element self[n]."""
        if self.start <= n < self.stop:
            return self.data[n - self.start]
        return 0

    def __repr__(self):
        return 'signal(%r, start=%d)' % (self.data, self.start)

    def __array__(self):
        """Convert to numpy array."""
        return np.array(self.data)

    def to_pandas(self):
        from pandas import Series
        return Series(data=self.data, index=self.range)

    def conj(self):
        """Return complex conjugate of signal."""
        return signal(self.data.conj(), self.start)

    def norm(self):
        """Return l^2 norm of signal."""
        return np.linalg.norm(self.data)

    def isclose(self, other, **kwargs):
        """Determine whether signals are close. All keyword arguments are forwarded to numpy.allclose."""
        start, stop, a, b = self._union_align(other)
        return np.allclose(a, b, **kwargs)

    def __add__(self, other):
        """Add two signals."""
        start, stop, a, b = self._union_align(other)
        return signal(a + b, start)

    def __sub__(self, other):
        """Subtract two symbols."""
        start, stop, a, b = self._union_align(other)
        return signal(a - b, start)

    def __mul__(self, other):
        """Scalar multiplication."""
        assert np.isscalar(other)
        return signal(self.data * other, self.start)

    def __rmul__(self, other):
        """Scalar multiplication."""
        assert np.isscalar(other)
        return signal(other * self.data, self.start)

    def __truediv__(self, other):
        """Scalar division."""
        assert np.isscalar(other)
        return signal(self.data / other, self.start)

    def __neg__(self):
        """Unary negation."""
        return signal(-self.data, self.start)

    def vdot(self, other):
        """Hermitian dot product (anti-linear in first argument)."""
        start, stop, a, b = self._intersect_align(other)
        if stop <= start:
            return 0
        return np.vdot(a, b)

    def shift(self, k):
        """Return signal shifted to the right (i.e., s.start = self.start + k)."""
        return signal(self.data, self.start + k)

    def modulate(self, z):
        """Return modulated signal s[n] = self[n] * z^n (z should be complex if n can be negative)."""
        data = np.multiply(self.data, z**np.array(self.range))
        return signal(data, self.start)

    def reverse(self):
        """Return reversed signal s[n] = self[-n]."""
        return signal(self.data[::-1], -self.start - len(self.data) + 1)

    def downsample(self, repeat=1):
        """Return downsampled signal s[n] = self[2n]."""
        start = self.start
        data = self.data
        for _ in range(repeat):
            data = data[start % 2::2]
            start = (start + 1) // 2
        return signal(data, start)

    def upsample(self):
        """Return upsampled signal, s[2n] = self[n]."""
        if self.data.size == 0:
            return signal()
        start = self.start * 2
        data = np.zeros(2 * self.data.size - 1, dtype=self.data.dtype)
        data[::2] = self.data
        return signal(data, start)

    def convolve(self, other):
        """Return convolution of self and other."""
        if self.data.size == 0 or other.data.size == 0:
            return signal()
        data = np.convolve(self.data, other.data)
        start = self.start + other.start
        return signal(data, start)

    def ft(self, omega):
        """Return periodic Fourier transform (see utils.dtft)."""
        return dtft(self.range, self.data, omega)

    def _intersect_align(self, other):
        start = max(self.start, other.start)
        stop = min(self.stop, other.stop)

        # truncate
        a = self.data[start - self.start:stop - self.start]
        b = other.data[start - other.start:stop - other.start]
        return start, stop, a, b

    def _union_align(self, other):
        start = min(self.start, other.start)
        stop = max(self.stop, other.stop)

        # pad by zeros
        a = np.zeros(stop - start, dtype=self.data.dtype)
        b = np.zeros(stop - start, dtype=other.data.dtype)
        a[self.start - start:self.stop - start] = self.data
        b[other.start - start:other.stop - start] = other.data

        return start, stop, a, b
