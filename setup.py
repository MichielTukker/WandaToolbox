from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wandatoolbox",  # Replace with your own username
    version="0.1.0",
    author="Michiel Tukker",
    author_email="Michiel.Tukker@deltares.nl",
    description="Python toolbox for Wanda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichielTukker/WandaToolbox",

    # packages=find_packages(),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=[
        "pywanda>=0.4.6",
        "matplotlib>=3.5.2",
        "pandas>=1.4.3",
        "numpy>=1.23.1"
    ],

    extras_require={
        "dev": [
            "pytest==7.1.2",
            "bump2version==1.0.1",
            "twine>=4.0.1",
        ],
        "doc": [
            "Sphinx==5.0.2",
            "sphinx-rtd-theme==1.0.0",
        ]

    },
    python_requires='>=3.6',
)
