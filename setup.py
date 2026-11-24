import re

import setuptools

REPO = 'https://github.com/udayRage/cuPAMI'
RAW = 'https://raw.githubusercontent.com/udayRage/cuPAMI/main'


def pypi_readme(text):
    """Make the README's relative links absolute so they work on PyPI."""
    def absolute(match):
        bang, label, target = match.groups()
        if re.match(r'[a-z]+://|#|mailto:', target):
            return match.group(0)
        base = RAW if bang else f'{REPO}/blob/main'
        return f'{bang}[{label}]({base}/{target})'
    return re.sub(r'(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)\)', absolute, text)


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = pypi_readme(fh.read())

setuptools.setup(
    name='cupami',
    version='2026.11.02',
    author='Rage Uday Kiran',
    author_email='uday.rage@gmail.com',
    description='GPU-accelerated pattern mining with CUDA: frequent, periodic, fuzzy, spatial, and coverage patterns',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(include=['cupami', 'cupami.*']),
    url=REPO,
    license='GPLv3',
    install_requires=[
        'numpy',
        'pandas',
        'psutil',
    ],
    extras_require={
        # CuPy wheels are CUDA-specific; prefer e.g. `pip install cupy-cuda12x`.
        'gpu': ['cupy'],
        'opencl': ['pyopencl>=2024.1'],
        'parquet': ['pyarrow'],
        'plots': ['matplotlib'],
        'dev': ['twine', 'setuptools', 'build'],
        'all': ['cupy', 'pyopencl>=2024.1', 'pyarrow', 'matplotlib'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: GPU :: NVIDIA CUDA',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
