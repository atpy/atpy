import os

from exceptions import TableException

import atpy

from decorators import auto_download_to_file, auto_decompress_to_fileobj, auto_fileobj_to_file


try:
    import h5py
    h5py_installed = True
except:
    h5py_installed = False


def _check_h5py_installed():
    if not h5py_installed:
        raise Exception("Cannot read/write HDF5 files - h5py required")


def _get_group(filename, group="", append=False):

    if append:
        f = h5py.File(filename, 'a')
    else:
        f = h5py.File(filename, 'w')

    if group:
        if append:
            if group in f.keys():
                g = f[group]
            else:
                g = f.create_group(group)
        else:
            g = f.create_group(group)
    else:
        g = f

    return f, g


def _create_required_groups(g, path):
    '''
    Given a file or group handle, and a path, make sure that the specified
    path exists and create if necessary.
    '''
    for dirname in path.split('/'):
        if not dirname in g:
            g = g.create_group(dirname)
        else:
            g = g[dirname]


def _list_tables(file_handle):
    list_of_names = []
    file_handle.visit(list_of_names.append)
    tables = {}
    for item in list_of_names:
        if isinstance(file_handle[item], h5py.highlevel.Dataset):
            if file_handle[item].dtype.names:
                tables[item] = item
    return tables


@auto_download_to_file
@auto_decompress_to_fileobj
@auto_fileobj_to_file
def read(self, filename, table=None, verbose=True):
    '''
    Read a table from an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to read the table from

          OR

        *file or group handle*: [ h5py.highlevel.File | h5py.highlevel.Group ]
            The HDF5 file handle or group handle to read the table from

    Optional Keyword Arguments:

        *table*: [ string ]
            The name of the table to read from the HDF5 file (this is only
            required if there are more than one table in the file)
    '''

    _check_h5py_installed()

    self.reset()

    if isinstance(filename, h5py.highlevel.File) or isinstance(filename, h5py.highlevel.Group):
        f, g = None, filename
    else:
        if not os.path.exists(filename):
            raise Exception("File not found: %s" % filename)
        f = h5py.File(filename, 'r')
        g = f['/']

    # If no table is requested, check that there is only one table
    if table is None:
        tables = _list_tables(g)
        if len(tables) == 1:
            table = tables.keys()[0]
        else:
            raise TableException(tables, 'table')

    # Set the table name
    self.table_name = str(table)

    self._setup_table(len(g[table]), g[table].dtype)

    # Add columns to table
    for name in g[table].dtype.names:
        self.data[name][:] = g[table][name][:]

    for attribute in g[table].attrs:
        self.add_keyword(attribute, g[table].attrs[attribute])

    if f is not None:
        f.close()


@auto_download_to_file
@auto_decompress_to_fileobj
@auto_fileobj_to_file
def read_set(self, filename, pedantic=False, verbose=True):
    '''
    Read all tables from an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to read the tables from
    '''

    _check_h5py_installed()

    self.reset()

    if isinstance(filename, h5py.highlevel.File) or isinstance(filename, h5py.highlevel.Group):
        f, g = None, filename
    else:
        if not os.path.exists(filename):
            raise Exception("File not found: %s" % filename)
        f = h5py.File(filename, 'r')
        g = f['/']

    for keyword in g.attrs:
        self.keywords[keyword] = g.attrs[keyword]

    for table in _list_tables(g):
        t = atpy.Table()
        read(t, filename, table=table, verbose=verbose)
        self.append(t)

    if f is not None:
        f.close()

def write(self, filename, compression=False, group="", append=False,
          overwrite=False, ignore_groups=False):
    '''
    Write the table to an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to write the table to

          OR

        *file or group handle*: [ h5py.highlevel.File | h5py.highlevel.Group ]
            The HDF5 file handle or group handle to write the table to

    Optional Keyword Arguments:

        *compression*: [ True | False ]
            Whether to compress the table inside the HDF5 file

        *group*: [ string ]
            The group to write the table to inside the HDF5 file

        *append*: [ True | False ]
            Whether to append the table to an existing HDF5 file

        *overwrite*: [ True | False ]
            Whether to overwrite any existing file without warning

        *ignore_groups*: [ True | False ]
            With this option set to True, groups are removed from table names.
            With this option set to False, tables are placed in groups that
            are present in the table name, and the groups are created if
            necessary.
    '''

    _check_h5py_installed()

    if isinstance(filename, h5py.highlevel.File) or isinstance(filename, h5py.highlevel.Group):
        f, g = None, filename
        if group:
            if group in g:
                g = g[group]
            else:
                g = g.create_group(group)
    else:
        if os.path.exists(filename) and not append:
            if overwrite:
                os.remove(filename)
            else:
                raise Exception("File exists: %s" % filename)

        f, g = _get_group(filename, group=group, append=append)

    if self.table_name:
        name = self.table_name
    else:
        name = "Table"

    if ignore_groups:
        name = os.path.basename(name)
    else:
        path = os.path.dirname(name)
        if path:
            _create_required_groups(g, path)

    if name in g.keys():
        raise Exception("Table %s/%s already exists" % (group, name))

    dset = g.create_dataset(name, data=self.data, compression=compression)

    for keyword in self.keywords:
        dset.attrs[keyword] = self.keywords[keyword]

    if f is not None:
        f.close()


def write_set(self, filename, compression=False, group="", append=False,
              overwrite=False, ignore_groups=False, **kwargs):
    '''
    Write the tables to an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to write the tables to

          OR

        *file or group handle*: [ h5py.highlevel.File | h5py.highlevel.Group ]
            The HDF5 file handle or group handle to write the tables to

    Optional Keyword Arguments:

        *compression*: [ True | False ]
            Whether to compress the tables inside the HDF5 file

        *group*: [ string ]
            The group to write the table to inside the HDF5 file

        *append*: [ True | False ]
            Whether to append the tables to an existing HDF5 file

        *overwrite*: [ True | False ]
            Whether to overwrite any existing file without warning

        *ignore_groups*: [ True | False ]
            With this option set to True, groups are removed from table names.
            With this option set to False, tables are placed in groups that
            are present in the table name, and the groups are created if
            necessary.
    '''

    _check_h5py_installed()

    if isinstance(filename, h5py.highlevel.File) or isinstance(filename, h5py.highlevel.Group):
        f, g = None, filename
        if group:
            if group in g:
                g = g[group]
            else:
                g = g.create_group(group)
    else:
        if os.path.exists(filename) and not append:
            if overwrite:
                os.remove(filename)
            else:
                raise Exception("File exists: %s" % filename)

        f, g = _get_group(filename, group=group, append=append)

    for keyword in self.keywords:
        g.attrs[keyword] = self.keywords[keyword]

    for i, table_key in enumerate(self.tables):

        if self.tables[table_key].table_name:
            name = self.tables[table_key].table_name
        else:
            name = "Table_%02i" % i

        if ignore_groups:
            name = os.path.basename(name)
        else:
            path = os.path.dirname(name)
            if path:
                _create_required_groups(g, path)

        if name in g.keys():
            raise Exception("Table %s/%s already exists" % (group, name))

        dset = g.create_dataset(name, data=self.tables[table_key].data, compression=compression)

        for keyword in self.tables[table_key].keywords:
            dset.attrs[keyword] = self.tables[table_key].keywords[keyword]

    if f is not None:
        f.close()
