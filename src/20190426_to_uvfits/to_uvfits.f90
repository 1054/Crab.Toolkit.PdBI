subroutine to_uvfits(fits,check,error)
  use gildas_def
  use gbl_message
  use image_def
  use gio_dependencies_interfaces, no_interface=>gr8_trie
  use gio_interfaces, except_this=>to_uvfits
  use gio_fitsdef
  !---------------------------------------------------------------------
  ! @ private
  ! FITS        Internal routine.
  !     Write current UV data on tape.
  !---------------------------------------------------------------------
  type(gildas), intent(in)  :: fits   !
  logical,      intent(in)  :: check  ! Verbose flag
  logical,      intent(out) :: error  ! Error flag
  ! Global
  include 'gbl_memory.inc'
  ! Local
  character(len=*), parameter :: rname='TO_UVFITS'
  integer(kind=address_length) :: k, kd, l
  integer :: nchan, iv
  real :: rmin, rmax, umin, umax, vmin, vmax, wmin, wmax, pmax, ps
  real :: jmin
  ! To sort visibilities versus time (to build fits file for aips++)
  integer(kind=size_length) :: length
  integer ::   ier
  logical ::   error_sort
  integer(kind=address_length) :: addr,ip_work,ip_key
  real ::      maxbas
  integer ::   maxa
  character(len=message_length) :: mess
  character(len=8) :: telescop
  !<20190426><dzliu>! ------------- ADDED BELOW
  integer, dimension(:), allocatable :: ListOfAntennae
  integer :: iListOfAntennae
  integer :: CheckAntenna
  real*4 :: IdOfOneAntennaAsReal ! 4-byte float value in *.uvt binary file
  integer :: IdOfOneAntenna ! integer value, note that this Id is 0-based. 
  allocate(ListOfAntennae(0))
  !<20190426><dzliu>! -------------
  !
  error = .false.
  length = 0
  ! Code:
  !
  pmax = -1.e37
  ps = 1.
  rmax = -1.e37
  umin = +1.e37
  umax = -1.e37
  vmin = +1.e37
  vmax = -1.e37
  jmin = 100000
  maxa   = 2                   ! minimum number of antenna
  !
  ! Loop on visibility points
  kd = gag_pointer(fits%loca%addr,memory)
  nchan = (fits%gil%dim(1)-7)/3
  do iv=1, fits%gil%dim(2)
    l = kd + 6
    k = kd + 7
    call swap_antenna(memory(kd),memory(k),nchan)
    call maxdaps(memory(kd),umin,umax,vmin,vmax,jmin)
    call maxvis(memory(k),nchan,rmax,pmax,fits%gil%bval)
    call maxant(memory(l),maxa)
    !<20190426><dzliu>! ------------- ADDED BELOW
    CheckAntenna = 0 ! search current antenna Id at memory address "&(l-1)" in "ListOfAntennae" array
    IdOfOneAntennaAsReal = transfer(memory(l-1), IdOfOneAntennaAsReal) ! bitwise type cast memory(l-1) as a real*4 number
    IdOfOneAntenna = int(IdOfOneAntennaAsReal)
    do iListOfAntennae = 1, size(ListOfAntennae)
        if (ListOfAntennae(iListOfAntennae).eq.IdOfOneAntenna) then
            CheckAntenna = 1
            exit
        endif
    enddo
    if (CheckAntenna.eq.0) then
        write(mess,*) 'Found antenna : ', IdOfOneAntenna
        call gio_message(seve%i,rname,mess)
        ListOfAntennae = [ListOfAntennae, IdOfOneAntenna]
    endif
    !
    CheckAntenna = 0 ! search current antenna Id at memory address "&l" in "ListOfAntennae" array
    IdOfOneAntennaAsReal = transfer(memory(l), IdOfOneAntennaAsReal) ! bitwise type cast memory(l) as a real*4 number
    IdOfOneAntenna = int(IdOfOneAntennaAsReal)
    do iListOfAntennae = 1, size(ListOfAntennae)
        if (ListOfAntennae(iListOfAntennae).eq.IdOfOneAntenna) then
            CheckAntenna = 1
            exit
        endif
    enddo
    if (CheckAntenna.eq.0) then
        ListOfAntennae = [ListOfAntennae, IdOfOneAntenna]
        write(mess,*) 'Found antenna : ', IdOfOneAntenna
        call gio_message(seve%i,rname,mess)
    endif
    !<20190426><dzliu>! -------------
    kd = kd + fits%gil%dim(1)
  enddo
  wmin= -1
  wmax= +1
  write(mess,*) 'Extremum : ', rmax
  call gio_message(seve%i,rname,mess)
  write(mess,*) 'Maximum weight : ',pmax
  call gio_message(seve%i,rname,mess)
  write(mess,*) 'Extrema : ',umin,umax,vmin,vmax
  call gio_message(seve%i,rname,mess)
  rmin = -rmax
  ps = rmax/pmax
  write(mess,*) 'Weight Scale ',ps
  call gio_message(seve%i,rname,mess)
  !
  ! Write header
  if (fits%gil%version_uv.ge.code_version_uvt_syst) then
    telescop = 'NOEMA'
  else
    telescop = 'IRAM PDB'
  endif
  !<20190426><dzliu>! ------------- ADDED
  if (fits%gil%nteles.gt.0) then
    telescop = fits%gil%teles(1)%ctele
  endif
  !<20190426><dzliu>! -------------
  call wr_fitshead(fits,rmin,rmax,umin,umax,vmin,vmax,wmin,wmax, &
    & jmin,nchan,ps,telescop,check,error)
  if (error) return
  maxbas = maxa*257             ! Allow MAXA antennas
  !
  ! Order data according to time (if AIPS style)
  if (a_style.eq.code_fits_aips.and.sort) then
    length = (2+fits%gil%dim(1))*fits%gil%dim(2)
    ier = sic_getvm(length,addr)
    if (ier.ne.1) then
      call gio_message(seve%e,rname,'Memory allocation failure')
      error = .true.
      return
    endif
    ip_key  = gag_pointer(addr,memory)
    ip_work = ip_key+2*fits%gil%dim(2)
    kd = gag_pointer(fits%loca%addr,memory)
    do iv=0,2*(fits%gil%dim(2)-1),2
      call compute_time(memory(kd),memory(ip_work+iv),jmin,maxbas)
      kd = kd + fits%gil%dim(1)
    enddo
    !
    call gr8_trie(memory(ip_work),memory(ip_key),fits%gil%dim(2),error_sort)
    kd = gag_pointer(fits%loca%addr,memory)
    call sort_visi(memory(kd),memory(ip_work),memory(ip_key), &
      & fits%gil%dim(1),fits%gil%dim(2))
    !
    kd = ip_work
  else
    kd = gag_pointer(fits%loca%addr,memory)
  endif
  !
  ! Loop to write the visibilities
  fd%nb = 0
  do iv=1, fits%gil%dim(2)
    k = kd + 7
    call write_visi (memory(kd),memory(k),nchan,jmin,ps,error)
    if (error) goto 99
    kd = kd + fits%gil%dim(1)
  enddo
  call fitreal_end(fd,error)
  if (error) goto 99
  !
  ! Write special extension for aips++
  if (a_style.eq.code_fits_aips) then
    write(mess,*) 'Number of antennas : ',maxa
    call gio_message(seve%i,rname,mess)
    call gio_message(seve%i,rname,'AIPS style')
    call write_extension(check,error,maxa)
  endif
  call fitreal_end(fd,error)
  if (length.ne.0) call free_vm(length,addr)
  return
  !
