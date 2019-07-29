#!/usr/bin/env python
# 

from __future__ import print_function

# import python packages
import os, sys, json, time, re, shutil
import numpy as np
from astropy.table import Table, Column
#np.warnings.filterwarnings('ignore')

#sys.path.append(os.path.expanduser('~')+'/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabpdbi')
#from CrabPdBI import calc_Sensitivity

if sys.version_info.major <= 2:
    pass
else:
    long = int




def usage():
    print('Usgae: ')
    print('  calc-alma-spec-scan-freq-setup.py -begin XXXGHz -number 4 -out output_spw_table.txt [-do-plot]')
    print('')
    print('Note:')
    print('  This code will compute a frequency setup for the input spectral scan frequency range')
    print('')




if __name__ == '__main__':
    # 
    # check user input
    if len(sys.argv) <= 1:
        usage()
        sys.exit()
    # 
    # read user input
    input_params = {}
    input_params['begin'] = np.nan
    input_params['end'] = np.nan
    input_params['number'] = np.nan
    input_params['out'] = ''
    input_params['plot'] = False
    i = 1
    while i < len(sys.argv):
        if sys.argv[i].startswith('-'):
            for key in input_params:
                if sys.argv[i].lower() == '-do-'+key.lower() or sys.argv[i].lower() == '--do-'+key.lower():
                    input_params[key] = True
                elif sys.argv[i].lower() == '-'+key.lower() or sys.argv[i].lower() == '--'+key.lower():
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
    if np.isnan(input_params['begin']):
        usage()
        sys.exit()
    # 
    # check ALMA band (ALMA_Cycle_7_Technical_Handbook Table 4.1)
    ALMA_Band = np.nan
    if input_params['begin'] >= 84.0 and  input_params['begin']<116.0:
        ALMA_Band = 3
        IF_range = (4.0, 8.0)
        IF_width = 7.5
    elif input_params['begin'] >= 125.0 and  input_params['begin']<158.0:
        ALMA_Band = 4
        IF_range = (4.0, 8.0)
        IF_width = 7.5
    elif input_params['begin'] >= 158.0 and  input_params['begin']<211.0:
        ALMA_Band = 5
        IF_range = (4.0, 8.0)
        IF_width = 7.5
    elif input_params['begin'] >= 211.0 and  input_params['begin']<275.0:
        ALMA_Band = 6
        IF_range = (4.0, 8.0)
        IF_width = 7.5
    elif input_params['begin'] >= 275.0 and  input_params['begin']<373.0:
        ALMA_Band = 7
        IF_range = (4.0, 8.0)
        IF_width = 7.5
    elif input_params['begin'] >= 385.0 and  input_params['begin']<500.0:
        ALMA_Band = 8
        IF_range = (4.0, 8.0)
        IF_width = 7.5
    elif input_params['begin'] >= 602.0 and  input_params['begin']<720.0:
        ALMA_Band = 9
        IF_range = (4.0, 12.0)
        IF_width = 7.5 # 15.0 <TODO>
    elif input_params['begin'] >= 787.0 and  input_params['begin']<950.0:
        ALMA_Band = 10
        IF_range = (4.0, 12.0)
        IF_width = 7.5 # 15.0 <TODO>
    # 
    # calc freq
    SPW_overlap = 0.250 # GHz
    SPW_width = 1.875
    LO_width = IF_range[0] * 2.0 # GHz
    SB_width = IF_range[1] - IF_range[0] # sideband width
    # 
    # 
    spw0center = input_params['begin'] + SPW_width/2.0
    spw1center = spw0center + SPW_width - SPW_overlap
    spw2center = (spw0center+spw1center)/2.0 + SB_width + LO_width - SPW_width/2.0 + SPW_overlap/2.0
    spw3center = spw2center + SPW_width - SPW_overlap
    LO_freq = (spw0center+spw1center)/2.0 + SB_width/2.0 + LO_width/2.0
    print('LSBcenter2Lo = %.6f'%((spw0center+spw1center)/2.0 - LO_freq))
    print('USBcenter2Lo = %.6f'%((spw2center+spw3center)/2.0 - LO_freq))
    print('spw0center = %.6f'%(spw0center))
    print('spw1center = %.6f'%(spw1center))
    print('spw2center = %.6f'%(spw2center))
    print('spw3center = %.6f'%(spw3center))
    # 
    # 
    if not np.isnan(input_params['number']):
        spw0centers = [spw0center]
        spw1centers = [spw1center]
        spw2centers = [spw2center]
        spw3centers = [spw3center]
        next_begin_freq = spw1center + SPW_width/2.0 - SPW_overlap
        for i in range(1,int(input_params['number'])):
            spw0center = next_begin_freq + SPW_width/2.0
            spw1center = spw0center + SPW_width - SPW_overlap
            spw2center = (spw0center+spw1center)/2.0 + SB_width + LO_width - SPW_width/2.0 + SPW_overlap/2.0
            spw3center = spw2center + SPW_width - SPW_overlap
            print('spw0center = %.6f'%(spw0center))
            print('spw1center = %.6f'%(spw1center))
            print('spw2center = %.6f'%(spw2center))
            print('spw3center = %.6f'%(spw3center))
            spw0centers.append(spw0center)
            spw1centers.append(spw1center)
            spw2centers.append(spw2center)
            spw3centers.append(spw3center)
            next_begin_freq = spw1center + SPW_width/2.0 - SPW_overlap
            if (i+1)%4 == 0:
                # if i+1 mod 4 equals 0, it means we need a giant leap
                # as every 4 setups covers an entire freq range
                next_begin_freq = spw3center + SPW_width/2.0 - SPW_overlap
    # 
    # 
    if input_params['out'] != '':
        if os.path.isfile(input_params['out']):
            print('Found existing "%s". Backing-up as "%s"!'%(input_params['out'], input_params['out']+'.backup'))
            shutil.move(input_params['out'], input_params['out']+'.backup')
        with open(input_params['out'], 'w') as fp:
            fp.write('# %8s %10s %15s %15s %15s\n'%('isetup', 'ispw', 'spw_begin', 'spw_end', 'spw_center'))
            for i in range(len(spw0centers)):
                fp.write('%10d %10d %15.6f %15.6f %15.6f\n'%(i+1, 0, spw0centers[i]-SPW_width/2.0, spw0centers[i]+SPW_width/2.0, spw0centers[i]))
                fp.write('%10d %10d %15.6f %15.6f %15.6f\n'%(i+1, 1, spw1centers[i]-SPW_width/2.0, spw1centers[i]+SPW_width/2.0, spw1centers[i]))
                fp.write('%10d %10d %15.6f %15.6f %15.6f\n'%(i+1, 2, spw2centers[i]-SPW_width/2.0, spw2centers[i]+SPW_width/2.0, spw2centers[i]))
                fp.write('%10d %10d %15.6f %15.6f %15.6f\n'%(i+1, 3, spw3centers[i]-SPW_width/2.0, spw3centers[i]+SPW_width/2.0, spw3centers[i]))
            print('Output to "%s"!'%(input_params['out']))
    # 
    # 
    if input_params['plot'] == True:
        pass #<TODO>
    
    



