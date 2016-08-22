; 
; return the [min,max] of an array
; 
FUNCTION CrabMinMax, Array, NoZero=NoZero, Expand=Expand
    
    IF N_ELEMENTS(Array) EQ 0 THEN RETURN, !NULL
    
    ArrayForCalc = Array
    IF KEYWORD_SET(NoZero) THEN BEGIN
        ArrayForCalc = Array[WHERE(Array GT 0)]
    ENDIF
    MinValue = DOUBLE(MIN(ArrayForCalc,/NAN))
    MaxValue = DOUBLE(MAX(ArrayForCalc,/NAN))
    IF KEYWORD_SET(Expand) THEN BEGIN
        ExMaxValue = MaxValue
        ExMinValue = MinValue
        MaxValue = MaxValue+(ExMaxValue-ExMinValue)*(Expand-1.0d)
        MinValue = MinValue-(ExMaxValue-ExMinValue)*(Expand-1.0d)
    ENDIF
    RETURN, [MinValue,MaxValue]
    
END