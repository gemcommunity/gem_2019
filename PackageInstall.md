## Python Packages

Packages are Python's way of _packaging_ and _distributing_ code for reuse. This includes, for example, packages designed for plotting in Python, working with and manipulating arrays, or downloading and opening data files. In Python packages can be installed via a package manager such as Conda, Anaconda's built in package manager, or PIP. 

If you're using Python for data analysis, or to follow along in the GEM tutorials, then there are a number of basic packages which you should make sure you have installed. These include:

- [Numpy][6], a fundemental package for scientific computing (e.g., arrays)
- [SciPy][7], package for mathematics, science, and engineering (e.g., FFTs)
- [Matplotlib][8], plotting in Python
- [Jupyter and Jupyter Notebook][9], web application for analysis and coding
- [iPython][10], provides an interactive shell for Python

To install these packages you can use any package manager. However, if you have Anaconda or Miniconda installed then it's easiest to use Conda:

```
conda install ipython numpy scipy matplotlib
conda install jupyter notebook
```

In addition to the basic scientific packages, a number of more Heliospheric and Magnetospheric specific packages exist. An excellent resource for these packages is the article by [Burrell et al. (2018)][11] and the [HelioPython][12] website.    

### Conda
[Conda][1] is the package management system and environment management system for Anaconda. It allows you to run updates and install new packages while keeping track of dependencies so that everything continues to work. It also allows you to create additional Python environments. These environments are isolated copies of Anaconda/Python that allow you to work with specific versions of Python and packages without affecting your base installation.

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

and to list the packages you have installed:
```
conda list
```

You can find more on package management [here][2] and Python environments [here][3].

### PIP

Pip is another Python package manager. If you are trying to install a package, maybe [IGRF][4], which may not be available via Anaconda then you can try installing the package via pip and the [Python Package Index (PyPI)][5] (a host for software developed and shared by the Python community).

To install packages via pip simply use:

```
pip install package_name
```

[1]:https://docs.conda.io/en/latest/
[2]:https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html
[3]:https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#
[4]:https://pypi.org/project/igrf12/
[5]:https://pypi.org/
[6]:https://www.numpy.org/
[7]:https://www.scipy.org/
[8]:https://matplotlib.org/
[9]:https://jupyter.org/
[10]:https://ipython.org/
[11]:https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JA025877
[12]:http://heliopython.org
