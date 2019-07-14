#!/usr/bin/env python
# 
# This code must be run in CASA
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil, pprint
import numpy as np
import astropy
try:
    import casacore # pip install python-casacore # documentation: http://casacore.github.io/python-casacore/
except:
    raise ImportError('Could not import casacore! Please install it via \'pip install python-casacore!\'')

from casacore.tables import table, taql





# 
# class json_interferometry_info_dict_encoder(json.JSONEncoder)
# -- for json dump and load 
# -- https://stackoverflow.com/questions/27050108/convert-numpy-type-to-python
# 
class json_interferometry_info_dict_encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(json_interferometry_info_dict_encoder, self).default(obj)



# 
# grab_interferometry_info
# 
def grab_interferometry_info(vis, info_dict_file = ''):
    # 
    # set info_dict file name
    if info_dict_file == '':
        info_dict_file = re.sub(r'\.ms$', r'', vis, re.IGNORECASE) + '.info.dict.json'
    # 
    # check existing info_dict file, if it exists, then load it and return, so that we do not repeat the analysis.
    if os.path.isfile(info_dict_file):
        #try:
        if True:
            print('Loading info_dict from "%s"'%(info_dict_file))
            with open(info_dict_file, 'r') as fp:
                info_dict = json.load(fp)
                fp.close()
                # print
                #print_interferometry_info_dict(info_dict)
                # return info_dict
                return info_dict
        #except:
        #    print('Failed to load info_dict from "%s"! Will continue to reprepare it!'%(info_dict_file))
        #    pass
    # 
    # print
    print('Preparing info_dict for "%s"'%(vis))
    # 
    # open table
    tb = table(vis) # open table tb1
    # 
    # test
    #print(tb.getkeywords())
    #print(tb.colnames())
    # 
    # prepare variables
    missing_keywords = []
    info_dict = {}
    info_dict['ANTENNA'] = {}
    info_dict['ANTENNA']['ID'] = []
    info_dict['ANTENNA']['OFFSET'] = []
    info_dict['ANTENNA']['POSITION'] = []
    info_dict['ANTENNA']['DISH_DIAMETER'] = []
    info_dict['FIELD'] = {} # unique source names
    info_dict['FIELD']['ID'] = []
    info_dict['FIELD']['SOURCE_ID'] = []
    info_dict['FIELD']['NAME'] = []
    info_dict['SOURCE'] = {} # source each with different spw and direction (mosaic)
    info_dict['SOURCE']['ID'] = []
    info_dict['SOURCE']['NAME'] = []
    info_dict['SOURCE']['SOURCE_ID'] = []
    info_dict['SOURCE']['SPW_ID'] = []
    info_dict['SPW'] = {} # spw
    info_dict['SPW']['ID'] = []
    info_dict['SPW']['NAME'] = []
    info_dict['SPW']['NUM_CHAN'] = []
    info_dict['DATA_DESC'] = {} # data_desc
    info_dict['DATA_DESC']['SPW_ID'] = {} # SPW_ID for each data row
    # 
    # get ANTENNA
    if 'ANTENNA' in tb.getkeywords():
        tb2 = table(tb.getkeyword('ANTENNA')) # open table tb2
        #print(tb2.colnames()) # ['OFFSET', 'POSITION', 'TYPE', 'DISH_DIAMETER', 'FLAG_ROW', 'MOUNT', 'NAME', 'STATION']
        info_dict['ANTENNA']['ID'] = np.arange(0,tb2.nrows()).astype(int)
        info_dict['ANTENNA']['OFFSET'] = tb2.getcol('OFFSET')
        info_dict['ANTENNA']['POSITION'] = tb2.getcol('POSITION')
        info_dict['ANTENNA']['DISH_DIAMETER'] = tb2.getcol('DISH_DIAMETER')
        tb2.close() # close table tb2
    else:
        missing_keywords.append('ANTENNA')
    # 
    # get FIELD
    if 'FIELD' in tb.getkeywords():
        tb2 = table(tb.getkeyword('FIELD')) # open table tb2
        #print(tb2.colnames()) # ['DELAY_DIR', 'PHASE_DIR', 'REFERENCE_DIR', 'CODE', 'FLAG_ROW', 'NAME', 'NUM_POLY', 'SOURCE_ID', 'TIME']
        info_dict['FIELD']['ID'] = np.arange(0,tb2.nrows()).astype(int)
        info_dict['FIELD']['SOURCE_ID'] = tb2.getcol('SOURCE_ID')
        info_dict['FIELD']['NAME'] = tb2.getcol('NAME')
        tb2.close() # close table tb2
    else:
        missing_keywords.append('FIELD')
    # 
    # get SOURCE
    if 'SOURCE' in tb.getkeywords():
        tb2 = table(tb.getkeyword('SOURCE')) # open table tb2
        #print(tb2.colnames()) # ['DIRECTION', 'PROPER_MOTION', 'CALIBRATION_GROUP', 'CODE', 'INTERVAL', 'NAME', 'NUM_LINES', 'SOURCE_ID', 'SPECTRAL_WINDOW_ID', 'TIME', 'POSITION', 'REST_FREQUENCY', 'SYSVEL', 'TRANSITION', 'SOURCE_MODEL']
        info_dict['SOURCE']['ID'] = np.arange(0,tb2.nrows()).astype(int)
        info_dict['SOURCE']['NAME'] = tb2.getcol('NAME')
        info_dict['SOURCE']['SOURCE_ID'] = tb2.getcol('SOURCE_ID')
        info_dict['SOURCE']['SPW_ID'] = tb2.getcol('SPECTRAL_WINDOW_ID')
        tb2.close() # close table tb2
    else:
        missing_keywords.append('SOURCE')
    # 
    # get DATA_DESCRIPTION
    if 'DATA_DESCRIPTION' in tb.getkeywords():
        tb2 = table(tb.getkeyword('DATA_DESCRIPTION')) # open table tb2
        #print(tb2.colnames()) # ['MEAS_FREQ_REF', 'CHAN_FREQ', 'REF_FREQUENCY', 'CHAN_WIDTH', 'EFFECTIVE_BW', 'RESOLUTION', 'FLAG_ROW', 'FREQ_GROUP', 'FREQ_GROUP_NAME', 'IF_CONV_CHAIN', 'NAME', 'NET_SIDEBAND', 'NUM_CHAN', 'TOTAL_BANDWIDTH']
        info_dict['DATA_DESC']['ID'] = np.arange(0,tb2.nrows()).astype(int)
        info_dict['DATA_DESC']['SPW_ID'] = tb2.getcol('SPECTRAL_WINDOW_ID')
        info_dict['DATA_DESC']['STOKES_ID'] = tb2.getcol('POLARIZATION_ID')
        tb2.close() # close table tb2
    else:
        missing_keywords.append('DATA_DESCRIPTION')
    # 
    # get SPECTRAL_WINDOW
    if 'SPECTRAL_WINDOW' in tb.getkeywords():
        tb2 = table(tb.getkeyword('SPECTRAL_WINDOW')) # open table tb2
        #print(tb2.colnames()) # ['MEAS_FREQ_REF', 'CHAN_FREQ', 'REF_FREQUENCY', 'CHAN_WIDTH', 'EFFECTIVE_BW', 'RESOLUTION', 'FLAG_ROW', 'FREQ_GROUP', 'FREQ_GROUP_NAME', 'IF_CONV_CHAIN', 'NAME', 'NET_SIDEBAND', 'NUM_CHAN', 'TOTAL_BANDWIDTH']
        info_dict['SPW']['ID'] = np.arange(0,tb2.nrows()).astype(int)
        info_dict['SPW']['NAME'] = tb2.getcol('NAME')
        info_dict['SPW']['NUM_CHAN'] = tb2.getcol('NUM_CHAN')
        info_dict['SPW']['DATA_DESC_ID'] = []
        info_dict['SPW']['PRIMARY_BEAM'] = [] # in units of degrees
        info_dict['SPW']['CHAN_PRIMARY_BEAM'] = [] # in units of degrees, should be a 2D array
        info_dict['SPW']['CHAN_FREQ'] = [] # should be a 2D array. 
        for k2 in range(tb2.nrows()):
            info_dict['SPW']['DATA_DESC_ID'].append( np.argwhere( info_dict['DATA_DESC']['SPW_ID'] == k2 ).flatten() ) # indicates which DATA_DESC_ID(s) correspond to current SPW_ID
            info_dict['SPW']['CHAN_FREQ'].append( tb2.getcell('CHAN_FREQ', k2) ) # in units of Hz
            info_dict['SPW']['CHAN_PRIMARY_BEAM'].append( 1.13  * (2.99792458e8/info_dict['SPW']['CHAN_FREQ'][k2]) / (np.min(info_dict['ANTENNA']['DISH_DIAMETER'])) / np.pi * 180.0 ) # in units of degrees
            info_dict['SPW']['PRIMARY_BEAM'].append( np.mean( info_dict['SPW']['CHAN_PRIMARY_BEAM'][-1] ) )
        tb2.close() # close table tb2
    else:
        missing_keywords.append('SPECTRAL_WINDOW')
    # 
    # check missing_keywords and exit on error
    if len(missing_keywords) > 0:
        print('Error! Could not find following keywords in the input vis "%s":'%(vis))
        print('    ' + ', '.join(missing_keywords))
        tb.close() # close table on error
        sys.exit() # exit on error
    # 
    # 
    # 
    # determine data column
    #print(tb.colnames())
    if 'CORRECTED_DATA' in tb.colnames():
        data_column = 'CORRECTED_DATA'
    else:
        data_column = 'DATA'
    print('Data column is "%s"'%(data_column))
    # 
    # determine query_str
    query_where_str = "(FLAG_ROW==FALSE)"
    # 
    # determine field. If user has input a field, use it, otherwise loop all fields. 
    #if field != '':
    #    field_list = [field]
    #else:
    #    field_list = info_dict['FIELD']['NAME']
    # 
    # just loop all fields
    field_list = info_dict['FIELD']['NAME']
    # 
    # loop field
    for field in field_list:
        print('Looping field %s in the field_list %s'%(field, field_list))
        # 
        # check field name
        if field in info_dict['FIELD']['NAME']:
            query_field_id = info_dict['FIELD']['ID'][ info_dict['FIELD']['NAME'].index(field) ]
            query_where_str3 = query_where_str + ' AND (FIELD_ID==%d)'%(query_field_id)
        else:
            print('Error! The input field "%s" is not in the FIELD table of the input data "%s"!'%(field, vis))
            tb.close() # close table on error
            sys.exit()
        # 
        # select rows
        tb3 = taql("SELECT UVW, "+data_column+", DATA_DESC_ID, EXPOSURE, TIME FROM $tb WHERE ("+query_where_str3+")") # open table tb3
        print('Selected %d rows with "%s" (field=%s)'%(tb3.nrows(), query_where_str3, field ) )
        if tb3.nrows() <= 0:
            print('Error! No data found with "%s"!'%(query_where_str3))
            tb3.close() # close table on error
            tb.close() # close table on error
            sys.exit()
        #print('DATA', type(tb3.getcol('DATA')), tb3.getcol('DATA').shape) # shape (nrow, nchan, nstokes)
        #print('DATA[0,:]', type(tb3.getcol('DATA')[0,:]), tb3.getcol('DATA')[0,:].shape) # 
        #print('DATA[0,0,:]', type(tb3.getcol('DATA')[0,0,:]), tb3.getcol('DATA')[0,0,:].shape) # 2 polarization
        #print('DATA[0,0,0]', type(tb3.getcol('DATA')[0,0,0]), tb3.getcol('DATA')[0,0,0]) # complex
        # 
        # check stokes
        number_of_stokes = -1
        #data_shape = tb3.getcol(data_column).shape
        #if len(data_shape) < 2:
        #    print('Error! Data has a wrong dimension of %s!'%(data_shape))
        #    tb3.close() # close table on error
        #    tb.close() # close table on error
        #    sys.exit()
        #elif len(data_shape) == 2:
        #    print('Warning! Data has a dimension of %s and no polarization dimension!'%(data_shape))
        #    number_of_stokes = 0
        #else:
        #    if data_shape[2] == 1:
        #        number_of_stokes = 1
        #    elif data_shape[2] == 2:
        #        number_of_stokes = 2
        #    else:
        #        print('Error! Data has a wrong polarization dimension of %s which should be 1 or 2!'%(data_shape[2]))
        #        tb3.close() # close table on error
        #        tb.close() # close table on error
        #        sys.exit()
        data_shape = tb3.getcell(data_column, int(tb3.nrows()/2) ).shape # this is faster than getting the full data_column column
        if len(data_shape) == 1:
            print('Warning! Data cell has a dimension of %s and no polarization dimension!'%(data_shape))
            number_of_stokes = 0
        elif len(data_shape) == 2:
            if data_shape[-1] == 1:
                number_of_stokes = 1
            elif data_shape[-1] == 2:
                number_of_stokes = 2
            else:
                print('Error! Data cell has a wrong polarization dimension of %s which should be 1 or 2!'%(data_shape[-1]))
                tb3.close() # close table on error
                tb.close() # close table on error
                sys.exit()
        else:
            print('Error! Data cell has a wrong dimension of %s which should be (Nchan, Nstokes)!'%(data_shape))
            tb3.close() # close table on error
            tb.close() # close table on error
            sys.exit()
        # 
        # prepare dict entry
        # -- each FIELD has its own UV coverage (due to flagging)
        # -- and SPW (although they are the same)
        fieldKey = 'FIELD_'+field
        info_dict[fieldKey] = {}
        info_dict[fieldKey]['UVW'] = {}
        info_dict[fieldKey]['SPW'] = {}
        # 
        # get (u,v,w)
        print('Getting UVW info')
        data_UVW = tb3.getcol('UVW')
        info_dict[fieldKey]['UVW']['U_MAX'] = np.max(data_UVW[:,0])
        info_dict[fieldKey]['UVW']['U_MIN'] = np.max(data_UVW[:,1])
        info_dict[fieldKey]['UVW']['V_MAX'] = np.max(data_UVW[:,2])
        info_dict[fieldKey]['UVW']['V_MIN'] = np.min(data_UVW[:,0])
        info_dict[fieldKey]['UVW']['W_MAX'] = np.min(data_UVW[:,1])
        info_dict[fieldKey]['UVW']['W_MIN'] = np.min(data_UVW[:,2])
        info_dict[fieldKey]['UVW']['U_ABSMAX'] = np.max( np.abs(data_UVW[:,0]) )
        info_dict[fieldKey]['UVW']['U_ABSMIN'] = np.max( np.abs(data_UVW[:,1]) )
        info_dict[fieldKey]['UVW']['V_ABSMAX'] = np.max( np.abs(data_UVW[:,2]) )
        info_dict[fieldKey]['UVW']['V_ABSMIN'] = np.min( np.abs(data_UVW[:,0]) )
        info_dict[fieldKey]['UVW']['W_ABSMAX'] = np.min( np.abs(data_UVW[:,1]) )
        info_dict[fieldKey]['UVW']['W_ABSMIN'] = np.min( np.abs(data_UVW[:,2]) )
        # 
        # loop spw and calc rms per channel
        print('Getting SPW info')
        info_dict[fieldKey]['SPW']['ID'] = []
        info_dict[fieldKey]['SPW']['NAME'] = []
        info_dict[fieldKey]['SPW']['CHAN_FREQ'] = [] # in units of Hz, should be a 2D array
        info_dict[fieldKey]['SPW']['PRIMARY_BEAM'] = [] # in units of degrees
        info_dict[fieldKey]['SPW']['CHAN_PRIMARY_BEAM'] = []  # in units of degrees, should be a 2D array
        info_dict[fieldKey]['SPW']['RMS'] = [] # in units of Jy/beam
        info_dict[fieldKey]['SPW']['CHAN_RMS'] = [] # in units of Jy/beam, should be a 2D array
        if number_of_stokes >= 1:
            info_dict[fieldKey]['SPW']['RMS_STOKES_RR'] = [] # in units of Jy/beam
            info_dict[fieldKey]['SPW']['RMS_STOKES_LL'] = [] # in units of Jy/beam
            info_dict[fieldKey]['SPW']['CHAN_RMS_STOKES_RR'] = [] #in units of Jy/beam,  should be a 2D array
            info_dict[fieldKey]['SPW']['CHAN_RMS_STOKES_LL'] = [] #in units of Jy/beam,  should be a 2D array
        info_dict[fieldKey]['SPW']['EXPOSURE_X_BASELINE'] = []
        info_dict[fieldKey]['SPW']['NUM_SCAN_X_BASELINE'] = []
        info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'] = []
        info_dict[fieldKey]['SPW']['NUM_STOKES'] = []
        info_dict[fieldKey]['SPW']['BMAJ'] = [] # in units of degrees
        info_dict[fieldKey]['SPW']['BMIN'] = [] # in units of degrees
        info_dict[fieldKey]['SPW']['CHAN_BMAJ'] = [] # in units of degrees, should be a 2D array
        info_dict[fieldKey]['SPW']['CHAN_BMIN'] = [] # in units of degrees, should be a 2D array
        for ispw in range(len(info_dict['SPW']['ID'])):
            print('Looping ispw %d spw %d spw name %s'%(ispw, info_dict['SPW']['ID'][ispw], info_dict['SPW']['NAME'][ispw]))
            # 
            # select spw
            if len(info_dict['SPW']['DATA_DESC_ID'][ispw]) <= 0:
                continue
            query_where_str4 = '(DATA_DESC_ID in [%s])'%( ','.join( map( str, info_dict['SPW']['DATA_DESC_ID'][ispw] ) ) )
            tb4 = taql("SELECT * FROM $tb3 WHERE ("+query_where_str4+")") # open table tb4
            print('Selected %d rows with "%s" (ispw==%d, spw=%d)'%(tb4.nrows(), query_where_str4, ispw, info_dict['SPW']['ID'][ispw] ) )
            # 
            # check nrows
            if tb4.nrows() <= 0:
                tb4.close() # close table on error
                continue
            # 
            # copy SPW ID NAME CHAN_FREQ PRIMARY_BEAM CHAN_PRIMARY_BEAM
            info_dict[fieldKey]['SPW']['ID'].append( info_dict['SPW']['ID'][ispw] )
            info_dict[fieldKey]['SPW']['NAME'].append( info_dict['SPW']['NAME'][ispw] )
            info_dict[fieldKey]['SPW']['CHAN_FREQ'].append( info_dict['SPW']['CHAN_FREQ'][ispw] )
            info_dict[fieldKey]['SPW']['PRIMARY_BEAM'].append( info_dict['SPW']['PRIMARY_BEAM'][ispw] )
            info_dict[fieldKey]['SPW']['CHAN_PRIMARY_BEAM'].append( info_dict['SPW']['CHAN_PRIMARY_BEAM'][ispw] )
            # 
            # calc rms per spw per channel
            if number_of_stokes == 2:
                data_array = tb4.getcol(data_column)
                print('data_array.shape', data_array.shape)
                data_stokesLL = data_array[:,:,0] # DATA shape (nrow, nchan, nstokes) and nstokes==2
                data_stokesRR = data_array[:,:,1] # DATA shape (nrow, nchan, nstokes) and nstokes==2
                data_stokesLL_abs = np.absolute(data_stokesLL)
                data_stokesRR_abs = np.absolute(data_stokesRR)
                data_stokesLL_abs_mean = np.mean(data_stokesLL_abs, axis=0)
                data_stokesRR_abs_mean = np.mean(data_stokesRR_abs, axis=0)
                data_stokesLL_rms_per_chan = np.std(data_stokesLL_abs - data_stokesLL_abs_mean, axis=0)
                data_stokesRR_rms_per_chan = np.std(data_stokesRR_abs - data_stokesRR_abs_mean, axis=0)
                #print('data_stokesLL_rms_per_chan = %s'%(data_stokesLL_rms_per_chan) )
                #print('data_stokesRR_rms_per_chan = %s'%(data_stokesRR_rms_per_chan) )
                data_stokesLL_rms_all = np.std(data_stokesLL_abs - data_stokesLL_abs_mean)
                data_stokesRR_rms_all = np.std(data_stokesRR_abs - data_stokesRR_abs_mean)
                #print('data_stokesLL_rms_all = %s'%(data_stokesLL_rms_all) )
                #print('data_stokesRR_rms_all = %s'%(data_stokesRR_rms_all) )
                # 
                # store into info_dict
                info_dict[fieldKey]['SPW']['RMS'].append( (data_stokesLL_rms_all + data_stokesRR_rms_all) / 2.0 )
                info_dict[fieldKey]['SPW']['RMS_STOKES_LL'].append( data_stokesLL_rms_all )
                info_dict[fieldKey]['SPW']['RMS_STOKES_RR'].append( data_stokesRR_rms_all )
                info_dict[fieldKey]['SPW']['CHAN_RMS'].append( (data_stokesRR_rms_per_chan + data_stokesLL_rms_per_chan) / 2.0 )
                info_dict[fieldKey]['SPW']['CHAN_RMS_STOKES_LL'].append( data_stokesLL_rms_per_chan )
                info_dict[fieldKey]['SPW']['CHAN_RMS_STOKES_RR'].append( data_stokesRR_rms_per_chan )
                # 
                # also sum up EXPOSURE, EXPOSURE * BASELINE, and EXPOSURE * ALL
                exposure = tb4.getcol('EXPOSURE')
                info_dict[fieldKey]['SPW']['EXPOSURE_X_BASELINE'].append( np.sum( exposure ) / 2.0 ) # single stokes
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_BASELINE'].append( len( exposure ) / 2.0 ) # single stokes
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'].append( len( exposure ) )
                info_dict[fieldKey]['SPW']['NUM_STOKES'].append( number_of_stokes )
            else:
                if number_of_stokes == 1:
                    data = tb4.getcol(data_column)[:,:,0] # DATA shape (nrow, nchan, nstokes) and nstokes==1
                else:
                    data = tb4.getcol(data_column)[:,:] # DATA shape (nrow, nchan), no stokes dimension
                print('data_array.shape', data_array.shape)
                data_abs = np.absolute(data)
                data_abs_mean = np.mean(data_abs, axis=0)
                data_rms_per_chan = np.std(data_abs - data_abs_mean, axis=0)
                data_rms_all = np.std(data_abs - data_abs_mean)
                # 
                # store into info_dict
                info_dict[fieldKey]['SPW']['RMS'].append( data_rms_all )
                info_dict[fieldKey]['SPW']['CHAN_RMS'].append( data_rms_per_chan )
                # 
                # also sum up EXPOSURE, EXPOSURE * BASELINE, and EXPOSURE * ALL
                # -- in average we have (N_ant * (N_ant - 1)) baselines
                exposure = tb4.getcol('EXPOSURE')
                info_dict[fieldKey]['SPW']['EXPOSURE_X_BASELINE'].append( np.sum( exposure ) ) # / np.sqrt( len(info_dict['ANTENNA']['ID']) * (len(info_dict['ANTENNA']['ID'])-1) )
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_BASELINE'].append( len( exposure ) )
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'].append( len( exposure ) )
                info_dict[fieldKey]['SPW']['NUM_STOKES'].append( number_of_stokes )
            # 
            # calc BMAJ BMIN for each CHAN of each SPW of each field (array operation)
            # interferometry: Fourier Transform is exp( 2 * pi * 1j * (u_m * x_rad + v_m * y_rad) / lambda_m )
            # "2.0*np.sqrt(2.0*np.log(2.0))" converts Gaussian sigma to FWHM
            info_dict[fieldKey]['SPW']['CHAN_BMAJ'].append( 2.99792458e8 / np.array(info_dict['SPW']['CHAN_FREQ'][ispw]) / info_dict[fieldKey]['UVW']['U_MAX'] / np.pi * 180.0) # in units of degrees
            info_dict[fieldKey]['SPW']['CHAN_BMIN'].append( 2.99792458e8 / np.array(info_dict['SPW']['CHAN_FREQ'][ispw]) / info_dict[fieldKey]['UVW']['V_MAX'] / np.pi * 180.0) # in units of degrees
            # 
            # calc BMAJ BMIN for each SPW of each field, taking the min of CHAN_FREQ
            info_dict[fieldKey]['SPW']['BMAJ'].append( np.min(info_dict[fieldKey]['SPW']['CHAN_BMAJ'][ispw]) )
            info_dict[fieldKey]['SPW']['BMIN'].append( np.min(info_dict[fieldKey]['SPW']['CHAN_BMIN'][ispw]) )
            # 
            # close table
            tb4.close()
            # 
            #if ispw >= 2:
            #    break
        # 
        # close table
        tb3.close() # close table tb3
    # 
    # close table
    tb.close() # # close table tb1
    # 
    # store into info_dict_file
    with open(info_dict_file, 'w') as fp:
        json.dump(info_dict, fp, indent=4, cls=json_interferometry_info_dict_encoder)
        print('Stored info_dict into "%s"!'%(info_dict_file))
    # 
    # print
    print_interferometry_info_dict(info_dict)
    # 
    # return
    return info_dict




