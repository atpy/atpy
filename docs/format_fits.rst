.. _format_fits:

===========
FITS tables
===========

.. note::
    The Flexible Image Transport System (FITS) format is a widely used file
    format in Astronomy, that is used to store, transmit, and manipulate
    images and tables. FITS tables contain one or more header-data units
    (HDU) which can be either images or tables in ASCII or binary format.
    Tables can contain meta-data, stored in the header.
    
Overview
--------
    
FITS tables are supported thanks to the `pyfits <http://www.stsci.edu/resources/software_hardware/pyfits>`_ module. Reading FITS tables is straightforward::

  >>> t = atpy.Table('table.fits')

If more than one table is present in the file, the HDU can be specified::

  >>> t = atpy.Table('table.fits', hdu=2)

To read in all HDUs in a file, use the ``TableSet`` class::

  >>> t = atpy.TableSet('table.fits') 

Compressed FITS files can be read easily::

  >>> t = atpy.Table('table.fits.gz')

In the event that ATpy does not recognize a FITS table (for example if the file extension is obscure),  the type can be explicitly given::

  >>> t = atpy.Table('table', type='fits')

.. note:: 
    As for all file formats, the ``verbose`` argument can be specified to
    control whether warning messages are shown when reading (the default is
    ``verbose=True``), and the ``overwrite`` argument can be used when
    writing to overwrite a file (the default is ``overwrite=False``).
    
Full API for advanced users
---------------------------

.. note ::
    The following functions should not be called directly - the arguments  should be passed to ``Table()/Table.read()``,
    ``Table.write()``, ``TableSet()/TableSet.read()``, and
    ``TableSet.write()`` respectively.

.. autofunction:: atpy.fitstable.read
.. autofunction:: atpy.fitstable.write
.. autofunction:: atpy.fitstable.read_set
.. autofunction:: atpy.fitstable.write_set
