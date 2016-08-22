; 
; This function lab_co_lines 
; returns the co line names/freqs/waves
; 
PRO lab_co_lines, J_Upper_Array=J_Upper_Array, J_Upper_Range=J_Upper_Range, $
                  LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, $
                  PLOT=PLOT
    
    ;; 
    IF N_ELEMENTS(J_Upper_Array) GT 0 THEN BEGIN
        ;; 
    ENDIF
    
    ;; 
    IF N_ELEMENTS(J_Upper_Range) EQ 2 THEN BEGIN
        IF J_Upper_Range[1] GT J_Upper_Range[0] THEN BEGIN
            J_Upper_Array = INDGEN((J_Upper_Range[1]-J_Upper_Range[0]+1),START=J_Upper_Range[0])
        ENDIF
    ENDIF
    
    ;;
    IF N_ELEMENTS(J_Upper_Array) EQ 0 THEN BEGIN
        PRINT, 'Usage:'
        PRINT, '    lab_co_lines, J_Upper_Range=[0,14], LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList'
        PRINT, '    '
        RETURN
    ENDIF
    
    ;; 
    LineNameList = []
    LineFreqList = []
    LineWaveList = []
    c30 = 29.9792458 ; speed of light 3e10 cm/s = 30e9 cm/s
    FOREACH J_Upper, J_Upper_Array DO BEGIN
        ;; 
        IF J_Upper EQ 0 THEN CONTINUE
        ;; 
        LineName = STRING(FORMAT='("CO","(",I0,"-",I0,")")',J_Upper,J_Upper-1)
        IF LineName EQ '' THEN BEGIN
            ;;
        ENDIF ELSE IF LineName EQ 'CO(1-0)' THEN BEGIN
            LineFreq = 115.2712018  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(2-1)' THEN BEGIN
            LineFreq = 230.5380000  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(3-2)' THEN BEGIN
            LineFreq = 345.7959899  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(4-3)' THEN BEGIN
            LineFreq = 461.0407682  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(5-4)' THEN BEGIN
            LineFreq = 576.2679305  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(6-5)' THEN BEGIN
            LineFreq = 691.4730763  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(7-6)' THEN BEGIN
            LineFreq = 806.6518060  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(8-7)' THEN BEGIN
            LineFreq = 921.7997000  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(9-8)' THEN BEGIN
            LineFreq = 1036.9123930  ; GHz
            LineWave = c30/LineFreq  ; cm
        ENDIF ELSE IF LineName EQ 'CO(10-9)' THEN BEGIN
            LineFreq = 1151.9854520  ; GHz
            LineWave = c30/LineFreq  ; cm
        ENDIF ELSE IF LineName EQ 'CO(11-10)' THEN BEGIN
            LineFreq = 1267.0144860  ; GHz
            LineWave = c30/LineFreq  ; cm
        ENDIF ELSE IF LineName EQ 'CO(12-11)' THEN BEGIN
            LineFreq = 1381.9951050  ; GHz
            LineWave = c30/LineFreq  ; cm
        ENDIF ELSE IF LineName EQ 'CO(13-12)' THEN BEGIN
            LineFreq = 1496.9229090  ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(14-13)' THEN BEGIN
            LineFreq = 1611.7935180 ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF ELSE IF LineName EQ 'CO(15-14)' THEN BEGIN
            LineFreq = 1726.6025057 ; GHz
            LineWave = c30/LineFreq ; cm
        ENDIF
        LineNameList = [ LineNameList, LineName ]
        LineFreqList = [ LineFreqList, LineFreq ]
        LineWaveList = [ LineWaveList, LineWave ]
    ENDFOREACH
    
    
    IF KEYWORD_SET(PLOT) THEN BEGIN
        IF !X.CRANGE[1] GT !X.CRANGE[0] AND !Y.CRANGE[1] GT !Y.CRANGE[0] THEN BEGIN
            LinePlotYLength = !Y.CRANGE[1] -!Y.CRANGE[0]
            LinePlotYRange = [!Y.CRANGE[1] - 0.25*LinePlotYLength, !Y.CRANGE[1] - 0.02*LinePlotYLength]
            IF !D.NAME EQ 'PS' THEN LinePlotThick = 2.0 ELSE LinePlotThick = 1.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharThick = 2.0 ELSE LinePlotCharThick = 1.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharSize = 0.8 ELSE LinePlotCharSize = 1.2
            FOR LinePlotIndex=0,N_ELEMENTS(LineFreqList)-1 DO BEGIN
                IF LinePlotIndex LE N_ELEMENTS(COLOR)-1 THEN LinePlotColor=COLOR[LinePlotIndex] ELSE LinePlotColor='FF00FF'xL
               ;PLOTS, [LineFreqList[LinePlotIndex],LineFreqList[LinePlotIndex]], LinePlotYRange, LINESTYLE=2, COLOR=LinePlotColor, Thick=LinePlotThick
                XYOUTS, LineFreqList[LinePlotIndex], LinePlotYRange[1], LineNameList[LinePlotIndex], ALIGNMENT=1.0, ORIENTATION=90, $
                        CHARSIZE=LinePlotCharSize, CHARTHICK=LinePlotCharThick, COLOR=LinePlotColor
            ENDFOR
        ENDIF
    ENDIF
    
    RETURN
    
END