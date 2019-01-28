#!/usr/bin/env python3
# 
# A Python code to split half visibilities randomly
# 

import os, sys, re
import numpy as np
import astropy
from astropy.table import Table
from astropy.io import fits
from copy import copy
import itertools

# 
# read user input
uvt_names = []
out_name = ''
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
    # 
    if arg_mode == 'name':
        if not os.path.isfile(sys.argv[iarg]):
            print('Error! The input file "%s" does not exist!'%(sys.argv[iarg]))
            sys.exit()
        uvt_names.append(sys.argv[iarg])
    if arg_mode == 'out':
        out_name = sys.argv[iarg]
    # 
    iarg += 1


# 
# print usage
if len(uvt_names) == 0 or out_name == '':
    print('')
    print('Usage: ')
    print('  pdbi-uvt-raw-uvtable-split-half-visibilities-randomly.py -name uvtable_spw1_example.uvfits -out output_split.uvfits')
    print('')
    print('Notes:')
    print('  -- this code allows to input *.uvt or *.uvfits, but uvfits must be generated in CASA data structure type. ')
    print('  -- The output file format must be *.uvfits. ')
    print('  -- We will output two files: one named as the output file name and contains half of the visibilities, the other named *.2.uvfits and contains the other half visibilities. ')
    print('')
    sys.exit()

if len(uvt_names) > 1:
    print('Error! Please input only one uvfits file!')
    sys.exit()


# 
# loop the input uvtables
output_data_array = None
output_data_array_2 = None
for i_uvt in range(len(uvt_names)):
    uvt_name = uvt_names[i_uvt]
    uvt_type = 'none'
    # 
    # check suffix
    if re.match(r'(.*?)\.uvt', uvt_name, re.IGNORECASE):
        uvt_name = re.sub(r'(.*?)\.uvt', r'\1', uvt_name, re.IGNORECASE)
        uvt_type = 'uvt'
    elif re.match(r'(.*?)\.uvfits', uvt_name, re.IGNORECASE):
        uvt_name = re.sub(r'(.*?)\.uvfits', r'\1', uvt_name, re.IGNORECASE)
        uvt_type = 'uvfits'
    else:
        print('Error! The input data is neither uvtable nor uvfits! Please check the input file type, make sure the suffix is either *.uvt or *.uvfits!')
        sys.exit()
    # 
    # check suffix for out_name
    if re.match(r'(.*?)\.uvfits', out_name, re.IGNORECASE):
        out_name = re.sub(r'(.*?)\.uvfits', r'\1', out_name, re.IGNORECASE)
    # 
    # convert uvt to uvfits
    if uvt_type == 'uvt':
        print('Running: echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
        os.system('echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
        if not os.path.isfile(uvt_name+'.uvfits'):
            print('Error! Failed to call GILDAS/mapping to convert "{0}.uvt" to "{0}.uvfits"!'.format(uvt_name))
            sys.exit()
    # 
    # read uvfits 
    print('Reading '+uvt_name+'.uvfits')
    hdu = fits.open(uvt_name+'.uvfits')
    if type(hdu[0]) != fits.GroupsHDU:
        print('Error! The uvfits file "{0}.uvfits" is not fits.GroupsHDU type!'.format(uvt_name))
        sys.exit()
    tb = hdu[0]
    print(type(tb))
    print(tb.columns)
    print(tb.columns.names)
    print(type(tb.data))
    print(len(tb.data))
    #print(tb.data.shape)
    #print(len(tb.data[0]))
    #print(tb.data[0]['DATA'].shape)
    #print(type(tb.data[0]['DATA']))
    #print(type(tb.data))
    #tb.data.sort(order=['UU','VV','WW'])
    # 
    # read data array 
    data_array = tb.data['DATA']
    print('DATA shape', data_array.shape)
    #print(tb.data['DATE'][0])
    #print(tb.data['DATE'][1])
    #print(tb.data['_DATE'][0])
    #print(tb.data['_DATE'][1])
    #print(tb.data['FREQSEL'][0])
    #print(tb.data['FREQSEL'][1])
    # 
    # copy data array and randomly select half
    p = 0.5
    mask = np.random.choice(a=[False, True], size=(len(tb.data),), p=[p, 1-p])
    print(type(mask), mask.shape, np.count_nonzero(mask)) # tb.data['UU'][mask]
    # 
    output_data_array = tb.copy()
    output_data_array.data = output_data_array.data[mask]
    #for key in tb.columns.names:
    #    print('Copying %s'%(key))
    #    output_data_array.data = output_data_array.data[mask]
    output_data_array.writeto(out_name+'.uvfits', overwrite=True)
    print('Output to "%s"!'%(out_name+'.uvfits'))
    # 
    output_data_array_2 = tb.copy()
    output_data_array_2.data = output_data_array_2.data[~mask]
    #for key in tb.columns:
    #    output_data_array_2.data[key] = output_data_array_2.data[key][~mask]
    output_data_array_2.writeto(out_name+'.2.uvfits', overwrite=True)
    print('Output to "%s"!'%(out_name+'.2.uvfits'))









