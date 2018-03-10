#!/bin/bash
# 


CASA_SETUP_BINSETS=$(dirname "${BASH_SOURCE[0]}")"/Portable/bin/bin_setup.bash"
CASA_SETUP_DIRROOT=$(dirname "${BASH_SOURCE[0]}")"/Portable"
CASA_SETUP_DIRPREF="casa*-"
CASA_SETUP_VERSION="5.1.1"
CASA_SETUP_ARCHIVE="*"

if [[ $# -ge 1 ]]; then
    if [[ "$1" == *"README"* ]]; then
        CASA_SETUP_VERSION=($(cat "$1" | grep -i "CASA" | grep -i "version" | perl -p -e 's/.* ([0-9])\.([0-9])\.([0-9][0-9-]*).*/\1 \2 \3 CASA_SETUP_ENDMARK/g' | grep "CASA_SETUP_ENDMARK" | sed -e "s/ CASA_SETUP_ENDMARK//g"))
        if [[ "${#CASA_SETUP_VERSION[@]}" -ne 3 ]]; then
            CASA_SETUP_VERSION=($(cat "$1" | grep -i "CASA" | grep -i "version" | perl -p -e 's/.* ([0-9])\.([0-9])$/\1 \2 CASA_SETUP_ENDMARK/g' | grep "CASA_SETUP_ENDMARK" | sed -e "s/ CASA_SETUP_ENDMARK//g"))
        fi
        if [[ "${#CASA_SETUP_VERSION[@]}" -lt 2 ]]; then
            echo "Error! Failed to read CASA version from the input \"$1\"!"
            echo "CASA_SETUP_VERSION = \"$CASA_SETUP_VERSION\""
            cat "$1" | grep -i "CASA" | grep -i "version" 
            return 1;
        fi
    else
        CASA_SETUP_VERSION=($(echo "$1" | sed -e 's/\./ /g'))
    fi
fi
if [[ $# -ge 2 ]]; then
    CASA_SETUP_ARCHIVE="*$2"
fi

echo "CASA_SETUP_VERSION = ${CASA_SETUP_VERSION[@]}"
CASA_SETUP_DIRNAME="${CASA_SETUP_DIRPREF}*"$(IFS=.; echo "${CASA_SETUP_VERSION[*]}")"${CASA_SETUP_ARCHIVE}"
echo "CASA_SETUP_DIRNAME = ${CASA_SETUP_DIRNAME}"
CASA_SETUP_DIRLIST=($(find "${CASA_SETUP_DIRROOT}" -maxdepth 1 -mindepth 1 -type d -name "${CASA_SETUP_DIRNAME}" | sort -V))
if [[ ${#CASA_SETUP_DIRLIST[@]} -eq 0 ]]; then
    echo "Error! Could not find \"${CASA_SETUP_DIRROOT}/${CASA_SETUP_DIRNAME}\"!"; return 1;
else
    CASA_SETUP_DIRPATH=${CASA_SETUP_DIRLIST[${#CASA_SETUP_DIRLIST[@]}-1]}
    echo "CASA_SETUP_DIRPATH = ${CASA_SETUP_DIRPATH}"
fi

#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${CASA_SETUP_DIRPATH}/lib"
#export PATH="$PATH:${CASA_SETUP_DIRPATH}/bin"

source "${CASA_SETUP_BINSETS}" -var PATH -path "${CASA_SETUP_DIRPATH}/bin" -append -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

source "${CASA_SETUP_BINSETS}" -var LD_LIBRARY_PATH -path "${CASA_SETUP_DIRPATH}/lib" -append -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

source "${CASA_SETUP_BINSETS}" -var CASALD_LIBRARY_PATH -path "${CASA_SETUP_DIRPATH}/lib" -prepend -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug

if [[ -d "${CASA_SETUP_DIRPATH}/lib/python2.7/site-packages" ]]; then
source "${CASA_SETUP_BINSETS}" -var PYTHONPATH -path "${CASA_SETUP_DIRPATH}/lib/python2.7/site-packages" -prepend -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -debug
fi

if [[ -d "${CASA_SETUP_DIRROOT}/analysis_scripts" ]]; then
source "${CASA_SETUP_BINSETS}" -var PYTHONPATH -path "${CASA_SETUP_DIRROOT}/analysis_scripts" -prepend -debug
fi

# casa --version


