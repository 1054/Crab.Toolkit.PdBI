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

if len(sys.argv) <= 1:
    print('Usage: ')
    print('    pdbi_uvt_go_plot_uvfit_result_spectrum_with_python.py *.result.obj_1.txt [-output output_name] [-figwidth 20] [-line-name XXX -rest-freq XXX -redshift XXX]')
    print('')
    sys.exit()

# 
# extrap1d -- from https://stackoverflow.com/questions/2745329/how-to-make-scipy-interpolate-give-an-extrapolated-result-beyond-the-input-range
def extrap1d(interpolator):
    xs = interpolator.x
    ys = interpolator.y
    def pointwise(x):
        if x < xs[0]:
            return ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
        elif x > xs[-1]:
            return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
        else:
            return interpolator(x)
    def ufunclike(xs):
        return numpy.array(map(pointwise, numpy.array(xs)))
    return ufunclike

# 
# getbaseline
def getbaseline(x_baseline, input_continuum):
    if len(input_continuum) >= 4:
        y_baseline = extrap_continuum(x_baseline)
    elif len(input_continuum) == 2:
        y_baseline = numpy.array(x_baseline)*0.0 + input_continuum[1]
    elif len(input_continuum) == 1:
        y_baseline = numpy.array(x_baseline)*0.0 + input_continuum[0]
    else:
        y_baseline = numpy.array(x_baseline)*0.0
    return y_baseline



# 
# Read user input file names
input_names = []
output_name = ''
input_redshift = 0.0 
input_linename = []
input_linefreq = [] # rest-frame
input_lineFWHM = [] # km/s
input_clip_sigma = 0.0
set_figure_size = [12.0,5.0]
set_no_errorbar = False
set_no_liblines = False
set_xrange = []
set_yrange = []
set_highlight_frange = []
set_xtickinterval = numpy.nan
set_ytickinterval = numpy.nan
set_xtitlefontsize = 16
set_ytitlefontsize = 16
set_xtickfontsize = 14
set_ytickfontsize = 14
set_plot_title = ''
set_plot_title_pad = 3
set_plot_title_fontsize = 16
set_plot_text_fontsize = 13
set_line_label_fontsize = [] # same dimension as input_linename <TODO>
set_plot_margin_top = None
set_plot_margin_bottom = None
set_plot_margin_left = None
set_plot_margin_right = None
input_continuum = []

