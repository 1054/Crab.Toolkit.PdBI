#!/usr/bin/env python3
# 

import os, sys, re
import astropy
from astropy.io import fits

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
        uvt_names.append(re.sub(r'(.*?)\.uvt', r'\1', sys.argv[iarg]))
    if arg_mode == 'out':
        out_name = re.sub(r'(.*?)\.uvt', r'\1', sys.argv[iarg])
    # 
    iarg += 1


# 
# print usage
if len(uvt_names) == 0 or out_name == '':
    print('Usage: ')
    print('  pdbi-uvt-merge-two-data-cube-spw-channel-by-channel.py -name uvtable_spw1_resampled.uvt uvtable_spw2_resampled.uvt uvtable_spw3_resampled.uvt -out output_merged_data_cube.uvt')
    sys.exit()


# 
# loop the input uvtables
for uvt_name in uvt_names:
    # 
    # convert uvt to uvfits
    if not os.path.isfile(uvt_name+'.uvfits'):
        print('Running: echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
        os.system('echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
    if not os.path.isfile(uvt_name+'.uvfits'):
        print('Error! Failed to call GILDAS/mapping to convert "{0}.uvt" to "{0}.uvfits"!'.format(uvt_name))
    # 
    # read uvfits 
    print('Reading '+uvt_name+'.uvfits')
    hdu = fits.open(uvt_name+'.uvfits')
    if type(hdu[0]) != fits.GroupsHDU:
        print('Error! The uvfits file "{0}.uvfits" is not fits.GroupsHDU type!'.format(uvt_name))
        sys.exit()
    tb = hdu[0]
    print(tb.columns)
    print(len(tb.data))




