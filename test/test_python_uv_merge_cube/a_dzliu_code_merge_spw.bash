#!/bin/bash
# 

pdbi-uvt-go-resample-v9 -name dataset_11_datacube_3.uvt -out dataset_11_datacube_3_resample.uvt -redshift 0.688 -frange 271.000 275.100 -width 0 -overwrite -keep-files
pdbi-uvt-go-resample-v9 -name dataset_11_datacube_4.uvt -out dataset_11_datacube_4_resample.uvt -redshift 0.688 -frange 271.000 275.100 -width 0 -overwrite -keep-files

echo "fits dataset_11_datacube_3_resample.uvfits from dataset_11_datacube_3_resample.uvt /style casa" | mapping -nw -nl
echo "fits dataset_11_datacube_4_resample.uvfits from dataset_11_datacube_4_resample.uvt /style casa" | mapping -nw -nl

# Try to merge the two data cubes --> FAILED
# In GILDAS/mapping we can either merge (add) new visibilities (uvw) for spectral data cube (i.e., combining multiple observations whose spectral grid are exactly the same)
# or merge (average) same visibilities (uvw) for single-channel continuum data (i.e., combining different spws from a single observation, but each combined data should be a single-channel continuum data)
# there is not implement to merge (average) same visibilities (uvw) for spectral data cube (i.e., combining different spws from a single observation, allowing multiple channels and averaging channel-by-channel)
#pdbi-uvt-go-merge -name dataset_11_datacube_3_resample.uvt dataset_11_datacube_4_resample.uvt -out dataset_11_datacube_merged_3_4.uvt -keep-files # NOT WORKING




# I have written a new code to merge the uv table data cube in spectral mode (channel by channel), such a merging can only be done to continuum data in GILDAS/mapping with the tool UV_MERGE with MODE 1
pdbi-uvt-merge-two-data-cube-spw-channel-by-channel.py -name dataset_11_datacube_3_resample.uvt dataset_11_datacube_4_resample.uvt -out merged

#pdbi-uvt-go-average -name dataset_11_datacube_4 -out "extracted_line_map_CO(4-3).uvt" -redshift 0.688 -linename "CO(4-3)" -linewidth 450

pdbi-uvt-go-average -name merged -out "extracted_line_map_CO(4-3).uvt" -redshift 0.688 -linename "CO(4-3)" -linewidth 450

Running pdbi-uvt-go-uvfit -name "extracted_line_map_CO(4-3).uvt" -radec 150.1502269 2.4751248 -fixedpos > "extracted_line_map_CO(4-3)_go_uvfit.stdout.txt"