# 
# def print_interferometry_info_dict()
# 
def print_interferometry_info_dict(info_dict, only_return_strings = False, current_dict_level = 1):
    printed_strings = []
    # 
    # determine dict key column width
    print_fmt_col_width = 0
    for k in info_dict.keys():
        if print_fmt_col_width < len(k):
            print_fmt_col_width = len(k)
    print_fmt_col_width += 1
    # 
    # loop dict keys
    for k in info_dict:
        # if value is dict, iterate this function
        if type(info_dict[k]) is dict:
            printed_strings2 = print_interferometry_info_dict(info_dict[k], only_return_strings = True, current_dict_level = current_dict_level + 1)
            for k2 in printed_strings2:
                print_fmt = '%%-%ds: %%s' % (print_fmt_col_width)
                print_str = print_fmt % (k, k2)
                printed_strings.append(print_str)
                if not only_return_strings:
                    print(print_str)
        # 
        else:
            # get item
            info_item = info_dict[k]
            if type(info_item) is list:
                # if list has at least two dimensions, i.e., is a nested list or array
                # we print something like: "[ [...], ..., [...] ]"
                item_shape = np.asarray(info_item).shape
                if len(item_shape) > 1:
                    if item_shape[0] > 1:
                        if len(info_item[0]) > 3:
                            print_fmt = '%%-%ds = [ [%%s, ...] to [%%s, ...] ] (shape=%%s)' % (print_fmt_col_width)
                            print_str = print_fmt % (k, ', '.join(map(str, info_item[0][0:3])), ', '.join(map(str, info_item[-1][0:3])), np.asarray(info_item).shape )
                        else:
                            print_fmt = '%%-%ds = [ [%%s] to [%%s] ] (shape=%%s)' % (print_fmt_col_width)
                            print_str = print_fmt % (k, ', '.join(map(str, info_item[0])), ', '.join(map(str, info_item[-1])), np.asarray(info_item).shape )
                    else:
                        if len(info_item[0]) > 3:
                            print_fmt = '%%-%ds = [ [%%s, ...] ] (shape=%%s)' % (print_fmt_col_width)
                            print_str = print_fmt % (k, ', '.join(map(str, info_item[0][0:3])), np.asarray(info_item).shape )
                        else:
                            print_fmt = '%%-%ds = [ [%%s] ] (shape=%%s)' % (print_fmt_col_width)
                            print_str = print_fmt % (k, ', '.join(map(str, info_item[0])), np.asarray(info_item).shape )
                # else if the list has only one dimension
                # we print like "[ ..., ..., ... ]"
                else:
                    print_fmt = '%%-%ds = [ %%s ] (len=1)' % (print_fmt_col_width)
                    print_str = print_fmt % (k, str(info_item[0] ) ) # ', '.join(map(str, info_item)
            else:
                print_fmt = '%%-%ds = [ %%s ] (scalar)' % (print_fmt_col_width)
                print_str = print_fmt % (k, info_item )
            # 
            printed_strings.append(print_str)
            if not only_return_strings:
                print(print_str)
    # 
    if only_return_strings:
       return printed_strings 




