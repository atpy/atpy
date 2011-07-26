import os
import warnings
from ConfigParser import SafeConfigParser

import atpy
from basetable import Table, TableSet, VectorException

__version__ = '0.9.5.3'

_readers = {}
_writers = {}
_set_readers = {}
_set_writers = {}
_extensions = {}


def set_masked_default(choice):
    'Set whether tables should be masked or not by default (True or False)'
    atpy.__masked__ = choice


def register_reader(ttype, function, override=False):
    '''
    Register a table reader function.

    Required Arguments:

        *ttype*: [ string ]
            The table type identifier. This is the string that will be used to
            specify the table type when reading.

        *function*: [ function ]
            The function to read in a single table.

    Optional Keyword Arguments:

        *override*: [ True | False ]
            Whether to override any existing type if already present.
    '''

    if not ttype in _readers or override:
        _readers[ttype] = function
    else:
        raise Exception("Type %s is already defined" % ttype)


def register_writer(ttype, function, override=False):
    '''
    Register a table writer function.

    Required Arguments:

        *ttype*: [ string ]
            The table type identifier. This is the string that will be used to
            specify the table type when writing.

        *function*: [ function ]
            The function to write out a single table.

    Optional Keyword Arguments:

        *override*: [ True | False ]
            Whether to override any existing type if already present.
    '''

    if not ttype in _writers or override:
        _writers[ttype] = function
    else:
        raise Exception("Type %s is already defined" % ttype)


def register_set_reader(ttype, function, override=False):
    '''
    Register a table set reader function.

    Required Arguments:

        *ttype*: [ string ]
            The table type identifier. This is the string that will be used to
            specify the table type when reading.

        *function*: [ function ]
            The function to read in a table set.

    Optional Keyword Arguments:

        *override*: [ True | False ]
            Whether to override any existing type if already present.
    '''

    if not ttype in _set_readers or override:
        _set_readers[ttype] = function
    else:
        raise Exception("Type %s is already defined" % ttype)


def register_set_writer(ttype, function, override=False):
    '''
    Register a table set writer function.

    Required Arguments:

        *ttype*: [ string ]
            The table type identifier. This is the string that will be used to
            specify the table type when writing.

        *function*: [ function ]
            The function to write out a table set.

    Optional Keyword Arguments:

        *override*: [ True | False ]
            Whether to override any existing type if already present.
    '''

    if not ttype in _set_writers or override:
        _set_writers[ttype] = function
    else:
        raise Exception("Type %s is already defined" % ttype)


def register_extensions(ttype, extensions, override=False):
    '''
    Associate file extensions with a specific table type

    Required Arguments:

        *ttype*: [ string ]
            The table type identifier. This is the string that is used to
            specify the table type when reading.

        *extensions*: [ string or list or tuple ]
            List of valid extensions for the table type - used for auto type
            selection. All extensions should be given in lowercase as file
            extensions are converted to lowercase before checking against this
            list. If a single extension is given, it can be specified as a
            string rather than a list of strings

    Optional Keyword Arguments:

        *override*: [ True | False ]
            Whether to override any extensions if already present.
    '''

    if type(extensions) == str:
        extensions = [extensions]

    for extension in extensions:
        if not extension in _extensions or override:
            _extensions[extension] = ttype
        else:
            raise Exception("Extension %s is already defined" % extension)


def _determine_type(string, verbose):

    if type(string) != str:
        raise Exception('Could not determine table type (non-string argument)')

    s = string.lower()

    if not '.' in s:
        extension = s
    else:
        extension = s.split('.')[-1]
        if extension.lower() in ['gz', 'bz2', 'bzip2']:
            extension = s.split('.')[-2]

    if extension in _extensions:
        table_type = _extensions[extension]
        if verbose:
            print "Auto-detected table type: %s" % table_type
    else:
        raise Exception('Could not determine table type for extension %s' % extension)

    return table_type

import fitstable

register_reader('fits', fitstable.read)
register_writer('fits', fitstable.write)
register_set_reader('fits', fitstable.read_set)
register_set_writer('fits', fitstable.write_set)
register_extensions('fits', ['fit', 'fits'])

import votable

register_reader('vo', votable.read)
register_writer('vo', votable.write)
register_set_reader('vo', votable.read_set)
register_set_writer('vo', votable.write_set)
register_extensions('vo', ['xml', 'vot'])

import ipactable

register_reader('ipac', ipactable.read)
register_writer('ipac', ipactable.write)
register_extensions('ipac', ['ipac', 'tbl'])

import sqltable

register_reader('sql', sqltable.read)
register_writer('sql', sqltable.write)
register_set_reader('sql', sqltable.read_set)
register_set_writer('sql', sqltable.write_set)
register_extensions('sql', ['sqlite', 'postgres', 'mysql', 'db'])

import asciitables

register_reader('cds', asciitables.read_cds)
register_reader('mrt', asciitables.read_cds)

register_reader('rdb', asciitables.read_rdb)
register_writer('rdb', asciitables.write_rdb)
register_extensions('rdb', ['rdb'])

register_reader('daophot', asciitables.read_daophot)

register_reader('ascii', asciitables.read_ascii)
register_writer('ascii', asciitables.write_ascii)

import hdf5table

register_reader('hdf5', hdf5table.read)
register_set_reader('hdf5', hdf5table.read_set)
register_writer('hdf5', hdf5table.write)
register_set_writer('hdf5', hdf5table.write_set)
register_extensions('hdf5', ['hdf5', 'h5'])

import irsa_service

register_reader('irsa', irsa_service.read)

import vo_conesearch

register_reader('vo_conesearch', vo_conesearch.read)

import htmltable

register_writer('html', htmltable.write)
register_extensions('html', ['html', 'htm'])

set_masked_default(False)

filename = os.path.expanduser('~/.atpyrc')
config = SafeConfigParser()
config.read(filename)
if config.has_option('general', 'masked_default'):
    if config.getboolean('general', 'masked_default'):
        warnings.warn(".atpyrc file found - masked arrays are ON by default")
        set_masked_default(True)
    else:
        warnings.warn(".atpyrc file found - masked arrays are OFF by default")
        set_masked_default(False)
