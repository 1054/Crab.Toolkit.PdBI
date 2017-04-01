#!/bin/bash
#

OutputDir=$(perl -MCwd -e 'print Cwd::abs_path shift' $(dirname "${BASH_SOURCE[0]}"))

if [[ ! -d "../../../Crab/" ]]; then
    echo "Error! \"../../../Crab/\" was not found!"
    exit
fi

cd ../../../Crab/

if [[ -d "CrabIO/CrabConst/" ]]; then
    cd CrabIO/CrabConst/
    g++ CrabStringClean.cpp radec2degree.cpp -o "$OutputDir"/radec2degree_linux_x86_64
    g++ CrabStringClean.cpp degree2radec.cpp -o "$OutputDir"/degree2radec_linux_x86_64
    g++ double2hex.cpp -o "$OutputDir"/double2hex_linux_x86_64
    g++ hex2double.cpp -o "$OutputDir"/hex2double_linux_x86_64
    g++ float2hex.cpp -o "$OutputDir"/float2hex_linux_x86_64
    g++ hex2float.cpp -o "$OutputDir"/hex2float_linux_x86_64
    g++ lumdist.cpp -o "$OutputDir"/lumdist_linux_x86_64
    cd ../../
fi

if [[ -d "CrabIO/CrabFitsIO/CrabFitsHeader/" ]]; then
    cd CrabIO/CrabFitsIO/CrabFitsHeader/
    #g++ -static-libstdc++ main.cpp CrabFitsIO.cpp -o "$OutputDir"/CrabFitsHeader_linux_x86_64
    g++ main.cpp CrabFitsIO.cpp -o "$OutputDir"/CrabFitsHeader_linux_x86_64
    cd ../../../
fi

if [[ -d "CrabIO/CrabFitsIO/CrabFitsImageArithmetic/" ]]; then
    cd CrabIO/CrabFitsIO/CrabFitsImageArithmetic/
    g++ main.cpp CrabFitsIO.cpp -o "$OutputDir"/CrabFitsImageArithmetic_linux_x86_64
    cd ../../../
fi

if [[ -d "CrabIO/CrabFitsIO/CrabFitsImageCut/" ]]; then
    cd CrabIO/CrabFitsIO/CrabFitsImageCut/
    g++ main.cpp CrabFitsIO.cpp -o "$OutputDir"/CrabFitsImageCrop_linux_x86_64
    cd ../../../
fi

if [[ -d "CrabIO/CrabTable/CrabTableReadColumn/" ]]; then
    cd CrabIO/CrabTable/CrabTableReadColumn/
    g++ main.cpp -o "$OutputDir"/CrabTableReadColumn_linux_x86_64
    cd ../../../
fi

if [[ -d "CrabIO/CrabTable/CrabTableReadInfo/" ]]; then
    cd CrabIO/CrabTable/CrabTableReadInfo/
    g++ main.cpp -o "$OutputDir"/CrabTableReadInfo_linux_x86_64
    cd ../../../
fi

if [[ -d "CrabIO/CrabFitsIO/CrabFitsImageFromGildasMapping/" ]]; then
    cd CrabIO/CrabFitsIO/CrabFitsImageFromGildasMapping/
    g++ -std=c++11 CrabFitsIO.cpp pdbi-uvt-to-fits.cpp -o "$OutputDir"/pdbi-uvt-to-fits_linux_x86_64
    g++ -std=c++11 CrabFitsIO.cpp pdbi-lmv-to-fits.cpp -o "$OutputDir"/pdbi-lmv-to-fits_linux_x86_64
    cd ../../../
fi











