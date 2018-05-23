#!/bin/bash
# 


echo ""
echo "This is a test script for \"extrema\"."
echo ""


mkdir test_6_extrema 2>/dev/null


cd test_6_extrema


source ../../SETUP.bash


cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt


# Run these directly in command line
# First image the uvt to make lmv maps
pdbi-uvt-go-uvmap -name NAME.uvt > NAME.uvmap.log
# Then compute EXTREMA and write log file
echo "HEADER NAME.lmv /EXTREMA" | mapping -nw -nl
echo "HEADER NAME.lmv" | mapping -nw -nl > NAME.extrema.log
echo ""; seq -s "-" 120 | tr -d '[:digit:]'; echo ""
# Read MAX_NOISE
grep "MAX_NOISE" NAME.uvmap.log | tee tmp_max_noise.txt
# Read EXTREMA
grep -A3 "Reference Pixel" NAME.extrema.log | tee tmp_conv_coord.txt # used for converting pixel coordinates to sky coordinates
grep "^Minimum" NAME.extrema.log | tee tmp_min.txt
grep "^Maximum" NAME.extrema.log | tee tmp_max.txt


echo "Done!"


