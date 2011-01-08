import os
from distutils import version
import numpy as np
import warnings
import re

from exceptions import TableException

import atpy

from helpers import smart_dtype

vo_minimum_version = version.LooseVersion('0.3')

try:
    from vo.table import parse
    from vo.tree import VOTableFile, Resource, Table, Field
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

        if type(field.name) == str:
            colname = field.name
        else:
            if type(field._ID) == str:
                colname = field._ID
            else:
                raise Exception("Error reading in the VO table: no name or ID for field")

        # Ensure that colname is a valid python variable name (i.e. contains
        # no non-allowed chars). The following will replace any invalid chars
        # with underscores, and/or prepend an initial underscore to names
        # that begin with a digit (patch provided by Marshall Perrin)
        clean = lambda varStr: re.sub('\W|^(?=\d)', '_', varStr)
        colname = clean(colname)

        if self._masked:
            self.add_column(colname, table.array[colname], \
                unit=field.unit, mask=table.mask[colname])
        else:
            self.add_column(colname, table.array[colname], \
                unit=field.unit)


def _to_table(self, VOTable):
    '''
    Return the current table as a VOT object
    '''

    table = Table(VOTable)

    # Define some fields

    n_rows = len(self)

    fields = []
    for i, name in enumerate(self.names):

        data = self.data[name]
        unit = self.columns[name].unit
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

        fields.append(Field(VOTable, ID="col" + str(i), name=name, \
                datatype=datatype, unit=unit, arraysize=arraysize, \
                precision=precision))

    table.fields.extend(fields)

    table.create_arrays(n_rows)

    # Character columns are stored as object columns in the VOTable
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

    VOTable = VOTableFile()
    resource = Resource()
    VOTable.resources.append(resource)

    resource.tables.append(_to_table(self, VOTable))

    if votype is 'binary':
        VOTable.get_first_table().format = 'binary'
        VOTable.set_all_tables_format('binary')

    VOTable.to_xml(filename)


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

    for tid in _list_tables(filename, pedantic=pedantic):
        t = atpy.Table()
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

    VOTable = VOTableFile()
    resource = Resource()
    VOTable.resources.append(resource)

    for table_key in self.tables:
        resource.tables.append(_to_table(self.tables[table_key], VOTable))

    if votype is 'binary':
        VOTable.get_first_table().format = 'binary'
        VOTable.set_all_tables_format('binary')

    VOTable.to_xml(filename)
