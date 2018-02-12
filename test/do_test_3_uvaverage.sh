#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_average by calling \"pdbi-uvt-go-average\"."
echo ""


mkdir test_3_uvaverage 2>/dev/null


cd test_3_uvaverage


source ../../SETUP.bash


cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt


pdbi-uvt-go-average -name NAME.uvt -out OUTPUTNAME


pdbi-uvt-go-average -name NAME.uvt -crange 2 5 -out OUTPUTNAME_CRANGE_2_5


pdbi-uvt-go-average -name NAME.uvt -vrange -400 400 -out OUTPUTNAME_VRANGE_-400_400



echo "Done!"


