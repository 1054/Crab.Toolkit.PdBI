#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_splitpolar by calling \"pdbi-uvt-go-splitpolar\"."
echo ""


mkdir test_1_splitpolar 2>/dev/null


cd test_1_splitpolar


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt


pdbi-uvt-go-splitpolar -name NAME.uvt \
                    -uvrange 10 200 \
                    -residual output_residual \
                    -out OUTPUTNAME \
                    -fov 30


echo "Done!"


