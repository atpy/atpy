.. _format_sql:

=============
SQL databases
=============

.. note::
    Structured Query Language (SQL) databases are wildly used in web
    infrastructure, and are also used to store large datasets in Science.
    Several flavors exist, the most popular of which are SQLite, MySQL, and
    PostGreSQL.

SQL databases are supported in ATpy thanks to the sqlite module built-in to Python, the `MySQL-python <http://sourceforge.net/projects/mysql-python>`_ module, and the `PyGreSQL <http://www.pygresql.org/>`_ module. When reading from databases, the first argument in ``Table`` should be the database type (one of ``sqlite``, ``mysql``, and ``postgres``). For SQLite databases, which are stored in a file, reading in a table is easy:

  >>> t = atpy.Table('sqlite', 'mydatabase.db')
  
If more than one table is present in the file, the table name can be specified::

  >>> t = atpy.Table('sqlite', 'mydatabase.db', table='observations')

For MySQL databases, standard MySQL parameters can be specified. These include ``user``, ``passwd``, ``db`` (the database name), ``host``, and ``port``. For PostGreSQL databases, standard PostGreSQL parameters can be specified. These include ``user``, ``password``, ``database``, and ``host``.

For example, to read a table called ``velocities`` from a MySQL database called ``measurements``, with a user ``monty`` and password ``spam``, one would use::

  >>> t = atpy.Table('mysql', user='monty', passwd='spam',
                     db='measurements', table='velocities')

To read in all the tables in a database, simply use the ``TableSet`` class, e.g::

  >>> t = atpy.TableSet('sqlite', 'mydatabase.db')

or

  >>> t = atpy.TableSet('mysql', user='monty', passwd='spam',
                        db='measurements')

It is possible to retrieve only a subset of a table, or the result of any standard SQL query, using the ``query`` argument. For example, the following will retrieve all entries where the ``quality`` variable is positive::

  >>> t = atpy.Table('mysql', user='monty', passwd='spam',
                     db='measurements', table='velocities',
                     query='SELECT * FROM velocities WHERE quality > 0;' )
                   
Any valid SQL command should work, including commands used to merge different tables.

Writing tables or table sets to databases is simple, and is done through the ``write`` method. As before, database parameters may need to be specified, e.g.::

  >>> t.write('sqlite', 'mydatabase.db')
  
or

  >>> t.write('mysql', user='monty', passwd='spam',
              db='measurements')

.. note:: 
    As for file formats, the ``verbose`` argument can be specified to
    control whether warning messages are shown when reading (the default is
    ``verbose=True``), and the ``overwrite`` argument can be used when
    writing to overwrite a file (the default is ``overwrite=False``).

Full API for advanced users
---------------------------

.. note ::
    The following functions should not be called directly - the arguments  should be passed to ``Table()/Table.read()``,
    ``Table.write()``, ``TableSet()/TableSet.read()``, and
    ``TableSet.write()`` respectively.
    
.. autofunction:: atpy.sqltable.read
.. autofunction:: atpy.sqltable.write
.. autofunction:: atpy.sqltable.read_set
.. autofunction:: atpy.sqltable.write_set
