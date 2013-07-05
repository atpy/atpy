.. _maskingandnull:

=======================
Masking and null values
=======================

It is often useful to be able to define missing or invalid values in a table. There are currently two ways to do this in ATpy, :ref:`null`, and :ref:`masking`. The preferred way is to use Masking, but this requires at least NumPy 1.4.1 in most cases, and the latest svn version of NumPy for SQL database input/output. Therefore, for version 0.9.4 of ATpy, the default is to use the Null value method. To opt-in to using masked arrays, specify the ``masked=True`` argument when creating a ``Table`` instance::

   >>> t = Table('example.fits.gz', masked=True)
   
In future, once NumPy 1.5.0 is out, we will switch over to using masked arrays by default, and will slowly phase out the Null value method.

If you want to set the default for masking to be on or off for a whole script, this can be done using the ``set_masked_default`` function::

  import atpy
  atpy.set_masked_default(True)
  
If you want to set the default for masking on a user-level, create a file named ``~/.atpyrc`` in your home directory, containing::

  [general]
  masked_default:yes
  
The ``set_masked_default`` function overrides the ``.atpyrc`` file, and the ``masked=`` argument in Table overrides both the ``set_masked_default`` function and the ``.atpyrc`` file.
   
.. _null:
   
Null values
===========

The basic idea behind this method is to specify a special value in each column that will signify missing or invalid data. To specify the Null value for a column, use the ``null`` argument in ``add_column``::

  >>> t.add_column('time', time, null=-999.)
  
Following this, if the table is written out to a file or database, this null value will be stored.

This method is generally unreliable, especially for floating point values, and does not allow users to easily distinguish between invalid and missing values.

.. _masking:

Masking
=======

NumPy supports masked arrays, where specific elements of an array can be properly masked by using a *mask* - a boolean array. There are several advantages to using this: 

* The mask is unrelated to the value in the cell - any cell can be masked, not
  just all cells with a specific value

* It is possible to distinguish between invalid (e.g. NaN) and missing values

* Values can easily be unmasked (although when writing to a file/database, the
  'old' values are lost for masked elements).
  
* NumPy provides masked versions of many functions, for example ``sum``,
  ``mean``, or ``median``, which means that it is easy to correctly compute
  statistics on masked arrays, ignoring the masked values.

To specify the mask of a column, use the ``mask`` argument in ``add_column``. To do the equivalent to the example in :ref:`null`, use::

   >>> t.add_column('time', time, mask=time==-999.)

When writing out to certain file/database formats, a masked value has to be given a specific value - this is called a *fill* value. To set the fill value, simply use the ``fill`` argument when adding data to a column:

    >>> t.add_column('time', time, mask=time==-999., fill=-999.)

In the above example, if the table is written out to an IPAC table, the value of -999. will be used for masked values.

.. note::
    When implementing this in ATpy, we discovered a few bugs in the masked
    structured implementation of NumPy, which have now been fixed. Therefore,
    we recommend using the latest svn version of NumPy if you want to use
    masked arrays.
