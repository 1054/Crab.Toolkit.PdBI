PRO label_spec_lines, LineNamePattern, LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, NOPLOT=NOPLOT
    
    IF N_ELEMENTS(LineNamePattern) EQ 0 THEN BEGIN
        PRINT, 'Usage:'
        PRINT, '    label_spec_lines, "H2O", LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, /NoPlot'
        PRINT, '    '
        RETURN
    ENDIF
    
    LabLineData = [ { Name:"H2O(110-101)", Freq: 556.93599 } , $
                    { Name:"H2O(111-000)", Freq:1113.34301 } , $
                    { Name:"H2O(202-111)", Freq: 987.92676 } , $
                    { Name:"H2O(211-202)", Freq: 752.03314 } , $
                    { Name:"H2O(220-211)", Freq:1228.78872 } , $
                    { Name:"H2O(312-221)", Freq:1153.12682 } , $
                    { Name:"H2O(312-303)", Freq:1097.36479 } , $
                    { Name:"H2O(321-312)", Freq:1162.91160 } , $
                    { Name:"H2O(322-313)", Freq:1919.35953 } , $
                    { Name:"H2O(422-331)", Freq: 916.17158 } , $
                    { Name:"H2O(422-413)", Freq:1207.63873 } , $
                    { Name:"H2O(423-330)", Freq: 448.00108 } , $
                    { Name:"H2O(523-432)", Freq:1918.48535 } , $
                    { Name:"H2O(523-514)", Freq:1410.61807 } , $
                    { Name:"[CI](3P1-3P0)",  Freq:492.16065  } , $
                    { Name:"[CI](3P2-3P1)",  Freq:809.34197  } , $
                    { Name:"[NII](3P2-3P1)", Freq:1461.13141 } , $
                    { Name:"CO(1-0)",   Freq:115.2712018  } , $
                    { Name:"CO(2-1)",   Freq:230.5380000  } , $
                    { Name:"CO(3-2)",   Freq:345.7959899  } , $
                    { Name:"CO(4-3)",   Freq:461.0407682  } , $
                    { Name:"CO(5-4)",   Freq:576.2679305  } , $
                    { Name:"CO(6-5)",   Freq:691.4730763  } , $
                    { Name:"CO(7-6)",   Freq:806.6518060  } , $
                    { Name:"CO(8-7)",   Freq:921.7997000  } , $
                    { Name:"CO(9-8)",   Freq:1036.9123930 } , $
                    { Name:"CO(10-9)",  Freq:1151.9854520 } , $
                    { Name:"CO(11-10)", Freq:1267.0144860 } , $
                    { Name:"CO(12-11)", Freq:1381.9951050 } , $
                    { Name:"CO(13-12)", Freq:1496.9229090 } , $
                    { Name:"CO(14-13)", Freq:1611.7935180 } , $
                    { Name:"CO(15-14)", Freq:1726.6025057 } , $
                    { Name:"CO(16-15)", Freq:1841.3455060 } , $
                    { Name:"CO(17-16)", Freq:1956.0181390 } , $
                    { Name:"CO(18-17)", Freq:2070.6159930 } , $
                    { Name:"CO(19-18)", Freq:2185.1346800 } , $
                    { Name:"CO(20-19)", Freq:2299.5698420 } , $
                    { Name:"TEST",      Freq:0000.00001   }   ]
    
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
            LinePlotYLength = !Y.CRANGE[1] -!Y.CRANGE[0]
            LinePlotYRange = [!Y.CRANGE[1] - 0.25*LinePlotYLength, !Y.CRANGE[1] - 0.02*LinePlotYLength]
            IF !D.NAME EQ 'PS' THEN LinePlotThick = 2.0 ELSE LinePlotThick = 1.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharThick = 2.0 ELSE LinePlotCharThick = 1.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharSize = 0.8 ELSE LinePlotCharSize = 1.2
            MESSAGE, "Labelling "+STRING(FORMAT='(I0)',N_ELEMENTS(LineFreqList))+" spec line names", /CONTINUE
            FOR LinePlotIndex=0,N_ELEMENTS(LineFreqList)-1 DO BEGIN
                IF LinePlotIndex LE N_ELEMENTS(COLOR)-1 THEN LinePlotColor=COLOR[LinePlotIndex] ELSE LinePlotColor='FF00FF'xL
               ;PLOTS, [LineFreqList[LinePlotIndex],LineFreqList[LinePlotIndex]], LinePlotYRange, LINESTYLE=2, COLOR=LinePlotColor, Thick=LinePlotThick
                XYOUTS, LineFreqList[LinePlotIndex], LinePlotYRange[1], LineNameList[LinePlotIndex], ALIGNMENT=1.0, ORIENTATION=90, $
                         CHARSIZE=LinePlotCharSize, CHARTHICK=LinePlotCharThick, COLOR=LinePlotColor
            ENDFOR
        ENDIF
    ENDIF
    
END