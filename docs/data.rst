.. _data:

====================
Accessing Table Data
====================

Accessing the data
==================

The table data is stored in a NumPy structured array, which can be accessed by passing the column name a key. This returns the column in question as a NumPy array::

  t['column_name']
  
For convenience, columns with names that satisfy the python variable name requirements (essentially starting with a letter and containing no symbols apart from underscores) can be accessed directly as attributes of the table::

  t.column_name
  
Since the returned data is a NumPy array, individual elements can be accessed using::

  t['column_name'][row_number]
  
or::

  t.column_name[row_number]
  
Both notations can be used to set data in the table, for example::

  t.column_name[row_number] = 1
  
and::

  t['column_name'][row_number] = 1
  
are equivalent, and will set the element at ``row_number`` to 1

Accessing the metadata
======================

The column metadata is stored in the ``columns`` attribute. To see an overview of the metadata, simply use::

  >>> t.columns
  
The metadata for a specific column can then be accessed by specifying the column name as a key::

  >>> t.columns['some_column']
  
or using the column number::

   >>> t.columns[column_number]
  
The attributes of a column object are ``dtype``, ``unit``, ``description``, ``null``, and ``format``.

.. note::
    While the unit, description and format for a column can be modified using
    the columns attribute, the dtype and null values should not be modified in
    this way as the changes will not propagate to the data array.

It is also possible to view a description of the table by using the ``describe`` method of the ``Table`` instance::

   >>> t.describe()

In addition to the column metadata, the comments and keywords are available via the ``keywords`` and ``comments`` attributes of the ``Table`` instance, for example::

   >>> instrument = t.keywords['instrument']

The ``keywords`` attribute is a dictionary, and the ``comments`` attribute is a list.

Accessing table rows
====================

The ``row(...)`` method can be used to access a specific row in a table::

  >>> row = t.row(row_number)
  
This returns the row as a NumPy record. The row can instead be returned as a tuple of elements with Python types, by using the ``python_types`` argument:

  >>> row = t.row(row_number, python_types=True)
  
Two more powerful methods are available: ``rows`` and ``where``. The ``rows`` method can be used to retrieve specific rows from a table as a new ``Table`` instance::

  >>> t_new = t.rows([1,3,5,2,7,8])
  
Alternatively, the ``where`` method can be given a boolean array to determine which rows should be selected. This is in fact very powerful as the boolean array can actually be written as selection conditions::

  >>> t_new = t.where((t.id > 10) & (t.ra < 45.4) & (t.flag == 'ok'))

Global Table properties
=======================

One can access the number of rows in a table by using the python ``len`` function::

  >>> len(t)

In addition, the number of rows and columns can also be accessed with the ``shape`` attribute:

  >>> t.shape

where the first number is the number of rows, and the second is the number of columns (note that a vector column counts as a single column).