# 
# def parseIntSet()
# 
#   based on https://stackoverflow.com/questions/712460/interpreting-number-ranges-in-python
#   returns a set of selected values when a string in the form:
#   '1~4,6,8,10~12'
#   would return:
#   [1,2,3,4,6,7,10,11,12]
# 
def parseIntSet(nputstr=""):
    selection = set()
    invalid = set()
    # tokens are comma seperated values
    tokens = [x.strip() for x in nputstr.split(',')]
    for i in tokens:
        if len(i) > 0:
            if i[:1] == "<":
                i = "1~%s"%(i[1:])
        try:
            # typically tokens are plain old integers
            selection.add(int(i))
        except:
            # if not, then it might be a range
            try:
                token = [int(k.strip()) for k in i.split('~')]
                if len(token) > 1:
                    token.sort()
                    # we have items seperated by a dash
                    # try to build a valid range
                    first = token[0]
                    last = token[len(token)-1]
                    for x in range(first, last+1):
                        selection.add(x)
            except:
                # not an int and not a range...
                invalid.add(i)
    # Report invalid tokens before returning valid selection
    if len(invalid) > 0:
        print("Error! Invalid set: " + str(invalid))
        sys.exit()
    # 
    return selection




# 
# get_tclean_parameter_list
# 
def get_tclean_parameter_list():
    return ['vis', 'imagename', 'field', 'selectdata', 'spw', 'width', 'reffreq', 'restfreq', 'veltype', 
            'cell', 'imsize', 'gridder', 'specmode', 'outframe', 'deconvolver', 'nterms', 'niter', 'calcres', 'calcpsf', 
            'usemask', 'pbmask', 'mask', 'pblimit', 'pbcor', 
            'threshold', 'weighting', 'robust', 'uvtaper', 
            'restoringbeam', 'savemodel', 'chanchunks', 'interactive', 'parallel']




