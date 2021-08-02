#!/usr/bin/env python
# 

from __future__ import print_function

# import python packages
import os, sys, json, time, re, shutil
import numpy as np
import astropy.units as u
import astropy.constants as const
#from astropy.table import Table, Column
from pprint import pprint
#np.warnings.filterwarnings('ignore')

#sys.path.append(os.path.expanduser('~')+'/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabpdbi')
#from CrabPdBI import calc_Sensitivity

if sys.version_info.major <= 2:
    pass
else:
    long = int




def usage():
    print('Usgae: ')
    print('  calc-candidate-redshifts-given-a-line.py XXXGHz')
    print('')
    print('Note:')
    print('  This code will compute candidate redshifts assuming the input frequency is a CO or CI or CII or NII line. ')
    print('')


def get_line_dict(line_list = ['CO', 'H2O', 'CI', 'CII', 'NII', 'OI', 'OIII']):
    line_dict = {}
    if 'CO' in line_list:
        line_dict['CO 1-0'] = 115.2712018 * u.GHz
        line_dict['CO 2-1'] = 230.5380000 * u.GHz
        line_dict['CO 3-2'] = 345.7959899 * u.GHz
        line_dict['CO 4-3'] = 461.0407682 * u.GHz
        line_dict['CO 5-4'] = 576.2679305 * u.GHz
        line_dict['CO 6-5'] = 691.4730763 * u.GHz
        line_dict['CO 7-6'] = 806.6518060 * u.GHz
        line_dict['CO 8-7'] = 921.7997000 * u.GHz
        line_dict['CO 9-8'] = 1036.9123930 * u.GHz
        line_dict['CO 10-9'] = 1151.9854520 * u.GHz
        #line_dict['CO 11-10'] = 1267.0144860 * u.GHz
        #line_dict['CO 12-11'] = 1381.9951050 * u.GHz
        #line_dict['CO 13-12'] = 1496.9229090 * u.GHz
    if 'H2O' in line_list:
        line_dict['H2O $1_{1,0}-1_{0,1}$'] = 556.93599 * u.GHz
        line_dict['H2O $1_{1,1}-0_{0,0}$'] = 1113.34301 * u.GHz
        line_dict['H2O $2_{0,2}-1_{1,1}$'] = 987.92676 * u.GHz
        line_dict['H2O $2_{1,1}-2_{0,2}$'] = 752.03314 * u.GHz
        line_dict['H2O $2_{1,2}-1_{0,1}$'] = 1669.90477 * u.GHz
        line_dict['H2O $2_{2,0}-2_{1,1}$'] = 1228.78872 * u.GHz
        line_dict['H2O $2_{2,1}-2_{1,2}$'] = 1661.00764 * u.GHz
        line_dict['H2O $3_{0,2}-2_{1,2}$'] = 1716.76963 * u.GHz
        line_dict['H2O $3_{1,2}-2_{2,1}$'] = 1153.12682 * u.GHz
        line_dict['H2O $3_{1,2}-3_{0,3}$'] = 1097.36479 * u.GHz
        line_dict['H2O $3_{2,1}-3_{1,2}$'] = 1162.9116 * u.GHz
        line_dict['H2O $3_{2,2}-3_{1,3}$'] = 1919.35953 * u.GHz
    if 'CI' in line_list:
        line_dict['CI $^3P_1-^3P_0$'] = 492.16065 * u.GHz
        line_dict['CI $^3P_2-^3P_1$'] = 809.34197 * u.GHz
    if 'CII' in line_list:
        line_dict['CI $^2P_{3/2}-^2P_{1/2}$'] = 1900.53690 * u.GHz
    if 'NII' in line_list:
        line_dict['NII $^3P_1-^3P_0$'] = 1461.13141 * u.GHz
        line_dict['NII $^3P_2-^3P_1$'] = 2459.38010 * u.GHz
    if 'OI' in line_list:
        line_dict['OI $^3P_1-^3P_0$'] = (const.c / 145.525439 * u.um).to(u.GHz)
        line_dict['OI $^3P_2-^3P_1$'] = (const.c / 63.183705 * u.um).to(u.GHz)
    if 'OIII' in line_list:
        line_dict['OIII $^3P_1-^3P_0$'] = (const.c / 88.356000 * u.um).to(u.GHz)
        line_dict['OIII $^3P_2-^3P_1$'] = (const.c / 51.814500 * u.um).to(u.GHz)
    # 
    return line_dict


