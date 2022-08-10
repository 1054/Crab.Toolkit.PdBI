#!/bin/bash
# 


echo ""
echo "This is a test script for running GILDAS uv_map by calling \"pdbi-uvt-go-uvmap\"."
echo ""


mkdir test_5_uvmap 2>/dev/null


cd test_5_uvmap


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt


pdbi-uvt-go-uvmap -name NAME.uvt \
                    -offset 0 0 \
                    -size 15 -map_size 512 \
                    -out OUTPUTNAME


echo "Done!"


