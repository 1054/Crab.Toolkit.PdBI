#!/usr/bin/env python
# 
from __future__ import print_function
import os, sys, re
import astropy
from astropy.io import fits
from astropy import wcs





if __name__ == '__main__':

    if len(sys.argv) <= 4:
        print('Usage: %s Input_fits_cube.fits X Y Z'%(os.path.basename(__file__)))
        sys.exit()
    
    input_sci_file = sys.argv[1]
    input_pos_X = float(sys.argv[2])
    input_pos_Y = float(sys.argv[3])
    input_pos_Z = float(sys.argv[4])
    
    sci_hdulist = fits.open(input_sci_file)
    sci_fits_data = sci_hdulist[0].data
    sci_fits_header = sci_hdulist[0].header
    
    cube_wcs = wcs.WCS(sci_fits_header, naxis=3)
    converted_coord = cube_wcs.wcs_pix2world([(input_pos_X, input_pos_Y, input_pos_Z)], 1)[0]
    print(converted_coord[0], converted_coord[1], converted_coord[2])




