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
# 20190816: simulate_Models, Sersic, skyfreq
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil
import numpy as np
import inspect
import random
try:
    import astropy
except:
    #pipinstallpath = ''
    #for temppath in sys.path:
    #    print(temppath, temppath.endswith('site-packages'))
    #    if temppath.endswith('site-packages'):
    #        pipinstallpath = temppath
    #if pipinstallpath != '':
    #    #import subprocess
    #    #subprocess.call('pip-2.7 install --install-option="--prefix=/Users/dzliu/Library/Python/2.7/lib/python/site-packages" astropy')
    #    #print('Running:')
    #    #print('pip-2.7 install --install-option="--prefix=%s" --ignore-installed astropy%(pipinstallpath))
    #    #os.system('pip-2.7 install --install-option="--prefix=%s" --ignore-installed astropy%(pipinstallpath))
    if os.path.isdir('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages'):
        sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
    try:
        import astropy
    except ImportError:
        raise ImportError('Error! Could not import astropy!')
# 
from astropy.wcs import wcs
from astropy.wcs.utils import proj_plane_pixel_scales
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import Angle
from astropy.modeling.models import Sersic2D
#from math import gamma as gamma_function
from scipy.special import gamma, gammainc, gammaincinv
#from scipy.optimize import brentq, newton, fsolve



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
# Rotate a Matrix
# 
def rotate_via_Rotation_Matrix(X, Y, RotateAngle, Center=None):
    # rotate the image, note that pos angle is about +Y, so angle is: 
    angle = float(RotateAngle) # deg
    theta = (angle/180.) * np.pi # rad
    if np.isscalar(X):
        X = [X]
    if np.isscalar(Y):
        Y = [Y]
    if Center is None:
        XY = np.vstack((np.array(X).flatten(),np.array(Y).flatten()))
    else:
        if np.isscalar(Center):
            Center = [Center, Center]
        elif len(Center) == 1:
            Center = [Center[0], Center[0]]
        XY = np.vstack(((np.array(X)-Center[0]).flatten(),(np.array(Y)-Center[1]).flatten()))
    rotMatrix = np.array([[np.cos(theta), -np.sin(theta)], 
                          [np.sin(theta),  np.cos(theta)]]) # counterclockwise
    #print(rotMatrix, XY, XY.shape)
    rotXY = rotMatrix.dot(XY)
    rotX = rotXY[0].reshape(X.shape)
    rotY = rotXY[1].reshape(Y.shape)
    if Center is None:
        return rotX, rotY
    else:
        return rotX+Center[0], rotY+Center[1]

def test_Rotating_via_Rotation_Matrix():
    print(rotate_via_Rotation_Matrix([100,40,30],[100,40,30], 45, Center=[100,100]))



