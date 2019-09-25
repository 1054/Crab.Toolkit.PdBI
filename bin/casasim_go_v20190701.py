#!/usr/bin/env python
# 
# This code needs to be ran in CASA.
# 
# This code simulates ALMA data. 
# 
# Usage:
#     casa
#     execfile(\'casasim_go.py\') <TODO>
# 
# Usage 2:
#     casa
#     sys.path.append('/Users/dzliu/Cloud/Github/Crab.Toolkit.PdBI/bin')
#     simfreq = '339.0 GHz'
#     simcell = '0.062 arcsec'
#     import casasim_go
#     reload(casasim_go)
#     skymodel, complist = casasim_go.simulate_Gaussian(locals())
#     casasim_go.simulate_Visibilities(locals())
# 
# 20190723: init
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil
import numpy as np
import inspect
import random



# 
# A function to get arg list of another function
# 
#def get_arg_list(func_name):
#    inspect__dir__ = dir(inspect)
#    arg_list = []
#    if 'signature' in inspect__dir__:
#        arg_list = inspect.signature(func_name).parameters.keys()
#        arg_list = list(arg_list)
#    elif 'getfullargspec' in inspect__dir__:
#        arg_list = inspect.getfullargspec(func_name)[0]
#    elif 'getargspec' in inspect__dir__:
#        arg_list = inspect.getargspec(func_name)[0]
#    else:
#        print('Error! Could not call inspect.getargspec() or inspect.getfullargspec() or inspect.signature()!')
#        sys.exit()
#    return arg_list