# 
# def get_optimized_imsize
# 
def get_optimized_imsize(imsize, return_decomposed_factors = False):
    # try to make imsize be even and only factorizable by 2,3,5,7
    imsize = int(imsize)
    decomposed_factors = []
    # 
    # if imsize is 1, then return it
    if imsize == 1:
        if return_decomposed_factors == True:
            return 1, [1]
        else:
            return 1
    # 
    # make it even
    if imsize % 2 != 0:
        imsize += 1
    # 
    # factorize by 2,3,5,7
    for k in [2, 3, 5, 7]:
        while imsize % k == 0:
            imsize = int(imsize / k)
            decomposed_factors.append(k)
    # 
    # make the non-factorizable number factorizable by 2, 3, 5, or 7
    while imsize != 1 and int( np.prod( [ (imsize % k) for k in [2, 3, 5, 7] ] ) ) != 0:
        # as long as it is factorizable by any of the [2, 3, 5, 7], the mod ("%") will be zero, so the product will also be zero
        #print('imsize', imsize, '(imsize % k)', [ (imsize % k) for k in [2, 3, 5, 7] ], 
        #                               np.prod( [ (imsize % k) for k in [2, 3, 5, 7] ] ) )
        imsize += 1
        #print('imsize', imsize, '(imsize % k)', [ (imsize % k) for k in [2, 3, 5, 7] ], 
        #                               np.prod( [ (imsize % k) for k in [2, 3, 5, 7] ] ) )
        
    # 
    imsize2, decomposed_factors2 = get_optimized_imsize(imsize, return_decomposed_factors = True)
    # 
    imsize = imsize2
    # 
    decomposed_factors.extend(decomposed_factors2)
    # 
    if return_decomposed_factors == True:
        return np.prod(decomposed_factors), decomposed_factors
    else:
        return np.prod(decomposed_factors)





