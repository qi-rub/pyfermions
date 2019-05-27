from .signal import *

__all__ = ["orthogonal_wavelet", "DAUBECHIES_D4"]


class orthogonal_wavelet:
    """Orthogonal wavelet consisting of a scaling (low-pass) filter and a wavelet (high-pass) filter that together form a conjugate mirror filter (CMF) pair."""

    def __init__(self, scaling_filter, wavelet_filter):
        #: Scaling filter (low-pass filter).
        self.scaling_filter = scaling_filter

        #: Wavelet filter (high-pass filter).
        self.wavelet_filter = wavelet_filter

    @staticmethod
    def from_scaling_filter(scaling_filter):
        """Construct orthogonal wavelet from scaling filter."""
        # could also use scipy.signal.qmf() and translate manually
        wavelet_filter = -scaling_filter.conj().modulate(-1.0).shift(-1).reverse()
        return orthogonal_wavelet(scaling_filter, wavelet_filter)

    @staticmethod
    def from_wavelet_filter(wavelet_filter):
        """Construct orthogonal wavelet from wavelet filter."""
        scaling_filter = -wavelet_filter.reverse().shift(1).modulate(-1.0).conj()
        return orthogonal_wavelet(scaling_filter, wavelet_filter)

    def analyze(self, s):
        """Decompose signal into scaling and wavelet coefficients."""
        scaling = s.convolve(self.scaling_filter.reverse()).downsample()
        wavelet = s.convolve(self.wavelet_filter.reverse()).downsample()
        return (scaling, wavelet)

    def reconstruct(self, scaling=None, wavelet=None):
        """Reconstruct signal from scaling and wavelet coefficients."""
        if scaling is None:
            scaling = signal()
        if wavelet is None:
            wavelet = signal()
        return scaling.upsample().convolve(
            self.scaling_filter
        ) + wavelet.upsample().convolve(self.wavelet_filter)

    def scaling_function(self, L):
        """Return scaling function at dyadic approximation 2^{-L}."""
        s = self._casade(L, scaling=signal([1]))
        return s.range * 2 ** -L, s.data * 2 ** (L / 2)

    def wavelet_function(self, L):
        """Return wavelet function at dyadic approximation 2^{-L}."""
        s = self._casade(L, wavelet=signal([1]))
        return s.range * 2 ** -L, s.data * 2 ** (L / 2)

    def _casade(self, L, wavelet=None, scaling=None):
        """Starting from scaling and wavelet coefficients at level L, return output of inverse wavelet transform."""
        # there is some numerical instability in scipy's implementation of the cascade algorithm (as compared to our code
        # below and to Matlab's wavefun); otherwise we could simply use scipy.signal.cascade(self.scaling_filter.data, L)
        s = self.reconstruct(scaling=scaling, wavelet=wavelet)
        for l in range(L - 1):
            s = self.reconstruct(scaling=s)
        return s


DAUBECHIES_D4_SCALING_FILTER = signal(
    [0.482_962_913_145, 0.836_516_303_738, 0.224_143_868_042, -0.129_409_522_551]
)

DAUBECHIES_D4 = orthogonal_wavelet.from_scaling_filter(DAUBECHIES_D4_SCALING_FILTER)
