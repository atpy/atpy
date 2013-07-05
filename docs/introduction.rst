============
Introduction
============

ATpy is a high-level Python package providing a way to manipulate tables of
astronomical data in a uniform way. The two main features of ATpy are:

* It provides a Table class that contains data stored in a NumPy structured
  array, along with meta-data to describe the columns, and methods to
  manipulate the table (e.g. adding/removing/renaming columns, selecting rows,
  changing values).

* It provides built-in support for reading and writing to several common
  file/database formats, including FITS, VO, and IPAC tables, and SQLite,
  MySQL and PostgreSQL databases, with a very simple API.

In addition, ATpy provides a TableSet class that can be used to contain multiple tables, and supports reading and writing to file/database formats that support this (FITS, VO, and SQL databases).

Finally, ATpy provides support for user-written read/write functions for file/database formats not supported by default. We encourage users to send us custom read/write functions to read commonly used formats, and would be happy to integrate them into the main distribution.