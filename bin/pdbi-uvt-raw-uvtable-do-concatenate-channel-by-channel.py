#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re
import numpy as np
import astropy
from astropy.table import Table
from astropy.io import fits
from copy import copy
import shutil

# 
# read user input
uvt_names = []
out_name = ''
iarg = 1
arg_mode = ''
while iarg < len(sys.argv):
    arg_str = sys.argv[iarg].lower().replace('--','-')
    if arg_str == '-name':
        arg_mode = 'name'
        iarg += 1
        continue
    elif arg_str == '-out':
        arg_mode = 'out'
        iarg += 1
        continue
    # 
    if arg_mode == 'name':
        uvt_names.append(re.sub(r'(.*?)\.uvt', r'\1', sys.argv[iarg]))
    if arg_mode == 'out':
        out_name = re.sub(r'(.*?)\.uvt', r'\1', sys.argv[iarg])
    # 
    iarg += 1


# 
# print usage
if len(uvt_names) == 0 or out_name == '':
    print('Usage: ')
    print('  pdbi-uvt-raw-uvtable-do-concatenate-channel-by-channel.py -name uvtable_spw1_resampled.uvt uvtable_spw2_resampled.uvt uvtable_spw3_resampled.uvt -out output_merged_data_cube.uvt')
    print('  -- this code will concatenate visibilities in the input uv tables which have the same channel number, i.e., same spectral window (spw) data from multiple observations.')
    sys.exit()


