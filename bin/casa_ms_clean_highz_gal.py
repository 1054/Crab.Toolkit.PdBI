#!/usr/bin/env python
# 
# This code NOT REALLY must be run in CASA
# 
# to run this code in CASA, use 
#   execfile(__file__, {}, locals()) 
# but we must set vis and field in advance
# 
# 20190718: Could not run this in CASA with __casac__. Still must need casacore. 
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil
import numpy as np
import inspect


# 
# def usage()
# 
def usage():
    print('Usage:')
    print('    casa_ms_clean_highz_gal.py \\')
    print('        -vis "input_vis.ms" \\')
    print('        -field "galaxy_name" \\')
    print('        [-out "output_name"] \\')
    print('        [-script "output_script_file"] \\')
    print('        [-dry-run] \\')
    print('        [-spw "0,1,2,3"] \\')
    print('        [-width "30km/s"] \\')
    print('        [-phasecenter ""] \\')
    print('        [-threshold ""] \\')
    print('    ')
    print('Output:')
    print('    The output will be a script to be ran in CASA. The default script name is "run_casa_ms_clean_highz_gal_cube.py" or "run_casa_ms_clean_highz_gal_continuum.py"')
    print('    ')
    print('Note:')
    print('    Arguments with [] means they are optional. Do not type the [] when use the argument.')
    print('    To run the output script in CASA, for now CASA uses Python 2, so just use execfile("run_casa_ms_clean_highz_gal.py")')
    print('    Todo: for future Python 3, we can from . import casa_ms_clean_highz_gal; casa_ms_clean_highz_gal.main()')
    print('')



# 
# set debug level
# 
global SET_DEBUG_LEVEL
SET_DEBUG_LEVEL = 0



# 
# import casacore table
# 
global USE_CASACORE
#try:
#    #from __casac__ import *
#    from __casac__.table import table
#    USE_CASACORE = False
#except:
#    try:
#        import casacore # pip install python-casacore # documentation: http://casacore.github.io/python-casacore/
#        from casacore.tables import table, taql
#        USE_CASACORE = True
#    except:
#        raise ImportError('Could not import casacore or __casac__! Please install casacore via \'pip install python-casacore!\'')
try:
    import casacore # PYTHONPATH= pip install --user python-casacore # documentation: http://casacore.github.io/python-casacore/
    from casacore.tables import table as casacore_table
    from casacore.tables import taql as casacore_taql
    USE_CASACORE = True
except:
    #print('Error! Python package casacore not found! Should we install it?')
    #print('We can run pip now to install python-casacore into user directory, if you argee by typing "y":')
    #if sys.version_info.major >= 3:
    #    check_yes = input("[y/n]: ")
    #else:
    #    check_yes = raw_input("[y/n]: ")
    #if check_yes.lower().startswith('y'):
    #    #os.system('PYTHONPATH= pip install --user python-casacore')
    #    print('Trying to import pip and install python-casacore')
    #    try:
    #        import pip
    #        #import sysconfig
    #        if hasattr(pip, 'main'):
    #            pip.main(['install', '--user', 'python-casacore'])
    #        else:
    #            pip._internal.main(['install', '--user', 'python-casacore'])
    #    except:
    #        try:
    #            import pip
    #            
    #        except:
    #            pass
    #    
    #    try:
    #        import casacore # PYTHONPATH= pip install --user python-casacore # documentation: http://casacore.github.io/python-casacore/
    #        from casacore.tables import table as casacore_table
    #        from casacore.tables import taql as casacore_taql
    #        USE_CASACORE = True
    #    except:
    #        print('Sorry, still could not import casacore!')
    #        raise ImportError('Could not import casacore or __casac__! Please install casacore via \'PYTHONPATH= pip install python-casacore!\'')
    #else:
    #    print('Abort!')
    #    raise ImportError('Could not import casacore or __casac__! Please install casacore via \'PYTHONPATH= pip install python-casacore!\'')
    raise ImportError('Could not import casacore! Please install casacore outside CASA via \'PYTHONPATH= pip install --user python-casacore!\'')

print('USE_CASACORE = %s'%(USE_CASACORE))




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
# open_casa_table
# 
def open_casa_table(table_file_path):
    global USE_CASACORE
    if USE_CASACORE == True:
        tb0 = casacore_table(table_file_path)
    else:
        tb0 = table()
        tb0.open(table_file_path)
    return tb0




