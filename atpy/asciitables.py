import os
from decorators import auto_download_to_file, auto_decompress_to_fileobj

# Thanks to Moritz Guenther for providing the initial code used to create this file

try:
    import asciitable
    asciitable_installed = True
except:
    asciitable_installed = False


def _check_asciitable_installed():
    if not asciitable_installed:
        raise Exception("Cannot read data with asciitable - no version of asciitable is found")


def read_cds(self, filename, **kwargs):
    '''
    Read data from a CDS table (also called Machine Readable Tables) file

        Required Arguments:

            *filename*: [ string ]
                The file to read the table from

        Keyword Arguments are passed to asciitable
    '''
    read_ascii(self, filename, Reader=asciitable.CdsReader, **kwargs)


def read_daophot(self, filename, **kwargs):
    '''
    Read data from a DAOphot table

        Required Arguments:

            *filename*: [ string ]
                The file to read the table from

        Keyword Arguments are passed to asciitable
    '''
    read_ascii(self, filename, Reader=asciitable.DaophotReader, **kwargs)


def read_rdb(self, filename, **kwargs):
    '''
    Read data from an RDB table

        Required Arguments:

            *filename*: [ string ]
                The file to read the table from

        Keyword Arguments are passed to asciitable
    '''
    read_ascii(self, filename, Reader=asciitable.RdbReader, **kwargs)


def write_rdb(self, filename, **kwargs):
    '''
    Write data to an RDB table

        Required Arguments:

            *filename*: [ string ]
                The file to write the table to

        Keyword Arguments are passed to asciitable
    '''
    write_ascii(self, filename, Writer=asciitable.Rdb, **kwargs)


# asciitable can handle file objects
@auto_download_to_file
@auto_decompress_to_fileobj
def read_ascii(self, filename, **kwargs):
    '''
    Read a table from an ASCII file using asciitable

    Optional Keyword Arguments:

        Reader - Reader class (default= BasicReader )
        Inputter - Inputter class
        delimiter - column delimiter string
        comment - regular expression defining a comment line in table
        quotechar - one-character string to quote fields containing special characters
        header_start - line index for the header line not counting comment lines
        data_start - line index for the start of data not counting comment lines
        data_end - line index for the end of data (can be negative to count from end)
        converters - dict of converters
        data_Splitter - Splitter class to split data columns
        header_Splitter - Splitter class to split header columns
        names - list of names corresponding to each data column
        include_names - list of names to include in output (default=None selects all names)
        exclude_names - list of names to exlude from output (applied after include_names)

    Note that the Outputter and numpy arguments are not passed to asciitable.

    See the asciitable documentation at http://cxc.harvard.edu/contrib/asciitable/ for more details.
    '''

    _check_asciitable_installed()

    self.reset()

    kwargs['numpy'] = True
    if 'Outputter' in kwargs:
        kwargs.pop('Outputter')
    table = asciitable.read(filename, **kwargs)

    for name in table.dtype.names:
        self.add_column(name, table[name])


def write_ascii(self, filename, **kwargs):
    '''
    Read a table from an ASCII file using asciitable

    Optional Keyword Arguments:

        Writer - Writer class (default= Basic)
        delimiter - column delimiter string
        write_comment - string defining a comment line in table
        quotechar - one-character string to quote fields containing special characters
        formats - dict of format specifiers or formatting functions
        names - list of names corresponding to each data column
        include_names - list of names to include in output (default=None selects all names)
        exclude_names - list of names to exlude from output (applied after include_names)

    See the asciitable documentation at http://cxc.harvard.edu/contrib/asciitable/ for more details.
    '''

    _check_asciitable_installed()

    if 'overwrite' in kwargs:
        overwrite = kwargs.pop('overwrite')
    else:
        overwrite = False

    if type(filename) is str and os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    asciitable.write(self.data, filename, **kwargs)
