# pyfermions ![Python 3.5+](https://img.shields.io/badge/python-3.5%2B-brightgreen.svg) [![Build Status](https://travis-ci.org/catch22/pyfermions.svg?branch=master)](https://travis-ci.org/catch22/pyfermions) [![arXiv](http://img.shields.io/badge/arXiv-1707.06243-blue.svg?style=flat)](http://arxiv.org/abs/1707.06243)

A Python package for rigorous free fermion entanglement renormalization from wavelet theory.

[![MERA for 1D free-fermion nearest-neighbor hopping Hamiltonian](docs/mera1d.png)](notebooks/mera1d.ipynb) [![Branching MERA for 2D free-fermion nearest-neighbor hopping Hamiltonian](docs/mera2d.png)](notebooks/mera2d.ipynb)

For details, please see [our paper](http://arxiv.org/abs/1707.06243).

```
@article{latticefermions,
  title={Rigorous free-fermion entanglement renormalization from wavelet theory}
  author={Jutho Haegeman and Brian Swingle and Michael Walter and Jordan Cotler and Glen Evenbly and Volkher B. Scholz},
  journal={Phys. Rev. X},
  year={2018},
  note={in press},
  eprint={1707.06243},
}
```

## Installation

```
pip install git+git://github.com/catch22/pyfermions
```

## Getting Started

Now download and explore some of the [Jupyter notebooks](notebooks).
The [mera1d](notebooks/mera1d.ipynb) notebook is a good starting point.

## Contributing

The contributors are listed [here](CONTRIBUTORS).

```
git clone git://github.com/catch22/pyfermions
cd pyfermions
pip install -e .[dev]
```
