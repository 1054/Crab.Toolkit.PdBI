; 
; This function plots
; 
PRO CrabSpecQuickPlot, XArray, YArray, SaveEPS=SaveEPS, AxesColor=AxesColor, Color=Color, Thick=Thick, CharSize=CharSize, CharThick=CharThick, $
                       XTitle=XTitle, YTitle=YTitle, Title=Title, XSize=XSize, YSize=YSize, XRange=XRange, YRange=YRange, XStyle=XStyle, YStyle=YStyle, XMargin=XMargin, YMargin=YMargin, $
                       XThick=XThick, YThick=YThick, XTickFormat=XTickFormat, YTickFormat=YTickFormat, XTickInterval=XTickInterval, YTickInterval=YTickInterval, $
                       Redshift=Redshift, Continue=Continue, Overplot=Overplot, Close=Close, Fill=Fill, Base=Base, NoData=NoData, Position=Position
    
    ;; 
    IF (N_ELEMENTS(XArray) LE 0 OR N_ELEMENTS(YArray) LE 0) THEN BEGIN
        
        IF NOT KEYWORD_SET(Close) THEN BEGIN
            MESSAGE, "Usage: CrabSpecQuickPlot, XArray, YArray"
            RETURN
        ENDIF
        
    ENDIF ELSE BEGIN
      
      IF NOT KEYWORD_SET(Overplot) THEN BEGIN
        
        ; SaveEPS
        IF KEYWORD_SET(SaveEPS) THEN BEGIN
            IF N_ELEMENTS(XSize) EQ 0 THEN XSize = 45.0
            IF N_ELEMENTS(YSize) EQ 0 THEN YSize = 3.0
            OpenPS, SaveEPS, XSize=XSize, YSize=YSize
        ENDIF
        
        ; TV Window
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
        
        ; Axes range 
        IF N_ELEMENTS(XStyle) EQ 0 THEN XStyle = 1
        IF N_ELEMENTS(YStyle) EQ 0 THEN YStyle = 1
        
        ; Thickness
        IF N_ELEMENTS(Thick)  EQ 0 THEN  Thick = 5.0
        IF N_ELEMENTS(XThick) EQ 0 THEN XThick = 3.0
        IF N_ELEMENTS(YThick) EQ 0 THEN YThick = 3.0
        IF N_ELEMENTS(CharThick) EQ 0 THEN CharThick = 2.25
        IF N_ELEMENTS(CharSize) EQ 0 THEN CharSize = 1.25
        
        ; Plot spec
        PLOT, XArray, YArray, /NODATA, Position=Position, XTitle=XTitle, YTitle=YTitle, XTickFormat=XTickFormat, YTickFormat=YTickFormat, XTickInterval=XTickInterval, YTickInterval=YTickInterval, $
              CharSize=CharSize, CharThick=CharThick, Thick=Thick, XThick=XThick, YThick=YThick, XMargin=XMargin, YMargin=YMargin, $
              Color=AxesColor, PSYM=10, Font=1, XRange=XRange, YRange=YRange, XStyle=XStyle, YStyle=YStyle, XTickLen=0.15, YTickLen=0.01
        
      ENDIF
      
      IF NOT KEYWORD_SET(NoData) THEN BEGIN
        
        ; Thickness
        IF N_ELEMENTS(Thick) EQ 0 THEN Thick = 1.5
        
        ; Plot spec
        IF KEYWORD_SET(Fill) THEN BEGIN
            IF N_ELEMENTS(Base) EQ 0 THEN Base=0.0 ; Base=!Y.CRange[0]
            XArray_Filled = [XArray[0],XArray[0],XArray,XArray[N_ELEMENTS(XArray)-1],XArray[N_ELEMENTS(XArray)-1]]
            YArray_Filled = [Base,Base,YArray,Base,Base]
            IF N_ELEMENTS(WHERE(YArray_Filled LT !Y.CRange[0],/NULL)) GT 0 THEN YArray_Filled[WHERE(YArray_Filled LT !Y.CRange[0],/NULL)] = !Y.CRange[0]
            IF N_ELEMENTS(WHERE(YArray_Filled GT !Y.CRange[1],/NULL)) GT 0 THEN YArray_Filled[WHERE(YArray_Filled GT !Y.CRange[1],/NULL)] = !Y.CRange[1]
            POLYFILL, XArray_Filled, YArray_Filled, THICK=Thick/2.0, Color=Color, NoClip=0
        ENDIF 
            XArray_Plot = XArray
            YArray_Plot = YArray
            IF N_ELEMENTS(WHERE(YArray_Plot LT !Y.CRange[0],/NULL)) GT 0 THEN YArray_Plot[WHERE(YArray_Plot LT !Y.CRange[0],/NULL)] = !Y.CRange[0]
            IF N_ELEMENTS(WHERE(YArray_Plot GT !Y.CRange[1],/NULL)) GT 0 THEN YArray_Plot[WHERE(YArray_Plot GT !Y.CRange[1],/NULL)] = !Y.CRange[1]
            OPLOT, XArray_Plot, YArray_Plot, COLOR=Color, THICK=Thick, PSYM=10
      ENDIF
      
    ENDELSE
    
    ;; plot lines
    ;IF N_ELEMENTS(Redshift) GT 0 THEN BEGIN
    ;    CrabSpecPlotCO, ColXs, ColYs, Redshift=Redshift, Color="magenta", CharThick=2.2
    ;ENDIF
    
    
    ; Save EPS
    IF !D.NAME EQ 'PS' AND ((NOT KEYWORD_SET(Continue)) OR KEYWORD_SET(Close)) THEN BEGIN
        DEVICE, /CLOSE
        IF STRMATCH(!VERSION.OS,'Win*',/FOLD_CASE) THEN SET_PLOT, 'WIN' ELSE SET_PLOT, 'X'
        ;PRINT, 'ClosePS: '+SaveEPS
    ENDIF
    
END