# 
# Make a 2D Sersic model image
# 
def make_2D_Sersic(imsize, center, flux, size, Sersic_index):
    # Note that size values are half-light diameter (NOT radius) or FWHM, within which there are half the flux.
    if np.isscalar(imsize):
        imsize = [imsize, imsize] # NX, NY
    if len(imsize) == 1:
        imsize = [imsize[0], imsize[0]]
    if np.isscalar(center):
        center = [center, center] # X0, Y0
    if len(center) == 1:
        center = [center[0], center[0]]
    if np.isscalar(size):
        size = [size, size] # MAJ_FWHM, MIN_FWHM, POS_ANGLE
    if len(size) == 1:
        size = [size[0], size[0]]
    # 
    if len(size) >= 3:
        print('make_2D_Sersic: imsize=%dx%d, center=(%d,%d), objsize=(%.2f,%.2f), posangle=%.1f'%(imsize[0], imsize[1], center[0], center[1], size[0], size[1], size[2]))
    else:
        print('make_2D_Sersic: imsize=%dx%d, center=(%d,%d), objsize=(%.2f,%.2f)'%(imsize[0], imsize[1], center[0], center[1], size[0], size[1]))
    # 
    y, x = np.mgrid[1:imsize[1]+1, 1:imsize[0]+1] # 1-based
    x = x.astype(float)
    y = y.astype(float)
    x0 = float(center[0]) # 1-based
    y0 = float(center[1]) # 1-based
    #xsig = size[0] / (2.0*np.sqrt(2.0*np.log(2.0)))
    #ysig = size[1] / (2.0*np.sqrt(2.0*np.log(2.0)))
    xhalf = size[0] / 2.0 # effective radius R_e that encloses half of the total light, for Gaussian it is FWHM/2.0, size is FWHM
    yhalf = size[1] / 2.0 # effective radius R_e that encloses half of the total light, for Gaussian it is FWHM/2.0, size is FWHM
    n = float(Sersic_index)
    # 
    use_astropy_Sersic2D = False # True # False #<TODO># 
    # 
    if len(size) >= 3 and (n < 0 or use_astropy_Sersic2D == False):
        # rotate the image, now major axis is along +X, 
        # the input size[2] is pos angle about +Y, so angle is 
        #print('x y shape', x.shape, y.shape)
        #print(x[0,0], y[0,0])
        x, y = rotate_via_Rotation_Matrix(x, y, -(size[2]+90.0), Center = [x0, y0]) # angle is negative because we need backward rotation
        #print(x[0,0], y[0,0])
        #x0, y0 = rotate_via_Rotation_Matrix(x, y, size[2]+90.0, Center = [x0, y0]) # center is unchanged
        pass
    # 
    if n > 0:
        if use_astropy_Sersic2D == True:
            if len(size) >= 3:
                angle = float(size[2]) + 90.0 # deg, convert from pos angle (+Y) to angle (+X)
                theta = (angle/180.) * np.pi # rad
            else:
                theta = 0.0
            #mod = Sersic2D(amplitude=1.0, r_eff=size[0], n=n, x_0=x0, y_0=y0, ellip=1.0-(size[1]/size[0]), theta=theta)
            mod = Sersic2D(amplitude=1.0, r_eff=xhalf, n=n, x_0=x0, y_0=y0, ellip=1.0-(yhalf/xhalf), theta=theta) #<TODO># must make sure xhalf > yhalf
            img = mod(x, y) # peak is 1.0
            img = img / np.sum(img) * flux #<TODO># What is the area of a Sersic area?
        else:
            # 
            # Sersic function:
            # exp(-bn * (r / r_eff)**(1/n))
            # 
            squaredvalues = ((x-x0)/xhalf)**2 + ((y-y0)/yhalf)**2
            expimg = (squaredvalues)**(0.5*(1.0/n))
            #solving_gamma_function = lambda bnx: (gammainc(2*n,bnx) - 1.0/2.0) # solving 2 * gamma(2n,bn) = Gamma(2n) # see http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html Eq.4 # Note that gammainc is normalized to 1.0 max, so here we solve it equals 0.5. 
            #bn = fsolve(solving_gamma_function, 1.9992*n-0.3271)
            #bn = newton(solving_gamma_function, 1.9992*n-0.3271)
            #bn = brentq(solving_gamma_function, 0.0, 100.0)
            #-- just use gammaincinv
            bn = gammaincinv(2*n, 0.5)
            if type(bn) is np.ndarray: bn = bn[0]
            print('solved gamma function with n = %.1f, bn = %s, gammainc(2*n,bn) = %s'%(n, bn, gammainc(2*n,bn)))
            #img = np.exp(-bn * (expimg - 1.0)) # see http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html Eq.1.
            #fRe = xhalf * yhalf * 2.0 * np.pi * n * np.exp(bn)/(bn**(2*n)) * gammainc(2*n,bn) * gamma(2*n) # see http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html Eq.2. # Note that scipy.gammainc is normalized to gammainc(2*n,+inf) = 1.0, which should be gamma(2*n).
            img = np.exp(-bn * expimg) # note that here we do not do "-bn * (expimg - 1.0)" in the exp(), so that the peak is 1.0 rather than that the half-light-radius flux is 1.0.
            fRe = xhalf * yhalf * 2.0 * np.pi * n * 1.0/(bn**(2*n)) * gammainc(2*n,bn) * gamma(2*n) # see http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html Eq.2. # Note that since we do not do "expimg - 1.0" in the above line, here we do not have the "np.exp(bn)" item in the integral. 
            print('flux within R_e: %s, image total: %s / %s, image peak: %s'%(fRe, np.sum(img), 2.0*fRe, np.max(img)))
            img = img / (2.0*fRe) * flux
            #print(x[0,0], y[0,0], x0, y0, expimg[0,0], img[0,0])
        # 
        #if n == 0.5:
        #    #img = img / (2.0*np.pi*xsig*ysig) * flux
        #    img = img / np.sum(img) * flux #<TODO># What is the area of a Sersic area?
        #else:
        #    img = img / np.sum(img) * flux #<TODO># What is the area of a Sersic area?
        
    else:
        # here we use n < 0 for a solid ellipse model, i.e., mask all pixels within the ellipse
        mask = (((x-x0)/xhalf)**2 + ((y-y0)/yhalf)**2 <= 1.0)
        img = 0.0*x*y
        img[mask] = 1.0
        img = img / np.sum(img) * flux #<TODO># What is the area of a Sersic area?
        
    # 
    #print('image.shape', img.shape)
    return img



