.. _manipulating:

================
Modifying tables
================

Manipulating table columns
==========================

Columns can be renamed or removed. To do this, one can use the
``remove_column``, ``remove_columns``, ``keep_columns`` and ``rename_column``
methods. For example, to rename a column ``time`` to ``space``, one can use::

  >>> t.rename_column('time','space')

The ``keep_columns`` essentially acts in the opposite way to
``remove_columns`` - it is used to specify which subset of the columns to not
remove, which can be useful for extracting specific columns from a large
table. For more information, see the :ref:`api`.

Sorting tables
==============

To sort a table, use the ``sort()`` method, along with the name of the column to sort by::

  >>> t.sort('time')

Combining tables
================

Given two ``Table`` instances with the same column metadata, and the same number of columns, one table can be added to the other via the ``append`` method::

   >>> t1 = Table(...)
   >>> t2 = Table(...)
   >>> t1.append(t2)