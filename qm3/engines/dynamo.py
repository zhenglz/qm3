# -*- coding: iso-8859-1 -*-

from __future__ import print_function, division
import	sys
if( sys.version_info[0] == 2 ):
	range = xrange
import	os
import	sys
import	qm3.io
import	qm3.mol
import	struct
import	stat
import	time
import	qm3.elements
import	math



def coordinates_read( fname = None ):
	"""
Subsystem     1  A
   452 ! # of residues.
!===============================================================================
Residue     1  SER
    11 ! # of atoms.
     1   N             7       -5.0950000000     27.6770000000    -14.8700000000
     2   H             1       -4.2860000000     28.3550000000    -14.8320000000
     3   CA            6       -6.1260000000     27.5020000000    -13.9140000000
	"""
	mol = qm3.mol.molecule()
	f = qm3.io.open_r( fname )
	t = f.readline().strip().split()
	while( t != [] ):
		if( t[0].lower() == "subsystem" ):
			segn = t[2]
		if( t[0].lower() == "orthorhombic" ):
			mol.boxl = [ float( t[1] ), float( t[2] ), float( t[3] ) ]
		if( t[0].lower() == "cubic" ):
			mol.boxl = [ float( t[1] ), float( t[1] ), float( t[1] ) ]
		if( t[0].lower() == "residue" ):
			resi = int( t[1] )
			resn = t[2]
			t = f.readline().split()
			while( t[0][0] == "!" ):
				t = f.readline().split()
			for i in range( int( t[0] ) ):
				t = f.readline().split()
				while( t[0][0] == "!" ):
					t = f.readline().split()
				mol.segn.append( segn )
				mol.resn.append( resn )
				mol.resi.append( resi )
				mol.labl.append( t[1] )
				mol.anum.append( int( t[2] ) )
				mol.coor.append( float( t[3] ) )
				mol.coor.append( float( t[4] ) )
				mol.coor.append( float( t[5] ) )
				mol.natm += 1
		t = f.readline().split()
	qm3.io.close( f, fname )
	mol.settle()
	return( mol )


def coordinates_write( mol, fname = None ):
	f = qm3.io.open_w( fname )
	f.write( "%d %d %d\n"%( mol.natm, len( mol.res_lim ) - 1, len( mol.seg_lim ) - 1 ) )
	if( mol.boxl != [ mol._mboxl, mol._mboxl, mol._mboxl ]  ):
		f.write( "Symmetry  1\n" )
		if( mol.boxl[0] == mol.boxl[1] and mol.boxl[0] == mol.boxl[2] ):
			f.write( "CUBIC  %lf\n"%( mol.boxl[0] ) )
		else:
			f.write( "ORTHORHOMBIC  %lf %lf %lf\n"%( mol.boxl[0], mol.boxl[1], mol.boxl[2] ) )
	l = 1
	for i in range( len( mol.seg_lim ) - 1 ):
		f.write ( "Subsystem%6d  %s\n"%( i + 1, mol.segn[mol.res_lim[mol.seg_lim[i]]] ) )
		f.write ( "%6d\n"%( mol.seg_lim[i+1] - mol.seg_lim[i] ) )
		for j in range( mol.seg_lim[i], mol.seg_lim[i+1] ):
			f.write ( "Residue%6d  %s\n"%( mol.resi[mol.res_lim[j]], mol.resn[mol.res_lim[j]] ) )
			f.write ( "%6d\n"%( mol.res_lim[j+1] - mol.res_lim[j] ) )
			for k in range( mol.res_lim[j], mol.res_lim[j+1] ):
				f.write ( "%6d   %-10s%5d%20.10lf%20.10lf%20.10lf\n"%( l, mol.labl[k], int( mol.anum[k] ),
					mol.coor[3*k], mol.coor[3*k+1], mol.coor[3*k+2] ) )
				l += 1
	qm3.io.close( f, fname )


def topology_read( mol, fname ):
	mol.mass = []
	mol.chrg = []
	mol.epsi = []
	mol.rmin = []
	f = open( fname, "rb" )
	for i in range( 6 ):
		f.read( struct.unpack( "i", f.read( 4 ) )[0] + 4 )
	f.read( 4 )
	if( mol.natm == struct.unpack( "i", f.read( 4 ) )[0] ):
		f.read( 8 )
		mol.mass = list( struct.unpack( "%dd"%( mol.natm ), f.read( 8 * mol.natm ) ) )
		f.read( 4 )
		for i in range( 3 ):
			f.read( struct.unpack( "i", f.read( 4 ) )[0] + 4 )
		f.read( 4 )
		mol.chrg = list( struct.unpack( "%dd"%( mol.natm ), f.read( 8 * mol.natm ) ) )
		f.read( 4 )
		f.read( struct.unpack( "i", f.read( 4 ) )[0] + 4 )
		f.read( 4 )
		c = 0.25 / 4.184
		mol.epsi = [ i*i*c for i in struct.unpack( "%dd"%( mol.natm ), f.read( 8 * mol.natm ) ) ]
		f.read( 4 )
		f.read( struct.unpack( "i", f.read( 4 ) )[0] + 4 )
		f.read( 4 )
		c = 0.5 * math.pow( 2, 1.0 / 6.0 )
		mol.rmin = [ i*i*c for i in struct.unpack( "%dd"%( mol.natm ), f.read( 8 * mol.natm ) ) ]
	f.close()


