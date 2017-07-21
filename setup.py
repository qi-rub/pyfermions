import ast, re, io, os.path
from setuptools import setup

# determine version (adapted from mitsuhiko)
VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')
with open('pyfermions/__init__.py', 'rb') as f:
    version = VERSION_RE.search(f.read().decode('utf-8')).group(1)
    version = str(ast.literal_eval(version))

# read long description and convert to RST
long_description = io.open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md'),
    encoding='utf-8').read()
try:
    import pypandoc
    long_description = pypandoc.convert(long_description, 'rst', format='md')
except ImportError:
    pass

setup(
    name='pyfermions',
    version=version,
    description=
    'Rigorous free fermion entanglement renormalization from wavelet theory',
    long_description=long_description,
    maintainer='Michael Walter',
    maintainer_email='michael.walter@stanford.edu',
    url='https://github.com/catch22/pyfermions',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research'
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    packages=['pyfermions'],
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
    ],
    extras_require={
        'dev': [
            'pypandoc',
            'pytest',
            'wheel',
        ],
    })
