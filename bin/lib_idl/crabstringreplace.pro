; ------------------------------------------------------------------------------------------------------
; CrabStringReplace ---
;                 CrabStringReplace('The sky is blue and the sea is blue','blue','red')
;                   -->              The sky is red and the sea is red
;                 CrabStringReplace('skldjfasdfo&(9*&*(#@asdfojldksjf','asdf','xxxx')
;                   -->              skldjfxxxxo&(9*&*(#@xxxxojldksjf
; ------------------------------------------------------------------------------------------------------
FUNCTION CrabStringReplace, Str, SearchStr, ReplaceStr, REGEX=REGEX
    IF N_PARAMS() NE 3 THEN BEGIN
        MESSAGE,'CrabStringReplace requires 3 parameters: Str, SearchStr, ReplaceStr.'
        RETURN,""
    ENDIF
    IF SIZE(Str,/TNAME) NE "STRING" THEN BEGIN
        MESSAGE,'Parameter Str must be of string type.'
        RETURN,""
    ENDIF
    SearchStr  = STRING(SearchStr)
    ReplaceStr = STRING(ReplaceStr)
    FoundIndex = STRPOS(Str,SearchStr)
    IF FoundIndex EQ -1 THEN RETURN, Str
    SplitStr = []
    FoundLeft = 0
    WHILE FoundIndex NE -1 DO BEGIN
        FoundRight = FoundIndex - 1
        SplitStr   = [ SplitStr, STRMID(Str,FoundLeft,FoundRight-FoundLeft+1) ]
        FoundLeft  = FoundIndex + STRLEN(SearchStr)
        FoundIndex = STRPOS(Str, SearchStr, FoundIndex+1)
    ENDWHILE
    FoundRight = STRLEN(Str)-1
    SplitStr = [ SplitStr, STRMID(Str,FoundLeft,FoundRight-FoundLeft+1) ]
    JointStr = STRJOIN(SplitStr,ReplaceStr)
    RETURN,      JointStr
END