def sequence( mol, fname = None ):
	f = qm3.io.open_w( fname )
	f.write( "Sequence\n%d\n\n"%( len( mol.seg_lim ) - 1 ) )
	for i in range( len( mol.seg_lim ) - 1 ):
		f.write ( "Subsystem  %s\n"%( mol.segn[mol.res_lim[mol.seg_lim[i]]] ) )
		f.write ( "%6d\n"%( mol.seg_lim[i+1] - mol.seg_lim[i] ) )
		k = 0
		for j in range( mol.seg_lim[i], mol.seg_lim[i+1] ):
			f.write ( " %s ;"%( mol.resn[mol.res_lim[j]] ) )
			k += 1
			if( k%12 == 0 ):
				f.write( "\n" )
		if( k%12 != 0 ):
			f.write( "\n" )
		f.write( "! Variant TYPE  RESN RESI\n" )
		f.write( "End\n\n" )
	f.write( "\n! Link TYPE  SEGN_A RESN_A RESI_A   SEGN_B RESN_B RESI_B\n" )
	f.write( "End" )
	qm3.io.close( f, fname )


def selection( mol, sele, fname = None ):
	f = qm3.io.open_w( fname )
	S = []
	R = []
	for i in sele:
		if( not mol.segn[i] in S ):
			S.append( mol.segn[i] )
			R.append( [] )
		else:
			w = S.index( mol.segn[i] )
			if( not mol.resi[i] in R[w] ):
				R[w].append( mol.resi[i] )
	f.write( """subroutine my_sele( selection )
	use atoms,             only : natoms
	use atom_manipulation, only : atom_selection
	logical, dimension(1:natoms), intent( inout ) :: selection
	selection = .false.
""" )
	for i in range( len( S ) ):
		if( len( R[i] ) > 0 ):
			f.write( "\tselection = selection .or. atom_selection( &\n\t\tsubsystem = (/ '%s' /), &\n\t\tresidue_number = (/"%( S[i] ) )
			k = 0
			for j in range( len( R[i] ) - 1 ):
				k += 1
				f.write( " %d,"%( R[i][j] ) )
				if( k%12 == 0 ):
					f.write( " &\n" )
			f.write( " %d /) )\n"%( R[i][-1] ) )
	f.write( "end subroutine" )
	qm3.io.close( f, fname )




class dynamo( object ):

	def __init__( self, mol ):
		self.exe = "./dynamo.exe"
		self.inp = "dynamo.inp.%d"%( os.getpid() )
		self.pfd = None


	def start( self, timeout = 10 ):
		if( os.access( self.inp, os.W_OK ) ):
			os.unlink( self.inp )
		os.mkfifo( self.inp )
		os.system( "%s %s > dynamo.log &"%( self.exe, self.inp ) )
		time.sleep( timeout )
		self.pfd = open( self.inp, "wt" )


	def stop( self ):
		self.pfd.write( "exit\n" )
		self.pfd.flush()
		self.pfd.close()
		try:
			os.unlink( self.inp )
		except:
			pass


	def update_charges( self, mol ):
		f = open( "dynamo.chrg", "wb" )
		f.write( struct.pack( "i", 8 * mol.natm ) )
		for i in range( mol.natm ):
			f.write( struct.pack( "d", mol.chrg[i] ) )
		f.write( struct.pack( "i", 8 * mol.natm ) )
		f.close()
		self.pfd.write( "charges\n" )
		self.pfd.flush()


	def update_coor( self, mol ):
		f = open( "dynamo.crd", "wb" )
		f.write( struct.pack( "i", 24 * mol.natm ) )
		for i in range( 3 * mol.natm ):
			f.write( struct.pack( "d", mol.coor[i] ) )
		f.write( struct.pack( "i", 24 * mol.natm ) )
		f.close()
		self.pfd.write( "coordinates\n" )
		self.pfd.flush()


	def get_func( self, mol ):
		try:
			os.unlink( "dynamo.dat" )
		except:
			pass
		self.pfd.write( "energy\n" )
		self.pfd.flush()
		while( not os.path.isfile( "dynamo.dat" ) ):
			time.sleep( 0.01 )
		while( os.stat( "dynamo.dat" )[stat.ST_SIZE] < 16 ):
			time.sleep( 0.01 )
		f = open( "dynamo.dat", "rb" )
		f.read( 4 )
		mol.func += struct.unpack( "d", f.read( 8 ) )[0]
		f.close()


	def get_grad( self, mol ):
		try:
			os.unlink( "dynamo.dat" )
		except:
			pass
		self.pfd.write( "gradient\n" )
		self.pfd.flush()
		while( not os.path.isfile( "dynamo.dat" ) ):
			time.sleep( 0.01 )
		t = 24 + 24 * mol.natm
		while( os.stat( "dynamo.dat" )[stat.ST_SIZE] < t ):
			time.sleep( 0.01 )
		f = open( "dynamo.dat", "rb" )
		f.read( 4 )
		mol.func += struct.unpack( "d", f.read( 8 ) )[0]
		f.read( 8 )
		t = list( struct.unpack( "%dd"%( 3 * mol.natm ), f.read( 24 * mol.natm ) ) )
		f.close()
		for i in range( 3 * mol.natm ):
			mol.grad[i] += t[i]