# 
# Simulate a Gaussian shape source
# 
def simulate_Gaussian(locals_dict):
    # 
    qa = locals_dict['qa']
    cl = locals_dict['cl']
    ia = locals_dict['ia']
    exportfits = locals_dict['exportfits']
    # 
    # load variables
    if not ('simfreq' in locals_dict):
        simfreq = '339.0GHz'
        #raise ValueError('Please set simfreq!')
    else:
        simfreq = locals_dict['simfreq']
    if not ('simcell' in locals_dict):
        simcell = '0.062arcsec'
        #raise ValueError('Please set simcell!')
    else:
        simcell = locals_dict['simcell']
    if not ('simsize' in locals_dict):
        simsize = 256
    else:
        simsize = locals_dict['simsize']
    if not ('skymodel' in locals_dict):
        skymodel = "casasim_Gaussian.fits"
    else:
        skymodel = locals_dict['skymodel']
        if skymodel == '': raise ValueError('Error! skymodel is empty!')
    if not ('complist' in locals_dict):
        complist = "casasim_Gaussian.cl"
    else:
        complist = locals_dict['complist']
        if complist == '': raise ValueError('Error! complist is empty!')
    # 
    if not ('casasim_source_models' in locals_dict):
        casasim_source_models = []
        #casasim_source_models.append({'ra':'10h00m00.0s','dec':'-30d00m00.0s','flux':2.0,'fluxunit':'mJy','shape':'Gaussian','majoraxis':'0.6arcsec','minoraxis':'0.4arcsec','positionangle':'0.0deg'})
        #<TODO># test reading ds9 regions file
        with open('ds9.reg', 'r') as fp:
            for fline in fp.readlines():
                if fline.startswith('ellipse'):
                    ra, dec, majoraxis, minoraxis, positionangle = re.sub(r'ellipse\(([0-9:+-\.]+)\s*,\s*([0-9:+-\.]+)\s*,\s*([0-9Ee:+-\.\"]+)\s*,\s*([0-9Ee:+-\.\"]+)\s*,\s*([0-9Ee:+-\.]+)\s*\)\s*.*', r'\1 \2 \3 \4 \5', fline.strip()).split(' ')
                    if ra.find(':')>=0: ra = re.sub(r'([0-9+-]+):([0-9+-]+):([0-9+-\.]+)', r'\1h\2m\3s', ra)
                    if dec.find(':')>=0: dec = re.sub(r'([0-9+-]+):([0-9+-]+):([0-9+-\.]+)', r'\1d\2m\3s', dec)
                    if majoraxis.endswith('"'): majoraxis = majoraxis.replace('"','arcsec')
                    if minoraxis.endswith('"'): minoraxis = minoraxis.replace('"','arcsec')
                    majoraxisvalue = qa.convert(majoraxis,'arcsec')['value']
                    minoraxisvalue = qa.convert(minoraxis,'arcsec')['value']
                    positionanglevalue = float(positionangle) # deg
                    if majoraxisvalue < minoraxisvalue:
                        majoraxis, minoraxis = minoraxis, majoraxis
                        positionangle = '%s'%(positionanglevalue + 90.0)
                    positionangle += 'deg'
                    flux_max = 2.0 #<TODO># test random flux between 0.2 - 2.0 mJy/beam
                    flux_min = 0.2 #<TODO># test random flux between 0.2 - 2.0 mJy/beam
                    flux = (random.random() - 0.0) / (1.0 - 0.0) * (flux_max - flux_min) + flux_min #<TODO># test random flux
                    casasim_source_models.append({'ra':ra,'dec':dec,'flux':flux,'fluxunit':'mJy','shape':'Gaussian','majoraxis':majoraxis,'minoraxis':minoraxis,'positionangle':positionangle})
                    #print(casasim_source_models[-1])
    # 
    # closes any open component lists, if any.
    cl.done()
    # 
    # backup previous result if any
    skymodelname = re.sub(r'^(.*)\.fits', r'\1', skymodel, re.IGNORECASE)
    if os.path.isdir(skymodelname+'.im'):
        if os.path.isdir(skymodelname+'.im'+'.backup'):
            shutil.rmtree(skymodelname+'.im'+'.backup')
        shutil.move(skymodelname+'.im', skymodelname+'.im'+'.backup')
    if os.path.isdir(complist):
        if os.path.isdir(complist+'.backup'):
            shutil.rmtree(complist+'.backup')
        shutil.move(complist, complist+'.backup')
    # 
    # prepare to set sim image center RA Dec by taking the position of the first model source
    simCenRA = None
    simCenDec = None
    # 
    # prepare to add components
    cl_addcomponent_arg_list = ['flux','fluxunit','shape','majoraxis','minoraxis','positionangle']
    for imodel, casasim_source_model in enumerate(casasim_source_models):
        cl_component_properties = {}
        for key in casasim_source_model.keys():
            if key in cl_addcomponent_arg_list and key != 'dir' and key != 'freq':
                cl_component_properties[key] = casasim_source_model[key]
                print('component %d, %s = %s'%(imodel, key, cl_component_properties[key]))
        cl.addcomponent(dir='J2000 %s %s'%(casasim_source_model['ra'], casasim_source_model['dec']), 
                        freq=simfreq, 
                        **cl_component_properties)
        if simCenRA is None: simCenRA = casasim_source_model['ra']
        if simCenDec is None: simCenDec = casasim_source_model['dec']
    # 
    # print message
    print('simCenRA = %s'%(simCenRA))
    print('simCenDec = %s'%(simCenDec))
    print('simfreq = %s'%(simfreq))
    print('simcell = %s'%(simcell))
    print('simsize = %s'%(simsize))
    print('complist = %s'%(complist))
    print('skymodel = %s'%(skymodel))
    print('casasim_source_models = %s'%(str(casasim_source_models)))
    # 
    # process image
    ia.fromshape(skymodelname+".im", [simsize,simsize,1,1], overwrite=True) # image a
    cs = ia.coordsys() # coordinate system
    cs.setunits(['rad', 'rad', '', 'Hz'])
    cell_rad = qa.convert(qa.quantity(simcell), "rad")['value']
    cs.setincrement([-cell_rad,cell_rad],'direction')
    cs.setreferencevalue([qa.convert(simCenRA,'rad')['value'], qa.convert(simCenDec,'rad')['value']], type="direction")
    cs.setreferencevalue(qa.convert(qa.quantity(simfreq),'Hz')['value'], 'spectral')
    cs.setincrement('31.25MHz','spectral')
    ia.setcoordsys(cs.torecord())
    ia.setbrightnessunit("Jy/pixel")
    ia.modify(cl.torecord(),subtract=False)
    exportfits(imagename = skymodelname+'.im', fitsimage = skymodelname+'.fits', overwrite = True)
    print('Output to "%s"!'%(skymodelname+'.im'))
    print('Output to "%s"!'%(skymodelname+'.fits'))
    # 
    cl.rename(complist)
    cl.done()
    print('Output to "%s"!'%(complist))
    return skymodel, complist
    # 
    #locals_dict.update({'skymodel':skymodelname+'.fits', 'complist':complist})



