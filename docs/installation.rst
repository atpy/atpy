========================
Obtaining and Installing
========================

Requirements
============

ATpy requires the following:

- `Python <http://www.python.org>`_ 2.6 or later

- `Numpy <http://www.numpy.org/>`_ 1.5 or later

- `Astropy <http://www.astropy.org>`_ 0.2 or later

The following packages are optional, but are required to read/write to certain
formats:

- `h5py <http://www.h5py.org>`_ 1.3.0 or later (for HDF5 tables)

- `MySQL-python <http://sourceforge.net/projects/mysql-python>`_ 1.2.2 or later
  (for MySQL tables)

- `PyGreSQL <http://www.pygresql.org/>`_ 3.8.1 or later (for PostGreSQL tables)

Stable version
==============

The latest stable release of ATpy can be downloaded from `PyPI <https://pypi.python.org/pypi/ATpy>`_. To install ATpy, use the standard installation procedure::

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
