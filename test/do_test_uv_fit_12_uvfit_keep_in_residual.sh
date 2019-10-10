#!/bin/bash
# 

echo ""
echo "This is a test script for running GILDAS uv_fit by calling \"pdbi-uvt-go-uvfit\"."
echo ""


mkdir test_uv_fit_12_uvfit_keep_in_residual


set -e


cd test_uv_fit_12_uvfit_keep_in_residual


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt


# go uvfit
pdbi-uvt-go-uvfit-v10 -name NAME.uvt \
                  -offset 0 0 -varypos -keep-in-residual \
                  -offset -1.2 0.3 -varypos \
                  -out FIT_result_1 -residual FIT_result_1_residual # subtract 2 only

pdbi-uvt-go-uvfit-v10 -name NAME.uvt \
                  -offset 0 0 -varypos \
                  -offset -1.2 0.3 -varypos -subtract \
                  -out FIT_result_2 -residual FIT_result_2_residual # subtract 1 and 2

pdbi-uvt-go-uvfit-v10 -name NAME.uvt \
                  -offset 0 0 -varypos -subtract \
                  -offset -1.2 0.3 -varypos -keep-in-residual \
                  -out FIT_result_3 -residual FIT_result_3_residual # subtract 1 only


# go uvmap the input and residual images
pdbi-uvt-go-uvmap -name NAME.uvt -out uvmap_input -FoV 5 -do-header

pdbi-uvt-go-uvmap -name FIT_result_1_residual.uvt -out uvmap_result_1_residual -FoV 5 -do-header

pdbi-uvt-go-uvmap -name FIT_result_2_residual.uvt -out uvmap_result_2_residual -FoV 5 -do-header

pdbi-uvt-go-uvmap -name FIT_result_3_residual.uvt -out uvmap_result_3_residual -FoV 5 -do-header


# open the images
#if [[ $(uname) == "Darwin" ]]; then
#echo "--------------------------------- fitted data table ---------------------------------"
#cat OUTPUTNAME.result.obj_1.txt
#echo ""
#open OUTPUTNAME.result.obj_1.image.pdf OUTPUTNAME.result.obj_1.spectrum.pdf # output_residual.eps
#fi


echo "Done!"


# clean up
#bash -c 'rm output_* *.lmv* *.eps *.txt *.log *.noi *.beam *.map *.script *.backup *"~" 2>/dev/null'


