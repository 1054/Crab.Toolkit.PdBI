PRO lab_spec_lines_optical, LineNamePattern, LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, LineRedshift=LineRedshift, $
                            NOPLOT=NOPLOT, PlotWavelength=PlotWavelength, PlotLineStyle=PlotLineStyle, PlotColor=PlotColor, PlotYRange=PlotYRange
    
    IF N_ELEMENTS(LineNamePattern) EQ 0 THEN BEGIN
        PRINT, 'Usage:'
        PRINT, '    lab_spec_lines_optical, "O|N|S", LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, /NoPlot'
        PRINT, '    '
        RETURN
    ENDIF
    
    LabLineData = [ { Name:"[OIII]88um",   Freq: 3393.00624 } , $
                    { Name:"[OIII]51um",   Freq: 5785.87959 } , $
                    { Name:"[CII]158um",   Freq: 1900.53690 } , $
                    { Name:"[SII]6731A",   Freq: 2.99792458e5/6730.820e-4 } , $
                    { Name:"[SII]6716A",   Freq: 2.99792458e5/6716.440e-4 } , $
                    { Name:"[NII]6583A",   Freq: 2.99792458e5/6583.450e-4 } , $
                    { Name:"Halpha_6563A", Freq: 2.99792458e5/6562.801e-4 } , $
                    { Name:"[NII]6548A",   Freq: 2.99792458e5/6548.050e-4 } , $
                    { Name:"[OIII]5007A",  Freq: 2.99792458e5/5006.843e-4 } , $
                    { Name:"[OIII]4959A",  Freq: 2.99792458e5/4958.911e-4 } , $
                    { Name:"Hbeta_4861A",  Freq: 2.99792458e5/4861.363e-4 } , $
                    { Name:"[OII]3727A",   Freq: 2.99792458e5/3727.e-4    }   ]
    
    LineMatch = STREGEX(LabLineData.Name, LineNamePattern, /BOOLEAN)
    ;PRINT, LineMatch
    
    IF N_ELEMENTS(WHERE(LineMatch, /NULL)) EQ 0 THEN BEGIN
        MESSAGE, "No line found with line name pattern "+LineNamePattern, /CONTINUE
        RETURN
    ENDIF
    
    LineNameList = (LabLineData.Name)[WHERE(LineMatch)]
    LineFreqList = (LabLineData.Freq)[WHERE(LineMatch)] ; GHz ; <bug><fixed><20160118><dzliu> must have round brackets
    LineWaveList = 299.792458/LineFreqList ; mm
    
    
    
    IF NOT KEYWORD_SET(NOPLOT) THEN BEGIN
        IF !X.CRANGE[1] GT !X.CRANGE[0] AND !Y.CRANGE[1] GT !Y.CRANGE[0] THEN BEGIN
            LinePlotXLength = !X.CRANGE[1] - !X.CRANGE[0]
            LinePlotYLength = !Y.CRANGE[1] - !Y.CRANGE[0]
            LinePlotYRange = [!Y.CRANGE[1] - 0.55*LinePlotYLength, !Y.CRANGE[1] - 0.02*LinePlotYLength]
            IF N_ELEMENTS(PlotYRange) EQ 2 THEN BEGIN
            LinePlotYRange = [!Y.CRANGE[0] + PlotYRange[0]*LinePlotYLength, !Y.CRANGE[0] + PlotYRange[1]*LinePlotYLength]
            ENDIF
            IF !D.NAME EQ 'PS' THEN LinePlotThick = 4.0 ELSE LinePlotThick = 2.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharThick = 4.0 ELSE LinePlotCharThick = 2.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharSize = 0.8 ELSE LinePlotCharSize = 1.2
            
            MESSAGE, "Labelling "+STRING(FORMAT='(I0)',N_ELEMENTS(LineFreqList))+" spec line names", /CONTINUE
            
            ; line redshift
            IF N_ELEMENTS(LineRedshift) EQ 0 THEN BEGIN
                LineRedshift = 0.0
            ENDIF
            
            FOR LinePlotIndex=0,N_ELEMENTS(LineFreqList)-1 DO BEGIN
                
                IF LinePlotIndex LE N_ELEMENTS(PlotColor)-1 THEN LinePlotColor=PlotColor[LinePlotIndex] ELSE LinePlotColor='FF00FF'xL
                
                IF N_ELEMENTS(PlotColor) EQ 1 THEN LinePlotColor=PlotColor
                
                IF N_ELEMENTS(PlotLineStyle) EQ 0 THEN PlotLineStyle = 1
                
                IF KEYWORD_SET(PlotWavelength) THEN BEGIN
                    ; wavelength unit default is mm, but can set PlotWavelength = 1e-10 to plot Angstrom
                    UnitWavelength = DOUBLE(PlotWavelength)*1e3 ; default is mm
                    XYOUTS, 0, 0, LineNameList[LinePlotIndex]+' ', FONT=1, CHARSIZE=-1, WIDTH=TextStw & TextPlotYRange = [LinePlotYRange[0],LinePlotYRange[1]-TextStw*1.09*LinePlotYLength*!D.X_SIZE/!D.Y_SIZE]
                    PLOTS, [LineWaveList[LinePlotIndex]*(1.0+LineRedshift)/UnitWavelength,$
                            LineWaveList[LinePlotIndex]*(1.0+LineRedshift)/UnitWavelength],LinePlotYRange, LINESTYLE=PlotLineStyle, COLOR=LinePlotColor, Thick=LinePlotThick
                    XYOUTS, LineWaveList[LinePlotIndex]*(1.0+LineRedshift)/UnitWavelength, LinePlotYRange[1], LineNameList[LinePlotIndex], ALIGNMENT=1.0, ORIENTATION=90, FONT=1, $
                            CHARSIZE=LinePlotCharSize, CHARTHICK=LinePlotCharThick, COLOR=LinePlotColor, /NOCLIP
                ENDIF ELSE BEGIN
                    UnitFrequency = DOUBLE(1.0) ; default is GHz
                    XYOUTS, 0, 0, LineNameList[LinePlotIndex]+' ', FONT=1, CHARSIZE=-1, WIDTH=TextStw & TextPlotYRange = [LinePlotYRange[0],LinePlotYRange[1]-TextStw*1.09*LinePlotYLength*!D.X_SIZE/!D.Y_SIZE]
                    PLOTS, [LineFreqList[LinePlotIndex]/(1.0+LineRedshift)/UnitFrequency,$
                            LineFreqList[LinePlotIndex]/(1.0+LineRedshift)/UnitFrequency], LinePlotYRange, LINESTYLE=PlotLineStyle, COLOR=LinePlotColor, Thick=LinePlotThick
                    XYOUTS, LineFreqList[LinePlotIndex]/(1.0+LineRedshift)/UnitFrequency, LinePlotYRange[1], LineNameList[LinePlotIndex], ALIGNMENT=1.0, ORIENTATION=90, FONT=1, $
                            CHARSIZE=LinePlotCharSize, CHARTHICK=LinePlotCharThick, COLOR=LinePlotColor, /NOCLIP
                ENDELSE
            ENDFOR
        ENDIF
    ENDIF
    
END
