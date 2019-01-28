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
    print('  pdbi-uvt-raw-uvtable-do-average-channel-by-channel.py -name uvtable_spw1_resampled.uvt uvtable_spw2_resampled.uvt uvtable_spw3_resampled.uvt -out output_merged_data_cube.uvt')
    print('  -- this code will merge data cubes with exactly the same channel number and visibilities, i.e., difference spectral window (spw) data from the same observation but after running pdbi-uvt-go-resample to a common frequency grid.')
    sys.exit()


# 
# loop the input uvtables
gloabl_n_visi = 0
global_tbs = []
global_tbdata = []
global_tbcols = []
previous_u_values = None
previous_v_values = None
previous_w_values = None
previous_data_shape = None
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
    tb.data.sort(order=['UU','VV','WW'])
    # 
    # check n_visi consistency
    n_visi = len(tb.data)
    if gloabl_n_visi == 0:
        gloabl_n_visi = n_visi
    elif gloabl_n_visi != n_visi:
        print('Error! The input uvfits files do not have matched number of visibilities!')
        print('gloabl_n_visi = %d, n_visi = %d'%(gloabl_n_visi, n_visi))
        sys.exit()
    # 
    # check n_chan consistency
    if previous_data_shape is None:
        previous_data_shape = tb.data['DATA'].shape
    elif not np.array_equal(previous_data_shape, tb.data['DATA'].shape):
        print('Error! The input uvfits file do not have matched number of channel and stokes!')
        sys.exit()
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
    current_u_values = tb.data['UU']
    current_v_values = tb.data['VV']
    current_w_values = tb.data['WW']
    # 
    # check uvw consistency
    check_uvw_toleration = 1e-3
    if previous_u_values is None:
        previous_u_values = current_u_values
        previous_v_values = current_v_values
        previous_w_values = current_w_values
    elif np.count_nonzero(np.abs(current_u_values - previous_u_values) > np.abs(current_u_values + previous_u_values) * check_uvw_toleration) > 0 or \
         np.count_nonzero(np.abs(current_v_values - previous_v_values) > np.abs(current_v_values + previous_v_values) * check_uvw_toleration) > 0 or \
         np.count_nonzero(np.abs(current_w_values - previous_w_values) > np.abs(current_w_values + previous_w_values) * check_uvw_toleration) > 0: 
        print('Error! The input uvfits files do not have matched visibilities (u,v,w)!')
        print('inconsistent u i_visi', np.array2string(np.argwhere(np.abs(current_u_values - previous_u_values) > np.abs(current_u_values + previous_u_values) * check_uvw_toleration).flatten(), separator=', '))
        print('inconsistent v i_visi', np.array2string(np.argwhere(np.abs(current_v_values - previous_v_values) > np.abs(current_v_values + previous_v_values) * check_uvw_toleration).flatten(), separator=', '))
        print('inconsistent w i_visi', np.array2string(np.argwhere(np.abs(current_w_values - previous_w_values) > np.abs(current_w_values + previous_w_values) * check_uvw_toleration).flatten(), separator=', '))
        i_visi = 985
        print('previous_uvw[0] = ' + np.array2string(np.array([previous_u_values[i_visi], previous_v_values[i_visi], previous_w_values[i_visi]]), separator=', ') + ', '
              'current_uvw[0] = ' + np.array2string(np.array([current_u_values[i_visi], current_v_values[i_visi], current_w_values[i_visi]]), separator=', '))
        print(np.abs(current_u_values[i_visi] - previous_u_values[i_visi]), np.abs(current_u_values[i_visi] + previous_u_values[i_visi]) * check_uvw_toleration, (np.abs(current_u_values[i_visi] - previous_u_values[i_visi]) > np.abs(current_u_values[i_visi] + previous_u_values[i_visi]) * 1e-6))
        print(np.abs(current_v_values[i_visi] - previous_v_values[i_visi]), np.abs(current_v_values[i_visi] + previous_v_values[i_visi]) * check_uvw_toleration, (np.abs(current_v_values[i_visi] - previous_v_values[i_visi]) > np.abs(current_v_values[i_visi] + previous_v_values[i_visi]) * 1e-6))
        print(np.abs(current_w_values[i_visi] - previous_w_values[i_visi]), np.abs(current_w_values[i_visi] + previous_w_values[i_visi]) * check_uvw_toleration, (np.abs(current_w_values[i_visi] - previous_w_values[i_visi]) > np.abs(current_w_values[i_visi] + previous_w_values[i_visi]) * 1e-6))
        sys.exit()
    # 
    # if passed all checks, append to global_tbs
    global_tbs.append(tb)