# 
# 
# 
def simulate_Visibilities(locals_dict):
    # 
    simobserve = locals_dict['simobserve']
    qa = locals_dict['qa']
    imhead = locals_dict['imhead']
    split = locals_dict['split']
    exportuvfits = locals_dict['exportuvfits']
    #inp = locals_dict['inp']
    # 
    # load variables
    if not ('project' in locals_dict):
        project = "casasim_Project"
    else:
        project = locals_dict['project']
    if not ('skymodel' in locals_dict):
        skymodel = "casasim_Gaussian.fits"
    else:
        skymodel = locals_dict['skymodel']
    if not ('complist' in locals_dict):
        complist = ""
    else:
        complist = locals_dict['complist']
    if not ('compwidth' in locals_dict):
        compwidth = ''
    else:
        compwidth = locals_dict['compwidth']
    if not ('inwidth' in locals_dict):
        inwidth = ''
    else:
        inwidth = locals_dict['inwidth']
    if not ('antennalist' in locals_dict):
        antennalist = 'alma;0.2arcsec'
    else:
        antennalist = locals_dict['antennalist']
    if not ('totaltime' in locals_dict):
        totaltime = ''
    else:
        totaltime = locals_dict['totaltime']
    if not ('integration' in locals_dict):
        integration = '600s'
    else:
        integration = locals_dict['integration']
    if not ('thermalnoise' in locals_dict):
        thermalnoise = '' # 'tsys-atm' (user_pwv=XXX)
    else:
        thermalnoise = locals_dict['thermalnoise']
    if not ('obsmode' in locals_dict):
        obsmode = 'int' # 'int' or 'sd'
    else:
        obsmode = locals_dict['obsmode']
    if not ('direction' in locals_dict):
        direction = '' # "J2000 10h00m00.0s -30d00m00.0s" # If left unset, simobserve will use the center of the skymodel image. -- not working?
    else:
        direction = locals_dict['direction']
    if not ('mapsize' in locals_dict):
        mapsize = '5arcsec'
    else:
        mapsize = locals_dict['mapsize']
    # 
    # print message
    print('project = %s'%(project))
    print('skymodel = %s'%(skymodel))
    #print('complist = %s'%(complist))
    #print('direction = %s'%(direction))
    # 
    # backup previous result if any
    if os.path.isdir(os.path.join(project, 'split_field_0_spw_0.ms')):
        if os.path.isdir(os.path.join(project, 'split_field_0_spw_0.ms'+'.backup')):
            shutil.rmtree(os.path.join(project, 'split_field_0_spw_0.ms'+'.backup'))
        shutil.move(os.path.join(project, 'split_field_0_spw_0.ms'), 
                    os.path.join(project, 'split_field_0_spw_0.ms'+'.backup'))
    # 
    # run simobserve task
    print('Running simobserve(project=\'%s\', ...)'%(project))
    project_in = project
    simobserve(project = project, 
               skymodel = skymodel, 
               complist = complist, 
               direction = direction, 
               mapsize = mapsize, 
               ptgfile = '', 
               compwidth = compwidth, 
               inwidth = inwidth, 
               obsmode = obsmode, 
               antennalist = antennalist, 
               integration = integration, 
               thermalnoise = thermalnoise, 
               verbose = True, 
               overwrite = True, 
              )
    project = project_in # it seems 'project' variable got changed after simobserve ...
    # 
    # check output
    if antennalist.endswith('.cfg'):
        outname = antennalist.replace('.cfg','').replace('alma.','alma_')
    else:
        outname = antennalist.replace(';','_').replace('alma.','alma_')
    if not (os.path.isdir(os.path.join(project, project+'.'+outname+'.ms'))):
        raise Exception('Error! Failed to run simobserve()! Could not find "%s"!'%(os.path.join(project, project+'.'+outname+'.ms')))
    print('Output to "%s"!'%(os.path.join(project, project+'.'+outname+'.ms')))
    # 
    # exportuvfits
    split(vis = os.path.join(project, project+'.'+outname+'.ms'), 
          outputvis = os.path.join(project, 'split_field_0_spw_0.ms'), 
          keepmms = False, 
          keepflags = False, 
          field = '0', 
          spw = '0', 
          timebin = '30s', 
          )
    if not (os.path.isdir(os.path.join(project, 'split_field_0_spw_0.ms'))):
        raise Exception('Error! Failed to run split()! Could not find "%s"!'%(os.path.join(project, 'split_field_0_spw_0.ms')))
    print('Output to "%s"!'%(os.path.join(project, 'split_field_0_spw_0.ms')))
    # 
    # exportuvfits
    exportuvfits(vis = os.path.join(project, 'split_field_0_spw_0.ms'), 
                 fitsfile = os.path.join(project, 'split_field_0_spw_0.uvfits'), 
                 multisource = False, 
                 combinespw = False, 
                 overwrite = True, 
                 )
    if not (os.path.isfile(os.path.join(project, 'split_field_0_spw_0.uvfits'))):
        raise Exception('Error! Failed to run exportuvfits()! Could not find "%s"!'%(os.path.join(project, 'split_field_0_spw_0.uvfits')))
    print('Output to "%s"!'%(os.path.join(project, 'split_field_0_spw_0.uvfits')))