# 
# clean_highz_gal
# 
def clean_highz_gal(my_clean_mode = 'cube', 
                    vis = '', 
                    field = '', 
                    imagename = '', 
                    phasecenter = '', 
                    stokes = '', 
                    spw = '', 
                    reffreq = '', 
                    restfreq = '', 
                    veltype = 'radio', 
                    width = '', 
                    start = '', 
                    nchan = '', 
                    threshold = '', 
                    weighting = 'briggs', 
                    robust = 2.0, 
                    uvtaper = [], 
                    clean_to_nsigma = 3.0, 
                    info_dict_file = '',
                   ):
    # 
    # check_ok
    check_ok = True
    # 
    # check my_clean_mode
    if my_clean_mode == '':
        print('Error! The input my_clean_mode is empty!')
        check_ok = False
    elif not my_clean_mode.startswith('cube') and not my_clean_mode.startswith('cont'):
        print('Error! The input my_clean_mode is "%s", but it should be either "cube" or "continuum"!'%(my_clean_mode))
        check_ok = False
    # 
    # check vis
    if vis == '':
        print('Error! The input vis is empty!')
        check_ok = False
    elif not os.path.isdir(vis):
        if os.path.isdir(vis+'.ms'):
            vis = vis+'.ms'
        else:
            print('Error! The input vis "%s" does not exist!'%(vis))
            check_ok = False
    # 
    # check vis
    if field == '':
        print('Error! The input field is empty!')
        check_ok = False
    # 
    # if not check_ok, print usage and exit
    if not check_ok:
        print("Please call this function like:")
        print("    clean_highz_gal('cube', 'example_vis_name.ms', 'example_field_name', 'example_output_image_name')")
        sys.exit()
    # 
    # grab_interferometry_info
    info_dict = grab_interferometry_info(vis)
    # 
    # check field 
    if not ('FIELD_'+field in info_dict):
        print('Error! The input field is not in the info_dict of the data "%s"!'%(vis))
        print('       Available fields are: %s'%(', '.join(['"'+t+'"' for t in info_dict['FIELD']['NAME']])))
        sys.exit()
    # 
    # set spw selection according to the input
    if spw == '':
        selectdata = False
        spw_list = []
        for ispw in range(len(info_dict['FIELD_'+field]['SPW']['ID'])):
            if (not info_dict['FIELD_'+field]['SPW']['NAME'].startswith('WVR')) \
               and info_dict['FIELD_'+field]['SPW']['NAME'].find('ALMA') > 0 \
               and info_dict['FIELD_'+field]['SPW']['NAME'].find('FULL_RES') > 0:
                spw_list.append(ispw) # ispw is the index for info_dict['FIELD_'+field]['SPW']['ID'] array
    else:
        selectdata = True
        spw_list = parseIntSet(spw)
    # 
    # set reffreq and restfreq if no input. 
    # -- reffreq is the Reference frequency for MFS (relevant only if nterms > 1)
    # -- restfreq is for translation of velocities. When no input, CASA tclean() will set it to the center of spw automatically.
    if my_clean_mode == 'continuum':
        if reffreq == '':
            if spw == '':
                sys.stdout.write('Computing reffreq as the centroid frequency of all spws:')
                sys.stdout.flush()
            else:
                sys.stdout.write('Computing reffreq as the centroid frequency of the input spws:')
                sys.stdout.flush()
            # loop spw_list and print frequency info
            for ispw in spw_list:
                sys.stdout.write(' %d (ID %d, freq %.6f-%.6f GHz)'%(ispw, info_dict['FIELD_'+field]['SPW']['ID'][ispw], info_dict['SPW']['CHAN_FREQ'][ispw][0] / 1e9, info_dict['SPW']['CHAN_FREQ'][ispw][-1] / 1e9))
                sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()
            # 
            reffreq = '%0.9f GHz'%(np.mean(np.array(info_dict['SPW']['CHAN_FREQ'])[np.array(spw_list)][0]) / 1e9)
        
    # 
    # set channel width if no input
    if width == '':
        if my_clean_mode.startswith('cube'):
            width = '2' # channel width
    # 
    # set imagename if no input
    if imagename == '':
        imagename = '%s_%s'%(re.sub(r'\.ms$', r'', vis, re.IGNORECASE), re.sub(r'[^a-zA-Z0-9_+-]', r'_', field))
    # 
    # set clean threshold
    if threshold == '':
        if spw == '':
            sys.stdout.write('Computing restfreq as the average of all spws:')
            sys.stdout.flush()
        else:
            sys.stdout.write('Computing restfreq as the average of the input spws:')
            sys.stdout.flush()
        # loop spw_list and print rms info
        for ispw in spw_list:
            sys.stdout.write(' %d (ID %d, RMS %.6f mJy/beam)'%(ispw, info_dict['FIELD_'+field]['SPW']['ID'][ispw], info_dict['FIELD_'+field]['SPW']['RMS'][ispw] * 1e3))
            sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()
        # 
        # image plane rms = visibility rms / sqrt( N_ant * (N_ant-1) * (t_source / t_interval) * n_polar ) -- see https://casaguides.nrao.edu/index.php/DataWeightsAndCombination
        #image_plane_rms_mJy_per_beam = np.mean(np.array(info_dict['SPW']['RMS'])[spw_list]) / np.sqrt( len(info_dict['ANTENNA']['ID']) * (len(info_dict['ANTENNA']['ID'])-1) ) * 1e3 # in units of mJy/beam
        # now we use NUM_SCAN_X_BASELINE == N_ant * (N_ant-1) * (t_source / t_interval), so image plane rms is as below
        # now we use NUM_SCAN_X_ALL == N_ant * (N_ant-1) * (t_source / t_interval) * n_polar, so image plane rms is as below
        image_plane_rms_mJy_per_beam = np.mean(np.array(info_dict['FIELD_'+field]['SPW']['RMS'])[spw_list]) \
                                       / np.sqrt( np.array(info_dict['FIELD_'+field]['SPW']['NUM_SCAN_X_ALL'])[spw_list] ) \
                                       * 1e3 # in units of mJy/beam
        if np.isnan(clean_to_nsigma):
            clean_to_nsigma = 3.0 #<TODO># clean to how many sigma
        threshold = '%0.6f mJy'%(image_plane_rms_mJy_per_beam * clean_to_nsigma) # in units of mJy/beam
    # 
    # set stokes
    if stokes == '':
        stokes = 'I' # merge polarizations, Stokes I = (LL + RR)/2 = (XX + YY)/2
    # 
    # print message
    print('spw_list = %s'%(spw_list))
    print('restfreq = %s'%(restfreq))
    print('threshold = %s'%(threshold))
    # 
    # set other parameters
    #start = ''
    #nchan = ''
    synthesized_beam_sampling_factor = 5.0
    cell_arcsec = np.min([info_dict['FIELD_'+field]['SPW']['BMAJ']*3600.0, \
                          info_dict['FIELD_'+field]['SPW']['BMIN']*3600.0]) \
                  / synthesized_beam_sampling_factor # in units of arcsec
    cell = '%0.6f arcsec'%(cell_arcsec) # in units of arcsec
    imsize = np.max(info_dict['FIELD_'+field]['SPW']['PRIMARY_BEAM'])*3600.0 * 2.0 / cell_arcsec # 2.0 * PB, in units of pixel
    imsize = get_optimized_imsize(imsize)
    # 
    if my_clean_mode.startswith('cube'):
        gridder = 'mosaic' # 'standard'
        specmode = 'cube' # for spectral line cube
    elif my_clean_mode.startswith('cont'):
        gridder='standard'
        specmode = 'mfs'
    outframe = 'LSRK'
    deconvolver = 'hogbom'
    usemask = 'pb' # construct a 1/0 mask at the 0.2 level
    pbmask = 0.2 # data outside this pbmask will not be fitted
    mask = '' #<TODO># 
    pblimit = 0.1 # data outside this pblimit will be output as NaN
    pbcor = True # create both pbcorrected and uncorrected images
    restoringbeam = 'common' # Automatically estimate a common beam shape/size appropriate for all planes.
    nterms = 1 # nterms must be ==1 when deconvolver='hogbom' is chosen
    chanchunks = -1 # This feature is experimental and may have restrictions on how chanchunks is to be chosen. For now, please pick chanchunks so that nchan/chanchunks is an integer. 
    interactive = False
    savemodel = 'virtual' # 'none', 'virtual', 'modelcolumn'. 'virtual' for simple gridding, 'modelcolumn' for gridder='awproject'.
    niter = 30000
    calcres = True # calculate initial residual image at the beginning of the first major cycle
    calcpsf = True
    if calcres==False and niter==0:
        print('Note: Only the PSF will be made and no data will be gridded in the first major cycle of cleaning.')
    elif calcres==False and niter>0:
        print('Note: We will assume that a "*.residual" image already exists and that the minor cycle can begin without recomputing it.')
    elif calcres==True:
        if calcpsf==False and not (os.path.isfile(imagename+'.psf') and os.path.isfile(imagename+'.sumwt')):
            calcpsf = True # calcres=True requires that calcpsf=True or that the .psf and .sumwt images already exist on disk (for normalization purposes)
    # 
    # set parallel (TODO: should be set inside real running environment)
    #parallel = False # Run major cycles in parallel (this feature is experimental)
    #if (os.popen("ps -p %d -oargs=" % os.getpid()).read().strip().find('mpirun') >= 0):
    #    parallel = True # Parallel tclean will run only if casapy has already been started using mpirun. 

    # 
    # write script
    if os.path.isfile('run_casa_ms_clean_highz_cal_cube.py'):
        print('Found existing "%s"! Backing it up as "%s"'%('run_casa_ms_clean_highz_cal_cube.py', 'run_casa_ms_clean_highz_cal_cube.py.backup'))
        shutil.move('run_casa_ms_clean_highz_cal_cube.py', 'run_casa_ms_clean_highz_cal_cube.py.backup')
    with open('run_casa_ms_clean_highz_cal_cube.py', 'w') as fp:
        t_local_vals = locals()
        for t in get_tclean_parameter_list():
            if t in t_local_vals:
                if type(t_local_vals[t]) is str:
                    if t_local_vals[t] == '':
                        continue
                    else:
                        fp.write('%-15s = \'%s\'\n'%(t, t_local_vals[t] ) )
                else:
                    fp.write('%-15s = %s\n'%(t, t_local_vals[t] ) )
        fp.write('\n')
        fp.write('inp(tclean)\n')
        fp.write('\n')
        fp.write('tclean()\n')
        fp.write('\n')
        print('Output to "%s"!'%('run_casa_ms_clean_highz_cal_cube.py'))
    # 
    # then run casa
    try: 
        __IPYTHON__
        type(tclean)
        print('Currently we are in CASA IPython! Running CASA `clean`!')
        saveinputs(tclean, 'run_casa_ms_clean_highz_cal_cube.tclean.saveinputs.txt') # store parameters in file
        print('Saved tclean parameters to "%s"!'%('run_casa_ms_clean_highz_cal_cube.tclean.saveinputs.txt'))
        #tget(clean, parfile) # restore parameters from file
        inp(tclean)
        tclean()
    except:
        print('Currently we are not in CASA IPython! Please run the output script within CASA by yourself!')
        print('e.g., casa -c "execfile(\'run_casa_ms_clean_highz_cal_cube.py\')"')


    





