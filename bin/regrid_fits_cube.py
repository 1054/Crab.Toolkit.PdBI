#!/usr/bin/env python
# 

import os, sys, shutil
from spectral_cube import SpectralCube
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales

if len(sys.argv) <= 3:
    print('Usage:')
    print('  regrid_fits_cube.py INPUT_DATA_CUBE.fits INPUT_TEMPLATE_CUBE.fits OUTPUT_DATA_CUBE.fits')
    print('Notes:')
    print('  We will regrid the INPUT_DATA_CUBE according to the world coordinate system (WCS) of the INPUT_TEMPLATE_CUBE, ')
    print('  and save into the OUTPUT_DATA_CUBE. Caution that we will overwrite any existing cube.')
    sys.exit()

input_data_cube_file = sys.argv[1]
input_template_cube_file = sys.argv[2]
output_data_cube_file = sys.argv[3]

if os.path.isfile(output_data_cube_file):
    shutil.move(output_data_cube_file, output_data_cube_file+'.backup')

input_data_cube = SpectralCube.read(input_data_cube_file)
input_data_cube.allow_huge_operations = True

input_template_cube = SpectralCube.read(input_template_cube_file)
input_template_cube.allow_huge_operations = True

output_data_cube = input_data_cube.reproject(input_template_cube.header, order='bicubic')
output_data_array = output_data_cube.unmasked_data[:,:,:]
output_data_array[np.logical_or(np.isnan(output_data_array), np.isclose(0.0))] = 0.0
output_data_cube = SpectralCube(data=output_data_array, wcs=output_data_cube.wcs)

if output_data_cube_file.find(os.sep) >= 0:
    if not os.path.isdir(os.path.dirname(output_data_cube_file)):
        os.makedirs(os.path.dirname(output_data_cube_file))

output_data_cube.write(output_data_cube_file, overwrite=True)



