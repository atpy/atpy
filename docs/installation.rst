========================
Obtaining and Installing
========================

Requirements
============

Python 2.5 or later is required, and Python 2.6 is recommended (as SQLite is included by default).

ATpy relies on a number of different packages to support reading and writing
to different file or database formats. However, the only compulsory package is
`NumPy <http://numpy.scipy.org/>`_. All other requirements are optional - if
they are not present, the relevant read/write methods will be disabled but
will not otherwise prevent ATpy from functioning.

Below is a list of the optional packages that ATpy depends on to support reading and writing to various table types:

* `pyfits <http://www.stsci.edu/resources/software_hardware/pyfits>`_ (FITS
  tables)

* `vo <https://trac6.assembla.com/astrolib>`_ (VO tables)

* `asciitable <http://cxc.harvard.edu/contrib/asciitable/>`_ (ASCII tables)

* `h5py <http://code.google.com/p/h5py/>`_ (HDF5 tables)

* `MySQL-python <http://sourceforge.net/projects/mysql-python>`_ (MySQL
  databases)

* `PyGreSQL <http://www.pygresql.org/>`_ (PostGreSQL databases)

Stable version
==============

The latest stable release of ATpy can be downloaded from `GitHub <https://github.com/atpy/atpy/archives/master>`_. To install ATpy, use the standard installation procedure::

    tar xvzf ATpy-X-X.X.tar.gz
    cd ATpy-X.X.X/
    python setup.py install
    
Developer version
=================

Advanced users wishing to use the latest development ("unstable") version can check it out with::

    git clone git://github.com/atpy/atpy.git
   
which can then be installed with::

    cd atpy
    python setup.py install
