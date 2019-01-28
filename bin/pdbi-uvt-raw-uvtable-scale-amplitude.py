#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re
import numpy as np
import astropy
from astropy.table import Table
from astropy.io import fits
from copy import copy
import shutil

# 
# read user input
uvt_names = []
out_name = ''
scale_factor = np.nan
iarg = 1
arg_mode = ''
while iarg < len(sys.argv):
    arg_str = sys.argv[iarg].lower().replace('--','-')
    if arg_str == '-name':
        arg_mode = 'name'
        iarg += 1
        continue
    elif arg_str == '-out':
        arg_mode = 'out'
        iarg += 1
        continue
    elif arg_str == '-factor':
        arg_mode = 'factor'
        iarg += 1
        continue
    # 
    if arg_mode == 'name':
        uvt_names.append(re.sub(r'(.*?)\.uvt', r'\1', sys.argv[iarg]))
    if arg_mode == 'out':
        out_name = re.sub(r'(.*?)\.uvt', r'\1', sys.argv[iarg])
    if arg_mode == 'factor':
        scale_factor = np.float(sys.argv[iarg])
        print('scale_factor = %s'%(scale_factor))
    # 
    iarg += 1


# 
# print usage
if len(uvt_names) == 0 or out_name == '' or np.isnan(scale_factor):
    print('Usage: ')
    print('  pdbi-uvt-raw-uvtable-scale-amplitude.py -name uvtable_spw1.uvt -factor 2.0 -out uvtable_spw1_scaled_amplitudes.uvt')
    print('  -- this code will scale the amplitudes of all visibilities in the input uv tables by the input factor.')
    sys.exit()