99 error = .true.
  if (length.ne.0) call free_vm(length,addr)
  return
end subroutine to_uvfits
!
subroutine swap_antenna(daps,visi,nchan)
  !---------------------------------------------------------------------
  ! @ no-interface
  ! Swap antenna if necessary: AIPS and MIRIAD are expecting a1<a2.
  ! This may not be the case if the UV table has been sorted.
  !---------------------------------------------------------------------
  real :: daps(7)                   !
  integer :: nchan                  !
  real :: visi(3,nchan)             !
  ! Local
  real :: tmp
  integer :: i
  !
  if (daps(6).gt.daps(7)) then
    daps(1) = -daps(1)         ! U
    daps(2) = -daps(2)         ! V
    tmp = daps(6)
    daps(6) = daps(7)          ! A1
    daps(7) = tmp              ! A2
    do i = 1,nchan
      visi(2,i) = -visi(2,i)   ! Imaginary part
    enddo
  endif
end subroutine swap_antenna
!
subroutine maxant(antenna, maxa)
  !---------------------------------------------------------------------
  ! @ no-interface
  ! Get maximum antenna number
  !---------------------------------------------------------------------
  real :: antenna                   !
  integer :: maxa                   !
  !
  maxa = max(antenna,real(maxa))
end subroutine maxant
!
subroutine maxvis (visi, nchan, rmax, pmax, blank)
  !---------------------------------------------------------------------
  ! @ no-interface
  ! Get maximum visibility and weight
  !---------------------------------------------------------------------
  integer :: nchan                  !
  real :: visi(3,nchan)             !
  real :: rmax                      !
  real :: pmax                      !
  real :: blank                     !
  ! Local
  real :: a
  integer :: i, j
  !
  do i=1, nchan
    a = 0
    do j=1,2
      if (visi(j,i).ne.blank) a = a + visi(j,i)**2
    enddo
    a = sqrt(a)
    rmax = max(a,rmax)
    if (visi(3,i).ne.blank) pmax = max(pmax,visi(3,i))
  enddo
