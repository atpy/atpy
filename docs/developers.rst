======================
Custom reading/writing
======================

One of the new features introduced in ATpy 0.9.2 is the ability for users to write their own read/write functions and *register* them with ATpy. A read or write function needs to satisfy the following requirements:

* The first argument should be a ``Table`` instance (in the case of a single
  table reader/writer) or a ``TableSet`` instance (in the case of a table set
  reader/writer)
  
* The function can take any other arguments, with the exception of the keyword
  arguments ``verbose`` and ``type``.
  
* The function should not return anything, but rather should operate directly
  on the table or table set instance passed as the first argument
  
* If the file format supports masking/null values, the function should take
  into account that there are two ways to mask values (see
  :ref:`maskingandnull`). The ``Table`` instance has a ``_masked`` attribute
  that specifies whether the user wants a Table with masked arrays, or with a
  null value. The function should take this into account. For example, in the
  built-in FITS reader, the table is populated with ``add_column`` in the
  following way::

    if self._masked:
        self.add_column(name, data, unit=columns.units[i], \
            mask=data==columns.nulls[i])
    else:
        self.add_column(name, data, unit=columns.units[i], \
            null=columns.nulls[i])
  
The reader/writer function can then fill the table by using the ``Table`` methods described in :ref:`api` (for a single table reader/writer) or :ref:`apiset` (for a table set reader/writer). In particular, a single table reader will likely contain calls to ``add_column``, while a single table writer will likely contain references to the ``data`` attribute of ``Table``.

Once a custom function is available, the user can register it using one of the four ATpy functions:

* ``atpy.register_reader``: Register a reader function for single tables

* ``atpy.register_set_reader``: Register a reader function for table sets

* ``atpy.register_writer``: Register a writer function for single tables

* ``atpy.register_set_writer``: Register a writer function for tables sets

The API for these functions is of the form ``(ttype, function, override=True/False)``, where ``ttype`` is the code name for the format (like the build-in ``fits``, ``vo``, ``ipac``, or ``sql`` types), function is the actual function to use, and override allows the user to override existing definitions (for example to provide an improved ``ipac`` reader).

For example, if a function is defined for reading HDF5 tables, which we can call hdf5.read, then one would first need to register this function after importing atpy::

    >>> import atpy
    >>> atpy.register_reader('hdf5', hdf5.read)
    
This type can then be used when reading in a table::

    >>> t = atpy.Table('mytable.hdf5', type='hdf5')
    
It is also possible to register extensions for a specific type using ``atpy.register_extensions``. This function expects a table type and a list of file extensions to associate with it. For example, by setting::

    >>> atpy.register_extensions('hdf5', ['hdf5', 'hdf'])
    
One can then read in an HDF5 table without specifying the type::

    >>> t = atpy.Table('mytable.hdf5')
    
We encourage users to send us examples of reader/writer functions for various formats, and would be happy in future to include readers and writers for commonly used formats in ATpy.

