#!/usr/bin/env python
# 

import os, sys, re
for i in range(len(sys.path)):
    if sys.path[i].find('GILDAS') >= 0:
        sys.path[i] = ''
    if sys.path[i].find('CASA') >= 0:
        sys.path[i] = ''
import numpy, matplotlib, astropy
import astropy.io.ascii as asciitable
from astropy.table import Table
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate

np = numpy

if len(sys.argv) <= 2:
    print('Usage: ')
    print('    pdbi_uvt_go_expand_line_channel_range_with_python.py "XXX.result.obj_1.txt" starting_frequency')
    print('')
    sys.exit()



# 
# Define function
def moving_mean(data, index, width):
    # mean of data[index, index+width], 
    # but mind the boundary
    if index < 0 or index >= len(data):
        return np.nan
    # 
    if width > 0:
        boundary_left = index
        boundary_right = index+width
        if boundary_right > len(data):
            boundary_right = len(data)-1
    else:
        boundary_left = index+width
        boundary_right = index
        if boundary_left < 0:
            boundary_left = 0
    # 
    return np.nanmean(data[boundary_left:boundary_right+1])



# 
# Read user input
input_table_file = ''
input_start_freq = np.nan
output_lower_freq = np.nan
output_upper_freq = np.nan

i = 1
while i < len(sys.argv):
    if input_table_file == '':
        input_table_file = sys.argv[i]
    elif np.isnan(input_start_freq):
        input_start_freq = float(sys.argv[i])
    i = i + 1

# 
# Check input_name
if input_table_file == '' or np.isnan(input_start_freq):
    print('Error! Please input uvfit result table and the starting frequency!')
    sys.exit()