# 
# initialize global_tbout
global_tbout = global_tbs[0].copy()
global_tbcols = global_tbout.columns
global_tbdata = global_tbout.data
print('global_tbcols = %s'%(global_tbcols))
print('global_tbdata_DATA_shape = %s'%(str(global_tbdata['DATA'].shape)))
#print('global_tbdata_DATA0_shape = %s'%(str(global_tbdata['DATA'][0].shape)))
#print(global_tbdata['DATA'][0][0][0][0].shape)
# dim = (1, 1, 1, 132, 1, 3)
#        sb
#           gb
#              mb
#                 chan
#                     stokes
#                         
#              
n_visi = global_tbdata['DATA'].shape[0]
n_chan = global_tbdata['DATA'][0][0][0][0].shape[0]
n_stokes = global_tbdata['DATA'][0][0][0][0][0].shape[0]
#i_visi = 100
#i_chan = 100
#i_stokes = 0
#print('global_tbdata i_visi=%d i_chan=%d:'%(i_visi, i_chan), global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes])
#print('type(global_tbdata[\'DATA\'][i_visi=%d][0][0][0][i_chan=%d][i_stokes=%d][0]):'%(i_visi,i_chan,i_stokes), type(global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes][0]), '(re)')
#print('type(global_tbdata[\'DATA\'][i_visi=%d][0][0][0][i_chan=%d][i_stokes=%d][1]):'%(i_visi,i_chan,i_stokes), type(global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes][1]), '(im)')
#print('type(global_tbdata[\'DATA\'][i_visi=%d][0][0][0][i_chan=%d][i_stokes=%d][2]):'%(i_visi,i_chan,i_stokes), type(global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes][2]), '(wt)')
#for i_visi in range(n_visi):
#    for i_chan in range(n_chan):
#        if(global_tbdata['DATA'][i_visi][0][0][0][i_chan][0][0] > 0):
#            print('global_tbdata i_visi=%d i_chan=%d:'%(i_visi, i_chan), global_tbdata['DATA'][i_visi][0][0][0][i_chan][0])
#sys.exit()

# 
# test np.count_nonzero
#test_data_vis0_chan0_stokes0 = np.array([0.0,0.0,0.0])
#test_data_vis0_chan1_stokes0 = np.array([0.0,0.0,1.0])
#test_data_vis0_chan2_stokes0 = np.array([0.0,0.0,1.0])
#test_data_vis0_chan3_stokes0 = np.array([0.0,0.0,1.0])
#test_data_vis0_chan0 = np.array([test_data_vis0_chan0_stokes0])
#test_data_vis0_chan1 = np.array([test_data_vis0_chan1_stokes0])
#test_data_vis0_chan2 = np.array([test_data_vis0_chan2_stokes0])
#test_data_vis0_chan3 = np.array([test_data_vis0_chan3_stokes0])
#test_data_vis0___ = np.array([test_data_vis0_chan0,
#                              test_data_vis0_chan1,
#                              test_data_vis0_chan2,
#                              test_data_vis0_chan3])
#test_data_vis0__ = np.array([test_data_vis0___])
#test_data_vis0_ = np.array([test_data_vis0__])
#test_data_vis0 = np.array([test_data_vis0_])
## 
#test_data_vis1_chan0_stokes0 = np.array([0.0,0.0,0.0])
#test_data_vis1_chan1_stokes0 = np.array([0.0,0.0,1.0])
#test_data_vis1_chan2_stokes0 = np.array([0.0,0.0,1.0])
#test_data_vis1_chan3_stokes0 = np.array([0.0,0.0,1.0])
#test_data_vis1_chan0 = np.array([test_data_vis1_chan0_stokes0])
#test_data_vis1_chan1 = np.array([test_data_vis1_chan1_stokes0])
#test_data_vis1_chan2 = np.array([test_data_vis1_chan2_stokes0])
#test_data_vis1_chan3 = np.array([test_data_vis1_chan3_stokes0])
#test_data_vis1___ = np.array([test_data_vis1_chan0,
#                              test_data_vis1_chan1,
#                              test_data_vis1_chan2,
#                              test_data_vis1_chan3])
#test_data_vis1__ = np.array([test_data_vis1___])
#test_data_vis1_ = np.array([test_data_vis1__])
#test_data_vis1 = np.array([test_data_vis1_])
## 
#data_array = np.array([test_data_vis0,test_data_vis1])
#count_nonzero_along_last_dimension = np.count_nonzero(data_array, axis=len(data_array.shape)-1) # If the item along the second last axis (re,im,wt) is (0,0,0) then count_nonzero is 0 otherwise 1. The output 'count_nonzero_along_last_dimension' has a dimension of 'data_array.shape[:-1]'. 
#count_nonzero_data_array = np.repeat(count_nonzero_along_last_dimension[...,np.newaxis], 3, axis=len(data_array.shape)-1) # If the item along the second last axis (re,im,wt) is (0,0,0), then each item along the last axis is set to 0, otherwise 1. The output 'count_nonzero_data_array' has a dimension of 'data_array.shape'. 
#print('data_array_shape = %s'%(str(data_array.shape)))
#print(count_nonzero_along_last_dimension.shape)
#print(count_nonzero_along_last_dimension)
#print(count_nonzero_data_array.shape)
#print(count_nonzero_data_array)
#sys.exit()


