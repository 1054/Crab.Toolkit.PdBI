#!/usr/bin/env python
# 

import os, sys, numpy, matplotlib, astropy
import astropy.io.ascii as asciitable
import matplotlib.pyplot as plt

if len(sys.argv) <= 1:
    print('Usage: ')
    print('    pdbi_uvt_go_plot_uvfit_result_spectrum_with_python.py *.result.obj_1.txt [-output output_name] [-figwidth 20] [-line-name XXX -rest-freq XXX -redshift XXX]')
    print('')
    sys.exit()


# 
# Read user input file names
input_names = []
output_name = ''
input_redshift = 0.0 
input_linename = []
input_linefreq = [] # rest-frame
input_lineFWHM = [] # km/s
set_figure_size = [12.0,5.0]
set_no_errorbar = False
set_no_liblines = False
set_highlight_frange = []
set_xtickinterval = numpy.nan

lib_linefreq = [115.2712018, 230.538, 345.7959899, 461.0407682, 576.2679305, 691.4730763, 806.651806, 921.7997, 1036.912393, 1151.985452, 1267.014486, 1381.995105, 1496.922909]
lib_linename = ['CO(1-0)', 'CO(2-1)', 'CO(3-2)', 'CO(4-3)', 'CO(5-4)', 'CO(6-5)', 'CO(7-6)', 'CO(8-7)', 'CO(9-8)', 'CO(10-9)', 'CO(11-10)', 'CO(12-11)', 'CO(13-12)']
lib_linefreq.extend([492.16065,809.34197])
lib_linename.extend(['[CI](1-0)','[CI](2-1)'])
lib_linefreq.extend([556.93599,1113.34301,987.92676,752.03314,1669.90477,1228.78872,1661.00764,1716.76963,1153.12682,1097.36479,1162.91160,1919.35953,1893.68651,1602.21937,916.17158,1207.63873,1410.61807])
lib_linename.extend(['H2O(110-101)','H2O(111-000)','H2O(202-111)','H2O(211-202)','H2O(212-101)','H2O(220-211)','H2O(221-212)','H2O(302-212)','H2O(312-221)','H2O(312-303)','H2O(321-312)','H2O(322-313)','H2O(331-404)','H2O(413-404)','H2O(422-331)','H2O(422-413)','H2O(523-514)'])

i = 1
while i < len(sys.argv):
    temp_argv = sys.argv[i].lower()
    if temp_argv.find('--') == 0:
        temp_argv = '-'+temp_argv.lstrip('-')
    elif temp_argv == '-out' or temp_argv == '-output':
        if i+1 < len(sys.argv):
            i = i + 1
            output_name = sys.argv[i]
    elif temp_argv == '-z' or temp_argv == '-redshift':
        if i+1 < len(sys.argv):
            i = i + 1
            input_redshift = float(sys.argv[i])
    elif temp_argv == '-linefreq' or temp_argv == '-line-freq' or temp_argv == '-rest-freq':
        if i+1 < len(sys.argv):
            i = i + 1
            input_linefreq.append(float(sys.argv[i]))
    elif temp_argv == '-linename' or temp_argv == '-line-name':
        if i+1 < len(sys.argv):
            i = i + 1
            input_linename.append(sys.argv[i])
    elif temp_argv == '-linewidth' or temp_argv == '-line-name':
        if i+1 < len(sys.argv):
            i = i + 1
            input_lineFWHM.append(float(sys.argv[i]))
    elif temp_argv == '-plot-width' or temp_argv == '-fig-width' or temp_argv == '-figwidth':
        if i+1 < len(sys.argv):
            i = i + 1
            set_figure_size[0] = float(sys.argv[i])
    elif temp_argv == '-plot-height' or temp_argv == '-fig-height' or temp_argv == '-figheight':
        if i+1 < len(sys.argv):
            i = i + 1
            set_figure_size[1] = float(sys.argv[i])
    elif temp_argv == '-plot-size' or temp_argv == '-fig-size' or temp_argv == '-figsize':
        if i+2 < len(sys.argv):
            i = i + 1
            set_figure_size[0] = float(sys.argv[i])
            i = i + 1
            set_figure_size[1] = float(sys.argv[i])
    elif temp_argv == '-plot-xtick-interval' or temp_argv == '-xtickinterval':
        if i+1 < len(sys.argv):
            i = i + 1
            set_xtickinterval = float(sys.argv[i])
    elif temp_argv == '-highlight-freq' or temp_argv == '-highlight-frange' or temp_argv == '-frange':
        if i+2 < len(sys.argv):
            i = i + 1
            if float(sys.argv[i+1]) >= float(sys.argv[i]):
                set_highlight_frange.append(float(sys.argv[i]))
                set_highlight_frange.append(float(sys.argv[i+1]))
            else:
                set_highlight_frange.append(float(sys.argv[i+1]))
                set_highlight_frange.append(float(sys.argv[i]))
            i = i + 1
    elif temp_argv == '-no-errorbar' or temp_argv == '-noerrorbar':
        set_no_errorbar = True
    elif temp_argv == '-no-lib-lines' or temp_argv == '-no-liblines' or temp_argv == '-noliblines':
        set_no_liblines = True
    else:
        input_names.append(sys.argv[i])
    i = i + 1

