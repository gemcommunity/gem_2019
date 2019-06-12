## Anaconda and Miniconda

Anaconda offers a simplified distribution of Python with everything required for science and research (plotting, reading in data, arrays etc.). It's available on Mac, Linux, and Windows, with very simple installs which are also easy to manage (like when adding new packages), and it's free and open-sourced.

Miniconda is a barebones installation of Anaconda. Though once installed you can update to the full version of Anaconda.


### On Linux and WSL

On Linux, or if you're running Windows Subsystem for Linux (WSL), you can install Anaconda via the command line by downloading the [latest install][5]:

```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh 
bash Miniconda3-latest-Linux-x86_64.sh
conda install -c anaconda anaconda 
```

### On Mac

Anaconda is also easily installed via the command line on Mac:

```
curl https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh > Miniconda3-latest-MacOSX-x86_64.sh 
bash Miniconda3-latest-MacOSX-x86_64.sh
conda install -c anaconda anaconda 
```

### On Windows

If you're not running WSL then installing Anaconda is easiest through the [graphic installer][6]. Simply download the appropriate install and follow the directions. This installs the full version of Anaconda as opposed to lighter Miniconda.

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


[1]:https://github.blog/2018-11-15-state-of-the-octoverse-top-programming-languages/
[2]:https://www.microsoft.com/en-us/p/python-37/9nj46sx7x90p?activetab=pivot:overviewtab 
[3]:https://devblogs.microsoft.com/python/python-in-the-windows-10-may-2019-update/
[4]:https://www.anaconda.com/
[5]:https://repo.continuum.io/
[6]:https://www.anaconda.com/distribution/
[7]:https://docs.conda.io/en/latest/
[8]:https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html
[9]:https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#
[10]:https://pypi.org/project/igrf12/
[11]:https://pypi.org/