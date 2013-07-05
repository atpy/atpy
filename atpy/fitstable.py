from __future__ import print_function, division

import os

import numpy as np
from astropy.io import fits

from .exceptions import TableException
from .helpers import smart_dtype, smart_mask
from .decorators import auto_download_to_file, auto_fileobj_to_file


standard_keys = ['XTENSION', 'NAXIS', 'NAXIS1', 'NAXIS2', 'TFIELDS', \
    'PCOUNT', 'GCOUNT', 'BITPIX', 'EXTNAME']

# Define type conversion dictionary
type_dict = {}
type_dict[np.bool_] = "L"
type_dict[np.int8] = "B"
type_dict[np.uint8] = "B"
type_dict[np.int16] = "I"
type_dict[np.uint16] = "I"
type_dict[np.int32] = "J"
type_dict[np.uint32] = "J"
type_dict[np.int64] = "K"
type_dict[np.uint64] = "K"
type_dict[np.float32] = "E"
type_dict[np.float64] = "D"
type_dict[np.str] = "A"
type_dict[np.string_] = "A"
type_dict[str] = "A"


def _list_tables(filename):
    hdulist = fits.open(filename)
    tables = {}
    for i, hdu in enumerate(hdulist[1:]):
        if hdu.header['XTENSION'] in ['BINTABLE', 'ASCIITABLE', 'TABLE']:
            tables[i + 1] = hdu.name
    hdulist.close()
    return tables


# PyFITS can handle compression, so no decompression detection
@auto_download_to_file
@auto_fileobj_to_file
def read(self, filename, hdu=None, memmap=False, verbose=True):
    '''
    Read a table from a FITS file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to read the table from

    Optional Keyword Arguments:

        *hdu*: [ integer ]
            The HDU to read from the FITS file (this is only required
            if there are more than one table in the FITS file)

        *memmap*: [ bool ]
            Whether PyFITS should use memory mapping
    '''

    self.reset()

    # If no hdu is requested, check that there is only one table
    if not hdu:
        tables = _list_tables(filename)
        if len(tables) == 0:
            raise Exception("No tables in file")
        elif len(tables) == 1:
            hdu = tables.keys()[0]
        else:
            raise TableException(tables, 'hdu')

    hdulist = fits.open(filename, memmap=memmap)
    hdu = hdulist[hdu]

    table = hdu.data
    header = hdu.header
    columns = hdu.columns

    # Construct dtype for table

    dtype = []

    for i in range(len(hdu.data.dtype)):

        name = hdu.data.dtype.names[i]
        type = hdu.data.dtype[name]
        if type.subdtype:
            type, shape = type.subdtype
        else:
            shape = ()

        # Get actual FITS format and zero-point
        format, bzero = hdu.columns[i].format, hdu.columns[i].bzero

        # Remove numbers from format, to find just type
        format = format.strip("1234567890.")

        if type.type is np.string_ and format in ['I', 'F', 'E', 'D']:
            if format == 'I':
                type = np.int64
            elif format in ['F', 'E']:
                type = np.float32
            elif format == 'D':
                type = np.float64

        if format == 'X' and type.type == np.uint8:
            type = np.bool
            if len(shape) == 1:
                shape = (shape[0] * 8,)

        if format == 'L':
            type = np.bool

        if bzero and format in ['B', 'I', 'J']:
            if format == 'B' and bzero == -128:
                dtype.append((name, np.int8, shape))
            elif format == 'I' and bzero == - np.iinfo(np.int16).min:
                dtype.append((name, np.uint16, shape))
            elif format == 'J' and bzero == - np.iinfo(np.int32).min:
                dtype.append((name, np.uint32, shape))
            else:
                dtype.append((name, type, shape))
        else:
            dtype.append((name, type, shape))

    dtype = np.dtype(dtype)

    if self._masked:
        self._setup_table(len(hdu.data), dtype, units=columns.units)
    else:
        self._setup_table(len(hdu.data), dtype, units=columns.units, \
                          nulls=columns.nulls)

    # Populate the table

    for i, name in enumerate(columns.names):

        format, bzero = hdu.columns[i].format[-1], hdu.columns[i].bzero

        if bzero and format in ['B', 'I', 'J']:
            data = np.rec.recarray.field(hdu.data, i)
            if format == 'B' and bzero == -128:
                data = (data.astype(np.int16) + bzero).astype(np.int8)
            elif format == 'I' and bzero == - np.iinfo(np.int16).min:
                data = (data.astype(np.int32) + bzero).astype(np.uint16)
            elif format == 'J' and bzero == - np.iinfo(np.int32).min:
                data = (data.astype(np.int64) + bzero).astype(np.uint32)
            else:
                data = table.field(name)
        else:
            data = table.field(name)

        self.data[name][:] = data[:]

        if self._masked:
            if columns.nulls[i] == 'NAN.0':
                null = np.nan
            elif columns.nulls[i] == 'INF.0':
                null = np.inf
            else:
                null = columns.nulls[i]
            self.data[name].mask = smart_mask(data, null)
            self.data[name].set_fill_value(null)

    for key in header.keys():
        if not key[:4] in ['TFOR', 'TDIS', 'TDIM', 'TTYP', 'TUNI'] and \
            not key in standard_keys:
            self.add_keyword(key, header[key])

    try:
        header['COMMENT']
    except KeyError:
        pass
    else:
        # PyFITS used to define header['COMMENT'] as the last comment read in
        # (which was a string), but now defines it as a _HeaderCommentaryCards
        # object
        if isinstance(header['COMMENT'], basestring):
            for comment in header.get_comment():
                if isinstance(comment, fits.Card):
                    self.add_comment(comment.value)
                else:
                    self.add_comment(comment)
        else:
            for comment in header['COMMENT']:
                if isinstance(comment, fits.Card):
                    self.add_comment(comment.value)
                else:
                    self.add_comment(comment)

    if hdu.name:
        self.table_name = str(hdu.name)

    hdulist.close()

    return


