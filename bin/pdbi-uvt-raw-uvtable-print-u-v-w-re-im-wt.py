#!/usr/bin/env python3
# 
# An alternative Python code to print u v w from the input uvtable
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
    print('  pdbi-uvt-raw-uvtable-print-u-v-w-re-im-wt.py -name uvtable_spw1_example.uvt -out output_u_v_w_re_im_wt_table.fits')
    print('')
    print('Notes:')
    print('  -- this code allows to input *.uvt or *.uvfits, but uvfits must be generated in CASA data structure type. ')
    print('  -- The output file format can be either *.fits or *.txt or *.csv. ')
    print('')
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
global_data_dict['date'] = []
global_data_dict['time'] = []
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
    x_vis, x_chan, x_stokes = np.array(\
                                        list(\
                                            itertools.product(\
                                                                np.linspace(1, n_visi, num=n_visi, endpoint=True, dtype=np.int32), 
                                                                np.linspace(1, n_chan, num=n_chan, endpoint=True, dtype=np.int32), 
                                                                np.linspace(1, n_stokes, num=n_stokes, endpoint=True, dtype=np.int32)
                                            )
                                        )
                                    ).T
    global_data_dict['ivis'].extend(x_vis.flatten().tolist())
    global_data_dict['ichan'].extend(x_chan.flatten().tolist())
    global_data_dict['istokes'].extend(x_stokes.flatten().tolist())
    global_data_dict['u'].extend(np.repeat(tb.data['UU'] * const.c.to('m/s').value, n_chan*n_stokes).flatten().tolist())
    global_data_dict['v'].extend(np.repeat(tb.data['VV'] * const.c.to('m/s').value, n_chan*n_stokes).flatten().tolist())
    global_data_dict['w'].extend(np.repeat(tb.data['WW'] * const.c.to('m/s').value, n_chan*n_stokes).flatten().tolist())
    global_data_dict['re'].extend(tb.data['DATA'].flatten().tolist()[0::3])
    global_data_dict['im'].extend(tb.data['DATA'].flatten().tolist()[1::3])
    global_data_dict['wt'].extend(tb.data['DATA'].flatten().tolist()[2::3])
    global_data_dict['amp'].extend(np.sqrt(np.array(global_data_dict['re'])**2 + np.array(global_data_dict['im'])**2).tolist())
    global_data_dict['date'].extend(np.repeat(tb.data['DATE'], n_chan*n_stokes).flatten().tolist())
    global_data_dict['time'].extend(np.repeat(tb.data['_DATE'], n_chan*n_stokes).flatten().tolist())


for i in ['ivis', 'ichan', 'istokes', 'u', 'v', 'w', 're', 'im', 'wt', 'amp', 'date', 'time']:
    print('len(global_data_dict[%s]) = %d'%(i, len(global_data_dict[i])))
tbout = Table(global_data_dict)
tbout['u'].format = '%0.3f'
tbout['v'].format = '%0.3f'
tbout['w'].format = '%0.3f'
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





