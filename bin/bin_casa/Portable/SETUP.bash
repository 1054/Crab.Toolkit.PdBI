#!/bin/bash
#

export CASA_ROOT_DIR=$(dirname $(perl -MCwd -e 'print Cwd::abs_path shift' "${BASH_SOURCE[0]}"))

export CASA_SUB_DIR="casa-release-4.7.0-1-el6"

if [[ $# -gt 0 ]]; then
    CASA_SUB_DIR=""
    if echo "$1" | grep -q "^4.7";     then export CASA_SUB_DIR="casa-release-4.7.2-el6";       fi
    if echo "$1" | grep -q "^4.7.0";   then export CASA_SUB_DIR="casa-release-4.7.0-1-el6";     fi
    if echo "$1" | grep -q "^4.6";     then export CASA_SUB_DIR="casa-release-4.6.0-el6";       fi
    if echo "$1" | grep -q "^4.4";     then export CASA_SUB_DIR="casa-release-4.4.0-el6";       fi
    if echo "$1" | grep -q "^4.5";     then export CASA_SUB_DIR="casa-release-4.5.3-el6";       fi
    if echo "$1" | grep -q "^4.5.2";   then export CASA_SUB_DIR="casa-release-4.5.2-el6";       fi
    if echo "$1" | grep -q "^4.5.1";   then export CASA_SUB_DIR="casa-release-4.5.1-el6";       fi
    if echo "$1" | grep -q "^4.3";     then export CASA_SUB_DIR="casa-release-4.3.1-el6";       fi
    if echo "$1" | grep -q "^4.2";     then export CASA_SUB_DIR="casapy-42.2.30986-1-64b";      fi
    if echo "$1" | grep -q "^4.2.2-p"; then export CASA_SUB_DIR="casapy-42.2.30986-pipe-1-64b"; fi
    if echo "$1" | grep -q "^3.4";     then export CASA_SUB_DIR="casapy-34.0.19988-002-64b";    fi
    if [[ x"$CASA_SUB_DIR" == x ]]; then
        echo "Error! The input CASA version \"$1\" could not be understood!"; exit 1
    fi
fi

echo "$CASA_SUB_DIR"

if [[ ! -d "$CASA_ROOT_DIR/$CASA_SUB_DIR" ]]; then
    echo "Error! \"$CASA_ROOT_DIR/$CASA_SUB_DIR\" was not found!"
    return
fi

source "$CASA_ROOT_DIR/bin/bin_setup.bash" -path "$CASA_ROOT_DIR/$CASA_SUB_DIR/bin" -prepend -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

source "$CASA_ROOT_DIR/bin/bin_setup.bash" -var LD_LIBRARY_PATH -path "$CASA_ROOT_DIR/$CASA_SUB_DIR/lib" -append -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

source "$CASA_ROOT_DIR/bin/bin_setup.bash" -var CASALD_LIBRARY_PATH -path "$CASA_ROOT_DIR/$CASA_SUB_DIR/lib" -prepend -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

source "$CASA_ROOT_DIR/bin/bin_setup.bash" -var PYTHONPATH -path "$CASA_ROOT_DIR/$CASA_SUB_DIR/lib/python2.7/site-packages" -prepend -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

source "$CASA_ROOT_DIR/bin/bin_setup.bash" -var PYTHONPATH -path "$CASA_ROOT_DIR/analysis_scripts" -prepend -debug