# 
# def usage()
# 
def usage():
    print('Usage:')
    print('    %s "Your_input_vis.ms" "Your_galaxy_name"'%(os.path.dirname(__file__) ) )






# 
# main
# 
if __name__ == '__main__':
    
    # 
    # read user input
    vis = ''
    gal = ''
    i = 1
    while i < len(sys.argv):
        if vis == '':
            vis = sys.argv[i]
        elif gal == '':
            gal = sys.argv[i]
        i += 1
    
    # 
    # check user input
    if vis == '' or \
       gal == '':
        usage()
        sys.exit()
    
    # 
    # print message
    print('vis = %s'%(vis))
    print('gal = %s'%(gal))
    
    # 
    # test subroutine
    #print('parseIntSet(\'1~4,6,8,10~12\')', parseIntSet('1~4,6,8,10~12'))
    
    # 
    # test subroutine
    #imsize = 101
    #print('get_optimized_imsize(%d)'%(imsize), get_optimized_imsize(imsize))
    #imsize = 381
    #print('get_optimized_imsize(%d)'%(imsize), get_optimized_imsize(imsize))
    #imsize = 271
    #print('get_optimized_imsize(%d)'%(imsize), get_optimized_imsize(imsize))
    #imsize = 3271
    #print('get_optimized_imsize(%d)'%(imsize), get_optimized_imsize(imsize))
    #imsize = 7*19
    #print('get_optimized_imsize(%d)'%(imsize), get_optimized_imsize(imsize))
    #imsize = 7*17
    #print('get_optimized_imsize(%d)'%(imsize), get_optimized_imsize(imsize))
    
    # 
    # run test 
    #grab_interferometry_info(vis)
    clean_highz_gal('cube', vis, gal)




