# 
# Simulate model image
# 
def simulate_Models(model_list, locals_dict):
    # 
    qa = locals_dict['qa']
    # 
    # load variables
    #simfreq = ''
    #if simfreq == '':
    #    if 'simfreq' in locals_dict:
    #        simfreq = str(locals_dict['simfreq'])
    #if simfreq == '':
    #    raise ValueError('Please set "simfreq" like "339.0GHz"!')
    #    return
    #if re.match(r'^[0-9eE.+-]+$', simra):
    #    raise ValueError('Please set "simfreq" with a unit like "339.0GHz"!')
    #    return
    #print('simfreq = %s'%(simfreq))
    # 
    simra = ''
    if simra == '':
        if 'simra' in locals_dict:
            simra = str(locals_dict['simra'])
    if simra == '':
        raise ValueError('Please set "simra" as a float number in units of degree or as a string like "10:00:00"!')
        check_OK = False
    if re.match(r'^[0-9eE.+-]+$', simra):
        # if the input has no unit, assuming it is deg
        simra = float(simra)
    else:
        simra = Angle(simra, unit=u.hour).deg
    print('simra = %s'%(simra))
    # 
    simdec = ''
    if simdec == '':
        if 'simdec' in locals_dict:
            simdec = str(locals_dict['simdec'])
    if simdec == '':
        raise ValueError('Please set "simdec" as a float number in units of degree or as a string like "+02:20:00"!')
        check_OK = False
    if re.match(r'^[0-9eE.+-]+$', simdec):
        # if the input has no unit, assuming it is deg
        simdec = float(simdec)
    else:
        simdec = Angle(simdec, unit=u.deg).deg
    print('simdec = %s'%(simdec))
    # 
    simcell = '' # pixel scale, first try to read from "simcell", if invalid then "beam"
    if simcell == '':
        if 'simcell' in locals_dict:
            simcell = str(locals_dict['simcell'])
    if simcell == '':
        if 'beam' in locals_dict:
            if locals_dict['beam'] != '':
                simcell = '%sarcsec'%(qa.convert(locals_dict['beam'],'arcsec')['value'] / 5.0) # assuming beam/cell = 5.0
    if simcell == '':
        raise ValueError('Please set simcell like "0.02arcsec" or set beam like "0.1arcsec"!')
        return
    if re.match(r'^[0-9eE.+-]+$', simcell):
        raise ValueError('Please set "simcell" as a string with a unit like "0.02arcsec"!')
        return
    print('simcell = %s'%(simcell))
    # 
    if not ('simsize' in locals_dict):
        simsize = 501
    else:
        simsize = locals_dict['simsize']
    print('simsize = %s'%(simsize))
    # 
    skymodel = ''
    if 'skymodel' in locals_dict:
        skymodel = locals_dict['skymodel']
    else:
        skymodel = "casasim_Model.fits"
    if skymodel == '': 
        raise ValueError('Please set "skymodel" as a string, which is the output skymodel fits file!')
        return
    print('skymodel = %s'%(skymodel))
    # 
    # prepare image
    if np.isscalar(simsize):
        t_imsize = [simsize, simsize]
    elif len(simsize) == 1:
        t_imsize = [simsize[0], simsize[0]]
    else:
        t_imsize = [simsize[0], simsize[1]]
    t_imcell = qa.convert(simcell, 'deg')['value'] # degree
    t_image = np.full(t_imsize[::-1], 0.0) # t_imsize is X, Y, but t_image array is in Python array format, shape=(NY,NX,)
    t_wcs = wcs.WCS(naxis=2)
    t_wcs.wcs.crpix = [(t_imsize[0]+1.0)/2.0, (t_imsize[1]+1.0)/2.0]
    t_wcs.wcs.cdelt = np.array([-t_imcell, t_imcell])
    t_wcs.wcs.crval = [simra, simdec]
    t_wcs.wcs.ctype = ["RA---SIN", "DEC--SIN"]
    #t_wcs.wcs.set_pv([(2, 1, 45.0)])
    # 
    # loop input models
    if not (type(model_list) is list):
        model_list = [model_list]
    for i,model in enumerate(model_list):
        if not (type(model) is dict):
            raise ValueError('Error! The %d-th model of the input model list is not a dict!'%(i))
            return
        if not ('ra' in model and 'dec' in model and 'shape' in model and 'flux' in model):
            raise ValueError('Error! The %d-th model of the input model list does not have \'ra\', \'dec\', \'shape\' or \'flux\'!'%(i))
            return
        # 
        # parse size
        if not ('size' in model):
            if ('majoraxis' in model and 'minoraxis' in model and 'positionangle' in model):
                model['size'] = [model['majoraxis'], model['minoraxis'], model['positionangle']]
            else:
                raise ValueError('Error! The %d-th model of the input model list does not have the size parameters!'%(i))
                return
        # 
        # make sure size is a three-element array, and parse the unit
        if not (type(model['size']) is list):
            model['size'] = [model['size'], model['size'], 0.0]
        if len(model['size']) == 1:
            model['size'] = [model['size'][0], model['size'][0], 0.0]
        if len(model['size']) == 2:
            model['size'] = [model['size'][0], model['size'][1], 0.0]
        for isize in range(3):
            if type(model['size'][isize]) is str:
                if re.match(r'^.*deg$', model['size'][isize], re.IGNORECASE) or \
                   re.match(r'^.*arcmin$', model['size'][isize], re.IGNORECASE) or \
                   re.match(r'^.*arcsec$', model['size'][isize], re.IGNORECASE):
                    if isize == 0 or isize == 1:
                        model['size'][isize] = qa.convert(model['size'][isize], 'arcsec')['value']
                    else:
                        model['size'][isize] = qa.convert(model['size'][isize], 'deg')['value']
                else:
                    try:
                        model['size'][isize] = float(model['size'][isize])
                    except:
                        raise ValueError('Error! The %d-th model of the input model list does not have correct size parameters (maj, min, posangle: %s)!'%(i, model['size']))
                        return
        # 
        # parse other parameters
        t_maj = model['size'][0] / (proj_plane_pixel_scales(t_wcs)[0]*3600.0) # convert arcsec to pixel, note that size is half-light diameter or FWHM, not radius.
        t_min = model['size'][1] / (proj_plane_pixel_scales(t_wcs)[1]*3600.0) # convert arcsec to pixel, note that size is half-light diameter or FWHM, not radius.
        t_PA = model['size'][2] # deg
        if t_maj <= 0.0 or t_min <= 0.0:
            print('Warning! Size is non-positive! Skip and continue!')
            continue
        if type(model['ra']) is str:
            t_ra = Angle(model['ra'], unit=u.hour).deg
        else:
            t_ra = model['ra'] # deg
        if type(model['dec']) is str:
            t_dec = Angle(model['dec'], unit=u.deg).deg
        else:
            t_dec = model['dec'] # deg
        #print('[t_ra, t_dec]', [t_ra, t_dec])
        t_cen = t_wcs.wcs_world2pix([[t_ra, t_dec]], 1) # 1-based xy position
        t_cen = t_cen[0]
        #print(t_cen, t_cen.shape)
        t_flux = model['flux'] #<NOTE># Jy
        # 
        # parse Sersic index
        if re.match(r'^Gaussian$', model['shape'], re.IGNORECASE):
            # Gaussian source model
            t_Sersic_index = 0.5 # 0.5 is Gaussian
            t_image += make_2D_Sersic(t_imsize, t_cen, t_flux, [t_maj, t_min, t_PA], t_Sersic_index)
            
        elif re.match(r'^Sersic$', model['shape'], re.IGNORECASE):
            # Sersic source model
            if 'sersic_index' in model:
                t_Sersic_index = model['sersic_index']
            elif 'Sersic_index' in model:
                t_Sersic_index = model['Sersic_index']
            elif 'n' in model:
                t_Sersic_index = model['n']
            else:
                raise ValueError('Error! The %d-th model of the input model list does not have the Sersic_index parameter!'%(i))
                return
            t_image += make_2D_Sersic(t_imsize, t_cen, t_flux, [t_maj, t_min, t_PA], t_Sersic_index)
            
        elif re.match(r'^Disk$', model['shape'], re.IGNORECASE):
            # solid ellipse disk source model
            t_image += make_2D_Sersic(t_imsize, t_cen, t_flux, [t_maj, t_min, t_PA], -1)
            
        elif re.match(r'^Point$', model['shape'], re.IGNORECASE):
            # point source model
            t_image += make_2D_Sersic(t_imsize, t_cen, t_flux, [1.0, 1.0, 0.0], -1)
            
        else:
            raise ValueError('Error! The %d-th model of the input model list does not have a valid shape! The shape "%s" is not one of Gaussian, Sersic, Disk or Point.'%(i, model['shape']))
            return
        
    # 
    # save image as a fits file
    t_header = t_wcs.to_header()
    hdu = fits.PrimaryHDU(data = t_image, header = t_header)
    if os.path.isfile(skymodel):
        print('Warning! Found existing skymodel "%s", backing-up as "%s"'%(skymodel, skymodel+'.backup'))
        shutil.move(skymodel, skymodel+'.backup')
    hdu.writeto(skymodel)
    print('Output skymodel to "%s"!'%(skymodel))



