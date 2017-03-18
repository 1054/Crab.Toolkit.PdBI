#!/bin/bash
#
# Aim:
#    This code will add the directory of this script into the PATH system variable. 
# 


# 
# read input arguments
Crab_BIN_SETUP_INPUT_FLAG="n/a"
Crab_BIN_SETUP_DEBUG_FLAG=0
Crab_BIN_SETUP_CLEAR_LIST=()
Crab_BIN_SETUP_CHECK_LIST=()
for (( i=1; i<=$#; i++ )); do
    #echo "${!i}"
    if echo "${!i}" | grep -q -i "^-debug"; then Crab_BIN_SETUP_INPUT_FLAG="n/a"; Crab_BIN_SETUP_DEBUG_FLAG=1; continue; fi
    if echo "${!i}" | grep -q -i "^-check"; then Crab_BIN_SETUP_INPUT_FLAG="check"; continue; fi
    if echo "${!i}" | grep -q -i "^-clear"; then Crab_BIN_SETUP_INPUT_FLAG="clear"; continue; fi
    if echo "${!i}" | grep -q -i "^-";      then Crab_BIN_SETUP_INPUT_FLAG="n/a"; continue; fi
    # 
    if [[ "$Crab_BIN_SETUP_INPUT_FLAG" == "check" ]]; then Crab_BIN_SETUP_CHECK_LIST+=("${!i}"); fi
    if [[ "$Crab_BIN_SETUP_INPUT_FLAG" == "clear" ]]; then Crab_BIN_SETUP_CLEAR_LIST+=("${!i}"); fi
done


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

if [[ $Crab_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
    echo "Crab_BIN_SETUP_PATH=$Crab_BIN_SETUP_PATH"
fi

Crab_BIN_SETUP_CLEAR_LIST+=("$Crab_BIN_SETUP_PATH")

#
# append PATH, move to the first if Crab_BIN_SETUP_PATH is not at the first place. 
# <20170313>
# <20170318>
#if [[ "$PATH" == *"$Crab_BIN_SETUP_PATH"* ]]
if [[ 1 == 1 ]]; then
    # split system path variable into a list
    Old_IFS=$IFS
    IFS=$":" Crab_BIN_SETUP_PATH_LIST=($PATH)
    IFS=$Old_IFS
    if [[ $Crab_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
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
        # clear path items
        Crab_BIN_SETUP_CLEAR_LIST_FLAG=0
        for (( j=0; j<${#Crab_BIN_SETUP_CLEAR_LIST[@]}; j++ )); do
            if [[ "${Crab_BIN_SETUP_PATH_LIST[i]}" == ${Crab_BIN_SETUP_CLEAR_LIST[j]} ]]; then
                if [[ $Crab_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
                    echo "Clearing \"${Crab_BIN_SETUP_CLEAR_LIST[j]}\""
                fi
                Crab_BIN_SETUP_CLEAR_LIST_FLAG=1; break
            fi
        done
        if [[ $Crab_BIN_SETUP_CLEAR_LIST_FLAG -eq 0 && "${Crab_BIN_SETUP_PATH_LIST[i]}" != "." ]]; then
            if [[ ${#Crab_BIN_SETUP_PATH_POOL[@]} -eq 0 ]]; then
                Crab_BIN_SETUP_PATH_TEXT="${Crab_BIN_SETUP_PATH_LIST[i]}"
                Crab_BIN_SETUP_PATH_POOL+=("${Crab_BIN_SETUP_PATH_LIST[i]}")
            else
                Crab_BIN_SETUP_PATH_TEXT="$Crab_BIN_SETUP_PATH_TEXT:${Crab_BIN_SETUP_PATH_LIST[i]}"
                Crab_BIN_SETUP_PATH_POOL+=("${Crab_BIN_SETUP_PATH_LIST[i]}")
            fi
        fi
        #echo "$Crab_BIN_SETUP_PATH_TEXT"
    done
    # finally append current directory as the last system path item
    if [[ x"$Crab_BIN_SETUP_PATH_TEXT" != x ]]; then
        export PATH="$Crab_BIN_SETUP_PATH_TEXT:."
    fi
    # print sorted/dup-removed/cleared PATH
    if [[ $Crab_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
        echo "Sorting PATH=$PATH"
    fi
fi

if [[ "$PATH" != *"$Crab_BIN_SETUP_PATH"* ]]; then
    export PATH="$Crab_BIN_SETUP_PATH:$PATH"
    if [[ $Crab_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
        echo "Prepending PATH=$PATH"
    fi
fi


# 
# check commands
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
#Crab_BIN_SETUP_CHECK_LIST=("$@")
#if [[ $- =~ "i" ]]; then 
    for (( i=0; i<${#Crab_BIN_SETUP_CHECK_LIST[@]}; i++ )); do
        if [[ $Crab_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
            echo "Checking ${Crab_BIN_SETUP_CHECK_LIST[i]}"
        fi
        type ${Crab_BIN_SETUP_CHECK_LIST[i]}
    done
#fi





