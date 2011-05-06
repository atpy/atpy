#!/usr/bin/env python

from distutils.core import setup

try: # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError: # Python 2.x
    from distutils.command.build_py import build_py


setup(name='ATpy',
      version='0.9.5.1',
      description='Astronomical Tables in Python',
      author='Thomas Robitaille and Eli Bressert',
      author_email='thomas.robitaille@gmail.com, elibre@users.sourceforge.net',
      license='MIT',
      url='http://atpy.github.com/',
      packages=['atpy'],
      provides=['atpy'],
      requires=['numpy'],
      cmdclass = {'build_py':build_py},
      keywords=['Scientific/Engineering'],
      classifiers=[
                   "Development Status :: 4 - Beta",
                   "Programming Language :: Python",
                   "License :: OSI Approved :: MIT License",
                  ],
     )
