#!/usr/bin/env tcsh
# 


set BIN_SETUP_SCRIPT = `dirname $0`/bin/bin_setup.bash

bash -c "source $BIN_SETUP_SCRIPT pdbi-uvt-go-average pdbi-uvt-go-uvfit"


