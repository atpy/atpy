from __future__ import print_function, division

import os
from distutils import version
import numpy as np
import warnings

from .exceptions import TableException
from .helpers import smart_dtype
from .decorators import auto_download_to_file, auto_decompress_to_fileobj, auto_fileobj_to_file

vo_minimum_version = version.LooseVersion('0.3')

try:
    from vo.table import parse
    from vo.tree import VOTableFile, Resource, Field, Param
    from vo.tree import Table as VOTable
    vo_installed = True
except:
    vo_installed = False


def _check_vo_installed():
    if not vo_installed:
        raise Exception("Cannot read/write VO table files - vo " +  \
            vo_minimum_version.vstring + " or later required")

# Define type conversion dictionary
type_dict = {}
type_dict[np.bool_] = "boolean"

type_dict[np.uint8] = "unsignedByte"
type_dict[np.int16] = "short"
type_dict[np.int32] = "int"
type_dict[np.int64] = "long"

type_dict[np.float32] = "float"
type_dict[np.float64] = "double"
type_dict[np.str] = "char"
type_dict[np.string_] = "char"
type_dict[str] = "char"


def _list_tables(filename, pedantic=False):
    votable = parse(filename, pedantic=pedantic)
    tables = {}
    for i, table in enumerate(votable.iter_tables()):
        tables[i] = table.name
    return tables


# VO can handle file objects, but because we need to read it twice we don't
# use that capability
@auto_download_to_file
@auto_decompress_to_fileobj
@auto_fileobj_to_file
def read(self, filename, pedantic=False, tid=-1, verbose=True):
    '''
    Read a table from a VOT file

    Required Arguments:

        *filename*: [ string ]
            The VOT file to read the table from

    Optional Keyword Arguments:

        *tid*: [ integer ]
            The ID of the table to read from the VO file (this is
            only required if there are more than one table in the VO file)

        *pedantic*: [ True | False ]
            When *pedantic* is True, raise an error when the file violates
            the VO Table specification, otherwise issue a warning.
    '''

    _check_vo_installed()

    self.reset()

    # If no table is requested, check that there is only one table
    if tid==-1:
        tables = _list_tables(filename, pedantic=pedantic)
        if len(tables) == 1:
            tid = 0
        elif len(tables) == 0:
            raise Exception("There are no tables present in this file")
        else:
            raise TableException(tables, 'tid')

    votable = parse(filename, pedantic=pedantic)
    for id, table in enumerate(votable.iter_tables()):
        if id==tid:
            break

    if table.ID:
        self.table_name = str(table.ID)
    elif table.name:
        self.table_name = str(table.name)

    for field in table.fields:

        colname = field.ID

        data = table.array[colname]

        if len(data) > 0 and data.ndim == 1 and not np.all([np.isscalar(x) for x in data]):
            warnings.warn("VO Variable length vector column detected (%s) - converting to string" % colname)
            data = np.array([str(x) for x in data])

        if self._masked:
            self.add_column(colname, data, \
                unit=field.unit, mask=table.mask[colname], \
                description=field.description)
        else:
            self.add_column(colname, data, \
                unit=field.unit, description=field.description)

    for param in table.params:
        self.add_keyword(param.ID, param.value)


