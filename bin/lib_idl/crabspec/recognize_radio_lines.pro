; 
; This function lab_co_lines 
; returns the co line names/freqs/waves
; 
PRO Recognize_Radio_Lines, InputText, $
                           LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, $
                           Verbose=Verbose
    
    ; Check Input
    IF N_ELEMENTS(InputText) EQ 0 THEN BEGIN
        PRINT, 'Usage:'
        PRINT, '    Recognize_Radio_Lines, InputText, LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList'
        PRINT, '    '
        RETURN
    ENDIF
    
    ; Prepare Data Arrays
    LineSpecies  = MAKE_ARRAY(N_ELEMENTS(InputText),/STRING,VALUE='')
    LineLvUpper  = MAKE_ARRAY(N_ELEMENTS(InputText),/STRING,VALUE='')
    LineLvLower  = MAKE_ARRAY(N_ELEMENTS(InputText),/STRING,VALUE='')
    LineNameList = MAKE_ARRAY(N_ELEMENTS(InputText),/STRING,VALUE='')
    LineFreqList = MAKE_ARRAY(N_ELEMENTS(InputText),/DOUBLE,VALUE=0.0D)
    LineWaveList = MAKE_ARRAY(N_ELEMENTS(InputText),/DOUBLE,VALUE=0.0D)
    c30 = 29.9792458 ; speed of light 3e10 cm/s = 30e9 cm/s
    
    ; Loop input text and recognize radio lines
    FOR i = 0, N_ELEMENTS(InputText)-1 DO BEGIN
        ; 
        TmpStr = STRTRIM((InputText[i]),2)
        TmpArr = ['']
        IF N_ELEMENTS(TmpArr) LE 1 OR TmpArr[0] EQ '' THEN BEGIN
            TmpArr = STREGEX(TmpStr,'(.*)[(](.*)[-](.*)[)][^()]*$',/EXTRACT,/SUBEXPR,/FOLD_CASE) ; e.g. XXX ( XXX - XXX )
        ENDIF
        IF N_ELEMENTS(TmpArr) LE 1 OR TmpArr[0] EQ '' THEN BEGIN
            TmpArr = STREGEX(TmpStr,'(.*)[ ]+(.*)[-](.*)$',/EXTRACT,/SUBEXPR,/FOLD_CASE) ; e.g. XXX XXX - XXX
        ENDIF
        IF N_ELEMENTS(TmpArr) LE 1 OR TmpArr[0] EQ '' THEN BEGIN
            TmpArr = STREGEX(TmpStr,'(.*[^0-9])([0-9]+)[-]([0-9]+)$',/EXTRACT,/SUBEXPR,/FOLD_CASE) ; e.g. XXX999 - 999
        ENDIF
        IF N_ELEMENTS(TmpArr) LE 1 OR TmpArr[0] EQ '' THEN BEGIN
            TmpArr = STREGEX(TmpStr,'(.*)[ ]+(.*)$',/EXTRACT,/SUBEXPR,/FOLD_CASE) ; e.g. XXX XXX
        ENDIF
        IF N_ELEMENTS(TmpArr) LE 1 OR TmpArr[0] EQ '' THEN BEGIN
            TmpArr = STREGEX(TmpStr,'(\[.*\])(.*)$',/EXTRACT,/SUBEXPR,/FOLD_CASE) ; e.g. [XXX]XXX
        ENDIF
        IF N_ELEMENTS(TmpArr) LE 1 OR TmpArr[0] EQ '' THEN BEGIN
            TmpArr = STREGEX(TmpStr,'(.*[^0-9])([0-9]+)$',/EXTRACT,/SUBEXPR,/FOLD_CASE) ; e.g. [XXX]XXX
        ENDIF
        ;HELP, TmpArr
        IF N_ELEMENTS(TmpArr) EQ 4 AND TmpArr[0] NE '' THEN BEGIN
            LineSpecies[i] = TmpArr[1]
            LineLvUpper[i] = TmpArr[2]
            LineLvLower[i] = TmpArr[3]
            LineNameList[i] = LineSpecies[i] + " ( "+LineLvUpper[i]+" - "+LineLvLower[i]+" )"
            IF KEYWORD_SET(Verbose) THEN BEGIN
                ;PRINT, LineNameList[i]
                PRINT, "LineSpecies = "+LineSpecies[i]
                PRINT, "LineTransition = "+LineLvUpper[i]+" - "+LineLvLower[i]
            ENDIF
        ENDIF ELSE $
        IF N_ELEMENTS(TmpArr) EQ 3 AND TmpArr[0] NE '' THEN BEGIN
            LineSpecies[i] = STRTRIM(TmpArr[1],2)
            LineLvUpper[i] = STRTRIM(TmpArr[2],2)
            LineNameList[i] = LineSpecies[i] + " "+LineLvUpper[i]
            IF KEYWORD_SET(Verbose) THEN BEGIN
                ;PRINT, LineNameList[i]
                PRINT, "LineSpecies = "+LineSpecies[i]
                PRINT, "LineTransition = "+LineLvUpper[i]
            ENDIF
        ENDIF
        ;
        ; OK now we got the LineSpecies[i]
        ; check line frequencies
        ; 
        IF LineSpecies[i] EQ 'CO' THEN BEGIN
            IF LineLvUpper[i] EQ '0' THEN BEGIN
                LineFreqList[i] = 0.0 ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '1' THEN BEGIN
                LineFreqList[i] =  115.2712018  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '2' THEN BEGIN
                LineFreqList[i] =  230.5380000  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '3' THEN BEGIN
                LineFreqList[i] =  345.7959899  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '4' THEN BEGIN
                LineFreqList[i] =  461.0407682  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '5' THEN BEGIN
                LineFreqList[i] =  576.2679305  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '6' THEN BEGIN
                LineFreqList[i] =  691.4730763  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '7' THEN BEGIN
                LineFreqList[i] =  806.6518060  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '8' THEN BEGIN
                LineFreqList[i] =  921.7997000  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '9' THEN BEGIN
                LineFreqList[i] =  1036.9123930  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '10' THEN BEGIN
                LineFreqList[i] =  1151.9854520  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '11' THEN BEGIN
                LineFreqList[i] =  1267.0144860  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '12' THEN BEGIN
                LineFreqList[i] =  1381.9951050  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '13' THEN BEGIN
                LineFreqList[i] =  1496.9229090  ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '14' THEN BEGIN
                LineFreqList[i] =  1611.7935180 ; GHz
            ENDIF ELSE IF LineLvUpper[i] EQ '15' THEN BEGIN
                LineFreqList[i] =  1726.6025057 ; GHz
            ENDIF
            LineWaveList[i] = c30/LineFreqList[i] ; cm
            IF KEYWORD_SET(Verbose) THEN BEGIN
                ;PRINT, LineNameList[i]
                PRINT, "LineFrequency = "+STRING(FORMAT='(F0.6)',LineFreqList[i])+" GHz"
                PRINT, "LineWavelength = "+STRING(FORMAT='(F0.6)',LineWaveList[i])+" cm"
            ENDIF
        ENDIF
        
    ENDFOR
    
END




PRO Recognize_Radio_Lines_Test
    Recognize_Radio_Lines, /Verbose, "H2O(321-312)"
    Recognize_Radio_Lines, /Verbose, "o-H2O(321-312)"
    Recognize_Radio_Lines, /Verbose, "o-H2O 321-312"
    Recognize_Radio_Lines, /Verbose, "[N II] (3P2-3P1)"
    Recognize_Radio_Lines, /Verbose, "[N II] 3P2-3P1"
    Recognize_Radio_Lines, /Verbose, "H_3O^{+} 1_{1,1}-0_{0,0}"
    Recognize_Radio_Lines, /Verbose, "CO(12-11)^{H2O}"
    Recognize_Radio_Lines, /Verbose, "CO(1-0)"
    Recognize_Radio_Lines, /Verbose, "[CII] 158um"
    Recognize_Radio_Lines, /Verbose, "[CII]158um"
    Recognize_Radio_Lines, /Verbose, "CO1-0"
    Recognize_Radio_Lines, /Verbose, "CO10"
END