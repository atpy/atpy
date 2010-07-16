import os
import numpy as np

from exceptions import TableException

import atpy


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


def _list_tables(filename):
    f = h5py.File(filename)
    list_of_names = []
    f.visit(list_of_names.append)
    tables = {}
    for item in list_of_names:
        if isinstance(f[item], h5py.highlevel.Dataset):
            if f[item].dtype.names:
                tables[item] = item
    return tables


def read(self, filename, table=None, verbose=True):
    '''
    Read a table from an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to read the table from

    Optional Keyword Arguments:

        *table*: [ string ]
            The name of the table to read from the HDF5 file (this is only
            required if there are more than one table in the file)
    '''

    _check_h5py_installed()

    self.reset()

    # If no table is requested, check that there is only one table
    if table is None:
        tables = _list_tables(filename)
        if len(tables) == 1:
            table = tables.keys()[0]
        else:
            raise TableException(tables, 'table')

    # Set the table name
    self.table_name = table

    # Open HDF5 file
    f = h5py.File(filename)

    # Convert table to numpy array
    table = np.array(f[table])

    # Add columns to table
    for name in table.dtype.names:
        self.add_column(name, table[name])


def read_set(self, filename, pedantic=False, verbose=True):
    '''
    Read all tables from an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to read the tables from
    '''

    _check_h5py_installed()

    self.tables = []

    for table in _list_tables(filename):
        t = atpy.Table()
        read(t, filename, table=table, verbose=verbose)
        self.tables.append(t)


def write(self, filename, compression=False, group="", append=False,
          overwrite=False):
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
    '''

    _check_h5py_installed()

    if isinstance(filename, h5py.highlevel.File) or isinstance(filename, h5py.highlevel.Group):
        f, g = None, filename
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

    if name in g.keys():
        raise Exception("Table %s/%s already exists" % (group, name))

    dset = g.create_dataset(name, data=self.data, compression=compression)

    for keyword in self.keywords:
        dset.attrs[keyword] = self.keywords[keyword]

    if f:
        f.close()


def write_set(self, filename, compression=False, group="", append=False,
              overwrite=False, **kwargs):
    '''
    Write the tables to an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to write the tables to

    Optional Keyword Arguments:

        *compression*: [ True | False ]
            Whether to compress the tables inside the HDF5 file

        *group*: [ string ]
            The group to write the table to inside the HDF5 file

        *append*: [ True | False ]
            Whether to append the tables to an existing HDF5 file

        *overwrite*: [ True | False ]
            Whether to overwrite any existing file without warning
    '''

    _check_h5py_installed()

    if os.path.exists(filename) and not append:
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    f, g = _get_group(filename, group=group, append=append)

    for keyword in self.keywords:
        g.attrs[keyword] = self.keywords[keyword]

    for i, table in enumerate(self.tables):

        if table.table_name:
            name = table.table_name
        else:
            name = "Table_%02i" % i

        if name in g.keys():
            raise Exception("Table %s/%s already exists" % (group, name))

        dset = g.create_dataset(name, data=table.data, compression=compression)

        for keyword in table.keywords:
            dset.attrs[keyword] = table.keywords[keyword]

    f.close()
