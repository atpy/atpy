.. _format_hdf5:

==============
Online queries
==============

It is possible to query online databases and automatically return the results
as a ``Table`` instance. There are several mechanisms for accessing online
catalogs:

Virtual Observatory
-------------------

An interface to the virtual observatory is provided via the `vo
<https://trac6.assembla.com/astrolib>`_ module. To list the catalogs
available, use the ``list_catalogs()`` method from ``atpy.vo_conesearch``::

  >>> from atpy.vo_conesearch import list_catalogs
  >>> list_catalogs()
             USNO-A2
             USNO-B1
          USNO NOMAD
            USNO ACT

A specific catalog can then be queried with a conesearch by specifying a
catalog, and the coordinates and radius (in degrees) to search::

  >>> t = atpy.Table(catalog='USNO-B1', ra=233.112, dec=23.432, radius=0.3, type='vo_conesearch')
  
How long this query takes will depend on the speed of your network, the load
on the server being queried, and the number of rows in the result. For
advanced users, it is also possible to query catalogs not listed by
``list_catalogs()`` - for more details, see the :ref:`fullapi`.

IRSA Query
----------

In addition to supporting Virtual Observatory queries, ATpy supports queries
to the `NASA/IPAC Infrared Science Archive (IRSA)
<http://irsa.ipac.caltech.edu/>`_. The interface is similar to that of the VO.  To list the catalogs
available, use the ``list_catalogs()`` method from ``atpy.irsa_service``::

  >>> from atpy.irsa_service import list_catalogs
  >>> list_catalogs()
              fp_psc  2MASS All-Sky Point Source Catalog (PSC)
              fp_xsc  2MASS All-Sky Extended Source Catalog (XSC)
              lga_v2  The 2MASS Large Galaxy Atlas
         fp_scan_dat  2MASS All-Sky Survey Scan Info 
                 ...  ...
                 
The first column is the catalog code used in the query. A specific catalog can then be queried by specifying a
query type, a catalog,  and additional arguments as required. The different kinds of search are:

* ``Cone``: This is a cone search. Requires ``objstr``, a string containing
  either coordinates or an object name (see `here
  <http://irsa.ipac.caltech.edu/search_help.html>`_ for more information),
  and ``radius``, with units given by ``units`` (``'arcsec'`` by
  default). For example::
  
    >>> t = atpy.Table('Cone', 'fp_psc', objstr='m13', \
                       radius=100., type='irsa')

* ``Box``: This is a box search. Requires ``objstr``, a string containing
  either coordinates or an object name (see `here
  <http://irsa.ipac.caltech.edu/search_help.html>`_ for more
  information), and ``size`` in arcseconds. For example::
  
    >>> t = atpy.Table('Box', 'fp_psc', objstr='T Tau', \
                       size=200., units='deg', type='irsa')
  
* ``Polygon``: This is a polygon search. Requires ``polygon``, which should be
  a list of tuples of (ra, dec) in decimal degrees::
  
    >>> t = atpy.Table('polygon','fp_psc', \
                       polygon=[(11.0, 45.0), (12.0, 45.0), (11.5, 46.)], \
                       type='irsa')
  
As for the VO query, how long these queries takes will depend on the speed of
your network, the load on the IRSA server, and the number of rows in the
result.

.. _fullapi:

Full API for advanced users
---------------------------

.. note ::
    The following functions should not be called directly - the arguments
    should be passed to ``Table()/Table.read()`` using either
    ``type=vo_conesearch`` or ``type=irsa``.
    
.. autofunction:: atpy.vo_conesearch.read
.. autofunction:: atpy.irsa_service.read