def _to_hdu(self):
    '''
    Return the current table as a astropy.io.fits HDU object
    '''

    columns = []

    for name in self.names:

        if self._masked:
            data = self.data[name].filled()
            null = self.data[name].fill_value
            if data.ndim > 1:
                null = null[0]
            if type(null) in [np.bool_, np.bool]:
                null = bool(null)
        else:
            data = self.data[name]
            null = self.columns[name].null

        unit = self.columns[name].unit
        dtype = self.columns[name].dtype
        elemwidth = None

        if unit == None:
            unit = ''

        if data.ndim > 1:
            elemwidth = str(data.shape[1])

        column_type = smart_dtype(dtype)

        if column_type == np.string_:
            elemwidth = dtype.itemsize

        if column_type in type_dict:
            if elemwidth:
                format = str(elemwidth) + type_dict[column_type]
            else:
                format = type_dict[column_type]
        else:
            raise Exception("cannot use numpy type " + str(column_type))

        if column_type == np.uint16:
            bzero = - np.iinfo(np.int16).min
        elif column_type == np.uint32:
            bzero = - np.iinfo(np.int32).min
        elif column_type == np.uint64:
            raise Exception("uint64 unsupported")
        elif column_type == np.int8:
            bzero = -128
        else:
            bzero = None

        columns.append(fits.Column(name=name, format=format, unit=unit, \
            null=null, array=data, bzero=bzero))

    hdu = fits.new_table(fits.ColDefs(columns))
    hdu.name = self.table_name

    for key in self.keywords:

        if len(key) > 8:
            keyname = "hierarch " + key
        else:
            keyname = key

        try:  # PyFITS 3.x
            hdu.header[keyname] = self.keywords[key]
        except KeyError:  # PyFITS 2.x
            hdu.header.update(keyname, self.keywords[key])

    for comment in self.comments:
        hdu.header.add_comment(comment)

    return hdu


def write(self, filename, overwrite=False):
    '''
    Write the table to a FITS file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to write the table to

    Optional Keyword Arguments:

        *overwrite*: [ True | False ]
            Whether to overwrite any existing file without warning
    '''

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    try:
        _to_hdu(self).writeto(filename)
    except:
        _to_hdu(self).writeto(filename, output_verify='silentfix')


# PyFITS can handle compression, so no decompression detection
@auto_download_to_file
@auto_fileobj_to_file
def read_set(self, filename, memmap=False, verbose=True):
    '''
    Read all tables from a FITS file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to read the tables from

    Optional Keyword Arguments:

        *memmap*: [ bool ]
            Whether PyFITS should use memory mapping
    '''

    self.reset()

    # Read in primary header
    header = fits.getheader(filename, 0)

    for key in header.keys():
        if not key[:4] in ['TFOR', 'TDIS', 'TDIM', 'TTYP', 'TUNI'] and \
            not key in standard_keys:
            self.add_keyword(key, header[key])

    try:
        header['COMMENT']
    except KeyError:
        pass
    else:
        # PyFITS used to define header['COMMENT'] as the last comment read in
        # (which was a string), but now defines it as a _HeaderCommentaryCards
        # object
        if isinstance(header['COMMENT'], basestring):
            for comment in header.get_comment():
                if isinstance(comment, fits.Card):
                    self.add_comment(comment.value)
                else:
                    self.add_comment(comment)
        else:
            for comment in header['COMMENT']:
                if isinstance(comment, fits.Card):
                    self.add_comment(comment.value)
                else:
                    self.add_comment(comment)


    # Read in tables one by one
    from .basetable import Table
    for hdu in _list_tables(filename):
        table = Table()
        read(table, filename, hdu=hdu, memmap=memmap, verbose=verbose)
        self.append(table)


def write_set(self, filename, overwrite=False):
    '''
    Write the tables to a FITS file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to write the tables to

    Optional Keyword Arguments:

        *overwrite*: [ True | False ]
            Whether to overwrite any existing file without warning
    '''

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    primary = fits.PrimaryHDU()
    for key in self.keywords:

        if len(key) > 8:
            keyname = "hierarch " + key
        else:
            keyname = key

        try:  # PyFITS 3.x
            primary.header[keyname] = self.keywords[key]
        except KeyError:  # PyFITS 2.x
            primary.header.update(keyname, self.keywords[key])

    for comment in self.comments:
        primary.header.add_comment(comment)

    hdulist = [primary]
    for table_key in self.tables:
        hdulist.append(_to_hdu(self.tables[table_key]))
    hdulist = fits.HDUList(hdulist)
    hdulist.writeto(filename)
