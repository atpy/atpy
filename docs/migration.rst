Guide for Migrating to Astropy
==============================

.. note:: If you encounter any other issues not described here when migrating to
          Astropy, please `let us know <https://github.com/atpy/atpy/issues>`_
          and we will update this guide accordingly.

Much of the functionality from ATpy has been incorporated into the `Astropy
<http://www.astropy.org>`_ as the `astropy.table
<http://docs.astropy.org/en/stable/table>`_ sub-package. The Astropy ``Table``.
class can be imported with::

    >>> from astropy.table import Table

In the process of including the code in Astropy, the API has been changed in a
backward-incompatible way, and the present document aims to describe the main
changes.

Note that the Astropy ``Table`` class is more powerful than the ATpy
equivalent in many respects, and we do not describe all the features here,
only functionality of ATpy that has changed in Astropy. For a full overview of
the Astropy ``Table`` class, see `astropy.table
<http://docs.astropy.org/en/stable/table>`_.

Adding columns
--------------

In ATpy, columns are added with::

    >>> from atpy import Table
    >>> t = Table()
    >>> t.add_column('a', [1, 2, 3])

In the Astropy 0.2.x ``Table`` class, the equivalent is::

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
`astroquery <http://astroquery.readthedocs.org>`_ package which is currently
under development.

Table Sets
----------

Table sets are not implemented in Astropy at this time, but it is possible to
simply loop over the tables in a file and construct a list or dictionary of
them.
