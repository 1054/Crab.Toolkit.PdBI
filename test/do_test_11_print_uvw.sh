#!/bin/bash
# 

set -e


echo ""
echo "This is a test script for running \"pdbi-uvt-raw-uvtable-print-u-v-w\"."
echo ""


if [[ ! -d test_11_print_uvw ]]; then mkdir test_11_print_uvw; fi


cd test_11_print_uvw


source ../../SETUP.bash


#cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt

cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME_1.uvt # testing single-channel data, for which we also print re im wt

pdbi-uvt-go-splitpolar -name NAME_1.uvt -out NAME.uvt

rm NAME_1.uvt


echo "Current time "$(date +"%Y-%m-%d %Hh%Mm%Ss %Z")
echo "Running pdbi-uvt-raw-uvtable-print-u-v-w -name NAME.uvt -out OUTPUT.txt -keep-files"
pdbi-uvt-raw-uvtable-print-u-v-w -name NAME.uvt -out OUTPUT.txt -keep-files
echo "Current time "$(date +"%Y-%m-%d %Hh%Mm%Ss %Z")


echo "Current time "$(date +"%Y-%m-%d %Hh%Mm%Ss %Z")
echo "Running pdbi-uvt-raw-uvtable-print-u-v-w.py -name NAME.uvt -out OUTPUT2.txt"
pdbi-uvt-raw-uvtable-print-u-v-w.py -name NAME.uvt -out OUTPUT2.txt
echo "Current time "$(date +"%Y-%m-%d %Hh%Mm%Ss %Z")


echo "Done!"


