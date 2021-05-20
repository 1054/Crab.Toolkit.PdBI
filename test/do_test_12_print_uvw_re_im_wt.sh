#!/bin/bash
# 

set -e


echo ""
echo "This is a test script for running \"pdbi-uvt-raw-uvtable-print-u-v-w\"."
echo ""


if [[ ! -d test_12_print_uvw_re_im_wt ]]; then mkdir test_12_print_uvw_re_im_wt; fi


cd test_12_print_uvw_re_im_wt


source ../../SETUP.bash


cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt


pdbi-uvt-raw-uvtable-print-u-v-w-re-im-wt -name NAME.uvt -out OUTPUT.txt


pdbi-uvt-raw-uvtable-print-u-v-w-re-im-wt.py -name NAME.uvt -out OUTPUT2.txt


echo "Done!"