# 
# query_casa_table
# 
def query_casa_table(tb0, query_where_str, columns = None, max_nrows = None, verbose = False):
    global USE_CASACORE
    global SET_DEBUG_LEVEL
    # 
    # query_columns_str must be a single string with comma separated.
    if columns is None:
        columns = []
    if type(columns) is str:
        query_columns_str = columns
    else:
        query_columns_str = ', '.join(map(str, columns))
    # 
    # query 
    if USE_CASACORE == True:
        if query_where_str != '' and query_where_str != '*':
            query_str = 'SELECT %s FROM $tb0 WHERE (%s)'%(query_columns_str, query_where_str)
        else:
            query_str = 'SELECT %s FROM $tb0'%(query_columns_str)
        if max_nrows is not None:
            query_str = query_str + ' LIMIT %d'%(max_nrows)
        if verbose == True or SET_DEBUG_LEVEL >=1 :
            print('casacore_taql: '+ query_str)
        tbout = casacore_taql(query_str)
    else:
        if query_where_str != '' and query_where_str != '*':
            tbout = tb0.query(query=query_where_str, columns=query_columns_str)
            #tbout = tb0.query(query=query_where_str, columns=query_columns_str, style='python') # https://casa.nrao.edu/docs/CasaRef/table.query.html -- 
            #style='python' not working?
        else:
            tbout = tb0.query(columns=query_columns_str)
    return tbout




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
    tb1 = open_casa_table(vis) # open table tb1
    # 
    # test
    #print(tb1.getkeywords())
    #print(tb1.colnames())
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
    if 'ANTENNA' in tb1.getkeywords():
        tb2 = open_casa_table(tb1.getkeyword('ANTENNA').replace('Table: ','')) # open table tb2
        #print(tb2.colnames()) # ['OFFSET', 'POSITION', 'TYPE', 'DISH_DIAMETER', 'FLAG_ROW', 'MOUNT', 'NAME', 'STATION']
        info_dict['ANTENNA']['ID'] = np.arange(0,tb2.nrows()).astype(int).tolist()
        info_dict['ANTENNA']['OFFSET'] = tb2.getcol('OFFSET').tolist()
        info_dict['ANTENNA']['POSITION'] = tb2.getcol('POSITION').tolist()
        info_dict['ANTENNA']['DISH_DIAMETER'] = tb2.getcol('DISH_DIAMETER').tolist()
        #print(type(info_dict['ANTENNA']['OFFSET']), np.array(info_dict['ANTENNA']['OFFSET']).shape)
        tb2.close() # close table tb2
    else:
        missing_keywords.append('ANTENNA')
    # 
    # get FIELD
    if 'FIELD' in tb1.getkeywords():
        tb2 = open_casa_table(tb1.getkeyword('FIELD').replace('Table: ','')) # open table tb2
        #print(tb2.colnames()) # ['DELAY_DIR', 'PHASE_DIR', 'REFERENCE_DIR', 'CODE', 'FLAG_ROW', 'NAME', 'NUM_POLY', 'SOURCE_ID', 'TIME']
        info_dict['FIELD']['ID'] = np.arange(0,tb2.nrows()) # .astype(int).tolist()
        info_dict['FIELD']['SOURCE_ID'] = tb2.getcol('SOURCE_ID') # .astype(int).tolist()
        info_dict['FIELD']['NAME'] = tb2.getcol('NAME') # .astype(str).tolist()
        for t in info_dict['FIELD'].keys(): 
            if type(info_dict['FIELD'][t]) is np.ndarray:
                info_dict['FIELD'][t] = info_dict['FIELD'][t].tolist()
        tb2.close() # close table tb2
    else:
        missing_keywords.append('FIELD')
    # 
    # get SOURCE
    if 'SOURCE' in tb1.getkeywords():
        tb2 = open_casa_table(tb1.getkeyword('SOURCE').replace('Table: ','')) # open table tb2
        #print(tb2.colnames()) # ['DIRECTION', 'PROPER_MOTION', 'CALIBRATION_GROUP', 'CODE', 'INTERVAL', 'NAME', 'NUM_LINES', 'SOURCE_ID', 'SPECTRAL_WINDOW_ID', 'TIME', 'POSITION', 'REST_FREQUENCY', 'SYSVEL', 'TRANSITION', 'SOURCE_MODEL']
        info_dict['SOURCE']['ID'] = np.arange(0,tb2.nrows()) # .astype(int).tolist()
        info_dict['SOURCE']['NAME'] = tb2.getcol('NAME') # .astype(str).tolist()
        info_dict['SOURCE']['SOURCE_ID'] = tb2.getcol('SOURCE_ID') # .astype(int).tolist()
        info_dict['SOURCE']['SPW_ID'] = tb2.getcol('SPECTRAL_WINDOW_ID') # .astype(int).tolist()
        for t in info_dict['SOURCE'].keys(): 
            if type(info_dict['SOURCE'][t]) is np.ndarray:
                info_dict['SOURCE'][t] = info_dict['SOURCE'][t].tolist()
        tb2.close() # close table tb2
    else:
        missing_keywords.append('SOURCE')
    # 
    # get DATA_DESCRIPTION
    if 'DATA_DESCRIPTION' in tb1.getkeywords():
        tb2 = open_casa_table(tb1.getkeyword('DATA_DESCRIPTION').replace('Table: ','')) # open table tb2
        #print(tb2.colnames()) # ['MEAS_FREQ_REF', 'CHAN_FREQ', 'REF_FREQUENCY', 'CHAN_WIDTH', 'EFFECTIVE_BW', 'RESOLUTION', 'FLAG_ROW', 'FREQ_GROUP', 'FREQ_GROUP_NAME', 'IF_CONV_CHAIN', 'NAME', 'NET_SIDEBAND', 'NUM_CHAN', 'TOTAL_BANDWIDTH']
        info_dict['DATA_DESC']['ID'] = np.arange(0,tb2.nrows()) # .astype(int).tolist()
        info_dict['DATA_DESC']['SPW_ID'] = tb2.getcol('SPECTRAL_WINDOW_ID') # .astype(int).tolist()
        info_dict['DATA_DESC']['STOKES_ID'] = tb2.getcol('POLARIZATION_ID') # .astype(int).tolist()
        for t in info_dict['DATA_DESC'].keys(): 
            if type(info_dict['DATA_DESC'][t]) is np.ndarray:
                info_dict['DATA_DESC'][t] = info_dict['DATA_DESC'][t].tolist()
        tb2.close() # close table tb2
    else:
        missing_keywords.append('DATA_DESCRIPTION')
    # 
    # get SPECTRAL_WINDOW
    if 'SPECTRAL_WINDOW' in tb1.getkeywords():
        tb2 = open_casa_table(tb1.getkeyword('SPECTRAL_WINDOW').replace('Table: ','')) # open table tb2
        #print(tb2.colnames()) # ['MEAS_FREQ_REF', 'CHAN_FREQ', 'REF_FREQUENCY', 'CHAN_WIDTH', 'EFFECTIVE_BW', 'RESOLUTION', 'FLAG_ROW', 'FREQ_GROUP', 'FREQ_GROUP_NAME', 'IF_CONV_CHAIN', 'NAME', 'NET_SIDEBAND', 'NUM_CHAN', 'TOTAL_BANDWIDTH']
        info_dict['SPW']['ID'] = np.arange(0,tb2.nrows()) # .astype(int).tolist()
        info_dict['SPW']['NAME'] = tb2.getcol('NAME') # .astype(str).tolist()
        info_dict['SPW']['NUM_CHAN'] = tb2.getcol('NUM_CHAN') # .astype(int).tolist()
        info_dict['SPW']['DATA_DESC_ID'] = []
        info_dict['SPW']['PRIMARY_BEAM'] = [] # in units of degrees
        info_dict['SPW']['CHAN_PRIMARY_BEAM'] = [] # in units of degrees, should be a 2D array
        info_dict['SPW']['CHAN_FREQ'] = [] # should be a 2D array. 
        for k2 in range(tb2.nrows()):
            info_dict['SPW']['DATA_DESC_ID'].append( np.argwhere( np.array(info_dict['DATA_DESC']['SPW_ID']) == k2 ).flatten() ) # indicates which DATA_DESC_ID(s) correspond to current SPW_ID # python2 has bug if np.argwhere( without np.array() inside )
            info_dict['SPW']['CHAN_FREQ'].append( tb2.getcell('CHAN_FREQ', k2) ) # in units of Hz
            info_dict['SPW']['CHAN_PRIMARY_BEAM'].append( 1.13  * (2.99792458e8/info_dict['SPW']['CHAN_FREQ'][k2]) / (np.min(info_dict['ANTENNA']['DISH_DIAMETER'])) / np.pi * 180.0 ) # in units of degrees
            info_dict['SPW']['PRIMARY_BEAM'].append( np.mean( info_dict['SPW']['CHAN_PRIMARY_BEAM'][-1] ) )
        for t in info_dict['SPW'].keys(): 
            if type(info_dict['SPW'][t]) is np.ndarray:
                info_dict['SPW'][t] = info_dict['SPW'][t].tolist()
        tb2.close() # close table tb2
    else:
        missing_keywords.append('SPECTRAL_WINDOW')
    # 
    # check missing_keywords and exit on error
    if len(missing_keywords) > 0:
        print('Error! Could not find following keywords in the input vis "%s":'%(vis))
        print('    ' + ', '.join(missing_keywords))
        tb1.close() # close table on error
        sys.exit() # exit on error
    # 
    # 
    # 
    # determine data column
    #print(tb1.colnames())
    if 'CORRECTED_DATA' in tb1.colnames():
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
            query_where_field_str = query_where_str + ' AND (FIELD_ID==%d)'%(query_field_id)
        else:
            print('Error! The input field "%s" is not in the FIELD table of the input data "%s"!'%(field, vis))
            tb1.close() # close table on error
            sys.exit()
        # 
        # select first row and check stokes
        tb3 = query_casa_table(tb1, query_where_field_str, 'GCOUNT()') # open table tb3, TAQL GCOUNT() counts global row number when no GROUPBY 
        number_of_data_rows_per_field = tb3.getcell(tb3.colnames()[0], 0)
        tb3.close()
        print('Selected %d rows with "%s" (field="%s")'%(number_of_data_rows_per_field, query_where_field_str, field ) )
        if number_of_data_rows_per_field <= 0:
            print('Error! No data found with "%s"!'%(query_where_field_str))
            tb1.close() # close table on error
            sys.exit()
        # 
        # check stokes
        number_of_stokes = -1
        tb3 = query_casa_table(tb1, query_where_field_str, 'SHAPE('+data_column+')', max_nrows = 1) # open table tb3, TAQL SHAPE() counts global row number
        data_cell_shape = tb3.getcell(tb3.colnames()[0], 0)
        tb3.close()
        if len(data_cell_shape) == 1:
            print('Warning! Data cell has a dimension of %s and no polarization dimension!'%(str(data_shape)))
            number_of_stokes = 0
        elif len(data_cell_shape) == 2:
            if USE_CASACORE == False:
                data_cell_shape = data_cell_shape[::-1] #<TODO><20190716># __casac__.table.table has a different dimension order than casacore.tables.table ???
                print('data_cell_shape', data_cell_shape, '(nrow, nstokes)')
            #--> now no need, we use style='python'
            if data_cell_shape[-1] == 1:
                number_of_stokes = 1
            elif data_cell_shape[-1] == 2:
                number_of_stokes = 2
            else:
                print('Error! Data cell has a wrong polarization dimension of %s which should be 1 or 2!'%(data_cell_shape[-1])) # [-1]
                tb1.close() # close table on error
                sys.exit()
        else:
            print('Error! Data cell has a wrong dimension of %s which should be (Nchan, Nstokes)!'%(str(data_cell_shape)))
            tb1.close() # close table on error
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
        #tb4 = query_casa_table(tb1, query_where_field_str, 'GMAXS(UVW)')
        #data_UVW_GMAXS = tb4.getcol(tb4.colnames()[0]) # output shape is (1, 3)
        #tb4.close()
        #tb4 = query_casa_table(tb1, query_where_field_str, 'GMINS(UVW)')
        #data_UVW_GMINS = tb4.getcol(tb4.colnames()[0]) # output shape is (1, 3)
        #tb4.close()
        #tb4 = query_casa_table(tb1, query_where_field_str, 'GMAXS(ABS(UVW))')
        #data_UVW_GMAXS_ABS = tb4.getcol(tb4.colnames()[0]) # output shape is (1, 3)
        #tb4.close()
        #tb4 = query_casa_table(tb1, query_where_field_str, 'GMINS(ABS(UVW))')
        #data_UVW_GMINS_ABS = tb4.getcol(tb4.colnames()[0]) # output shape is (1, 3)
        #tb4.close()
        #print(data_UVW_GMAXS, data_UVW_GMINS)
        #print(data_UVW_GMAXS_ABS, data_UVW_GMINS_ABS)
        tb4 = query_casa_table(tb1, query_where_field_str, 'GMAX(sqrt(sumsqr(UVW[1:2])))')
        data_UVW_GMAX = tb4.getcell(tb4.colnames()[0], 0) # output cell is a scalar
        tb4.close()
        tb4 = query_casa_table(tb1, query_where_field_str, 'GMIN(sqrt(sumsqr(UVW[1:2])))')
        data_UVW_GMIN = tb4.getcell(tb4.colnames()[0], 0) # output cell is a scalar
        tb4.close()
        info_dict[fieldKey]['UVW']['MAX'] = data_UVW_GMAX
        info_dict[fieldKey]['UVW']['MIN'] = data_UVW_GMIN
        if SET_DEBUG_LEVEL >= 1:
            print('info_dict[fieldKey][\'UVW\']', info_dict[fieldKey]['UVW'])
        #sys.exit()
        # 
        # prepare spw dict for each field
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
        # prepare more per-spw meta data
        info_dict[fieldKey]['SPW']['EXPOSURE_X_BASELINE'] = []
        info_dict[fieldKey]['SPW']['EXPOSURE_X_ALL'] = []
        info_dict[fieldKey]['SPW']['NUM_SCAN_X_BASELINE'] = []
        info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'] = []
        info_dict[fieldKey]['SPW']['NUM_STOKES'] = []
        info_dict[fieldKey]['SPW']['BMAJ'] = [] # in units of degrees
        info_dict[fieldKey]['SPW']['BMIN'] = [] # in units of degrees
        info_dict[fieldKey]['SPW']['CHAN_BMAJ'] = [] # in units of degrees, should be a 2D array
        info_dict[fieldKey]['SPW']['CHAN_BMIN'] = [] # in units of degrees, should be a 2D array
        # 
        # loop spw and calc rms per channel
        for ispw in range(len(info_dict['SPW']['ID'])):
            print('Looping ispw %d spw %d spw name %s'%(ispw, info_dict['SPW']['ID'][ispw], info_dict['SPW']['NAME'][ispw]))
            # 
            # check field has this spw
            if len(info_dict['SPW']['DATA_DESC_ID'][ispw]) <= 0:
                print('Skipped ispw %d spw %d for the field %s because it has no DATA_DESC_ID'%(ispw, info_dict['SPW']['ID'][ispw], field))
                continue
            # 
            # check spw is not WVR
            if info_dict['SPW']['NAME'][ispw].startswith('WVR'):
                print('Skipped ispw %d spw %d for the field %s because it is Water Vapour frequency'%(ispw, info_dict['SPW']['ID'][ispw], field))
                continue
            # 
            # set spw data
            query_where_spw_str = '(DATA_DESC_ID in [%s])'%( ','.join( map( str, info_dict['SPW']['DATA_DESC_ID'][ispw] ) ) )
            # 
            # query this spw for this field
            tb4 = query_casa_table(tb1, query_where_field_str + ' AND ' + query_where_spw_str, 'GCOUNT()')
            if SET_DEBUG_LEVEL >= 1:
                print('tb4.nrows()', tb4.nrows())
                print('tb4.colnames()', tb4.colnames())
                print('tb4.getcol(tb4.colnames()[0]).shape', tb4.getcol(tb4.colnames()[0]).shape)
            if tb4.nrows() <= 0:
                number_of_data_rows_per_field_per_spw = 0
            else:
                number_of_data_rows_per_field_per_spw = tb4.getcell(tb4.colnames()[0], 0)
            tb4.close()
            # 
            # check nrows
            if number_of_data_rows_per_field_per_spw <= 0:
                print('Skipped ispw %d spw %d for the field %s due to no data selected'%(ispw, info_dict['SPW']['ID'][ispw], field))
                continue
            # 
            # print 
            print('Selected %d rows with "%s" (ispw==%d, spw=%d, field="%s")'%(number_of_data_rows_per_field_per_spw, query_where_spw_str, ispw, info_dict['SPW']['ID'][ispw], field ) )
            
            # 
            # prepare SPW dict for each fieldKey in info_dict
            # copy SPW ID NAME CHAN_FREQ PRIMARY_BEAM CHAN_PRIMARY_BEAM
            info_dict[fieldKey]['SPW']['ID'].append( info_dict['SPW']['ID'][ispw] )
            info_dict[fieldKey]['SPW']['NAME'].append( info_dict['SPW']['NAME'][ispw] )
            info_dict[fieldKey]['SPW']['CHAN_FREQ'].append( info_dict['SPW']['CHAN_FREQ'][ispw] )
            info_dict[fieldKey]['SPW']['PRIMARY_BEAM'].append( info_dict['SPW']['PRIMARY_BEAM'][ispw] )
            info_dict[fieldKey]['SPW']['CHAN_PRIMARY_BEAM'].append( info_dict['SPW']['CHAN_PRIMARY_BEAM'][ispw] )
            # 
            # calc rms per channel per stokes for each spw
            tb4 = query_casa_table(tb1, query_where_field_str + ' AND ' + query_where_spw_str, 
                                        columns = 'RMSS(GAGGR(amplitude('+data_column+')),0)') 
                                        # open table tb4, data array has a shape of (nchan, nstokes)
                                        # casacore GAGGR() stacks DATA, so the shape becomes (nrows, nchan, nstokes)
                                        # casacore RMSS() computes along axis 0, so the shape becomes (1, nchan, nstokes)
                                        # columns = 'GRMS(ABS(mscal.stokes('+data_column+',\'LL\')))') # not working
            data_array_rms_per_chan = tb4.getcol(tb4.colnames()[0])[0]
            #print(data_array_rms_per_chan.shape) # (nchan, nstokes)
            tb4.close()
            # 
            # calc rms for all channels per stokes for each spw
            tb4 = query_casa_table(tb1, query_where_field_str + ' AND ' + query_where_spw_str, 
                                        columns = 'RMSS(GAGGR(amplitude('+data_column+')),[0,1])') 
                                        # open table tb4, data array has a shape of (nchan, nstokes)
                                        # see above
            data_array_rms = tb4.getcol(tb4.colnames()[0])[0]
            #print(data_array_rms.shape) # (nstokes)
            tb4.close()
            # 
            # store into info_dict
            if number_of_stokes >= 2:
                info_dict[fieldKey]['SPW']['RMS'].append( np.mean(data_array_rms) )
                info_dict[fieldKey]['SPW']['RMS_STOKES_LL'].append( data_array_rms[0] )
                info_dict[fieldKey]['SPW']['RMS_STOKES_RR'].append( data_array_rms[1] )
                info_dict[fieldKey]['SPW']['CHAN_RMS'].append( np.mean(data_array_rms_per_chan, axis=1) ) # merge along stokes axis
                info_dict[fieldKey]['SPW']['CHAN_RMS_STOKES_LL'].append( data_array_rms_per_chan[:,0] )
                info_dict[fieldKey]['SPW']['CHAN_RMS_STOKES_RR'].append( data_array_rms_per_chan[:,1] )
            elif number_of_stokes == 1:
                info_dict[fieldKey]['SPW']['RMS'].append( np.mean(data_array_rms) )
                info_dict[fieldKey]['SPW']['CHAN_RMS'].append( np.mean(data_array_rms_per_chan, axis=1) ) # single stokes axis
            elif number_of_stokes == 0:
                info_dict[fieldKey]['SPW']['RMS'].append( data_array_rms )
                info_dict[fieldKey]['SPW']['CHAN_RMS'].append( data_array_rms_per_chan ) # no stokes axis
            # 
            # calculate sum of EXPOSURE, EXPOSURE * BASELINE, and EXPOSURE * ALL, ALL means BASELINE * NSTOKES. 
            tb4 = query_casa_table(tb1, query_where_field_str + ' AND ' + query_where_spw_str, 
                                        columns = 'GSUM(EXPOSURE), GCOUNT(EXPOSURE)')
            exposure_sum = tb4.getcell(tb4.colnames()[0], 0)
            exposure_count = tb4.getcell(tb4.colnames()[1], 0)
            tb4.close()
            # 
            # store more into info_dict
            if number_of_stokes >= 2:
                info_dict[fieldKey]['SPW']['EXPOSURE_X_BASELINE'].append( exposure_sum ) # single stokes
                info_dict[fieldKey]['SPW']['EXPOSURE_X_ALL'].append( exposure_sum * float(number_of_stokes) ) # all stokes
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_BASELINE'].append( exposure_count ) # single stokes
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'].append( exposure_count * float(number_of_stokes) ) # all stokes
                info_dict[fieldKey]['SPW']['NUM_STOKES'].append( number_of_stokes )
            else:
                info_dict[fieldKey]['SPW']['EXPOSURE_X_BASELINE'].append( exposure_sum ) # single stokes
                info_dict[fieldKey]['SPW']['EXPOSURE_X_ALL'].append( exposure_sum ) # single stokes
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_BASELINE'].append( exposure_count ) # single stokes
                info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'].append( exposure_count ) # single stokes
                info_dict[fieldKey]['SPW']['NUM_STOKES'].append( number_of_stokes )
            # 
            # calc BMAJ BMIN for each CHAN of each SPW of each field (array operation)
            # interferometry: Fourier Transform is exp( 2 * pi * 1j * (u_m * x_rad + v_m * y_rad) / lambda_m )
            # "2.0*np.sqrt(2.0*np.log(2.0))" converts Gaussian sigma to FWHM
            # print(np.array(info_dict[fieldKey]['SPW']['CHAN_FREQ']).shape) # (nspw, nchan)
            info_dict[fieldKey]['SPW']['CHAN_BMAJ'].append( 2.99792458e8 / np.array(info_dict[fieldKey]['SPW']['CHAN_FREQ'])[-1,:] / info_dict[fieldKey]['UVW']['MAX'] / np.pi * 180.0) # in units of degrees
            info_dict[fieldKey]['SPW']['CHAN_BMIN'].append( 2.99792458e8 / np.array(info_dict[fieldKey]['SPW']['CHAN_FREQ'])[-1,:] / info_dict[fieldKey]['UVW']['MAX'] / np.pi * 180.0) # in units of degrees
            # 
            # calc BMAJ BMIN for each SPW of each field, taking the min of CHAN_FREQ
            info_dict[fieldKey]['SPW']['BMAJ'].append( np.min(info_dict[fieldKey]['SPW']['CHAN_BMAJ'][-1]) )
            info_dict[fieldKey]['SPW']['BMIN'].append( np.min(info_dict[fieldKey]['SPW']['CHAN_BMIN'][-1]) )
            # 
            # 
            #if ispw >= 2:
            #    break
            #sys.exit()
    # 
    # close table
    tb1.close() # # close table tb1
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
    if current_dict_level == 2:
        for k in info_dict.keys():
            if not (type(info_dict[k]) is dict):
                print_fmt_col_width = np.max([print_fmt_col_width, 15])
    #print_fmt_col_width += 1
    # 
    # loop dict keys
    for k in info_dict.keys():
        # if value is dict, iterate this function
        if type(info_dict[k]) is dict:
            printed_strings2 = print_interferometry_info_dict(info_dict[k], only_return_strings = True, current_dict_level = current_dict_level + 1)
            for k2 in printed_strings2:
                print_fmt = '%%-%ds : %%s' % (print_fmt_col_width)
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
                    if len(info_item) > 3:
                        print_fmt = '%%-%ds = [ %%s, ..., %%s ] (len=%%d)' % (print_fmt_col_width)
                        print_str = print_fmt % (k, str(info_item[0]), str(info_item[-1]), len(info_item) )
                    elif len(info_item) > 0:
                        print_fmt = '%%-%ds = [ %%s ] (len=%%d)' % (print_fmt_col_width)
                        print_str = print_fmt % (k, ', '.join(map(str, info_item)), len(info_item) )
                    else:
                        print_fmt = '%%-%ds = [ ] (len=0)' % (print_fmt_col_width)
                        print_str = print_fmt % (k, )
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
# def parseSpw()
# 
#   based on https://stackoverflow.com/questions/712460/interpreting-number-ranges-in-python
#   returns a set of selected values when a string in the form:
#   '1~4,6,8,10~12'
#   would return:
#   (1,2,3,4,6,7,10,11,12)
# 
def parseSpw(input_str="", no_chan=False):
    selection = {'spw':[], 'chan':[], 'spw+chan':[]}
    invalid = []
    # tokens are comma seperated values
    tokens = [t.strip() for t in input_str.split(',')]
    for token in tokens:
        # a token could be a spw, a spw+chan (separated with comma), or a range of spw
        # 
        # check if the input spw expression contains channels or not
        chan_expression = ''
        chan_selection = None
        chan_list = []
        if token.find(':') >= 0:
            tokens2 = [t.strip() for t in token.split(':')]
            if len(tokens2) > 1:
                token = tokens2[0]
                chan_expression = tokens2[1]
                chan_selection = parseSpw(chan_expression, no_chan=True)
                chan_list = chan_selection['chan']
        # 
        # check the input spw expression when split out any channel selection
        if len(token) > 0:
            if token[:1] == "<":
                token = "1~%s"%(token[1:])
        try:
            # typically tokens are plain old integers
            selection['spw'].append(int(token))
            selection['chan'].append(chan_list)
            if chan_expression != '':
                selection['spw+chan'].append(token+':'+chan_expression)
            else:
                selection['spw+chan'].append(token)
        except:
            # if not, then it might be a range
            try:
                tokens2 = [int(k.strip()) for k in token.split('~')]
                if len(tokens2) > 1:
                    tokens2.sort()
                    # we have items seperated by a dash
                    # try to build a valid range
                    first = tokens2[0]
                    last = tokens2[len(tokens2)-1]
                    for t in range(first, last+1):
                        selection['spw'].append(t)
                        selection['chan'].append(chan_list)
                        if chan_expression != '':
                            selection['spw+chan'].append(token+':'+chan_expression)
                        else:
                            selection['spw+chan'].append(token)
            except:
                # not an int and not a range...
                invalid.append(token)
    # Report invalid tokens before returning valid selection
    if len(invalid) > 0:
        print("Error! Invalid inputs: " + str(invalid))
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
                    beam = '', 
                    cell = '', 
                    imsize = 0, 
                    threshold = '', 
                    weighting = 'briggs', 
                    robust = 2.0, 
                    uvtaper = [], 
                    clean_to_nsigma = 1.5, 
                    info_dict_file = '',
                    script_file = 'run_casa_ms_clean_highz_gal.py', 
                    is_dry_run = False, 
                    overwrite = False, 
                   ):
    # 
    # check_ok
    check_ok = True
    # 
    # check my_clean_mode
    if my_clean_mode == '':
        print('Error! The input my_clean_mode is empty!')
        check_ok = False
    elif not my_clean_mode.lower().startswith('cube') and \
         not my_clean_mode.lower().startswith('cont') and \
         not my_clean_mode.lower().startswith('line') and \
         not my_clean_mode.lower().startswith('map'):
        print('Error! The input my_clean_mode is "%s", but it should be either "cube" or "continuum" (or "line_map" or "map" (TODO))!'%(my_clean_mode))
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
    # if not check_ok, print usage and exit
    if not check_ok:
        print("Please call this function like:")
        print("    clean_highz_gal('cube', 'example_vis_name.ms', 'example_field_name', 'example_output_image_name')")
        sys.exit()
    # 
    # grab_interferometry_info
    info_dict = grab_interferometry_info(vis)
    # 
    # check field empty
    if field == '':
        print('Error! The input field is empty!')
        print('       Available fields are: %s'%(', '.join(['"'+t+'"' for t in info_dict['FIELD']['NAME']])))
        sys.exit()
    # 
    # check field 
    if not ('FIELD_'+field in info_dict):
        print('Error! The input field "%s" is not in the info_dict of the data "%s"!'%(field, vis))
        print('       Available fields are: %s'%(', '.join(['"'+t+'"' for t in info_dict['FIELD']['NAME']])))
        sys.exit()
    # 
    # check spw empty
    if len(info_dict['FIELD_'+field]['SPW']['ID']) == 0:
        print('Error! The info_dict table shows zero SPW for the field %s! Maybe re-read the info_dict by deleting "%s" and run this code again?'%(field, re.sub(r'\.ms$', r'', vis, re.IGNORECASE) + '.info.dict.json'))
        print(info_dict['FIELD_'+field])
        sys.exit()
    # 
    # set spw selection according to the input
    if spw == '':
        selectdata = False
        spw_list = []
        ispw_list = []
        for ispw in range(len(info_dict['FIELD_'+field]['SPW']['ID'])):
            #print('info_dict[%s][\'SPW\'][\'NAME\'][%d] = %s'% ('FIELD_'+field, ispw, info_dict['FIELD_'+field]['SPW']['NAME'][ispw]) )
            if (not info_dict['FIELD_'+field]['SPW']['NAME'][ispw].startswith('WVR')) \
                and info_dict['FIELD_'+field]['SPW']['NAME'][ispw].find('ALMA') > 0 \
                and info_dict['FIELD_'+field]['SPW']['NAME'][ispw].find('FULL_RES') > 0:
                ispw_list.append(ispw) # ispw is the index for info_dict['FIELD_'+field]['SPW']['ID'] array
                spw_list.append(info_dict['FIELD_'+field]['SPW']['ID'][ispw])
            elif (info_dict['FIELD_'+field]['SPW']['NAME'][ispw] == 'none'):
                ispw_list.append(ispw) # ispw is the index for info_dict['FIELD_'+field]['SPW']['ID'] array
                spw_list.append(info_dict['FIELD_'+field]['SPW']['ID'][ispw])
    else:
        selectdata = True
        spw_chan_selection = parseSpw(spw)
        spw_list = spw_chan_selection['spw']
        ispw_list = []
        for ispw in range(len(spw_list)):
            if spw_list[ispw] in info_dict['FIELD_'+field]['SPW']['ID']:
                ispw_list.append(info_dict['FIELD_'+field]['SPW']['ID'].index(spw_list[ispw]))
            else:
                print('Error! The input spw %d is not in the info_dict of the data "%s"!'%(spw_list[ispw], vis))
                print('       Available spws are: %s'%(str(info_dict['FIELD_'+field]['SPW']['ID'])))
                sys.exit()
    #print('ispw_list', ispw_list)
    if len(ispw_list) == 0:
        print('Error! The spw list is empty?! This should not happen..')
        sys.exit()
    # 
    # set reffreq and restfreq if no input. 
    # -- reffreq is the Reference frequency for MFS (relevant only if nterms > 1)
    # -- restfreq is for translation of velocities. When no input, CASA tclean() will set it to the center of spw automatically.
    if my_clean_mode.lower().startswith('cont'):
        if reffreq == '':
            if spw == '':
                sys.stdout.write('Computing reffreq as the centroid frequency of all spws:')
                sys.stdout.flush()
            else:
                sys.stdout.write('Computing reffreq as the centroid frequency of the input spws:')
                sys.stdout.flush()
            # loop spw_list and print frequency info
            for ispw in ispw_list:
                sys.stdout.write(' %d (%.6f-%.6f GHz)'%(info_dict['FIELD_'+field]['SPW']['ID'][ispw], info_dict['SPW']['CHAN_FREQ'][ispw][0] / 1e9, info_dict['SPW']['CHAN_FREQ'][ispw][-1] / 1e9))
                sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()
            # 
            #print('ispw_list', ispw_list)
            if len(ispw_list) > 1:
                reffreq = '%0.9f GHz'%(np.mean(np.array(info_dict['SPW']['CHAN_FREQ'])[ispw_list][0]) / 1e9)
            else:
                reffreq = '%0.9f GHz'%(np.mean(np.array(info_dict['SPW']['CHAN_FREQ'])[ispw_list]) / 1e9)
        
    # 
    # set channel width if no input
    if width == '':
        if my_clean_mode.lower().startswith('cube'):
            width = '2' # channel width, default is 2 channels <TODO>
        #elif my_clean_mode.lower().startswith('map') or my_clean_mode.lower().startswith('line'):
        #    width = '1' # single-channel line map <TODO>
    # 
    # set imagename if no input
    if imagename == '':
        if vis.find(os.sep) >= 0:
            vis_name = os.path.basename(vis)
        else:
            vis_name = vis
        imagename = '%s_%s_%s'%(re.sub(r'\.ms$', r'', vis_name, re.IGNORECASE), \
                                re.sub(r'[^a-zA-Z0-9_+-]', r'_', field), \
                                re.sub(r'[^a-zA-Z0-9_+-]', r'_', my_clean_mode)
                               )
    # 
    # check imagename existence
    check_dir_ok = True
    for check_dir_suffix in ['.image', 
                             '.image.pbcor', 
                             '.mask', 
                             '.model', 
                             '.pb', 
                             '.psf', 
                             '.weight', 
                             '.residual', 
                             '.sumwt']:
        if os.path.isdir(imagename+check_dir_suffix): 
            if overwrite == False:
                print('Error! The output data "%s" already exists!'%(imagename+'.image'))
                check_dir_ok = False
            else:
                shutil.rmtree(imagename+check_dir_suffix)
    # 
    for check_file_suffix in ['.image.fits', '.residual.fits']:
        if os.path.isfile(imagename+check_file_suffix): 
            if overwrite == False:
                print('Error! The output file "%s" already exists!'%(imagename+check_file_suffix))
                check_dir_ok = False
            else:
                print('Backing-up previous output file "%s" as "%s.backup"'%(imagename+check_file_suffix, imagename+check_file_suffix))
                shutil.move(imagename+check_file_suffix, imagename+check_file_suffix+'.backup')
    # 
    if check_dir_ok == False:
        print('Error occurred! Please check the above error message!')
        sys.exit()
    # 
    # set clean threshold
    if threshold == '':
        # 
        # set clean to which sigma level
        #if np.isnan(clean_to_nsigma):
        #    clean_to_nsigma = 1.5 #<TODO># clean to how many sigma
        # 
        # check if selectdata==True (i.e., spw != '')
        if spw == '':
            sys.stdout.write('Computing uv plane rms per channel for all spws:')
            sys.stdout.flush()
        else:
            sys.stdout.write('Computing uv plane rms per channel for the input spws:')
            sys.stdout.flush()
        # loop spw and print rms info
        for ispw in ispw_list:
            sys.stdout.write(' %d (%.6f mJy/beam)'%(info_dict['FIELD_'+field]['SPW']['ID'][ispw], info_dict['FIELD_'+field]['SPW']['RMS'][ispw] * 1e3))
            sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()
        # 
        # image plane rms per channel = 
        #     visibility rms per channel / sqrt( N_ant * (N_ant-1) * (t_source / t_interval) * n_polar ) -- see https://casaguides.nrao.edu/index.php/DataWeightsAndCombination
        # --> (info_dict['SPW']['RMS'])  / sqrt( N_baseline        * N_scan                  * N_stokes )
        # --> (info_dict['SPW']['RMS'])  / sqrt( info_dict[fieldKey]['SPW']['NUM_SCAN_X_ALL'] )
        # 
        # where NUM_SCAN_X_BASELINE == N_ant * (N_ant-1) * (t_source / t_interval), 
        #   and NUM_SCAN_X_ALL == N_ant * (N_ant-1) * (t_source / t_interval) * n_polar, 
        # 
        image_plane_rms_mJy_per_beam = np.mean( np.array(info_dict['FIELD_'+field]['SPW']['RMS'])[ispw_list] ) \
                                       / np.sqrt( np.array(info_dict['FIELD_'+field]['SPW']['NUM_SCAN_X_ALL'])[ispw_list] ) \
                                       * 1e3 # in units of mJy/beam
        print('image plane rms per channel = %s mJy/beam'%(image_plane_rms_mJy_per_beam))
        # 
        # check if selectdata==True (i.e., spw != '') and has channel selection expression
        if spw != '':
            for ispw in ispw_list:
                if len(spw_chan_selection['chan'][ispw]) > 0:
                    image_plane_rms_mJy_per_beam = np.array(info_dict['FIELD_'+field]['SPW']['RMS'])[ispw] \
                                       / np.sqrt( np.array(info_dict['FIELD_'+field]['SPW']['NUM_SCAN_X_ALL'])[ispw] ) \
                                       / np.sqrt(len(spw_chan_selection['chan'][ispw])) \
                                       * 1e3 # in units of mJy/beam
                    print('image plane rms of spw %d over %d channels = %s mJy/beam'%(spw_list[ispw], len(spw_chan_selection['chan'][ispw]), image_plane_rms_mJy_per_beam))
        # 
        threshold = '%0.6f mJy'%(np.min(image_plane_rms_mJy_per_beam) * clean_to_nsigma) # in units of mJy/beam
    # 
    # set stokes
    if stokes == '':
        stokes = 'I' # merge polarizations, Stokes I = (LL + RR)/2 = (XX + YY)/2
    # 
    # print message
    print('spw_list = %s'%(spw_list))
    print('reffreq = %s'%(reffreq)) # for continuum
    print('restfreq = %s'%(restfreq)) # for line, if empty CASA tclean will compute the centeroid frequency by itself
    print('threshold = %s'%(threshold))
    # 
    # set other parameters
    #start = ''
    #nchan = ''
    if beam == '':
        restoringbeam = '%.5g arcsec'%(np.min([np.array(info_dict['FIELD_'+field]['SPW']['BMAJ'])[ispw_list]*3600.0, \
                                       np.array(info_dict['FIELD_'+field]['SPW']['BMIN'])[ispw_list]*3600.0]))
        # or 'common'? # Automatically estimate a common beam shape/size appropriate for all planes.
    else:
        restoringbeam = beam 
    # 
    if cell == '':
        synthesized_beam_sampling_factor = 6.45 # 5.0
        cell_arcsec = np.min([np.array(info_dict['FIELD_'+field]['SPW']['BMAJ'])[ispw_list]*3600.0, \
                              np.array(info_dict['FIELD_'+field]['SPW']['BMIN'])[ispw_list]*3600.0]) \
                      / synthesized_beam_sampling_factor # in units of arcsec
        cell = '%0.5g arcsec'%(cell_arcsec) # in units of arcsec
    # 
    if imsize == 0:
        imsize = np.max(np.array(info_dict['FIELD_'+field]['SPW']['PRIMARY_BEAM'])[ispw_list])*3600.0 * 2.0 / cell_arcsec # 2.0 * PB, in units of pixel
        imsize = get_optimized_imsize(imsize)
    # 
    if my_clean_mode.lower().startswith('cube'):
        gridder = 'mosaic' # 'standard'
        specmode = 'cube' # for spectral line cube
    elif my_clean_mode.lower().startswith('cont'):
        gridder='standard'
        specmode = 'mfs'
    elif my_clean_mode.lower().startswith('map') or my_clean_mode.lower().startswith('line'):
        gridder = 'mosaic' # 'standard'
        specmode = 'cube' # for single-channel line map
    outframe = 'LSRK'
    deconvolver = 'hogbom'
    usemask = 'pb' # construct a 1/0 mask at the 0.2 level
    pbmask = 0.2 # data outside this pbmask will not be fitted
    mask = '' #<TODO># 
    pblimit = 0.1 # data outside this pblimit will be output as NaN
    pbcor = True # create both pbcorrected and uncorrected images
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
    if os.path.isfile(script_file):
        print('Found existing "%s"! Backing it up as "%s"'%(script_file, script_file+'.backup'))
        shutil.move(script_file, script_file+'.backup')
    with open(script_file, 'w') as fp:
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
        fp.write('\n')
        fp.write('\n')
        fp.write('imagename = \'%s\'\n'%(imagename+'.image'))
        fp.write('fitsimage = \'%s\'\n'%(imagename+'.image.fits'))
        fp.write('\n')
        fp.write('inp(exportfits)\n')
        fp.write('\n')
        fp.write('exportfits()\n')
        fp.write('\n')
        fp.write('\n')
        fp.write('\n')
        fp.write('imagename = \'%s\'\n'%(imagename+'.residual'))
        fp.write('fitsimage = \'%s\'\n'%(imagename+'.residual.fits'))
        fp.write('\n')
        fp.write('inp(exportfits)\n')
        fp.write('\n')
        fp.write('exportfits()\n')
        fp.write('\n')
        fp.write('\n')
        print('Output script to "%s"!'%(script_file))
    # 
    # then run casa
    if is_dry_run == False:
        try: 
            if 'casa' in globals() and 'tclean' in globals():
                type(tclean)
                print('Currently we are in CASA IPython! Running CASA `clean`!')
                saveinputs(tclean, script_file+'.tclean.saveinputs.txt') # store parameters in file
                print('Saved tclean parameters to "%s"!'%(script_file+'tclean.saveinputs.txt'))
                #tget(clean, parfile) # restore parameters from file
                inp(tclean)
                tclean()
        except:
            print('Currently we are not in CASA IPython! Please run the output script within CASA by yourself!')
            print('e.g., casa -c "execfile(\'%s\')"'%(script_file))
    else:
        print('This is a dry run!Please run the output script within CASA by yourself!')
        print('e.g., casa -c "execfile(\'%s\')"'%(script_file))








