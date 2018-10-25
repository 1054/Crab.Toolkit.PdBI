#!/usr/bin/env python
# 

from __future__ import print_function
import pkg_resources
pkg_resources.require('astropy')
import os, sys, re, json, time, astropy
import numpy as np
import astropy.io.ascii as asciitable
from astropy.table import Table, Column, hstack
from matplotlib import pyplot as plt
from matplotlib import ticker as ticker
from copy import copy

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+os.sep+'Common_Python_Code')

if sys.version_info.major >= 3:
    long = int
    unicode = str

import matplotlib as mpl
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}'] #for \text command
mpl.rcParams['text.latex.preamble'].append(r'\makeatletter \newcommand*{\rom}[1]{\expandafter\@slowromancap\romannumeral #1@} \makeatother')
mpl.rcParams['axes.labelsize'] = '16' # https://matplotlib.org/users/customizing.html
mpl.rcParams['axes.grid'] = True
mpl.rcParams['axes.axisbelow'] = True
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['xtick.minor.visible'] = True
mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['xtick.labelsize'] = '14'
mpl.rcParams['ytick.labelsize'] = '14'
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.right'] = True
#mpl.rcParams['grid.color'] = 'b0b0b0'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linewidth'] = 0.25
mpl.rcParams['grid.alpha'] = 0.8
mpl.rcParams['text.usetex'] = True
mpl.rcParams['legend.fontsize'] = '10.5'



from astropy.cosmology import FlatLambdaCDM
cosmo = FlatLambdaCDM(H0=73, Om0=0.27, Tcmb0=2.725)







output_name = 'Plot_absolute_flux_density_scale'




# 
# main
# 
if __name__ == '__main__':
    
    tb = Table.read('Perley_and_Butler_2017_Table_6.txt', format='ascii.commented_header')
    mask = np.array(np.where(tb['Source'].data=="3C286")).flatten()[0]
    print(mask)
    x = np.linspace(35, 30, 100) # GHz
    y = x*0.0
    for i in range(0,5+1,1):
        if ~np.isnan(tb['a%d'%(i)][mask]):
            y += tb['a%d'%(i)][mask] * np.power(np.log10(x), float(i))
    y = 10**y # Jy
    # log(S_Jy)=a0 +a1*log(freq_GHz)+a2*[log(freq_GHz)]**2+a3*[logfreq_GHz)]**3+...
    x1 = x
    y1 = y
    
    
    tb = Table.read('results_3C286_flux_density_DataSet_01.txt', format='ascii.commented_header')
    x2 = tb['freq'] # GHz
    y2 = tb['flux'] / 1e3 # Jy
    
    
    # 
    # make plot
    # 
    fig = plt.figure(figsize=(5.2,4.0))
    ax = fig.add_subplot(1,1,1)
    #ax1_layer1_cm = plt.cm.get_cmap('jet') # ('RdYlBu_r')
    
    #ax.scatter(x, y1, s=25, marker='o', c='blue',  edgecolor='k', lw=0.3, alpha=0.5, label='Genzel+2015 Eq.(6)')
    #ax.scatter(x, y2, s=25, marker='^', c='green', edgecolor='k', lw=0.3, alpha=0.5, label='Genzel+2015 Eq.(7)')
    #ax.scatter(x, y3, s=25, marker='s', c='red',   edgecolor='k', lw=0.3, alpha=0.5, label=r'Bolatto+2013 Eq.(31) $\Sigma_{\mathrm{gas}}=100\;\mathrm{M_{\odot}\,pc^{-2}}$')
    #ax.scatter(x, y4, s=25, marker='D', c='red',   edgecolor='k', lw=0.3, alpha=0.5, label=r'Bolatto+2013 Eq.(31) $\Sigma_{\mathrm{gas}}=1000\;\mathrm{M_{\odot}\,pc^{-2}}$')
    
    ax.plot(x1, y1, markersize=5, marker='.', c='blue', lw=1, alpha=0.5, label=r'Perley \& Butler (2017)')
    ax.plot(x2, y2, markersize=5, marker='o', c='red',  ls='none', lw=1, alpha=0.5, label='VLA 15B-290')
    
    #cbaxes = fig.add_axes([0.6, 0.30, 0.3, 0.05])
    #cbar = fig.colorbar(mappable=ax1_layer1, cax=cbaxes, ticks = [9.0, 10.0, 11.0, 12.0], orientation='horizontal') # ticks=[0.,1], 
    #cbar.set_label(label=r'$\log\;(M_{\star}/\mathrm{M_{\odot}})$', size=13)
    #cbar.ax.tick_params(labelsize=12)
    #ax1_layer2 = ax.errorbar(xarray[~detected], 3.0*yerror[~detected], yerr=yerror[~detected], uplims=True, c=cbar.to_rgba(3.0), capsize=2, linestyle='none', linewidth=0.5, alpha=0.2, zorder=4) # uplims=upperlimits, lolims=lowerlimits, xuplims=True
    
    
    #ax.fill_between(x, (x*0.0+4.4)/1.3, (x*0.0+4.4)*1.3, color='royalblue', alpha=0.3)
    #ax.fill_between(x, (x*0.0+0.8)/1.3, (x*0.0+0.8)*1.3, color='orangered', alpha=0.3)
    
    ax.plot(x1, y1/1.005, c='k', linestyle='--', lw=1.8, alpha=0.4, zorder=1, label='1/1.005')
    #ax.plot([metalZ_solar,metalZ_solar], [1e-3,1e6], color='k', linestyle='--', lw=1.8, alpha=0.4, zorder=1)
    
    
    ax.set_xlabel(r'Frequency [GHz]', labelpad=6)
    ax.set_ylabel(r'Flux Density [Jy]', labelpad=12)
    #ax.set_xscale('log')
    #ax.set_yscale('log')
    #ax.set_xticks([7.5,8.0,8.5,9.0,9.5,10.0,10.5])
    #ax.set_xlim([7.8,9.2])
    #ax.set_ylim([0.1,3e4])
    
    ax.legend() # loc='upper left'
    
    #ax.tick_params(labelsize=12)
    #ax.tick_params(direction='in', axis='both', which='both')
    #ax.tick_params(top=True, right=True, which='both') # top='on', right='on' -- deprecated -- use True/False instead
    #ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y))) # https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
    #ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: (r'${{:.{:1d}f}}$'.format(int(np.maximum(-np.log10(y),0)))).format(y) if y<1e4 else r'$10^{%d}$'%(np.log10(y)))) # https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
    fig.subplots_adjust(left=0.20, right=0.95, bottom=0.16, top=0.95)
    fig.savefig(output_name+'.pdf')
    print('Output to "%s"' % (output_name+'.pdf'))
    os.system('open "%s"' % (output_name+'.pdf'))
    #plt.show(block=True)
    
    
    #for i in range(len(labels)):
    #    if True:
    #        ax.annotate(labels[i], xy=(xarray[i], yarray[i]), xytext=(0, 0), textcoords='offset points', fontsize='2', zorder=6)
    #fig.savefig(output_name+'_with_labels.pdf')
    #print('Output to "%s"' % (output_name+'_with_labels.pdf'))
    #os.system('open "%s"' % (output_name+'_with_labels.pdf'))