# 
# Check input_name
if input_names == []:
    print('Error! Failed to read data table names from user input!')
    sys.exit()

# Check input_linename, input_linefreq and input_lineFWHM
#input_check = True
#input_count = max([len(input_linename), len(input_linefreq), len(input_lineFWHM)])
#if len(input_linename) > 0:
#    if len(input_linefreq) > 0:
#        if len(input_linefreq) != len(input_linename):
#            print('Error! The input_linefreq and input_linename do not have the same dimension!')
#            input_check = False
#    if len(input_lineFWHM) > 0:
#        if len(input_lineFWHM) != len(input_linename):
#            print('Error! The input_lineFWHM and input_linename do not have the same dimension!')
#            input_check = False
#if input_check == False:
#    sys.exit()

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
fig = plt.figure(figsize=set_figure_size, dpi=90)  # set figure size 12.0 x 5.0 inches, 90 pixels per inch. 

ax = fig.add_subplot(1,1,1)

global_x_min = numpy.nan
global_x_max = numpy.nan
global_x_arr = []
global_y_arr = []
global_linewidth = 2.0
global_capsize = 12.0
global_spec_list = []


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
        x = numpy.array(input_table['freq']).astype(float)
    if 'frequency' in input_table.colnames:
        x = numpy.array(input_table['frequency']).astype(float)
    if 'flux' in input_table.colnames:
        y = numpy.array(input_table['flux']).astype(float)
    if 'flux_err' in input_table.colnames:
        yerr = numpy.array(input_table['flux_err']).astype(float)
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
                x_highlights = []
                y_highlights = []
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
                    # highlight freq    
                    if len(set_highlight_frange) > 0:
                        for k in range(0,len(set_highlight_frange),2):
                            if k+1 < len(set_highlight_frange):
                                if x[j]-x_left_width[j] >= set_highlight_frange[k] and x[j]+x_right_width[j] <= set_highlight_frange[k+1]:
                                    x_highlights.append([x[j]-x_left_width[j],x[j]+x_right_width[j]])
                                    y_highlights.append([y[j],y[j]])
                    # 
                    # highlight by input_lineFWHM
                    if len(input_linefreq) > 0:
                        for kk in range(len(input_linefreq)):
                            if kk >= len(input_lineFWHM):
                                input_lineFWHM.append(input_lineFWHM[-1])
                            if input_lineFWHM[kk] > 0:
                                x_highlights.append([(1.0-input_lineFWHM[kk]/2.99792458e9)*input_linefreq[kk]/(1.0+input_redshift)-x_left_width[j],
                                                     (1.0+input_lineFWHM[kk]/2.99792458e9)*input_linefreq[kk]/(1.0+input_redshift)+x_right_width[j]])
                                y_highlights.append([y[j],y[j]])
                # 
                linewidth = 100.0/len(x) # plotting line thickness
                if linewidth > 1.0:
                    linewidth = 1.0
                if global_linewidth > linewidth:
                    global_linewidth = linewidth
                #print('dataset %d len(x) = %s'%(i+1, len(x)))
                #print('dataset %d linewidth = %s'%(i+1, linewidth))
                # 
                #ax.bar(x, y, width=2.0*x_left_width, align='center', fill=False, edgecolor='#1e90ff', alpha=1.0)
                spec_plot = ax.errorbar(x_plot, y_plot, linestyle='-', color='blue', alpha=1.0, linewidth=linewidth) # color='#1e90ff'
                global_spec_list.append(spec_plot)
                global_x_arr.extend(x) # add to global_x_arr
                global_y_arr.extend(y) # add to global_y_arr
                # 
                # highlight specific channels
                for k in range(len(x_highlights)):
                    ax.fill_between(x_highlights[k], y_highlights[k], numpy.array(y_highlights[k])*0.0, color='gold', alpha=0.5)
                # 
                # capsize
                capsize = 120.0/len(x)
                if capsize > 12.0:
                    capsize = 12.0
                if capsize < 0.25:
                    capsize = 0.25
                if global_capsize > capsize:
                    global_capsize = capsize
                # 
                if yerr is not None and not set_no_errorbar:
                    ax.errorbar(x, y, yerr=yerr, linestyle='none', capsize=capsize, color='blue', alpha=0.9, linewidth=linewidth/2.0) # color='#1e90ff'


