#!/usr/bin/env python

from distutils.core import setup

try: # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError: # Python 2.x
    from distutils.command.build_py import build_py


setup(name='ATpy',
      version='0.9.5',
      description='Astronomical Tables in Python',
      author='Eli Bressert and Thomas Robitaille',
      author_email='elibre@users.sourceforge.net, \
        robitaille@users.sourceforge.net',
      url='http://atpy.sourceforge.net/',
      packages=['atpy'],
      cmdclass = {'build_py':build_py},
     )
