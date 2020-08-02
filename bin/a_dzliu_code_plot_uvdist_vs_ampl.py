#!/usr/bin/env python
# 

import os, sys, re, copy, shutil
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib as mpl
import matplotlib.pyplot as plt

import astropy
from astropy.io import fits
from astropy.table import Table

if len(sys.argv) < 2:
    print('Usage: ')
    print('  ./a_dzliu_code_plot_uvdist_vs_ampl.py input_data.uvfits Plot_uvdist_vs_ampl.pdf')
    print('Notes: ')
    print('  Input an uvfits file and set the output figure file name.')
    sys.exit()


input_data = sys.argv[1]
output_name = sys.argv[2] # 'Plot_uvdist_vs_ampl.pdf'

print('Reading %r'%(input_data))
with fits.open(input_data) as hdulist:
    for iext, hdu in enumerate(hdulist):
        #print('type(hdu)', type(hdu))
        if isinstance(hdu, fits.GroupsHDU):
            print('Loading fits extension %d'%(iext))
            print('hdu.data.shape', hdu.data.shape)
            restfreq = hdu.header['RESTFREQ'] # Hz
            print('restfreq: %s GHz'%(restfreq/1e9))
            kilolambda = 1e3 * 2.99792458e8 / restfreq # km
            parnames = hdu.data.parnames
            print('parnames: %r'%(parnames))
            u = hdu.data.par('UU')
            v = hdu.data.par('VV')
            uvdist = np.sqrt(u**2 + v**2) * 2.99792458e8
            uvwave = uvdist / kilolambda # seconds * c -> meters -> kilo-lambda
            print('min max uvwave: %s %s kilo-lambda'%(np.min(uvwave), np.max(uvwave)))
            
            # visibilities
            print('hdu.data.data.shape', hdu.data.data.shape)
            print('hdu.data.data[0]', hdu.data.data[100])
            print('hdu.data.data[0]', hdu.data.data[101])
            print('hdu.data.data[0]', hdu.data.data[102])
            vis_re = hdu.data.data[:, 0, 0, 0, 0, 0, 0]
            vis_im = hdu.data.data[:, 0, 0, 0, 0, 0, 1]
            vis_wt = hdu.data.data[:, 0, 0, 0, 0, 0, 2]
            vis_ampl = np.sqrt(vis_re**2 + vis_im**2)
            print('uvwave.shape', uvwave.shape)
            print('vis_ampl.shape', vis_ampl.shape)
            
            # scatter
            mask = np.random.choice(np.arange(len(uvwave)), 100000)
            x = uvwave[mask]
            y = vis_ampl[mask]
            w = vis_wt[mask]
            xy = np.vstack([x,y])
            w = gaussian_kde(xy)(xy) # color by density
            idx = w.argsort()
            x, y, w = x[idx], y[idx], z[idx]
            
            # bin
            uvwave_bins = np.linspace(np.min(uvwave), np.max(uvwave), num=30, endpoint=True)
            xmean = []
            ymean = []
            #binwidths = []
            for i in range(len(uvwave_bins)-1):
                # 
                if i < len(uvwave_bins)-1:
                    mask = np.logical_and(uvwave>=uvwave_bins[i], uvwave<uvwave_bins[i+1])
                else:
                    mask = np.logical_and(uvwave>=uvwave_bins[i], uvwave<=uvwave_bins[i+1])
                # 
                if np.count_nonzero(mask) > 0:
                    ymean.append(np.average(vis_ampl[mask], weights=vis_wt[mask]))
                    #ymean.append(np.mean(vis_ampl[mask]))
                    xmean.append((uvwave_bins[i+1]+uvwave_bins[i])/2.0)
            
            
            # prepare matplotlib figure
            fig = plt.figure(figsize=(5.0,4.0))
            fig.subplots_adjust(left=0.17, right=0.98, bottom=0.14, top=0.96)
            ax = fig.add_subplot(1,1,1)
            
            print('Plotting %d data'%(len(x)))
            pobj = ax.scatter(x, y, s=0.5, c=w, edgecolor='none', norm=mpl.colors.LogNorm())
            fig.colorbar(pobj, ax=ax)
            
            print('Plotting %d uvwave bins'%(len(xmean)))
            ax.plot(xmean, ymean, ls='none', marker='s', ms=0.5, mfc='none', mec='red', mew=1.2)
            
            #ax.set_yscale('log')
            ax.set_ylim([0.0, 0.5])
            
            ax.set_xlabel(r'UVwave [$k \lambda$]', fontsize=15)
            ax.set_ylabel(r'Amplitude', fontsize=15, labelpad=10)
            ax.tick_params(which='both', direction='in', labelsize=12, right=True, top=True)
            #ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1.0))
            #ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.1))
            #ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(1.0))
            #ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.1))
            ax.grid(True, lw=0.2, c='darkgray', ls='dotted')
            
            
            # average uvw
            
            
            # save figure
            if os.path.isfile(output_name):
                shutil.move(output_name, output_name+'.backup')
            fig.savefig(output_name, overwrite=True, dpi=300, transparent=True)
            #os.system('open "%s"'%(output_name))
            print('Output to "%s"!'%(output_name))

