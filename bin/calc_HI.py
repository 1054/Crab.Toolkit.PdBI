#!/usr/bin/env python
#
import os, sys
import numpy as np
import astropy.units as u
import astropy.constants as const
from astropy.cosmology import FlatLambdaCDM
from astropy.cosmology import WMAP9 as cosmo
lumdist = cosmo.luminosity_distance

z = 4.0
line_flux_mJy = 0.04
line_width_kms = 100

z = 1
line_flux_mJy = 0.04 # flux 0.04 mJy or 0.80 mK over 100 km/s for M_HI 1e10 at z=1.
line_width_kms = 100

z = 1
line_flux_mJy = 0.0125 # flux 0.0125 mJy over 100 km/s for M_HI 0.33e10 at z=1. -- 67 hours on+off time
line_width_kms = 100

#z = float(sys.argv[1]) #  4.0
#line_flux_mJy_kms = float(sys.argv[2]) * float(sys.argv[3]) # 0.04 * 100

print('z: %s'%(z))

c = 2.99792458e10
h = 6.6260755e-27
kb = 1.380658e-16
freq_hz = 1420e6/(1.+z)
beam = 2.9*(1.+z)*u.arcmin
print('beam: %s [arcmin]'%(beam))
beam_in_sr = np.pi*(beam.to(u.rad).value/2.0*beam.to(u.rad).value/2.0)/np.log(2)
print('freq: %.5f MHz'%(freq_hz/1e6))
jtok = c**2 / beam_in_sr / 1e23 / (2*kb*freq_hz**2)
print('jtok: %s'%(jtok))

dL = lumdist(z).to(u.Mpc).value
dA = dL / (1.+z)**2
kpc2arcsec = 1e-3/dA/3.1415926*180.0*3600.0
beam_kpc = beam.to(u.arcsec).value / kpc2arcsec
beam_cm = (beam_kpc*u.kpc).to(u.cm).value
beamarea_cm2 = np.pi/(4.*np.log(2.))*beam_cm**2

#jtok = 20. # jtok 0.300 812
line_flux_mJy_kms = line_flux_mJy * line_width_kms
line_flux_K_kms = line_flux_mJy_kms * 1e-3 * jtok
line_flux_mK = line_flux_mJy * jtok
print('flux: %s [mJy]'%(line_flux_mJy))
print('flux: %s [mK]'%(line_flux_mK))
print('flux: %s [mK km s-1]'%(line_flux_K_kms * 1e3))

N_HI = 1.8224e18 * line_flux_K_kms

print('N_HI: %e [atoms cm-2]'%(N_HI))
print('M_HI: %e [M_sun]'%(N_HI * beamarea_cm2 * const.m_p / const.M_sun))


M_HI = 2.356e5 * line_flux_mJy_kms * 1e-3 / (1.+z) * dL**2 / (1.+z)

print('M_HI: %e [M_sun]'%(M_HI))