lib_linefreq = [115.2712018, 230.538, 345.7959899, 461.0407682, 576.2679305, 691.4730763, 806.651806, 921.7997, 1036.912393, 1151.985452, 1267.014486, 1381.995105, 1496.922909]
lib_linename = ['CO(1-0)', 'CO(2-1)', 'CO(3-2)', 'CO(4-3)', 'CO(5-4)', 'CO(6-5)', 'CO(7-6)', 'CO(8-7)', 'CO(9-8)', 'CO(10-9)', 'CO(11-10)', 'CO(12-11)', 'CO(13-12)']
lib_linefreq.extend([492.16065,809.34197])
lib_linename.extend(['[CI](1-0)','[CI](2-1)'])
lib_linefreq.extend([556.93599,1113.34301,987.92676,752.03314,1669.90477,1228.78872,1661.00764,1716.76963,1153.12682,1097.36479,1162.91160,1919.35953,1893.68651,1602.21937,916.17158,1207.63873,1410.61807])
lib_linename.extend(['H2O(110-101)','H2O(111-000)','H2O(202-111)','H2O(211-202)','H2O(212-101)','H2O(220-211)','H2O(221-212)','H2O(302-212)','H2O(312-221)','H2O(312-303)','H2O(321-312)','H2O(322-313)','H2O(331-404)','H2O(413-404)','H2O(422-331)','H2O(422-413)','H2O(523-514)'])
lib_linefreq.extend([1900.53690,1461.13141,2459.38010])
lib_linename.extend(['[CII](1-0)','[NII](1-0)','[NII](2-1)']) # CII158, NII205, NII122
#lib_linefreq.extend([3393.00624,5785.87959])
#lib_linename.extend(['[OIII](1-0)','[OIII](2-1)']) # OIII88, OIII51

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
    elif temp_argv == '-linewidth' or temp_argv == '-line-width' or \
         temp_argv == '-linefwhm' or temp_argv == '-line-fwhm' or \
         temp_argv == '-linefwzi' or temp_argv == '-line-fwzi':
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
    elif temp_argv == '-plot-ytick-interval' or temp_argv == '-ytickinterval':
        if i+1 < len(sys.argv):
            i = i + 1
            set_ytickinterval = float(sys.argv[i])
    elif temp_argv == '-plot-xtick-fontsize' or temp_argv == '-xtickfontsize':
        if i+1 < len(sys.argv):
            i = i + 1
            set_xtickfontsize = float(sys.argv[i])
    elif temp_argv == '-plot-ytick-fontsize' or temp_argv == '-ytickfontsize':
        if i+1 < len(sys.argv):
            i = i + 1
            set_ytickfontsize = float(sys.argv[i])
    elif temp_argv == '-plot-xtitle-fontsize' or temp_argv == '-xtitlefontsize':
        if i+1 < len(sys.argv):
            i = i + 1
            set_xtitlefontsize = float(sys.argv[i])
    elif temp_argv == '-plot-ytitle-fontsize' or temp_argv == '-ytitlefontsize':
        if i+1 < len(sys.argv):
            i = i + 1
            set_ytitlefontsize = float(sys.argv[i])
    elif temp_argv == '-plot-yrange' or temp_argv == '-set-ylim' or temp_argv == '-yrange' or temp_argv == '-ylim':
        if i+2 < len(sys.argv):
            i = i + 1
            set_yrange.append(float(sys.argv[i]))
            i = i + 1
            set_yrange.append(float(sys.argv[i]))
    elif temp_argv == '-plot-xrange' or temp_argv == '-set-xlim' or temp_argv == '-xrange' or temp_argv == '-xlim':
        if i+2 < len(sys.argv):
            i = i + 1
            set_xrange.append(float(sys.argv[i]))
            i = i + 1
            set_xrange.append(float(sys.argv[i]))
    elif temp_argv == '-plot-title' or temp_argv == '-title':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_title = sys.argv[i]
    elif temp_argv == '-plot-title-padding' or temp_argv == '-title-pad':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_title_pad = float(sys.argv[i])
    elif temp_argv == '-plot-title-fontsize' or temp_argv == '-title-fontsize':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_title_fontsize = float(sys.argv[i])
    elif temp_argv == '-plot-margin-top':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_margin_top = float(sys.argv[i])
    elif temp_argv == '-plot-margin-bottom':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_margin_bottom = float(sys.argv[i])
    elif temp_argv == '-plot-margin-left':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_margin_left = float(sys.argv[i])
    elif temp_argv == '-plot-margin-right':
        if i+1 < len(sys.argv):
            i = i + 1
            set_plot_margin_right = float(sys.argv[i])
    elif temp_argv == '-clip-sigma' or temp_argv == '-sigma-clip':
        if i+1 < len(sys.argv):
            i = i + 1
            input_clip_sigma = float(sys.argv[i])
            print('input_clip_sigma = %s'%(input_clip_sigma))
    elif temp_argv == '-continuum':
        # should be either one value
        # or pairs of values
        j = i + 1
        while j < len(sys.argv):
            try:
                float(sys.argv[j])
                input_continuum.append(float(sys.argv[j]))
            except:
                break
            i = j
            j += 1
        # 
    #elif temp_argv == '-plot-line-label-fontsize' or temp_argv == '-line-label-fontsize':
    #    if i+1 < len(sys.argv):
    #        i = i + 1
    #        while len(set_line_label_fontsize) < len(input_linename):
    #            # make sure set_line_label_fontsize has the same dimension as input_linename
    #        set_line_label_fontsize = float(sys.argv[i])
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
if len(input_linename) > 0:
    if len(input_linefreq) == 0:
        for kk in range(len(input_linename)):
            if input_linename[kk] != '':
                jkk = []
                for ikk in range(len(lib_linename)):
                    if lib_linename[ikk] == input_linename[kk]:
                        jkk.append(ikk)
                #jkk = numpy.argwhere(lib_linename == input_linename[kk]).flatten().tolist()
                #print(jkk)
                if len(jkk) > 0:
                    input_linefreq.append(lib_linefreq[jkk[0]])
                else:
                    print('Error! Could not find line name "%s" in our library! Please input its rest-frequency in GHz with the "-linefreq" option!'%(input_linename[kk]))
                    sys.exit()
