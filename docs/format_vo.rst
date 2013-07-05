.. _format_vo:

=========
VO tables
=========

.. note::
    Virtual Observatory (VO) tables are a new format developed by the
    International Virtual Observatory Alliance to store one or more tables.
    It is a format based on the Extensible Markup Language (XML).

VO tables are supported thanks to the `vo <https://trac6.assembla.com/astrolib>`_ module. Reading VO tables is straightforward::

  >>> t = atpy.Table('table.vot')
  
If more than one table is present in the file, ATpy will give a list of available tables, identified by an ID (``tid``). The specific table to read can then be specified with the ``tid=`` argument::

  >>> t = atpy.Table('table.vot', tid=2)
  
To read in all tables in a file, use the ``TableSet`` class::

  >>> t = atpy.TableSet('table.vot') 

In some cases, the VO table file may not be strictly standard compliant. When reading in a VO table, it is possible to specify an argument which controls whether to adhere strictly to standards and throw an exception if any errors are found (``pedantic=True``), or whether to relax the requirements and accept non-standard features (``pedantic=False``). The latter is the default.

Finally, when writing out a VO table, the default is to use ASCII VO tables (analogous to ASCII FITS tables). It is also possible to write tables out in binary VO format. To do this, use the ``votype`` argument:

  >>> t.write('table.vot', votype='binary')
  
The default is ``votype='ascii'``.

In the event that ATpy does not recognize a VO table (for example if the file extension is obscure),  the type can be explicitly given::

  >>> t = atpy.Table('table', type='vo')
  
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
        
.. autofunction:: atpy.votable.read
.. autofunction:: atpy.votable.write
.. autofunction:: atpy.votable.read_set
.. autofunction:: atpy.votable.write_set

