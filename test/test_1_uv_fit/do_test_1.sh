#!/bin/bash
# 

source ../../SETUP.bash

# go uvfit
pdbi-uvt-go-uvfit -name split_z35_68_spw0_width128.uvt \
                    -offset 0 0 \
                    -uvrange 10 2000 \
                    -subtract -residual output_residual \
                    -out output_uv_fit

# go uvmap the input image
pdbi-uvt-go-uvmap -name split_z35_68_spw0_width128.uvt

# go uvmap the residual image
pdbi-uvt-go-uvmap -name output_residual.uvt

# open the images
if [[ $(uname) == "Darwin" ]]; then
open split_z35_68_spw0_width128.eps output_residual.eps
fi

echo "Done!"

