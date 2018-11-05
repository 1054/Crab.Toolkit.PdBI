#!/bin/bash
# 

set -e


echo ""
echo "This is a test script for running GILDAS uv_mult by calling \"pdbi-uvt-go-mult\"."
echo ""


mkdir test_10_uvmult 2>/dev/null


cd test_10_uvmult


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME_1.uvt


pdbi-uvt-go-mult -name NAME_1.uvt -factor 2.0 # -out NEW_1.uvt


# check whether fluxes are scaled up by a factor of 2
pdbi-uvt-go-uvfit -name NAME_1.uvt -offset 0 0
pdbi-uvt-go-uvfit -name NAME_1-Multiplied.uvt -offset 0 0
cat NAME_1_go_uvfit.result.obj_1.txt
cat NAME_1-Multiplied_go_uvfit.result.obj_1.txt



echo "Done!"


