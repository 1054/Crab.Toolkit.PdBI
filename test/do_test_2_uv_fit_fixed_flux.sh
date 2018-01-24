#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_fit by calling \"pdbi-uvt-go-uvfit\"."
echo ""


mkdir test_2_uv_fit 2>/dev/null
cd test_2_uv_fit
cp ../test_1_uv_fit/split_z35_68_spw0_width128.uvt .

source ../../SETUP.bash

# go uvfit
pdbi-uvt-go-uvfit-v7 -name split_z35_68_spw0_width128.uvt \
                    -uvrange 10 200 \
                    -residual output_residual \
                    -out output_uv_fit \
                    -flux 8.57042E-04 -fix-flux \
                    -fov 30

# go uvmap the input image
pdbi-uvt-go-uvmap -name split_z35_68_spw0_width128.uvt -uvrange 10 200 -do-header

# go uvmap the residual image
pdbi-uvt-go-uvmap -name output_residual.uvt -uvrange 10 200 -do-header

# open the images
if [[ $(uname) == "Darwin" ]]; then
echo "--------------------------------- fitted data table ---------------------------------"
cat output_uv_fit.result.obj_1.txt
echo ""
open output_uv_fit.result.obj_1.image.pdf output_residual.eps
fi

echo "Done!"

# clean up
#bash -c 'rm output_* *.lmv* *.eps *.txt *.log *.noi *.beam *.map *.script *.backup *"~" 2>/dev/null'