def _to_table(self, vo_table):
    '''
    Return the current table as a VOT object
    '''

    table = VOTable(vo_table)

    # Add keywords
    for key in self.keywords:
        if isinstance(self.keywords[key], basestring):
            arraysize = '*'
        else:
            arraysize = None
        param = Param(table, name=key, ID=key, value=self.keywords[key], arraysize=arraysize)
        table.params.append(param)

    # Define some fields

    n_rows = len(self)

    fields = []
    for i, name in enumerate(self.names):

        data = self.data[name]
        unit = self.columns[name].unit
        description = self.columns[name].description
        dtype = self.columns[name].dtype
        column_type = smart_dtype(dtype)

        if data.ndim > 1:
            arraysize = str(data.shape[1])
        else:
            arraysize = None

        if column_type in type_dict:
            datatype = type_dict[column_type]
        elif column_type == np.int8:
            warnings.warn("int8 unsupported - converting to int16")
            datatype = type_dict[np.int16]
        elif column_type == np.uint16:
            warnings.warn("uint16 unsupported - converting to int32")
            datatype = type_dict[np.int32]
        elif column_type == np.uint32:
            warnings.warn("uint32 unsupported - converting to int64")
            datatype = type_dict[np.int64]
        elif column_type == np.uint64:
            raise Exception("uint64 unsupported")
        else:
            raise Exception("cannot use numpy type " + str(column_type))

        if column_type == np.float32:
            precision = 'F9'
        elif column_type == np.float64:
            precision = 'F17'
        else:
            precision = None

        if datatype == 'char':
            if arraysize is None:
                arraysize = '*'
            else:
                raise ValueError("Cannot write vector string columns to VO files")

        field = Field(vo_table, ID=name, name=name, \
                datatype=datatype, unit=unit, arraysize=arraysize, \
                precision=precision)

        field.description = description

        fields.append(field)

    table.fields.extend(fields)

    table.create_arrays(n_rows)

    # Character columns are stored as object columns in the vo_table
    # instance. Leaving the type as string should work, but causes
    # a segmentation fault on MacOS X with Python 2.6 64-bit so
    # we force the conversion to object type columns.

    for name in self.names:

        dtype = self.columns[name].dtype
        column_type = smart_dtype(dtype)

        # Add data to the table
        # At the moment, null values in VO table are dealt with via a
        # 'mask' record array

        if column_type == np.string_:
            table.array[name] = self.data[name].astype(np.object_)
            if self._masked:
                table.mask[name] = self.data[name].mask.astype(np.object_)
            else:
                table.mask[name] = (self.data[name] == \
                            self.columns[name].null).astype(np.object_)
        else:
            table.array[name] = self.data[name]
            if self._masked:
                table.mask[name] = self.data[name].mask
            else:
                table.mask[name] = self.data[name] == \
                            self.columns[name].null

    table.name = self.table_name

    return table


def write(self, filename, votype='ascii', overwrite=False):
    '''
    Write the table to a VOT file

    Required Arguments:

        *filename*: [ string ]
            The VOT file to write the table to

    Optional Keyword Arguments:

        *votype*: [ 'ascii' | 'binary' ]
            Whether to write the table as ASCII or binary
    '''

    _check_vo_installed()

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    vo_table = VOTableFile()
    resource = Resource()
    vo_table.resources.append(resource)

    resource.tables.append(_to_table(self, vo_table))

    if votype is 'binary':
        vo_table.get_first_table().format = 'binary'
        vo_table.set_all_tables_format('binary')

    vo_table.to_xml(filename)


# VO can handle file objects, but because we need to read it twice we don't
# use that capability
@auto_download_to_file
@auto_decompress_to_fileobj
@auto_fileobj_to_file
def read_set(self, filename, pedantic=False, verbose=True):
    '''
    Read all tables from a VOT file

    Required Arguments:

        *filename*: [ string ]
            The VOT file to read the tables from

    Optional Keyword Arguments:

        *pedantic*: [ True | False ]
            When *pedantic* is True, raise an error when the file violates
            the VO Table specification, otherwise issue a warning.
    '''

    _check_vo_installed()

    self.reset()

    from .basetable import Table
    for tid in _list_tables(filename, pedantic=pedantic):
        t = Table()
        read(t, filename, tid=tid, verbose=verbose, pedantic=pedantic)
        self.append(t)


def write_set(self, filename, votype='ascii', overwrite=False):
    '''
    Write all tables to a VOT file

    Required Arguments:

        *filename*: [ string ]
            The VOT file to write the tables to

    Optional Keyword Arguments:

        *votype*: [ 'ascii' | 'binary' ]
            Whether to write the tables as ASCII or binary tables
    '''

    _check_vo_installed()

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    vo_table = VOTableFile()
    resource = Resource()
    vo_table.resources.append(resource)

    for table_key in self.tables:
        resource.tables.append(_to_table(self.tables[table_key], vo_table))

    if votype is 'binary':
        vo_table.get_first_table().format = 'binary'
        vo_table.set_all_tables_format('binary')

    vo_table.to_xml(filename)