# 
# loop the input uvtables
global_hdu = None
global_datamax = None
global_datamin = None
global_bscale = None
previous_data_shape = None
for i_uvt in range(len(uvt_names)):
    uvt_name = uvt_names[i_uvt]
    # 
    # convert uvt to uvfits
    if not os.path.isfile(uvt_name+'.uvfits'):
        print('Running: echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
        os.system('echo "fits {0}.uvfits from {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(uvt_name))
    if not os.path.isfile(uvt_name+'.uvfits'):
        print('Error! Failed to call GILDAS/mapping to convert "{0}.uvt" to "{0}.uvfits"!'.format(uvt_name))
        sys.exit()
    # 
    # read uvfits 
    print('Reading '+uvt_name+'.uvfits')
    hdulist = fits.open(uvt_name+'.uvfits')
    if type(hdulist[0]) != fits.GroupsHDU:
        print('Error! The uvfits file "{0}.uvfits" is not fits.GroupsHDU type!'.format(uvt_name))
        sys.exit()
    hdu = hdulist[0]
    print(hdu.columns)
    #print(len(hdu.data))
    #print(hdu.data.shape)
    #print(len(hdu.data[0]))
    #print(hdu.data[0]['DATA'].shape)
    #print(type(hdu.data[0]['DATA']))
    #print(type(hdu.data))
    #hdu.data.sort(order=['UU','VV','WW'])
    # 
    # check n_chan consistency
    if previous_data_shape is None:
        previous_data_shape = hdu.data['DATA'].shape
    elif not np.array_equal(previous_data_shape[1:], hdu.data['DATA'].shape[1:]):
        print('Error! The input uvfits file do not have matched number of channel and stokes!')
        print('previous_data_shape = %s, current_data_shape = %s'%(str(previous_data_shape), str(hdu.data['DATA'].shape)))
        sys.exit()
    # 
    # concatenate
    if global_hdu is None:
        global_hdu = hdu.copy()
        #print(type(global_hdu))
        #print(type(global_hdu.data))
        # 
        # deal with datamin datamax bscale
        global_datamin = global_hdu.header['DATAMIN']
        global_datamax = global_hdu.header['DATAMAX']
        global_bscale = global_hdu.header['BSCALE']
    else:
        previous_nrows = global_hdu.data.shape[0]
        current_nrows = hdu.data.shape[0]
        new_data_shape = list(global_hdu.data.data.shape)
        new_data_shape[0] = previous_nrows + current_nrows
        new_data_shape = tuple(new_data_shape)
        #print(global_hdu.columns)
        #print(global_hdu._populate_table_keywords())
        
        #global_hdu.columns[global_hdu.columns.names.index('DATA')].dim = str(global_hdu.columns[global_hdu.columns.names.index('DATA')].dim)
        ##global_hdu.columns[global_hdu.columns.names.index('DATA')].bscale = 1.0
        ##global_hdu.columns[global_hdu.columns.names.index('DATA')].bzero = 1.0
        #print(global_hdu.columns)
        #global_hdu = fits.BinTableHDU.from_columns(global_hdu.columns, nrows=previous_nrows+current_nrows) # see -- http://docs.astropy.org/en/stable/io/fits/usage/table.html "Appending Tables"
        #for key in global_hdu.columns.names:
        #    global_hdu.data[key][previous_nrows:] = hdu.data[key]
        
        ##new_data_shape = global_hdu.data.shape
        ##new_data_shape[0] = previous_nrows + current_nrows
        #c1 = fits.Column(name=global_hdu.columns[0].name, format=global_hdu.columns[0].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[0]],hdu.data[hdu.columns.names[0]])) )
        #c2 = fits.Column(name=global_hdu.columns[1].name, format=global_hdu.columns[1].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[1]],hdu.data[hdu.columns.names[1]])) )
        #c3 = fits.Column(name=global_hdu.columns[2].name, format=global_hdu.columns[2].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[2]],hdu.data[hdu.columns.names[2]])) )
        #c4 = fits.Column(name=global_hdu.columns[3].name, format=global_hdu.columns[3].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[3]],hdu.data[hdu.columns.names[3]])) )
        #c5 = fits.Column(name=global_hdu.columns[4].name, format=global_hdu.columns[4].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[4]],hdu.data[hdu.columns.names[4]])) )
        #c6 = fits.Column(name=global_hdu.columns[5].name, format=global_hdu.columns[5].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[5]],hdu.data[hdu.columns.names[5]])) )
        #c7 = fits.Column(name=global_hdu.columns[6].name, format=global_hdu.columns[6].format, array=np.concatenate((global_hdu.data[global_hdu.columns.names[6]],hdu.data[hdu.columns.names[6]])), dim=str(global_hdu.columns[6].dim) )
        ##print(c1, c2, c3, c4, c5, c6, c7)
        #global_hdu = fits.BinTableHDU.from_columns(fits.ColDefs([c1, c2, c3, c4, c5, c6, c7]))
        #print(global_hdu.columns)
        
        #updated_data_array = global_hdu.data
        #for key in global_hdu.columns.names:
        #    print(type(updated_data_array.field(key)))
        #    print(type(updated_data_array[key]))
        #    updated_data_array[key] = np.concatenate((updated_data_array.field(key),hdu.data.field(key)))
        #global_hdu.data = updated_data_array
        
        #data_array = np.append(fits.FITS_rec(global_hdu.data),hdu.data) # http://docs.astropy.org/en/stable/_modules/astropy/io/fits/fitsrec.html#FITS_rec
        #print(type(data_array), data_array.shape)
        ##for key in global_hdu.columns.names:
        ##    data_array[key] = np.concatenate((global_hdu.data[key], hdu.data[key]))
        #print(type(global_hdu.data))
        #global_hdu = fits.hdu.groups.GroupData(fits.FITS_rec(data_array)) # http://docs.astropy.org/en/stable/_modules/astropy/io/fits/hdu/groups.html#GroupData
        #print(type(global_hdu.data))
        
        #print(list(global_hdu.header))
        #global_hdu.columns[global_hdu.columns.names.index('DATA')].dim = None
        #global_hdu = fits.BinTableHDU.from_columns(global_hdu.columns, header=global_hdu.header, nrows=previous_nrows+current_nrows) # see -- http://docs.astropy.org/en/stable/io/fits/usage/table.html "Appending Tables"
        #print(list(global_hdu.header))
        #for key in global_hdu.columns.names:
        #    global_hdu.data[key][previous_nrows:] = hdu.data[key]
        
        print('global_hdu.data', type(global_hdu.data), global_hdu.data.shape)
        print('global_hdu.data.data', type(global_hdu.data.data), global_hdu.data.data.shape)
        #concat_array = np.concatenate((global_hdu.data.data, hdu.data.data))
        global_hdu.data.resize((new_data_shape[0]))
        global_hdu.data.data.resize(new_data_shape)
        #print(global_hdu.data.pardata)
        for key in global_hdu.columns.names:
            global_hdu.data[key][previous_nrows:] = hdu.data[key]
        #global_hdu.data.data[:] = concat_array[:]
        print(global_hdu.data.data[2075][0][0][0][5], global_hdu.data.field('UU')[2075])
        #concat_array = np.concatenate((global_hdu.data.data, hdu.data.data))
        #global_hdu.data[:] = concat_array[:]
        print('global_hdu.data', type(global_hdu.data), global_hdu.data.shape)
        print('global_hdu.data.data', type(global_hdu.data.data), global_hdu.data.data.shape)
        
        concat_header = global_hdu.header
        #print(concat_header['PCOUNT'])
        #print(concat_header['GCOUNT'])
        global_hdu.header['GCOUNT'] = previous_nrows + current_nrows
        #print(global_hdu.header['PCOUNT'])
        #print(global_hdu.header['GCOUNT'])
        
        print(global_hdu.data.shape)
        
        #print(concat_array.dtype.names)
        #print(concat_array.dtype.fields)
        #print(global_hdu.data.parnames)
        #print(fits.GroupsHDU(data = fits.GroupData(input=concat_array, 
        #                                           bscale=global_hdu.data.bscale), 
        #                                           parnames=global_hdu.data.parnames, 
        #                                           pardata=global_hdu.data.pardata, 
        #                     header = concat_header))
        #global_hdu.data = fits.FITS_rec(concat_array)
        #print(global_hdu.header['PCOUNT'])
        #print(global_hdu.header['GCOUNT'])
        
        
        # 
        # also deal with datamin datamax bscale
        if hdu.header['DATAMIN'] < global_datamin:
            global_datamin = hdu.header['DATAMIN']
        if hdu.header['DATAMAX'] > global_datamax:
            global_datamax = hdu.header['DATAMAX']
        if hdu.header['BSCALE'] > global_bscale:
            global_bscale = hdu.header['BSCALE']
    

# 
# store datamin datamax bscale
global_hdu.header['DATAMIN'] = global_datamin
global_hdu.header['DATAMAX'] = global_datamax
global_hdu.header['BSCALE'] = global_bscale # otherwise overflow because ['DATA'] is stored in J (32-bit integer) format -- http://docs.astropy.org/en/stable/_modules/astropy/io/fits/column.html
global_hdu.columns['DATA'].bscale = global_hdu.header['BSCALE'] # otherwise overflow because ['DATA'] is stored in J (32-bit integer) format -- http://docs.astropy.org/en/stable/_modules/astropy/io/fits/column.html


# 
# Print global_hdu info
print('global_hdu.columns = %s'%(global_hdu.columns))
print('global_hdu.data.data.shape = %s'%(str(global_hdu.data.data.shape)))
# dim = (1, 1, 1, 132, 1, 3)
#        IF
#           RA
#              DEC
#                 CHAN
#                     STOKES
#                         RE,IM,WT
# 


#n_visi = global_hdu.data['DATA'].shape[0]
#n_chan = global_hdu.data['DATA'][0][0][0][0].shape[0]
#n_stokes = global_hdu.data['DATA'][0][0][0][0][0].shape[0]



# 
# Save as new uvfits and uvt
if os.path.isfile(out_name+'.uvfits'):
    print('Found existing "{0}"! Backup it as "{0}.uvfits.backup"!'.format(out_name))
    shutil.move(out_name+'.uvfits', out_name+'.uvfits.backup')
global_hdu.writeto(out_name+'.uvfits', overwrite=True)
# then convert uvfits to uvt
if os.path.isfile(out_name+'.uvfits'):
    print('Output to "{0}.uvfits"!'.format(out_name))
    # check existing file
    if os.path.isfile(out_name+'.uvt'):
        print('Backing-up existing {0}.uvt as {0}.uvt.backup'.format(out_name))
        os.system('mv {0}.uvt {0}.uvt.backup'.format(out_name))
    # run gildas/mapping
    if os.path.isfile(out_name+'.uvfits'):
        print('Running: echo "fits {0}.uvfits to {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(out_name))
        os.system('echo "fits {0}.uvfits to {0}.uvt /style casa" | mapping -nw -nl > {0}.uvfits.stdout.txt'.format(out_name))
    # check output file
    if os.path.isfile(out_name+'.uvt'):
        print('Output to "{0}.uvt"!'.format(out_name))
        print('Done!')
    else:
        print('Error! Failed to output {0}.uvt!'.format(out_name))
else:
    print('Error! Failed to output {0}.uvfits!'.format(out_name))










