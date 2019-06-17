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

## Installing Packages

Python packages can be installed via the package managers Conda or PIP. An brief description of these package managers, core Python packages, and Heliophysics specefic packages can be found [here][12].




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
[12]:https://github.com/kylermurphy/gem_2019/blob/master/PackageInstall.md