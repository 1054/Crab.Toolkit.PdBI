PRO lab_spec_lines_submillimeter, LineNamePattern, LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, LineRedshift=LineRedshift, $
                                  NOPLOT=NOPLOT, PlotWavelength=PlotWavelength, PlotLineStyle=PlotLineStyle, PlotColor=PlotColor, PlotYRange=PlotYRange
    
    IF N_ELEMENTS(LineNamePattern) EQ 0 THEN BEGIN
        PRINT, 'Usage:'
        PRINT, '    lab_spec_lines_optical, "O|N|S", LineNameList=LineNameList, LineFreqList=LineFreqList, LineWaveList=LineWaveList, /NoPlot'
        PRINT, '    '
        RETURN
    ENDIF
    
    LabLineData = [ $
                    { Name:'CO(1-0)',         Freq: 115.2712018D       } , $
                    { Name:'CO(2-1)',         Freq: 230.5380000D       } , $
                    { Name:'CO(3-2)',         Freq: 345.7959899D       } , $
                    { Name:'CO(4-3)',         Freq: 461.0407682D       } , $
                    { Name:'CO(5-4)',         Freq: 576.2679305D       } , $
                    { Name:'CO(6-5)',         Freq: 691.4730763D       } , $
                    { Name:'CO(7-6)',         Freq: 806.6518060D       } , $
                    { Name:'CO(8-7)',         Freq: 921.7997000D       } , $
                    { Name:'CO(9-8)',         Freq: 1036.9123930D      } , $
                    { Name:'CO(10-9)',        Freq: 1151.9854520D      } , $
                    { Name:'CO(11-10)',       Freq: 1267.0144860D      } , $
                    { Name:'CO(12-11)',       Freq: 1381.9951050D      } , $
                    { Name:'CO(13-12)',       Freq: 1496.9229090D      } , $
                    { Name:'CO(14-13)',       Freq: 1611.7935180D      } , $
                    { Name:'CO(15-14)',       Freq: 1726.6025057D      } , $
                    { Name:'CO(16-15)',       Freq: 1841.3455060D      } , $
                    { Name:'CO(17-16)',       Freq: 1956.0181390D      } , $
                    { Name:'CO(18-17)',       Freq: 2070.6159930D      } , $
                    { Name:'CO(19-18)',       Freq: 2185.1346800D      } , $
                    { Name:'CO(20-19)',       Freq: 2299.5698420D      } , $
                    { Name:'13CO(1-0)',       Freq: 110.20135D         } , $
                    { Name:'13CO(2-1)',       Freq: 220.39868D         } , $
                    { Name:'13CO(3-2)',       Freq: 330.58787D         } , $
                    { Name:'13CO(4-3)',       Freq: 440.76517D         } , $
                    { Name:'13CO(5-4)',       Freq: 550.92629D         } , $
                    { Name:'13CO(6-5)',       Freq: 661.06728D         } , $
                    { Name:'13CO(7-6)',       Freq: 771.18412D         } , $
                    { Name:'13CO(8-7)',       Freq: 881.27281D         } , $
                    { Name:'13CO(9-8)',       Freq: 991.32931D         } , $
                    { Name:'13CO(10-9)',      Freq: 1101.34960D        } , $
                    { Name:'13CO(11-10)',     Freq: 1211.32966D        } , $
                    { Name:'13CO(12-11)',     Freq: 1321.26548D        } , $
                    { Name:'13CO(13-12)',     Freq: 1431.15304D        } , $
                    { Name:'13CO(14-13)',     Freq: 1540.98832D        } , $
                    { Name:'13CO(15-14)',     Freq: 1650.76730D        } , $
                    { Name:'13CO(16-15)',     Freq: 1760.48598D        } , $
                    { Name:'13CO(17-16)',     Freq: 1870.14035D        } , $
                    { Name:'13CO(18-17)',     Freq: 1979.72639D        } , $
                    { Name:'12C18O(1-0)',     Freq: 109.78217D         } , $
                    { Name:'12C18O(2-1)',     Freq: 219.56035D         } , $
                    { Name:'12C18O(3-2)',     Freq: 329.33055D         } , $
                    { Name:'12C18O(4-3)',     Freq: 439.08877D         } , $
                    { Name:'12C18O(5-4)',     Freq: 548.83101D         } , $
                    { Name:'12C18O(6-5)',     Freq: 658.55328D         } , $
                    { Name:'12C18O(7-6)',     Freq: 768.25159D         } , $
                    { Name:'12C18O(8-7)',     Freq: 877.92196D         } , $
                    { Name:'12C18O(9-8)',     Freq: 987.56020D         } , $
                    { Name:'12C18O(10-9)',    Freq: 1097.16350D        } , $
                    { Name:'12C18O(11-10)',   Freq: 1206.72470D        } , $
                    { Name:'12C18O(12-11)',   Freq: 1316.24440D        } , $
                    { Name:'12C18O(13-12)',   Freq: 1425.71540D        } , $
                    { Name:'12C18O(14-13)',   Freq: 1535.13330D        } , $
                    { Name:'12C18O(15-14)',   Freq: 1644.49730D        } , $
                    { Name:'12C18O(16-15)',   Freq: 1753.79998D        } , $
                    { Name:'12C18O(17-16)',   Freq: 1863.03936D        } , $
                    { Name:'12C18O(18-17)',   Freq: 1972.21087D        } , $
                    { Name:'HCN(1-0)',        Freq: 88.6316023D        } , $
                    { Name:'HCN(2-1)',        Freq: 177.2611115D       } , $
                    { Name:'HCN(3-2)',        Freq: 265.8864343D       } , $
                    { Name:'HCN(4-3)',        Freq: 354.5054779D       } , $
                    { Name:'HCN(5-4)',        Freq: 443.1161493D       } , $
                    { Name:'HCN(6-5)',        Freq: 531.7163479D       } , $
                    { Name:'HCN(7-6)',        Freq: 620.3040022D       } , $
                    { Name:'HCN(8-7)',        Freq: 708.8770051D       } , $
                    { Name:'HCN(9-8)',        Freq: 797.4332623D       } , $
                    { Name:'HCN(10-9)',       Freq: 885.9706949D       } , $
                    { Name:'HNC(1-0)',        Freq: 90.66356D          } , $
                    { Name:'HNC(2-1)',        Freq: 181.32473D         } , $
                    { Name:'HNC(3-2)',        Freq: 271.98111D         } , $
                    { Name:'HNC(4-3)',        Freq: 362.63030D         } , $
                    { Name:'HNC(5-4)',        Freq: 453.26992D         } , $
                    { Name:'HNC(6-5)',        Freq: 543.89755D         } , $
                    { Name:'HNC(7-6)',        Freq: 634.51083D         } , $
                    { Name:'HNC(8-7)',        Freq: 725.10734D         } , $
                    { Name:'HNC(9-8)',        Freq: 815.68468D         } , $
                    { Name:'HNC(10-9)',       Freq: 906.24046D         } , $
                    { Name:'HCO+(1-0)',       Freq: 89.18852D          } , $
                    { Name:'HCO+(2-1)',       Freq: 178.37501D         } , $
                    { Name:'HCO+(3-2)',       Freq: 267.55753D         } , $
                    { Name:'HCO+(4-3)',       Freq: 356.73413D         } , $
                    { Name:'HCO+(5-4)',       Freq: 445.90272D         } , $
                    { Name:'HCO+(6-5)',       Freq: 535.06140D         } , $
                    { Name:'HCO+(7-6)',       Freq: 624.20818D         } , $
                    { Name:'HCO+(8-7)',       Freq: 713.34123D         } , $
                    { Name:'HCO+(9-8)',       Freq: 802.45820D         } , $
                    { Name:'HCO+(10-9)',      Freq: 891.55729D         } , $
                    { Name:'H2O(110-101)',    Freq: 556.93599D         } , $
                    { Name:'H2O(111-000)',    Freq: 1113.34301D        } , $
                    { Name:'H2O(202-111)',    Freq: 987.92676D         } , $
                    { Name:'H2O(211-202)',    Freq: 752.03314D         } , $
                    { Name:'H2O(212-101)',    Freq: 1669.90477D        } , $
                    { Name:'H2O(220-211)',    Freq: 1228.78872D        } , $
                    { Name:'H2O(221-212)',    Freq: 1661.00764D        } , $
                    { Name:'H2O(302-212)',    Freq: 1716.76963D        } , $
                    { Name:'H2O(312-221)',    Freq: 1153.12682D        } , $
                    { Name:'H2O(312-303)',    Freq: 1097.36479D        } , $
                    { Name:'H2O(321-312)',    Freq: 1162.91160D        } , $
                    { Name:'H2O(322-313)',    Freq: 1919.35953D        } , $
                    { Name:'H2O(331-404)',    Freq: 1893.68651D        } , $
                    { Name:'H2O(413-404)',    Freq: 1602.21937D        } , $
                    { Name:'H2O(422-331)',    Freq: 916.17158D         } , $
                    { Name:'H2O(422-413)',    Freq: 1207.63873D        } , $
                    { Name:'H2O(423-330)',    Freq: 448.00108D         } , $
                    { Name:'H2O(432-505)',    Freq: 1713.88297D        } , $
                    { Name:'H2O(523-432)',    Freq: 1918.48535D        } , $
                    { Name:'H2O(523-514)',    Freq: 1410.61807D        } , $
                    { Name:'H2O(524-431)',    Freq: 970.31505D         } , $
                    { Name:'H2O(532-441)',    Freq: 620.70095D         } , $
                    { Name:'H2O(624-615)',    Freq: 1794.78895D        } , $
                    { Name:'H2O(625-523)',    Freq: 1322.06480D        } , $
                    { Name:'H2O(633-542)',    Freq: 1541.96701D        } , $
                    { Name:'H2O(633-624)',    Freq: 1762.04279D        } , $
                    { Name:'H2O(634-541)',    Freq: 1158.32385D        } , $
                    { Name:'[CI](2-1)',       Freq: 809.34197D         } , $
                    { Name:'[CI](1-0)',       Freq: 492.16065D         } , $
                    { Name:'[CII]158',        Freq: 1900.53690D        } , $
                    { Name:'[OI]63',          Freq: 4744.77510D        } , $
                    { Name:'[OI]146',         Freq: 2060.06886D        } , $
                    { Name:'[OIII]51',        Freq: 5785.87959D        } , $
                    { Name:'[OIII]88',        Freq: 3393.00624D        } , $
                    { Name:'[NII]122',        Freq: 2459.38010D        } , $
                    { Name:'[NII]205',        Freq: 1461.13141D        }   ]
    
    
    LineMatch = STREGEX(LabLineData.Name, LineNamePattern[0], /BOOLEAN)
    IF N_ELEMENTS(LineNamePattern) GT 1 THEN BEGIN
        FOREACH LineNamePatternOne, LineNamePattern DO BEGIN
            LineMatch = (LineMatch OR STREGEX(LabLineData.Name, LineNamePatternOne, /BOOLEAN))
        ENDFOREACH
    ENDIF
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
            LinePlotXLength = !X.CRANGE[1] - !X.CRANGE[0]
            LinePlotYLength = !Y.CRANGE[1] - !Y.CRANGE[0]
            LinePlotYRange = [!Y.CRANGE[1] - 0.55*LinePlotYLength, !Y.CRANGE[1] - 0.02*LinePlotYLength]
            IF N_ELEMENTS(PlotYRange) EQ 2 THEN BEGIN
            LinePlotYRange = [!Y.CRANGE[0] + PlotYRange[0]*LinePlotYLength, !Y.CRANGE[0] + PlotYRange[1]*LinePlotYLength]
            ENDIF
            IF !D.NAME EQ 'PS' THEN LinePlotThick = 4.0 ELSE LinePlotThick = 2.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharThick = 4.0 ELSE LinePlotCharThick = 2.0
            IF !D.NAME EQ 'PS' THEN LinePlotCharSize = 0.8 ELSE LinePlotCharSize = 1.2
            
            MESSAGE, "Labelling "+STRING(FORMAT='(I0)',N_ELEMENTS(LineFreqList))+" spec line names", /CONTINUE
            
            ; line redshift
            IF N_ELEMENTS(LineRedshift) EQ 0 THEN BEGIN
                LineRedshift = 0.0
            ENDIF
            
            FOR LinePlotIndex=0,N_ELEMENTS(LineFreqList)-1 DO BEGIN
                
                IF LinePlotIndex LE N_ELEMENTS(PlotColor)-1 THEN LinePlotColor=PlotColor[LinePlotIndex] ELSE LinePlotColor='FF00FF'xL
                
                IF N_ELEMENTS(PlotColor) EQ 1 THEN LinePlotColor=PlotColor
                
                IF N_ELEMENTS(PlotLineStyle) EQ 0 THEN PlotLineStyle = 1
                
                IF KEYWORD_SET(PlotWavelength) THEN BEGIN
                    ; wavelength unit default is mm, but can set PlotWavelength = 1e-10 to plot Angstrom
                    UnitWavelength = DOUBLE(PlotWavelength)*1e3 ; default is mm
                    XYOUTS, 0, 0, LineNameList[LinePlotIndex]+' ', FONT=1, CHARSIZE=-1, WIDTH=TextStw & TextPlotYRange = [LinePlotYRange[0],LinePlotYRange[1]-TextStw*1.09*LinePlotYLength*!D.X_SIZE/!D.Y_SIZE]
                    PLOTS, [LineWaveList[LinePlotIndex]*(1.0+LineRedshift)/UnitWavelength,$
                            LineWaveList[LinePlotIndex]*(1.0+LineRedshift)/UnitWavelength],LinePlotYRange, LINESTYLE=PlotLineStyle, COLOR=LinePlotColor, Thick=LinePlotThick
                    XYOUTS, LineWaveList[LinePlotIndex]*(1.0+LineRedshift)/UnitWavelength, LinePlotYRange[1], LineNameList[LinePlotIndex], ALIGNMENT=1.0, ORIENTATION=90, FONT=1, $
                            CHARSIZE=LinePlotCharSize, CHARTHICK=LinePlotCharThick, COLOR=LinePlotColor, /NOCLIP
                ENDIF ELSE BEGIN
                    UnitFrequency = DOUBLE(1.0) ; default is GHz
                    XYOUTS, 0, 0, LineNameList[LinePlotIndex]+' ', FONT=1, CHARSIZE=-1, WIDTH=TextStw & TextPlotYRange = [LinePlotYRange[0],LinePlotYRange[1]-TextStw*1.09*LinePlotYLength*!D.X_SIZE/!D.Y_SIZE]
                    PLOTS, [LineFreqList[LinePlotIndex]/(1.0+LineRedshift)/UnitFrequency,$
                            LineFreqList[LinePlotIndex]/(1.0+LineRedshift)/UnitFrequency], LinePlotYRange, LINESTYLE=PlotLineStyle, COLOR=LinePlotColor, Thick=LinePlotThick
                    XYOUTS, LineFreqList[LinePlotIndex]/(1.0+LineRedshift)/UnitFrequency, LinePlotYRange[1], LineNameList[LinePlotIndex], ALIGNMENT=1.0, ORIENTATION=90, FONT=1, $
                            CHARSIZE=LinePlotCharSize, CHARTHICK=LinePlotCharThick, COLOR=LinePlotColor, /NOCLIP
                ENDELSE
            ENDFOR
        ENDIF
    ENDIF
    
END
