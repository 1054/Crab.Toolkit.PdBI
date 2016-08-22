; 
; This function overplots HCN lines
; 
; X axis must be frequency in GHz
; Y axis can be any intensity
; 
PRO CrabSpecPlotHCN, Redshift=Redshift, Color=Color, Thick=Thick, CharThick=CharThick, CharSize=CharSize, ALIGNMENT=ALIGNMENT
    
    ;; 
    lab_hcn_lines, LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList
    PRINT, LineNameList, LineFreqList
    
    ;;
    IF N_ELEMENTS(Redshift) GT 0 THEN BEGIN
        LineFreqList = LineFreqList / (1.0+Redshift[0])
    ENDIF
    PRINT, LineNameList, LineFreqList
    
    ;;
    IF SIZE(Color,/TNAME) EQ "STRING" THEN PlotColor=cgColor(Color)
    
    ;;
    IF N_ELEMENTS(ALIGNMENT) EQ 0 THEN ALIGNMENT=0.5
    
    ;; 
    FOR i=0,N_ELEMENTS(LineFreqList)-1 DO BEGIN
        PlotXArr = [0.0,0.0]
        PlotYArr = [0.0,0.0]
        IF (LineFreqList[i]-!X.CRANGE[0]) GT -0.25*(!X.CRANGE[1]-!X.CRANGE[0]) AND $
           (LineFreqList[i]-!X.CRANGE[1]) LT +0.25*(!X.CRANGE[1]-!X.CRANGE[0]) THEN BEGIN
            PlotXArr[0] = LineFreqList[i]
            PlotXArr[1] = LineFreqList[i]
            PlotXCen    = LineFreqList[i]
            PlotYArr[0] = !Y.CRANGE[0]
            PlotYArr[1] = !Y.CRANGE[1]
            PlotYCen    = !Y.CRANGE[0] + 0.68*(!Y.CRANGE[1]-!Y.CRANGE[0])
            PLOTS, PlotXArr, PlotYArr, Color=PlotColor, LINESTYLE=2, Thick=Thick
            XYOUTS, PlotXCen, PlotYCen, LineNameList[i], Color=PlotColor, CharThick=CharThick, CharSize=CharSize, ALIGNMENT=ALIGNMENT
        ENDIF
    ENDFOR
    
    RETURN
    
END