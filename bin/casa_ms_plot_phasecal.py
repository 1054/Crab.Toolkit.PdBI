#!/usr/bin/env python
# 
# This code must be run in CASA
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil
import numpy as np


# 
# Check CASA environment
# 
if not ('casac' in globals() and 'tb' in globals()):
    raise Exception('Error! Please run this code in CASA!')
    #sys.exit()



# 
# Load vis and out from os.getenv
# 
if os.getenv('CASAMS_VIS') == None:
    raise Exception('Error! Please set system variable CASAMS_VIS in SHELL before calling CASA!')
if os.getenv('CASAMS_OUT') == None:
    raise Exception('Error! Please set system variable CASAMS_OUT in SHELL before calling CASA!')

vis = os.getenv('CASAMS_VIS')
out = os.getenv('CASAMS_OUT')

if not os.path.isdir(vis):
    raise Exception('Error! The input CASAMS_VIS "%s" does not exist!'%(vis))

if not os.path.isdir(out):
    os.makedirs(out)



# 
# Identify phasecal sources by reading STATE table
# 
tb.open(os.path.join(vis,'STATE'))
state_mode = tb.getcol('OBS_MODE').tolist()
state_index = []
state_intent = []
tb.close()
for i in range(len(state_mode)):
    if state_mode[i].find('CALIBRATE_PHASE') >= 0:
        state_index.append(i)
        state_intent.append(state_mode[i])
if len(state_index) == 0:
    raise Exception('Error! No phasecal was found!')
    #sys.exit()



# 
# Count spectral window number
# 
tb.open(os.path.join(vis,'SPECTRAL_WINDOW'))
spwcount = len(tb.rownumbers())
spwnchan = tb.getcol('NUM_CHAN').tolist()
spwnames = tb.getcol('NAME').tolist() #<20170113><dzliu># We should examine phase cal before and after cal
spwilist = [] #<20170113><dzliu># on the data product which has not been split yet
for spwi in range(spwcount): #<20170113><dzliu># i.e. named like "calibrated/working/uid___A002_Xb18ac0_X1b7e.ms"
    if spwnames[spwi].find('X0000000000#') < 0: #<20170113><dzliu># instead of "calibrated/uid___A002_Xb18ac0_X1b7e.ms.split.cal"
        if spwnames[spwi].find('#ALMA_') >= 0: #<20170113><dzliu># instead of "calibrated/uid___A002_Xb18ac0_X1b7e.ms.split.cal"
            if spwnames[spwi].find('#BB_') >= 0: #<20170113><dzliu># In the latter split data product, DATA column has already 
                if spwnames[spwi].find('#FULL_RES') >= 0: #<20170113><dzliu># been filled with CORRECTED_DATA column. 
                    spwilist.append(spwi) #<20170113><dzliu># 
tb.close()



# 
# List fields
# 
tb.open(os.path.join(vis,'FIELD'))
field_names = tb.getcol('NAME').tolist()
field_index = range(len(field_names))
tb.close()



# 
# plotms
print('Plotting phase vs. uvdist for phasecal')
for i in range(len(loop_found_tuple)): 
    for spwi in spwilist:  #<20170113><dzliu># 
        source = sources[loop_found_tuple[i][0]]
        intent = intents[loop_found_tuple[i][1]]
        plotms( 
            vis         = vis, 
            xaxis       = 'uvdist', 
            yaxis       = 'phase', 
            field       = '%s'%(source), 
            spw         = '%d'%(spwi), 
            avgchannel  = '%d'%(spwnchan[spwi]), 
            avgtime     = '31536000',  #<TODO># time averaging
            intent      = '%s'%(intent), 
            coloraxis   = 'baseline', 
            ydatacolumn = 'data', 
            plotrange   = [0,0,-270,270], 
            plotfile    = '${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d.png'%(source,spwi), 
            overwrite   =  True 
        )
        os.system('echo \"source = %s\" >  \"%s\"'%(source,'${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d.txt'%(source,spwi)))
        os.system('echo \"intent = %s\" >> \"%s\"'%(intent,'${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d.txt'%(source,spwi)))
        os.system('cat \"%s\"'%('${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d.txt'%(source,spwi)))
        os.system('ls  \"%s\"'%('${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d.png'%(source,spwi)))

