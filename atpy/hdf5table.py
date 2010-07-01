import os


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


def write(self, filename, compression=False, group="", append=False,
          overwrite=False):
    '''
    Write the table to an HDF5 file

    Required Arguments:

        *filename*: [ string ]
            The HDF5 file to write the table to

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
