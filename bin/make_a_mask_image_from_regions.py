#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os, sys, re, shutil
import glob
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales, proj_plane_pixel_area
#from astropy.convolution import convolve, Gaussian2DKernel, Box1DKernel
import astropy.units as u
import click


from regions import (Region, RectangleSkyRegion, SkyRegion, CirclePixelRegion, PixelRegion, PixCoord)
try:
    from regions import Regions
    my_ds9_parser = Regions.parse
    read_ds9 = Regions.read
except:
    from regions import DS9Parser, ShapeList, Shape, read_ds9, write_ds9, ds9_objects_to_string
    my_ds9_parser = lambda x: [t.to_region() for t in DS9Parser(x).shapes]
    #DS9Parser deprecated, use Regions.parse(regions_str, format='ds9')


@click.command()
@click.argument('image_file', type=click.Path(exists=True))
@click.argument('region_file', type=click.Path(exists=True))
@click.argument('output_name', type=click.Path(exists=False))
@click.option('--revert', default=False, is_flag=True)
def main(
        image_file, 
        region_file, 
        output_name, 
        revert,
    ):
    # 
    print('Reading image %r'%(image_file))
    image, header = fits.getdata(image_file, header=True)
    imshape = (image.shape)
    wcs = None # WCS(header, naxis=2)
    ny, nx = header['NAXIS2'], header['NAXIS1']
    if len(imshape) >= 3:
        nchan = np.prod(imshape[0:-2])
        if len(imshape) > 3:
            image = image.reshape([nchan, ny, nx])
    
    # 
    print('Reading regions %r'%(region_file))
    region_list = read_ds9(region_file)
    
    # 
    region_mask = np.full((ny,nx), fill_value=False)
    for region_obj in region_list:
        if isinstance(region_obj, SkyRegion):
            if wcs is None:
                wcs = WCS(header, naxis=2)
            pixel_region = region_obj.to_pixel(wcs)
        else:
            pixel_region = region_obj
        region_mask = np.logical_or(region_mask, pixel_region.to_mask().to_image((ny,nx)).astype(bool))
    
    # 
    #mask = np.logical_and.reduce((~np.isnan(image), np.isfinite(image), region_mask))
    if len(imshape) >= 3:
        mask = np.repeat(region_mask[np.newaxis, :, :], nchan)
    else:
        mask = region_mask
    # 
    if revert:
        image[~mask] = 1
        image[mask] = 0
    else:
        image[~mask] = 0
        image[mask] = 1
    if len(imshape) >= 3:
        image = image.astype(np.int32)
    else:
        image = image.reshape(imshape).astype(np.int32)
    header['BITPIX'] = 32
    header['HISTORY'] = 'Created mask with the input region "{}" for the input image "{}".'.format(region_file, image_file)

    hdu = fits.PrimaryHDU(data=image, header=header)

    output_image_file = output_name
    if os.path.isfile(output_image_file):
        print('Found existing output file, backing up as %r'%(output_image_file+'.backup'))
        shutil.move(output_image_file, output_image_file+'.backup')
    if output_image_file.find(os.sep)>=0:
        if not os.path.isdir(os.path.dirname(output_image_file)):
            os.makedirs(os.path.dirname(output_image_file))
    print('Writing image %r'%(output_image_file))
    hdu.writeto(output_image_file)



########
# MAIN #
########

if __name__ == '__main__':
    
    main()