# 
# Check input input_continuum
if len(input_continuum) > 0:
    print('input_continuum: %s'%(input_continuum))
    if len(input_continuum) >= 2 and len(input_continuum) % 2 != 0:
        input_continuum = input_continuum[:-1]
    if len(input_continuum) >= 4:
        interp_continuum = interpolate.interp1d(input_continuum[::2], input_continuum[1:][::2])
        extrap_continuum = extrap1d(interp_continuum) # see https://stackoverflow.com/questions/2745329/how-to-make-scipy-interpolate-give-an-extrapolated-result-beyond-the-input-range
        

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
    #input_table = Table.read(input_name, format='ascii.commented_header')
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
        # Find out invalid data with '***'
        invalid_mask = [True if '*' in str(t) else False for t in input_table['freq']]
        if numpy.count_nonzero(invalid_mask) > 0:
            input_table['freq'][invalid_mask] = 'NaN'
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
            # clip sigma
            if input_clip_sigma > 0.0:
                y_rms = numpy.std(y)
                sig_mask = (numpy.abs(y)-numpy.median(y) <= input_clip_sigma*y_rms)
                x = x[sig_mask]
                y = y[sig_mask]
                if yerr is not None: yerr = yerr[sig_mask]
                if SNR is not None: SNR = SNR[sig_mask]
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
                sum_highlights = 0.0
                cnt_highlights = 0.0
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
                                    sum_highlights+=y[j]
                                    cnt_highlights+=1
                    # 
                    # highlight by input_lineFWHM
                    if len(input_linefreq) > 0:
                        for kk in range(len(input_linefreq)):
                            if len(input_lineFWHM) == 0:
                                input_lineFWHM = [500.0] #<20181128># bug fixed. 
                            if kk >= len(input_lineFWHM):
                                input_lineFWHM.append(input_lineFWHM[-1])
                            if input_lineFWHM[kk] > 0:
                                if numpy.abs(x[j] / (input_linefreq[kk]/(1.0+input_redshift)) - 1.0) * 2.99792458e5 <= input_lineFWHM[kk] / 2.0:
                                    x_highlights.append([x[j]-x_left_width[j],x[j]+x_right_width[j]])
                                    y_highlights.append([y[j],y[j]])
                                    sum_highlights+=y[j]
                                    cnt_highlights+=1
                                    #print('highlighting input spectral line %d between %0.6f and %0.6f GHz'%(kk+1,x[j]-x_left_width[j],x[j]+x_right_width[j]))
                                #x_highlights.append([(1.0-input_lineFWHM[kk]/2.99792458e5)*input_linefreq[kk]/(1.0+input_redshift)-x_left_width[j],
                                #                     (1.0+input_lineFWHM[kk]/2.99792458e5)*input_linefreq[kk]/(1.0+input_redshift)+x_right_width[j]])
                                #y_highlights.append([y[j],y[j]])
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
                #print(list(zip(x_plot, y_plot)))
                spec_plot = ax.errorbar(x_plot, y_plot, linestyle='-', color='blue', alpha=1.0, linewidth=linewidth) # color='#1e90ff'
                global_spec_list.append(spec_plot)
                global_x_arr.extend(x) # add to global_x_arr
                global_y_arr.extend(y) # add to global_y_arr
                # 
                # highlight specific channels
                for k in range(len(x_highlights)):
                    x_baseline = x_highlights[k]
                    y_baseline = getbaseline(x_baseline, input_continuum)
                    ax.fill_between(x_highlights[k], y_highlights[k], y_baseline, color='gold', alpha=0.5)
                # 
                # label sum_highlights
                if cnt_highlights > 0:
                    ax.text(0.01, 0.22, 'sum of highlighted channels: %0.6g'%(sum_highlights), transform=ax.transAxes, fontsize=set_plot_text_fontsize)
                    ax.text(0.01, 0.16, 'avg of highlighted channels: %0.6g'%(sum_highlights/cnt_highlights), transform=ax.transAxes, fontsize=set_plot_text_fontsize)
                    ax.text(0.01, 0.10, 'channel velocity resolution: %0.6g'%(numpy.abs(x[1]-x[0])/numpy.abs(x[0])*2.99792458e5), transform=ax.transAxes, fontsize=set_plot_text_fontsize)
                    print('sum of highlighted channels = %0.6g'%(sum_highlights))
                    print('avg of highlighted channels = %0.6g'%(sum_highlights/cnt_highlights))
                    print('channel velocity resolution = %0.5f'%(numpy.abs(x[1]-x[0])/numpy.abs(x[0])*2.99792458e5))
                    
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
                    errorbar_plot = ax.errorbar(x, y, yerr=yerr, linestyle='none', capsize=capsize, color='blue', alpha=0.9, linewidth=linewidth/2.0) # color='#1e90ff'

