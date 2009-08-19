from distutils import version
import numpy as np

from exceptions import TableException

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
type_dict[np.uint8] = "int"
type_dict[np.int16] = "int"
type_dict[np.int32] = "int"
type_dict[np.int64] = "int"
type_dict[np.float32] = "float"
type_dict[np.float64] = "double"
type_dict[np.str] = "char"
type_dict[np.string_] = "char"
type_dict[str] = "char"


def _list_tables(filename):
    votable = parse(filename)
    tables = {}
    for i, table in enumerate(votable.iter_tables()):
        tables[i] = table.name
    return tables


class VOMethods(object):
    ''' A class for reading and writing a single VO table.'''

    def vo_read(self, filename, pedantic=False, tid=-1):
        '''
        Read a table from a VOT file

        Required Arguments:

            *filename*: [ string ]
                The VOT file to read the table from

        Optional Keyword Arguments:

            *tid*: [ integer ]
                The ID of the table to read from the VO file (this is
                only required if there are more than one table in the VO file)

            *pendantic*: [ True | False ]
                When *pedantic* is True, raise an error when the file violates
                the VO Table specification, otherwise issue a warning.
        '''

        _check_vo_installed()

        self.reset()

        # If no table is requested, check that there is only one table
        if tid==-1:
            tables = _list_tables(filename)
            if len(tables) == 1:
                tid = 0
            else:
                raise TableException(tables, 'tid')

        votable = parse(filename, pedantic=pedantic)
        for id, table in enumerate(votable.iter_tables()):
            if id==tid:
                break

        if table.ID:
            self.table_name = table.ID
        elif table.name:
            self.table_name = table.name

        for field in table.fields:
            self.add_column(field.name, table.array[field.name], \
                unit=field.unit)

    def _to_table(self, VOTable):
        '''
        Return the current table as a VOT object
        '''

        table = Table(VOTable)

        # Define some fields

        n_rows = len(self.data[self.names[0]])

        fields = []
        for i, name in enumerate(self.names):

            data = self.data[name]
            unit = self.units[name]

            coltype = type(data)

            elemtype = data.dtype.type

            if data.ndim > 1:
                arraysize = str(data.shape[1])
            else:
                arraysize = None

            if elemtype in type_dict:
                datatype = type_dict[elemtype]
            else:
                raise Exception("cannot use numpy type " + str(elemtype))

            if arraysize:
                fields.append(Field(VOTable, ID="col" + str(i), name=name, \
                    datatype=datatype, unit=unit, arraysize=arraysize))
            else:
                fields.append(Field(VOTable, ID="col" + str(i), name=name, \
                    datatype=datatype, unit=unit))

        table.fields.extend(fields)

        table.create_arrays(n_rows)

        # Character columns are stored as object columns in the VOTable
        # instance. Leaving the type as string should work, but causes
        # a segmentation fault on MacOS X with Python 2.6 64-bit so
        # we force the conversion to object type columns.

        for name in self.names:
            if self.data[name].dtype.type in [np.string_, str, np.str]:
                table.array[name] = self.data[name].astype(np.object_)
            else:
                table.array[name] = self.data[name]

        table.name = self.table_name

        return table

    def vo_write(self, filename, votype='ascii'):
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

        VOTable = VOTableFile()
        resource = Resource()
        VOTable.resources.append(resource)

        resource.tables.append(self._to_table(VOTable))

        if votype is 'binary':
            VOTable.get_first_table().format = 'binary'
            VOTable.set_all_tables_format('binary')

        VOTable.to_xml(filename)


class VOSetMethods(object):
    ''' A class for reading and writing a set of VO tables.'''

    def vo_read(self, filename):
        '''
        Read all tables from a VOT file

        Required Arguments:

            *filename*: [ string ]
                The VOT file to read the tables from
        '''

        _check_vo_installed()

        self.tables = []

        for tid in _list_tables(filename):
            t = self._single_table_class()
            t.vo_read(filename, tid=tid)
            self.tables.append(t)

    def vo_write(self, filename, votype='ascii'):
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

        VOTable = VOTableFile()
        resource = Resource()
        VOTable.resources.append(resource)

        for table in self.tables:
            resource.tables.append(table._to_table(VOTable))

        if votype is 'binary':
            VOTable.get_first_table().format = 'binary'
            VOTable.set_all_tables_format('binary')

        VOTable.to_xml(filename)
