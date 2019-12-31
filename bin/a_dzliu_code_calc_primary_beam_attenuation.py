#!/usr/bin/env python
# 

import os, sys
import numpy as np

import astropy
from astropy.table import Table

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import ScalarFormatter, FuncFormatter, FormatStrFormatter, NullFormatter, LogLocator



# prepare function
def calc_primary_beam_attenuation(antenna_dish_diameter, sky_frequency, primary_beam_dist, verbose=False):
    # primary_beam_dist # arcsec
    primary_beam_disq = primary_beam_dist**2
    sky_wavelength = 2.99792458e5/sky_frequency # um
    primary_beam_diam = antenna_dish_diameter # 12.0 # ALMA 12m
    #primary_beam_tape = 10.0 # https://safe.nrao.edu/wiki/bin/view/ALMA/AlmaPrimaryBeamCorrection
    #primary_beam_bpar = 1.243 - 0.343 * primary_beam_tape + 0.12 * primary_beam_tape**2 # http://legacy.nrao.edu/alma/memos/html-memos/alma456/memo456.pdf -- Eq(18)
    primary_beam_bpar = 1.13
    primary_beam_fwhm = primary_beam_disq*0.0 + primary_beam_bpar * sky_wavelength / (primary_beam_diam*1e6) / np.pi * 180.0 * 3600.0 # arcsec
    primary_beam_sigm = primary_beam_disq*0.0 + primary_beam_fwhm/(2.0*np.sqrt(2.0*np.log(2)))
    primary_beam_attenuation = np.exp((-primary_beam_disq) / (2.0*((primary_beam_sigm)**2)) ) #<TODO><20170613># 
    if verbose == True:
        print('primary_beam_diam', primary_beam_diam, 'm')
        print('primary_beam_dist', primary_beam_dist, 'arcsec')
        print('primary_beam_fwhm', primary_beam_fwhm, 'arcsec')
        print('primary_beam_sigm', primary_beam_sigm, 'arcsec')
        print('ratio_of_dist_to_pb_rad', primary_beam_dist/primary_beam_fwhm*2)
        print('primary_beam_attenuation', primary_beam_attenuation)
    return primary_beam_attenuation

# prepare function
def calc_primary_beam_dist(antenna_dish_diameter, sky_frequency, primary_beam_attenuation):
    # inversed process of calc_primary_beam_attenuation
    sky_wavelength = 2.99792458e5/sky_frequency # um
    primary_beam_diam = antenna_dish_diameter # 12.0 # ALMA 12m
    primary_beam_bpar = 1.13
    primary_beam_fwhm = primary_beam_attenuation*0.0 + primary_beam_bpar * sky_wavelength / (primary_beam_diam*1e6) / np.pi * 180.0 * 3600.0 # arcsec
    primary_beam_sigm = primary_beam_attenuation*0.0 + primary_beam_fwhm/(2.0*np.sqrt(2.0*np.log(2)))
    primary_beam_disq = - np.log(primary_beam_attenuation) * (2.0*((primary_beam_sigm)**2))
    primary_beam_dist = np.sqrt(primary_beam_disq)
    return primary_beam_dist/primary_beam_fwhm # return normalized value






if __name__ == '__main__':
    
    # check user input
    if len(sys.argv) <= 3:
        print('Usage: ')
        print('    a_dzliu_code_calc_primary_beam_attenuation.py antenna_dish_diameter_m sky_frequency_GHz primary_beam_dist_arcsec')
        print('')
        sys.exit()
    
    # read user input
    if str(sys.argv[1]).upper() == 'NOEMA':
        antenna_dish_diameter = 15.0
    elif str(sys.argv[1]).upper() == 'ALMA':
        antenna_dish_diameter = 12.0
    else:
        antenna_dish_diameter = float(sys.argv[1])
    sky_frequency = float(sys.argv[2])
    primary_beam_dist = float(sys.argv[3])
    
    calc_primary_beam_attenuation(antenna_dish_diameter, sky_frequency, primary_beam_dist, verbose=True)
    #print((2.0*np.sqrt(2.0*np.log(2)))/2.0)
    #print(np.exp(-(1.1774**2)/2.0))
    
    #./a_dzliu_code_calc_primary_beam_attenuation.py 19.288 230
    #primary_beam_dist 19.288 arcsec
    #primary_beam_fwhm 25.31717231449028 arcsec
    #primary_beam_sigm 10.751213184172439 arcsec
    #ratio_of_dist_to_pb_rad 1.5237088692531842 # ratio of distance to half of the primary beam FWHM, when it is 1.0, pb attenuation is 0.5.
    #primary_beam_attenuation 0.20003318740273365




