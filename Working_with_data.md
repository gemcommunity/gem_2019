---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.1.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Working with data files in Python

- Plain text
- IDL save sets
- NetCDF3
- NetCDF4, HDF5, and Matlab save files
- NASA CDF

## Data, metadata, and data models

Concepts of metadata, self-describing file formats, and heirarchical data formats.
SpacePy data model. Relate to file systems and arrays.


## Setup

Let's get started by importing all of the modules we'll need. If you've installed the prerequisite packages then you should be able to work with any of these data types.

To stay organized, let's import modules in order:
1. Python standard library
2. Third-party: The _scientific stack_
3. Third-party: Everything else

```python
#standard library
import os
import glob
from ftplib import FTP
#scientific stack
import numpy as np
import scipy.io as scio
from matplotlib import pyplot as plt
#everything else
from spacepy import pycdf
import spacepy.datamodel as dm
import spacepy.plot as splot

#juypter/ipython magic command for inline plotting
%matplotlib inline
```

## Getting files

If you have grabbed these data files in advance, great! If not, let's get them now...

First, we'll grab a NASA CDF file with THEMIS data from the NASA Space Physics Data Facility. There are sveral ways to do this, but we'll use a basic, generic FTP transfer. Since we already know eaxctly what the file is, and where it is, this method works just fine.

```python
#set the input/output file name
fname = os.path.join('data', 'thd_l2_gmom_20120115_v01.cdf')

if not os.path.file(fname):
    #now open a connection to the SPDF FTP server and log in.
    #It's an anonymous FTP server, so we don't need login credentials
    ftp = FTP('spdf.gsfc.nasa.gov')
    ftp.login()
    #change directory to the location of the file we want
    ftp.cwd('pub/data/themis/thd/l2/gmom/2012')
    #now retrieve it and log out
    with open(fname, 'wb') as fh:
        ftp.retrbinary('RETR {0}'.format(fname), fh.write, 1024)
    ftp.quit()
```

The next file is a NetCDF3 file with data from the AMPERE constellation. Since the AMPERE site requires downloaders to have an account, this file is in the GEM\_2019 github repository.

```python
ampfile = os.path.join('data', '20120109.1300.1200.600.north.grd.ncdf')
if not os.path.isfile(ampfile):
    #retrieve from github
```

## Plain Text

We'll start with regular ASCII, or *_delimiter separated values_*. You've heard of CSV? That's _comma separated values_. If you use whitespace or tabs, for example, then you have DSV. Since this notebook should act as a reference, we'll do several methods. If you're in the room at GEM, we'll just use `numpy` to load the text file.


There are a lot of different binary formats used for data. Thankfully, the days of proprietary binary data requiring a minimally-documented code from the instrument team (that probably won't compile on your system) are just about over.

## NetCDF3

NetCDF is widely used in Earth and atmospheric sciences, and a lot of Earth-observing data uses it. It's been superseded by NetCDF4, so we'll just see where the tools are and move on.

```python
ampdata = dm.fromNC3(ampfile)
ampdata.tree(verbose=True, attrs=True)
```



```python
ampdata['colat'][:,-1]
```

## HDF5, NetCDF4, and Matlab save files

HDF5 is the current generation of the Heirarchical Data Format. It's been around since about 2002, and it's broadly used across the sciences. HDF5 has great parallel support and is widely adopted across high-performance comupting.

So why are NetCDF4 and Matlab save files listed here? Well, NetCDF4 is built on top of HDF5. Since version 7 of Matlab, the default save format (the `.mat` saveset) has used HDF5 under the hood. So, unless the files are using either specific features not supported by Python interfaces to the HDF5 library, then reading NetCDF4 and `.mat` files is as easy as reading HDF5.

```python

```
