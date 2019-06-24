#!/usr/bin/env python
'''
An example module that contains a class for reading and plotting a simple
solar wind ASCII file.

To use, import in the usual manner:
>>>import example_imf

Alternatively, this can be run as a script.  To do this, simply call it
from the command line with the help option:
$ example_imf.py -h

This file was originally created for the GEM/CEDAR Joint Workshop 2016.
It has been lightly updated for the GEM Workshop 2019

DTW - dwelling@uta.edu
'''

# top level imports are available to all functions/classes
# declared below:
import numpy as np

# Make a function that customizes an axes object:
def format_ax(ax, ylabel=None):
    '''
    Format an axes object, *ax*, to quickly add labels, change time ticks to
    sensible values, turn off xtick labels unless we're on the bottom
    row of plots, and set the y-axis label to kwarg *ylabel*
    
    Example usage: format_ax(axis, ylabel='some label string')
    '''

    import matplotlib.dates as mdt
    
    # Better tick spacing.  Let's put a major tick every 6 hours, a minor
    # tick every hour, and label the ticks by HH:MM UT.  Use locator
    # objects (special objects that find where to put ticks) to set tick
    # locations.  Use formatter objects to set the format of the tick
    # labels.  This looks pedantic, but is very, very powerful.
    Mtick=mdt.HourLocator(byhour=[0,6,12,18])
    mtick=mdt.HourLocator(byhour=range(24))
    fmt = mdt.DateFormatter('%H:%M UT')

    # Apply those to our axes.  Note that the axes objects contain
    # axis objects for the x axis and y axis.  We can edit single
    # axes so they look different!
    ax.xaxis.set_major_locator(Mtick)
    ax.xaxis.set_minor_locator(mtick)
    ax.xaxis.set_major_formatter(fmt)

    # Turn on the grid:
    ax.grid()
    
    # Set ylabel, if set:
    if ylabel: ax.set_ylabel(ylabel, size=16)

    # Kill some labels.  Get the list of label objects and turn some off.
    labels =ax.get_yticklabels()   # Get the labels...
    labels[-1].set_visible(False)  # Turn off the first.
    labels[0].set_visible(False)   # Turn off the 2nd.

    # Determine the axes' geometry.  Use this to determine if we're in the
    # bottom row of plots.  The geometry is returned as (nrows, ncols, iplot).
    geom = ax.get_geometry()
    # We're in the bottom row if the number of the current plot we're on is
    # greater than the number of plots in all rows above the last.
    is_bottom = geom[-1] > (geom[0]-1)*geom[1]
    
    # If we're in the bottom row, label the axes with the date and time.
    if is_bottom:
        # Get time limits, as floating point numbers,  from our axes object:
        tStart, tEnd = ax.get_xlim() # returns range of x-axes.
        # Convert tStart into a datetime:
        tStart = mdt.num2date(tStart)
        # Note how Datetime objects have methods to pretty-print the time!
        ax.set_xlabel( 'Time from {}'.format(tStart.isoformat()), size=18 )
    else:
        # No labels on any axis except the bottom plot.  Set the list of
        # labels to an empty list for no labels (but keep ticks!)
        ax.xaxis.set_ticklabels([])

