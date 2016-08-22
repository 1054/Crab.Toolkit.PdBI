; 
; This code will fill a spectrum
; 
PRO CrabSpecCalcRMS, flux, output_rms, output_sigma, output_mean, IndexArray = output_index_array
    
    ; check input
    IF N_ELEMENTS(flux) EQ 0 THEN MESSAGE, 'CrabSpecCalcRMS: Error! flux contains no data!'
    
    ; iteratively remove lines and use only line-free data
    temp_flux = flux
    temp_rms = 9.0
    next_rms = 0.0
    next_indice = WHERE(FINITE(flux),/NULL)
    
    WHILE (temp_rms - next_rms GT 3e-3*temp_rms) DO BEGIN
        
        temp_flux = temp_flux[next_indice]
        
        temp_mean = MEAN(temp_flux,/DOUBLE,/NAN)
        temp_rms = STDDEV(temp_flux,/DOUBLE,/NAN)
        temp_sigma = STDDEV(temp_flux-temp_mean,/DOUBLE,/NAN)
        temp_3sigma = 3.0*temp_sigma
        temp_indice = WHERE(temp_flux LT temp_3sigma,/NULL)
        
        next_flux = temp_flux[temp_indice]
        
        next_mean = MEAN(next_flux,/DOUBLE)
        next_rms = STDDEV(next_flux,/DOUBLE)
        next_sigma = STDDEV(next_flux-next_mean,/DOUBLE)
        next_3sigma = 3.0*next_sigma
        next_indice = WHERE(next_flux LT next_3sigma,/NULL)
        
    ENDWHILE
    
    output_mean = next_mean
    output_rms = next_rms
    output_sigma = next_sigma
    output_index_array = next_indice
    
END