print('global_x_min = ', global_x_min)
print('global_x_max = ', global_x_max)
ax.plot([global_x_min-0.1*(global_x_max-global_x_min), global_x_max+0.1*(global_x_max-global_x_min)], [0.0, 0.0], linewidth=1, color='k')
global_y_min, global_y_max = ax.get_ylim()


# 
# Annotate lines
# 
if set_no_liblines:
    lib_linefreq = input_linefreq
    lib_linename = input_linename
else:
    if len(input_linefreq) > 0:
        lib_linefreq.extend(input_linefreq)
    if len(input_linename) > 0:
        lib_linename.extend(input_linename)
# 
for j in range(len(lib_linefreq)):
    linefreq = lib_linefreq[j] / (1.0+input_redshift)
    if j < len(lib_linename):
        linename = lib_linename[j]
    else:
        linename = 'Line at %0.3f GHz'%(linefreq)
    if (linefreq >= global_x_min and linefreq <= global_x_max) or True:
        if linename.startswith('H2O'):
            fontsize = 6
            color = 'seagreen'
            yshift = 0.05
        elif linename.startswith('[CI]'):
            fontsize = 6
            color = 'magenta'
            yshift = 0.1
        else:
            fontsize = None
            color = None
            yshift = 0.0
        # annotate the line
        lineheight = global_y_arr[numpy.argsort(numpy.abs(np.array(global_x_arr)-linefreq))[0]]
        ax.annotate(linename + '\n' + 'at %0.3f GHz'%(linefreq), 
                        xy=(linefreq,lineheight+0.02*(global_y_max-global_y_min)), # xy=(linefreq,global_y_max-0.2*(global_y_max-global_y_min)), # 
                        xycoords='data', 
                        xytext=(linefreq,global_y_max-0.01*(global_y_max-global_y_min)-yshift*(global_y_max-global_y_min)), 
                        ha='center', va='top', 
                        textcoords='data', 
                        arrowprops=dict(arrowstyle="->",relpos=(0.5,0.0)), #, connectionstyle="arc,angleA=0,armA=50,rad=10"
                        fontsize=fontsize, 
                        color=color, 
                    )
        print('annotating line %s at %s GHz'%(linename, linefreq))



# 
# adjust plot line thickness
for spec_plot in global_spec_list:
    # see https://matplotlib.org/api/container_api.html#matplotlib.container.ErrorbarContainer
    spec_plot_data_line, spec_plot_caplines, spec_plot_barlinecols = spec_plot
    spec_plot_data_line.set_linewidth(global_linewidth)
    for spec_plot_capline in spec_plot_caplines: 
        spec_plot_capline.set_linewidth(global_linewidth)
        #spec_plot_capline.markersize = global_capsize #<TODO>#
        print(spec_plot_capline.markersize)


# 
# xy label
if numpy.isnan(set_xtickinterval):
    set_xtickinterval2 = numpy.log10((global_x_max-global_x_min)/10.0)
    if set_xtickinterval2 > 0:
        set_xtickinterval = numpy.power(10, float(int(set_xtickinterval2)) )
    else:
        set_xtickinterval = numpy.power(10, float(int(set_xtickinterval2)-1) )
    set_xtickinterval = float(int((global_x_max-global_x_min)/10.0 / set_xtickinterval)) * set_xtickinterval
print('set_xtickinterval = %s'%(set_xtickinterval))
ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=set_xtickinterval))
ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(base=set_xtickinterval/10.0))
ax.tick_params(axis='both', which='both', direction='in')
plt.grid(True)
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






