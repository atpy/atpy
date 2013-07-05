.. _format_hdf5:

===========
HDF5 tables
===========

.. note::
    The Hierarchical Data Format (HDF) is a format that can be used to
    store, transmit, and manipulate datasets (n-dimensional arrays or
    tables). Datasets can be collected into groups, which can be
    collected into larger groups. Datasets and groups can contain
    meta-data, in the form of attributes.

HDF5 tables are supported thanks to the `h5py <http://code.google.com/p/h5py/>`_ module. Reading HDF5 tables is straightforward::

  >>> t = atpy.Table('table.hdf5')
  
If more than one table is present in the file, ATpy will give a list of available tables, identified by a path. The specific table to read can then be specified with the ``table=`` argument::

  >>> t = atpy.Table('table.hdf5', table='Measurements')
  
In the case where a table is inside a group, or a hierarchy of groups, the table name may be a full path inside the file::

  >>> t = atpy.Table('table.hdf5', table='Group1/Measurements')

To read in all tables in an HDF5 file, use the ``TableSet`` class::

  >>> t = atpy.TableSet('table.hdf5') 
  
When writing out an HDF5 table, the default is to write the uncompressed, but it is possible to turn on compression using the ``compression`` argument::

  >>> t.write('table.hdf5', compression=True)
  
To write the table to a specific group within the file, use the ``group`` argument::

  >>> t.write('table.hdf5', group='Group4')
  
Finally, it is possible to append tables to existing files, using the ``append`` argument. For example, the following two commands write out two tables to the same existing file::

  >>> t1.write('existing_table.hdf', append=True)
  >>> t2.write('existing_table.hdf', append=True)

In the event that ATpy does not recognize an HDF5 table (for example if the file extension is obscure),  the type can be explicitly given::

  >>> t = atpy.Table('table', type='hdf5')

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
    
.. autofunction:: atpy.hdf5table.read
.. autofunction:: atpy.hdf5table.write
.. autofunction:: atpy.hdf5table.read_set
.. autofunction:: atpy.hdf5table.write_set