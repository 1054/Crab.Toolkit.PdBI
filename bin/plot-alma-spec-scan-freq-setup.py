#!/usr/bin/env python
# 

import os, sys, re, time, datetime
import numpy as np
#sys.path.append(os.path.expanduser('~')+os.sep+'Cloud/Github/Crab.Toolkit.Python/lib/crab')
#from crabplot.CrabPlot import CrabPlot
#from crabimage.CrabImage import CrabImage
from astropy.table import Table
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



def usage():
    print('Usgae: ')
    print('  plot-alma-spec-scan-freq-setup.py input_spec_scan_spw_table.txt output_spw_plot_file.pdf')
    print('')
    print('Note:')
    print('  This code will plot the spws for the input ASCII table.')
    print('  The table must have 4 columns: isetup, ispw, spw_begin and spw_end. ')
    print('  The last two columns are frequences in units of GHz.')
    print('')
  


if not (len(sys.argv) > 2):
    usage()
    sys.exit()

input_table = Table.read(sys.argv[1], format='ascii')
input_table['spw_begin'] = input_table['spw_center'] - 1.875/2.0
input_table['spw_end'] = input_table['spw_center'] + 1.875/2.0
input_table.write('aaa.txt', format='ascii.fixed_width', delimiter=' ', overwrite=True)
output_name = re.sub(r'\.pdf', r'', sys.argv[2], re.IGNORECASE)
isetup = input_table[input_table.colnames[0]]
ispw = input_table[input_table.colnames[1]]
spwBegins = input_table[input_table.colnames[2]]
spwEnds = input_table[input_table.colnames[3]]



fig = plt.figure(figsize = (8.0, 1.5))
ax = fig.add_subplot(1, 1, 1)
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.35, top=0.97)

y_min = np.min(isetup)-0.5
y_max = np.max(isetup)+0.5
ax.set_ylim([y_min, y_max])

c_map = matplotlib.cm.jet

for i in range(len(isetup)):
    plot_color = c_map(float(isetup[i]+0.1*ispw[i] - np.min(isetup))/(np.max(isetup)-np.min(isetup))) # input should in the range of 0.0-1.0
    ax.plot([spwBegins[i], spwEnds[i]], [isetup[i], isetup[i]], lw=10, c=plot_color, alpha=0.5, solid_capstyle='butt', solid_joinstyle='miter')

ax.set_xlim(ax.get_xlim())

# some tests
#ax.plot(ax.get_xlim(), [5.0, 5.0], color='k', lw=1.2)
#ax.text(ax.get_xlim()[1], 5.1, 'new setups', color='red', ha='right', va='bottom')
#ax.text(ax.get_xlim()[1], 4.9, 'previous setups', color='blue', ha='right', va='top')

ax.set_xlabel('Observing Frequency [GHz]', fontsize=13, labelpad=5)
ax.set_ylabel('Setup', fontsize=13, labelpad=10)
ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
#plot_var.set_figure_margin(bottom=0.18)
ax.grid(color='gray', linestyle='dotted', linewidth=0.15, alpha=0.5)
fig.savefig('%s.pdf'%(output_name))

os.system('open %s.pdf'%(output_name))

