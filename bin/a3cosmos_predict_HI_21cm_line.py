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

from astropy.cosmology import FlatLambdaCDM
cosmo = FlatLambdaCDM(H0=70, Om0=0.27, Tcmb0=2.725)

#sys.path.append('/Users/dzliu/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabpdbi')
#from CrabPdBI import convert_Wavelength_um_to_Frequency_GHz, \
#                    calc_radio_line_frequencies, \
#                    find_radio_lines_in_frequency_range, \
#                    calc_radio_line_flux_from_IR_luminosity

if sys.version_info.major <= 2:
    pass
else:
    long = int




def usage():
    print('Usgae: ')
    print('  a3cosmos_predict_HI_21cm_line.py redshift M_HI [d_L]')
    print('Example:')
    print('  a3cosmos_predict_HI_21cm_line.py 0.385 1e10')






def convert_flux2lprm(S_Jy_km_s, rest_freq_GHz, z = 0.0, dL = 0.0):
    # convert flux [Jy km/s] to lumin prime [K km s-1 pc2]
    if dL <= 0.0:
        lumdist_Mpc = cosmo.luminosity_distance(z).value # Mpc
    else:
        lumdist_Mpc = dL
    L_K_km_s__1_pc_2 = np.array(S_Jy_km_s) * 3.25e7 * lumdist_Mpc**2 / np.array(rest_freq_GHz)**2 / (1.0+z)
    return L_K_km_s__1_pc_2


def convert_lprm2flux(L_K_km_s__1_pc_2, rest_freq_GHz, z = 0.0, dL = 0.0):
    # convert lumin prime [K km s-1 pc2] to flux [Jy km/s]
    if dL <= 0.0:
        lumdist_Mpc = cosmo.luminosity_distance(z).value # Mpc
    else:
        lumdist_Mpc = dL
    S_Jy_km_s = np.array(L_K_km_s__1_pc_2) / 3.25e7 / lumdist_Mpc**2 * np.array(rest_freq_GHz)**2 * (1.0+z)
    return S_Jy_km_s


def convert_flux2lsun(S_Jy_km_s, rest_freq_GHz, z = 0.0, dL = 0.0):
    # convert flux [Jy km/s] to luminosity [L_sun]
    # https://1054.github.io/Wiki/radio_line_brightness_temperature/
    if dL <= 0.0:
        lumdist_Mpc = cosmo.luminosity_distance(z).value # Mpc
    else:
        lumdist_Mpc = dL
    L_L_sun = np.array(S_Jy_km_s) * 1.0339577e-3 * lumdist_Mpc**2 * np.array(rest_freq_GHz) / (1.0+z)
    return L_L_sun


def convert_lsun2flux(L_Lsun, rest_freq_GHz, z = 0.0, dL = 0.0):
    # convert flux [Jy km/s] to luminosity [L_sun]
    # https://1054.github.io/Wiki/radio_line_brightness_temperature/
    if dL <= 0.0:
        lumdist_Mpc = cosmo.luminosity_distance(z).value # Mpc
    else:
        lumdist_Mpc = dL
    S_Jy_km_s = np.array(L_Lsun) / 1.0339577e-3 / lumdist_Mpc**2 / np.array(rest_freq_GHz) * (1.0+z)
    return S_Jy_km_s


def convert_lprm2lsun(L_K_km_s__1_pc_2, rest_freq_GHz):
    # convert lumin prime [K km/s pc2] to luminosity [L_sun]
    L_L_sun = L_K_km_s__1_pc_2 * 3.1814084e-11 * np.array(rest_freq_GHz)**3 # https://1054.github.io/Wiki/radio_line_brightness_temperature/
    return L_L_sun


def convert_lsun2lprm(L_L_sun, rest_freq_GHz):
    # convert luminosity [L_sun] to lumin prime [K km/s pc2]
    L_K_km_s__1_pc_2 = L_L_sun / 3.1814084e-11 / np.array(rest_freq_GHz)**3 # https://1054.github.io/Wiki/radio_line_brightness_temperature/
    return L_K_km_s__1_pc_2





if __name__ == '__main__':
    # 
    # check user input
    if len(sys.argv) <= 1:
        usage()
        sys.exit()
    # 
    # read user input
    z = np.nan
    M_HI = np.nan
    d_L = np.nan
    i = 1
    while i < len(sys.argv):
        if np.isnan(z):
            z = float(sys.argv[i])
        elif np.isnan(M_HI):
            M_HI = float(sys.argv[i])
        elif np.isnan(d_L):
            d_L = float(sys.argv[i])
        else:
            pass
        i += 1
    # 
    # check user input
    if np.isnan(z) or np.isnan(M_HI):
        usage()
        sys.exit()
    # 
    # 
    # set default value
    line_freq = 1.420405751 # GHz
    line_name = 'HI21cm'
    obs_freq = line_freq / (1. + z)
    if np.isnan(d_L):
        d_L = cosmo.luminosity_distance(z).value # Mpc
        print('Luminosity distance %s Mpc'%(d_L))
    # 
    # predict line flux
    S_HI = M_HI / (2.355e5 * d_L**2) # Jy km/s
    line_flux_prediction = S_HI
    # 
    # 
    output_str = 'Line name %s, predicted flux %s Jy km s-1.'%(line_name, line_flux_prediction)
    print(output_str)
    #print(''.join(map(lambda x: x*len(output_str), '-')))
    
    
    
    # Fukui 2018
    # When optically thin, N_HI_percmsq = 1.823e18 * W_HI_Kkms
    



