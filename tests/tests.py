from atpy import *

# Read in AJ VO Table

print "Reading VO Table"
vt = VOTable(name='red sources')
vt.read('examples/aj285677t2_VOTable.xml')

# Convert to FITS Table

print "Converting to FITS Table"
ft = FITSTable(vt)
ft.write('temp1.fits',overwrite=True)

# Convert to IPAC Table

print "Converting to IPAC Table"
it = IPACTable(vt)
it.write('temp1.tbl')

# Convert to SQLite databases

print "Converting to SQL databases"
st = SQLTable2(vt)
st.write('postgres',database='python',user='tom',overwrite=True)
st.write('sqlite','temp1.db',overwrite=True)
st.write('mysql',db='python',user='tom',passwd="C2#uwQsk",overwrite=True)

# Read in UKIDSS FITS table

print "Reading in FITS Table"
ft = FITSTable()
ft.read('examples/catalog_1.fits.gz')
ft.table_name = "UKIDSS"

# Convert to VO Table

print "Converting to VO Table"
vt = VOTable(ft)
vt.write('temp2.xml')

# Convert to IPAC Table

print "Converting to IPAC Table"
it = IPACTable(ft)
it.write('temp2.tbl')

# Convert to SQL databases

print "Converting to SQL databases"
st = SQLTable2(ft)
st.write('postgres',database='python',user='tom',overwrite=True)
st.write('sqlite','temp2.db',overwrite=True)
st.write('mysql',db='python',user='tom',passwd="C2#uwQsk",overwrite=True)

# Reading in FITS file with vector columns

print "Reading in FITS Table set"
ft = FITSTable()
ft.read('examples/3000030_1_sed.fits.gz',hdu=3)

print "Converting to VO Table"
vt = VOTable(ft)
vt.write('temp6.xml')

# Read in set of FITS Tables

print "Reading in FITS Table set"
fts = FITSTableSet()
fts.read('examples/3000030_1_sed.fits.gz')

# Write out set of VO Tables

print "Writing out VO Table set"
vts = VOTableSet(fts)
vts.write('temp3.xml')

# Read in set of VO Tables

print "Reading VO Table Set"
vts = VOTableSet()
vts.read('temp3.xml')

# Write out set of FITS Tables

print "Writing out FITS Table set"
fts = FITSTableSet(vts)
fts.write('temp3.fits',overwrite=True)

# Read in IPAC Table

print "Reading in IPAC Table"
it = IPACTable(name='2MASS PSC')
it.read('examples/2mass.tbl')

# Convert to FITS Table

print "Converting to FITS Table"
ft = FITSTable(it)
ft.write('temp4.fits',overwrite=True)

# Convert to VO Table

print "Converting to VO Table"
vt = VOTable(it)
vt.write('temp4.xml')

