#!/usr/bin/env python
# 

import os, sys, re
import numpy as np
import astropy
from astropy.modeling import models, fitting
import scipy
from scipy.fftpack import fft2, ifft2, fftshift
import matplotlib as mpl
import matplotlib.pyplot as plt

# 
# Setup image dimension
nx = 30 # 300
ny = 35 # 350
vmin = None # 0.0
vmax = None # 1.0

# 
# Generate coordinate mesh
mesh_y, mesh_x = np.meshgrid(range(ny), range(nx), indexing='ij') # 0-based


# 
# Generate model source 1
obj1_model = models.Gaussian2D(amplitude=1.0, x_mean=nx*0.3, y_mean=ny*0.1, x_stddev=3.0/(2.0*np.sqrt(2.0*np.log(2.0))), y_stddev=3.0/(2.0*np.sqrt(2.0*np.log(2.0))))
obj1_image = obj1_model(mesh_x, mesh_y)
#obj1_image = obj1_image * 0.0
#obj1_image[3,10] = 1.0


# 
# Generate model source 2
obj2_model = models.Gaussian2D(amplitude=1.0, x_mean=nx*0.3, y_mean=ny*0.9, x_stddev=3.0/(2.0*np.sqrt(2.0*np.log(2.0))), y_stddev=3.0/(2.0*np.sqrt(2.0*np.log(2.0))))
obj2_image = obj2_model(mesh_x, mesh_y)
#obj2_image = obj2_image * 0.0
#obj2_image[20,10] = 1.0


# 
# Add up image
objs_image = obj1_image + obj2_image


# 
# do convolution
#scipy.signal.convolve2d(in1, in2)
objs_visib = fftshift(fft2(objs_image)) # fftshift shifts the zero frequency to the center
print(objs_visib.shape)

#vis = objs_visib[30,100]
#print(vis.real, vis.imag, np.sqrt(vis.real**2+vis.imag**2), np.absolute(vis), np.angle(vis) )


# 
# Show the image
fig = plt.figure(figsize=(13.0,4.0))
ax_image = fig.add_subplot(1,3,1)
ax_imshow = ax_image.imshow(objs_image, origin='lower', vmin=vmin, vmax=vmax)
plt.colorbar(ax_imshow)
ax_image.set_title('Image')

ax_visabs = fig.add_subplot(1,3,2)
ax_imshow = ax_visabs.imshow(np.absolute(objs_visib), origin='lower', vmin=vmin, vmax=vmax)
plt.colorbar(ax_imshow)
ax_visabs.set_title('Interferogram Amplitude')


ax_visangle = fig.add_subplot(1,3,3)
ax_imshow = ax_visangle.imshow(np.angle(objs_visib), origin='lower')
plt.colorbar(ax_imshow)
ax_visangle.set_title('Interferogram Phase')

fig.tight_layout()
fig.savefig('Plot_demo_conv_1.pdf')
plt.show(block=True)

#

