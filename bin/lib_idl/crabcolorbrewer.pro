; 
; provide a list of colors
; 
FUNCTION CrabColorBrewer, BrColorIndex, Colorfull=Colorfull, ColorScheme=ColorScheme
    
    ; Firebrick - Red - Orange - Yellow - Grass - Green - Naval - Blue - Purple
    ; BrColors = ['42019e'xL,'4f3ed5'xL,'436df4'xL,'61aefd'xL,'8be0fe'xL,'bfffff'xL,'98f5e6'xL,'a4ddab'xL,'a5c266'xL,'bd8832'xL,'a24f5e'xL]
    BrColors = ['42019e'xL,'4f3ed5'xL,'436df4'xL,'61aefd'xL,'8be0fe'xL,'a4ddab'xL,'a5c266'xL,'bd8832'xL,'a24f5e'xL]
    
    IF KEYWORD_SET(Colorfull) THEN BEGIN
        BrColors = ['7f0000'xL,'4865ef'xL,'9ed4fd'xL,'8eddad'xL,'438423'xL,'294500'xL,'c4cc7b'xL,'be8c2b'xL,'814008'xL]
        ;            red        orange   light orange light green green   dark green   
    ENDIF
    
    IF N_ELEMENTS(ColorScheme) GT 0 THEN BEGIN
        IF ColorScheme EQ '201601' THEN BEGIN
;            BrColors = [ 'FFC929'xL, $
;                         'FF5E29'xL, $
;                         'FF295E'xL, $
;                         'FF29C9'xL, $
;                         'C929FF'xL, $
;                         '5E29FF'xL, $
;                         '295EFF'xL, $
;                         '29C9FF'xL, $
;                         '29FFC9'xL, $
;                         '29FF5E'xL, $
;                         '5EFF29'xL, $
;                         'C9FF29'xL, $
;                         'FFD966'xL, $
;                         'FFE8A3'xL, $
;                         '668CFF'xL, $
;                         'A3BAFF'xL  ] ; http://www.colorschemer.com/online.html Set RGB #29C9FF
            BrColors = [ '29C9FF'xL, $
                         '295EFF'xL, $
                         '5E29FF'xL, $
                         'C929FF'xL, $
                         'FF29C9'xL, $
                         'FF295E'xL, $
                         'FF5E29'xL, $
                         'FFC929'xL, $
                         'C9FF29'xL, $
                         '5EFF29'xL, $
                         '29FF5E'xL, $
                         '29FFC9'xL, $
                         '66D9FF'xL, $
                         'A3E8FF'xL, $
                         'FF8C66'xL, $
                         'FFBAA3'xL  ] ; 'RRGGBB'xL ; http://www.colorschemer.com/online.html Set RGB #29C9FF
        ENDIF
    ENDIF
    
    
    IF N_ELEMENTS(BrColorIndex) GT 0 THEN BEGIN
        IF BrColorIndex GT 0 THEN BEGIN
            BrCI = ROUND(BrColorIndex) MOD (N_ELEMENTS(BrColors)-1)
        ENDIF ELSE BEGIN
            BrCI = BrColorIndex
        ENDELSE
        RETURN, BrColors[BrCI]
    ENDIF
    
    RETURN, BrColors
    
END