import atpy
import os
import getpass

# The default for the databases is to connect with the current username and
# password "C2#uwQsk".

username = getpass.getuser()
password = "C2#uwQsk"


def test_write(t, verbose=False, vector_columns=False):

    # Read in AJ VO Table

    print "Writing VO Table ... ",
    try:
        t.write('temp.xml', verbose=False)
        print "passed"
        os.remove('temp.xml')
    except:
        print "failed"

    # Convert to FITS Table

    print "Writing FITS Table ... ",
    try:
        t.write('temp.fits', overwrite=True, verbose=False)
        print "passed"
        os.remove('temp.fits')
    except:
        print "failed"

    # Convert to IPAC Table

    print "Writing IPAC Table ... ",
    try:
        t.write('temp.tbl', verbose=False)
        os.remove('temp.tbl')
        if vector_columns:
            print "failed"
        else:
            print "passed"
    except atpy.VectorException:
        if vector_columns:
            print "passed"
        else:
            print "failed"
    except:
        print "failed"

    # Convert to SQLite databases

    print "Converting to PostGreSQL database ... ",
    try:
        t.write('postgres', database='python', user=username, overwrite=True, \
            verbose=False)
        if vector_columns:
            print "failed"
        else:
            print "passed"
    except atpy.VectorException:
        if vector_columns:
            print "passed"
        else:
            print "failed"
    except:
        print "failed"

    print "Converting to SQLite database ... ",
    try:
        t.write('sqlite', 'temp1.db', overwrite=True, verbose=False)
        if vector_columns:
            print "failed"
        else:
            print "passed"
    except atpy.VectorException:
        if vector_columns:
            print "passed"
        else:
            print "failed"
    except:
        print "failed"

    print "Converting to MySQL database ... ",
    try:
        t.write('mysql', db='python', user=username, passwd=password, \
            overwrite=True, verbose=False)
        if vector_columns:
            print "failed"
        else:
            print "passed"
    except atpy.VectorException:
        if vector_columns:
            print "passed"
        else:
            print "failed"
    except:
        print "failed"

# Read in IRSA IPAC Table

print "Reading IPAC Table ... ",
try:
    t = atpy.Table('examples/2mass.tbl', name='irsa', verbose=False)
    print "passed"
except:
    print "failed"

test_write(t, verbose=False)

# Read in AJ VO Table

print "Reading VO Table ... ",
try:
    t = atpy.Table('examples/aj285677t2_VOTable.xml', name='red sources', \
        verbose=False)
    print "passed"
except:
    print "failed"

test_write(t, verbose=False)

# Read in UKIDSS FITS table

print "Reading in FITS Table ... ",
try:
    t = atpy.Table('examples/catalog_1.fits.gz', name='UKIDSS', verbose=False)
    print "passed"
except:
    print "failed"

test_write(t, verbose=False)

# Reading in FITS file with vector columns

print "Reading in FITS table with vector columns ... ",
try:
    t = atpy.Table('examples/3000030_1_sed.fits.gz', hdu=3, verbose=False)
    print "passed"
except:
    print "failed"

test_write(t, verbose=False, vector_columns=True)

# Read in set of FITS Tables

print "Reading in FITS Table set ... ",
try:
    ts = atpy.TableSet('examples/3000030_1_sed.fits.gz', verbose=False)
    print "passed"
except:
    print "failed"

test_write(ts, verbose=False, vector_columns=True)
