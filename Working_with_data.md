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
Assuming we have a good internet conenction, you don't need to do any prep. *_BUT_*, we all know how conference wifi works out. So *if you want to grab the data in advance, just skip down to the "Getting files" section* and make sure you have all the data files. Nothing there is big, so it should all be fairly quick to retrieve.

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
import spacepy.toolbox as tb
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
This is partly because we need files to demonstrate how to work with files, and partly as a basic reference for how to fetch files from the internet. It's fairly straightforward to start doing this programmatically in a workflow.

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

Now let's grab an IDL save set. I've made a simple file that contains two variables for the pruposes of demonstrating this. Unless you downloaded or cloned the whole repository, then we'll have to grab it from the web. For this we'll need to use Python's basic web handling.

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
if not os.path.isfile(ampfn):
    #retrieve from github
    with urllib.request.urlopen(req) as response, open(guvifn, 'wb') as outfile:
        adata = response.read()
        outfile.write(adata)
```

## Working with text

We'll start with regular ASCII, or *_delimiter separated values_*. You've heard of CSV? That's _comma separated values_. If you use whitespace or tabs, for example, then you have DSV. Since this notebook should act as a reference, we'll do several methods. If you're in the room at GEM, we'll just use `numpy` to load the text file.

<!-- #region -->
The file, rather awkwardly, has both ':' and '#' a to mark header lines.
```
:Data_list: Gp_part_5m.txt
:Created: 2019 Jun 17 1816 UTC
# Prepared by the U.S. Dept. of Commerce, NOAA, Space Weather Prediction Center
...
#                 Modified Seconds
# UTC Date  Time   Julian  of the
# YR MO DA  HHMM    Day     Day     P > 1     P > 5     P >10     P >30     P >50     P>100     E>0.8     E>2.0     E>4.0
#-------------------------------------------------------------------------------------------------------------------------
2019 06 17  1615   58651  58500   3.71e+00  3.19e-01  2.78e-01  1.84e-01  1.28e-01  9.04e-02  1.67e+04  6.65e+01 -1.00e+05
```
First, we'll do this a native-Python way, and put our results into a structure that mimics the data model described at the top of the notebook.
<!-- #endregion -->

### Method 1: Plain "hand-rolled" Python

```python
with open('data/goes-particle-flux-primary.txt') as fh:
    # this will read EVERYTHING from the file
    #each row willbe a string
    tempdata = fh.readlines()
tempdata = [line.strip() for line in tempdata]
#strip() #removes line breaks, trailing blanks, etc.

gheader = [line for line in tempdata if line[0] in [':', '#']]
print('Header (start and end only):\n\n{0}\n{1}'.format(gheader[0], gheader[1]))
print('...\n{0}\n{1}\n{2}'.format(gheader[-3], gheader[-2], gheader[-1]))

gbody = [line.split() for line in tempdata if line[0] not in [':', '#']] #breaks each line into parts, splitting on whitespace
gbody = np.asarray(gbody)

#now let's make a dictionary so we can access by variable name, then we'll put arrays inside it...
goesdata = dict()
goesdata['year'] = gbody[:, 0].astype(int)
goesdata['month'] = gbody[:, 1].astype(int)
goesdata['day'] = gbody[:, 2].astype(int)
goesdata['seconds_of_day'] = gbody[:, 5]
goesdata['flux_p'] = gbody[:, 6:12]
goesdata['flux_e'] = gbody[:, 12:]
```

```python
tb.dictree(goesdata, verbose=True)
```

### Method 2: Using numpy's loadtxt

```python
#We'll use numpy's loadtxt function to read the data and ignore the header.
goesdata_np = np.loadtxt('data/goes-particle-flux-primary.txt', comments=['#',':'])

#now inspect the shape of the data, so we know what array dimensions we are working with
print('The GOES data has dimensions {0}'.format(goesdata.shape))

#and we'll inspect the first line, which should be 15 elements long
print('Values in first row:\n {0}'.format(goesdata[0]))
```

So we can either access the array directly whenever we want to use it, or copy the code from above to put it into a dictionary. Or, ...

### Method 3: loadtxt, with a record array

we can specify the data types in advance, and numpy will give us a "record array" that we can access by name. This time we'll just keep the columns we want.

```python
cols = (0, 1, 2, 5, 12, 13, 14) #time info and electron flux data
names = ('year', 'month', 'day', 'seconds_of_day', 'flux_e1', 'flux_e2', 'flux_e3')
datatypes = (np.int, np.int, np.int, np.float, np.float, np.float, np.float)
goesdata_np = np.loadtxt('data/goes-particle-flux-primary.txt', comments=['#',':'],
                         usecols=cols, dtype={'names': names, 'formats': datatypes})
```

```python
print('Values in first row:\n {0} {1} {2} {3} {4} {5} {6}'.format(*[goesdata_np[nn][0] for nn in names]))
```

We can also use SpacePy to convert a record array to a dictionary-like construction. We'll overwrite the old one, just for the convenience of having the same name.

```python
goesdata = dm.fromRecArray(goesdata_np)

