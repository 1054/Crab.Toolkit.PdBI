#!/usr/bin/env python
# 
# This code needs to be ran in CASA.
# 
# This code manipulates ALMA visibility data. 
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil
import numpy as np
import inspect
import random
try:
    import astropy
except:
    #pipinstallpath = ''
    #for temppath in sys.path:
    #    print(temppath, temppath.endswith('site-packages'))
    #    if temppath.endswith('site-packages'):
    #        pipinstallpath = temppath
    #if pipinstallpath != '':
    #    #import subprocess
    #    #subprocess.call('pip-2.7 install --install-option="--prefix=/Users/dzliu/Library/Python/2.7/lib/python/site-packages" astropy')
    #    #print('Running:')
    #    #print('pip-2.7 install --install-option="--prefix=%s" --ignore-installed astropy%(pipinstallpath))
    #    #os.system('pip-2.7 install --install-option="--prefix=%s" --ignore-installed astropy%(pipinstallpath))
    if os.path.isdir('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages'):
        sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
    try:
        import astropy
    except ImportError:
        raise ImportError('Error! Could not import astropy!')
# 
from astropy.wcs import wcs
from astropy.wcs.utils import proj_plane_pixel_scales
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import Angle
from astropy.modeling.models import Sersic2D
#from astropy.table import Table
#from math import gamma as gamma_function
from scipy.special import gamma, gammainc, gammaincinv
#from scipy.optimize import brentq, newton, fsolve



# 
# A function to get arg list of another function
# 
#def get_arg_list(func_name):
#    inspect__dir__ = dir(inspect)
#    arg_list = []
#    if 'signature' in inspect__dir__:
#        arg_list = inspect.signature(func_name).parameters.keys()
#        arg_list = list(arg_list)
#    elif 'getfullargspec' in inspect__dir__:
#        arg_list = inspect.getfullargspec(func_name)[0]
#    elif 'getargspec' in inspect__dir__:
#        arg_list = inspect.getargspec(func_name)[0]
#    else:
#        print('Error! Could not call inspect.getargspec() or inspect.getfullargspec() or inspect.signature()!')
#        sys.exit()
#    return arg_list