end subroutine maxvis
!
subroutine maxdaps(daps,umin,umax,vmin,vmax,jmin)
  !---------------------------------------------------------------------
  ! @ no-interface
  !---------------------------------------------------------------------
  real :: daps(7)                   !
  real :: umin                      !
  real :: umax                      !
  real :: vmin                      !
  real :: vmax                      !
  real :: jmin                      !
  !
  umin = min(umin,daps(1))
  umax = max(umax,daps(1))
  vmin = min(vmin,daps(2))
  vmax = max(vmax,daps(2))
  jmin = min(jmin,daps(4))
end subroutine maxdaps
!
subroutine write_visi(daps,visi,nchan,jmin,ps,error)
  use gio_fitsdef
  !---------------------------------------------------------------------
  ! @ no-interface
  ! FITS        Internal routine.
  !     Write one visibility on tape.
  !---------------------------------------------------------------------
  real :: daps(7)                  !
  integer :: nchan                 !
  real :: visi(3,nchan)            !
  real :: jmin                     !
  real :: ps                       !
  logical, intent(inout) :: error  !
  ! Local
  integer :: i
  real :: time, date, base, weight
  !
  ! Write daps
  call fitreal(fd,1,daps(1),uscal,uzero,error)
  if (error) return
  call fitreal(fd,1,daps(2),vscal,vzero,error)
  if (error) return
  ! CALL FITREAL(fd,1,DAPS(3),WSCAL,WZERO,ERROR)
  call fitreal(fd,1,0.0,wscal,wzero,error)
  if (error) return
  base = 256*daps(6) + daps(7) !<20190426><dzliu>! Note that here will be buggy if N_antenna > 256!
  call fitreal(fd,1,base,1.0,0.0,error)
  if (error) return
  time = daps(4) - jmin + daps(5)/86400.
  date = 0.25*int(4*time)
  time = time-date
  call fitreal(fd,1,date,0.25,0.0,error)
  if (error) return
  call fitreal(fd,1,time,tscal,tzero,error)
  if (error) return
  !
  ! Write data
  do i=1, nchan
    call fitreal(fd,2,visi(1,i),cscal,czero,error)    ! Data
    if (error) return
    weight = visi(3,i)*ps
    call fitreal(fd,1,weight,cscal,czero,error) ! Weight
    if (error) return
  enddo
end subroutine write_visi
!
subroutine compute_time(daps,t,jmin,maxbas)
  use gio_fitsdef
  !---------------------------------------------------------------------
  ! @ no-interface
  ! Compute time
  !---------------------------------------------------------------------
  real, intent(in) ::   daps(7)                 ! Data Associated Parameters
  real(8), intent(out) :: t                     ! Current time
  real, intent(in) ::   jmin                    ! Minimum date
  real, intent(in) ::   maxbas                  ! Maximum baseline
  !
  t = daps(4) - jmin + daps(5)/86400. + (daps(6)*256+daps(7))/86400/maxbas
end subroutine compute_time
!
subroutine sort_visi(x,xwork,key,dim1,dim2)
  use gildas_def
  !---------------------------------------------------------------------
  ! @ no-interface
  ! Sort visibility records
  !---------------------------------------------------------------------
  integer(kind=index_length), intent(in) :: dim1  !
  integer(kind=index_length), intent(in) :: dim2  !
  real :: x(dim1,dim2)              !
  real :: xwork(dim1,dim2)          !
  integer :: key(dim2)              !
  ! Local
  integer(kind=index_length) :: i,j
  !
  do j=1,dim2
    do i=1,dim1
      xwork(i,j) = x(i,key(j))
    enddo
  enddo
