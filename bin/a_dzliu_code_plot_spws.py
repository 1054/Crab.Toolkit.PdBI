#!/usr/bin/env python
# 

import os, sys, re, copy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import astropy
from astropy.table import Table

tb = Table.read('meta_data_table_with_dataset_names_and_spws.txt', format='ascii')



fig = plt.figure(figsize=(12.0,4.0))
fig.subplots_adjust(left=0.07, right=0.99, bottom=0.14, top=0.97)

ax = fig.add_subplot(1,1,1)

ch0 = tb['Ch0_MHz']/1e3
ch1 = tb['Ch0_MHz']/1e3+tb['NChans']*(tb['ChanWid_kHz']/1e6)

idatasets = np.array(list(map(int, [re.sub(r'.*_([0-9]+)$', r'\1',t) for t in tb['DataSet']])))

ispw = copy.copy(tb['SpwID'].data)
ispw[idatasets==3] = np.arange(0,len(ispw[idatasets==3])) # re-arrange ispw like 0,1,2,3

ax.set_ylim([0.5, len(np.unique(tb['DataSet'].data))+0.5])
ax.set_xlabel('Frequency [GHz]', fontsize=15)
ax.set_ylabel(r'DataSetID + 0.1 $\times$ SpwID', fontsize=15, labelpad=10)
ax.tick_params(direction='in', labelsize=12, right=True, top=True)
ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1.0))
ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.1))
ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(1.0))
ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.1))
ax.grid(True, lw=0.2, c='darkgray', ls='dotted')

icolors = ['red', 'blue', 'magenta', 'cyan']

for i in range(len(ch0)):
    
    if ch0[i] < ch1[i]:
        plot_x = [ch0[i], ch1[i]]
    else:
        plot_x = [ch1[i], ch0[i]]
    
    plot_y = np.repeat(idatasets[i]+0.1*ispw[i],2)
    
    ax.fill_between(plot_x, 
                    plot_y, 
                    plot_y+0.0618, 
                    color = icolors[idatasets[i]-1], 
                    alpha = 0.5, 
                    )
    
    ax.text(plot_x[1], plot_y[0], ' spw %d'%(tb['SpwID'][i]), fontsize = 8, color = icolors[idatasets[i]-1], )
    
    #print(plot_x, idatasets[i]+0.1*ispw[i])

fig.savefig('Plot_spws.pdf')
os.system('open "Plot_spws.pdf"')
print('Output to "Plot_spws.pdf"!')