global_y_rms = numpy.std(global_y_arr)
print('global channel rms = %0.6g'%(global_y_rms))
ax.text(0.01, 0.04, 'global channel rms: %0.6g'%(global_y_rms), transform=ax.transAxes, fontsize=set_plot_text_fontsize)

print('global_x_min = ', global_x_min)
print('global_x_max = ', global_x_max)
baseline_x = numpy.linspace(global_x_min-0.1*(global_x_max-global_x_min), global_x_max+0.1*(global_x_max-global_x_min), num=100, endpoint=True)
baseline_y = getbaseline(baseline_x, input_continuum)
ax.plot(baseline_x, 
        baseline_y, 
        linewidth=1, color='k')
# 
# x y range
# 
if len(set_xrange) == 2:
    ax.set_xlim(set_xrange)
if len(set_yrange) == 2:
    ax.set_ylim(set_yrange)
global_y_min, global_y_max = ax.get_ylim()



# 
# adjust plot line thickness
for spec_plot in global_spec_list:
    # see https://matplotlib.org/api/container_api.html#matplotlib.container.ErrorbarContainer
    spec_plot_data_line, spec_plot_caplines, spec_plot_barlinecols = spec_plot
    spec_plot_data_line.set_linewidth(global_linewidth)
    for spec_plot_capline in spec_plot_caplines: 
        spec_plot_capline.set_linewidth(global_linewidth)
        #spec_plot_capline.markersize = global_capsize #<TODO>#
        #print(spec_plot_capline.markersize)


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
if ~numpy.isnan(set_ytickinterval):
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=set_ytickinterval))
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(base=set_ytickinterval/10.0))
ax.tick_params(axis='both', which='both', direction='in')
ax.grid(True, ls='dotted', lw=0.8, color='darkgray')
plt.xticks(fontsize=set_xtickfontsize)
plt.yticks(fontsize=set_ytickfontsize)
plt.xlabel('Observing Frequency', fontsize=set_xtitlefontsize)
plt.ylabel('Flux Density', fontsize=set_ytitlefontsize)
if set_plot_title != '':
    title_plot = set_plot_title
else:
    title_plot = os.path.basename(input_names[0])
    if len(input_names)>1:
        title_plot = title_plot + ' and %d files'%(len(input_names)-1)
plt.title(title_plot, fontsize = set_plot_title_fontsize) # , pad = set_plot_title_pad <TODO>

# 
# adjust margin
if set_plot_margin_top is not None or \
   set_plot_margin_bottom is not None or \
   set_plot_margin_left is not None or \
   set_plot_margin_right is not None:
    plt.subplots_adjust(bottom=set_plot_margin_bottom, top=1.0-set_plot_margin_top, left=set_plot_margin_left, right=1.0-set_plot_margin_right)
else:
    plt.tight_layout()


# 
# Annotate lines
# (must after tight_layout()
loop_linefreq = []
loop_linename = []
if set_no_liblines:
    loop_linefreq = input_linefreq
    loop_linename = input_linename
else:
    # append library lines
    if len(input_linefreq) > 0:
        loop_linefreq.extend(input_linefreq)
    if len(input_linename) > 0:
        loop_linename.extend(input_linename)
    loop_linefreq.extend(lib_linefreq)
    loop_linename.extend(lib_linename)
# 
# 
for j in range(len(loop_linefreq)):
    linefreq = loop_linefreq[j] / (1.0+input_redshift) # obs-frame frequency
    if j < len(loop_linename):
        linename = loop_linename[j]
    else:
        linename = 'Line at %0.3f GHz'%(linefreq)
    if (linefreq >= global_x_min and linefreq <= global_x_max) or True:
        if linename.startswith('H2O'):
            fontsize = 8
            color = 'seagreen'
            yshift = 0.05
        elif linename.startswith('[CI]'):
            fontsize = 8
            color = 'magenta'
            yshift = 0.1
        else:
            fontsize = None
            color = None
            yshift = 0.0
        # annotate the line
        lineheight = global_y_arr[numpy.argsort(numpy.abs(numpy.array(global_x_arr)-linefreq))[0]]
        if lineheight < 0:
            lineheight = -lineheight
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
# Save figure
plt.savefig(output_name)
print('Output to "%s"!'%(output_name))