# 
# loop the input uvtables
for i_uvt in range(len(uvt_names)):
    uvt_name = uvt_names[i_uvt]
    # 
    # convert uvt to uvfits
    if not os.path.isfile(uvt_name+'.uvfits'):
        print('Running: echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
        os.system('echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
    if not os.path.isfile(uvt_name+'.uvfits'):
        print('Error! Failed to call GILDAS/mapping to convert "{0}.uvt" to "{0}.uvfits"!'.format(uvt_name))
        sys.exit()
    # 
    # read uvfits 
    print('Reading '+uvt_name+'.uvfits')
    hdulist = fits.open(uvt_name+'.uvfits')
    if type(hdulist[0]) != fits.GroupsHDU:
        print('Error! The uvfits file "{0}.uvfits" is not fits.GroupsHDU type!'.format(uvt_name))
        sys.exit()
    hdu = hdulist[0]
    #print(hdu.columns)
    # 
    # copy 
    output_hdu = hdu.copy()
    # 
    # deal with header
    #output_hdu.header['BZERO'] = 0.0 # hdu.header['BZERO']
    #output_hdu.header['BSCALE'] = 1.0 # hdu.header['BSCALE']
    #output_hdu.header['DATAMAX'] = scale_factor * hdu.header['DATAMAX']
    #output_hdu.header['DATAMIN'] = scale_factor * hdu.header['DATAMIN']
    #print(output_hdu.columns['DATA'])
    if scale_factor > 1.0:
        output_hdu.header['BSCALE'] = scale_factor * output_hdu.header['BSCALE'] # otherwise overflow because ['DATA'] is stored in J (32-bit integer) format -- http://docs.astropy.org/en/stable/_modules/astropy/io/fits/column.html
        output_hdu.columns['DATA'].bscale = output_hdu.header['BSCALE'] # otherwise overflow because ['DATA'] is stored in J (32-bit integer) format -- http://docs.astropy.org/en/stable/_modules/astropy/io/fits/column.html
        output_hdu.header['DATAMAX'] = scale_factor * hdu.header['DATAMAX']
        output_hdu.header['DATAMIN'] = scale_factor * hdu.header['DATAMIN']
    else:
        output_hdu.header['BSCALE'] = (1.0/scale_factor**2) * output_hdu.header['BSCALE'] # otherwise overflow because ['DATA'] is stored in J (32-bit integer) format -- http://docs.astropy.org/en/stable/_modules/astropy/io/fits/column.html
        output_hdu.columns['DATA'].bscale = output_hdu.header['BSCALE'] # otherwise overflow because ['DATA'] is stored in J (32-bit integer) format -- http://docs.astropy.org/en/stable/_modules/astropy/io/fits/column.html
        output_hdu.header['DATAMAX'] = (1.0/scale_factor**2) * hdu.header['DATAMAX']
        output_hdu.header['DATAMIN'] = (1.0/scale_factor**2) * hdu.header['DATAMIN']
    # 
    # array operation, scale amplitudes
    # -- output_hdu is fits.GroupsHDU
    # -- output_hdu.data is fits.GroupsData, i.e., fits.FITS_rec, i.e., np.recarray
    # -- output_hdu.data.data is np.ndarray
    #output_hdu.data.data[...,2::3] = output_hdu.data.data[...,2::3] * scale_factor
    #output_hdu.data.data[2::3] = scale_factor * output_hdu.data.data[2::3]
    #output_hdu.data['DATA'][:][:][:][:][:][:][2] = scale_factor * output_hdu.data['DATA'][:][:][:][:][:][:][2]
    print(output_hdu.data['DATA'].shape)
    #print('DEBUG', output_hdu.data['UU'][0], output_hdu.data['VV'][0], output_hdu.data['WW'][0], output_hdu.data['DATA'][0][0][0][0][4][0][:])
    output_hdu.data['DATA'][...,0] = scale_factor * output_hdu.data['DATA'][...,0]
    output_hdu.data['DATA'][...,1] = scale_factor * output_hdu.data['DATA'][...,1]
    output_hdu.data['DATA'][...,2] = (1.0/scale_factor**2) * output_hdu.data['DATA'][...,2] # weights scales with 1/sigma**2, sigma scales with signal. 
    #print('DEBUG', output_hdu.data['UU'][0], output_hdu.data['VV'][0], output_hdu.data['WW'][0], output_hdu.data['DATA'][0][0][0][0][4][0][:])
    # 
    # check existing file
    if os.path.isfile(out_name+'.uvfits'):
        print('Found existing "{0}.uvfits"! Backup it as "{0}.uvfits.backup"!'.format(out_name))
        shutil.move(out_name+'.uvfits', out_name+'.uvfits.backup')
    # 
    # output
    output_hdu.writeto(out_name+'.uvfits', overwrite=True)
    # check output file and convert uvfits to uvt
    if os.path.isfile(out_name+'.uvfits'):
        print('Output to "{0}.uvfits"!'.format(out_name))
        # check existing file
        if os.path.isfile(out_name+'.uvt'):
            print('Found existing "{0}.uvt"! Backup it as "{0}.uvt.backup"!'.format(out_name))
            shutil.move(out_name+'.uvt', out_name+'.uvt.backup')
        # run gildas/mapping
        if os.path.isfile(out_name+'.uvfits'):
            print('Running: echo "fits {0}.uvfits to {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(out_name))
            os.system('echo "fits {0}.uvfits to {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(out_name))
        # check output file
        if os.path.isfile(out_name+'.uvt'):
            print('Output to "{0}.uvt"!'.format(out_name))
            print('Done!')
        else:
            print('Error! Failed to output {0}.uvt!'.format(out_name))
    else:
        print('Error! Failed to output {0}.uvfits!'.format(out_name))
    
    # 
    # debug read it back and check values
    #check_hdulist = fits.open(out_name+'.uvfits')
    #check_hdu = check_hdulist[0]
    #print('DEBUG', check_hdu.data['UU'][0], check_hdu.data['VV'][0], check_hdu.data['WW'][0], check_hdu.data['DATA'][0][0][0][0][4][0][:])
    
    # CrabFitsHeader test_random_2.uvfits > tmp_1.txt
    # CrabFitsHeader test_random_2_scaled_amplitude.uvfits > tmp_2.txt
    