# 
# 
# 
#def convolve_model_image_with_beam(locals_dict):
#    # 
#    imsmooth = locals_dict['imsmooth']
#    # 
#    # load variables
#    if not ('project' in locals_dict):
#        project = "casasim_Project"
#    else:
#        project = locals_dict['project']
#    if not ('skymodel' in locals_dict):
#        skymodel = "casasim_Gaussian.fits"
#    else:
#        skymodel = locals_dict['skymodel']
#    if not ('beam' in locals_dict):
#        skymodel = "casasim_Gaussian.fits"
#    else:
#        skymodel = locals_dict['skymodel']
#    # 
#    # check antennalist
#    if not ('antennalist' in locals_dict):
#        raise Exception('Errro! antennalist was not set!')
#    else:
#        antennalist = locals_dict['antennalist']
#    # 
#    if antennalist.endswith('.cfg'):
#        outname = antennalist.replace('.cfg','').replace('alma.','alma_')
#    else:
#        outname = antennalist.replace(';','_').replace('alma.','alma_')
#    # 
#    if not (os.path.isdir(os.path.join(project, project+'.'+outname+'.ms'))):
#        raise Exception('Error! Could not find "%s"! Please run simobserve() first!'%(os.path.join(project, project+'.'+outname+'.ms')))
#    # 
#    print('Reading "%s"'%(os.path.join(project, project+'.'+outname+'.ms')))
#    # 
#    # get clean beam size
#    restoringbeam = 
#    # 
#    # skymodelname
#    skymodelname = re.sub(r'\.fits$', r'', skymodel, re.IGNORECASE)
#    # 
#    # output a smoothed version 
#    imsmooth(imagename = skymodel, kernel = 'gauss', beam = beam)
#    print('Output to "%s"!'%(skymodelname+'_convolved.fits'))