# 
# main
# 
def main():
    
    # 
    # initialize variables
    if 'vis' in locals():
        vis = locals()['vis']
    else:
        vis = ''
    
    if 'out' in locals():
        out = locals()['out']
    else:
        out = ''
    
    if 'field' in locals():
        field = locals()['field']
    else:
        field = ''
    
    if 'spw' in locals():
        spw = locals()['spw']
    else:
        spw = ''
    
    if 'width' in locals():
        width = locals()['width']
    else:
        width = ''
    
    if 'freq' in locals():
        freq = locals()['freq']
    else:
        freq = ''
    
    if 'beam' in locals():
        beam = locals()['beam']
    else:
        beam = ''
    
    if 'cell' in locals():
        cell = locals()['cell']
    else:
        cell = ''
    
    if 'imsize' in locals():
        imsize = locals()['imsize']
    else:
        imsize = 0
    
    if 'phasecenter' in locals():
        phasecenter = locals()['phasecenter']
    else:
        phasecenter = ''
    
    if 'threshold' in locals():
        threshold = locals()['threshold']
    else:
        threshold = ''
    
    if 'clean_mode' in locals():
        clean_mode = locals()['clean_mode']
    else:
        clean_mode = 'cube' # cube, continuum
    
    if 'script_file' in locals():
        script_file = locals()['script_file']
    else:
        script_file = ''
    
    if 'is_dry_run' in locals():
        is_dry_run = locals()['is_dry_run']
    else:
        is_dry_run = False
    
    # 
    # check globals()
    # 
    # read user input
    user_input_ok = True
    iarg = 1
    while iarg < len(sys.argv):
        istr = re.sub(r'[-]+', r'-', sys.argv[iarg]).lower()
        if istr == '-vis' or istr == '-ms':
            if iarg+1 < len(sys.argv):
                iarg += 1
                vis = sys.argv[iarg]
                print('vis = %s'%(vis))
        elif istr == '-gal' or istr == '-field':
            if iarg+1 < len(sys.argv):
                iarg += 1
                field = sys.argv[iarg]
                print('field = %s'%(field))
        elif istr == '-out' or istr == '-output':
            if iarg+1 < len(sys.argv):
                iarg += 1
                out = sys.argv[iarg]
                print('out = %s'%(out))
        elif istr == '-spw':
            if iarg+1 < len(sys.argv):
                iarg += 1
                spw = sys.argv[iarg]
                print('spw = %s'%(spw))
        elif istr == '-width':
            if iarg+1 < len(sys.argv):
                iarg += 1
                width = sys.argv[iarg]
                print('width = %s'%(width))
        elif istr == '-freq':
            if iarg+1 < len(sys.argv):
                iarg += 1
                freq = sys.argv[iarg]
                print('freq = %s'%(freq))
        elif istr == '-beam':
            if iarg+1 < len(sys.argv):
                iarg += 1
                beam = sys.argv[iarg]
                print('beam = %s'%(beam))
        elif istr == '-cell':
            if iarg+1 < len(sys.argv):
                iarg += 1
                cell = sys.argv[iarg]
                print('cell = %s'%(cell))
        elif istr == '-imsize':
            if iarg+1 < len(sys.argv):
                iarg += 1
                imsize = int(sys.argv[iarg])
                print('imsize = %s'%(imsize))
        elif istr == '-phasecenter':
            if iarg+1 < len(sys.argv):
                iarg += 1
                phasecenter = sys.argv[iarg]
                print('phasecenter = %s'%(phasecenter))
        elif istr == '-threshold':
            if iarg+1 < len(sys.argv):
                iarg += 1
                threshold = sys.argv[iarg]
                print('threshold = %s'%(threshold))
        elif istr == '-mode' or istr == '-clean-mode':
            if iarg+1 < len(sys.argv):
                iarg += 1
                clean_mode = sys.argv[iarg]
        elif istr == '-dry-run':
            is_dry_run = True
        elif istr == '-overwrite':
            overwrite = True
        elif istr == '-debug':
            SET_DEBUG_LEVEL += 1
        else:
            #if vis == '':
            #    vis = sys.argv[iarg]
            #elif field == '':
            #    field = sys.argv[iarg]
            #elif spw == '':
            #    spw = sys.argv[iarg]
            print('Error! Unknown/unimplemented input "%s"'%(sys.argv[iarg]))
            user_input_ok = False
        # 
        iarg += 1
    
    # 
    # check user input
    if vis == '' or user_input_ok == False:
        usage()
        if user_input_ok == False:
            print('Please check the error message about the user inputs above usage.')
        sys.exit()
    
    # 
    # determine clean_mode
    if width != '':
        clean_mode = 'cube'
        if width == '0':
            clean_mode = 'continuum'
            width = ''
    
    # 
    # fix field "" 
    field = field.replace('"','')
    
    # 
    # print message
    #print('vis = %s'%(vis))
    #print('field = %s'%(field))
    #print('spw = %s'%(spw))
    #print('width = %s'%(width))
    #print('freq = %s'%(freq))
    print('clean_mode = %s'%(clean_mode))
    print('is_dry_run = %s'%(is_dry_run))
    
    # 
    # test subroutine parseSpw()
    #print('parseSpw(\'1~4,6,8,10~12\')', parseSpw('1~4,6,8,10~12'))
    #print('parseSpw(\'1~4:5~59,5:2,6~10\')', parseSpw('1~4:5~59,5:2,6~10'))
    #sys.exit()
    
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
    # try to get clean_highz_gal() argument list from locals() and pass arguments as a dict to the function.
    try:
        arg_list = inspect.signature(clean_highz_gal).parameters.keys()
        arg_list = list(arg_list)
    except:
        try:
            arg_list = inspect.getfullargspec(clean_highz_gal)[0]
        except:
            try:
                arg_list = inspect.getargspec(clean_highz_gal)[0]
            except:
                pass
    #print(arg_list)
    #print(locals()['vis'])
    #arg_parser = lambda l, d=locals(): dict((k, d[k]) for k in l if k in d)
    #arg_dict = arg_parser(arg_list)
    #print(type(arg_dict), arg_dict.keys())
    #print(type(locals()), locals().keys())
    #sys.exit()
    
    
    # 
    # check clean_mode <TODO> cube, continuum, line_map
    my_clean_mode = clean_mode
    
    
    # 
    # check output
    imagename = out
    restoringbeam = beam
    #field = gal
    if freq != '':
        if clean_mode.lower().startswith('cont'):
            reffreq = freq
        else:
            restfreq = freq
    
    
    # 
    # run test 
    #grab_interferometry_info(vis)
    if script_file == '':
        script_file = 'run_casa_ms_clean_highz_gal_%s.py'%(my_clean_mode)
    # 
    arg_parser = lambda l, d=locals(): dict((k, d[k]) for k in l if k in d)
    # 
    clean_highz_gal(**arg_parser(arg_list))
    
        







# 
# __main__
# 
if __name__ == '__main__':
    # 
    main()















