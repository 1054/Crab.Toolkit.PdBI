#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_merge by calling \"pdbi-uvt-go-merge\"."
echo ""


mkdir test_2_uvmerge 2>/dev/null


cd test_2_uvmerge


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME_1.uvt

cp ../uv_table_data/split_z35_68_spw1_width128.uvt NAME_2.uvt


pdbi-uvt-go-merge -name NAME_1.uvt NAME_2.uvt -out OUTPUTNAME -weight 5 10



echo "Done!"


