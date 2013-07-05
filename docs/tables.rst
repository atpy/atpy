.. _tables:

====================
Constructing a table
====================

The ``Table`` class is the basic entity in ATpy. It consists of table data
and metadata. The data is stored using a `NumPy <http://numpy.scipy.org/>`_
structured array. The metadata includes units, null values, and column
descriptions, as well as comments and keywords.

Data can be stored in the table using many of the `NumPy types
<http://docs.scipy.org/doc/numpy/reference/arrays.scalars.html#built-in-scalar-types>`_,
including booleans, 8, 16, 32, and 64-bit signed and unsigned integers, 32
and 64-bit floats, and strings. Not all file formats and databases support
reading and writing all of these types -- for more information, see
:ref:`formats`.

Creating a table
================

The simplest way to create an instance of the ``Table`` is to call the
class with no arguments::

  >>> t = atpy.Table()

Populating the table
====================

A table can be populated either manually or by reading data from a file or database. Reading data into a table erases previous content. Data can be manually added once a table has been read in from a file.

Reading data from a file
------------------------

The ``read(...)`` method can be used to read in a table from a file. To date, ATpy supports the following file formats:

  * `FITS <http://archive.stsci.edu/fits/fits_standard/>`_ tables (``type=fits``)
  * `VO <http://www.ivoa.net/Documents/VOTable/>`_ tables (``type=vo``)
  * `IPAC <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_ tables (``type=ipac``)
  * `HDF5 <http://www.hdfgroup.org/HDF5/>`_ (``type=hdf5``)
  
Now that ATpy has integrates with `asciitable <http://cxc.harvard.edu/contrib/asciitable/>`_, the following formats are also supported:

  * `CDS <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (``type=cds`` or ``type=mrt``)
  * DAOPhot (``type=daophot``)
  * RDB (``type=rdb``)
  * Arbitrary ASCII tables (``type=ascii``)
  
When reading a table from a file, the only required argument is the filename. For example, to read a VO table called ``example.xml``, the following should be used::

  >>> t.read('example.xml')
  Auto-detected input type: VO table
  
The ``read()`` method will in most cases correctly identify the format of the file from the extension. As seen above, the default behavior is to specifically tell the user what format is being assumed, but this can be controlled via the ``verbose`` argument.
  
In some cases, ``read()`` will fail to determine the input type. In this case, or to override the automatically selected type, the input type can be specified using the ``type`` argument::

  >>> t.read('example.xml', type='vo')

The ``read`` method supports additional file-format-dependent options. These are described in more detail in :ref:`formats`.

In cases where multiple tables are available in a table file, ATpy will display a message to the screen with instructions of how to specify which table to read in. Alternatively, see :ref:`tablesets` for information on how to read all tables into a single ``TableSet`` instance.

As a convenience, it is possible to create a ``Table`` instance and read in data in a single command::

  >>> t = Table('example.xml')
  
Any arguments given to ``Table`` are passed on to the ``read`` method, so the above is equivalent to::

  >>> t = Table()
  >>> t.read('example.xml')
  
As of 0.9.6, it is now possible to specify URLs starting with ``http://``
or ``ftp://`` and the file will automatically be downloaded. Furthermore,
it is possible to specify files compressed in gzip or bzip format for all
I/O formats.

Reading data from a database
----------------------------

Reading a table from a database is very similar to reading a table from a file. The main difference is that for databases, the first argument should be the database type, To date, ATpy supports the following database types:

  * SQLite (``sqlite``)
  * MySQL (``mysql``)
  * PostGreSQL (``postgres``)
 
The remaining arguments depend on the database type. For example, an SQLite database can be read by specifying the database filename::

  >>> t.read('sqlite','example.db')

For MySQL and PostGreSQL databases, it is possible to specify the database, table, authentication, and host parameters. The various options are descried in more detail in :ref:`formats`. As for files, the ``verbose`` and ``type`` arguments can be used.

As for reading in from files, one can read in data from a database while initializing the ``Table`` object::

  >>> t = Table('sqlite','example.db')

.. note::
    It is possible to specify a full SQL query using the ``query`` argument.
    Any valid SQL is allowed. If this is used, the table name should
    nevertheless be specified using the ``table`` argument.

Adding columns to a table
-------------------------

It is possible to add columns to an empty or an existing table. Two methods exist for this. The first, ``add_column``, allows users to add an existing array to a column. For example, the following can be used to add a column named ``time`` where the variable ``time_array`` is a NumPy array::

  >>> t.add_column('time', time_array)
  
The ``add_column`` method also optionally takes metadata about the column, such as units, or a description. For example::

  >>> t.add_column('time', time_array, unit='seconds')
  
indicates that the units of the column are seconds. It is also possible to convert the datatype of an array while adding it to a table by using the ``dtype`` argument. For example, the following stores the column from the above examples as 32-bit floating point values::

  >>> t.add_column('time', time_array, unit='seconds', dtype=np.float32)
  
In some cases, it is desirable to add an empty column to a table, and populate it element by element. This can be done using the ``add_empty_column`` method. The only required arguments for this method are the name and the data type of the column::


  >>> t.add_empty_column('id', np.int16)
  
If the column is the first one being added to an empty table, the ``shape`` argument should be used to specify the number of rows. This should either be an integer giving the number of rows, or a tuple in the case of vector columns (see :ref:`vectorcolumns` for more details)

.. _vectorcolumns:

Vector Columns
--------------

As well as using one-dimensional columns is also possible to specify so-called vector columns, which are essentially two-dimensional arrays. Only FITS and VO tables support reading and writing these. The ``add_column`` method accepts two-dimensional arrays as input, and uses these to define vector columns. Empty vector columns can be created by using the ``add_empty_column`` method along with the ``shape`` argument to specify the full shape of the column. This should be a tuple of the form ``(n_rows, n_elements)``.

Writing the data to a file
--------------------------

Writing data to files or databases is done through the ``write`` method. The arguments to this method are very similar to that of the ``read`` data. The only main difference is that the ``write`` method can take an ``overwrite`` argument that specifies whether or not to overwrite existing files.

Adding meta-data
================

Comments and keywords can be added to a table using the ``add_comment()`` and ``add_keyword()`` methods::

  >>> t.add_comment("This is a great table")
  >>> t.add_keyword("meaning", 42)
  
