Guide for Migrating to Astropy
==============================

Much of the functionality from ATpy has been incorporated into the `Astropy
<http://www.astropy.org>`_ as the `astropy.table
<http://docs.astropy.org/en/stable/table>`_ sub-package. The Astropy table
class can be imported with::

    >>> from astropy.table import Table

which aims to replace the ATpy ``Table``` class.

In the process of including the code in Astropy, the API has been changed in a
backward-incompatible way, and the present document aims to describe the main
changes.

Adding columns
--------------

In ATpy, columns are added with::

    >>> from atpy import Table
    >>> t = Table()
    >>> t.add_column('a', [1, 2, 3])

In the Astropy table class, as of 0.2, the equivalent is::

    >>> from astropy.table import Table, Column
    >>> t = Table()
    >>> t.add_column(Column(data=[1, 2, 3], name='a'))

This is a little more verbose, but from Astropy 0.3 onwards, this can be done
more simply with::

    >>> from astropy.table import Table, Column
    >>> t = Table()
    >>> t['a'] = [1, 2, 3]

This is already implemented in the latest developer version of Astropy, and
will be the recommended way of adding columns.

Reading/writing
---------------

While it was possible to read a table directly into the ``Table`` class upon
initialization in ATpy::

    >>> from atpy import Table
    >>> t = Table('test.fits')

Astropy now requires reading to be done by a class method::

    >>> from astropy.table import Table
    >>> t = Table.read('test.fits')

Writing should be similar between ATpy and Astropy::

    >>> t.write('test.fits')

As of Astropy 0.2, Astropy can read/write the same ASCII formats as ATpy, as
well as VO tables and HDF5. As of Astropy 0.3 (and in the current developer
version of Astropy), FITS reading/writing is also implemented. This means that
as of Astropy 0.3, the only features ATpy includes that are not supported by
Astropy directly are the SQL input/output and the online (VO and IRSA)
querying. However, the VO and IRSA querying will be possible with the new
`astroquery <http://astroquery.readthedocs.org`_ package which is still under
development.