# 
# loop each input uvtable and average valid data
global_data_array = global_tbdata['DATA'] * 0.0
global_count_array = global_tbdata['DATA'] * 0
for i_tb in range(len(global_tbs)):
    #print('data_table = "%s"'%(uvt_names[i_tb]))
    # 
    # array operation to mask valid data and only average valid data
    data_array = global_tbs[i_tb].data['DATA']
    count_nonzero_along_last_dimension = np.count_nonzero(data_array, axis=len(data_array.shape)-1) # If the item along the second last axis (re,im,wt) is (0,0,0) then count_nonzero is 0 otherwise 1. The output 'count_nonzero_along_last_dimension' has a dimension of 'data_array.shape[:-1]'. 
    count_array = np.repeat(count_nonzero_along_last_dimension[...,np.newaxis], 3, axis=len(data_array.shape)-1) # If the item along the second last axis (re,im,wt) is (0,0,0), then each item along the last axis is set to 0, otherwise 1. The output 'count_nonzero_data_array' has a dimension of 'data_array.shape'. 
    #print('data_array.shape = %s'%(str(data_array.shape)))
    # 
    mask_array = (count_array > 0)
    #print('mask_array.shape = %s'%(str(mask_array.shape)))
    # 
    global_data_array[mask_array] += data_array[mask_array]
    global_count_array += mask_array.astype(int)
    # 
    # print debug info
    #i_visi = 100
    #i_chan = 64
    #i_stokes = 0
    #print('debug info: i_visi=%d, i_chan=%d, i_stokes=%d, i_tb=%d, data_array=%s'%(i_visi, i_chan, i_stokes, i_tb, np.array2string(data_array[i_visi][0][0][0][i_chan][i_stokes], separator=', ')))
    #print('debug info: i_visi=%d, i_chan=%d, i_stokes=%d, i_tb=%d, mask_array=%s'%(i_visi, i_chan, i_stokes, i_tb, np.array2string(mask_array[i_visi][0][0][0][i_chan][i_stokes], separator=', ')))
    #print('debug info: i_visi=%d, i_chan=%d, i_stokes=%d, i_tb=%d, mask_array=%s'%(i_visi, i_chan, i_stokes, i_tb, np.array2string(mask_array[i_visi][0][0][0][i_chan][i_stokes].astype(int), separator=', ')))
    ##continue
# 
global_mask_array = (global_count_array > 0)
global_data_array[global_mask_array] = global_data_array[global_mask_array] / global_count_array[global_mask_array]
# 

# 
# print debug info
#i_visi = 100
#i_chan = 64
#i_stokes = 0
#print('debug info: i_visi=%d, i_chan=%d, i_stokes=%d, global_data_array=%s'%(i_visi, i_chan, i_stokes, np.array2string(global_data_array[i_visi][0][0][0][i_chan][i_stokes], separator=', ')))
#print('debug info: i_visi=%d, i_chan=%d, i_stokes=%d, global_count_array=%s'%(i_visi, i_chan, i_stokes, np.array2string(global_count_array[i_visi][0][0][0][i_chan][i_stokes], separator=', ')))

#sys.exit()

