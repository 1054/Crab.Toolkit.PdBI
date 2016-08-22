; 
; This function read a data cube
; 
PRO CrabSpecReadCube, InputSpecCube
    
    InputSpecCube = '/Users/dliu/Working/SpireLines/Data/DataRelease/2013-05-31/ListOfSourcesPart3/CenA/spec/SPIRE_FTS_SOF2/1342204036_HR_SLW_unapod_Extended_preCube.fits'
    
    IF NOT FILE_TEST(InputSpecCube) THEN BEGIN
        MESSAGE, 'CrabSpecReadCube: Data does not exist! Please check '+InputSpecCube
    ENDIF
    
    FITS_INFO, InputSpecCube, EXTNAME=TotExtName, N_EXT=TotExtNumb, SILENT=Silent
    
    FOR GotExtNumb=0,TotExtNumb-1 DO BEGIN
        GotExtData = MRDFITS(InputSpecCube,GotExtNumb,GotExtHeader)
        IF STRUPCASE(FXPAR(GotExtHeader,'XTENSION')) EQ 'BINTABLE' THEN BREAK
    ENDFOR
    
    ; Now we got GotExtData and GotExtHeader
    
    
    
    PRINT, 'debug'
    
    RETURN
    
END