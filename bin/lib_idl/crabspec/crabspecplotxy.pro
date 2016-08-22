; 
; This function plots csv table
; assuming first column is x and second column is y
; 
PRO CrabSpecPlotXY, SpecDataFiles, Color=Colors, Thick=Thicks, XTitle=XTitle, YTitle=YTitle, Title=Title, XSize=XSize, YSize=YSize, Redshift=Redshift
    
    ;; 
    IF N_ELEMENTS(SpecDataFiles) LE 0 THEN BEGIN
        ;; 
        PRINT, "Usage: CrabSpecPlotXY, SpecDataFiles, Color=Colors, XTitle=XTitle, YTitle=YTitle, Title=Title, XSize=XSize, YSize=YSize"
        RETURN
    ENDIF
    
    ;; 
    i = 0
    ColXs = []
    ColYs = []
    ColNs = []
    ColCs = [] ; Plot Colors
    ColTs = [] ; Plot Thicknesses
    FOREACH SpecDataFile, SpecDataFiles DO BEGIN
        ;; filesearch
        SpecDataTables = FILE_SEARCH(SpecDataFile, FOLD_CASE=FOLD_CASE)
        ;; color
        IF i LT N_ELEMENTS(Colors) THEN ColC=Colors[i] ELSE ColC=0L
        IF i LT N_ELEMENTS(Thicks) THEN ColT=Thicks[i] ELSE ColT=1.0
        IF SIZE(ColC,/TNAME) EQ "STRING" THEN ColC=cgColor(ColC) ELSE ColC=0L
        ;; 
        FOREACH SpecDataTable, SpecDataTables DO BEGIN
            ;; 
            IF SpecDataTable EQ "" THEN CONTINUE
            ;; readcol
            PRINT, SpecDataTable
            READCOL, SpecDataTable, ColX, ColY
            ColN = N_ELEMENTS(ColX)
            ;; append to record
            ColXs = [ ColXs, ColX ]
            ColYs = [ ColYs, ColY ]
            ColNs = [ ColNs, ColN ]
            ColCs = [ ColCs, ColC ]
            ColTs = [ ColTs, ColT ]
        ENDFOREACH
        i++
    ENDFOREACH
    
    ;; 
    IF TOTAL(ColNs) LE 0 THEN BEGIN
        MESSAGE, "No Data!"
        RETURN
    ENDIF
    
    ;; 
    IF N_ELEMENTS(XSize) EQ 0 THEN XSize=800
    IF N_ELEMENTS(YSize) EQ 0 THEN YSize=350
    
    ;; 
    n1 = 0 & n2 = ColNs[0]-1  & i = 0
    IF !D.NAME NE "PS" THEN WINDOW, 1, XSize=XSize, YSize=YSize
    PLOT, ColXs, ColYs, /NODATA, XTitle=XTitle, YTitle=YTitle, CharSize=1.5, CharThick=2.5
    IF N_ELEMENTS(Title) GE 1 THEN BEGIN
        XYOUTS, 0.5, 0.88, Title, CHARTHICK=3.0, CHARSIZE=1.8, /NORMAL, ALIGNMENT=0.5
    ENDIF
    FOR i=0,N_ELEMENTS(ColNs)-1 DO BEGIN
        ;; load spec
        ColX = ColXs[n1:n2]
        ColY = ColYs[n1:n2]
        ColN = ColNs[i]
        ColC = ColCs[i] ; plot color
        ColT = ColTs[i] ; plot thick
        ;; plot spec
        PLOTS, ColX, ColY, COLOR=ColC, THICK=ColT
        ;; next spec
        n1 = n1 + ColN
        n2 = n2 + ColN
    ENDFOR
    ;; plot lines
    IF N_ELEMENTS(Redshift) GT 0 THEN BEGIN
        CrabSpecPlotCO, ColXs, ColYs, Redshift=Redshift, Color="magenta", CharThick=2.2
    ENDIF
    
    
    RETURN
    
END