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

In this notebook we'll cover the basics of working with data files in Python, from a space physics user perspective.

Types of data file:
- Plain text (and variants)
- IDL save sets
- NetCDF3
- NetCDF4, HDF5, and Matlab save files
- NASA CDF

## Contents
Here's what the notebook will cover. In the session at GEM we'll scroll through some of this pretty quickly, as the notebook is intended to be a resource.

- Data, metadata, and data models
- Setting up the Python environment
- Getting files
- Working with text
- Legacy IDL save sets
- Working with NetCDF3
- HDF5, NetCDF4, and Matlab save files
- NASA CDF

## Prepping for the session
Assuming we have a good internet conenction, you don't need to do any prep. *_BUT_*, we all know how conference wifi works out. So if you want to grab the data in advance, just skip down to the "Getting files" section and make sure you have all the data files. Nothing there is big, so it should all be fairly quick to retrieve.

<!-- #region -->
## Data, metadata, and data models

We're all familiar with the concpet of data. Whatever our data source, we are almost certainly using numbers to represent a measurement (or simulated measurement). There are a few extra concpets that are helpful to be aware of for talking about data files, some (most? all?) of which will already be familiar to you.

### Metadata

Metadata is _data that describes data_. For example, I asked a coworker for a file containing electron flux data. They sent me a text file with 8 columns of numbers... What are the columns? What units do they have? This information is _metadata_.

An easy way to provide basic metadata is labeling columns, the way you might in a spreadsheet. While that's better than nothing, there's so much more that can be done. What information might we want to store?
- Units for each variable
- Conversion factors (if not in SI units)
- Long-form descriptions of variables
We may also want metadata about the file, not just the variables:
- Who is the instrument PI (or the originator of the data)
- When was the file created?
- What version number is this data?

While some of this can be encoded in short-form headers, and in the file name itself, it can be difficult to know what's in the file without opening it and reading it. Also, while it is possible to represent data with more than two dimensions in text, this leads to design decisions that require custom tools for each specific data product, and metadata may or may not be included in the design.

So a lot of what we'll be dealing with are binary files in _self-describing_ data formats.


### Self-describing file formats and data models

Ideally, the user won't need to know anything about how the data is stored in order to read it. The file should provide all that information in a discoverable way. Similarly, the _global_ metadata for the file should be available, as should the _per variable_ metadata.

Most self-describing file formats are actually both a file format, and a software library that provides an interface to the data files. This means that the user doesn't need to know about how the data are stored, but the user still needs to know which interface to use (NASA CDF? HDF5?). The final thing to know is the data model - this is an abstraction of how the data are stored. Most modern self-describing formats use a data model that's analagous to a file system.

<img src="images/datamodel.png"  width="280">

In this schematic, we have a base folder (like the root directory on a linux-like file system). Attached to the base directory is global metadata. This is basically the README for the whole directory structure. What was the original filename of this self-describing file? What version of the processing code was the file made by?

Then, inside the base directory we can also store data (analagous to files in a directory). Here we have a variable containing the common timebase, as well as two variables containing our data. Each of these variables have local metadata, such as units.

The final entry at the base level is a variable group. This is like a subdirectory that can contain multiple variables all grouped together. It can carry metadata for the group. An example use-case might be for radiation belt electron phase space density. Calculating this requires a magnetic field model. So perhaps we want to group some of our variables by field model (PSD, McIlwain L, B<sub>0</sub> and B<sub>mirror</sub>).

### Back to data formats

This brings us back to the data formats we'll look at today.

NASA CDF, NetCDF, and HDF are all self-describing formats. They all follow a data model similar to the one described above, with various restrictions. These formats are all pretty flexible, so we also need to know what metadata standard the files follow. NASA heliophysics mission all have to use the ISTP standard.
- NASA CDF does not support nested groups
  - There will only ever be one level in NASA CDF files. That is, you open the file, and all of your variables are right there. This can lead to logical groupings being done by varaible name, or by proliferation of files.
  - CDF provides specific `epoch` data types, as the general assumption is that our data will be time-ordered. Most/all CDF tools will automatically convert the epoch to user-friendly dates and times.
