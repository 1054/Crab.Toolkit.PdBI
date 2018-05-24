#!/usr/bin/env python
# 

import os, sys, numpy, matplotlib, astropy
import astropy.io.ascii as asciitable
import matplotlib.pyplot as plt

if len(sys.argv) <= 1:
    print('Usage: ')
    print('    pdbi_uvt_go_plot_uvfit_result_spectrum_with_python.py *.result.obj_1.txt [-output output_name]')
    print('')
    sys.exit()


# 
# Read user input file names
input_names = []
output_name = ''
set_no_errorbar = False

i = 1
while i < len(sys.argv):
    temp_argv = sys.argv[i].lower()
    if temp_argv.find('--') == 0:
        temp_argv = '-'+temp_argv.lstrip('-')
    if temp_argv == '-out' or temp_argv == '-output':
        if i+1 < len(sys.argv):
            i = i + 1
            output_name = sys.argv[i]
    elif temp_argv == '-no-errorbar' or temp_argv == '-noerrorbar':
        set_no_errorbar = True
    else:
        input_names.append(sys.argv[i])
    i = i + 1

# 
# Check input_name
if input_names == []:
    print('Error! Failed to read data table names from user input!')
    sys.exit()

# 
# Set default output_name if not given
if output_name == '':
    input_name = input_names[0]
    input_basename, input_extension = os.path.splitext(input_name)
    output_name = input_basename + '.spectrum.pdf'
else:
    if not output_name.endswith('.pdf') or output_name.endswith('.PDF'):
        output_name = output_name + '.pdf'



# 
# Make plot
fig = plt.figure(figsize=(12.0,5.0), dpi=90)  # set figure size 12.0 x 5.0 inches, 90 pixels per inch. 

ax = fig.add_subplot(1,1,1)

global_x_min = numpy.nan
global_x_max = numpy.nan


# 
# For each input file
for i in range(len(input_names)):
    # 
    # Input_name
    input_name = input_names[i]
    # 
    # Read input data table
    input_table = asciitable.read(input_name)
    #input_table_header = asciitable.read(input_name, data_start = 0, data_end = 1)
    #print(input_table_header)
    # 
    # Read x y
    x = None
    y = None
    yerr = None
    SNR = None
    if 'freq' in input_table.colnames:
        x = numpy.array(input_table['freq'])
    if 'frequency' in input_table.colnames:
        x = numpy.array(input_table['frequency'])
    if 'flux' in input_table.colnames:
        y = numpy.array(input_table['flux'])
    if 'flux_err' in input_table.colnames:
        yerr = numpy.array(input_table['flux_err'])
    if 'SNR' in input_table.colnames:
        SNR = numpy.array(input_table['SNR'])
        SNR_mask = (numpy.isnan(SNR)) # excluding NaN
        if x is not None: x[SNR_mask] = numpy.nan
        if y is not None: y[SNR_mask] = numpy.nan
        if yerr is not None: yerr[SNR_mask] = numpy.nan
    # 
    # Make plot
    if x is not None and y is not None:
        # 
        # check array size
        if len(x) > 1 and len(y) == len(x):
            # 
            # nonnan
            nan_mask = (~numpy.isnan(x)) & (~numpy.isnan(y))
            nan_iarg = numpy.argwhere(nan_mask)
            x = x[nan_mask]
            y = y[nan_mask]
            if yerr is not None: yerr = yerr[nan_mask]
            if SNR is not None: SNR = SNR[nan_mask]
            # 
            # check array size
            if len(x) > 1 and len(y) == len(x):
                # 
                # sort
                sort_iarg = numpy.argsort(x)
                x = x[sort_iarg]
                y = y[sort_iarg]
                if yerr is not None: yerr = yerr[sort_iarg]
                if SNR is not None: SNR = SNR[sort_iarg]
                #print('')
                #asciitable.write((x,y,yerr,SNR), sys.stdout, Writer=asciitable.FixedWidthTwoLine, names=['x','y','yerr','SNR'])
                # 
                # determine first and last valid data, and global xmin xmax
                j_first = -1
                j_last = -1
                for j in range(len(x)):
                    if j_first < 0:
                        j_first = j # determine first and last valid data
                    j_last = j # determine first and last valid data
                    if numpy.isnan(global_x_min):
                        global_x_min = x[j]
                    elif x[j] < global_x_min:
                        global_x_min = x[j]
                    if numpy.isnan(global_x_max):
                        global_x_max = x[j]
                    elif x[j] > global_x_max:
                        global_x_max = x[j]
                #print('j_first = ', j_first)
                #print('j_last = ', j_last)
                # 
                # left and right side width
                x_left_width = [(x[j]-x[j-1])/2.0 for j in numpy.arange(1,len(x))]
                x_right_width = [(x[j+1]-x[j])/2.0 for j in numpy.arange(0,len(x)-1)]
                x_left_width.insert(0, x_left_width[0])
                x_right_width.append(x_right_width[len(x_right_width)-1])
                x_left_width = numpy.array(x_left_width)
                x_right_width = numpy.array(x_right_width)
                # 
                # prepare variables of connected points 
                x_plot = []
                y_plot = []
                # 
                # draw connect points 
                for j in range(len(x)):
                    #print(x[j])
                    if j == j_first:
                        x_plot.append(x[j]-x_left_width[j])
                        y_plot.append(0.0)
                        has_first = True
                    x_plot.append(x[j]-x_left_width[j])
                    y_plot.append(y[j])
                    x_plot.append(x[j]+x_right_width[j])
                    y_plot.append(y[j])
                    if j == j_last:
                        x_plot.append(x[j]+x_right_width[j])
                        y_plot.append(0.0)
                # 
                #ax.bar(x, y, width=2.0*x_left_width, align='center', fill=False, edgecolor='#1e90ff', alpha=1.0)
                ax.errorbar(x_plot, y_plot, linestyle='-', color='blue', alpha=1.0) # color='#1e90ff'
                # 
                # capsize
                capsize = 120/len(x)
                if capsize > 12:
                    capsize = 12
                if capsize < 0.25:
                    capsize = 0.25
                # 
                if yerr is not None and not set_no_errorbar:
                    ax.errorbar(x, y, yerr=yerr, linestyle='none', capsize=12, color='blue', alpha=0.9) # color='#1e90ff'

print('global_x_min = ', global_x_min)
print('global_x_max = ', global_x_max)
ax.plot([global_x_min-0.1*(global_x_max-global_x_min), global_x_max+0.1*(global_x_max-global_x_min)], [0.0, 0.0], linewidth=1, color='k')

# 
# xy label
#plt.grid(True)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlabel('Observing Frequency', fontsize=16)
plt.ylabel('Flux Density', fontsize=16)
title_plot = os.path.basename(input_names[0])
if len(input_names)>1:
    title_plot = title_plot + ' and %d files'%(len(input_names)-1)
plt.title(title_plot, fontsize=16)

# 
# Save figure
plt.savefig(output_name)
print('Output to "%s"!'%(output_name))