### 
### loop each visibility and do average channel by channel
##count_processed = 0
##for i_visi in range(n_visi):
##    u = global_tbdata[i_visi]['UU']
##    v = global_tbdata[i_visi]['VV']
##    w = global_tbdata[i_visi]['WW']
##    # 
##    # check u v w consistency
##    #for i_tb in range(len(global_tbs)):
##    #    t_u = global_tbs[i_tb].data[i_visi]['UU']
##    #    t_v = global_tbs[i_tb].data[i_visi]['VV']
##    #    t_w = global_tbs[i_tb].data[i_visi]['WW']
##    #    # 
##    #    # check u v w consistency
##    #    #print('checking u consistency: u = %s, tb%d_u = %s'%(u, i_tb+1, t_u))
##    #    #print('checking v consistency: v = %s, tb%d_v = %s'%(v, i_tb+1, t_v))
##    #    #print('checking w consistency: w = %s, tb%d_w = %s'%(w, i_tb+1, t_w))
##    #    check_ok = False
##    #    if np.abs(u - t_u) < np.abs(u + t_u) * 1e-6 and \
##    #       np.abs(v - t_v) < np.abs(v + t_v) * 1e-6 and \
##    #       np.abs(w - t_w) < np.abs(w + t_w) * 1e-6:
##    #       check_ok = True
##    # 
##    # loop each channel and average data
##    for i_chan in range(n_chan):
##        for i_stokes in range(n_stokes):
##            # prepare to sum value per channel
##            n_valid = 0
##            sum_val = np.array([0.0,0.0,0.0])
##            for i_tb in range(len(global_tbs)):
##                t_val = global_tbs[i_tb].data[i_visi]['DATA'][0][0][0][i_chan][i_stokes]
##                if np.count_nonzero(t_val) > 0:
##                    #print('i_visi', i_visi, 'i_chan', i_chan, 'i_stokes', i_stokes, '%-12s'%('tb%d_val'%(i_tb+1)), t_val)
##                    sum_val += t_val
##                    n_valid += 1
##            if n_valid > 0:
##                global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes] = sum_val / np.float(n_valid)
##                # 
##                # print debuf message
##                if False:
##                    print('i_visi', '%-3d'%(i_visi), 'i_chan', '%-3d'%(i_chan), 'i_stokes', i_stokes, '%-12s'%('global_val'), sum_val / n_valid)
##                    if n_valid > 1:
##                        count_processed += 1
##                        sum_val = np.array([0.0,0.0,0.0])
##                        for i_tb in range(len(global_tbs)):
##                            t_val = global_tbs[i_tb].data[i_visi]['DATA'][0][0][0][i_chan][i_stokes]
##                            sum_val += t_val
##                            print('i_visi', '%-3d'%(i_visi), 'i_chan', '%-3d'%(i_chan), 'i_stokes', i_stokes, '%-12s'%('tb%d_val'%(i_tb+1)), t_val, 'np.count_nonzero(t_val)', np.count_nonzero(t_val), 'sum_val', sum_val)
##                        val = global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes]
##                        print('i_visi', '%-3d'%(i_visi), 'i_chan', '%-3d'%(i_chan), 'i_stokes', i_stokes, '%-12s'%('global_val'), val)
##                        #print(sum_val, np.float(n_valid), sum_val / np.float(n_valid)) # must make sure the data is a copy otherwise here we have problem.
##        
##        # 
##        #if count_processed > 5:
##        #    break
##    # 
##    #if count_processed > 5:
##    #    break
##
##
###i_visi = 100
###i_chan = 100
###i_stokes = 0
###print(i_visi,i_chan,i_stokes, global_tbdata[i_visi]['DATA'][0][0][0][i_chan][i_stokes])
###print(i_visi,i_chan,i_stokes, global_tbout.data[i_visi]['DATA'][0][0][0][i_chan][i_stokes])
###100 100 0 [0.0670351  0.01619025 0.24953307]
###100 100 0 [0.0670351  0.01619025 0.24953307]


# 
# store the data array
global_tbout.data['DATA'] = global_data_array


# 
# Save as new uvfits and uvt
if os.path.isfile(out_name+'.uvfits'):
    print('Found existing "{0}"! Backup it as "{0}.uvfits.backup"!'.format(out_name))
    shutil.move(out_name+'.uvfits', out_name+'.uvfits.backup')
global_tbout.writeto(out_name+'.uvfits', overwrite=True)
# then convert uvfits to uvt
if os.path.isfile(out_name+'.uvfits'):
    print('Output to "{0}.uvfits"!'.format(out_name))
    # check existing file
    if os.path.isfile(out_name+'.uvt'):
        print('Backing-up existing {0}.uvt as {0}.uvt.backup'.format(out_name))
        os.system('mv {0}.uvt {0}.uvt.backup'.format(out_name))
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










