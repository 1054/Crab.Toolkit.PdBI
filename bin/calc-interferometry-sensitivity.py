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

np.warnings.filterwarnings('ignore')

sys.path.append(os.path.expanduser('~')+'/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabpdbi')
from CrabPdBI import calc_Sensitivity

if sys.version_info.major <= 2:
    pass
else:
    long = int




def usage():
    print('Usgae: ')
    print('  calc-interferometry-sensitivity.py -Tint XXXs -Frequency XXXGHz -Tsys XXXK')
    print('Example:')
    print('  calc-interferometry-sensitivity.py -Tint 30s -Frequency 160GHz -Telescope ALMA -Weather Winter -Velowidth 30km/s')
    print('  calc-interferometry-sensitivity.py -Tint 30s -Frequency 160GHz -Velowidth 30km/s -Tsys 120K -Velowidth 30km/s')
    print('  calc-interferometry-sensitivity.py ')




if __name__ == '__main__':
    # 
    # check user input
    if len(sys.argv) <= 1:
        usage()
        sys.exit()
    # 
    # read user input
    input_params = {}
    input_params['Tsys'] = np.nan
    input_params['Tint'] = np.nan
    input_params['Nant'] = 2 # in default one visibility means one baseline, two antennae
    input_params['Npol'] = 1
    input_params['Bandwidth'] = np.nan
    input_params['Velowidth'] = np.nan
    input_params['Frequency'] = np.nan
    input_params['Diameter'] = np.nan
    input_params['Telescope'] = ''
    input_params['Weather'] = ''
    input_params['eta_ap'] = 0.8
    i = 1
    while i < len(sys.argv):
        if sys.argv[i].startswith('-'):
            for key in input_params:
                if sys.argv[i].lower() == '-'+key.lower() or sys.argv[i].lower() == '--'+key.lower():
                    if i+1 < len(sys.argv):
                        i += 1
                        if type(input_params[key]) is str:
                            input_params[key] = sys.argv[i]
                        else:
                            if re.match(r'^[0-9.]+kHz$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('kHz',''))*1e6 # convert to GHz
                            if re.match(r'^[0-9.]+MHz$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('MHz',''))*1e3 # convert to GHz
                            elif re.match(r'^[0-9.]+GHz$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('GHz','')) # convert to GHz
                            elif re.match(r'^[0-9.]+s$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('s','')) # convert to seconds
                            elif re.match(r'^[0-9.]+m$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('m',''))*60.0 # convert to seconds
                            elif re.match(r'^[0-9.]+h$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('h',''))*3600.0 # convert to seconds
                            elif re.match(r'^[0-9.]+km/s$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('km/s',''))*3600.0 # convert to km/s
                            elif re.match(r'^[0-9.]+K$',sys.argv[i],re.IGNORECASE):
                                input_params[key] = float(sys.argv[i].replace('K',''))*3600.0 # convert to Kelvin
                            else:
                                input_params[key] = float(sys.argv[i])
            
        i += 1
    # 
    # check user input
    print(input_params)
    if not (\
            (~np.isnan(input_params['Tint']) and ~np.isnan(input_params['Frequency']) and ~np.isnan(input_params['Tsys']) and ~np.isnan(input_params['Diameter'])) or \
            (~np.isnan(input_params['Tint']) and ~np.isnan(input_params['Frequency']) and ''!=input_params['Telescope'] and ''!=input_params['Weather']) \
        ):
        usage()
        sys.exit()
    # 
    # save input
    calc_Sensitivity(   Tint=input_params['Tint'], 
                        Tsys=input_params['Tsys'], 
                        Nant=input_params['Nant'], 
                        Npol=input_params['Npol'], 
                        Bandwidth=input_params['Bandwidth'], 
                        Velowidth=input_params['Velowidth'], 
                        Frequency=input_params['Frequency'], 
                        Telescope=input_params['Telescope'], 
                        Diameter=input_params['Diameter'], 
                        Weather=input_params['Weather'], 
                        eta_ap=input_params['eta_ap'], 
                        Verbose=True)
    
    



