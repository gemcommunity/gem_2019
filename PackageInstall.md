### Conda
[Conda][7] is the package management system and environment management system for Anaconda. It allows you to run updates and install new packages while keeping track of dependencies so that everything continues to work. It also allows you to create additional Python environments. These environments are isolated copies of Anaconda/Python that allow you to work with specific versions of Python and packages without affecting your base installation.

To install new packages with conda simply:

```
conda install scikit-learn
```

or specific versions

```
conda install scikit-learn=0.20.3
```

or to update:

```
conda update scikit-learn
```

You can find more on package management [here][8] and Python environments [here][9].

### PIP

PIP is another Python package manager. If you are trying to install a package, maybe [IGRF][10], which may not be avialable via Anaconda then you can try installing the package via PIP and the [Python Package Index (PyPI)][11] (a host for software developed and shared by the Python community).

To install packages via pip simply use:

```
pip install package_name
```