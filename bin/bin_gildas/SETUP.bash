#!/bin/bash
#
export GAG_TOP_DIR=$(dirname ${BASH_SOURCE[0]})
export GAG_SUB_DIR="gildas-exe-07feb18"
export GAG_ROOT_DIR=$(perl -MCwd -e 'print Cwd::abs_path shift' "$GAG_TOP_DIR/$GAG_SUB_DIR")
export GAG_EXEC_SYSTEM=$(ls -1 "$GAG_TOP_DIR/$GAG_SUB_DIR/" | grep gfortran)
source "$GAG_TOP_DIR/bin/bin_setup.bash" -path "$GAG_TOP_DIR/$GAG_SUB_DIR/$GAG_EXEC_SYSTEM/bin" -check astro class mapping -clear '*gildas-exe-*' -debug
source "$GAG_TOP_DIR/$GAG_SUB_DIR/etc/bash_profile" # > /dev/null

type astro class mapping

if [[ x"$GAG_ROOT_DIR" == x ]]; then
    echo "Error! Failed to source \"$GAG_TOP_DIR/$GAG_SUB_DIR/etc/bash_profile\"!"
    return
fi




# 
# Print version info if in interactive shell
if [[ $- =~ "i" ]]; then
    mapping -v
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


