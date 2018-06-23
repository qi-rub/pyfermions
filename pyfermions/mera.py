import numpy as np
from .utils import *
from .signal import *
from .wavelets import *
from .hilbert import *

__all__ = ["mera1d", "mera2d"]


class mera1d:
    """1D Gaussian MERA for approximate ground state of free-fermion Hamiltonian at half filling."""

    def __init__(self, h, g):
        """The wavelet instances h, g should form an approximate Hilbert pair."""
        self.h, self.g = h, g

    @staticmethod
    def selesnick(K, L):
        return mera1d(*selesnick_hwlet(K, L))

    def eigenmode_pair(self, level, x=0):
        """
        Return approximate (negative-energy) eigenmode pair (a,b) on even/odd sublattices that arise from inserting
        unit signals into the given level of the inverse wavelet transforms (level=1, 2, ...).
        """
        assert level >= 1
        a = self.h.reconstruct(wavelet=signal([1], start=x))
        b = self.g.reconstruct(wavelet=signal([1], start=x))
        for _ in range(level - 1):
            a = self.h.reconstruct(scaling=a)
            b = self.g.reconstruct(scaling=b)
        return a, b

    def eigenmode(self, level, x=0, positive_energy=False):
        """
        Return approximate (negative-energy) eigenmode on original lattice that arises from the given level of the MERA
        (level=1, 2, ...).
        """
        assert level >= 1
        a, b = self.eigenmode_pair(level, x)
        a = a.modulate(-1.).upsample()
        b = b.modulate(-1.).upsample().shift(1)
        if not positive_energy:
            psi = (a + b) / np.sqrt(2)
        else:
            psi = (a - b) / np.sqrt(2)
        return psi

    @staticmethod
    def energy_of_mode(psi):
        """Compute energy of given single-particle mode."""
        return -2 * np.real(psi.vdot(psi.shift(-1)))

    def energy(self, levels):
        """Compute energy of approximate ground state with levels MERA layers."""
        E = []
        for level in range(1, levels + 1):
            psi = self.eigenmode(level)
            E.append(mera1d.energy_of_mode(psi) / 2 ** (level + 1))
        return np.sum(E)

    def correlation(self, dx, levels, x=None):
        """Compute correlation function C(x, x+dx) of approximate ground state with levels MERA layers."""
        if x is None:
            x = np.array([0])

        C = np.zeros(shape=(x.size, dx.size))
        for level in range(1, levels + 1):
            psi = self.eigenmode(level)
            for i, the_x in enumerate(x):
                for j, the_dx in enumerate(dx):
                    the_y = the_x + the_dx
                    C[i, j] += (
                        psi.shift(-the_y)
                        .downsample(level + 1)
                        .vdot(psi.shift(-the_x).downsample(level + 1))
                    )

        return C

    def covariance(self, stop, levels, start=None):
        """Return covariance matrix <a_i^\dagger a_j> of subsystem {start,...,stop-1}."""
        if start is None:
            start = 0
        x = np.arange(start, stop)
        C = np.zeros(shape=(x.size, x.size))
        for level in range(1, levels + 1):
            psi = self.eigenmode(level)
            for i, the_x in enumerate(x):
                for j, the_y in enumerate(x):
                    C[i, j] += (
                        psi.shift(-the_y)
                        .downsample(level + 1)
                        .vdot(psi.shift(-the_x).downsample(level + 1))
                    )
        return C

    def h_scaling(self, level, k):
        """
        Return single-particle scaling Hamiltonian (renormalized Hamiltonian) at given level
        (level = 0 is the original Hamiltonian).
        """
        h_10 = self._h_renormalized(level, k)
        return np.array([[np.zeros_like(k), h_10.conj()], [h_10, np.zeros_like(k)]])

    def e_scaling(self, level, k):
        """
        Return dispersion relation of scaling Hamiltonian (renormalized Hamiltonian) at given level
        (level 0 is the original Hamiltonian).
        """
        return np.abs(self._h_renormalized(level, k))

    def e_wavelet(self, level, k):
        """Return dispersion relation of level-l wavelet Hamiltonian."""
        assert level >= 1
        return np.abs(self._h_renormalized(level, k, wavelet=True))

    def _h_renormalized(self, level, k, wavelet=False):
        """Return [1,0] matrix element of level-l single-particle Hamiltonian in k-space."""
        if level == 0:
            return np.exp(1j * k) - 1

        H = self.h.wavelet_filter.ft if wavelet else self.h.scaling_filter.ft
        G = self.g.wavelet_filter.ft if wavelet else self.g.scaling_filter.ft
        a = G(k / 2).conj() * H(k / 2) * self._h_renormalized(level - 1, k / 2)
        b = (
            G(k / 2 + np.pi).conj()
            * H(k / 2 + np.pi)
            * self._h_renormalized(level - 1, k / 2 + np.pi)
        )
        return (a + b) / 2


class mera2d:
    """2D Gaussian MERA for approximate ground state of free-fermion Hamiltonian at half filling."""

    def __init__(self, h, g):
        """The wavelet instances h, g should form an approximate Hilbert pair."""
        self.mera1d = mera1d(h, g)

    @staticmethod
    def selesnick(K, L):
        return mera2d(*selesnick_hwlet(K, L))

    def eigenmode_pair(self, level_x, level_y, x=0, y=0):
        """
        Return approximate (negative-energy) eigenmode pair (a,b) on even/odd sublattices that arise from inserting
        a unit signal at site (x, y) into the inverse wavelet transforms at the given levels (level_x, level_y = 1, 2, ...).
        """
        assert level_x >= 1 and level_y >= 1
        a_x, b_x = self.mera1d.eigenmode_pair(level_x, x)
        a_y, b_y = self.mera1d.eigenmode_pair(level_y, y)
        assert np.allclose(a_x.range, b_x.range)
        assert np.allclose(a_y.range, b_y.range)

        n = a_x.range
        m = a_y.range
        a = np.outer(a_x.data, a_y.data)
        b = np.outer(b_x.data, b_y.data)
        return n, m, a, b

    @staticmethod
    def energy_of_mode_pair(n, m, a, b):
        """Compute energy of given single-particle mode pair (no need to go to original lattice)."""
        a = a / np.sqrt(2)
        b = b / np.sqrt(2)

        E = (
            np.tensordot(a.conj(), b)
            + np.tensordot(b.conj()[:-1, :-1], a[1:, 1:])
            - np.tensordot(a.conj()[1:, :], b[:-1, :])
            - np.tensordot(b.conj()[:, :-1], a[:, 1:])
        )
        return -2 * np.real(E)

    def energy(self, levels_x, levels_y):
        """Compute energy of approximate ground state with branching MERA truncated at given numbers of layers."""
        E = []
        for level_x in range(1, levels_x + 1):
            for level_y in range(1, levels_y + 1):
                n, m, a, b = self.eigenmode_pair(level_x, level_y)
                e = mera2d.energy_of_mode_pair(n, m, a, b)
                E.append(e / 2 ** (level_x + level_y + 1))
        return np.sum(E)
