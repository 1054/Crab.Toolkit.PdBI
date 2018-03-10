#!/usr/bin/env fish
#

set -gx CASA_ROOT_DIR (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status -f)))

set -gx CASA_SUB_DIR casa-release-4.7.0-1-el6

if [ (count $argv) -gt 0 ]; 
    set -gx CASA_SUB_DIR "N/A"
    if echo "$argv[1]" | grep -q "^4.7";     set -gx CASA_SUB_DIR "casa-release-4.7.0-1-el6";      end
    if echo "$argv[1]" | grep -q "^4.6";     set -gx CASA_SUB_DIR "casa-release-4.6.0-el6";        end
    if echo "$argv[1]" | grep -q "^4.5";     set -gx CASA_SUB_DIR "casa-release-4.5.3-el6";        end
    if echo "$argv[1]" | grep -q "^4.4";     set -gx CASA_SUB_DIR "casa-release-4.4.0-el6";        end
    if echo "$argv[1]" | grep -q "^4.3";     set -gx CASA_SUB_DIR "casa-release-4.3.1-el6";        end
    if echo "$argv[1]" | grep -q "^4.2";     set -gx CASA_SUB_DIR "casapy-42.2.30986-1-64b";       end
    if echo "$argv[1]" | grep -q "^4.2.2-p"; set -gx CASA_SUB_DIR "casapy-42.2.30986-pipe-1-64b";  end
    if echo "$argv[1]" | grep -q "^3.4";     set -gx CASA_SUB_DIR "casapy-34.0.19988-002-64b";     end
    if [ "$CASA_SUB_DIR" = "N/A" ]; 
        echo "Error! The input CASA version \"$argv[1]\" could not be understood!"; exit 1
    end

end

echo "$CASA_SUB_DIR"

if [ ! -d "$CASA_ROOT_DIR/$CASA_SUB_DIR" ]; 
    echo "Error! \"$CASA_ROOT_DIR/$CASA_SUB_DIR\" was not found!"
    exit
end

set -gx PATH (string split ":" (bash -c "source $CASA_ROOT_DIR/bin/bin_setup.bash -path $CASA_ROOT_DIR/$CASA_SUB_DIR/bin -clear '*casa-release-*' '*casapy-*' -print | tail -n 1"))

set -gx LD_LIBRARY_PATH (string split ":" (bash -c "source $CASA_ROOT_DIR/bin/bin_setup.bash -var LD_LIBRARY_PATH -path $CASA_ROOT_DIR/$CASA_SUB_DIR/lib -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -append -print | tail -n 1"))

set -gx CASALD_LIBRARY_PATH (string split ":" (bash -c "source $CASA_ROOT_DIR/bin/bin_setup.bash -var CASALD_LIBRARY_PATH -path $CASA_ROOT_DIR/$CASA_SUB_DIR/lib -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -append -print | tail -n 1"))

set -gx PYTHONPATH (string split ":" (bash -c "source $CASA_ROOT_DIR/bin/bin_setup.bash -var PYTHONPATH -path $CASA_ROOT_DIR/$CASA_SUB_DIR/lib/python2.7/lib -clear '*casa-release-*' '*casapy-*' '*/CASA/Portable/*' -preppend -print | tail -n 1"))

set -gx PYTHONPATH (string split ":" (bash -c "source $CASA_ROOT_DIR/bin/bin_setup.bash -var PYTHONPATH -path $CASA_ROOT_DIR/analysis_scripts -preppend -print | tail -n 1"))

type casa

echo "PATH = $PATH"

echo "LD_LIBRARY_PATH = $LD_LIBRARY_PATH"

echo "CASALD_LIBRARY_PATH = $CASALD_LIBRARY_PATH"

echo "PYTHONPATH = $PYTHONPATH"


