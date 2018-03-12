#!/bin/bash
# 
# Last update: 2018-03-12
# 

if [[ $# -lt 1 ]]; then
    echo "Usage :"
    echo "    a_dzliu_code_to_convert_alma_uvt_to_uvfits.sh XXX.uvt"
    echo ""
fi

# check gildas/mapping
if [[ $(type mapping 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "****************************************"
    echo "Error! GILDAS/MAPPING was not installed!"
    echo "****************************************"
    exit 255
fi

# read input
for (( i=1; i<=$#; i++ )); do
    fits_uvt="${!i}"
    fits_name=$(basename "$fits_uvt" | sed -e 's/[.][uU][vV][tT]$//g')
    echo "Processing \"$fits_uvt\""
    if [[ ! -f "$fits_uvt" ]] && [[ ! -L "$fits_uvt" ]]; then
        echo "****************************************"
        echo "Error! \"$fits_uvt\" does not exist!"
        echo "****************************************"
        continue
    fi
    if [[ -f "$fits_name.uvfits" ]]; then
        echo "Found existing \"$fits_name.uvfits\"! Backup as \"$fits_name.uvfits.backup\""
        mv "$fits_name.uvfits" "$fits_name.uvfits.backup"
    fi
    
    # First export uvfits
    echo "vector\fits $fits_name.uvfits from $fits_uvt /style casa /overwrite" | mapping -nw -nl > "$fits_name.uvfits.log"
    # Then fix the NAXIS2 in the Antenna Table (the second fits extension)
    #cat "$fits_name.uvfits.log" | grep "Number of antennas"
    NANT=$(cat $fits_name.uvfits.log | grep "Number of antennas" | sed -e 's/.*: *//g')
    if [[ x"$NANT" == x ]]; then 
        echo "****************************************"
        echo "Error! Failed to run GILDAS/MAPPING to convert uvfits to uvt! Please check log file \"$fits_name.uvfits.log\"!"
        echo "****************************************"
        continue
    fi
    LANG=C LC_CTYPE=C sed -i.bak -e "s/NAXIS2  =                    \*/NAXIS2  =                   $NANT/g" "$fits_name.uvfits"
    # Then fix the TELESCOP
    LANG=C LC_CTYPE=C sed -i.bak -e "s/TELESCOP= \'NOEMA/TELESCOP= \'ALMA /g" "$fits_name.uvfits"
    # Then fix the ZSOURCE
    LANG=C LC_CTYPE=C sed -i.bak -e "s/ZSOURCE =/ZSOURCEX=/g" "$fits_name.uvfits"
    # Clean up
    if [[ -f "$fits_name.uvfits.bak" ]]; then rm "$fits_name.uvfits.bak"; fi
    
    # 
    echo "Output to \"$fits_name.uvfits\"!"
    
done

