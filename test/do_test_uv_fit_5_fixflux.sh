#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_fit by calling \"pdbi-uvt-go-uvfit\"."
echo ""


mkdir test_uv_fit_5_fixflux


cd test_uv_fit_5_fixflux


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt


# go uvfit
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -uvrange 10 200 \
                  -offset 0.5 0.5 -fixpos -size 0.9 0.7 -fixsize -angle 90 -fixangle -egauss -flux 2e-3 -fixflux \
                  -residual OUTPUT_RESIDUAL \
                  -FoV 10 \
                  -out OUTPUTNAME


# go uvmap the input image
#pdbi-uvt-go-uvmap -name NAME.uvt -uvrange 10 200 -do-header


# go uvmap the residual image
pdbi-uvt-go-uvmap -name OUTPUT_RESIDUAL.uvt -uvrange 10 200 -do-header -FoV 10


# open the images
if [[ $(uname) == "Darwin" ]]; then
echo "--------------------------------- fitted data table ---------------------------------"
cat OUTPUTNAME.result.obj_1.txt
echo ""
open OUTPUTNAME.result.obj_1.image.pdf OUTPUT_RESIDUAL.pdf # OUTPUTNAME.result.obj_1.spectrum.pdf # OUTPUT_RESIDUAL.eps
fi


echo "Done!"


# clean up
#bash -c 'rm output_* *.lmv* *.eps *.txt *.log *.noi *.beam *.map *.script *.backup *"~" 2>/dev/null'


