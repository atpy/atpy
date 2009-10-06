import numpy as np
from copy import copy
import string

from fitstable import FITSMethods, FITSSetMethods
from sqltable import SQLMethods, SQLSetMethods
from votable import VOMethods, VOSetMethods
from ipactable import IPACMethods
from autotable import AutoMethods

from exceptions import VectorException

default_format = {}
default_format[None.__class__] = 16, '.9e'
default_format[np.bool_] = 5, 's'
default_format[np.int16] = 5, 'i'
default_format[np.int32] = 10, 'i'
default_format[np.int64] = 20, 'i'
default_format[np.float32] = 11, '.4e'
default_format[np.float64] = 16, '.9e'
default_format[np.str] = 0, 's'
default_format[np.string_] = 0, 's'
default_format[np.uint8] = 0, 's'
default_format[str] = 0, 's'
default_format[np.unicode_] = 0, 's'
default_format[np.object_] = 10, 's'


class Table(FITSMethods, IPACMethods, SQLMethods, VOMethods, AutoMethods):

    def __init__(self, *args, **kwargs):
        '''
        Create a table instance

        Optional Arguments:

            If no arguments are given, and empty table is created

            If one or more arguments are given they are passed to the
            Table.read() method.
        '''

        self.reset()

        if 'name' in kwargs:
            self.table_name = kwargs.pop('name')
        else:
            self.table_name = None

        if len(args) + len(kwargs) > 0:
            self.read(*args, **kwargs)

        self._update_shape()

        return

    def __getattr__(self, attribute):

        if attribute in self.names:
            return self.data[attribute]
        else:
            raise AttributeError(attribute)

    def __len__(self):
        if len(self.names) == 0:
            return 0
        else:
            return len(self.data[self.names[0]])

    def reset(self):
        '''
        Empty the table
        '''
        self.names = []
        self.types = {}
        self.data = {}
        self.units = {}
        self.descriptions = {}
        self.nulls = {}
        self.formats = {}
        self.keywords = {}
        self.comments = []
        return

    def _raise_vector_columns(self):
        names = []
        for name in self.data:
            column = self.data[name]
            if column.ndim > 1:
                names.append(name)
        if names:
            names = string.join(names, ", ")
            raise VectorException(names)
        return

    def add_column(self, name, data, unit='', null='', description='', \
        format=None, dtype=None):
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
        '''

        self.names.append(name)
        self.data[name] = np.array(data, dtype=dtype)
        self.types[name] = self.data[name].dtype.type
        self.units[name] = unit
        self.descriptions[name] = description
        self.nulls[name] = null

        column_type = data.dtype.type

        if format:
            self.formats[name] = format
        else:
            self.formats[name] = default_format[column_type]

        if self.formats[name][1] == 's':
            self.formats[name] = self.data[name].itemsize, 's'

        self._update_shape()
        return

    def remove_column(self, remove_name):
        '''
        Remove a column from the table

        Required Argument:

            *remove_name*: [ string ]
                The name of the column to remove
        '''

        try:

            colnum = self.names.index(remove_name)
            self.names.pop(colnum)

            self.data.pop(remove_name)
            self.units.pop(remove_name)
            self.types.pop(remove_name)
            self.nulls.pop(remove_name)
            self.descriptions.pop(remove_name)

        except ValueError, KeyError:

            raise Exception("Column " + remove_name + " does not exist")

        self._update_shape()
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

        for name in remove_names:
            self.remove_column(name)

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

        for i, name in enumerate(self.names):
            if name == old_name:
                self.names[i] = new_name

                self.data[new_name] = self.data[old_name]
                del self.data[old_name]

                self.units[new_name] = self.units[old_name]
                del self.units[old_name]

                self.descriptions[new_name] = self.descriptions[old_name]
                del self.descriptions[old_name]

                self.nulls[new_name] = self.nulls[old_name]
                del self.nulls[old_name]

                self.formats[new_name] = self.formats[old_name]
                del self.formats[old_name]

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
            len_unit_max = max(len(str(self.units[name])), len_unit_max)
            len_datatype_max = max(len(str(self.types[name])), \
                len_datatype_max)
            len_formats_max = max(len(self.format(name)), len_formats_max)

        # Print out table

        format = "| %" + str(len_name_max) + \
            "s | %" + str(len_unit_max) + \
            "s | %" + str(len_datatype_max) + \
            "s | %" + str(len_formats_max) + "s |"

        len_tot = len_name_max + len_unit_max + len_datatype_max + \
            len_formats_max + 13

        print "-"*len_tot
        print format % ("Name", "Unit", "Type", "Format")
        print "-"*len_tot

        for name in self.names:
            print format % (name, str(self.units[name]), \
                str(self.types[name]), self.format(name))

        print "-"*len_tot

        return

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

        row = []
        if not python_types:
            for name in self.names:
                row.append(self.data[name][row_number])
        else:
            for name in self.names:
                if np.isnan(self.data[name][row_number]):
                    elem = None
                elif self.types[name] in [np.float32, np.float64]:
                    elem = float(self.data[name][row_number])
                elif self.types[name] in [np.int16, np.int32, np.int64]:
                    elem = int(self.data[name][row_number])
                elif self.types[name] in [np.string_, np.str]:
                    elem = str(self.data[name][row_number])
                row.append(elem)
        return tuple(row)

    def where(self, mask):
        '''
        Select certain rows from the table and return a new table instance

        Required Argument:

            *mask*: [ np.bool array ]
                A boolean array with the same length as the table.

        Returns:

            A new table instance, containing only the rows selected
        '''

        new_table = self.__class__()

        new_table.table_name = copy(self.table_name)
        new_table.names = copy(self.names)
        new_table.types = copy(self.types)
        new_table.array = copy(self.data)
        new_table.units = copy(self.units)
        new_table.descriptions = copy(self.descriptions)
        new_table.keywords = copy(self.keywords)
        new_table.comments = copy(self.comments)
        new_table.nulls = copy(self.nulls)
        new_table.formats = copy(self.formats)

        for name in new_table.names:
            new_table.data[name] = self.data[name][mask]

        new_table._update_shape()

        return new_table

    def _update_shape(self):
        n_rows = self.__len__()
        n_cols = len(self.names)
        self.shape = (n_rows, n_cols)

        return

    def format(self, name):
        '''
        Return the ASCII format of a given column

        Required Arguments:

            *name*: [ string ]
                The column name
        '''
        return str(self.formats[name][0]) + self.formats[name][1]

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


class TableSet(FITSSetMethods, SQLSetMethods, VOSetMethods, AutoMethods):

    _single_table_class = Table

    def __init__(self, *args, **kwargs):
        '''
        Create a table set instance

        Optional Arguments:

            If no arguments are given, an empty table set will be created.

            If one of the arguments is a list or a Table instance, then only
            this argument will be used.

            If one or more arguments are present, they are passed to the read
            method

        '''

        self.tables = []

        if len(args) == 1:

            arg = args[0]

            if type(arg) == list:
                for table in arg:
                    self.tables.append(table)
                    return

            elif isinstance(arg, TableSet):
                for table in arg.tables:
                    self.tables.append(table)
                    return

        # Pass arguments to read
        self.read(*args, **kwargs)

        return

    def __getattr__(self, attribute):

        for table in self.tables:
            if attribute == table.table_name:
                return table

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
        self.tables.append(table)
        return

    def describe(self):
        '''
        Describe all the tables in the set
        '''
        for table in self.tables:
            table.describe()
        return
