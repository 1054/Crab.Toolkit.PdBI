#!/usr/bin/env tcsh
# 


set BIN_SETUP_SCRIPT = `dirname $0`/bin/bin_setup.bash

set PATH = `bash -c "source $BIN_SETUP_SCRIPT -print" | tail -n 1`

type casa-ms-split
type casa-ms-concat
type pdbi-uvt-go-splitpolar
type pdbi-uvt-go-import-uvfits
type pdbi-uvt-go-average
type pdbi-uvt-go-uvfit


