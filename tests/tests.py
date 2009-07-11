from atpy import *

# Read in AJ VO Table

print "Reading VO Table"
t = Table('examples/aj285677t2_VOTable.xml',name='red sources')

# Convert to FITS Table

print "Converting to FITS Table"
t.write('temp1.fits',overwrite=True)

# Convert to IPAC Table

print "Converting to IPAC Table"
t.write('temp1.tbl')

# Convert to SQLite databases

print "Converting to SQL databases"
t.write('postgres',database='python',user='tom',overwrite=True)
t.write('sqlite','temp1.db',overwrite=True)
t.write('mysql',db='python',user='tom',passwd="C2#uwQsk",overwrite=True)

# Read in UKIDSS FITS table

print "Reading in FITS Table"
t = Table('examples/catalog_1.fits.gz',name='UKIDSS')

# Convert to VO Table

print "Converting to VO Table"
t.write('temp2.xml')

# Convert to IPAC Table

print "Converting to IPAC Table"
t.write('temp2.tbl')

# Convert to SQL databases

print "Converting to SQL databases"
t.write('postgres',database='python',user='tom',overwrite=True)
t.write('sqlite','temp2.db',overwrite=True)
t.write('mysql',db='python',user='tom',passwd="C2#uwQsk",overwrite=True)

# Reading in FITS file with vector columns

print "Reading in FITS Table set"
t = Table('examples/3000030_1_sed.fits.gz',hdu=3)

print "Converting to VO Table"
t.write('temp6.xml')

# Read in IPAC Table

print "Reading in IPAC Table"
t = Table('examples/2mass.tbl',name='2MASS PSC')

# Convert to FITS Table

print "Converting to FITS Table"
t.write('temp4.fits',overwrite=True)

# Convert to VO Table

print "Converting to VO Table"
t.write('temp4.xml')

# Read in set of FITS Tables

print "Reading in FITS Table set"
ts = TableSet('examples/3000030_1_sed.fits.gz')

# Write out set of VO Tables

print "Writing out VO Table set"
ts.write('temp3.xml')

# Convert to SQL databases

# The following needs vector columns in SQL to work
#ts.write('postgres',database='python',user='tom',overwrite=True)
#ts.write('sqlite','temp2.db',overwrite=True)
#ts.write('mysql',db='python',user='tom',passwd="C2#uwQsk",overwrite=True)
    
# Read in set of VO Tables

print "Reading VO Table Set"
ts = TableSet('temp3.xml')

# Write out set of FITS Tables

print "Writing out FITS Table set"
ts.write('temp3.fits',overwrite=True)

# Convert to SQL databases

# The following needs vector columns in SQL to work
#ts.write('postgres',database='python',user='tom',overwrite=True)
#ts.write('sqlite','temp2.db',overwrite=True)
#ts.write('mysql',db='python',user='tom',passwd="C2#uwQsk",overwrite=True)