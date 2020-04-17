#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_fit by calling \"pdbi-uvt-go-uvfit\"."
echo "Requiring GILDAS around and later than nov19."
echo ""


mkdir test_uv_fit_13_fixpos_espergel


cd test_uv_fit_13_fixpos_espergel


source ../../SETUP.bash


cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt


# go uvfit
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -radec 150.0351 2.01330 -fixpos -espergel \
                  -out OUTPUTNAME


# go uvmap the input image
#pdbi-uvt-go-uvmap -name NAME.uvt -uvrange 10 200 -do-header


# go uvmap the residual image
#pdbi-uvt-go-uvmap -name OUTPUT_RESIDUAL.uvt -uvrange 10 200 -do-header


# open the images
if [[ $(uname) == "Darwin" ]]; then
echo "--------------------------------- fitted data table ---------------------------------"
cat OUTPUTNAME.result.obj_1.txt
echo ""
open OUTPUTNAME.result.obj_1.image.pdf OUTPUTNAME.result.obj_1.spectrum.pdf # output_residual.eps
fi


echo "Done!"


# clean up
#bash -c 'rm output_* *.lmv* *.eps *.txt *.log *.noi *.beam *.map *.script *.backup *"~" 2>/dev/null'


