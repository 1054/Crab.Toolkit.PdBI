#!/usr/bin/env fish
# 


set BIN_SETUP_SCRIPT (dirname (status --current-filename))/bin/bin_setup.bash

#echo 
#echo "PATH = $PATH"
#echo 

set -x PATH (string split ":" (bash -c "source $BIN_SETUP_SCRIPT -debug -check pdbi-uvt-go-average pdbi-uvt-go-uvfit -print" | tail -n 1))

type casa-ms-split
type casa-ms-concat
type pdbi-uvt-go-splitpolar
type pdbi-uvt-go-import-uvfits
type pdbi-uvt-go-average
type pdbi-uvt-go-uvfit

#echo 
#echo "PATH = $PATH"
#echo 


