========================
Obtaining and Installing
========================

Requirements
============

Python 2.6 or later is required.

The required dependencies are:

* `NumPy <http://numpy.scipy.org/>`_ 1.5.0 or later

* `Astropy <http://www.astropy.org/>`_ 0.2 or later

In addition, the following packages will optionally extend the ability of ATpy to read/write certain formats:

* `h5py <http://code.google.com/p/h5py/>`_ (HDF5 tables)

* `MySQL-python <http://sourceforge.net/projects/mysql-python>`_ (MySQL
  databases)

* `PyGreSQL <http://www.pygresql.org/>`_ (PostGreSQL databases)

Stable version
==============

The latest stable release of ATpy can be downloaded from `GitHub <https://pypi.python.org/pypi/ATpy>`_. To install ATpy, use the standard installation procedure::

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
