#!/bin/bash
#
# readlink
if [[ $(uname) == *"Darwin"* ]]; then
    function readlink() {
        if [[ $# -gt 1 ]]; then if [[ "$1" == "-f" ]]; then shift; fi; fi
        DIR=$(echo "${1%/*}"); (cd "$DIR" && echo "$(pwd -P)/$(basename ${1})")
    }
fi
CRABTOOLKITDIR=$(dirname $(readlink -f "${BASH_SOURCE[0]}"))
export CRABTOOLKITDIR
#
# PATH
if [[ $PATH != *"$CRABTOOLKITDIR/bin"* ]]; then
    export PATH="$CRABTOOLKITDIR/bin":$PATH
fi
#
# LIST
CRABTOOLKITCMD=(pdbi-uvt-go-average pdbi-uvt-go-uvfit)
# 
# CHECK
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
if [[ $- =~ "i" ]]; then 
  for TEMPTOOLKITCMD in ${CRABTOOLKITCMD[@]}; do
    type $TEMPTOOLKITCMD
  done
fi


