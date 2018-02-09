#!/usr/bin/fish
#

if contains "Darwin" (uname)
    if type greadlink | grep -q "Could not find"
        set TMP_READLINK=(dirname (status -f))/bin/3rd_party/greadlink
        set -x GAG_ROOT_DIR ($TMP_READLINK -f (dirname (status -f)))/gildas-exe-06feb18
    else
        set -x GAG_ROOT_DIR (greadlink -f (dirname (status -f)))/gildas-exe-06feb18
    end
else
    set -x GAG_ROOT_DIR (readlink -f (dirname (status -f)))/gildas-exe-06feb18
end

set -x GAG_EXEC_SYSTEM (ls -1 $GAG_ROOT_DIR | grep gfortran)

set -x GAG_EXEC_DIR "$GAG_ROOT_DIR/$GAG_EXEC_SYSTEM"

set -x GAG_PATH "$GAG_ROOT_DIR/etc"

# source "$GAG_ROOT_DIR/etc/bash_profile" # > /dev/null

# 
# PATH
# remove old variable in PATH
set TMP_PATH_LIST
for TMP_PATH_ITEM in {$PATH}
    if [ "$TMP_PATH_ITEM" != "$GAG_EXEC_DIR/bin" ]
        set TMP_PATH_LIST $TMP_PATH_LIST $TMP_PATH_ITEM
    end
end
set -x PATH $TMP_PATH_LIST





if not contains             "$GAG_EXEC_DIR/bin" $PATH
    set -x PATH             "$GAG_EXEC_DIR/bin" $PATH
end
if not contains             "/usr/lib" $LD_LIBRARY_PATH
    set -x LD_LIBRARY_PATH  "/usr/lib" $LD_LIBRARY_PATH
end
if not contains             "$GAG_EXEC_DIR/lib" $LD_LIBRARY_PATH
    set -x LD_LIBRARY_PATH  "$GAG_EXEC_DIR/lib" $LD_LIBRARY_PATH
end
if not contains             "$GAG_EXEC_DIR/python" $PYTHONPATH
    set -x PYTHONPATH       "$GAG_EXEC_DIR/python" $PYTHONPATH
end

# 
# have to reformat LD_LIBRARY_PATH, see --
# https://github.com/fish-shell/fish-shell/issues/2456
if true
    set -xg LD_LIBRARY_PATH (printf '%s\n' $LD_LIBRARY_PATH | perl -p -e 's/:/ /g')
end

# 
# print welcome message if in interactive environment
if not set -q "$PS1"
    echo
    echo "Selecting GILDAS version: 06feb18, executable tree, $GAG_EXEC_SYSTEM"
    echo
end

# 
# deal with sed -i problem
if true
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
if true
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