# 
# Simulate model image
# 
def simulate_Models_3D(model_list, locals_dict):
    # 
    # model_list must contain 'chan'
    if type(model_list) is not list:
        raise ValueError('Error! The input model list should be a list! It is %s.'%(type(model_list)))
        return
    # 
    for model in model_list:
        if not ('chan' in model):
            raise ValueError('Error! The %d-th model of the input model list does not contain the "chan" parameter!'%(i))
            return
    # 
    
            
        






# 
# Generate example Gaussian models
# 
def generate_example_Gaussian_models(locals_dict):
    # 
    locals_dict['simra'] = '10:00:00'
    locals_dict['simdec'] = '02:00:00'
    locals_dict['simsize'] = [1001, 1001]
    locals_dict['simcell'] = '0.008arcsec'
    # 
    # 
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.2arcsec', '0.1arcsec', '45deg'], 
                   'shape': 'Gaussian', 
                  }]
    # 
    locals_dict['skymodel'] = 'casasim_Model_Example_Gaussian_noncircular.fits'
    simulate_Models(model_list, locals_dict)
    # 
    # 
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.15arcsec', '0.15arcsec', '45deg'], 
                   'shape': 'Gaussian', 
                  }]
    # 
    locals_dict['skymodel'] = 'casasim_Model_Example_Gaussian_circular.fits'
    simulate_Models(model_list, locals_dict)
    # 
    return