print(type(goesdata))
goesdata.tree(verbose=True)
```

This is basically the same as the _hand-rolled_ version above, but now the dictionary-like container carries metadata, as do the arrays. By default, these are empty, but we'll come back to this later.

```python
print('Glabal metadata (should be empty here): {0}'.format(goesdata.attrs))
print('Metadata on "day" (should be empty here): {0}'.format(goesdata['day'].attrs))
```

## Legacy IDL save sets

IDL has a long history in space physics, and the convenience of dumping the variables in an environment to a file has led to data being distributed in IDL's "save set" format. 

Thankfully, you don't need IDL to use an IDL save set any more! `scipy` is a core part of the scientific Python ecosystem, and it has had support for reading IDL save sets for a fairly long time.

_NOTE_: Some IDL data types aren't supported, in my experience. Null pointers, for example. That means that occasionally you'll find an IDL saveset you just can't read with `scipy`. Unfortunately the way around that is to get access to a licensed copy, read the saveset in, then write it back out as a different file type.

```python
idldata = scio.readsav('data/test_idlsav.sav')
print(idldata)
print()
tb.dictree(idldata)
```

<!-- #region -->
You can see that `readsav` generates a dictionary containing arrays for each named variable.


## Working with NetCDF3

There are a lot of different binary formats used for data. Thankfully, the days of proprietary binary data requiring a minimally-documented code from the instrument team (that probably won't compile on your system) are just about over. Similarly, the days of needing a specific commercial software package just to read a file are pretty much over. The free self-describing file formats are more widely supported, and better in almost every way, than the proprietary formats these days.

NetCDF is widely used in Earth and atmospheric sciences, and a lot of Earth-observing data uses it. NetCDF3 is a legacy version that has been superseded by NetCDF4, so we'll just see where the tools are and move on. Again, `scipy` provides the ability to work with NetCDF files:
<!-- #endregion -->

```python
with scio.netcdf.netcdf_file(ampfn) as ampdata:
    print('Opening the file gives us a file-like object: {0}'.format(ampdata))
    print("\nLet's look at what's in it... (just the first 7 variables)")
    print([var for idx, var in enumerate(ampdata.variables) if idx<=6])
    #to access the data we have to copy it from the file to a variable
    ampdata_copy = dict()
    ampdata_copy['nlon'] = ampdata.variables['nlon'][:].copy()

print('\nAnd now we can inspect the data we just read in.\n')
tb.dictree(ampdata_copy, verbose=True)
print("\nampdata_copy['nlon'] = {0}".format(ampdata_copy['nlon']))
```

Since we've extolled the virtues of having metadata, let's access the metadata on 'nlon'. The `with` block above closes the file on exit, so we're going to have to open it again...
I'll just print it here.

```python
with scio.netcdf.netcdf_file(ampfn) as ampdata:
    print(ampdata.variables['nlon'].description)
```

For convenience, SpacePy's datamodel also provides a one-line read from NetCDF3 into SpacePy's data model.

_NOTE_: The main reason you might not want to use these convenience methods is for very large files. If your file won't fit into memory, the convenience of the "_suck all of the data into memory_" approach will obviously fail. Then you'll have to fall back to the more manual methods above.

```python
ampdata_easy = dm.fromNC3(ampfn)

print("\nampdata_easy['nlon'] = {0}".format(ampdata_easy['nlon']))
```
And now all the metadata comes along for the ride, so we can inspect it by just looking at the `attrs` attribute.

```python
print(ampdata_easy['nlon'].attrs)
```

## HDF5, NetCDF4, and Matlab save files

HDF5 is the current generation of the Heirarchical Data Format. It's been around since about 2002, and it's broadly used across the sciences. HDF5 has great parallel support and is widely adopted across high-performance comupting.

So why are NetCDF4 and Matlab save files listed here? Well, NetCDF4 is built on top of HDF5. Since version 7 of Matlab, the default save format (the `.mat` saveset) has used HDF5 under the hood. So, unless the files are using either specific features not supported by Python interfaces to the HDF5 library, then reading NetCDF4 and `.mat` files is as easy as reading HDF5.

The two major libraries that provide HDF5 support are `h5py` and `pytables`. `spacepy` provides convenience routines to read/write in one line through its `datamodel` module. As before, files that won't fit in memory shouldn't try to use the convenience routines.

```python

```

## NASA CDF

And finally, NASA's Common Data Format (CDF). This really hasn't seen much use outside of heliophysics, so tools aimed at a broader community (like `scipy`) don't provide access to CDF.

The Python tools that do are (in order of appearance):
1. spacepy
  - Originally released in 2009, this library has had full CDF support (read, write, etc.) since around 2010. It provides a robust interface to the NASA CDF library.
    - Benefit: When the CDF library updates, as it does regularly, you just install the new one and SpacePy will use it. No waiting for the developers!
    - Benefit: Provides full, robust, well-tested CDF library access.
    - Drawback: You have to install a C library (but NASA's instructions are pretty good).
2. pysatCDF
  - pysatCDF was designed to provide a lightweight, easy-to-install, CDF reader. It was primarily aimed at users of pysat (largely the CEDAR community). The "easy-to-install" part comes from the fact that the CDF library is bundled with it.
    - Benefit: CDF is included, and `pysatCDF` will try to build it for you.
    - Benefit: Syntax for use is modeled on `spacepy`, so the two are fairly interoperable.
    - Drawback: If you need a new version of CDF you have to wait for `pysatCDF` to be updated, then reinstall that.
    - Drawback: Only has read capability, no write capability.
3. cdflib
  - Originally (I believe) written for MAVEN, this is a pure Python version of the CDF library. It's only been around for a couple of years.
    - Benefit: It's just Python. No need to worry about compiling C code, or having someone else compile it. It's just Python.
    - Drawback: Any changes to how CDF works under-the-hood will nned to be implemented in `cdflib` after CDF updates the C library.
    - Drawback: Can only write v3 CDFs

For the sake of interoperability I'll focus on using SpacePy. Reading using `pysatCDF` should work just about the same way as using the `spacepy.pycdf` module. `cdflib` has different syntax.

```python

```
