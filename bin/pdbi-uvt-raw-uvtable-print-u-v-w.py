#!/usr/bin/env python
# 
# An alternative Python code to print u v w from the input uvtable
# if the uv table has only one channel and one stokes, then we also output re im wt amp
# 

import os, sys, re
import numpy as np
import astropy
from astropy.table import Table
from astropy.io import fits
import astropy.constants as const
from copy import copy
import shutil
import itertools

# 
# read user input
uvt_names = []
out_name = ''
keep_zeros = False
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
    elif arg_str == '-keep-zeros' or arg_str == '-keepzeros':
        arg_mode = ''
        keep_zeros = True
        iarg += 1
        continue
    elif arg_str == '-keep-files' or arg_str == '-keepfiles':
        arg_mode = ''
        iarg += 1
        continue
    # 
    if arg_mode == 'name':
        if not os.path.isfile(sys.argv[iarg]):
            print('Error! The input file "%s" does not exist!'%(sys.argv[iarg]))
            sys.exit()
        uvt_names.append(sys.argv[iarg])
    elif arg_mode == 'out':
        out_name = sys.argv[iarg]
    # 
    iarg += 1


# 
# print usage
if len(uvt_names) == 0 or out_name == '':
    print('')
    print('Usage: ')
    print('  pdbi-uvt-raw-uvtable-print-u-v-w.py -name uvtable_spw1_example.uvt -out output_u_v_w_re_im_wt_table.txt')
    print('')
    print('Notes:')
    print('  -- This code allows to input *.uvt or *.uvfits, but uvfits must be generated in CASA data structure type.')
    print('     In the case of inputting a *.uvt, we will call GILDAS MAPPING FITS command to convert it to *.uvfits.')
    print('  -- The output file is a table with 4 or 7 columns: ')
    print('     If the input data has more than one channel or stokes, then we output 4 columns: ivis, u, v, w.')
    print('     Else if the input data has only one channel and one stokes, then we output 7 columns: ivis, u, v, w, re, im, wt, amp.')
    print('     The output format can be either *.txt or *.csv or *.fits.')
    print('  -- Data rows where re, im, wt are all zeros will not be output, this can happen for some edge channels,')
    print('     and thus the output table might not have a uniform block size. To keep those zero rows, use the -keep-zeros option.')
    print('')
    sys.exit()


# 
# check uvt_names
if len(uvt_names) > 1:
    print('Error! Please input only one uv table!')
    sys.exit(255)


# 
# loop the input uvtables
global_data_dict = {}
global_data_dict['ivis'] = []
#global_data_dict['ichan'] = []
#global_data_dict['istokes'] = []
global_data_dict['u'] = []
global_data_dict['v'] = []
global_data_dict['w'] = []
global_data_dict['re'] = []
global_data_dict['im'] = []
global_data_dict['wt'] = []
global_data_dict['amp'] = []
#global_data_dict['date'] = [] # if output date mjd and time then uncomment this line
#global_data_dict['time'] = [] # if output date mjd and time then uncomment this line
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
        # check existing file
        if os.path.isfile(out_name+'.uvfits'):
            print('Found existing "{0}.uvfits"! Backup it as "{0}.uvfits.backup"!'.format(out_name))
            shutil.move(out_name+'.uvfits', out_name+'.uvfits.backup')
        # run gildas/mapping
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
    print(tb.columns)
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
    print('DATA shape', data_array.shape)
    #print(tb.data['DATE'][0])
    #print(tb.data['DATE'][1])
    #print(tb.data['_DATE'][0])
    #print(tb.data['_DATE'][1])
    #print(tb.data['FREQSEL'][0])
    #print(tb.data['FREQSEL'][1])
    n_visi = data_array.shape[0]
    n_chan = data_array.shape[4]
    n_stokes = data_array.shape[5]
    # 
    x_vis = np.linspace(1, n_visi, num=n_visi, endpoint=True, dtype=np.int32)
    global_data_dict['ivis'].extend(x_vis.flatten().tolist())
    global_data_dict['u'].extend((tb.data['UU'] * const.c.to('m/s').value).flatten().tolist())
    global_data_dict['v'].extend((tb.data['VV'] * const.c.to('m/s').value).flatten().tolist())
    global_data_dict['w'].extend((tb.data['WW'] * const.c.to('m/s').value).flatten().tolist())
    # 
    # if the uv table has only one channel and one stokes, then we also output re im wt amp
    if n_chan == 1 and n_stokes == 1:
        global_data_dict['re'].extend(tb.data['DATA'].flatten().tolist()[0::3])
        global_data_dict['im'].extend(tb.data['DATA'].flatten().tolist()[1::3])
        global_data_dict['wt'].extend(tb.data['DATA'].flatten().tolist()[2::3])
        global_data_dict['amp'].extend(np.sqrt(np.array(global_data_dict['re'])**2 + np.array(global_data_dict['im'])**2).tolist())
        #global_data_dict['date'].extend((tb.data['DATE']).flatten().tolist()) # if output date mjd and time then uncomment this line
        #global_data_dict['time'].extend((tb.data['_DATE']).flatten().tolist()) # if output date mjd and time then uncomment this line
    
    # 
    # check whether to keep rows where re, im, wt are all zeros
    if not keep_zeros:
        mask_zeros = np.logical_and.reduce((np.isclose(global_data_dict['re'], 0.0), np.isclose(global_data_dict['im'], 0.0), np.isclose(global_data_dict['wt'], 0.0)))
        count_zeros = np.count_nonzero(mask_zeros)
        if count_zeros > 0:
            print('Removing %d rows where re, im, wt are all zeros'%(count_zeros))
            for key in global_data_dict:
                global_data_dict[key] = np.array(global_data_dict[key])[~mask_zeros]


#for i in ['ivis', 'ichan', 'istokes', 'u', 'v', 'w', 're', 'im', 'wt', 'amp', 'date', 'time']:
for i in ['ivis']:
    print('len(global_data_dict[%s]) = %d'%(i, len(global_data_dict[i])))
keys = list(global_data_dict.keys())
for key in keys:
    if len(global_data_dict[key]) == 0:
        del global_data_dict[key]
tbout = Table(global_data_dict)
tbout['u'].format = '%0.3f'
tbout['v'].format = '%0.3f'
tbout['w'].format = '%0.3f'
if 'amp' in global_data_dict:
    tbout['re'].format = '%0.3E'
    tbout['im'].format = '%0.3E'
    tbout['wt'].format = '%0.3E'
    tbout['amp'].format = '%0.3E'

regex_pattern = re.compile(r'^(.+)\.(fits|txt|csv)$')
if regex_pattern.match(out_name):
    out_base = regex_pattern.sub(r'\1', out_name)
    out_type = regex_pattern.sub(r'\2', out_name)
else:
    out_base = out_name
    out_type = 'fits'

print('Writing to disk')
if out_type.lower() == 'txt':
    out_format = 'ascii.fixed_width'
    tbout.write(out_base+'.'+out_type, format=out_format, delimiter=' ', bookend=True, overwrite=True)
    with open(out_base+'.'+out_type, 'r+') as fp:
        fp.seek(0)
        fp.write('#')
else:
    out_format = out_type.lower()
    tbout.write(out_base+'.'+out_type, format=out_format, overwrite=True)

print('Output to "%s"!'%(out_base+'.'+out_type))





