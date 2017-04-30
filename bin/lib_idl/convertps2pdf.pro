; 
; Updated: 2014-04-08 MKDIR
; 
PRO ConvertPs2Pdf, InputFile, OutputFile
    
    
    IF !D.Name EQ 'PS' THEN BEGIN
        DEVICE, /CLOSE
        IF STRMATCH(!VERSION.OS_FAMILY,'*window*',/F) THEN SET_PLOT, 'WIN'
        IF STRMATCH(!VERSION.OS_FAMILY,'*unix*',/F) THEN SET_PLOT, 'X'
    ENDIF
    
    IF N_ELEMENTS(OutputFile) EQ 0 THEN BEGIN
        IF STRMATCH(InputFile,'*.ps') THEN BEGIN
            OutputFile = FILE_DIRNAME(InputFile,/MARK_DIR)+FILE_BASENAME(InputFile,'.ps')+'.pdf'
        ENDIF ELSE IF STRMATCH(InputFile,'*.eps') THEN BEGIN
            OutputFile = FILE_DIRNAME(InputFile,/MARK_DIR)+FILE_BASENAME(InputFile,'.eps')+'.pdf'
        ENDIF ELSE BEGIN
            OutputFile = FILE_DIRNAME(InputFile,/MARK_DIR)+FILE_BASENAME(InputFile)+'.pdf'
        ENDELSE
    ENDIF
    
    ; Check Output dir
    OutputDirp = FILE_DIRNAME(OutputFile)
    IF NOT FILE_TEST(OutputDirp,/DIR) THEN BEGIN
        SPAWN, 'mkdir '+OutputDirp
    ENDIF
    
    IF STRMATCH(!VERSION.OS_FAMILY,'*Windows*',/FOLD_CASE) THEN BEGIN
;        ExecStr = ''
;        ExecStr = ExecStr + 'D: & cd D:\GreenSoftware\GhostScript\9.06\bin & '
;;       ExecStr = ExecStr + 'set PATH=D:\GreenSoftware\GhostScript\9.06\bin;C:\Windows\Fonts;%PATH% & '
;        ExecStr = ExecStr + 'set PATH=D:\GreenSoftware\GhostScript\9.06\bin;%PATH% & '
;;       ExecStr = ExecStr + 'ps2pdf.bat -dNOPLATFONTS -sFONTPATH="C:\Windows\Fonts" -dEPSCrop "'+OutputFile+'" '
;;       ExecStr = ExecStr + 'ps2pdf.bat -dEPSCrop "'+OutputFile+'" '
;        ExecStr = ExecStr + 'gswin32c.exe -sDEVICE=pdfwrite -dSAFER -dPDFSETTINGS=/prepress -dCompatibilityLevel=1.4 ' ; -q or -dQUIET ; /prepress or /screen
;        ExecStr = ExecStr +              '-dNOPAUSE -dBATCH -dEmbedAllFonts=true -dSubsetFonts=true -dNeverEmbed[] '
;        ExecStr = ExecStr +              '-dNOPLATFONTS -sFONTPATH="C:\Windows\Fonts" '
;        ExecStr = ExecStr +              '-dEPSCrop -sOutputFile="'+OutputFile+'" -c save pop -f "'+InputFile+'"'
;;       ExecStr = ExecStr + ' & pause()'
;        SPAWN, ExecStr
        ExecBin = (FILE_SEARCH('C:\Program Files\gs\gs*\bin\gswin64c.exe'))[0]
        IF ExecBin EQ '' THEN ExecBin = 'gswin32c.exe'
        ExecFile = FILE_DIRNAME(OutputFile,/MARK_DIR)+FILE_BASENAME(OutputFile,'.pdf')+'.bat'
        OPENW, LUN, ExecFile, /GET_LUN
        PRINTF, LUN, '"' + ExecBin + '" -sDEVICE=pdfwrite -dSAFER -dPDFSETTINGS=/prepress -dCompatibilityLevel=1.4 -dNOPAUSE -dBATCH -dEmbedAllFonts=true -dSubsetFonts=true -dNeverEmbed[] -dNOPLATFONTS -sFONTPATH="C:\Windows\Fonts" -dEPSCrop -sOutputFile="'+OutputFile+'" -c save pop -f "'+InputFile+'"'
        CLOSE, LUN
        FREE_LUN, LUN
        SPAWN, ExecFile
    ENDIF
    IF STRMATCH(!VERSION.OS_FAMILY,'*unix*',/FOLD_CASE) THEN BEGIN
;       SPAWN, 'cd "'+FILE_DIRNAME(OutputFile)+'" & ps2pdf -dEPSCrop "'+FILE_DIRNAME(OutputFile,/MARK_DIR)+FILE_BASENAME(OutputFile,'.pdf')+'.ps" '
        SPAWN, 'ps2pdf -dEPSCrop "'+InputFile+'" '+' "'+OutputFile+'" '
    ENDIF
    
    PRINT, 'ConvertPs2Pdf: OUTPUT '+OutputFile
    
END