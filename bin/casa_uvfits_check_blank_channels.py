#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil, pprint
import numpy as np
import astropy
from astropy.io import fits
try:
    import casacore # pip install python-casacore # documentation: http://casacore.github.io/python-casacore/
except:
    raise ImportError('Could not import casacore! Please install it via \'pip install python-casacore!\'')

from casacore.tables import table, taql








# 
# def check_blank_channels()
# 
def check_blank_channels(input_uvfits, check_zero = True):
    hdulist = fits.open(input_uvfits)
    if len(hdulist) > 0:
        hdu = hdulist[0]
        if type(hdu) is fits.hdu.groups.GroupsHDU:
            # print data shape, should have just one dimension, each element is a Group object
            #print(hdu.data.shape)
            # 
            # print all Group par names
            #print(hdu.data.parnames)
            # 
            # index one Group par value of a data
            #hdu.data.par('parname')[irow]
            #hdu.data[irow].par('parname')
            # 
            # index one Group data and its one par value, the shape of one Group data should be (1, 1, 1, nchan, nstokes, 3), 3 is the complex number (re,im,wt)
            #print(hdu.data[99].data.shape)
            #print(hdu.data[99].par('UU'))
            # 
            # select data array
            #data_per_chan = [t.data[:,:,:,0,:,:] for t in hdu.data]
            #data_per_chan = [t.data[0,0,0,0,:,:] for t in hdu.data]
            #for t in hdu.data:
            #    print(t.data[0,0,0,0,:,:].shape)
            #    break
            #print(hdu.data[:].data[0,0,0,0,:,:].shape)
            # 
            # select data array in a better way
            data_array = hdu.data[:].data[0,0,0,0,:,:,0] + 1j * hdu.data[:].data[0,0,0,0,:,:,1]
            # 
            # merge stokes
            data_array_stokesI = np.mean(data_array, axis=1)
            # 
            # compute the absolute of complex numbers
            data_array_abs = np.absolute(data_array_stokesI)
            # 
            # check which are blank channels
            mask_blank_channels = np.logical_or( \
                                        np.isnan(data_array_abs) , 
                                        np.isinf(data_array_abs) 
                                    )
            if check_zero == True:
                mask_blank_channels = np.logical_or( \
                                            mask_blank_channels, 
                                            np.abs(data_array_abs) < 1e-30
                                        ) # np.isclose checks "absolute(a - b) <= (atol + rtol * absolute(b))"
            return mask_blank_channels
        # 
    # 
    return []








# 
# def usage()
# 
def usage():
    print('Usage:')
    print('    %s "Your_input_uvfits.uvfits"'%(os.path.dirname(__file__) ) )






# 
# main
# 
if __name__ == '__main__':
    
    # 
    # read user input
    input_uvfits = ''
    i = 1
    while i < len(sys.argv):
        if input_uvfits == '':
            input_uvfits = sys.argv[i]
        i += 1
    
    # 
    # check user input
    if input_uvfits == '':
        usage()
        sys.exit()
    
    # 
    # print message
    print('input_uvfits = %s'%(input_uvfits))
    
    # 
    # check file existence
    if not os.path.isfile(input_uvfits):
        print('Error! The input uvfits "%s" was not found!'%(input_uvfits))
        sys.exit()
    
    # 
    # run
    mask_blank_channels = check_blank_channels(input_uvfits)
    
    # 
    # print
    if np.count_nonzero(mask_blank_channels) > 0:
        print('Found %d blank channels (with channel number 1-based): '%(len(mask_blank_channels)))
        for i in range(len(mask_blank_channels)):
            if mask_blank_channels[i] == True:
                print('    %d'%(i+1))
    else:
        print('No blank channel found!')
























