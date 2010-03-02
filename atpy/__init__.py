from basetable import Table, TableSet, VectorException
__version__ = '0.9.3'

_readers = {}
_writers = {}
_set_readers = {}
_set_writers = {}
_extensions = {}

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

    s = string.lower()

    if not '.' in s:
        extension = s
    else:
        extension = s.split('.')[-1]
        if extension in ['gz', 'bzip2', 'Z']:
            extension = s.split('.')[-2]

    if extension in _extensions:
        table_type = _extensions[extension]
        if verbose:
            print "Auto-detected input type: %s" % table_type
    else:
        raise Exception('Could not determine input type for extension %s' % extension)

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
