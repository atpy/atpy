.. _format_ipac:

===========
IPAC tables
===========

.. note::
    IPAC tables are an ASCII table that can contain a single table. The
    format can contain meta-data that consists of keyword values and
    comments (analogous to FITS files), and the column headers are
    separated by pipe (``|``) symbols that indicate the position of the
    columns.

IPAC tables are natively supported in ATpy (no additional module is required). Reading IPAC tables is straightforward::

  >>> t = atpy.Table('table.tbl')
  
and writing a table out in IPAC format is equally easy::

  >>> t.write('table.tbl')
  
IPAC tables can have three different definitions with regard to the alignment of the columns with the pipe symbols in the header. The definition to use is controlled by the ``definition`` argument. The definitions are:

1. Any character below a pipe symbol belongs to the column on the left, and any characters below the first pipe symbol belong to the first column.
2. Any character below a pipe symbol belongs to the column on the right.
3. No characters should be present below the pipe symbols.

The default is ``definition=3``.

.. note:: 
    As for all file formats, the ``verbose`` argument can be specified to
    control whether warning messages are shown when reading (the default is
    ``verbose=True``), and the ``overwrite`` argument can be used when
    writing to overwrite a file (the default is ``overwrite=False``).

Full API for advanced users
---------------------------

.. note ::
    The following functions should not be called directly - the arguments  should be passed to ``Table()/Table.read()`` and
    ``Table.write()`` respectively.
    
.. autofunction:: atpy.ipactable.read
.. autofunction:: atpy.ipactable.write