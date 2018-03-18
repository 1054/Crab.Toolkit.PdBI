#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_shift by calling \"pdbi-uvt-go-shift\"."
echo ""


mkdir test_4_uvshift 2>/dev/null


cd test_4_uvshift


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt


pdbi-uvt-go-shift -name NAME.uvt \
                    -offset -30 -30  \
                    -out OUTPUTNAME


echo "Done!"


