#!/usr/bin/env python
# 
# This code must be run in CASA
# 

from __future__ import print_function
import os, sys, re, json, copy, time, datetime, shutil, pprint
import numpy as np
import astropy




if 'casa' in globals() and 'mstransform' in globals() and 'vis' in locals():
    
    vis_before_timebin = locals()['vis']
    vis_after_timebin = re.sub(r'\.ms$', r'_timebin.ms', vis_before_timebin, re.IGNORECASE)
    
    mstransform( vis = vis_before_timebin, outputvis = vis_after_timebin, vis_after_timebin, timeaverage=True, timebin='30s')