if __name__ == '__main__':
    # 
    # check user input
    if len(sys.argv) <= 1:
        usage()
        sys.exit()
    # 
    # read user input
    input_frequencies = []
    input_params = {}
    input_params['zmin'] = 1.0
    input_params['zmax'] = 10.0
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
                            input_params[key] = float(sys.argv[i])
        else:
            # if a float number without unit has been input, then we take it as a frequency in GHz unit.
            if re.match(r'^[0-9.+-]+$', sys.argv[i]):
                freq = float(sys.argv[i]) * u.GHz
            # otherwise try reading it as a quantity with units.
            else:
                try:
                    freq = u.Quantity(sys.argv[i])
                    print('Input frequency: %s'%(freq))
                except:
                    raise Exception('Error! Could not parse the input argument "%s" into a frequency quantity!'%(sys.argv[i]))
            input_frequencies.append(freq)
        i += 1
    # 
    # check user input
    if len(input_frequencies) <= 0:
        usage()
        sys.exit()
    # 
    # prepare output list
    candiate_redshifts = []
    for ifreq, line_obsfreq in enumerate(input_frequencies):
        candiate_redshifts.append([])
    # 
    # check lines
    line_dict = get_line_dict(line_list=['CO', 'CI', 'CII'])
    sys.stdout.write('line_dict: ')
    print(line_dict)
    z_min = input_params['zmin']
    z_max = input_params['zmax']
    for line_name in line_dict:
        line_restfreq = line_dict[line_name]
        for ifreq, line_obsfreq in enumerate(input_frequencies):
            z = np.round((line_restfreq/line_obsfreq).value-1.0, 4)
            if z > z_min and z < z_max:
                candiate_redshifts[ifreq].append((z, line_name))
    # 
    # 
    sys.stdout.write('candiate_redshifts: ')
    print(candiate_redshifts)
    # 
    # print candidate lines left and right next to the input line
    nleft = 2
    nright = 2
    line_restfreqs_to_sort = [line_dict[key].to(u.GHz).value for key in line_dict]
    line_sort = np.argsort(line_restfreqs_to_sort)
    line_names_sorted = (np.array(list(line_dict.keys()))[line_sort]).tolist()
    print('line_names_sorted', line_names_sorted)
    print('looping each candidate redshift and print lines left and right of the input line:')
    for ifreq, line_obsfreq in enumerate(input_frequencies):
        icandidate_sorted = np.argsort([t[0] for t in candiate_redshifts[ifreq]])
        for icandidate in icandidate_sorted:
            z = candiate_redshifts[ifreq][icandidate][0]
            line_name = candiate_redshifts[ifreq][icandidate][1]
            indent_str = '    %d z=%s:'%(icandidate, z)
            sys.stdout.write(indent_str)
            sys.stdout.flush()
            iline = line_names_sorted.index(line_name)
            ileft = iline - nleft
            while ileft <= iline-1:
                if ileft >= 0:
                    line_name_x = line_names_sorted[ileft]
                    line_obsfreq_x = line_dict[line_name_x] / (1.+z)
                    sys.stdout.write(' '+str((line_name_x, line_obsfreq_x)))
                    sys.stdout.flush()
                ileft += 1
            sys.stdout.write(' '+str((line_name, line_obsfreq)))
            sys.stdout.flush()
            iright = iline + 1
            while iright <= iline+nright:
                if iright <= len(line_names_sorted):
                    line_name_x = line_names_sorted[iright]
                    line_obsfreq_x = line_dict[line_name_x] / (1.+z)
                    sys.stdout.write(' '+str((line_name_x, line_obsfreq_x)))
                    sys.stdout.flush()
                iright += 1
            sys.stdout.write('\n')
            sys.stdout.flush()
    



