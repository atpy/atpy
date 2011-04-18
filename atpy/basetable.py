# Need to depracate fits_read, etc.

import warnings
import atpy

import numpy as np
import numpy.ma as ma

from copy import deepcopy
import string

from exceptions import VectorException

import structhelper as sta
from odict import odict

default_format = {}
default_format[None.__class__] = 16, '.9e'
default_format[np.bool_] = 1, 'i'
default_format[np.int8] = 3, 'i'
default_format[np.uint8] = 3, 'i'
default_format[np.int16] = 5, 'i'
default_format[np.uint16] = 5, 'i'
default_format[np.int32] = 12, 'i'
default_format[np.uint32] = 12, 'i'
default_format[np.int64] = 22, 'i'
default_format[np.uint64] = 23, 'i'
default_format[np.float32] = 16, '.8e'
default_format[np.float64] = 25, '.17e'
default_format[np.str] = 0, 's'
default_format[np.string_] = 0, 's'
default_format[np.uint8] = 0, 's'
default_format[str] = 0, 's'
default_format[np.unicode_] = 0, 's'


class ColumnHeader(object):

    def __init__(self, dtype, unit=None, description=None, null=None, format=None):
        self.__dict__['dtype'] = dtype
        self.unit = unit
        self.description = description
        self.__dict__['null'] = null
        self.format = format

    def __setattr__(self, attribute, value):
        if attribute in ['unit', 'description', 'format']:
            self.__dict__[attribute] = value
        elif attribute in ['null', 'dtype']:
            raise Exception("Cannot change %s through the columns object" % attribute)
        else:
            raise AttributeError(attribute)

    def __repr__(self):
        s = "type=%s" % str(self.dtype)
        if self.unit:
            s += ", unit=%s" % str(self.unit)
        if self.null:
            s += ", null=%s" % str(self.null)
        if self.description:
            s += ", description=%s" % self.description
        return s

    def __eq__(self, other):
        if self.dtype != other.dtype:
            return False
        if self.unit != other.unit:
            return False
        if self.description != other.description:
            return False
        if self.null != other.null:
            if np.isnan(self.null):
                if not np.isnan(other.null):
                    return False
            else:
                return False
        if self.format != other.format:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class Table(object):

    def fits_read(self, *args, **kwargs):
        warnings.warn("WARNING: fits_read is deprecated; use read instead")
        kwargs['type'] = 'fits'
        self.read(*args, **kwargs)

    def vo_read(self, *args, **kwargs):
        warnings.warn("WARNING: vo_read is deprecated; use read instead")
        kwargs['type'] = 'vo'
        self.read(*args, **kwargs)

    def sql_read(self, *args, **kwargs):
        warnings.warn("WARNING: sql_read is deprecated; use read instead")
        kwargs['type'] = 'sql'
        self.read(*args, **kwargs)

    def ipac_read(self, *args, **kwargs):
        warnings.warn("WARNING: ipac_read is deprecated; use read instead")
        kwargs['type'] = 'ipac'
        self.read(*args, **kwargs)

    def fits_write(self, *args, **kwargs):
        warnings.warn("WARNING: fits_write is deprecated; use write instead")
        kwargs['type'] = 'fits'
        self.write(*args, **kwargs)

    def vo_write(self, *args, **kwargs):
        warnings.warn("WARNING: vo_write is deprecated; use write instead")
        kwargs['type'] = 'vo'
        self.write(*args, **kwargs)

    def sql_write(self, *args, **kwargs):
        warnings.warn("WARNING: sql_write is deprecated; use write instead")
        kwargs['type'] = 'sql'
        self.write(*args, **kwargs)

    def ipac_write(self, *args, **kwargs):
        warnings.warn("WARNING: ipac_write is deprecated; use write instead")
        kwargs['type'] = 'ipac'
        self.write(*args, **kwargs)

    def __repr__(self):
        s = "<Table name='%s' rows=%i fields=%i>" % (self.table_name, self.__len__(), len(self.columns))
        return s

    def __init__(self, *args, **kwargs):
        '''
        Create a table instance

        Optional Arguments:

            If no arguments are given, and empty table is created

            If one or more arguments are given they are passed to the
            Table.read() method.

        Optional Keyword Arguments (independent of table type):

            *name*: [ string ]
                The table name

            *masked*: [ True | False ]
                Whether to use masked arrays. WARNING: this feature is
                experimental and will only work correctly with the svn version
                of numpy post-revision 8025. Note that this overrides the
                default set by atpy.set_masked_default.
        '''

        self.reset()

        if 'name' in kwargs:
            self.table_name = kwargs.pop('name')
        else:
            self.table_name = None

        if 'masked' in kwargs:
            self._masked = kwargs.pop('masked')
        else:
            self._masked = atpy.__masked__

        if len(args) + len(kwargs) > 0:
            self.read(*args, **kwargs)

        return

    def read(self, *args, **kwargs):
        '''
        Read in a table from a file/database.

        Optional Keyword Arguments (independent of table type):

            *verbose*: [ True | False ]
                Whether to print out warnings when reading (default is True)

            *type*: [ string ]
                The read method attempts to automatically guess the
                file/database format based on the arguments supplied. The type
                can be overridden by setting this argument.
        '''

        if 'verbose' in kwargs:
            verbose = kwargs['verbose']
        else:
            verbose = True

        if 'type' in kwargs:
            table_type = kwargs.pop('type').lower()
        elif type(args[0]) == str:
            table_type = atpy._determine_type(args[0], verbose)
        else:
            raise Exception('Could not determine table type')

        original_filters = warnings.filters[:]

        if verbose:
            warnings.simplefilter("always")
        else:
            warnings.simplefilter("ignore")

        try:

            if verbose:
                warnings.simplefilter("always")
            else:
                warnings.simplefilter("ignore")

            if table_type in atpy._readers:
                atpy._readers[table_type](self, *args, **kwargs)
            else:
                raise Exception("Unknown table type: " + table_type)

        finally:
            warnings.filters = original_filters

        return

    def write(self, *args, **kwargs):
        '''
        Write out a table to a file/database.

        Optional Keyword Arguments (independent of table type):

            *verbose*: [ True | False ]
                Whether to print out warnings when writing (default is True)

            *type*: [ string ]
                The read method attempts to automatically guess the
                file/database format based on the arguments supplied. The type
                can be overridden by setting this argument.
        '''

        if 'verbose' in kwargs:
            verbose = kwargs.pop('verbose')
        else:
            verbose = True

        if 'type' in kwargs:
            table_type = kwargs.pop('type').lower()
        elif type(args[0]) == str:
            table_type = atpy._determine_type(args[0], verbose)
        else:
            raise Exception('Could not determine table type')

        original_filters = warnings.filters[:]

        if verbose:
            warnings.simplefilter("always")
        else:
            warnings.simplefilter("ignore")

        try:

            if table_type in atpy._writers:
                atpy._writers[table_type](self, *args, **kwargs)
            else:
                raise Exception("Unknown table type: " + table_type)

        finally:
            warnings.filters = original_filters

        return

    def __getattr__(self, attribute):

        if attribute == 'names':
            return self.__dict__['data'].dtype.names
        elif attribute == 'units':
            print "WARNING: Table.units is depracated - use Table.columns to access this information"
            return dict([(name, self.columns[name].unit) for name in self.names])
        elif attribute == 'types':
            print "WARNING: Table.types is depracated - use Table.columns to access this information"
            return dict([(name, self.columns[name].type) for name in self.names])
        elif attribute == 'nulls':
            print "WARNING: Table.nulls is depracated - use Table.columns to access this information"
            return dict([(name, self.columns[name].null) for name in self.names])
        elif attribute == 'formats':
            print "WARNING: Table.formats is depracated - use Table.columns to access this information"
            return dict([(name, self.columns[name].format) for name in self.names])
        elif attribute == 'shape':
            return (len(self.data), len(self.names))
        else:
            try:
                return self.__dict__['data'][attribute]
            except:
                raise AttributeError(attribute)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        if 'data' in self.__dict__:
            if isinstance(self.data, np.ndarray):
                if item in self.data.dtype.names:
                    self.data[item] = value
                    return
        raise ValueError("Column %s does not exist" % item)

    def keys(self):
        return self.data.dtype.names

    def append(self, table):
        for colname in self.columns:
            if self.columns[colname] != table.columns[colname]:
                raise Exception("Columns do not match")
        self.data = np.hstack((self.data, table.data))

    def __setattr__(self, attribute, value):
        if 'data' in self.__dict__:
            if isinstance(self.data, np.ndarray):
                if attribute in self.data.dtype.names:
                    self.data[attribute] = value
                    return
        self.__dict__[attribute] = value

    def __len__(self):
        if len(self.columns) == 0:
            return 0
        else:
            return len(self.data)

    def reset(self):
        '''
        Empty the table
        '''
        self.keywords = odict()
        self.comments = []
        self.columns = odict()
        self.data = None
        self._primary_key = None
        return

    def _raise_vector_columns(self):
        names = []
        for name in self.names:
            if self.data[name].ndim > 1:
                names.append(name)
        if names:
            names = string.join(names, ", ")
            raise VectorException(names)
        return

    def _setup_table(self, n_rows, dtype, units=None, descriptions=None, formats=None, nulls=None):

        if self._masked:
            self.data = ma.zeros(n_rows, dtype=dtype)
        else:
            self.data = np.zeros(n_rows, dtype=dtype)

        for i in range(len(dtype)):

            if units is None:
                unit = None
            else:
                unit = units[i]

            if descriptions is None:
                description = None
            else:
                description = descriptions[i]

            if formats is None:
                if dtype[i].subdtype:
                    format = default_format[dtype[i].subdtype[0].type]
                else:
                    format = default_format[dtype[i].type]
            else:
                format = formats[i]

            if format[1] == 's':
                format = self.data.itemsize, 's'

            if nulls is None:
                null = None
            else:
                null = nulls[i]

            column = ColumnHeader(dtype[i], unit=unit, description=description, null=null, format=format)

            self.columns[dtype.names[i]] = column

    def add_empty_column(self, name, dtype, unit='', null='', \
        description='', format=None, column_header=None, shape=None, before=None, after=None, \
        position=None):
        '''
        Add an empty column to the table. This only works if there
        are already existing columns in the table.

        Required Arguments:

            *name*: [ string ]
                The name of the column to add

            *dtype*: [ numpy type ]
                Numpy type of the column. This is the equivalent to
                the dtype= argument in numpy.array

        Optional Keyword Arguments:

            *unit*: [ string ]
                The unit of the values in the column

            *null*: [ same type as data ]
                The values corresponding to 'null', if not NaN

            *description*: [ string ]
                A description of the content of the column

            *format*: [ string ]
                The format to use for ASCII printing

            *column_header*: [ ColumnHeader ]
                The metadata from an existing column to copy over. Metadata
                includes the unit, null value, description, format, and dtype.
                For example, to create a column 'b' with identical metadata to
                column 'a' in table 't', use:

                    >>> t.add_column('b', column_header=t.columns[a])

            *shape*: [ tuple ]
                Tuple describing the shape of the empty column that is to be
                added. If a one element tuple is specified, it is the number
                of rows. If a two element tuple is specified, the first is the
                number of rows, and the second is the width of the column.

            *before*: [ string ]
                Column before which the new column should be inserted

            *after*: [ string ]
                Column after which the new column should be inserted

            *position*: [ integer ]
                Position at which the new column should be inserted (0 = first
                column)
        '''
        if shape:
            data = np.zeros(shape, dtype=dtype)
        elif self.__len__() > 0:
            data = np.zeros(self.__len__(), dtype=dtype)
        else:
            raise Exception("Table is empty, you need to use the shape= argument to specify the dimensions of the first column")

        self.add_column(name, data, unit=unit, null=null, \
            description=description, format=format, column_header=column_header, before=before, \
            after=after, position=position)

    def add_column(self, name, data, unit='', null='', description='', \
        format=None, dtype=None, column_header=None, before=None, after=None, position=None, mask=None, fill=None):
        '''
        Add a column to the table

        Required Arguments:

            *name*: [ string ]
                The name of the column to add

            *data*: [ numpy array ]
                The column data

        Optional Keyword Arguments:

            *unit*: [ string ]
                The unit of the values in the column

            *null*: [ same type as data ]
                The values corresponding to 'null', if not NaN

            *description*: [ string ]
                A description of the content of the column

            *format*: [ string ]
                The format to use for ASCII printing

            *dtype*: [ numpy type ]
                Numpy type to convert the data to. This is the equivalent to
                the dtype= argument in numpy.array

            *column_header*: [ ColumnHeader ]
                The metadata from an existing column to copy over. Metadata
                includes the unit, null value, description, format, and dtype.
                For example, to create a column 'b' with identical metadata to
                column 'a' in table 't', use:

                    >>> t.add_column('b', column_header=t.columns[a])

            *before*: [ string ]
                Column before which the new column should be inserted

            *after*: [ string ]
                Column after which the new column should be inserted

            *position*: [ integer ]
                Position at which the new column should be inserted (0 = first
                column)

            *mask*: [ numpy array ]
                An array of booleans, with the same dimensions as the data,
                indicating whether or not to mask values.

            *fill*: [ value ]
                If masked arrays are used, this value is used as the fill
                value in the numpy masked array.
        '''

        if column_header is not None:

            if dtype is not None:
                warnings.warn("dtype= argument overriden by column_header=")
            dtype = column_header.dtype

            if unit != '':
                warnings.warn("unit= argument overriden by column_header=")
            unit = column_header.unit

            if null != '':
                warnings.warn("null= argument overriden by column_header=")
            null = column_header.null

            if description != '':
                warnings.warn("description= argument overriden by column_header=")
            description = column_header.description

            if format is not None:
                warnings.warn("format= argument overriden by column_header=")
            format = column_header.format

        if self._masked:
            if null:
                warnings.warn("null= argument can only be used if Table does not use masked arrays (ignored)")
            data = ma.array(data, dtype=dtype, mask=mask, fill_value=fill)
        else:
            if np.any(mask):
                warnings.warn("mask= argument can only be used if Table uses masked arrays (ignored)")
            data = np.array(data, dtype=dtype)

        dtype = data.dtype

        if dtype.type == np.object_:

            if len(data) == 0:
                longest = 0
            else:
                longest = len(max(data, key=len))

            if self._masked:
                data = ma.array(data, dtype='|%iS' % longest)
            else:
                data = np.array(data, dtype='|%iS' % longest)

            dtype = data.dtype

        if data.ndim > 1:
            newdtype = (name, data.dtype, data.shape[1])
        else:
            newdtype = (name, data.dtype)

        if before:
            try:
                position = list(self.names).index(before)
            except:
                raise Exception("Column %s does not exist" % before)
        elif after:
            try:
                position = list(self.names).index(after) + 1
            except:
                raise Exception("Column %s does not exist" % before)

        if len(self.columns) > 0:
            self.data = sta.append_field(self.data, data, dtype=newdtype, position=position, masked=self._masked)
        else:
            if self._masked:
                self.data = ma.array(zip(data), dtype=[newdtype], mask=zip(data.mask), fill_value=data.fill_value)
            else:
                self.data = np.array(zip(data), dtype=[newdtype])

        if not format:
            format = default_format[dtype.type]

        if format[1] == 's':
            format = data.itemsize, 's'

        column = ColumnHeader(dtype, unit=unit, description=description, null=null, format=format)

        if not np.equal(position, None):
            self.columns.insert(position, name, column)
        else:
            self.columns[name] = column

        return

    def remove_column(self, remove_name):
        print "WARNING: remove_column is depracated - use remove_columns instead"
        self.remove_columns([remove_name])
        return

    def remove_columns(self, remove_names):
        '''
        Remove several columns from the table

        Required Argument:

            *remove_names*: [ list of strings ]
                A list containing the names of the columns to remove
        '''

        if type(remove_names) == str:
            remove_names = [remove_names]

        for remove_name in remove_names:
            self.columns.pop(remove_name)

        self.data = sta.drop_fields(self.data, remove_names, masked=self._masked)

        # Remove primary key if needed
        if self._primary_key in remove_names:
            self._primary_key = None

        return

    def keep_columns(self, keep_names):
        '''
        Keep only specific columns in the table (remove the others)

        Required Argument:

            *keep_names*: [ list of strings ]
                A list containing the names of the columns to keep.
                All other columns will be removed.
        '''

        if type(keep_names) == str:
            keep_names = [keep_names]

        remove_names = list(set(self.names) - set(keep_names))

        if len(remove_names) == len(self.names):
            raise Exception("No columns to keep")

        self.remove_columns(remove_names)

        return

    def rename_column(self, old_name, new_name):
        '''
        Rename a column from the table

        Require Arguments:

            *old_name*: [ string ]
                The current name of the column.

            *new_name*: [ string ]
                The new name for the column
        '''

        if new_name in self.names:
            raise Exception("Column " + new_name + " already exists")

        if not old_name in self.names:
            raise Exception("Column " + old_name + " not found")

        # tuple.index was only introduced in Python 2.6, so need to use list()
        pos = list(self.names).index(old_name)
        self.data.dtype.names = self.names[:pos] + (new_name, ) + self.names[pos + 1:]

        if self._masked:
            self.data.mask.dtype.names = self.data.dtype.names[:]

        self.columns.rename(old_name, new_name)

        # Update primary key if needed
        if self._primary_key == old_name:
            self._primary_key = new_name

        return

    def describe(self):
        '''
        Prints a description of the table
        '''

        if self.table_name:
            print "Table : " + self.table_name
        else:
            print "Table has no name"

        # Find maximum column widths
        len_name_max, len_unit_max, len_datatype_max, \
            len_formats_max = 4, 4, 4, 6

        for name in self.names:
            len_name_max = max(len(name), len_name_max)
            len_unit_max = max(len(str(self.columns[name].unit)), len_unit_max)
            len_datatype_max = max(len(str(self.columns[name].dtype)), \
                len_datatype_max)
            len_formats_max = max(len(self.columns[name].format), len_formats_max)

        # Print out table

        format = "| %" + str(len_name_max) + \
            "s | %" + str(len_unit_max) + \
            "s | %" + str(len_datatype_max) + \
            "s | %" + str(len_formats_max) + "s |"

        len_tot = len_name_max + len_unit_max + len_datatype_max + \
            len_formats_max + 13

        print "-" * len_tot
        print format % ("Name", "Unit", "Type", "Format")
        print "-" * len_tot

        for name in self.names:
            print format % (name, str(self.columns[name].unit), \
                str(self.columns[name].dtype), self.format(name))

        print "-" * len_tot

        return

    def sort(self, keys):
        '''
        Sort the table according to one or more keys. This operates
        on the existing table (and does not return a new table).

        Required arguments:

            *keys*: [ string | list of strings ]
                The key(s) to order by
        '''
        if not type(keys) == list:
            keys = [keys]
        self.data.sort(order=keys)

    def row(self, row_number, python_types=False):
        '''
        Returns a single row

        Required arguments:

            *row_number*: [ integer ]
                The row number (the first row is 0)

        Optional Keyword Arguments:

            *python_types*: [ True | False ]
                Whether to return the row elements with python (True)
                or numpy (False) types.
        '''

        if python_types:
            return list(self.data[row_number].tolist())
        else:
            return self.data[row_number]

    def rows(self, row_ids):
        '''
        Select specific rows from the table and return a new table instance

        Required Argument:

            *row_ids*: [ list | np.int array ]
                A python list or numpy array specifying which rows to select,
                and in what order.

        Returns:

            A new table instance, containing only the rows selected
        '''
        return self.where(np.array(row_ids, dtype=int))

    def where(self, mask):
        '''
        Select matching rows from the table and return a new table instance

        Required Argument:

            *mask*: [ np.bool array ]
                A boolean array with the same length as the table.

        Returns:

            A new table instance, containing only the rows selected
        '''

        new_table = self.__class__()

        new_table.table_name = deepcopy(self.table_name)

        new_table.columns = deepcopy(self.columns)
        new_table.keywords = deepcopy(self.keywords)
        new_table.comments = deepcopy(self.comments)

        new_table.data = self.data[mask]

        return new_table

    def format(self, name):
        '''
        Return the ASCII format of a given column

        Required Arguments:

            *name*: [ string ]
                The column name
        '''
        return str(self.columns[name].format[0]) + self.columns[name].format[1]

    def add_comment(self, comment):
        '''
        Add a comment to the table

        Required Argument:

            *comment*: [ string ]
                The comment to add to the table
        '''

        self.comments.append(comment.strip())
        return

    def add_keyword(self, key, value):
        '''
        Add a keyword/value pair to the table

        Required Arguments:

            *key*: [ string ]
                The name of the keyword

            *value*: [ string | float | integer | bool ]
                The value of the keyword
        '''

        if type(value) == str:
            value = value.strip()
        self.keywords[key.strip()] = value
        return

    def set_primary_key(self, key):
        '''
        Set the name of the table column that should be used as a unique
        identifier for the record. This is the same as primary keys in SQL
        databases. A primary column cannot contain NULLs and must contain only
        unique quantities.

        Required Arguments:

            *key*: [ string ]
                The column to use as a primary key
        '''

        if not key in self.names:
            raise Exception("No such column: %s" % key)
        else:
            if self.columns[key].null != '':
                if np.any(self.data[key] == self.columns[key].null):
                    raise Exception("Primary key column cannot contain null values")
            elif len(np.unique(self.data[key])) != len(self.data[key]):
                raise Exception("Primary key column cannot contain duplicate values")
            else:
                self._primary_key = key

        return


