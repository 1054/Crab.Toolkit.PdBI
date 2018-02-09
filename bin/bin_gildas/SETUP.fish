#!/usr/bin/env fish
#
set -gx GAG_TOP_DIR (dirname (status -f))
set -gx GAG_SUB_DIR "gildas-exe-01apr17"
set -gx GAG_EXEC_SYSTEM (ls -1 "$GAG_TOP_DIR/$GAG_SUB_DIR/" | grep gfortran)

set -gx PATH (string split ":" (bash -c "source '$GAG_TOP_DIR/bin/bin_setup.bash' -path '$GAG_TOP_DIR/$GAG_SUB_DIR/$GAG_EXEC_SYSTEM/bin' -clear '*gildas-exe-*' -print | tail -n 1"))

set -gx PYTHONPATH (string split ":" (bash -c "source '$GAG_TOP_DIR/bin/bin_setup.bash' -path '$GAG_TOP_DIR/$GAG_SUB_DIR/$GAG_EXEC_SYSTEM/python' -clear '*gildas-exe-*' -print | tail -n 1"))

set -gx LD_LIBRARY_PATH (bash -c "source '$GAG_TOP_DIR/bin/bin_setup.bash' -path '$GAG_TOP_DIR/$GAG_SUB_DIR/$GAG_EXEC_SYSTEM/lib' -clear '*gildas-exe-*' -print | tail -n 1")   # Note that LD_LIBRARY_PATH must be ":"-split even in FISH SHELL!

type astro class mapping



set -gx GAG_EXEC_DIR (dirname "$PATH[1]")
set -gx GAG_ROOT_DIR (dirname "$GAG_EXEC_DIR")
set -gx GAG_PATH     "$GAG_ROOT_DIR/etc"



# 
# Print version if in interactive shell
if not set -q "$PS1"
    echo
    mapping -v
    echo
end



# 
# deal with sed -i problem
if false
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
end

# 
# deal with gzip problem
if false
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
end


