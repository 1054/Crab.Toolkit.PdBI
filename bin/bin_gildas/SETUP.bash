#!/bin/bash
#
export GAG_ROOT_DIR=$(dirname ${BASH_SOURCE[0]})/gildas-exe-06feb18
export GAG_EXEC_SYSTEM=$(ls -1 $GAG_ROOT_DIR | grep gfortran)

#
# PATH
# <20170313>

TEMP_PATH_DROP="$GAG_ROOT_DIR"
if [[ "$PATH" == *"$TEMP_PATH_DROP"* ]]; then
    # split system path variable into a list
    Old_IFS=$IFS
    IFS=$":" TEMP_PATH_LIST=($PATH)
    IFS=$Old_IFS
    #echo ${TEMP_PATH_LIST[@]} "(${#TEMP_PATH_LIST[@]})"
    TEMP_PATH_POOL=()
    TEMP_PATH_TEXT=""
    # loop each system path item and remove duplicated and the specified path to drop
    for (( i=0; i<${#TEMP_PATH_LIST[@]}; i++ )); do
        # check duplication
        for (( j=0; j<${#TEMP_PATH_POOL[@]}; j++ )); do
            if [[ "${TEMP_PATH_LIST[i]}" == "${TEMP_PATH_POOL[j]}" ]]; then
                TEMP_PATH_LIST[i]="."
            fi
        done
        # append to path
        if [[ "${TEMP_PATH_LIST[i]}" != *"$TEMP_PATH_DROP"* && "${TEMP_PATH_LIST[i]}" != "." ]]; then
            if [[ ${#TEMP_PATH_POOL[@]} -eq 0 ]]; then
                TEMP_PATH_TEXT="${TEMP_PATH_LIST[i]}"
                TEMP_PATH_POOL+=("${TEMP_PATH_LIST[i]}")
            else
                TEMP_PATH_TEXT="$TEMP_PATH_TEXT:${TEMP_PATH_LIST[i]}"
                TEMP_PATH_POOL+=("${TEMP_PATH_LIST[i]}")
            fi
            #echo "$TEMP_PATH_TEXT"
        fi
    done
    # finally append current directory as the last system path item
    if [[ x"$TEMP_PATH_TEXT" != x ]]; then
        export PATH="$TEMP_PATH_TEXT:."
    fi
    #echo "PATH = $PATH"
fi
if [[ $PATH != *"$GAG_ROOT_DIR"* ]]; then
    source "$GAG_ROOT_DIR/etc/bash_profile" # > /dev/null
fi



# 
# deal with sed -i problem
if [[ 1 == 0 ]]; then
    echo "Fixing sed -i problem"
    echo "#!/bin/bash"                                                  >  "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "#"                                                            >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "if [[ \$# -gt 0 ]]; then"                                     >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "    if [[ \"\$1\" == \"-i\" && \"\$*\" != *\"-e \"* ]]; then" >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "        shift"                                                >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "        /usr/bin/sed -i -e \"\$@\""                           >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "    else"                                                     >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "        /usr/bin/sed \"\$@\""                                 >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "    fi"                                                       >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "else"                                                         >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "    /usr/bin/sed"                                             >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo "fi"                                                           >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    echo ""                                                             >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
    chmod +x "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed"
else
    rm "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/sed" 2>/dev/null
fi
# 
# deal with gzip problem
if [[ 1 == 0 ]]; then
    echo "Fixing gzip -k problem"
    echo "#!/bin/bash"                                                  >  "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "#"                                                            >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "if [[ \$# -gt 0 ]]; then"                                     >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "    if [[ \"\$1\" == \"-f\" && \"\$*\" != *\"-k \"* ]]; then" >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "        shift"                                                >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "        /usr/bin/gzip -k -f \"\$@\""                          >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "    else"                                                     >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "        /usr/bin/gzip -k -f \"\$@\""                          >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "    fi"                                                       >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "else"                                                         >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "    /usr/bin/gzip"                                            >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo "fi"                                                           >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    echo ""                                                             >> "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
    chmod +x "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip"
else
    rm "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM/bin/gzip" 2>/dev/null
fi


