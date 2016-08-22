; 
; This function lab_HCN_lines 
; returns the HCN line names/freqs/waves
; <TODO> input something to select lines to return
; 
PRO lab_HCN_lines, $
                  LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, $
                  PLOT=PLOT
    
    
    ;;
    ;;IF N_ELEMENTS(J_Upper_Array) EQ 0 THEN BEGIN
    ;;    PRINT, 'Usage:'
    ;;    PRINT, '    lab_HCN_lines, J_Upper_Range=[0,14], LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList'
    ;;    PRINT, '    '
    ;;    RETURN
    ;;ENDIF
    
    ;; 
    LineNameList = []
    LineFreqList = []
    LineWaveList = []
    c30 = 29.9792458 ; speed of light 3e10 cm/s = 30e9 cm/s
    LineName="HCN(1-0)"   & LineFreq=88.6316023  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(2-1)"   & LineFreq=177.2611115 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(3-2)"   & LineFreq=265.8864343 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(4-3)"   & LineFreq=354.5054779 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(5-4)"   & LineFreq=443.1161493 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(6-5)"   & LineFreq=531.7163479 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(7-6)"   & LineFreq=620.3040022 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(8-7)"   & LineFreq=708.8770051 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(9-8)"   & LineFreq=797.4332623 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HCN(10-9)"  & LineFreq=885.9706949 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    
    ;; 
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