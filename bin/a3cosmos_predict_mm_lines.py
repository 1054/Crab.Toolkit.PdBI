#!/usr/bin/env python
# 

from __future__ import print_function

# import python packages
import os, sys, json, time, re
import numpy as np

import astropy
import astropy.io.ascii as asciitable
from astropy.table import Table, Column

from copy import copy
from pprint import pprint
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter, LogLocator, MultipleLocator

#np.warnings.filterwarnings('ignore')
import warnings
warnings.filterwarnings('ignore')

sys.path.append('/Users/dzliu/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabpdbi')
from CrabPdBI import convert_Wavelength_um_to_Frequency_GHz, \
                    calc_radio_line_frequencies, \
                    find_radio_lines_in_frequency_range, \
                    calc_radio_line_flux_from_IR_luminosity

if sys.version_info.major <= 2:
    pass
else:
    long = int




def usage():
    print('Usgae: ')
    print('  a3cosmos_predict_mm_lines.py redshift IR_luminosity spectral_setups')
    print('Example:')
    print('  a3cosmos_predict_mm_lines.py 3.0 5e12 # we will list all CO Jup=1-7 and CII lines')
    print('  a3cosmos_predict_mm_lines.py 3.0 5e12 100.0 300.0 # we will only list lines within observed frame 100-300 GHz')
    print('  a3cosmos_predict_mm_lines.py 3.0 5e12 100.0 112.0 112.0 114.0 120.0 122.0 122.0 124.0 # similar as above but can input multiple pairs of frequency setups')




if __name__ == '__main__':
    # 
    # check user input
    if len(sys.argv) <= 1:
        usage()
        sys.exit()
    # 
    # print
    print('# Calculated by: ')
    print('#   "%s" %s'%(os.path.abspath(__file__), ' '.join(sys.argv[1:])))
    print('# CO are predicted based on CO-IR luminosity-luminosity correlations: ')
    print('#   CO J=1-0: Sargent et al. 2014; ')
    print('#   CO J=4-3 to 12-11: Liu et al. 2015; Daddi et al. 2015; ')
    print('#   CO J=2-1 and 3-2: interpolation of low-J and high-J CO predictions.')
    print('# ')
    # 
    # read user input
    source_redshift = np.nan
    IR_luminosity = np.nan
    spectral_setups = []
    i = 1
    while i < len(sys.argv):
        if np.isnan(source_redshift):
            source_redshift = float(sys.argv[i])
        elif np.isnan(IR_luminosity):
            IR_luminosity = float(sys.argv[i])
        else:
            spectral_setups.append(float(sys.argv[i]))
        i += 1
    # 
    # check user input
    if np.isnan(source_redshift) or np.isnan(IR_luminosity):
        usage()
        sys.exit()
    # 
    # save input
    z = source_redshift
    # 
    # set default value
    if len(spectral_setups) == 0:
        line_freqs, line_names = find_radio_lines_in_frequency_range([80.0, 850, 1461, 1462, 1900, 1901, 2060, 2061, 3393, 3394], Redshift=0.0, include_faint_lines = False)
    else:
        line_freqs, line_names = find_radio_lines_in_frequency_range(spectral_setups, Redshift=z, include_faint_lines = False)
    # 
    print('line_freqs and line_names: ', (line_freqs, line_names))
    # 
    # 
    # predict line flux
    for line_name in line_names:
        # 
        # predict line flux
        line_flux_prediction = calc_radio_line_flux_from_IR_luminosity(line_name, IR_luminosity, z, verbose=True) # TODO: IR_color = IR_color
        # 
        # 
        output_str = 'Line name %s, predicted flux %s Jy km s-1.'%(line_name, line_flux_prediction)
        print(output_str)
        print(''.join(map(lambda x: x*len(output_str), '-')))
    