# 
# -- plotms
print('Plotting phase vs. uvdist for phasecal (corrected)')
for i in range(len(loop_found_tuple)): 
    for spwi in spwilist:  #<20170113><dzliu># 
        source = sources[loop_found_tuple[i][0]]
        intent = intents[loop_found_tuple[i][1]]
        plotms( 
            vis         = '${CASAMS_VIS}${CASAMS_VIS_SFIX}', 
            xaxis       = 'uvdist', 
            yaxis       = 'phase', 
            field       = '%s'%(source), 
            spw         = '%d'%(spwi), 
            avgchannel  = '%d'%(spwnchan[spwi]), 
            avgtime     = '31536000',  #<TODO># time averaging
            intent      = '%s'%(intent), 
            coloraxis   = 'baseline', 
            ydatacolumn = 'corrected', 
            plotrange   = [0,0,-270,270], 
            plotfile    = '${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d_corrected.png'%(source,spwi), 
            overwrite   =  True 
        )
        os.system('echo \"source = %s\" >  \"%s\"'%(source,'${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d_corrected.txt'%(source,spwi)))
        os.system('echo \"intent = %s\" >> \"%s\"'%(intent,'${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d_corrected.txt'%(source,spwi)))
        os.system('cat \"%s\"'%('${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d_corrected.txt'%(source,spwi)))
        os.system('ls  \"%s\"'%('${CASAMS_OUT}/Phase_vs_uvdist_Source_%s_spw_%d_corrected.png'%(source,spwi)))

# 
# -- plotms
print('Plotting phase vs. time for phasecal')
for i in range(len(loop_found_tuple)): 
    for spwi in spwilist:  #<20170113><dzliu># 
        source = sources[loop_found_tuple[i][0]]
        intent = intents[loop_found_tuple[i][1]]
        plotms( 
            vis         = '${CASAMS_VIS}${CASAMS_VIS_SFIX}', 
            xaxis       = 'time', 
            yaxis       = 'phase', 
            field       = '%s'%(source), 
            spw         = '%d'%(spwi), 
            antenna     = '',  #<TODO># antenna = 'DA44&*'
            avgchannel  = '%d'%(spwnchan[spwi]), 
            intent      = '%s'%(intent), 
            coloraxis   = 'baseline', 
            ydatacolumn = 'data', 
            plotrange   = [0,0,-270,270], 
            plotfile    = '${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d.png'%(source,spwi), 
            overwrite   =  True 
        )
        os.system('echo \"source = %s\" >  \"%s\"'%(source,'${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d.txt'%(source,spwi)))
        os.system('echo \"intent = %s\" >> \"%s\"'%(intent,'${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d.txt'%(source,spwi)))
        os.system('cat \"%s\"'%('${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d.txt'%(source,spwi)))
        os.system('ls  \"%s\"'%('${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d.png'%(source,spwi)))

# 
# -- plotms
print('Plotting phase vs. time for phasecal (corrected)')
for i in range(len(loop_found_tuple)): 
    for spwi in spwilist:  #<20170113><dzliu># 
        source = sources[loop_found_tuple[i][0]]
        intent = intents[loop_found_tuple[i][1]]
        plotms( 
            vis         = '${CASAMS_VIS}${CASAMS_VIS_SFIX}', 
            xaxis       = 'time', 
            yaxis       = 'phase', 
            field       = '%s'%(source), 
            spw         = '%d'%(spwi), 
            antenna     = '',  #<TODO># antenna = 'DA44&*'
            avgchannel  = '%d'%(spwnchan[spwi]), 
            intent      = '%s'%(intent), 
            coloraxis   = 'baseline', 
            ydatacolumn = 'corrected', 
            plotrange   = [0,0,-270,270], 
            plotfile    = '${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d_corrected.png'%(source,spwi), 
            overwrite   =  True 
        )
        os.system('echo \"source = %s\" >  \"%s\"'%(source,'${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d_corrected.txt'%(source,spwi)))
        os.system('echo \"intent = %s\" >> \"%s\"'%(intent,'${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d_corrected.txt'%(source,spwi)))
        os.system('cat \"%s\"'%('${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d_corrected.txt'%(source,spwi)))
        os.system('ls  \"%s\"'%('${CASAMS_OUT}/Phase_vs_time_Source_%s_spw_%d_corrected.png'%(source,spwi)))



    
    