else:
    # 
    # Read input data table
    #input_table = Table.read(input_name, format='ascii.commented_header')
    input_table = asciitable.read(input_table_file)
    #input_table_header = asciitable.read(input_name, data_start = 0, data_end = 1)
    #print(input_table_header)
    # 
    # Read x y
    x = None
    y = None
    yerr = None
    SNR = None
    if 'freq' in input_table.colnames:
        # Find out invalid data with '***'
        invalid_mask = [True if '*' in str(t) else False for t in input_table['freq']]
        if numpy.count_nonzero(invalid_mask) > 0:
            input_table['freq'][invalid_mask] = 'NaN'
    if 'SNR' in input_table.colnames:
        # Find out invalid data with '***'
        invalid_mask = [True if '*' in str(t) else False for t in input_table['SNR']]
        if numpy.count_nonzero(invalid_mask) > 0:
            input_table['SNR'][invalid_mask] = 'NaN'
    if 'freq' in input_table.colnames:
        x = numpy.array(input_table['freq']).astype(float)
    if 'frequency' in input_table.colnames:
        x = numpy.array(input_table['frequency']).astype(float)
    if 'flux' in input_table.colnames:
        y = numpy.array(input_table['flux']).astype(float)
    if 'flux_err' in input_table.colnames:
        yerr = numpy.array(input_table['flux_err']).astype(float)
    if 'SNR' in input_table.colnames:
        SNR = numpy.array(input_table['SNR']).astype(float)
        SNR_mask = (numpy.isnan(SNR)) # excluding NaN
        if x is not None: x[SNR_mask] = numpy.nan
        if y is not None: y[SNR_mask] = numpy.nan
        if yerr is not None: yerr[SNR_mask] = numpy.nan
    # 
    # check x y arrays
    if x is not None and y is not None:
        # 
        # check array size
        if len(x) > 1 and len(y) == len(x):
            # 
            # compute rms
            # 
            mask = np.full(y.shape, False, dtype=bool)
            mask_nonnan = ~np.isnan(y)
            count_all_pixels = np.count_nonzero(mask_nonnan)
            count_masked_pixels = 0
            data_mean_from_last_iteration = np.nan
            data_std_from_last_iteration = np.nan
            count_iteration = 0
            variation_between_iteration = 1.0 # percent
            while (count_iteration == 0) or \
                  (count_iteration < 500 and count_masked_pixels < count_all_pixels and variation_between_iteration > 1e-3):
                count_iteration += 1
                data_mean = np.nanmean(y[~mask])
                data_std = np.nanstd(y[~mask] - data_mean)
                mask[mask_nonnan] = np.logical_or(mask[mask_nonnan], y[mask_nonnan] > data_mean+3.0*data_std)
                mask[~mask_nonnan] = False
                count_masked_pixels = np.count_nonzero(mask)
                if not np.isnan(data_mean_from_last_iteration):
                    variation_between_iteration = np.abs(data_mean - data_mean_from_last_iteration)/data_mean_from_last_iteration
                print('Iteration %d, data mean = %0.3e (changed %.1f%%), data std = %0.3e, mask pixel count = %d (%.1f%%)'%(count_iteration, data_mean, variation_between_iteration*100., data_std, count_masked_pixels, count_masked_pixels/count_all_pixels*100.))
                # prepare for next iteration
                data_mean_from_last_iteration = data_mean
                data_std_from_last_iteration = data_std
            # 
            # find starting channel
            starting_frequency = input_start_freq
            starting_channel = np.argwhere(np.abs(x-starting_frequency) == np.min(np.abs(x-starting_frequency))).flatten()[0]
            print('starting_frequency = %s (GHz)'%(starting_frequency))
            print('starting_channel = %s (0-based)'%(starting_channel))
            lower_channel = starting_channel
            upper_channel = starting_channel
            greedy_mode = False
            while lower_channel-1 >= 0:
                # 
                lower_channel -= 1
                # 
                print('chan %s (0-based), y = %s'%(lower_channel, y[lower_channel]))
                if not np.isnan(y[lower_channel]):
                    if greedy_mode == False:
                        # compute moving mean, if this hits the mean value, turn on greedy mode
                        if moving_mean(y, lower_channel, -3) < data_mean_from_last_iteration:
                            greedy_mode = True
                    if greedy_mode == True:
                        # on greedy mode, we expand any consequent channel above mean, while break when it hits mean
                        if y[lower_channel] < data_mean_from_last_iteration:
                            lower_channel += 1 # fallback one channel as this is already below mean
                            break
                    #if y[lower_channel-1] < data_mean_from_last_iteration:
                    #    # if two consequent channels fall below mean value, 
                    #    # or one and the one after next one are below mean value, 
                    #    # then break
                    #    if lower_channel-2 >= 0:
                    #        if y[lower_channel-2] < data_mean_from_last_iteration:
                    #            break # two consequent channels fall below mean value, 
                    #        elif lower_channel-3 >= 0:
                    #            if y[lower_channel-3] < data_mean_from_last_iteration:
                    #                break # three channels, two are below mean value
                # 
                #lower_channel -= 1
            # 
            greedy_mode = False
            while upper_channel+1 < len(x):
                # 
                upper_channel += 1
                # 
                print('chan %s (0-based), y = %s'%(upper_channel, y[upper_channel]))
                if not np.isnan(y[upper_channel]):
                    if greedy_mode == False:
                        # compute moving mean, if this hits the mean value, turn on greedy mode
                        if moving_mean(y, upper_channel, +3) < data_mean_from_last_iteration:
                            greedy_mode = True
                    if greedy_mode == True:
                        # on greedy mode, we expand any consequent channel above mean, while break when it hits mean
                        if y[upper_channel] < data_mean_from_last_iteration:
                            upper_channel -= 1 # fallback one channel as this is already below mean
                            break
                    #if y[upper_channel+1] < data_mean_from_last_iteration:
                    #    # if two consequent channels fall below mean value, 
                    #    # or one and the one after next one are below mean value, 
                    #    # then break
                    #    if upper_channel+2 < len(x):
                    #        if y[upper_channel+2] < data_mean_from_last_iteration:
                    #            break # two consequent channels fall below mean value, 
                    #        elif upper_channel+3 < len(x):
                    #            if y[upper_channel+3] < data_mean_from_last_iteration:
                    #                break # three channels, two are below mean value
                # 
                #upper_channel += 1
            # 
            if lower_channel < 0:
                lower_channel = 0
            if upper_channel >= len(x):
                upper_channel = len(x)-1
            print(lower_channel+1, upper_channel+1, '(expanded channel range)')
            output_lower_freq = x[lower_channel]
            output_upper_freq = x[upper_channel]



# 
print(output_lower_freq, output_upper_freq)









