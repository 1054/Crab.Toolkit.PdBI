#!/usr/bin/env fish
# 


set BIN_SETUP_SCRIPT (dirname (status --current-filename))/bin/bin_setup.bash

bash -c "source $BIN_SETUP_SCRIPT pdbi-uvt-go-average pdbi-uvt-go-uvfit"



