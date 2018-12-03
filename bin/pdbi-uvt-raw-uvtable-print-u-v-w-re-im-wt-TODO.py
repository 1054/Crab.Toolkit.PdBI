#!/usr/bin/env python3
# 
# An alternative Python code to print u v w from the input uvtable
# 

import os, sys, re
import numpy as np
import astropy
from astropy.table import Table
from astropy.io import fits
from copy import copy

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
    print('Usage: ')
    print('  pdbi-uvt-raw-uvtable-print-u-v-w-re-im-wt.py -name uvtable_spw1_resampled.uvt -out output_u_v_w_re_im_wt_table.txt')
    print('  -- this code allows to input *.uvt or *.uvfits, but uvfits must be generated in CASA data structure type. ')
    sys.exit()


# 
# loop the input uvtables
global_data_dict = {}
global_data_dict['ivis'] = []
global_data_dict['ichan'] = []
global_data_dict['istokes'] = []
global_data_dict['u'] = []
global_data_dict['v'] = []
global_data_dict['w'] = []
global_data_dict['re'] = []
global_data_dict['im'] = []
global_data_dict['wt'] = []
global_data_dict['amp'] = []
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
    #print(tb.columns)
    #print(len(tb.data))
    #print(tb.data.shape)
    #print(len(tb.data[0]))
    #print(tb.data[0]['DATA'].shape)
    #print(type(tb.data[0]['DATA']))
    #print(type(tb.data))
    #tb.data.sort(order=['UU','VV','WW'])
    # 
    # read data array 
    data_array = tb.data['DATA']
    print(data_array.shape)
    n_visi = data_array.shape[0]
    n_chan = data_array.shape[4]
    n_stokes = data_array.shape[5]
    i_visi = 
    # 
    # debug: dump the sorted uvw data
    #dump_uvw_data_dict = {}
    #dump_uvw_data_dict['u'] = tb.data['UU']
    #dump_uvw_data_dict['v'] = tb.data['VV']
    #dump_uvw_data_dict['w'] = tb.data['WW']
    #dump_uvw_data_table = Table(dump_uvw_data_dict)
    #dump_uvw_data_table['u'].format = '%0.3e'
    #dump_uvw_data_table['v'].format = '%0.3e'
    #dump_uvw_data_table['w'].format = '%0.3e'
    #dump_uvw_data_table.write('dump_uvw_of_i_uvt_%d.txt'%(i_uvt), format='ascii.fixed_width', overwrite=True)
    #current_u_values = tb.data['UU']
    #current_v_values = tb.data['VV']
    #current_w_values = tb.data['WW']


tbout = Table(global_data_dict)
tbout['u'].format = '%0.3e'
tbout['v'].format = '%0.3e'
tbout['w'].format = '%0.3e'
tbout['amp'].format = '%0.3e'
