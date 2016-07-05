PRO PdBI_UVT_Super_Combine_SPW, InputDataFiles, OutputDataFile
    
    ; idl
    ; .compile '/home/dzliu/Cloud/Github/Crab.Toolkit/ds9/pdbi_uvt_super_combine_spw.pro'
    
    ; TODO 
    ; Stokes Number could not be determined from 512-header!
    
    ; TODO
    ; Check (u,v,w) then concat spw channels
    ; need a lot of work to do
    
    ;InputDataFiles = ['a12345_spw37.uvt','a12345_spw38.uvt']
    ;OutputDataFile = 'test_out.uvt'
    
    ;!EXCEPT=2
    PRINT, 'Welcome'
    
    ; Read Command Line Arguments
    InputCommandLineArguments = COMMAND_LINE_ARGS(Count=InputCommandLineArgCount)
    ;PRINT, InputCommandLineArguments, InputCommandLineArgCount
    IF InputCommandLineArgCount GE 2 THEN BEGIN
    	InputDataFiles = []
    	FOR i = 0, InputCommandLineArgCount-1-1 DO BEGIN
    		InputDataFiles = [ InputDataFiles, InputCommandLineArguments[i] ]
    	ENDFOR
    	OutputDataFile = InputCommandLineArguments[InputCommandLineArgCount-1]
    	;PRINT, InputDataFiles, OutputDataFile
    ENDIF
    ;RETURN
    
    ; 
    IF N_ELEMENTS(InputDataFiles) EQ 0 OR N_ELEMENTS(OutputDataFile) EQ 0 THEN BEGIN
        PRINT, 'Usage: PdBI_UVT_Super_Combine_SPW, InputDataFiles, OutputDataFile'
        RETURN
    ENDIF
    
    ; Check input files
    FOR i=0,N_ELEMENTS(InputDataFiles)-1 DO BEGIN
        IF NOT STRMATCH(InputDataFiles[i],'*.uvt') THEN BEGIN
            InputDataFiles[i] = InputDataFiles[i]+'.uvt'
        ENDIF
        IF NOT FILE_TEST(InputDataFiles[i],/READ) THEN BEGIN
            MESSAGE, 'Error! Could not read "'+InputDataFiles[i]+'"'
        ENDIF
    ENDFOR
    
    ; Check output file
    IF NOT STRMATCH(OutputDataFile,'*.uvt',/FOLD_CASE) THEN BEGIN
    	OutputDataFile = OutputDataFile+'.uvt'
    ENDIF
    
    ; Loop input files, read uvt header, determine UVT_channel_shape
    UVT_head_list = []
    UVT_data_list = []
    CheckSpecChannelIncrement = 0.0D
    UVT_channel_shape = {MinFrequency:!VALUES.D_NAN, MaxFrequency:!VALUES.D_NAN, Increment:!VALUES.D_NAN, Dimension:0L, $
    	                 RefChannel=0.0D, RefFrequency=0.0D, 
    	                 Channels:PTR_NEW(/ALLOCATE_HEAP), Frequencies:PTR_NEW(/ALLOCATE_HEAP)}
    FOR i=0,N_ELEMENTS(InputDataFiles)-1 DO BEGIN
        ; 
        ; create UVT head structure
        UVT_head = {Pointer:PTR_NEW(/ALLOCATE_HEAP), Bytes:PTR_NEW(/ALLOCATE_HEAP), File: InputDataFiles[i], Size:0L, $
                    NAXIS1:0L, NAXIS2:0L, CRPIX1:0.0D, CRPIX2:0.0D, CRVAL1:0.0D, CRVAL2:0.0D, CDELT1:0.0D, CDELT2:0.0D, $
                    ChannelNumber:0L, StokesNumber:0, VisibilityNumber:0L, $
                    Channels:PTR_NEW(/ALLOCATE_HEAP), Frequencies:PTR_NEW(/ALLOCATE_HEAP), Stokes:PTR_NEW(/ALLOCATE_HEAP)}
        ; 
        ; open UVT 
        OPENR, TempFilePointer, InputDataFiles[i], /GET_LUN
        ; 
        ; read first 512 bytes and determine the header size
        TempByteHeader = BYTARR(512)
        READU, TempFilePointer, TempByteHeader
        ; 
        ; determine the header type and read more if header is 1024 bytes
        IF STRING(TempByteHeader[232:232+6]) EQ 'UV-DATA' THEN BEGIN
              UVT_head.Size = 512
            (*UVT_head.Bytes) = BYTARR(UVT_head.Size)
            (*UVT_head.Bytes) = TempByteHeader[0:512-1]
              UVT_head.NAXIS1 = (LONG((*UVT_head.Bytes)[048:048+3],0))   ; long int, 4 bytes
              UVT_head.NAXIS2 = (LONG((*UVT_head.Bytes)[052:052+3],0))   ; long int, 4 bytes
              UVT_head.CRPIX1 = (DOUBLE((*UVT_head.Bytes)[064:064+7],0)) ; double, 8 bytes
              UVT_head.CRVAL1 = (DOUBLE((*UVT_head.Bytes)[072:072+7],0)) ; double, 8 bytes
              UVT_head.CDELT1 = (FLOAT((*UVT_head.Bytes)[084:084+3],0))  ; float, 4 bytes
              UVT_head.ChannelNumber = (LONG((*UVT_head.Bytes)[048:048+3],0)-7)/3 ; 048 long int 4 bytes ; NAXIS1 Size of Each Visibility, in unit of 4 bytes
                                                                                                         ; Stokes Number ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO
                                                                                                         ; Stokes Number ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO
              UVT_head.StokesNumber = (LONG((*UVT_head.Bytes)[432:432+3],0))      ; 431 long int 4 bytes ; Stokes Number ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO
                                                                                                         ; Stokes Number ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO
                                                                                                         ; Stokes Number ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO ??? TODO
              UVT_head.VisibilityNumber = UVT_head.NAXIS2
        ENDIF ELSE IF STRING(TempByteHeader['164'xL:'164'xL+6]) EQ 'UV-DATA' THEN BEGIN
            UVT_GDFBIG_re_allocation = FIX(TempByteHeader['018'xL:'018'xL+1],0) ; some ALMA converted uvt has a "I-GIO_RIH, GDFBIG re-allocation 3", i.e. 1536 bytes header. 
            ;PRINT, 'UVT_GDFBIG_re_allocation: ', UVT_GDFBIG_re_allocation
            UVT_head.Size = 512*UVT_GDFBIG_re_allocation
            (*UVT_head.Bytes) = BYTARR(UVT_head.Size)
            FOR hi=1,UVT_GDFBIG_re_allocation DO BEGIN
                (*UVT_head.Bytes)[512*(hi-1):512*hi-1] = TempByteHeader[0:512-1] & IF hi LT UVT_GDFBIG_re_allocation THEN READU, TempFilePointer, TempByteHeader
            ENDFOR
            UVT_head.NAXIS1 = (LONG((*UVT_head.Bytes)['050'xL:'050'xL+3],0))        ; long int, 4 bytes
            UVT_head.NAXIS2 = (LONG((*UVT_head.Bytes)['058'xL:'058'xL+3],0))        ; long int, 4 bytes
            UVT_head.CRPIX1 = (DOUBLE((*UVT_head.Bytes)['0A8'xL:'0A8'xL+7],0))      ; double, 8 bytes
            UVT_head.CRVAL1 = (DOUBLE((*UVT_head.Bytes)['0B0'xL:'0B0'xL+7],0))      ; double, 8 bytes
            UVT_head.CDELT1 = (DOUBLE((*UVT_head.Bytes)['0B8'xL:'0B8'xL+7],0))      ; double, 8 bytes
            UVT_head.ChannelNumber = (LONG((*UVT_head.Bytes)['2D4'xL:'2D4'xL+3],0)) ; 0x2D4 long int 4 bytes ; Channel Number
            UVT_head.StokesNumber = (LONG((*UVT_head.Bytes)['2E0'xL:'2E0'xL+3],0))  ; 0x2E0 long int 4 bytes ; Stokes Number
            UVT_head.VisibilityNumber = UVT_head.NAXIS2
            ;PRINT, UVT_head.NAXIS1, UVT_head.NAXIS2, UVT_head.ChannelNumber, UVT_head.StokesNumber
            ;PRINT, *UVT_head.Bytes
        ENDIF ELSE BEGIN
            MESSAGE, 'Error! Input data file "'+InputDataFiles[i]+'" has wrong UV-DATA type!'
        ENDELSE
        ; 
        ; Save 
        ;PRINT, 'Reading "'+InputDataFiles[i]+'" (header,channels,stokes) ', [UVT_head.Size, UVT_head.ChannelNumber, UVT_head.StokesNumber]
        PRINT, 'Reading ------------------------------------------------------------------------------------------------------ '+'"'+InputDataFiles[i]+'"'
        *(UVT_head.Pointer) = TempFilePointer
        
        ; 
        ; <TEST> Skip some UNKNOWN bytes ??!! -- Perhaps it's because of the /STYLE CASA!
        ;;IF InputDataFiles[i] EQ 'test_ALMA_2012.1.00175.S_Eyelash_spw4.uvt' THEN BEGIN
        ;;    TempByteArray = BYTARR(512) ; 128*4bytes??!!
        ;;    READU, *(UVT_head.Pointer), TempByteArray
        ;;ENDIF
        ;;IF InputDataFiles[i] EQ 'test_ALMA_2012.1.00175.S_Eyelash_spw4_spolar.uvt' THEN BEGIN
        ;;   ;TempByteArray = BYTARR(0) ; 128*4bytes??!!
        ;;   ;READU, *(UVT_head.Pointer), TempByteArray
        ;;ENDIF
        
        ; 
        ; Read first data block of visibility and have a look
        TempDataBlock = {UVW:FLTARR(3),Date:FLTARR(1),Time:FLTARR(1),Antennae:FLTARR(2),Data:FLTARR(3,UVT_head.StokesNumber*UVT_head.ChannelNumber)} ; BYTARR(4*(7+3*HeadStokes*HeadChanns))
        READU, *(UVT_head.Pointer), TempDataBlock
        ;HELP, TempDataBlock
        ;PRINT, TempDataBlock
        ;PRINT, 'Reading "'+InputDataFiles[i]+'" (u,v,w,ant1,ant2,block) ', [TempDataBlock.UVW, TempDataBlock.Antennae, UVT_head.StokesNumber*UVT_head.ChannelNumber*3]
        ;PRINT, 'Reading "'+InputDataFiles[i]+'" (u,v,w,ant1,ant2,data) ', [REFORM(TempDataBlock.UVW), REFORM(TempDataBlock.Antennae), REFORM(TempDataBlock.Data[0,0:2])]
        ;<20160626> checked with pdbi-uvt-to-fits.cpp, working quite well. 
        ;<20160626> and this IDL code can determine header type automatically! Data block is also well defined!
        ;BREAK
        
        ; 
        ; Check Axis 1 Channel-Frequency Axis
        ;PRINT, 'Reading "'+InputDataFiles[i]+'" (cr,c1,cf,c2,cd) ', UVT_head.CRVAL1, 1.0, UVT_head.CRPIX1, FLOAT(UVT_head.ChannelNumber), UVT_head.CDELT1
        TempChanArray = DINDGEN(UVT_head.ChannelNumber)+1
        TempFreqArray = (TempChanArray-UVT_head.CRPIX1)*UVT_head.CDELT1+UVT_head.CRVAL1 ; <NOTE> unit is MHz, GILDAS standard
        (*UVT_head.Channels) = TempChanArray
        (*UVT_head.Frequencies) = TempFreqArray
        FOR ci=0,2 DO BEGIN
            PRINT, FORMAT='(A20,I8,A20,F16.4,A20,F12.4)', 'Channel', TempChanArray[ci], 'Frequency', TempFreqArray[ci], 'Increment', DOUBLE(UVT_head.CDELT1)
        END
        FOR ci=9,9 DO BEGIN
            PRINT, FORMAT='(A20,A8,A20,A16,A20,A12)', 'Channel', '...', 'Frequency', '...', 'Increment', '...'
        END
        FOR ci=N_ELEMENTS(TempChanArray)-3,N_ELEMENTS(TempChanArray)-1 DO BEGIN
            PRINT, FORMAT='(A20,I8,A20,F16.4,A20,F12.4)', 'Channel', TempChanArray[ci], 'Frequency', TempFreqArray[ci], 'Increment', DOUBLE(UVT_head.CDELT1)
        END
        
        ; 
        ; <TODO>
        ; now the situation is, we need to combine spw
        ; (1) spw with similar frequency coverage but channels are shifted
        ; (2) spw with different frequency coverage, we put them in one uvt for better 
        
        ; 
        ; Check Spec Channel Increment
        IF NOT FINITE(UVT_channel_shape.Increment) THEN BEGIN
        	UVT_channel_shape.Increment = UVT_head.CDELT1
        	UVT_channel_shape.MinFrequency = MIN(TempFreqArray)
        	UVT_channel_shape.MaxFrequency = MAX(TempFreqArray)
        ENDIF ELSE BEGIN
            IF ABS(UVT_channel_shape.Increment-UVT_head.CDELT1) LE 1E-3 THEN BEGIN
            	; OK, Channel Increment is consistent, 
            	; now determien channel shape MinFrequency MaxFrequency
        	    UVT_channel_shape.MinFrequency = MIN([UVT_channel_shape.MinFrequency,TempFreqArray])
        	    UVT_channel_shape.MaxFrequency = MAX([UVT_channel_shape.MaxFrequency,TempFreqArray])
            ENDIF ELSE BEGIN
                PRINT, "Error! Channel Increment is inconsistent! Previous value "+STRING(FORMAT='(F0.6)',UVT_channel_shape.Increment)+$
                       " but current value "+STRING(FORMAT='(F0.6)',UVT_head.CDELT1)+" in "+InputDataFiles[i]+"."
                RETURN
            ENDELSE
        ENDELSE
        
        ; 
        ; Store into UVT_head_list
        UVT_head_list = [ UVT_head_list, UVT_head ]
        
        
    ENDFOR
    
    ; Loop input files, read uvt header, plot new channel shape
    FOR i=0,N_ELEMENTS(InputDataFiles)-1 DO BEGIN
    	UVT_head = UVT_head_list[i]
        TempChanArray = (*UVT_head.Channels)
        TempFreqArray = (*UVT_head.Frequencies)
        ; Plot the channels
        IF i EQ 0 THEN BEGIN
        	PlotDevice = PLOT(TempFreqArray, TempFreqArray*0, YRANGE=[-UVT_head.ChannelNumber/5,UVT_head.ChannelNumber/5*N_ELEMENTS(InputDataFiles)], /NODATA)
        ENDIF
        PlotDevice = PLOT(TempFreqArray, TempFreqArray*0+double(i)*0.5, Symbol='+', Sym_Size=3, /OVERPLOT, COLOR=CrabColorBrewer(i,ColorScheme='201601'))
    ENDFOR
    TempFreqArray = CrabArrayIndGen(UVT_channel_shape.MinFrequency, UVT_channel_shape.MaxFrequency, UVT_channel_shape.Increment)
    TempChanArray = DINDGEN(N_ELEMENTS(TempFreqArray))
    UVT_channel_shape.Dimension = N_ELEMENTS(TempFreqArray)
    *UVT_channel_shape.Channels = TempChanArray
    *UVT_channel_shape.Frequencies = TempFreqArray
    UVT_channel_shape.RefChannel = DOUBLE(LONG(UVT_channel_shape.Dimension/2)+1)
    UVT_channel_shape.RefFrequency = TempFreqArray[WHERE(TempChanArray EQ LONG(UVT_channel_shape.Dimension/2)+1)]
    PlotDevice = PLOT(TempFreqArray, TempFreqArray*0-0.5, Symbol='+', Sym_Size=3, THICK=2, /OVERPLOT, COLOR='magenta')
    
    
    
    
    ; Prepare output file, pack float into byte array http://www.idlcoyote.com/code_tips/packfloat.php
    UVT_head = UVT_head_list[0]
    UVT_head_bytes = *UVT_head.Bytes
    IF UVT_head.Size EQ 512 THEN BEGIN
    	UVT_head_bytes[048:048+3] = BYTE(UVT_channel_shape.Dimension,    0, 4, 1) ; NAXIS1 ; long int, 4 bytes
    	UVT_head_bytes[064:064+7] = BYTE(UVT_channel_shape.RefChannel,   0, 8, 1) ; CRPIX1 ; double, 8 bytes
    	UVT_head_bytes[072:072+7] = BYTE(UVT_channel_shape.RefFrequency, 0, 8, 1) ; CRVAL1 ; double, 8 bytes
    ENDIF ELSE BEGIN
    	UVT_head_bytes['050'xL:'050'xL+3] = BYTE(UVT_channel_shape.Dimension,    0, 4, 1) ; NAXIS1 ; long int, 4 bytes
    	UVT_head_bytes['0A8'xL:'0A8'xL+7] = BYTE(UVT_channel_shape.RefChannel,   0, 8, 1) ; CRPIX1 ; double, 8 bytes
    	UVT_head_bytes['0B0'xL:'0B0'xL+7] = BYTE(UVT_channel_shape.RefFrequency, 0, 8, 1) ; CRVAL1 ; double, 8 bytes
    ENDELSE
    ;OPENW, OutputFilePointer, OutputDataFile, /GET_LUN
    ;WRITEU, OutputFilePointer, UVT_head_bytes
    
    
    ; Loop input files, read each visibility and resample to new channel shape
    FOR i=0,N_ELEMENTS(InputDataFiles)-1 DO BEGIN
    	UVT_head = UVT_head_list[i]
    	; Rewind
    	POINT_LUN, *(UVT_head.Pointer), (UVT_head.Size)
    	; Read data block
    	TempDataBlock = {UVW:FLTARR(3),Date:FLTARR(1),Time:FLTARR(1),Antennae:FLTARR(2),Data:FLTARR(3,UVT_head.StokesNumber*UVT_head.ChannelNumber)} ; BYTARR(4*(7+3*HeadStokes*HeadChanns))
    	TempDataBlockNew = {UVW:FLTARR(3),Date:FLTARR(1),Time:FLTARR(1),Antennae:FLTARR(2),Data:FLTARR(3,UVT_channel_shape.Dimension)} ; BYTARR(4*(7+3*HeadStokes*HeadChanns))
    	
    	FOR j = 0, UVT_head.VisibilityNumber-1 DO BEGIN
    		READU, *(UVT_head.Pointer), TempDataBlock
    		TempDataBlockNew.UVW = TempDataBlock.UVW
    		TempDataBlockNew.Date = TempDataBlock.Date
    		TempDataBlockNew.Time = TempDataBlock.Time
    		TempDataBlockNew.Antennae = TempDataBlock.Antennae
    		TempDataBlockNew.Data[] = TempDataBlock.Data[] ;#<TODO># h%gil%order = code_stok_chan or code_chan_stok ??? --- http://cdsweb.u-strasbg.fr/vizier/doc/man/gildas/pdf/sic-gdfv2.pdf
    		           ;<TODO>;
    		           ;<TODO>;
    		           ;<TODO>;
    		           ;<TODO>; 
    		                  ; Actually super-combine-spw will lead to a hell lot of blank data, making the data two times larger! Really not a wise option!
    		                  ; So I'll leave the code here. Will not continue trying to do super-combine-spw. 
    		                  ; dzliu 20160704 01:27 UTC+8 
    		           ;<TODO>;
    		           ;<TODO>;
    		           ;<TODO>;
    		           ;<TODO>;
    	ENDFOR
    	;<TODO> use data block arary to speed up
    	;TempDataBlockIncrement = 1
    	;FOR j = 0, UVT_head.VisibilityNumber-1, TempDataBlockIncrement DO BEGIN
    	;	TempDataBlockArray = REPLICATE(TempDataBlock, TempDataBlockIncrement)
    	;	READU, *(UVT_head.Pointer), TempDataBlockArray
    	;ENDFOR
        
        ;<TODO><DEBUG>;
        BREAK
        
    ENDFOR
    
    
    ; Close input files
    FOR i=0,N_ELEMENTS(InputDataFiles)-1 DO BEGIN
    	UVT_head = UVT_head_list[i]
        CLOSE, *(UVT_head.Pointer)
        FREE_LUN, *(UVT_head.Pointer)
    ENDFOR
    ;CLOSE, OutputFilePointer
    ;FREE_LUN, OutputFilePointer
    
    
    ; Wait for confirmation to exit
    ;Read, PROMPT='Ready to leave?', ReadyToLeave
    
END
