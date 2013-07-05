.. _tablesets:

===========
Table Sets
===========

A ``TableSet`` instance contains a Python list of individual instances of the ``Table`` class. The advantage of using a ``TableSet`` instead of building a Python list of ``Table`` instances manually is that ATpy allows reading and writing of groups of tables to file formats that support it (e.g. FITS and VO table files or SQL databases).

Initialization
==============

The easiest way to create a table set object is to call the ``TableSet`` class with no arguments::

    tset = TableSet()
    
Manually adding a table to a set
================================

An instance of the ``Table`` class can be added to a set by using the ``append()`` method::

    tset.append(t)

where ``t`` is an instance of the ``Table()`` class. 

Reading in tables from a file or database
=========================================

The ``read()`` method can be used to read in multiple tables from a file or database. This method automatically determines the file or database type and reads in the tables. For example, all the tables in a VO table can be read in using::

    tset.read('somedata.xml')

while all the tables in a FITS file can be read in using::

    tset.read('somedata.fits')

As for the ``Table()`` class, in some cases, ``read()`` will fail to determine the input type. In this case, or to override the automatically selected type, the input type can be specified using the type argument::

    tset.read('somedata.fits.gz', type='fits')


Any arguments passed to ``TableSet()`` when creating a table instance are passed to the ``read()`` method. This can be used to create a ``TableSet()`` instance and fill it with data in a single line. For example, the following::

    tset = TableSet('somedata.xml')

is equivalent to::

    tset = TableSet()
    tset.read('somedata.xml')

Accessing a single table
========================

Single tables can be accessed through the ``TableSet.tables`` python list. For example, the first table in a set can be accessed with::

    tset.tables[0]
    
And all methods associated with single tables are then available. For example, the following shows how to run the ``describe`` method of the first table in a set::

    tset.tables[0].describe()

Adding meta-data
================

As well as having keywords and comments associated with each ``Table``, it is possible to have overall keywords and comments associated with a ``TableSet``.
Comments and keywords can be added to a table using the ``add_comment()`` and ``add_keyword()`` methods::

  >>> tset.add_comment("This is a great table set")
  >>> tset.add_keyword("version", 314)