# 
# Generate example Sersic models
# 
def generate_example_Sersic_models(locals_dict):
    # 
    locals_dict['simra'] = '10:00:00'
    locals_dict['simdec'] = '02:00:00'
    locals_dict['simsize'] = [1001, 1001]
    locals_dict['simcell'] = '0.008arcsec'
    # 
    # 
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.2arcsec', '0.12arcsec', '45deg'], 
                   'shape': 'sersic', 
                   'n': 1.0, 
                  }]
    # 
    locals_dict['skymodel'] = 'casasim_Model_Example_Sersic_n_EQ_1_noncircular.fits'
    simulate_Models(model_list, locals_dict)
    # 
    # 
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.15arcsec', '0.15arcsec', '45deg'], 
                   'shape': 'sersic', 
                   'n': 1.0, 
                  }]
    # 
    locals_dict['skymodel'] = 'casasim_Model_Example_Sersic_n_EQ_1_circular.fits'
    simulate_Models(model_list, locals_dict)
    # 
    # 
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.15arcsec', '0.15arcsec', '45deg'], 
                   'shape': 'sersic', 
                   'n': 2.0, 
                  }]
    # 
    locals_dict['skymodel'] = 'casasim_Model_Example_Sersic_n_EQ_2_circular.fits'
    simulate_Models(model_list, locals_dict)
    # 
    # 
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.15arcsec', '0.15arcsec', '45deg'], 
                   'shape': 'sersic', 
                   'n': 4.0, 
                  }]
    # 
    locals_dict['skymodel'] = 'casasim_Model_Example_Sersic_n_EQ_4_circular.fits'
    simulate_Models(model_list, locals_dict)
    # 
    return