# 
# read visibility table and bin uvdist
# 
def bin_uvdist_amplitude(vis, locals_dict):
    # 
    ms = locals_dict['ms']
    # 
    nbin = 12
    if 'nbin' in locals_dict:
        if np.isscalar(locals_dict['nbin']):
            if int(locals_dict['nbin']) > 0:
                nbin = int(locals_dict['nbin'])
    # 
    ms.open(vis)
    ms.selectinit(datadescid=0) #<TODO># spw0 
    # 
    uvdist_boundaries = np.linspace(0.0, 1200.0, num=nbin, endpoint=True)
    mean_amplitudes = []
    median_amplitudes = []
    scatter_amplitudes = []
    mean_real_part = []
    median_real_part = []
    scatter_real_part = []
    vis_uvdist = []
    vis_amplitudes = []
    vis_real_part = []
    for i in range(len(uvdist_boundaries)-1):
        #print('uvdist: %s ~ %s'%(uvdist_boundaries[i], uvdist_boundaries[i+1]))
        ms.select( { 'uvdist': [uvdist_boundaries[i], uvdist_boundaries[i+1]] } )
        #ms.partition('partition.ms', timebin='120s', whichcol='all', combine='scan')
        #data = ms.getdata(["amplitude", "axis_info", "ha"],ifraxis=True) # see https://casa.nrao.edu/docs/CasaRef/ms.getdata.html#x333-3340001.3.1
        data = ms.getdata(["amplitude", "axis_info", "time", "real", "uvdist"], ifraxis=True) # see https://casa.nrao.edu/docs/CasaRef/ms.getdata.html#x333-3340001.3.1
        #print('data["amplitude"].shape', data["amplitude"]) # (2,1,47,12) = Nstokes, Nchan, Nbaseline, Ntime. If ifraxis=False then the shape will be (Nstokes, Nchan, Nrows)
        # averaging over all stokes, channels and times but per baseline
        data["amplitude"] = np.mean(data["amplitude"], axis=(0,1,3))
        data["real"] = np.mean(data["real"], axis=(0,1,3))
        data["uvdist"] = np.mean(data["uvdist"], axis=(1,))
        #print('data["uvdist"].shape', data["uvdist"].shape, 'data["amplitude"].shape', data["amplitude"].shape)
        #datatable = Table(data)
        mean_amplitudes.append(np.mean(data["amplitude"]))
        median_amplitudes.append(np.median(data["amplitude"]))
        scatter_amplitudes.append(np.std(data["amplitude"]))
        mean_real_part.append(np.mean(data["real"]))
        median_real_part.append(np.median(data["real"]))
        scatter_real_part.append(np.std(data["real"]))
        vis_uvdist.extend(data["uvdist"])
        vis_amplitudes.extend(data["amplitude"])
        vis_real_part.extend(data["real"])
        ms.reset()
        # 
        print('uvdist: %8.2f ~ %8.2f, min max %8.2f %8.2f, ampl mean = %8g, med = %8g, std = %8g, real mean = %8g, med = %8g, std = %8g'%(\
                uvdist_boundaries[i], uvdist_boundaries[i+1], 
                np.min(data["uvdist"]), np.max(data["uvdist"]), 
                mean_amplitudes[-1], median_amplitudes[-1], scatter_amplitudes[-1], 
                mean_real_part[-1], median_real_part[-1], scatter_real_part[-1], 
             ))
    # 
    mean_amplitudes = np.array(mean_amplitudes) * 1e3 # convert from Jy/beam to mJy/beam
    median_amplitudes = np.array(median_amplitudes) * 1e3 # convert from Jy/beam to mJy/beam
    scatter_amplitudes = np.array(scatter_amplitudes) * 1e3 # convert from Jy/beam to mJy/beam
    mean_real_part = np.array(mean_real_part) * 1e3 # convert from Jy/beam to mJy/beam
    median_real_part = np.array(median_real_part) * 1e3 # convert from Jy/beam to mJy/beam
    scatter_real_part = np.array(scatter_real_part) * 1e3 # convert from Jy/beam to mJy/beam
    vis_uvdist = np.array(vis_uvdist)
    vis_amplitudes = np.array(vis_amplitudes) * 1e3 # convert from Jy/beam to mJy/beam
    vis_real_part = np.array(vis_real_part) * 1e3 # convert from Jy/beam to mJy/beam
    # 
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0,5.0))
    ax = fig.add_subplot(2, 2, 1)
    uvdist_centers = (uvdist_boundaries[0:-1]+uvdist_boundaries[1:]) / 2.0
    uvdist_widths = (uvdist_boundaries[1:]-uvdist_boundaries[0:-1]) / 2.0
    # 
    ylim = [np.min([mean_amplitudes,median_amplitudes]), np.max([mean_amplitudes,median_amplitudes])]
    ylim = [ylim[0]-0.15*(ylim[1]-ylim[0]), ylim[1]+0.15*(ylim[1]-ylim[0])]
    # 
    ax.plot(vis_uvdist, vis_amplitudes, marker='o', markersize=0.5, color='#cccccc', linestyle='none', alpha=0.8, zorder=10)
    ax.plot(uvdist_centers, mean_amplitudes, marker='o', linestyle='none', zorder=15)
    ax.tick_params(axis='both', which='major', labelsize=9)
    ax.errorbar(uvdist_centers, mean_amplitudes, yerr = scatter_amplitudes, xerr = uvdist_widths, elinewidth = 1.05, capsize = 2.0, zorder=18)
    ax.set_xlabel('uvdist')
    ax.set_ylabel('mean(Ampl) [mJy/beam]')
    ax.set_ylim(ylim)
    ax.grid(True, ls='dotted', lw=0.35, alpha=0.45)
    # 
    ax = fig.add_subplot(2, 2, 2)
    ax.plot(vis_uvdist, vis_amplitudes, marker='o', markersize=0.5, color='#cccccc', linestyle='none', alpha=0.8, zorder=10)
    ax.plot(uvdist_centers, median_amplitudes, marker='o', linestyle='none')
    ax.tick_params(axis='both', which='major', labelsize=9)
    ax.errorbar(uvdist_centers, median_amplitudes, yerr = scatter_amplitudes, xerr = uvdist_widths, elinewidth = 1.05, capsize = 2.0, zorder=18)
    ax.set_xlabel('uvdist')
    ax.set_ylabel('median(Ampl) [mJy/beam]')
    ax.set_ylim(ylim)
    ax.grid(True, ls='dotted', lw=0.35, alpha=0.45)
    # 
    ylim = [np.min([mean_real_part,median_real_part]), np.max([mean_real_part,median_real_part])]
    ylim = [ylim[0]-0.15*(ylim[1]-ylim[0]), ylim[1]+0.15*(ylim[1]-ylim[0])]
    # 
    ax = fig.add_subplot(2, 2, 3)
    ax.plot(vis_uvdist, vis_real_part, marker='o', markersize=0.5, color='#cccccc', linestyle='none', alpha=0.8, zorder=10)
    ax.plot(uvdist_centers, mean_real_part, marker='o', linestyle='none')
    ax.tick_params(axis='both', which='major', labelsize=9)
    ax.errorbar(uvdist_centers, mean_real_part, yerr = scatter_real_part, xerr = uvdist_widths, elinewidth = 1.05, capsize = 2.0, zorder=18)
    ax.set_xlabel('uvdist')
    ax.set_ylabel('mean(Real) [mJy/beam]')
    ax.set_ylim(ylim)
    ax.grid(True, ls='dotted', lw=0.35, alpha=0.45)
    # 
    ax = fig.add_subplot(2, 2, 4)
    ax.plot(vis_uvdist, vis_real_part, marker='o', markersize=0.5, color='#cccccc', linestyle='none', alpha=0.8, zorder=10)
    ax.plot(uvdist_centers, median_real_part, marker='o', linestyle='none')
    ax.tick_params(axis='both', which='major', labelsize=9)
    ax.errorbar(uvdist_centers, median_real_part, yerr = scatter_real_part, xerr = uvdist_widths, elinewidth = 1.05, capsize = 2.0, zorder=18)
    ax.set_xlabel('uvdist')
    ax.set_ylabel('median(Real) [mJy/beam]')
    ax.set_ylim(ylim)
    ax.grid(True, ls='dotted', lw=0.35, alpha=0.45)
    fig.tight_layout()
    plt.savefig('Plot_bin_uvdist_amplitude.pdf', transparent=True)
    print('Output to "Plot_bin_uvdist_amplitude.pdf"!')
    # 
    return uvdist_boundaries, mean_amplitudes
    




