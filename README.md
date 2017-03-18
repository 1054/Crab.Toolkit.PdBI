# Crab.Toolkit.PdBI
Crab Toolkit for PdBI Data Reduction

This toolkit contains several commands that can be directly executed under Terminal. 

Examples are given below. 




## Deal with ALMA Measurement Sets ##

Running the follow command to split all sources in an ALMA measurement set in continuum mode. 
Use arguments "-width 1" to split the data with original channel width. 
```
cd /path/to/your/temporary/working/place/
casa-ms-split -vis "/path/to/your/ALMA/calibrated.ms" 
```
After run this, you will get a bunch of scripts under current directory. Among which, please execute "run_casa_ms_split_all.bash". 
```
./run_casa_ms_split_all.bash
```
Then this shell script will call CASA to run split(), cvel(), exportuvfits(), clean(), uvmodelfit() and call GILDAS/mapping to run FITS TO UV table task. 




## Deal with GILDAS UV table ##

First split polarization:
```
pdbi-uvt-go-splitpolar -name MY_UV_table.uvt -out MY_UV_table_output.uvt
```

Then run uv_fit at the phase center:
```
pdbi-uvt-go-uvfit-v2 -name "ID-6406-1mm" -fixpos -point -out "ID-6406-1mm.uvt.uvfit.P.FixedPos"
pdbi-uvt-go-uvfit-v2 -name "ID-6406-1mm" -varypos -point -out "ID-6406-1mm.uvt.uvfit.P.VariedPos"
pdbi-uvt-go-uvfit-v2 -name "ID-6406-1mm" -varypos -cgauss -out "ID-6406-1mm.uvt.uvfit.C.VariedPos"
pdbi-uvt-go-uvfit-v2 -name "ID-6406-1mm" -varypos -egauss -out "ID-6406-1mm.uvt.uvfit.G.VariedPos"
```
The output fitting log file will be "ID-6406-1mm.uvt.uvfit.P.VariedPos.log". 

Or run uv_fit for multiple source by giving the "-radec" argument list:
```
pdbi-uvt-go-uvfit-v2 -name "ID-6406-1mm" -radec 12:01:56.0 55:55:55.0 -fixpos -point \
                                         -radec 12:02:56.0 55:55:55.0 -fixpos -egauss \
                                         -radec 12:03:56.0 55:55:55.0 -fixpos -egauss \
                                         -out "output_multi_source_uv_fit"
```
The output fitting log file will be "output_multi_source_uv_fit.log". 



## More examples for uv_fit ##

Fix circular Gaussian size for uv_fit

```
```









