#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_cont and uv_average by calling \"pdbi-uvt-go-uvcont\" and \"pdbi-uvt-go-average\"."
echo ""


mkdir test_uv_cont_uv_average


cd test_uv_cont_uv_average


source ../../SETUP.bash


cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt


# go uvcont
pdbi-uvt-go-uvcont -name NAME.uvt \
                  -out OUT_UVCONT

# go uvcont2
pdbi-uvt-go-uvcont -name NAME.uvt \
                  -out OUT_UVCONT2 -width 16

# go uvaverage
pdbi-uvt-go-average -name NAME.uvt \
                  -out OUT_UVAVERAGE


echo "Done!"


# clean up
#bash -c 'rm output_* *.lmv* *.eps *.txt *.log *.noi *.beam *.map *.script *.backup *"~" 2>/dev/null'


