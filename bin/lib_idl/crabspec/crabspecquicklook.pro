; 
; This function plots
; 
PRO CrabSpecQuickLook, InputFiles, Redshift=Redshift, $
                       SaveEPS=SaveEPS, AxesColor=AxesColor, Color=Color, Thick=Thick, CharSize=CharSize, CharThick=CharThick, $
                       XTitle=XTitle, YTitle=YTitle, Title=Title, XSize=XSize, YSize=YSize, XRange=XRange, YRange=YRange, XStyle=XStyle, YStyle=YStyle, XMargin=XMargin, YMargin=YMargin, $
                       XThick=XThick, YThick=YThick, XTickFormat=XTickFormat, YTickFormat=YTickFormat, XTickInterval=XTickInterval, YTickInterval=YTickInterval, $
                       Continue=Continue, Overplot=Overplot, Close=Close, Fill=Fill, Base=Base, NoData=NoData, Position=Position, $
                       SET_FONT=SET_FONT
    
    ;;
    ;; Read Command Line Arguments
    InputCommandLineArguments = COMMAND_LINE_ARGS(Count=InputCommandLineArgCount)
    IF InputCommandLineArgCount GE 1 THEN BEGIN
        InputFiles = []
        FOR i = 0, InputCommandLineArgCount-1 DO BEGIN
            IF STRMATCH(InputCommandLineArguments[i],'SaveEPS=*',/FOLD_CASE) THEN BEGIN
                SaveEPS = CrabStringReplace(InputCommandLineArguments[i],'SaveEPS=','')
                IF NOT STRMATCH(SaveEPS,'*.eps',/FOLD_CASE) THEN SaveEPS=SaveEPS+'.eps'
            ENDIF ELSE IF STRMATCH(InputCommandLineArguments[i],'XTitle=*',/FOLD_CASE) THEN BEGIN
                XTitle = (CrabStringReplace(InputCommandLineArguments[i],'XTitle=',''))
            ENDIF ELSE IF STRMATCH(InputCommandLineArguments[i],'YTitle=*',/FOLD_CASE) THEN BEGIN
                YTitle = (CrabStringReplace(InputCommandLineArguments[i],'YTitle=',''))
            ENDIF ELSE IF STRMATCH(InputCommandLineArguments[i],'Redshift=*',/FOLD_CASE) THEN BEGIN
                Redshift = Double(CrabStringReplace(InputCommandLineArguments[i],'Redshift=',''))
            ENDIF ELSE BEGIN
                InputFiles = [ InputFiles, InputCommandLineArguments[i] ]
            ENDELSE
        ENDFOR
    ENDIF
    ;; 
    ;; Check input
    IF N_ELEMENTS(InputFiles) EQ 0 AND NOT KEYWORD_SET(Close) THEN BEGIN
        PRINT, 'Usage: CrabSpecQuickLook, ["file_1.dat", "file_2.dat", "file_3.dat"]'
        PRINT, 'Notes: Input files should have at least two columns, first for wavelength for frequency, second for intensity. '
        RETURN
    ENDIF
    ;; 
    ;; Check input if is a STRING
    IF SIZE(InputFiles,/TNAME) NE 'STRING' THEN BEGIN
        MESSAGE, "Error! Please input InputFiles as string types."
        RETURN
    ENDIF
    ;; 
    ;; Check input if is one element
    IF (SIZE(InputFiles))[0] EQ 0 THEN BEGIN
        InputFiless = [InputFiles]
    ENDIF ELSE BEGIN
        InputFiless = InputFiles
    ENDELSE
    ;; 
    ;; Check input file list and search file
    InputFileList = []
    FOR file_id = 0, N_ELEMENTS(InputFiless)-1 DO BEGIN
        TempFileList = FILE_SEARCH(InputFiless[file_id],/TEST_READ)
        IF N_ELEMENTS(TempFileList) EQ 1 THEN BEGIN
            IF TempFileList EQ '' THEN BEGIN
                MESSAGE, 'Error! Could not find the input file "'+InputFiless[file_id]+'"'
                RETURN
            ENDIF
        ENDIF
        InputFileList = [InputFileList, TempFileList]
    ENDFOR
    ;; 
    ;; resolve_routine
    resolve_all
    ;; 
    ;; Prepare Figure
    IF NOT KEYWORD_SET(Overplot) THEN BEGIN
        ; SaveEPS
        IF KEYWORD_SET(SaveEPS) THEN BEGIN
            IF N_ELEMENTS(XSize) EQ 0 THEN XSize = 30.0
            IF N_ELEMENTS(YSize) EQ 0 THEN YSize = 12.0
            OpenPS, SaveEPS, XSize=XSize, YSize=YSize, SET_FONT=SET_FONT
        ENDIF
        ; TVWindow
        IF N_ELEMENTS(TVWindow) EQ 0 THEN TVWindow=1 ELSE TVWindow=FIX(TVWindow)
        IF !D.NAME EQ 'X' OR !D.NAME EQ 'Win' THEN BEGIN
            IF N_ELEMENTS(XSize) EQ 0 THEN XSize = 1200
            IF N_ELEMENTS(YSize) EQ 0 THEN YSize = 400
            IF N_ELEMENTS(TVPosition) NE 2 THEN BEGIN
                Window, TVWindow, XSIZE=XSize, YSIZE=YSize, TITLE=TVTitle 
            ENDIF ELSE BEGIN
                Window, TVWindow, XSIZE=XSize, YSIZE=YSize, TITLE=TVTitle, XPOS=TVPosition[0], YPOS=TVPosition[1]
            ENDELSE
        ENDIF ELSE IF !D.NAME EQ 'PS' THEN BEGIN
            ; already opened eps above
        ENDIF
    ENDIF
    ;; 
    ;; Prepare data array
    NSpectra = 0
    XArrayMinMax = []
    YArrayMinMax = []
    ;; 
    ;; Read input files
    FOR file_id = 0, N_ELEMENTS(InputFileList)-1 DO BEGIN
        XArray = []
        YArray = []
        readcol, InputFileList[file_id], format='(d)', XArray, /SILENT
        readcol, InputFileList[file_id], format='(d,d)', XArray, YArray, /SILENT
        IF N_ELEMENTS(XArray) GT 0 THEN BEGIN
            ;<TODO>
            XArray = XArray * 1e-9 ; Hz -> GHz
            IF N_ELEMENTS(YArray) EQ 0 THEN BEGIN ; if YArray is empty
                YArray = XArray*0.0D
            ENDIF
            ;PRINT, N_ELEMENTS(XArray)
            (SCOPE_VARFETCH(STRING(FORMAT='(A,"_",I0)','XArray',file_id+1),/ENTER)) = XArray
            (SCOPE_VARFETCH(STRING(FORMAT='(A,"_",I0)','YArray',file_id+1),/ENTER)) = YArray
            XArrayMinMax = [XArrayMinMax, CrabMinMax(XArray)]
            YArrayMinMax = [YArrayMinMax, CrabMinMax(YArray)]
            NSpectra = NSpectra + 1
        ENDIF ELSE BEGIN
            MESSAGE, 'Error! Failed to read "'+InputFileList[file_id]+'"'
        ENDELSE
    ENDFOR
    PRINT, 'Read '+STRTRIM(STRING(NSpectra),2)+' Spectra'
    ;; 
    ;; Plot 
    IF N_ELEMENTS(NSpectra) GT 0 THEN BEGIN
        ; Tune YRange
        SetRandomYShifts = REPLICATE(0.0D,NSpectra)
        IF MIN(YArrayMinMax) EQ MAX(YArrayMinMax) THEN BEGIN
            IF YArrayMinMax[0] EQ 0 THEN BEGIN
                YArrayMinMax[1] = YArrayMinMax[0]+1.00
                YArrayMinMax[2] = YArrayMinMax[0]-0.75
                SetRandomYShifts = 1.00*((RANDOMU(!PI,NSpectra)-0.5))
            ENDIF ELSE BEGIN
                YArrayMinMax[1] = YArrayMinMax[0]*1.50
                YArrayMinMax[2] = YArrayMinMax[0]*0.75
                SetRandomYShifts = YArrayMinMax[0]*0.25*((RANDOMU(!PI,NSpectra)-0.5))
            ENDELSE
        ENDIF
        ; Random Color
        IF N_ELEMENTS(Color) EQ 0 THEN BEGIN
            SetRandomColors = 5*((RANDOMU(5*!PI,NSpectra)-0.5))
            SetRandomColors = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        ENDIF
        ; Axes range 
        IF N_ELEMENTS(XStyle) EQ 0 THEN XStyle = 1
        IF N_ELEMENTS(YStyle) EQ 0 THEN YStyle = 1
        ; Thickness
        IF !D.NAME EQ 'PS' THEN BEGIN
            IF N_ELEMENTS(Thick)     EQ 0 THEN Thick_Plot     = 12.0
            IF N_ELEMENTS(XThick)    EQ 0 THEN XThick_Plot    = 3.5
            IF N_ELEMENTS(YThick)    EQ 0 THEN YThick_Plot    = 3.5
            IF N_ELEMENTS(CharThick) EQ 0 THEN CharThick_Plot = 3.25
            IF N_ELEMENTS(CharSize)  EQ 0 THEN CharSize_Plot  = 1.25
            IF N_ELEMENTS(XTickLen)  EQ 0 THEN XTickLen_Plot  = 0.02/!D.Y_SIZE*!D.X_SIZE
            IF N_ELEMENTS(YTickLen)  EQ 0 THEN YTickLen_Plot  = 0.02
        ENDIF ELSE BEGIN
            IF N_ELEMENTS(Thick)     EQ 0 THEN Thick_Plot     = 2.25
            IF N_ELEMENTS(XThick)    EQ 0 THEN XThick_Plot    = 1.25
            IF N_ELEMENTS(YThick)    EQ 0 THEN YThick_Plot    = 1.25
            IF N_ELEMENTS(CharThick) EQ 0 THEN CharThick_Plot = 1.25
            IF N_ELEMENTS(CharSize)  EQ 0 THEN CharSize_Plot  = 2.25
            IF N_ELEMENTS(XTickLen)  EQ 0 THEN XTickLen_Plot  = 0.02/!D.Y_SIZE*!D.X_SIZE
            IF N_ELEMENTS(YTickLen)  EQ 0 THEN YTickLen_Plot  = 0.02
        ENDELSE
        ; Font use
        IF N_ELEMENTS(SET_FONT) NE 0 THEN BEGIN
            Use_Font=1 
        ENDIF ELSE BEGIN
            Use_Font=!NULL
        ENDELSE
        ; Plot box
        ;PRINT, 'PLOT', ' XArrayMinMax=', XArrayMinMax, ' YArrayMinMax=', YArrayMinMax
        PRINT, 'PLOT', ' XRange=', XRange, ' YRange=', YRange
        PLOT, XArrayMinMax, YArrayMinMax, /NODATA, Position=Position, XTitle=XTitle, YTitle=YTitle, XTickFormat=XTickFormat, YTickFormat=YTickFormat, XTickInterval=XTickInterval, YTickInterval=YTickInterval, $
              CharSize=CharSize_Plot, CharThick=CharThick_Plot, Thick=Thick_Plot, XThick=XThick_Plot, YThick=YThick_Plot, XMargin=XMargin, YMargin=YMargin, $
              Color=AxesColor, PSYM=10, Font=Use_Font, XRange=XRange, YRange=YRange, XStyle=XStyle, YStyle=YStyle, XTickLen=XTickLen_Plot, YTickLen=YTickLen_Plot
        ; Plot spec
        IF NOT KEYWORD_SET(NoData) THEN BEGIN
            
            FOR spec_id = 0, NSpectra-1 DO BEGIN
                
                ; Load XArray YArray
                XArray = (SCOPE_VARFETCH(STRING(FORMAT='(A,"_",I0)','XArray',spec_id+1)))
                YArray = (SCOPE_VARFETCH(STRING(FORMAT='(A,"_",I0)','YArray',spec_id+1)))
                ;PRINT, N_ELEMENTS(XArray)
                
                ; Thickness
                IF N_ELEMENTS(Thick) EQ 0 OR N_ELEMENTS(Thick) LE spec_id THEN BEGIN
                     IF !D.NAME EQ 'PS' THEN BEGIN
                         IF N_ELEMENTS(Thick_Plot) EQ 0 THEN Thick_Plot = 2.50
                     ENDIF ELSE BEGIN
                         IF N_ELEMENTS(Thick_Plot) EQ 0 THEN Thick_Plot = 1.50
                     ENDELSE
                 ENDIF ELSE BEGIN
                    Thick_Plot = Thick[spec_id]
                 ENDELSE
                
                ; Thickness
                IF N_ELEMENTS(Color) EQ 0 OR N_ELEMENTS(Color) LE spec_id THEN BEGIN
                    ;Color_Plot = (get_color(100, /random))[SetRandomColors[spec_id]]
                    ;PRINT, SetRandomColors[spec_id], Color_Plot
                    Color_Plot = CrabColorBrewer(spec_id,ColorScheme='201601')
                ENDIF ELSE BEGIN
                    Color_Plot = Color[spec_id]
                ENDELSE
                
                ; Plot spec
                IF KEYWORD_SET(Fill) THEN BEGIN
                    IF N_ELEMENTS(Base) EQ 0 THEN Base=0.0 ; Base=!Y.CRange[0]
                    XArray_Filled = [XArray[0],XArray[0],XArray,XArray[N_ELEMENTS(XArray)-1],XArray[N_ELEMENTS(XArray)-1]]
                    YArray_Filled = [Base,Base,YArray,Base,Base]
                    IF N_ELEMENTS(WHERE(YArray_Filled LT !Y.CRange[0],/NULL)) GT 0 THEN YArray_Filled[WHERE(YArray_Filled LT !Y.CRange[0],/NULL)] = !Y.CRange[0]
                    IF N_ELEMENTS(WHERE(YArray_Filled GT !Y.CRange[1],/NULL)) GT 0 THEN YArray_Filled[WHERE(YArray_Filled GT !Y.CRange[1],/NULL)] = !Y.CRange[1]
                    POLYFILL, XArray_Filled, YArray_Filled, THICK=Thick_Plot/2.0, Color=Color_Plot, NoClip=0
                ENDIF
                
                XArray_Plot = XArray
                YArray_Plot = YArray + SetRandomYShifts[spec_id]
                ;PRINT, !Y.CRange
                ;PRINT, CrabMinMax(YArray_Plot)
                IF N_ELEMENTS(WHERE(YArray_Plot LT !Y.CRange[0],/NULL)) GT 0 THEN YArray_Plot[WHERE(YArray_Plot LT !Y.CRange[0],/NULL)] = !Y.CRange[0]
                IF N_ELEMENTS(WHERE(YArray_Plot GT !Y.CRange[1],/NULL)) GT 0 THEN YArray_Plot[WHERE(YArray_Plot GT !Y.CRange[1],/NULL)] = !Y.CRange[1]
                ;PRINT, 'OPLOT', ' XArray_Plot=', XArray_Plot[0], ' YArray_Plot=', YArray_Plot[0]
                OPLOT, XArray_Plot, YArray_Plot, PSYM=10, THICK=Thick_Plot, COLOR=Color_Plot
                
                ; Legend
                Simplified_Lengend = STRMID(InputFileList[spec_id],STRPOS(STRUPCASE(InputFileList[spec_id]),'SPW'))
                IF STRMATCH(Simplified_Lengend,'*.txt') THEN Simplified_Lengend = STRMID(Simplified_Lengend,0,STRPOS(Simplified_Lengend,'.txt')) ; remove filename suffix
                XYOUTS, XArray_Plot[N_ELEMENTS(XArray_Plot)/2-1], YArray_Plot[N_ELEMENTS(YArray_Plot)/2-1]+(!Y.CRange[1]-!Y.CRange[0])*0.01, $
                        Simplified_Lengend, CHARTHICK=CharThick_Plot, COLOR=Color_Plot, ALIGNMENT=0.5, FONT=Use_Font
                
            ENDFOR
        ENDIF
    ENDIF
    
    ; plot lines
    IF N_ELEMENTS(Redshift) GT 0 THEN BEGIN
        CrabSpecPlotCO, Redshift=Redshift, Color="magenta", CharThick=CharThick_Plot, CharSize=CharSize_Plot/2
        CrabSpecPlotH2O, Redshift=Redshift, Color="cyan", CharThick=CharThick_Plot, CharSize=CharSize_Plot/2
        CrabSpecPlotHCN, Redshift=Redshift, Color="blue", CharThick=CharThick_Plot, CharSize=CharSize_Plot/2
    ENDIF
    
    
    ; Save EPS
    IF !D.NAME EQ 'PS' AND ((NOT KEYWORD_SET(Continue)) OR KEYWORD_SET(Close)) THEN BEGIN
        DEVICE, /CLOSE
        IF STRMATCH(!VERSION.OS,'Win*',/FOLD_CASE) THEN SET_PLOT, 'WIN' ELSE SET_PLOT, 'X'
        PRINT, 'ClosePS: '+SaveEPS
    ENDIF
    
    
END