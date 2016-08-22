; 
; This code will fill a spectrum
; 
PRO CrabSpecFill, freq, flux, Velocity=Velocity, BarStyle=BarStyle, Histogram=Histogram, THICK=THICK, COLOR=COLOR, LINE_FILL=LINE_FILL, ORIENTATION=ORIENTATION, SPACING=SPACING, NOCLIP=NOCLIP, BASE_LEVEL=BASE_LEVEL, BASE_ARRAY=BASE_ARRAY
    
    ; check input
    IF N_ELEMENTS(freq) EQ 0 THEN MESSAGE, 'CrabSpecFill: Error! freq contains no data!'
    IF N_ELEMENTS(flux) EQ 0 THEN MESSAGE, 'CrabSpecFill: Error! flux contains no data!'
    IF N_ELEMENTS(freq) EQ 1 THEN MESSAGE, 'CrabSpecFill: Error! freq contains only one data point!'
    IF N_ELEMENTS(flux) EQ 1 THEN MESSAGE, 'CrabSpecFill: Error! flux contains only one data point!'
    IF N_ELEMENTS(flux) NE N_ELEMENTS(freq) THEN MESSAGE, 'CrabSpecFill: Error! flux and freq have different dimensions!'
    
    ; check keywords
    IF KEYWORD_SET(Histogram) THEN BarStyle=1
    
    ; use polyfill to fill the space under spectrum
    FOR i=0,N_ELEMENTS(freq)-1 DO BEGIN
        IF NOT KEYWORD_SET(BarStyle) THEN BEGIN
            IF i LT N_ELEMENTS(freq)-1 THEN BEGIN
                IF (flux[i] GT 0 OR flux[i+1] GT 0) THEN BEGIN
                POLYFILL, [freq[i],freq[i],freq[i+1],freq[i+1]], $
                          [0.00000,flux[i],flux[i+1],0.0000000], $
                          THICK=THICK, COLOR=COLOR, LINE_FILL=LINE_FILL, ORIENTATION=ORIENTATION, SPACING=SPACING, NOCLIP=NOCLIP
                ENDIF
            ENDIF
        ENDIF ELSE BEGIN
            IF N_ELEMENTS(BASE_LEVEL) EQ 0 THEN BEGIN
                BASE_LEVEL = 0.0D
            ENDIF
            IF N_ELEMENTS(BASE_ARRAY) EQ N_ELEMENTS(freq) THEN BEGIN
                BASE_LEVEL = BASE_ARRAY[i]
            ENDIF
            IF i EQ 0 THEN BEGIN
                half_freq_left = (freq[i+1]-freq[i])/2.0 
                half_freq_right = (freq[i+1]-freq[i])/2.0 
                OPLOT,    [freq[i]-half_freq_left,freq[i]-half_freq_left,freq[i]+half_freq_right,freq[i]+half_freq_right], $
                          [BASE_LEVEL            ,flux[i]               ,flux[i]                ,flux[i+1]              ], $
                          THICK=THICK, COLOR=COLOR, NOCLIP=NOCLIP
                POLYFILL, [freq[i]-half_freq_left,freq[i]-half_freq_left,freq[i]+half_freq_right,freq[i]+half_freq_right], $
                          [BASE_LEVEL            ,flux[i]               ,flux[i]                ,BASE_LEVEL             ], $
                          THICK=THICK, COLOR=COLOR, LINE_FILL=LINE_FILL, ORIENTATION=ORIENTATION, SPACING=SPACING, NOCLIP=NOCLIP
            ENDIF ELSE IF i EQ N_ELEMENTS(freq)-1 THEN BEGIN
                half_freq_left = (freq[i]-freq[i-1])/2.0 
                half_freq_right = (freq[i]-freq[i-1])/2.0 
                OPLOT,    [freq[i]-half_freq_left,freq[i]-half_freq_left,freq[i]+half_freq_right,freq[i]+half_freq_right], $
                          [flux[i-1]             ,flux[i]               ,flux[i]                ,BASE_LEVEL             ], $
                          THICK=THICK, COLOR=COLOR, NOCLIP=NOCLIP
                POLYFILL, [freq[i]-half_freq_left,freq[i]-half_freq_left,freq[i]+half_freq_right,freq[i]+half_freq_right], $
                          [BASE_LEVEL            ,flux[i]               ,flux[i]                ,BASE_LEVEL             ], $
                          THICK=THICK, COLOR=COLOR, LINE_FILL=LINE_FILL, ORIENTATION=ORIENTATION, SPACING=SPACING, NOCLIP=NOCLIP
            ENDIF ELSE BEGIN
                half_freq_left = (freq[i]-freq[i-1])/2.0 
                half_freq_right = (freq[i+1]-freq[i])/2.0 
                OPLOT,    [freq[i]-half_freq_left,freq[i]-half_freq_left,freq[i]+half_freq_right,freq[i]+half_freq_right], $
                          [flux[i-1]             ,flux[i]               ,flux[i]                ,flux[i+1]              ], $
                          THICK=THICK, COLOR=COLOR, NOCLIP=NOCLIP
                POLYFILL, [freq[i]-half_freq_left,freq[i]-half_freq_left,freq[i]+half_freq_right,freq[i]+half_freq_right], $
                          [BASE_LEVEL            ,flux[i]               ,flux[i]                ,BASE_LEVEL             ], $
                          THICK=THICK, COLOR=COLOR, LINE_FILL=LINE_FILL, ORIENTATION=ORIENTATION, SPACING=SPACING, NOCLIP=NOCLIP
            ENDELSE
        ENDELSE
    ENDFOR
    
END