# 
# Generate example Disk models
# 
def generate_example_Disk_models(locals_dict):
    # 
    locals_dict['simra'] = '10:00:00'
    locals_dict['simdec'] = '02:00:00'
    locals_dict['simsize'] = [201, 301]
    model_list = [{'ra': '10:00:00', 
                   'dec': '02:00:00', 
                   'flux': 5.0e-3, 
                   'size': ['0.2arcsec', '0.12arcsec', '45deg'], 
                   'shape': 'disk', 
                  }]
    # 
    simulate_Models(model_list, locals_dict)
    # 
    return





# 
# Simulate a Gaussian shape source
# 
def simulate_Gaussian_Obsolete_20190816(locals_dict):
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
    check_OK = True
    # 
    if not ('project' in locals_dict):
        project = "casasim_Project"
    else:
        project = locals_dict['project']
    print('project = %s'%(project))
    # 
    skymodel = ''
    if skymodel == '':
        if 'skymodel' in locals_dict:
            skymodel = locals_dict['skymodel']
    if skymodel == '':
        raise ValueError('Please set skymodel to a skymodel fits image file!')
        check_OK = False
    print('skymodel = %s'%(skymodel))
    # 
    skyfreq = ''
    if skyfreq == '':
        if 'skyfreq' in locals_dict:
            skyfreq = str(locals_dict['skyfreq'])
            incenter = skyfreq
    if skyfreq == '':
        if 'incenter' in locals_dict:
            skyfreq = str(locals_dict['incenter'])
            incenter = skyfreq
    if skyfreq == '':
        raise ValueError('Please set skyfreq or incenter like "339.0GHz"!')
        check_OK = False
    if re.match(r'^[0-9eE.+-]+$', skyfreq):
        raise ValueError('Please set skyfreq or incenter with a unit like "339.0GHz"!')
        check_OK = False
    print('skyfreq = %s'%(skyfreq))
    # 
    simra = ''
    if simra == '':
        if 'simra' in locals_dict:
            simra = str(locals_dict['simra'])
    if simra == '':
        raise ValueError('Please set "simra" (simulated image center RA) with a float number or hour format string!')
        check_OK = False
    if re.match(r'^[0-9eE.+-]+$', simra):
        # if the input has no unit, assuming it is deg
        simra = float(simra)
    else:
        simra = Angle(simra, unit=u.hour).deg
    print('simra = %s'%(simra))
    # 
    simdec = ''
    if simdec == '':
        if 'simdec' in locals_dict:
            simdec = str(locals_dict['simdec'])
    if simdec == '':
        raise ValueError('Please set "simdec" (simulated image center Dec) with a float number or degree format string!')
        check_OK = False
    if re.match(r'^[0-9eE.+-]+$', simdec):
        # if the input has no unit, assuming it is deg
        simdec = float(simdec)
    else:
        simdec = Angle(simdec, unit=u.deg).deg
    print('simdec = %s'%(simdec))
    # 
    #if not ('complist' in locals_dict):
    #    complist = ''
    #else:
    #    complist = locals_dict['complist']
    complist = ''
    # 
    #if not ('compwidth' in locals_dict):
    #    compwidth = ''
    #else:
    #    compwidth = locals_dict['compwidth']
    compwidth = ''
    # 
    inwidth = '' # bandwidth
    if inwidth == '':
        if ('inwidth' in locals_dict):
            if locals_dict['inwidth'] != '':
                print('Warning! The input "inwidth" is empty!')
                inwidth = locals_dict['inwidth']
    if inwidth == '':
        print('Warning! No valid inwidth input! Setting it as "7.5GHz"!')
        inwidth = '7.5GHz'
    print('inwidth = %s'%(inwidth))
    # 
    antennalist = '' # beam size
    if antennalist == '':
        if 'beam' in locals_dict:
            if locals_dict['beam'] != '':
                antennalist = 'alma;%s'%(locals_dict['beam'])
    if antennalist == '':
        if 'antennalist' in locals_dict:
            if locals_dict['antennalist'] != '':
                antennalist = locals_dict['antennalist']
    if antennalist == '':
        print('Please set beam like "0.1arcsec" antennalist like "alma;0.1arcsec"!')
        check_OK = False
    print('antennalist = %s'%(antennalist))
    # 
    if not ('totaltime' in locals_dict):
        totaltime = ''
        print('Please set totaltime like "15min"!')
        check_OK = False
    else:
        totaltime = locals_dict['totaltime']
    print('totaltime = %s'%(totaltime))
    # 
    if not ('integration' in locals_dict):
        integration = '10s' # time interval for each integration, e.g., '10s'
    else:
        integration = locals_dict['integration']
    print('integration = %s'%(integration))
    # 
    if not ('thermalnoise' in locals_dict):
        thermalnoise = '' # 'tsys-atm' (user_pwv=XXX)
    else:
        thermalnoise = locals_dict['thermalnoise']
    print('thermalnoise = %s'%(thermalnoise))
    # 
    if not ('user_pwv' in locals_dict):
        user_pwv = 0.5 # 'tsys-atm' (user_pwv=XXX)
    else:
        user_pwv = locals_dict['user_pwv']
    print('user_pwv = %s'%(user_pwv))
    # 
    if not ('obsmode' in locals_dict):
        obsmode = 'int' # 'int' or 'sd'
    else:
        obsmode = locals_dict['obsmode']
    print('obsmode = %s'%(obsmode))
    # 
    #if not ('direction' in locals_dict):
    #    direction = '' # "J2000 10h00m00.0s -30d00m00.0s" # If left unset, simobserve will use the center of the skymodel image. -- not working?
    #else:
    #    direction = locals_dict['direction']
    # 
    direction = "J2000 %s %s"%(Angle(simra, unit=u.deg).to_string(u.hour), 
                               Angle(simdec, unit=u.deg).to_string(u.deg, alwayssign=True))
    print('direction = %s'%(direction))
    # 
    mapsize = ''
    if 'mapsize' in locals_dict:
        if type(locals_dict['mapsize']) is str:
            mapsize = locals_dict['mapsize']
        elif len(locals_dict['mapsize']) > 0:
            if locals_dict['mapsize'][0] == '':
                mapsize = ''
    if mapsize == '':
        mapsize = '2arcsec'
        #print('Please set mapsize like "2arcsec"! The small value prevents mosaicing.')
        #check_OK = False
    print('mapsize = %s'%(mapsize))
    # 
    if check_OK == False:
        raise ValueError('Error occured! Please see the above information.')
        return
    # 
    # print message
    print('project = %s'%(project))
    print('skymodel = %s'%(skymodel))
    #print('complist = %s'%(complist))
    #print('direction = %s'%(direction))
    # 
    # set outname and output_ms
    if antennalist.endswith('.cfg'):
        outname = antennalist.replace('.cfg','').replace('alma.','alma_')
    else:
        outname = antennalist.replace(';','_').replace('alma.','alma_')
    output_ms = os.path.join(project, os.path.basename(project)+'.'+outname+'.ms')
    output_uvfits = re.sub(r'\.ms$', r'.uvfits', output_ms, re.IGNORECASE)
    output_noisy_ms = os.path.join(project, os.path.basename(project)+'.'+outname+'.noisy.ms')
    output_noisy_uvfits = re.sub(r'\.ms$', r'.uvfits', output_noisy_ms, re.IGNORECASE)
    # 
    # backup previous result if any
    for file_name in [output_ms, output_uvfits, output_noisy_ms, output_noisy_uvfits]:
        if os.path.isdir(file_name):
            if os.path.isdir(file_name+'.backup'):
                shutil.rmtree(file_name+'.backup')
            shutil.move(file_name, file_name+'.backup')
        if os.path.isfile(file_name):
            if os.path.isfile(file_name+'.backup'):
                os.remove(file_name+'.backup')
            shutil.move(file_name, file_name+'.backup')
    # 
    # run simobserve task
    print('Running simobserve(project=\'%s\', ...)'%(project))
    project_in = project
    simobserve(project = project, 
               skymodel = skymodel, 
               complist = complist, 
               incenter = incenter, 
               direction = direction, 
               mapsize = mapsize, 
               ptgfile = '', 
               compwidth = compwidth, 
               inwidth = inwidth, 
               obsmode = obsmode, 
               antennalist = antennalist, 
               totaltime = totaltime, 
               integration = integration, 
               thermalnoise = thermalnoise, 
               user_pwv = user_pwv, 
               verbose = True, 
               overwrite = True, 
              )
    project = project_in # it seems 'project' variable got changed after simobserve ...
    # 
    # check output
    if os.path.isdir(output_ms):
        print('Output to "%s"!'%(output_ms))
        # 
        # exportuvfits
        exportuvfits(vis = output_ms, 
                     fitsfile = output_uvfits, 
                     multisource = False, 
                     combinespw = False, 
                     overwrite = True, 
                     ) #<TODO># multisource, combinespw
        if not (os.path.isfile(output_uvfits)):
            raise Exception('Error! Failed to run exportuvfits()! Could not find "%s"!'%(output_uvfits))
            return
        print('Output to "%s"!'%(output_uvfits))
    else:
        raise Exception('Error! Failed to run simobserve()! Could not find "%s"!'%(output_ms))
        return
    # 
    # check noisy data output as well
    if os.path.isdir(output_noisy_ms):
        print('Output to "%s"!'%(output_noisy_ms))
        # 
        # exportuvfits
        exportuvfits(vis = output_noisy_ms, 
                     fitsfile = output_noisy_uvfits, 
                     multisource = False, 
                     combinespw = False, 
                     overwrite = True, 
                     ) #<TODO># multisource, combinespw
        if not (os.path.isfile(output_noisy_uvfits)):
            raise Exception('Error! Failed to run exportuvfits()! Could not find "%s"!'%(output_noisy_uvfits))
            return
        print('Output to "%s"!'%(output_noisy_uvfits))
    # 
    # backup previous result if any
    #if os.path.isdir(os.path.join(project, 'split_field_0_spw_0.ms')):
    #    if os.path.isdir(os.path.join(project, 'split_field_0_spw_0.ms'+'.backup')):
    #        shutil.rmtree(os.path.join(project, 'split_field_0_spw_0.ms'+'.backup'))
    #    shutil.move(os.path.join(project, 'split_field_0_spw_0.ms'), 
    #                os.path.join(project, 'split_field_0_spw_0.ms'+'.backup'))
    # 
    # split
    #split(vis = output_ms, 
    #      outputvis = os.path.join(project, 'split_field_0_spw_0.ms'), 
    #      keepmms = False, 
    #      keepflags = False, 
    #      field = '0', 
    #      spw = '0', 
    #      timebin = '30s', 
    #      )
    #if not (os.path.isdir(os.path.join(project, 'split_field_0_spw_0.ms'))):
    #    raise Exception('Error! Failed to run split()! Could not find "%s"!'%(os.path.join(project, 'split_field_0_spw_0.ms')))
    #print('Output to "%s"!'%(os.path.join(project, 'split_field_0_spw_0.ms')))
    ## 
    ## exportuvfits
    #exportuvfits(vis = os.path.join(project, 'split_field_0_spw_0.ms'), 
    #             fitsfile = os.path.join(project, 'split_field_0_spw_0.uvfits'), 
    #             multisource = False, 
    #             combinespw = False, 
    #             overwrite = True, 
    #             )
    #if not (os.path.isfile(os.path.join(project, 'split_field_0_spw_0.uvfits'))):
    #    raise Exception('Error! Failed to run exportuvfits()! Could not find "%s"!'%(os.path.join(project, 'split_field_0_spw_0.uvfits')))
    #print('Output to "%s"!'%(os.path.join(project, 'split_field_0_spw_0.uvfits')))









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
#    if not (os.path.isdir(os.path.join(project, os.path.basename(project)+'.'+outname+'.ms'))):
#        raise Exception('Error! Could not find "%s"! Please run simobserve() first!'%(os.path.join(project, os.path.basename(project)+'.'+outname+'.ms')))
#    # 
#    print('Reading "%s"'%(os.path.join(project, os.path.basename(project)+'.'+outname+'.ms')))
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








