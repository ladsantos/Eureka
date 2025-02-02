# NIRSpec specific rountines go here
import os
import numpy as np
from astropy.io import fits
from . import nircam

def read(filename, data, meta):
    '''Reads single FITS file from JWST's NIRCam instrument.

    Parameters
    ----------
    filename:   str
        Single filename to read
    data:   DataClass
        The data object in which the fits data will stored
    meta:   MetaClass
        The metadata object

    Returns
    -------
    data: DataClass
        The updated data object with the fits data stored inside

    Notes
    -----
    History:

    - November 2012 Kevin Stevenson
        Initial version
    - June 2021 Aarynn Carter/Eva-Maria Ahrer
        Updated for NIRSpec
    '''

    assert isinstance(filename, str)

    # Now we can start working with the data.
    hdulist 		= fits.open(filename)
    data.filename = filename
    data.mhdr 		= hdulist[0].header
    data.shdr 		= hdulist['SCI',1].header

    data.intstart 	= 1

    try:
        data.intstart = data.mhdr['INTSTART']
        data.intend   = data.mhdr['INTEND']
    except:
        print('  WARNING: Manually setting INTSTART to 1 and INTEND to NINTS')
        data.intstart  = 1
        data.intend    = data.mhdr['NINTS']

    data.data 		= hdulist['SCI',1].data
    data.err 		= hdulist['ERR',1].data
    data.dq 		= hdulist['DQ',1].data
    data.wave 		= hdulist['WAVELENGTH',1].data
    data.v0 		= hdulist['VAR_RNOISE',1].data
    int_times	    = hdulist['INT_TIMES',1].data[data.intstart-1:data.intend]

    # Record integration mid-times in BJD_TDB
    # data.time = int_times['int_mid_BJD_TDB']
    # meta.time_units = 'BJD_TDB'
    # There is no time information in the simulated NIRSpec data
    print('  WARNING: The timestamps for the simulated NIRSpec data are currently '
          'hardcoded because they are not in the .fits files themselves')
    data.time = np.linspace(data.mhdr['EXPSTART'], data.mhdr['EXPEND'], data.intend)
    meta.time_units = 'BJD_TDB'

    # NIRSpec CV3 data has a lot of NaNs in the data and err arrays, which is making life difficult.
    print('  WARNING: Manually changing NaNs from DATA and ERR arrays to 0 for the CV3 data')
    data.err[np.where(np.isnan(data.err))] = np.inf
    data.data[np.where(np.isnan(data.data))] = 0

    return data, meta


def flag_bg(data, meta):
    '''Outlier rejection of sky background along time axis.

    Uses the code written for NIRCam and untested for NIRSpec, but likely to still work

    Parameters
    ----------
    data:   DataClass
        The data object in which the fits data will stored
    meta:   MetaClass
        The metadata object

    Returns
    -------
    data:   DataClass
        The updated data object with outlier background pixels flagged.
    '''
    return nircam.flag_bg(data, meta)


def fit_bg(data, meta, n, isplots=False):
    '''Fit for a non-uniform background.

    Uses the code written for NIRCam and untested for NIRSpec, but likely to still work
    '''
    return nircam.fit_bg(data, meta, n, isplots=isplots)