- HDF5 is the most widely used self-describing format
  - The description above is basically that of HDF5 `groups` and `datasets`.
  - SpacePy's internal data representation is modeled after the HDF5 data model
  - There's an older version of HDF (HDF4) which isn't compatible with HDF5, but you're unlikely to encounter it in the wild.
- NetCDF4 is built on top of HDF5
  - NetCDF3 can be read using the NetCDF4 library, but *_not_* directly with the HDF5 library.
<!-- #endregion -->

## Setting up the Python environment

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
import urllib.request
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

#And we'll set a variable for the directory with the data files,
#in case you aren't using the github repo, or just want to point
#to a different place.
mydatapath = 'data'
```

## Getting files

If you have grabbed these data files in advance, great! If not, let's get them now...

First, we'll grab a NASA CDF file with THEMIS data from the NASA Space Physics Data Facility. There are sveral ways to do this, but we'll use a basic, generic FTP transfer. Since we already know eaxctly what the file is, and where it is, this method works just fine.

```python
#set the input/output file name
fname = 'thd_l2_gmom_20120115_v01.cdf'
localfname = os.path.join(mydatapath, fname)
if not os.path.isfile(localfname):
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

Now let's grab an IDL save set. This is from the Global UltraViolet Imager (GUVI) on the TIMED satellite. For this we'll need to use Python's basic web handling.

```python
guvifn = os.path.join(mydatapath, 'guvi_aurora_2003_197')
guvi_url = 'http://guvitimed.jhuapl.edu/data/level3/guvi_aurora/data/IDLsave/2003/guvi_aurora_2003_197.sav'

req = urllib.request.Request(guvi_url)
#depending on where you are, web access might go through a proxy server
#in that case you'd want to explicitly set your proxy by uncommenting the next two lines
#proxy = 'proxy.example.edu:1405'
#req.set_proxy(proxy, 'http')
if not os.path.isfile(guvifn):
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(req) as response, open(guvifn, 'wb') as outfile:
        gdata = response.read()
        outfile.write(gdata)
```

The next file is a NetCDF3 file with data from the AMPERE constellation. Since the AMPERE site requires downloaders to have an account, this file is in the GEM\_2019 github repository.

```python
ampfile = '20120109.1300.1200.600.north.grd.ncdf'
ampfn = os.path.join(mydatapath, ampfile)
amp_url = 'https://github.com/gemcommunity/gem_2019/blob/master/data/{0}'.format(ampfile)

req = urllib.request.Request(amp_url)
#do proxy stuff if required
if not os.path.isfile(ampfile):
    #retrieve from github
    with urllib.request.urlopen(req) as response, open(guvifn, 'wb') as outfile:
    adata = response.read()
    outfile.write(adata)
```

## Working with text

We'll start with regular ASCII, or *_delimiter separated values_*. You've heard of CSV? That's _comma separated values_. If you use whitespace or tabs, for example, then you have DSV. Since this notebook should act as a reference, we'll do several methods. If you're in the room at GEM, we'll just use `numpy` to load the text file.

```python

```

IDL has a long history in space physics, and the convenience of dumping the variables in an environement to a file has led to data being distributed in IDL's "save set" format. 

## Legacy IDL save sets

Thankfully, you don't need IDL to use an IDL save set any more! `scipy` is a core part of the scientific Python ecosystem, and it has had support for reading IDL save sets for a fairly long time.

```python
guvi = scio.readsav(guvifn)
```

There are a lot of different binary formats used for data. Thankfully, the days of proprietary binary data requiring a minimally-documented code from the instrument team (that probably won't compile on your system) are just about over.

## Working with NetCDF3

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
