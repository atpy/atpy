.. _format_ascii:

============
ASCII tables
============

.. note::
    There are probably as many ASCII table formats as astronomers (if not
    more). These generally store a single table, and can sometimes include
    meta-data.

Overview
--------

Reading ASCII tables is supported thanks to the `asciitable <http://cxc.harvard.edu/contrib/asciitable/>`_ module, which makes it easy to read in arbitrary ASCII files.

By default, several pre-defined formats are available. These include `CDS <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ tables (also called Machine-Readable tables), DAOPhot tables, and RDB tables. To read these formats, simply use::

  >>> t = atpy.Table('table.mrt', type='mrt')
  >>> t = atpy.Table('table.cds', type='cds')
  >>> t = atpy.Table('table.phot', type='daophot')
  >>> t = atpy.Table('table.rdb', type='rdb')
  
The `type=` argument is optional for these formats, if they have appropriate file extensions, but due to the large number of ASCII file formats, it is safer to include it.

ATpy also allows full access to asciitable. If the ``type='ascii'`` argument is specified in ``Table()``, all arguments are passed to ``asciitable.read``, and the result is automatically stored in the ATpy ``Table`` instance. For more information on the arguments available in ``asciitable.read``, see `here <http://cxc.harvard.edu/contrib/asciitable/#basic-usage-with-read>`_.
  
.. note:: 
    As for all file formats, the ``verbose`` argument can be specified to
    control whether warning messages are shown when reading (the default is
    ``verbose=True``), and the ``overwrite`` argument can be used when
    writing to overwrite a file (the default is ``overwrite=False``).

Full API for advanced users
---------------------------

.. note ::
    The following functions should not be called directly - the arguments  should be passed to ``Table()/Table.read()``.
    
.. autofunction:: atpy.asciitables.read_cds
.. autofunction:: atpy.asciitables.read_daophot
.. autofunction:: atpy.asciitables.read_rdb
.. autofunction:: atpy.asciitables.read_ascii
.. autofunction:: atpy.asciitables.write_ascii