end subroutine sort_visi
!
subroutine wr_fitshead(fits,rmin,rmax,umin,umax,vmin,vmax,wmin,wmax,jmin,  &
  nchan,ps,telescop,check,error)
  use phys_const
  use gbl_message
  use image_def
  use gio_dependencies_interfaces
  use gio_interfaces, except_this=>wr_fitshead
  use gio_fitsdef
  !---------------------------------------------------------------------
  ! @ private
  ! UVFITS
  !     Write the FITS header for a visibility set.
  !---------------------------------------------------------------------
  type(gildas),     intent(in)  :: fits       !
  real(kind=4),     intent(in)  :: rmin,rmax  !
  real(kind=4),     intent(in)  :: umin,umax  !
  real(kind=4),     intent(in)  :: vmin,vmax  !
  real(kind=4),     intent(in)  :: wmin,wmax  !
  real(kind=4),     intent(in)  :: jmin       !
  integer(kind=4),  intent(in)  :: nchan      !
  real(kind=4),     intent(in)  :: ps         ! Weight scaling factor
  character(len=*), intent(in)  :: telescop   !
  logical,          intent(in)  :: check      !
  logical,          intent(out) :: error      !
  ! Local
  real(kind=4), parameter :: epsr4=1e-7  ! Relative precision of REAL*4
  character(len=80) :: line
  character(len=23) :: date
  real(kind=4) :: freq_resolution
  real(kind=8) :: factor
  real(kind=8) :: c=clight
  !
  ! Make sure we have the right representation of UV table
  if (fits%gil%column_pointer(code_uvt_topo).ne.0) then
    call gio_message(seve%e,'TO_UVFITS', &
    & 'Table has Doppler tracking column, information lost in UVFITS')
    error = .true.
    return
  endif
  !
  if (fd%snbit.eq.16) then
    factor = 1.01d0 / 32767.d0 / 2.d0
  elseif (fd%snbit.eq.32) then
    factor = 1.01d0 / 2147483647.d0 / 2.d0
  elseif (fd%snbit.eq.-32) then
    factor = 1.0d0
  else
    error = .true.
    return
  endif
  call gfits_put ('SIMPLE  =                    T         /',check,error)
  if (error) return
  write (line,10) 'BITPIX  =           ',fd%snbit
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Defines 6 different axis, 7 for AIPS...
  !
  if (a_style.eq.code_fits_aips) then
    call gfits_put ('NAXIS   =                    7         /',check,error)
  else
    call gfits_put ('NAXIS   =                    6         /',check,error)
  endif
  if (error) return
  ! No standard image, just groups.
  call gfits_put ('NAXIS1  =                    0         /',check,error)
  if (error) return
  ! Complex
  call gfits_put ('NAXIS2  =                    3         /',check,error)
  if (error) return
  ! Stokes
  call gfits_put ('NAXIS3  =                    1         /',check,error)
  if (error) return
  ! Frequency
  write (line,10) 'NAXIS4  =           ',nchan
  call gfits_put (line,check,error)
  if (error) return
  ! RA
  call gfits_put ('NAXIS5  =                    1         /',check,error)
  if (error) return
  ! DEC
  call gfits_put ('NAXIS6  =                    1         /',check,error)
  if (error) return
  ! IF
  if (a_style.eq.code_fits_aips) then
    call gfits_put ('NAXIS7  =                    1         /',check,error)
    if (error) return
  endif
  !
  call gfits_put ("TELESCOP= '"//telescop//"'                   /",check,error)
  if (error) return
  call gfits_put ('EXTEND  =                    T         /',check,error)
  if (error) return
  !
  ! Compute extrema, and determine optimal scaling.
  if (fd%snbit.ne.-32) then
    cscal = (rmax - rmin) * factor
    czero  = (rmin+rmax)*0.5
  else
    cscal = 1.0
    czero = 0.0
  endif
  if (fd%snbit.eq.16) then
    write (line,10) 'BLANK   =           ',32767,'Blanking value'
    call gfits_put (line,check,error)
  elseif (fd%snbit.eq.32) then
    write (line,10) 'BLANK   =           ',2147483647,'Blanking value'
    call gfits_put (line,check,error)
  endif
  if (error) return
  write (line,20) 'BSCALE  = ',cscal
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'BZERO   = ',czero
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'DATAMIN = ',rmin
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'DATAMAX = ',rmax
  call gfits_put (line,check,error)
  if (error) return
  call gfits_put ('BUNIT   = ''JY      ''                   /',check,error)
  if (error) return
  !
  ! Coordinates of pointing centre need not be the same as phase centre.
  write (line,20) 'EQUINOX = ',fits%gil%epoc,'Equinox of coordinates'
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'OBSRA   = ',180.d0*fits%gil%ra/pi,'Pointing centre RA'
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'OBSDEC  = ',180.d0*fits%gil%dec/pi,'Pointing centre DEC'
  call gfits_put (line,check,error)
  if (error) return
  !
  !  Description af axes. No first axis for UVFITS.
  call gfits_put ('CTYPE2  = ''COMPLEX ''                   /',check,error)
  if (error) return
  call gfits_put ('CRVAL2  =      1.0000000000000         /',check,error)
  if (error) return
  call gfits_put ('CDELT2  =      1.0000000000000         /',check,error)
  if (error) return
  call gfits_put ('CRPIX2  =      1.0000000000000         /',check,error)
  if (error) return
  call gfits_put ('CROTA2  =      0.0000000000000         /',check,error)
  if (error) return
  !
  call gfits_put ('CTYPE3  = ''STOKES  ''                   /',check,error)
  if (error) return
  if (a_style.ne.code_fits_aips) then
    call gfits_put ('CRVAL3  =      1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CDELT3  =      1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CRPIX3  =      1.0000000000000         /',check,error)
    if (error) return
  else
    call gfits_put ('CRVAL3  =     -1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CDELT3  =     -1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CRPIX3  =      1.0000000000000         /',check,error)
    if (error) return
  endif
  call gfits_put ('CROTA3  =      0.0000000000000         /',check,error)
  if (error) return
  !
  ! Observing frequency (upper side band ?..)
  ! Should be the Observatory Frequency
  call gfits_put ('CTYPE4  = ''FREQ    ''                   /',check,error)
  if (error) return
  write (line,20) 'CRVAL4  = ',fits%gil%freq*1d6,'Frequency in Hz'
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Frequency resolution is here
  freq_resolution = fits%gil%fres*1d6 
  write (line,20) 'CDELT4  = ',freq_resolution,'Frequency Resolution in Hz'
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'CRPIX4  = ',fits%gil%ref(1),'Reference channel '
  call gfits_put (line,check,error)
  if (error) return
  call gfits_put ('CROTA4  =      0.0000000000000         /',check,error)
  if (error) return
  !
  ! Coordinates of phase tracking center. Assume Equatorial in present version.
  call gfits_put ('CTYPE5  = ''RA      ''                   /',check,error)
  if (error) return
  write (line,20) 'CRVAL5  = ',180.d0*fits%gil%a0/pi,'Right Ascension'
  call gfits_put (line,check,error)
  if (error) return
  call gfits_put ('CDELT5  =      1.0000000000000         /',check,error)
  if (error) return
  call gfits_put ('CRPIX5  =      1.0000000000000         /',check,error)
  if (error) return
  ! What happens for rotated UV data ?
  call gfits_put ('CROTA5  =      0.0000000000000         /',check,error)
  if (error) return
  !
  call gfits_put ('CTYPE6  = ''DEC     ''                   /',check,error)
  if (error) return
  write (line,20) 'CRVAL6  = ',180.d0*fits%gil%d0/pi,'Declination'
  call gfits_put (line,check,error)
  if (error) return
  call gfits_put ('CDELT6  =      1.0000000000000         /',check,error)
  if (error) return
  call gfits_put ('CRPIX6  =      1.0000000000000         /',check,error)
  if (error) return
  ! What happens for rotated UV data ?
  call gfits_put ('CROTA6  =      0.0000000000000         /',check,error)
  if (error) return
  if (a_style.eq.code_fits_aips) then
    call gfits_put ('CTYPE7  = ''IF      ''                   /',check,error)
    if (error) return
    call gfits_put ('CRVAL7  =      1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CDELT7  =      1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CRPIX7  =      1.0000000000000         /',check,error)
    if (error) return
    call gfits_put ('CROTA7  =      0.0000000000000         /',check,error)
    if (error) return
  endif
  !
  ! Miscellaneous
  write (line,30) 'OBJECT  = ',fits%char%name
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Spectral line information
  write (line,30) 'LINE    = ',fits%char%line,'Line name'
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'RESTFREQ= ', fits%gil%freq*1d6, 'Rest frequency'
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Check here for velocity referential. 
  call gfits_put ('SPECSYS = ''SOURCE  ''                   /',check,error) 
  call gfits_put ('SSYSOBS = ''TOPOCENT''                   /',check,error) 
  if (fits%gil%vtyp.eq.vel_lsr) then
    call gfits_put ('SSYSSRC = ''LSRK    ''                   /',check,error) 
    write(line,20)  'ZSOURCE = ',fits%gil%voff*1d3  ! km/s to m/s
    call gfits_put(line,check,error)
  elseif (fits%gil%vtyp.eq.vel_hel) then
    call gfits_put ('SSYSSRC = ''BARYCENT''                   /',check,error) 
    write(line,20)  'ZSOURCE = ',fits%gil%voff*1d3  ! km/s to m/s
    call gfits_put(line,check,error)
  elseif (fits%gil%vtyp.eq.vel_obs) then
    call gfits_put ('SSYSSRC = ''TOPOCENT''                   /',check,error) 
    write(line,20)  'ZSOURCE = ',fits%gil%voff*1d3  ! km/s to m/s
    call gfits_put(line,check,error)
  elseif (fits%gil%vtyp.eq.vel_ear) then
    call gfits_put ('SSYSSRC = ''GEOCENT ''                   /',check,error) 
    write(line,20)  'ZSOURCE = ',fits%gil%voff*1d3  ! km/s to m/s
    call gfits_put(line,check,error)
  endif
  write(line,20)  'VELOSYS = ',fits%gil%dopp*299792458d0  !  m/s
  call gfits_put(line,check,error)
  !
  ! New ISO Date Format
  call sic_isodate(date)
  write (line,13) 'DATE    = ',trim(date),'Date written'
  call gfits_put(line,check,error)
  if (error) return
  ! Write new ISO DATE FORMAT
  call gfits_put('TIMESYS = ''UTC             ''           /',check,error)
  if (error) return
  call gag_mjd2isodate(dble(gagzero_in_mjd+jmin),date,error)
  if (error) return
  write (line,13) 'DATE-OBS= ',trim(date),'Date observed'
  call gfits_put(line,check,error)
  if (error) return
  call gfits_put ('ORIGIN  = ''GILDAS-NOEMA    ''           /',check,error) 
  !
  ! UVFITS specific information
  ! Indicate extension to FITS is UVFITS
  call gfits_put ('GROUPS  =                    T         /',check,error)
  if (error) return
  !
  ! Number of integers in one DAP record
  write (line,10) 'PCOUNT  =           ',6
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Number of visibilities
  write (line,10) 'GCOUNT  =           ',fits%gil%dim(2)
  call gfits_put (line,check,error)
  if (error) return
  !
  ! First DAP is U. Units are seconds  of time.
  call gfits_put ('PTYPE1  = ''UU      ''                   /',check,error)
  if (error) return
  if (fd%snbit.eq.-32) then
    uscal = 1.0
    uzero = 0.0
  else
    uscal = (umax - umin) * factor
    uzero = (umin+umax)*0.5
  endif
  write (line,20) 'PSCAL1  = ',uscal/c ! Convert metres to seconds
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'PZERO1  = ',uzero/c
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Second DAP is V. Units are seconds  of time.
  call gfits_put ('PTYPE2  = ''VV      ''                   /',check,error)
  if (error) return
  if (fd%snbit.eq.-32) then
    vscal = 1.0
    vzero = 0.0
  else
    vscal = (vmax - vmin) * factor
    vzero = (vmin+vmax)*0.5
  endif
  write (line,20) 'PSCAL2  = ',vscal/c
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'PZERO2  = ',vzero/c
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Third DAP is W. Units are seconds  of time.
  call gfits_put ('PTYPE3  = ''WW      ''                   /',check,error)
  if (error) return
  if (fd%snbit.eq.-32) then
    wscal = 1.0
    wzero = 0.0
  else
    wscal = (wmax - wmin) * factor
    wzero = (wmin+wmax)*0.5
  endif
  write (line,20) 'PSCAL3  = ',wscal/c
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'PZERO3  = ',wzero/c
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Fourth DAP is baseline number (256*ANT1+ANT2+(ARRAY#-1)/100).
  call gfits_put ('PTYPE4  = ''BASELINE''                   /',check,error)
  if (error) return
  write (line,20) 'PSCAL4  = ',1.d0
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'PZERO4  = ',0.d0
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Fifth DAP is observing day (Julian Date)
  call gfits_put ('PTYPE5  = ''DATE    ''                   /',check,error)
  if (error) return
  write (line,20) 'PSCAL5  = ',0.25d0
  call gfits_put (line,check,error)
  if (error) return
  ! This is the offset between Julian day numbers and CLIC's internal code
  write (line,20) 'PZERO5  = ',2460549.5d0+jmin
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Sixth DAP is UT (in fraction of Julian Day)
  call gfits_put ('PTYPE6  = ''DATE    ''                   /',check,error)
  if (error) return
  if (fd%snbit.eq.-32) then
    tscal = 1.0
    uzero = 0.0
  else
    tscal = factor
    tzero = 0.
  endif
  write (line,20) 'PSCAL6  = ',tscal
  call gfits_put (line,check,error)
  if (error) return
  write (line,20) 'PZERO6  = ',tzero
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Finish Header
  write (line,20) 'HISTORY   WTSCAL   ',1e6/ps  ! As units are MHz
  call gfits_put (line,check,error)
  if (error) return
  !
  call gfits_put ('END                         ',check,error)
  if (error) return
  call gfits_flush_header (error)
  !
10 format(a,i10,'         / ',a)
13 format(a,'''',a,'''',t40,'/ ',a)
20 format(a,e20.13,'         / ',a)
30 format(a,'''',a12,'''','               / ',a)
end subroutine wr_fitshead
!
subroutine write_extension(check,error,maxa)
  !<20190426><dzliu>! ----------- ADDED THE FOLLOWING LINE SO AS TO USE "call gio_message(seve%i,...)"
  use gbl_message
  !<20190426><dzliu>! -----------
  use gio_interfaces, except_this=>write_extension
  use gio_fitsdef
  !---------------------------------------------------------------------
  ! @ private
  !---------------------------------------------------------------------
  logical, intent(in)    :: check        ! Verbose flag
  logical, intent(inout) :: error        ! Error flag
  integer                :: maxa         !
  ! Local
  real(8) ::      dval
  integer ::      ival,nbit_table
  integer ::      j,iant,nant
  character(len=80) :: line
  !<20190426><dzliu>! --------------- REPLACED
  !<20190426><dzliu>! character(len=2880) :: cbuf
  !<20190426><dzliu>! --------------- WITH
  character(len=:), allocatable :: cbuf
  integer :: cbufsize
  !<20190426><dzliu>! ---------------
  !
  call gfits_put ('XTENSION= ''BINTABLE''                   / Extension type',check,error)
  if (error) return
  nbit_table = 8
  write (line,10) 'BITPIX  =           ',nbit_table,'Binary data'
  call gfits_put (line,check,error)
  if (error) return
  !
  ! Defines 2 different axis
  !
  call gfits_put ('NAXIS   =                    2         / Table is a matrix',check,error)
  if (error) return
  !
  call gfits_put ('NAXIS1  =                   70         / Width in bytes',check,error)
  if (error) return
  write (line,'(a9,i21,a33)') 'NAXIS2  =',maxa,'         / Nr of entries in table'
  call gfits_put (line,check,error)
  if (error) return
  !
  ! General parameters of table
  call gfits_put ('PCOUNT  =                    0         / Random parameter group',check,error)
  if (error) return
  call gfits_put ('GCOUNT  =                    1         / Group count',check,error)
  if (error) return
  call gfits_put ('TFIELDS =                   12         / Number of fields',check,error)
  call gfits_put ('EXTNAME = ''AIPS AN ''                   / AIPS table file',check,error)
  if (error) return
  write(line,14) 'EXTVER  =                    1         /',  &
                 ' Version number of table'
  call gfits_put (line, check,error)
  if (error) return
  !
  ! Definitions of table parameters
  write(line,14) 'TFORM1  = ''8A      ''                   /',  &
                 ' FORTRAN format of field 1'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE1  = ''ANNAME          ''           /',  &
                 ' Type (heading) of field 1'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT1  = ''        ''                   /',  &
                 ' Physical units of field 1'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM2  = ''3D      ''                   /',  &
                 ' FORTRAN format of field 2'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE2  = ''STABXYZ         ''           /',  &
                 ' Type (heading) of field 2'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT2  = ''METERS  ''                   /',  &
                 ' Physical units of field 2'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM3  = ''0D      ''                   /',  &
                 ' FORTRAN format of field 3'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE3  = ''ORBPARM         ''           /',  &
                 ' Type (heading) of field 3'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT3  = ''        ''                   /',  &
                 ' Physical units of field 3'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM4  = ''1J      ''                   /',  &
                 ' FORTRAN format of field 4'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE4  = ''NOSTA           ''           /',  &
                 ' Type (heading) of field 4'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT4  = ''        ''                   /',  &
                 ' Physical units of field 4'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM5  = ''1J      ''                   /',  &
                 ' FORTRAN format of field 5'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE5  = ''MNTSTA          ''           /',  &
                 ' Type (heading) of field 5'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT5  = ''        ''                   /',  &
                 ' Physical units of field 5'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM6  = ''1E      ''                   /',  &
                 ' FORTRAN format of field 6'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE6  = ''STAXOF          ''           /',  &
                 ' Type (heading) of field 6'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT6  = ''METERS  ''                   /',  &
                 ' Physical units of field 6'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM7  = ''1A      ''                   /',  &
                 ' FORTRAN format of field 7'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE7  = ''POLTYA          ''           /',  &
                 ' Type (heading) of field 7'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT7  = ''        ''                   /',  &
                 ' Physical units of field 7'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM8  = ''1E      ''                   /',  &
                 ' FORTRAN format of field 8'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE8  = ''POLAA           ''           /',  &
                 ' Type (heading) of field 8'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT8  = ''DEGREES ''                   /',  &
                 ' Physical units of field 8'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM9  = ''2E      ''                   /',  &
                 ' FORTRAN format of field 9'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE9  = ''POLCALA         ''           /',  &
                 ' Type (heading) of field 9'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT9  = ''        ''                   /',  &
                 ' Physical units of field 9'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM10 = ''1A      ''                   /',  &
                 ' FORTRAN format of field 10'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE10 = ''POLTYB          ''           /',  &
                 ' Type (heading) of field 10'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT10 = ''        ''                   /',  &
                 ' Physical units of field 10'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM11 = ''1E      ''                   /',  &
                 ' FORTRAN format of field 11'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE11 = ''POLAB           ''           /',  &
                 ' Type (heading) of field 11'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT11 = ''DEGREES ''                   /',  &
                 ' Physical units of field 11'
  call gfits_put (line, check, error)
  if (error) return
  !
  write(line,14) 'TFORM12 = ''2E      ''                   /',  &
                 ' FORTRAN format of field 12'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TTYPE12 = ''POLCALB         ''           /',  &
                 ' Type (heading) of field 12'
  call gfits_put (line, check,error)
  if (error) return
  write(line,14) 'TUNIT12 = ''        ''                   /',  &
                 ' Physical units of field 12'
  call gfits_put (line, check, error)
  if (error) return
  !
  ! Other parameters
  dval = 4.524e+06   ! BURE
  write(line,20) 'ARRAYX  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  dval = 0.468e+06   ! BURE
  write(line,20) 'ARRAYY  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  dval = 4.460e+06   ! BURE
  write(line,20) 'ARRAYZ  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  !
  dval = 0
  write(line,20) 'GSTIA0  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  write(line,20) 'DEGPDY  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  write(line,20) 'FREQ    = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  call gfits_put ('RDATE   = ''01/01/99''', check, error)
  if (error) return
  write(line,20) 'POLARX  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  write(line,20) 'POLARY  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  write(line,20) 'UT1UTC  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  write(line,20) 'DATUTC  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  call gfits_put ('TIMSYS  = ''IAT     ''', check, error)
  if (error) return
  call gfits_put ('ARRNAM  = ''IRAM PDB''', check, error)
  if (error) return
  ival = 0
  write (line,10) 'NUMORB  =           ',ival
  call gfits_put (line, check, error)
  if (error) return
  ival = 2
  write (line,10) 'NOPCAL  =           ',ival
  call gfits_put (line, check, error)
  if (error) return
  ival = 1
  write (line,10) 'FREQID  =           ',ival
  call gfits_put (line, check, error)
  if (error) return
  write (line,20) 'IATUTC  = ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  write(line,'(a)') 'POLTYPE = ''APPROX  '''
  call gfits_put (line, check, error)
  if (error) return
  ival = 15
  write (line,10) 'P_REFANT=           ',ival
  call gfits_put (line, check, error)
  if (error) return
  write (line,20) 'P_DIFF01= ',dval,' '
  call gfits_put (line, check, error)
  if (error) return
  !
  ! Finish Header
  call gfits_put ('END                         ',check,error)
  if (error) return
  call gfits_flush_header (error)
  if (error) return
  !
  ! Table
  !
  fd%nb = 0
  !<20190426><dzliu>! ------------- REPLACED
  !<20190426><dzliu>! do j=1,2880
  !<20190426><dzliu>!   cbuf(j:j) = char(0)  ! Fill with zeroes
  !<20190426><dzliu>! enddo
  !<20190426><dzliu>! nant = maxa
  !<20190426><dzliu>! ------------- WITH
  nant = maxa
  cbufsize = 2880*ceiling(nant*70.0/2880)
  allocate(character(len=cbufsize) :: cbuf)
  do j=1,cbufsize
    cbuf(j:j) = char(0)  ! Fill with zeroes
  enddo
  !<20190426><dzliu>! note: one antenna needs 70 bytes, see above, NAXIS1 = 70.
  !<20190426><dzliu>! -------------
  do iant = 1,nant
    j = (iant-1)*70 + 1
    !<20190426><dzliu>! ------------- REPLACED
    !<20190426><dzliu>! write(cbuf(j:j+7),'(a7,i1)') 'IRAM PDB:AN',iant
    !<20190426><dzliu>! ------------- WITH
    write(cbuf(j:j+7),'(a1,i3.3,a4)') 'A',iant,' ' ! total 8 bytes
    call gio_message(seve%i,'TO_UVFITS','Writing antenna '//cbuf(j:j+7))
    !<20190426><dzliu>! -------------
    cbuf(j+44:j+44)= 'X'
    cbuf(j+57:j+57)= 'X'
    cbuf(j+35:j+35)=char(iant)
  enddo
  !<20190426><dzliu>! ------------- REPLACED
  !<20190426><dzliu>! call gfits_putbuf(cbuf,2880,error)
  !<20190426><dzliu>! ------------- WITH
  call gfits_putbuf(cbuf,cbufsize,error)
  !<20190426><dzliu>! -------------
  fd%nb = 0
  return
  !
10 format(a,i10,'         / ',a)
14 format(a,a)
20 format(a,e20.13,'         / ',a)
end subroutine write_extension