# 
# compute visibility rms
# 
def compute_visibility_rms(vis, locals_dict):
    # 
    tb = locals_dict['tb']
    # 
    # each tb row corresponds to one FIELD and one SPW
    # the FIELD ID is indicated by the 'FIELD_ID' column, 
    # while the SPW ID is indicate dby the 'DATA_DESCRIPTION' column. 
    # 
    # get data_desc_IDs
    data_desc_ID_to_spw_ID_dict = {}
    tb.open(vis+os.sep+'DATA_DESCRIPTION')
    for i in range(tb.nrows()):
        data_desc_ID_to_spw_ID_dict[i] = tb.getcell('SPECTRAL_WINDOW_ID', i)
    tb.close()
    # 
    # get FIELD
    field_ID_to_field_name_dict = {}
    field_ID_list = []
    tb.open(vis+os.sep+'FIELD')
    for i in range(tb.nrows()):
        field_ID_to_field_name_dict[i] = tb.getcell('NAME', i)
        field_ID_list.append(i)
    tb.close()
    # 
    # get SPW_ID_list
    SPW_ID_list = []
    SPW_ID_to_chanwidth_dict = {}
    SPW_ID_to_bandwidth_dict = {}
    SPW_total_bandwidth = 0.0 # Hz
    tb.open(vis+os.sep+'SPECTRAL_WINDOW')
    for i in range(tb.nrows()):
        SPW_ID_list.append(i)
        SPW_ID_to_chanwidth_dict[i] = tb.getcell('CHAN_WIDTH', i) # it is an array
        SPW_ID_to_bandwidth_dict[i] = tb.getcell('TOTAL_BANDWIDTH', i) # it is a scalar
        SPW_total_bandwidth += SPW_ID_to_bandwidth_dict[i]
    tb.close()
    # 
    # get visibility data
    tb.open(vis)
    # 
    if 'CORRECTED_DATA' in tb.colnames():
        data_column = 'CORRECTED_DATA'
    else:
        data_column = 'DATA'
    print('Data column is "%s"'%(data_column))
    # 
    vis_rms_dict = {}
    # 
    for field_ID in field_ID_list:
        field_name = field_ID_to_field_name_dict[field_ID]
        print('Looping field %s (%d/%d)'%(field_name, field_ID+1, len(field_ID_list)))
        # 
        query_str = "(FLAG_ROW==FALSE)" + ' AND ' + '(FIELD_ID==%d)'%(field_ID)
        # 
        tb_queried = tb.query(query = query_str + ' LIMIT 1', 
                              columns = data_column, style = 'python') # shape of (nstokes, nchan)
        check_data_cell = tb_queried.getcell(tb_queried.colnames()[0], 0)
        print('check_data_cell', re.sub(r'\n', r',', str(check_data_cell)), 'check_data_cell.shape', check_data_cell.shape)
        if len(check_data_cell.shape) >= 2:
            number_of_stokes = check_data_cell.shape[0]
        else:
            number_of_stokes = 1
        print('number_of_stokes', number_of_stokes)
        # 
        # 
        #query_str += ' AND ' + (DATA_DESC_ID in [%s])'%( ','.join( map( str, info_dict['SPW']['DATA_DESC_ID'][ispw] ) ) )
        tb_queried = tb.query(query = query_str, 
                              #columns = data_column, style = 'python') 
                              #columns = 'amplitude('+data_column+')', style = 'python') # shape of (nstokes, nchan) and nrows groups
                              #columns = 'GAGGR(amplitude('+data_column+'))', style = 'python') # shape of (nstokes, nchan, nrows)
                              #columns = 'MEANS(GAGGR(amplitude('+data_column+')),2)', style = 'python') # shape of (nchan, nrows)
                              #columns = 'RMSS(MEANS(GAGGR(amplitude('+data_column+')),2),0)', style = 'python') # shape of (nchan)
                              columns = 'RMSS(GAGGR(amplitude('+data_column+')),0)', style = 'python') # shape of (nstokes, nchan)
                              # 
                              # Data array has a shape of (nstokes, nchan, nrows), and each data cell is a complex number. 
                              # After TAQL function amplitude(), the shape is still (nstokes, nchan, nrows), but now is real numbers.
                              # After TAQL function GMEAN(), the shape is still (nstokes, nchan, nrows), but now is real numbers.
                              # TAQL function MEANS(GAGGR(),2) is equivalent to GMEANS() but can control the axis,
                              # here we compute the mean over the 3rd axis nstokes, so the shape becomes (1stoke, nchan, nrows)
                              # TAQL function RMSS() computes the RMS along axis 0, so the shape becomes (1stoke, nchan)
                              # 
                              # GAGGR: Stack the row values in a group to form an array where the row is the slowest varying axis 
                              #        (similar to numpy's dstack). Thus if the column contains scalar values, the result is a vector. 
                              #        Otherwise it is an array whose dimensionality is one higher. It requires that all arrays in 
                              #        a group have the same shape. 
                              #        -- https://casacore.github.io/casacore-notes/199.html
                              # 
                              # When using python style, axis 0 is the most slowly varying axis. 
                              # 
        #vis_rms_per_chan = tb_queried.getcell(tb_queried.colnames()[0], 0) # must get cell as it will only have one cell
        #print('vis_rms_per_chan', vis_rms_per_chan, 'vis_rms_per_chan.shape', vis_rms_per_chan.shape) # shape of (nchan)
        vis_rms_per_chan_per_stokes = tb_queried.getcell(tb_queried.colnames()[0], 0) # must get cell as it will only have one cell
        print('vis_rms_per_chan_per_stokes', re.sub(r'\n', r',', str(vis_rms_per_chan_per_stokes)), 'vis_rms_per_chan_per_stokes.shape', vis_rms_per_chan_per_stokes.shape) # shape of (nstokes, nchan)
        # 
        # calculate sum of EXPOSURE, EXPOSURE * BASELINE, and EXPOSURE * ALL, ALL means BASELINE * NSTOKES. 
        tb_queried = tb.query(query = query_str, 
                              columns = 'GSUM(EXPOSURE), GCOUNT(EXPOSURE)')
        exposure_sum = tb_queried.getcell(tb_queried.colnames()[0], 0)
        exposure_count = tb_queried.getcell(tb_queried.colnames()[1], 0)
        print('exposure_sum', exposure_sum, 'exposure_count', exposure_count)
        # 
        # calculate image plane rms noise expected
        #                           np.sqrt(np.sum(np.square(vis_rms_per_chan_per_stokes))) \
        image_plane_continuum_rms = np.mean(vis_rms_per_chan_per_stokes) \
                                    / np.sqrt(SPW_total_bandwidth / np.mean(SPW_ID_to_chanwidth_dict[0])) \
                                    / np.sqrt(exposure_count * number_of_stokes)
                                    # visibility rms is per channel and per scan. 
        print('image_plane_continuum_rms %s mJy/beam over a total bandwidth of %s GHz.'%(image_plane_continuum_rms*1e3, SPW_total_bandwidth/1e9))
        # 
        # 
        # --> test
        # '/Users/dzliu/Work/AlmaCosmos/Simulations/CASA_Sim/Sim_single_Gaussian/casasim_Project_R150mas_Gaussian_circular/casasim_Project_R150mas_Gaussian_circular.alma_0.18arcsec.noisy.uvfits'
        # this code --> image_plane_continuum_rms 0.129169000823 mJy/beam over a total bandwidth of 7.5 GHz.
        # gildas mapping go noise --> 1.3448471E-04 Jy/beam. 
    # 
    tb.close()
    