class TableSet(object):

    def fits_read(self, *args, **kwargs):
        warnings.warn("WARNING: fits_read is deprecated; use read instead")
        kwargs['type'] = 'fits'
        self.read(*args, **kwargs)

    def vo_read(self, *args, **kwargs):
        warnings.warn("WARNING: vo_read is deprecated; use read instead")
        kwargs['type'] = 'vo'
        self.read(*args, **kwargs)

    def sql_read(self, *args, **kwargs):
        warnings.warn("WARNING: sql_read is deprecated; use read instead")
        kwargs['type'] = 'sql'
        self.read(*args, **kwargs)

    def ipac_read(self, *args, **kwargs):
        warnings.warn("WARNING: ipac_read is deprecated; use read instead")
        kwargs['type'] = 'ipac'
        self.read(*args, **kwargs)

    def fits_write(self, *args, **kwargs):
        warnings.warn("WARNING: fits_write is deprecated; use write instead")
        kwargs['type'] = 'fits'
        self.write(*args, **kwargs)

    def vo_write(self, *args, **kwargs):
        warnings.warn("WARNING: vo_write is deprecated; use write instead")
        kwargs['type'] = 'vo'
        self.write(*args, **kwargs)

    def sql_write(self, *args, **kwargs):
        warnings.warn("WARNING: sql_write is deprecated; use write instead")
        kwargs['type'] = 'sql'
        self.write(*args, **kwargs)

    def ipac_write(self, *args, **kwargs):
        warnings.warn("WARNING: ipac_write is deprecated; use write instead")
        kwargs['type'] = 'ipac'
        self.write(*args, **kwargs)

    def reset(self):
        '''
        Empty the table set
        '''
        self.tables = odict()
        self.keywords = {}
        self.comments = []
        return

    def __init__(self, *args, **kwargs):
        '''
        Create a table set instance

        Optional Arguments:

            If no arguments are given, an empty table set will be created.

            If one of the arguments is a list or a Table instance, then only
            this argument will be used.

            If one or more arguments are present, they are passed to the read
            method

        Optional Keyword Arguments (independent of table type):

            *masked*: [ True | False ]
                Whether to use masked arrays. WARNING: this feature is
                experimental and will only work correctly with the svn version
                of numpy post-revision 8025. Note that this overrides the
                default set by atpy.set_masked_default.


        '''

        self.reset()

        if len(args) == 1:

            arg = args[0]

            if type(arg) == list:
                for table in arg:
                    self.append(table)
                return

            elif isinstance(arg, TableSet):
                for table in arg.tables:
                    self.append(table)
                return

        # Pass arguments to read
        if len(args) + len(kwargs) > 0:
            self.read(*args, **kwargs)

        return

    def read(self, *args, **kwargs):
        '''
        Read in a table set from a file/database.

        Optional Keyword Arguments (independent of table type):

            *verbose*: [ True | False ]
                Whether to print out warnings when reading (default is True)

            *type*: [ string ]
                The read method attempts to automatically guess the
                file/database format based on the arguments supplied. The type
                can be overridden by setting this argument.
        '''

        if 'verbose' in kwargs:
            verbose = kwargs['verbose']
        else:
            verbose = True

        if 'type' in kwargs:
            table_type = kwargs.pop('type').lower()
        elif type(args[0]) == str:
            table_type = atpy._determine_type(args[0], verbose)
        else:
            raise Exception('Could not determine table type')

        original_filters = warnings.filters[:]

        if verbose:
            warnings.simplefilter("always")
        else:
            warnings.simplefilter("ignore")

        try:

            if verbose:
                warnings.simplefilter("always")
            else:
                warnings.simplefilter("ignore")

            if table_type in atpy._set_readers:
                atpy._set_readers[table_type](self, *args, **kwargs)
            else:
                raise Exception("Unknown table type: " + table_type)

        finally:
            warnings.filters = original_filters

        return

    def write(self, *args, **kwargs):
        '''
        Write out a table set to a file/database.

        Optional Keyword Arguments (independent of table type):

            *verbose*: [ True | False ]
                Whether to print out warnings when writing (default is True)

            *type*: [ string ]
                The read method attempts to automatically guess the
                file/database format based on the arguments supplied. The type
                can be overridden by setting this argument.
        '''

        if 'verbose' in kwargs:
            verbose = kwargs.pop('verbose')
        else:
            verbose = True

        if 'type' in kwargs:
            table_type = kwargs.pop('type').lower()
        elif type(args[0]) == str:
            table_type = atpy._determine_type(args[0], verbose)
        else:
            raise Exception('Could not determine table type')

        original_filters = warnings.filters[:]

        if verbose:
            warnings.simplefilter("always")
        else:
            warnings.simplefilter("ignore")

        try:

            if table_type in atpy._set_writers:
                atpy._set_writers[table_type](self, *args, **kwargs)
            else:
                raise Exception("Unknown table type: " + table_type)

        finally:
            warnings.filters = original_filters

        return

    def __getitem__(self, item):
        return self.tables[item]

    def __getattr__(self, attribute):

        for table in self.tables:
            if attribute == self.tables[table].table_name:
                return self.tables[table]

        raise AttributeError(attribute)

    def append(self, table):
        '''
        Append a table to the table set

        Required Arguments:

            *table*: [ a table instance ]
                This can be a table of any type, which will be converted
                to a table of the same type as the parent set (e.g. adding
                a single VOTable to a FITSTableSet will convert the VOTable
                to a FITSTable inside the set)
        '''

        table_key = table.table_name

        if table_key in self.tables:
            for i in range(1, 10001):
                if not "%s.%05i" % (table_key, i) in self.tables:
                    table_key = "%s.%05i" % (table_key, i)
                    warnings.warn("There is already a table named %s in the TableSet. Renaming to %s" % (table.table_name, table_key))
                    break
        elif table_key is None:
            for i in range(1, 10001):
                if not "Untitled.%05i" % i in self.tables:
                    table_key = "Untitled.%05i" % i
                    warnings.warn("Table has no name. Setting to %s" % table_key)
                    break

        self.tables[table_key] = table
        return

    def describe(self):
        '''
        Describe all the tables in the set
        '''
        for table in self.tables:
            table.describe()
        return

    def add_comment(self, comment):
        '''
        Add a comment to the table set

        Required Argument:

            *comment*: [ string ]
                The comment to add to the table
        '''

        self.comments.append(comment.strip())
        return

    def add_keyword(self, key, value):
        '''
        Add a keyword/value pair to the table set

        Required Arguments:

            *key*: [ string ]
                The name of the keyword

            *value*: [ string | float | integer | bool ]
                The value of the keyword
        '''

        if type(value) == str:
            value = value.strip()
        self.keywords[key.strip()] = value
        return