DYNAMO_F90_TEMPLATE = """subroutine driver
	use dynamo
	implicit none
	character( len = 256 ) :: str
	integer :: i, j

	call getarg( 1, str )
	write(*,"(a,a,a)") "[", trim( str ), "]"
	open( file = trim( str ), unit = 998, action = "read", form = "formatted" )
	read( 998, "(a)" ) str
	write(*,"(a,a,a)") "[", trim( str ), "]"
	do while( trim( str ) /= "exit" )
		if( trim( str ) == "charges" ) then
			open( file = "dynamo.chrg", unit = 999, action = "read", form = "unformatted" )
			read( 999 ) atmchg
			close( 999 )
		end if
		if( trim( str ) == "coordinates" ) then
			open( file = "dynamo.crd", unit = 999, action = "read", form = "unformatted" )
			read( 999 ) atmcrd(1:3,1:natoms)
			close( 999 )
		end if
		if( trim( str ) == "energy" ) then
			call energy_bond( ebond, virial )
			call energy_angle( eangle )
			call energy_dihedral( edihedral )
			call energy_improper( eimproper )
			call energy_non_bonding_calculate( eelect, elj, virial )
			write( *, "(6f20.10)" ) ebond, eangle, edihedral, eimproper, eelect, elj
			open( file = "dynamo.dat", unit = 999, action = "write", form = "unformatted" )
			write( 999 ) ebond + eangle + edihedral + eimproper + eelect + elj
			close( 999 )
		end if
		if( trim( str ) == "gradient" ) then
			if( .not. allocated( atmder ) ) allocate( atmder(1:3,1:natoms ) )
			atmder = 0.0_dp
			call energy_bond( ebond, virial, atmder )
			call energy_angle( eangle, atmder )
			call energy_dihedral( edihedral, atmder )
			call energy_improper( eimproper, atmder )
			call energy_non_bonding_calculate( eelect, elj, virial, atmder )
			write( *, "(6f20.10)" ) ebond, eangle, edihedral, eimproper, eelect, elj
			open( file = "dynamo.dat", unit = 999, action = "write", form = "unformatted" )
			write( 999 ) ebond + eangle + edihedral + eimproper + eelect + elj
			write( 999 ) atmder
			close( 999 )
		end if
		read( 998, "(a)" ) str
		write(*,"(a,a,a)") "[", trim( str ), "]"
	end do
	close( 998 )
end subroutine driver


program slave
	use dynamo
	implicit none

	logical, dimension(:), allocatable :: flg
	integer :: i

	call dynamo_header

!   call mm_file_process( "borra", "opls" )
!   call mm_system_construct( "borra", "seq" )
!   call mm_system_write( "sys_bin" )
!   stop
    call mm_system_read( "sys_bin" )
	call coordinates_read( "crd" )

	allocate( flg(1:natoms) )
	flg = .false.
	flg = atom_selection( subsystem = (/ "A" /), residue_number = (/ 1 /) )
	call atoms_fix( flg )
	do i = 1, natoms
		if( flg(i) ) then
			atmchg(i) = 0.0_dp
			atmchg14(i) = 0.0_dp
		end if
	end do

	call energy_initialize
    call energy_non_bonding_options( &
		list_cutoff   = 18.0_dp, &
		outer_cutoff  = 16.0_dp, &
		inner_cutoff  = 14.0_dp, &
		minimum_image = .false. )

	call driver

	deallocate( flg )

end program
"""
