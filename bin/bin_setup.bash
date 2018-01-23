#!/bin/bash
#
# Aim:
#    This code will add the directory of this script into the PATH system variable. 
# 
# Usage:
#    source /some/path/to/bin_setup.bash -check command_1 command_2
#    source /some/path/to/bin_setup.bash -var LD_LIBRARY_PATH -path /my/lib 
#    source /some/path/to/bin_setup.bash -var PATH -clear "/some/path/to/be/deleted/from/path" -noop -debug
# 


# 
# read input arguments
CRAB_BIN_SETUP_INPUT_FLAG="n/a"
CRAB_BIN_SETUP_DEBUG_FLAG=0
CRAB_BIN_SETUP_CLEAR_LIST=()
CRAB_BIN_SETUP_CHECK_LIST=()
CRAB_BIN_SETUP_INPUT_PATH=""
CRAB_BIN_SETUP_PRINT_FLAG=0
CRAB_BIN_SETUP_ORDER_FLAG=1 # 1 for prepend, 0 for append
CRAB_BIN_SETUP_NO_OP_FLAG=0 # no operation for current path
CRAB_BIN_SETUP_VARIABLE="PATH"
for (( i=1; i<=$#; i++ )); do
    #echo "${!i}"
    if echo "${!i}" | grep -q -i "^-debug";   then CRAB_BIN_SETUP_INPUT_FLAG="n/a"; CRAB_BIN_SETUP_DEBUG_FLAG=1; continue; fi
    if echo "${!i}" | grep -q -i "^-print";   then CRAB_BIN_SETUP_INPUT_FLAG="n/a"; CRAB_BIN_SETUP_PRINT_FLAG=1; continue; fi
    if echo "${!i}" | grep -q -i "^-prepend"; then CRAB_BIN_SETUP_INPUT_FLAG="n/a"; CRAB_BIN_SETUP_ORDER_FLAG=1; continue; fi
    if echo "${!i}" | grep -q -i "^-append";  then CRAB_BIN_SETUP_INPUT_FLAG="n/a"; CRAB_BIN_SETUP_ORDER_FLAG=0; continue; fi
    if echo "${!i}" | grep -q -i "^-noop";    then CRAB_BIN_SETUP_INPUT_FLAG="n/a"; CRAB_BIN_SETUP_NO_OP_FLAG=1; continue; fi
    if echo "${!i}" | grep -q -i "^-check";   then CRAB_BIN_SETUP_INPUT_FLAG="check"; continue; fi
    if echo "${!i}" | grep -q -i "^-clear";   then CRAB_BIN_SETUP_INPUT_FLAG="clear"; continue; fi
    if echo "${!i}" | grep -q -i "^-path";    then CRAB_BIN_SETUP_INPUT_FLAG="path"; continue; fi
    if echo "${!i}" | grep -q -i "^-var";     then CRAB_BIN_SETUP_INPUT_FLAG="var"; continue; fi
    if echo "${!i}" | grep -q -i "^-";        then CRAB_BIN_SETUP_INPUT_FLAG="n/a"; continue; fi
    # 
    if [[ "$CRAB_BIN_SETUP_INPUT_FLAG" == "check" ]]; then CRAB_BIN_SETUP_CHECK_LIST+=("${!i}"); fi
    if [[ "$CRAB_BIN_SETUP_INPUT_FLAG" == "clear" ]]; then CRAB_BIN_SETUP_CLEAR_LIST+=("${!i}"); fi
    if [[ "$CRAB_BIN_SETUP_INPUT_FLAG" == "path"  ]]; then CRAB_BIN_SETUP_INPUT_PATH="${!i}"; fi
    if [[ "$CRAB_BIN_SETUP_INPUT_FLAG" == "var"   ]]; then CRAB_BIN_SETUP_VARIABLE="${!i}"; fi
done


# 
# if CRAB_BIN_SETUP_PRINT_FLAG == 1 then CRAB_BIN_SETUP_DEBUG_FLAG = 0
# 
if [[ $CRAB_BIN_SETUP_PRINT_FLAG -eq 1 ]]; then
    CRAB_BIN_SETUP_DEBUG_FLAG=0
    CRAB_BIN_SETUP_CHECK_LIST=()
fi


# 
# set dzreadlink to get full path but does not follow/resolve symbol links
# 

function dzreadlink() {
    if [[ $# -gt 1 ]]; then if [[ "$1" == "-f" ]]; then shift; fi; fi
    DIR="$1"; if [[ "$DIR" != *"/"* ]]; then DIR="./$DIR"; fi # 20170228: fixed bug: path without "/"
    DIR=$(echo "${DIR%/*}") # 20160410: fixed bug: source SETUP just under the Softwares dir
    # if [[ -d "$DIR" ]]; then cd "$DIR" && echo "$(pwd -P)/$(basename ${1})";  # 20171208: 'pwd -P' will resolve symbolic links!
    # else echo "$(pwd -P)/$(basename ${1})"; fi # 20171208: 'pwd -P' will resolve symbolic links!
    if [[ -d "$DIR" ]]; then cd "$DIR" && echo "$(pwd)/$(basename ${1})"; 
    else echo "$(pwd)/$(basename ${1})"; fi
}


# 
# get current script directory as the CRAB_BIN_SETUP_PATH (if not given by the input argument -path)
# 
if [[ x"$CRAB_BIN_SETUP_INPUT_PATH" == x ]]; then
    CRAB_BIN_SETUP_INPUT_PATH=$(dirname "${BASH_SOURCE[0]}")
fi
#<20170807># if [[ $(type perl 2>/dev/null | wc -l) -eq 1 ]]; then
#<20170807>#     CRAB_BIN_SETUP_PATH=$(perl -MCwd -e 'print Cwd::abs_path shift' "$CRAB_BIN_SETUP_INPUT_PATH")
#<20170807># else
#<20170807>#     if [[ $(uname) == *"Darwin"* ]]; then
#<20170807>#         if [[ $(type greadlink 2>/dev/null | wc -l) -eq 1 ]]; then
#<20170807>#             CRAB_BIN_SETUP_PATH=$(greadlink -f "$CRAB_BIN_SETUP_INPUT_PATH")
#<20170807>#         else
#<20170807>#             function greadlink() {
#<20170807>#                 if [[ $# -gt 1 ]]; then if [[ "$1" == "-f" ]]; then shift; fi; fi
#<20170807>#                 DIR="$1"; if [[ "$DIR" != *"/"* ]]; then DIR="./$DIR"; fi # 20170228: fixed bug: path without "/"
#<20170807>#                 DIR=$(echo "${DIR%/*}") # 20160410: fixed bug: source SETUP just under the Softwares dir
#<20170807>#                 if [[ -d "$DIR" ]]; then cd "$DIR" && echo "$(pwd -P)/$(basename ${1})"; 
#<20170807>#                 else echo "$(pwd -P)/$(basename ${1})"; fi
#<20170807>#             }
#<20170807>#             CRAB_BIN_SETUP_PATH=$(greadlink -f "$CRAB_BIN_SETUP_INPUT_PATH")
#<20170807>#         fi
#<20170807>#     else
#<20170807>#         CRAB_BIN_SETUP_PATH=$(readlink -f "$CRAB_BIN_SETUP_INPUT_PATH")
#<20170807>#     fi
#<20170807># fi
CRAB_BIN_SETUP_PATH=$(dzreadlink "$CRAB_BIN_SETUP_INPUT_PATH")

if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
    echo "CRAB_BIN_SETUP_PATH=$CRAB_BIN_SETUP_PATH"
fi



export CRAB_BIN_SETUP_PATH



# Prepare to clear existing current PATH
if [[ $CRAB_BIN_SETUP_NO_OP_FLAG -eq 0 ]]; then
    CRAB_BIN_SETUP_CLEAR_LIST+=("$CRAB_BIN_SETUP_PATH")
fi



# If no PATH to clear (i.e. nothing to append to PATH), then exit directly
if [[ ${#CRAB_BIN_SETUP_CLEAR_LIST[@]} -eq 0 ]]; then
    exit
fi



#
# append PATH, move to the first if CRAB_BIN_SETUP_PATH is not at the first place. 
# <20170313>
# <20170318>
#if [[ "$PATH" == *"$CRAB_BIN_SETUP_PATH"* ]]
if [[ 1 == 1 ]]; then
    # split system path variable into a list
    Old_IFS=$IFS
    IFS=$":" CRAB_BIN_SETUP_PATH_LIST=(${!CRAB_BIN_SETUP_VARIABLE})
    IFS=$Old_IFS
    # remove empty item
    i=0
    while [[ $i -lt ${#CRAB_BIN_SETUP_PATH_LIST[@]} && ${#CRAB_BIN_SETUP_PATH_LIST[@]} -gt 0 ]]; do
        #echo "Debug: Checking CRAB_BIN_SETUP_PATH_LIST[$i]: \"${CRAB_BIN_SETUP_PATH_LIST[i]}\""
        if [[ -z "${CRAB_BIN_SETUP_PATH_LIST[i]}" ]]; then
            CRAB_BIN_SETUP_PATH_LIST=(${CRAB_BIN_SETUP_PATH_LIST[@]:0:$i} ${CRAB_BIN_SETUP_PATH_LIST[@]:$(($i+1))})
        else
            i=$((i+1))
        fi
    done
    if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
        echo -n "Checking $CRAB_BIN_SETUP_VARIABLE="
        echo "${CRAB_BIN_SETUP_PATH_LIST[@]}" "(${#CRAB_BIN_SETUP_PATH_LIST[@]})"
    fi
    CRAB_BIN_SETUP_PATH_POOL=()
    CRAB_BIN_SETUP_PATH_TEXT=""
    # loop each system path item and remove duplicated and the specified path to drop
    for (( i=0; i<${#CRAB_BIN_SETUP_PATH_LIST[@]}; i++ )); do
        # check duplication
        for (( j=0; j<${#CRAB_BIN_SETUP_PATH_POOL[@]}; j++ )); do
            if [[ "${CRAB_BIN_SETUP_PATH_LIST[i]}" == "${CRAB_BIN_SETUP_PATH_POOL[j]}" ]]; then
                CRAB_BIN_SETUP_PATH_LIST[i]="."
            fi
        done
        # clear path items
        CRAB_BIN_SETUP_CLEAR_LIST_FLAG=0
        for (( j=0; j<${#CRAB_BIN_SETUP_CLEAR_LIST[@]}; j++ )); do
            if [[ "${CRAB_BIN_SETUP_PATH_LIST[i]}" == ${CRAB_BIN_SETUP_CLEAR_LIST[j]} ]]; then
                if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
                    echo "Clearing \"${CRAB_BIN_SETUP_CLEAR_LIST[j]}\""
                fi
                CRAB_BIN_SETUP_CLEAR_LIST_FLAG=1; break
            fi
        done
        if [[ $CRAB_BIN_SETUP_CLEAR_LIST_FLAG -eq 0 && "${CRAB_BIN_SETUP_PATH_LIST[i]}" != "." && ! -z "${CRAB_BIN_SETUP_PATH_LIST[i]}" ]]; then
            if [[ ${#CRAB_BIN_SETUP_PATH_POOL[@]} -eq 0 ]]; then
                CRAB_BIN_SETUP_PATH_TEXT="${CRAB_BIN_SETUP_PATH_LIST[i]}"
                CRAB_BIN_SETUP_PATH_POOL+=("${CRAB_BIN_SETUP_PATH_LIST[i]}")
            else
                CRAB_BIN_SETUP_PATH_TEXT="$CRAB_BIN_SETUP_PATH_TEXT:${CRAB_BIN_SETUP_PATH_LIST[i]}"
                CRAB_BIN_SETUP_PATH_POOL+=("${CRAB_BIN_SETUP_PATH_LIST[i]}")
            fi
        fi
        #echo "$CRAB_BIN_SETUP_PATH_TEXT" # paths not to be cleared
    done
    # finally append current directory "." as the last system path item
    if [[ x"$CRAB_BIN_SETUP_PATH_TEXT" != x ]]; then
        declare $CRAB_BIN_SETUP_VARIABLE="$CRAB_BIN_SETUP_PATH_TEXT:."
    else
        declare $CRAB_BIN_SETUP_VARIABLE="."
    fi
    # print sorted/dup-removed/cleared PATH
    if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
        echo "Sorting $CRAB_BIN_SETUP_VARIABLE=${!CRAB_BIN_SETUP_VARIABLE}"
    fi
fi

if [[ $CRAB_BIN_SETUP_NO_OP_FLAG -eq 0 ]]; then
    if [[ ":${!CRAB_BIN_SETUP_VARIABLE}:" != *":$CRAB_BIN_SETUP_PATH:"* ]]; then
        if [[ $CRAB_BIN_SETUP_ORDER_FLAG -eq 1 ]]; then
            declare $CRAB_BIN_SETUP_VARIABLE="$CRAB_BIN_SETUP_PATH:${!CRAB_BIN_SETUP_VARIABLE}"
            if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
                echo "Prepending $CRAB_BIN_SETUP_VARIABLE=${!CRAB_BIN_SETUP_VARIABLE}"
            fi
        else
            declare $CRAB_BIN_SETUP_VARIABLE="${!CRAB_BIN_SETUP_VARIABLE}:$CRAB_BIN_SETUP_PATH"
            if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
                echo "Appending $CRAB_BIN_SETUP_VARIABLE=${!CRAB_BIN_SETUP_VARIABLE}"
            fi
        fi
    fi
fi



if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
    echo "Exporting $CRAB_BIN_SETUP_VARIABLE=${!CRAB_BIN_SETUP_VARIABLE}"
fi



export $CRAB_BIN_SETUP_VARIABLE



# 
# check commands
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
#CRAB_BIN_SETUP_CHECK_LIST=("$@")
#if [[ $- =~ "i" ]]; then 
    for (( i=0; i<${#CRAB_BIN_SETUP_CHECK_LIST[@]}; i++ )); do
        if [[ $CRAB_BIN_SETUP_DEBUG_FLAG -eq 1 ]]; then
            echo "Checking ${CRAB_BIN_SETUP_CHECK_LIST[i]}"
        fi
        type ${CRAB_BIN_SETUP_CHECK_LIST[i]}
    done
#fi



# 
# Final print
# 
if [[ $CRAB_BIN_SETUP_PRINT_FLAG -eq 1 ]]; then
    echo "${!CRAB_BIN_SETUP_VARIABLE}"
fi





