# Crab.Toolkit.PdBI
Crab Toolkit for NOEMA(PdBI)/ALMA Data Reduction and Analysis

This toolkit contains several useful code to easily deal with NOEMA(PdBI)/ALMA UV table/UV FITS data. 

The scripts in this toolkits are mostly wrappers of the [GILDAS](https://www.iram.fr/IRAMFR/GILDAS) [MAPPING](https://www.iram.fr/IRAMFR/GILDAS/doc/pdf/map.pdf) module's tasks. 
Because GILDAS is interative and usually needs GUI operations, this toolkit can let you run the tasks in command line which is much easier for batch data processing. 


## First of all, add it into your PATH ##

In your BASH shell, 
```
source /path/to/the/downloaded/Crab.Toolkit.PdBI/SETUP.bash
```
This will add the "bin" directory path to your system PATH enviornment, so that you can directly call our scripts from the command line. 

Our script names are like 'pdbi-uvt-go-*'. If you type `pdbi-uvt-go-` in the command line than press your tab key, it should show you those commands. 

Our script usually needs some input arguments. If you type our script name and do not input any argument and press enter, you will get the usage of that script. 

A brief overview of the scripts are in the table below.

| Script name | Description | Arguments |
|-------------|-------------|-----------|
| pdbi-uvt-go-average | Collapse all channel in a uvtable. | -name a.uvt |
| pdbi-uvt-go-clean | Do CLEAN. | -name a.uvt -clean-sigma 4 |
| pdbi-uvt-go-clean-with-mask | Do CLEAN with mask. | -name a.uvt -mask b.fits -clean-sigma 1 |
| pdbi-uvt-go-compress | Bin channels in channel width. | -name a.uvt -width 2 |
| pdbi-uvt-go-merge | Merge uvtables with compatible frequency setups. | -name a.uvt b.uvt c.uvt -out o.uvt |
| pdbi-uvt-go-resample | Resample channels into certain velocity width. | -name a.uvt -width 500 |
| pdbi-uvt-go-shift | Shift the phase center to RA Dec. | -name a.uvt -radec 150.0 2.0 |
| pdbi-uvt-go-uvfit | Perform GILDAS/MAPPING UV_FIT. | -name a.uvt -offset 0 0 -varypos |
|                   |  | -name a.uvt -radec 150.0 2.0 -fixpos |
| pdbi-uvt-go-uvmap | Make a dirty image. | -name a.uvt -size -map_size |
| pdbi-uvt-go-subtract | Subtract a uvtable (b) e.g. as continuum from another (a). | -name a.uvt b.uvt -out o.uvt |


## Use this code to do an UV_FIT (uv-plane source fitting) ##

One of the most important task is probably the GILDAS/MAPPING UV_FIT, which performs uv-plane source fitting. If the data has multiple channels, then the source fitting is done channel by channel, and in the end you will get a table containing all the fluxes and channel frequencies, i.e., a spectrum. 

Our `pdbi-uvt-go-uvfit` script can do uv_fit easily with a large flexibility! 
Below are some examples. You can try these commands with our test uvtable file in the "test" directory. 

```
mkdir -p test/test_uv_fit
cd test/test_uv_fit
cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt

# fit point source model at the phase center, allow source position to vary.
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -out OUTPUTNAME \

# fit point source model at a fixed position of (0,0) arcsec offset from the phase center.
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -offset 0 0 -fixpos \
                  -out OUTPUTNAME

# fit point source model at a fixed position of (0,0) arcsec offset from the phase center.
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -offset 0 0 -fixpos \
                  -out OUTPUTNAME

# fit circular Gaussian source model at a fixed position of RA Dec 150.0351 2.01330 (only support J2000), in default we allow size to vary, unless you specify -size NNN -fixsize.
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -radec 150.0351 2.01330 -fixpos -cgauss \
                  -out OUTPUTNAME

# fit an elliptical Gaussian source model at a fixed position of RA Dec 150.0351 2.01330, fix major and minor FWHM size 0.9 0.7 arcsec and position angle 90 degree.
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -radec 150.0351 2.01330 -fixpos -size 0.9 0.7 -fixsize -angle 90 -fixangle -egauss \
                  -out OUTPUTNAME

# we can specify a field of view with "-FoV", so that the code will output "OUTPUTNAME.result.obj_*.image.pdf". 
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -radec 150.0351 2.01330 -fixpos -size 0.9 0.7 -fixsize -angle 90 -fixangle -egauss \
                  -FoV 10 \
                  -out OUTPUTNAME

# we can input multiple sources, then the output will be "OUTPUTNAME.result.obj_*.txt" and ""
pdbi-uvt-go-uvfit -name NAME.uvt \
                  -radec 150.0351 2.01330 -fixpos -size 0.9 0.7 -fixsize -angle 90 -fixangle -egauss \
                  -offset 3.0 3.0 -fixpos \
                  -offset -6.0 6.0 -fixpos \
                  -FoV 10 \
                  -out OUTPUTNAME
```

Note that for running 'pdbi-uvt-go-uvfit' in a current best mode, you might want to install supermongo ... --> 2018-02-12 no need, now we have python code for plotting the spectrum! 

Note that GILDAS MAPPING has a different definition of angle versus position angle, our code should already be taking care of that. So your input -angle is just the position angle starting from +North direction and increases counter-clockwise. 



## Other scripts ##

Our 'pdbi-uvt-go-*' commands can process uvtable data in a batch mode by calling the [GILDAS MAPPING](https://www.iram.fr/IRAMFR/GILDAS/) tasks without invoking the GUI. 

'pdbi-uvt-go-splitpolar' can average two polarization (stokes). For example, 

```
mkdir -p test/test_1_splitpolar
cd test/test_1_splitpolar
cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME.uvt
pdbi-uvt-go-splitpolar -name NAME.uvt -out OUTPUTNAME
```

'pdbi-uvt-go-merge' can merge two UV tables. For example, 

```
mkdir -p test/test_2_uvmerge
cd test/test_2_uvmerge
cp ../uv_table_data/split_z35_68_spw0_width128.uvt NAME_1.uvt
cp ../uv_table_data/split_z35_68_spw1_width128.uvt NAME_2.uvt
pdbi-uvt-go-merge -name NAME_1.uvt NAME_2.uvt -out OUTPUTNAME
# we can also specify relative weighting, e.g., 
pdbi-uvt-go-merge -name NAME_1.uvt NAME_2.uvt -out OUTPUTNAME -weighting 5.0 12.0
```

'pdbi-uvt-go-average' can average UV table channels and make a single channel UV table, which is just continuum data. For example, 

```
mkdir -p test/test_3_uvaverage
cd test/test_3_uvaverage
cp ../uv_table_data/split_VUDS0510807732_spw1_width10_SP.uvt NAME.uvt
pdbi-uvt-go-average -name NAME.uvt -out OUTPUTNAME
# we can specify channel range '-crange MM NN', or velocity range '-vrange MM NN', or frequency range '-frange MM NN'.
pdbi-uvt-go-average -name NAME.uvt -crange 2 5 -out OUTPUTNAME
pdbi-uvt-go-average -name NAME.uvt -vrange -400 400 -out OUTPUTNAME
```

'pdbi-uvt-go-compress' (TODO)

'pdbi-uvt-go-resample' (TODO)

'pdbi-uvt-go-shift' (TODO)

'pdbi-uvt-go-subtract' (TODO)

'pdbi-uvt-go-uvmap' (TODO)



## Deal with ALMA Measurement Sets? ##

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




## Deal with GILDAS UV table (older manual, before 2018-02-12) ##

First split polarization:
```
pdbi-uvt-go-splitpolar -name MY_UV_table.uvt -out MY_UV_table_output.uvt
```

Then run uv_fit at the phase center:
```
pdbi-uvt-go-uvfit-v3 -name "ID-6406-1mm" -fixpos -point -out "ID-6406-1mm.uvt.uvfit.P.FixedPos"
pdbi-uvt-go-uvfit-v3 -name "ID-6406-1mm" -varypos -point -out "ID-6406-1mm.uvt.uvfit.P.VariedPos"
pdbi-uvt-go-uvfit-v3 -name "ID-6406-1mm" -varypos -cgauss -out "ID-6406-1mm.uvt.uvfit.C.VariedPos"
pdbi-uvt-go-uvfit-v3 -name "ID-6406-1mm" -varypos -egauss -out "ID-6406-1mm.uvt.uvfit.G.VariedPos"
```
The output fitting log file will be "ID-6406-1mm.uvt.uvfit.P.VariedPos.log", and the output data table will be "ID-6406-1mm.uvt.uvfit.P.VariedPos.uvfit.obj_1.txt". 

Or run uv_fit for multiple source by giving the "-radec" argument list:
```
pdbi-uvt-go-uvfit-v3 -name "ID-6406-1mm" -radec 12:01:56.0 55:55:55.0 -fixpos -point \
                                         -radec 12:02:56.0 55:55:55.0 -fixpos -egauss \
                                         -radec 12:03:56.0 55:55:55.0 -fixpos -egauss \
                                         -out "Output_filename"
```
The output fitting log file will be "Output_filename.log", and the output data table will be "Output_filename.uvfit.obj_1.txt".   



## More examples for uv_fit ##

Fix circular Gaussian size for uv_fit

```
pdbi-uvt-go-uvfit-v3 -name "ID-6406-1mm" \
                                         -radec 12:02:56.0 55:55:55.0 -fixpos -size 1.0 -fixsize -cgauss \
                                         -radec 12:03:56.0 55:55:55.0 -fixpos -size 1.0 0.75 -fixsize -angle 0 -fixangle -egauss \
                                         -out "Output_filename"
```
The output fitting log file will be "Output_filename.log", and the output data table will be "Output_filename.uvfit.obj_1.txt" and "Output_filename.uvfit.obj_2.txt". 
We also output spectrum figures as "Output_filename.plotfit.obj_1.eps". 





## What is this code actually doing? ##

The core idea of the scripts in this toolkit is: first creating a "\*.init" file according to the user inputs, which is needed by each GILDAS/MAPPING task, then generating a simple script "\*.script" that calls the GILDAS/MAPPING task with the "\*.init" file, then launchs the GILDAS/MAPPING main executable in a no-window, no-logging mode to run the "\*.scrpit" file:

```
echo "aaa.script" | mapping -nw -nl
```

If you have added the `-keep-files` argument when you call our script in the command line, you should get the "\*.init" and "\*.script" file saved on the disk. You can view the contents, and run it in GILDAS/MAPPING environment by yourself:

```
# Launch the GILDAS/MAPPING GUI
mapping 
! now I'm in the GILDAS/MAPPING environment
! I'll try to run the "aaa.script" here
@aaa.script
```














