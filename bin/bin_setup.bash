#!/bin/bash
#
# Aim:
#    This code will add the directory of this script into the PATH system variable. 
# 



# 
# get Crab_BIN_SETUP_PATH
Crab_BIN_SETUP_PATH=""
if [[ $(uname) == *"Darwin"* ]]; then
    if [[ $(type greadlink 2>/dev/null | wc -l) -eq 1 ]]; then
        Crab_BIN_SETUP_PATH=$(dirname $(greadlink -f "${BASH_SOURCE[0]}"))
    else
        function greadlink() {
            if [[ $# -gt 1 ]]; then if [[ "$1" == "-f" ]]; then shift; fi; fi
            DIR="$1"; if [[ "$DIR" != *"/"* ]]; then DIR="./$DIR"; fi # 20170228: fixed bug: path without "/"
            DIR=$(echo "${DIR%/*}") # 20160410: fixed bug: source SETUP just under the Softwares dir
            if [[ -d "$DIR" ]]; then cd "$DIR" && echo "$(pwd -P)/$(basename ${1})"; 
            else echo "$(pwd -P)/$(basename ${1})"; fi
        }
        Crab_BIN_SETUP_PATH=$(dirname $(greadlink -f "${BASH_SOURCE[0]}"))
    fi
else
    Crab_BIN_SETUP_PATH=$(dirname $(readlink -f "${BASH_SOURCE[0]}"))
fi

if echo "$@" | grep -q -i "debug"; then
    echo "Crab_BIN_SETUP_PATH=$Crab_BIN_SETUP_PATH"
fi


#
# append PATH, move to the first if Crab_BIN_SETUP_PATH is not at the first place. 
# <20170313>
# <20170318>
if [[ "$PATH" == *"$Crab_BIN_SETUP_PATH"* ]]; then
    # split system path variable into a list
    Old_IFS=$IFS
    IFS=$":" Crab_BIN_SETUP_PATH_LIST=($PATH)
    IFS=$Old_IFS
    if echo "$@" | grep -q -i "debug"; then
        echo -n "Checking PATH="
        echo "${Crab_BIN_SETUP_PATH_LIST[@]}" "(${#Crab_BIN_SETUP_PATH_LIST[@]})"
    fi
    Crab_BIN_SETUP_PATH_POOL=()
    Crab_BIN_SETUP_PATH_TEXT=""
    # loop each system path item and remove duplicated and the specified path to drop
    for (( i=0; i<${#Crab_BIN_SETUP_PATH_LIST[@]}; i++ )); do
        # check duplication
        for (( j=0; j<${#Crab_BIN_SETUP_PATH_POOL[@]}; j++ )); do
            if [[ "${Crab_BIN_SETUP_PATH_LIST[i]}" == "${Crab_BIN_SETUP_PATH_POOL[j]}" ]]; then
                Crab_BIN_SETUP_PATH_LIST[i]="."
            fi
        done
        # append to path
        if [[ "${Crab_BIN_SETUP_PATH_LIST[i]}" != "$Crab_BIN_SETUP_PATH" && "${Crab_BIN_SETUP_PATH_LIST[i]}" != "." ]]; then
            if [[ ${#Crab_BIN_SETUP_PATH_POOL[@]} -eq 0 ]]; then
                Crab_BIN_SETUP_PATH_TEXT="${Crab_BIN_SETUP_PATH_LIST[i]}"
                Crab_BIN_SETUP_PATH_POOL+=("${Crab_BIN_SETUP_PATH_LIST[i]}")
            else
                Crab_BIN_SETUP_PATH_TEXT="$Crab_BIN_SETUP_PATH_TEXT:${Crab_BIN_SETUP_PATH_LIST[i]}"
                Crab_BIN_SETUP_PATH_POOL+=("${Crab_BIN_SETUP_PATH_LIST[i]}")
            fi
            #echo "$Crab_BIN_SETUP_PATH_TEXT"
        fi
    done
    # finally append current directory as the last system path item
    if [[ x"$Crab_BIN_SETUP_PATH_TEXT" != x ]]; then
        export PATH="$Crab_BIN_SETUP_PATH_TEXT:."
    fi
fi

if [[ "$PATH" != *"$Crab_BIN_SETUP_PATH"* ]]; then
    export PATH="$Crab_BIN_SETUP_PATH":$PATH
fi
    
if echo "$@" | grep -q -i "debug"; then
    echo "Sorting PATH=$PATH"
fi


# 
# check commands
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
Crab_BIN_SETUP_CHECK_CMD=("$@")
#if [[ $- =~ "i" ]]; then 
    for (( i=0; i<${#Crab_BIN_SETUP_CHECK_CMD[@]}; i++ )); do
        if echo "${Crab_BIN_SETUP_CHECK_CMD[i]}" | grep -v -q -i "debug"; then
            if echo "$@" | grep -q -i "debug"; then
                echo "Checking cmd ${Crab_BIN_SETUP_CHECK_CMD[i]}"
            fi
            type ${Crab_BIN_SETUP_CHECK_CMD[i]}
        fi
    done
#fi





