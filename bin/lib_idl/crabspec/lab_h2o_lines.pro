; 
; This function lab_h2o_lines 
; returns the h2o line names/freqs/waves
; <TODO> input something to select lines to return
; 
PRO lab_h2o_lines, $
                  LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, $
                  PLOT=PLOT
    
    
    ;;
    ;;IF N_ELEMENTS(J_Upper_Array) EQ 0 THEN BEGIN
    ;;    PRINT, 'Usage:'
    ;;    PRINT, '    lab_h2o_lines, J_Upper_Range=[0,14], LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList'
    ;;    PRINT, '    '
    ;;    RETURN
    ;;ENDIF
    
    ;; 
    LineNameList = []
    LineFreqList = []
    LineWaveList = []
    c30 = 29.9792458 ; speed of light 3e10 cm/s = 30e9 cm/s
    LineName="H2O(4_{2,3}-3_{3,0})"  & LineFreq=448.0010750  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(1_{1,0}-1_{0,1})"  & LineFreq=556.9360020  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(2_{1,1}-2_{0,2})"  & LineFreq=752.0332270  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(4_{2,2}-3_{3,1})"  & LineFreq=916.1715820  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(2_{0,2}-1_{1,1})"  & LineFreq=987.9267640  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="OH^+(1_2-0_1)"         & LineFreq=971.919200   & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="OH^+(1_1-0_1)"         & LineFreq=1033.00440   & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(3_{1,2}-3_{0,3})"  & LineFreq=1097.3647910 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(3_{1,2}-2_{2,1})"  & LineFreq=1153.1268220 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(1_{1,1}-0_{0,0})"  & LineFreq=1113.3429640 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(3_{2,1}-3_{1,2})"  & LineFreq=1162.9115930 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(4_{2,2}-4_{1,3})"  & LineFreq=1207.6387140 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(2_{2,0}-2_{1,1})"  & LineFreq=1228.7887720 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="H2O(5_{2,3}-5_{1,4})"  & LineFreq=1410.6180740 & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="HF(1-0)"               & LineFreq=1232.47622   & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave] 
    LineName="CH^+(1-0)"             & LineFreq=835.07895    & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]
    LineName="NH_{3}(2-1)"           & LineFreq=1215.245714  & LineWave=c30/LineFreq & LineNameList=[LineNameList,LineName] & LineFreqList=[LineFreqList,LineFreq] & LineWaveList=[LineWaveList,LineWave]

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