# This is our class definition for handling our IMF files.
# In our definition, we declare that ImfData inherits from subclass *dict*,
# or a default Python dictionary.  This makes our object behave like
# a dictionary right out of the gate.
class ImfData(dict):
    '''
    A class for handling Imf data in SWMF ascii format.  To instantiate, 
    simply use,
    
    >>>imf = ImfData('some/file/here.txt')

    ...where 'some/file/here.txt' is an ASCII formated IMF input file for
    the SWMF.  Follow this link for more info on the data format:
    http://herot.engin.umich.edu/~gtoth/SWMF/doc/HTML/SWMF/node301.html

    The data values are accessed using dictionary syntax:

    >>>imf['bx']
    >>>print(imf.keys())

    This class' parent is **dict**, so it behaves as a specialized
    dictionary.

    '''

    # Double-underscore methods are special methods that control
    # object behavior, such as how it is printed, how it is
    # instatiated, etc.  Let's define these for our object.
    
    # Define the __init__ method, which sets how the object is made:
    def __init__(self, filename):
        # Call initialization method of parent class.  This causes the
        # object to be built just like a dictionary...
        super(ImfData, self).__init__(self)

        # A really important concept is "self".  When we create an object
        # from a class, it is assigned a variable name.  However, when we
        # define the class, we don't know a priori what the object's assigned
        # name will be.  Therefore, we access the yet-to-be-instatiated
        # object via "self".
        
        # ...but we'll customize how it is made:
        # Store file name as an object attribute
        self.file = filename

        # Load the data into self:
        self._read_data()

        # Good to return "None".
        return None
        
    def __str__(self):
        '''
        Set the string representation of the object, i.e., what is displayed
        if you type print(self).
        '''
        return 'ImfData object of {}'.format(self.file)

    def __repr__(self):
        '''
        This sets how the object is displayed to screen when Python tries to
        show you information about the object.  Let's default to the __str__
        result.
        '''
        return self.__str__()

    def calc_b(self):
        '''
        Calculate the magnitude of the magnetic field.  Store as self['b'].
        '''
        # Import numpy's square root function.
        from numpy import sqrt
        # Calculate and store the total field magnitude.
        self['b'] = sqrt(self['bx']**2 + self['by']**2 +self['bz']**2)

    def calc_v(self):
        '''
        Calculate the magnitude of the velocity vector.  Store as self['v'].
        '''
        # Import numpy's square root function.
        from numpy import sqrt
        # Calculate and store the total field magnitude.
        self['v'] = sqrt(self['vx']**2 + self['vy']**2 +self['vz']**2)

    def calc_clock(self):
        '''
        Calculate IMF clock angle, arctan(By/Bz).
        Theta=0 is purely northward IMF, 180 is southward.
        '''
        self['clock'] = np.arctan2(self['by'],self['bz'])
        
    def calc_epsilon(self):
        '''
        Calculate the epsilon parameter representing the power input into 
        the magnetosphere.  See Perreault, P., and S.-I. Akasofu (1978), 
        A study of geomagnetic storms, Geophys. J. R. Astron. Soc., 54, 547.
        '''
        # Ensure prequisite variables are calculated:
        if 'b' not in self: self.calc_b()
        if 'v' not in self: self.calc_v()
        if 'clock' not in self: self.calc_clock()

        # Calculate epsilon:
        mu_o = 4*np.pi*1E-7

        # Calculate conversion factors:
        conv = 1000. * 1E-9**2 /mu_o # km/s->m/s; nT**2->T**2
        
        self['epsilon'] = conv*self['v']*self['b']**2*np.sin(self['clock']/2)**4

    def _read_data(self):
        '''
        Load data from self.file to self. 
        '''
        
        # This method reads the data from the ASCII file and loads it into
        # the object. 
        
        import numpy as np
        import datetime as dt
        
        # Check our arguments, raise exceptions if something is wrong.
        # This check ensures that the file name is a string:
        if type(self.file) != type('str'):
            raise(TypeError('Input file name must be a string.'))

        # Open the file in read-only mode by creating a file object.
        f = open(self.file, 'r')

        # Read the very first line. Just like IDL, Python will remember our 
        # position in the file so that no lines are read twice.
        line=f.readline()
    
        # These files have a lot of header information.  We want to skip that.
        # We know, a priori, that the data begins after the "#START" text.  
        # Let's loop through the first lines until we hit that line.
        # When comparing two strings, we want to cut off leading and trailing
        # blanks.  We do that with the "strip" object method.
        while line.strip() != '#START':
            line=f.readline()
        
        # At this point, we should be at the line where the data starts.
        # We can load the rest of the lines by using the "readlines()" (note the
        # s) to slurp all remaining lines.  Slurp is a term that means "read the
        # whole damn file."  'lines' is now a list of lines from the file.
        lines=f.readlines()

        # We're now down with this file, so close it.
        f.close()
    
        # How many lines do we have?  The "len()" function will tell us! 
        nLines = len(lines)

        # Define variable names.  In this example, the variable names and
        # order are given as already known.
        keys=['bx','by','bz', 'vx','vy','vz', 'rho', 'temp']

        # Now, we want to create empty Numpy arrays of the correct size.
        # We use the "zeros" function from the numpy module.  For time,
        # we'll be using datetime objects.  Learn about them!
        # https://docs.python.org/2/library/datetime.html
        # Create a numpy array that can hold datetime objects:
        self['time']=np.zeros(nLines, dtype='object')

        # Now make numpy arrays for all other variables:
        for k in keys:
            self[k]=np.zeros(nLines) # a vector of floats!
            
        # Now, to parse.  This is just a matter of splitting the line into
        # parts, turning them into floats or ints.  Special care must be taken
        # with time because we want datetime objects (Python's special time
        # variables.) Start by looping through all lines:
        for i, l in enumerate(lines):
            # Split up the line into parts by spaces:
            parts=l.split()
            
            # Extract time.  We know that the first six parts of the line
            # refer to time, but they can be split by tabs or an arbitrary
            # number of white spaces.  Let's stitch it back together so that
            # we know exactly what it will look like using the "join" method
            # on a string that is a single space:
            tNow = ' '.join(parts[:6])
            # Now use the tNow string to create a new datetime object.
            # The format codes used below are described here:
            # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
            self['time'][i]=dt.datetime.strptime(tNow, '%Y %m %d %H %M %S')
            
            # Extract remaining data.  To do so quickly, loop over both
            # the data names and the values in the line from the file at once:
            for k, p in zip(keys, parts[7:]):
                self[k][i]=p
            # With a little dictionary magic and loop fun, we did the entire 
            # variable group in two lines.  Play with the syntax to figure out
            # how this works (left as an excercise for the reader.)

    def plot_imf(self, outname=None):
        '''
        Plot the IMF information in *self* to screen.
        If kwarg *outname* is given, plot is saved to file using *outname* as 
        the output file name.
        '''
        
        # Start by importing.
        import matplotlib.pyplot as plt  # our base plotting package.

        # Create a figure object.  This will hold all of our axes objects.  
        # Think of this as the paper on which we write.
        # Use *figsize* to set the size in inches (metric is possible, too.)
        fig = plt.figure(figsize=(8.5,11))

        # "subplots_adjust" sets figure spacing.  Use the interactive plot
        # window to find your best spacing values, then paste 'em here!
        fig.subplots_adjust(hspace=0.001, right=0.96, top=0.93, left=0.13, 
                            bottom=0.07)

        # Add subplots to the figure object.  Use a three-digit code to specify
        # the number of rows, columns, and finally which position to use.
        # Each Axes is an object that we save as a variable.
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(413)
        ax3 = plt.subplot(414)

        # Put the title on the top axis. 
        ax1.set_title(self.file)

        # TOP AXES: IMF
        # Create the IMF By, Bz plot.  Note how we call the object methods
        # that belong to the axes we want to edit.  "label" sets the legend
        # label.  There are MANY kwargs that customize plots!
        ax1.plot(self['time'], self['by'], 'c--', label='$B_{Y}$')
        ax1.plot(self['time'], self['bz'], 'b', label='$B_{Z}$')
        
        # Create a legend: The legend command is very flexible, check out the
        # docstring to see how it works.
        ax1.legend(loc='upper right', ncol=2)
        
        # Horizontal lines:  Must specify the y, xStart and xEnd.  lw is width.
        ax1.hlines(0, self['time'][0], self['time'][-1], colors='k', 
                   linestyles='dashed', lw=2.0)

        # Call our format function to cleanup and label our axes.
        format_ax(ax1, 'IMF ($nT$)')
        
        # MIDDLE AXES: NUMBER DENSITY
        ax2.plot(self['time'], self['rho'], 'r-')
        format_ax(ax2, r'$\rho$ ($cm^{-3}$)')
        
        # BOTTOM AXES: VELOCITY
        ax3.plot(self['time'], -1*self['vx'], 'g-')
        format_ax(ax3, r'$V_{X}$ ($\frac{km}{s}$)')
        
        # Finally, either save or show the plot.
        if(outname):
            fig.savefig(outname)
        else:
            plt.show()
        
if __name__ == '__main__':
    # This line checks the current namespace.  If this file is loaded
    # as a module, the following code suite will not run.  However, if
    # run as a script, this code suite will run.  Therefore, these
    # sections are useful to get extra utility out of your file.

    # As an example, let's make this file run as a stand-alone script.
    # Alternatively, we could dedicate this section to testing the
    # functionality of this module.  Read about the unittest module:
    # http://docs.python-guide.org/en/latest/writing/tests/

    import argparse
    import matplotlib.pyplot as plt

    # To parse our argument list, let's use the argparse module.
    # See the documentation on argparse to see how to use it:
    # https://docs.python.org/2/howto/argparse.html
    parser = argparse.ArgumentParser(description = 'Open and create a ' +
                                     'quick-look plot of an IMF file.  Plot '+
                                     'will be saved as a PNG file.')
    parser.add_argument('file', help='Path of file to open and plot')

    args = parser.parse_args()

    # From our input file name, create an output file name with
    # the '.png' suffix.
    name_parts = args.file.split('.') # break up into parts by '.'.
    savename = '.'.join(name_parts[:-1]+['png']) # build new file name.
    
    # Now, use our argument and our defined class to quickly plot.
    imf = ImfData(args.file)
    imf.plot_imf(savename)
