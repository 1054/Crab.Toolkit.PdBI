#!/bin/bash
# 

set -e


echo ""
echo "This is a test script for running \"pdbi-uvt-raw-uvtable-print-u-v-w\"."
echo ""


if [[ ! -d test_11_print_uvw ]]; then mkdir test_11_print_uvw; fi


cd test_11_print_uvw


source ../../SETUP.bash


cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt


pdbi-uvt-raw-uvtable-print-u-v-w -name NAME.uvt -out OUTPUT.txt


echo "Done!"

