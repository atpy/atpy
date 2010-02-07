import os
from distutils import version
import numpy as np

from exceptions import TableException

import atpy

pyfits_minimum_version = version.LooseVersion('2.1')

try:
    import pyfits
    if version.LooseVersion(pyfits.__version__) < pyfits_minimum_version:
        raise
    pyfits_installed = True
except:
    pyfits_installed = False


def _check_pyfits_installed():
    if not pyfits_installed:
        raise Exception("Cannot read/write FITS files - pyfits " + \
            pyfits_minimum_version.vstring + " or later required")

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
    hdulist = pyfits.open(filename)
    tables = {}
    for i, hdu in enumerate(hdulist[1:]):
        if hdu.header['XTENSION'] == 'BINTABLE' or \
            hdu.header['XTENSION'] == 'ASCIITABLE':
            tables[i + 1] = hdu.name
    return tables


def read(self, filename, hdu=None, verbose=True):
    '''
    Read a table from a FITS file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to read the table from

    Optional Keyword Arguments:

        *hdu*: [ integer ]
            The HDU to read from the FITS file (this is only required
            if there are more than one table in the FITS file)
    '''

    _check_pyfits_installed()

    self.reset()

    # If no hdu is requested, check that there is only one table
    if not hdu:
        tables = _list_tables(filename)
        if len(tables) == 1:
            hdu = tables.keys()[0]
        else:
            raise TableException(tables, 'hdu')

    hdu = pyfits.open(filename)[hdu]

    table = hdu.data
    header = hdu.header
    columns = hdu.columns

    for i, name in enumerate(columns.names):

        format, bzero = hdu.columns[i].format[-1], hdu.columns[i].bzero

        if bzero and format in ['B', 'I', 'J']:
            data = pyfits.rec.recarray.field(hdu.data, i)
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

        # pyfits uses chararrays - need to make sure we are using normal
        # numpy arrays
        # data = np.array(data)

        if self._masked:
            self.add_column(name, data, unit=columns.units[i], \
                mask=data==columns.nulls[i])
        else:
            self.add_column(name, data, unit=columns.units[i], \
                null=columns.nulls[i])

    for key in header.keys():
        if not key[:4] in ['TFOR', 'TDIS', 'TDIM', 'TTYP', 'TUNI'] and \
            not key in standard_keys:
            self.add_keyword(key, header[key])

    for comment in header.get_comment():
        self.add_comment(comment)

    if hdu.name:
        self.table_name = hdu.name


def _to_hdu(self):
    '''
    Return the current table as a pyfits HDU object
    '''

    columns = []

    for name in self.names:

        if self._masked:
            data = self.data[name].filled()
            null = self.data[name].fill_value
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

        if dtype.type == np.string_:
            elemwidth = dtype.itemsize

        if dtype.type in type_dict:
            if elemwidth:
                format = str(elemwidth) + type_dict[dtype.type]
            else:
                format = type_dict[dtype.type]
        else:
            raise Exception("cannot use numpy type " + str(dtype.type))

        if dtype.type == np.uint16:
            bzero = - np.iinfo(np.int16).min
        elif dtype.type == np.uint32:
            bzero = - np.iinfo(np.int32).min
        elif dtype.type == np.uint64:
            raise Exception("uint64 unsupported")
        elif dtype.type == np.int8:
            bzero = -128
        else:
            bzero = None

        columns.append(pyfits.Column(name=name, format=format, unit=unit, \
            null=null, array=data, bzero=bzero))

    hdu = pyfits.new_table(pyfits.ColDefs(columns))
    hdu.name = self.table_name

    for key in self.keywords:
        if len(key) > 8:
            keyname = "hierarch " + key
        else:
            keyname = key
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

    _check_pyfits_installed()

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    try:
        _to_hdu(self).writeto(filename)
    except:
        _to_hdu(self).writeto(filename, output_verify='silentfix')


def read_set(self, filename, verbose=True):
    '''
    Read all tables from a FITS file

    Required Arguments:

        *filename*: [ string ]
            The FITS file to read the tables from
    '''

    _check_pyfits_installed()

    self.tables = []

    # Read in primary header
    header = pyfits.getheader(filename, 0)

    for key in header.keys():
        if not key[:4] in ['TFOR', 'TDIS', 'TDIM', 'TTYP', 'TUNI'] and \
            not key in standard_keys:
            self.add_keyword(key, header[key])

    for comment in header.get_comment():
        self.add_comment(comment)

    # Read in tables one by one
    for hdu in _list_tables(filename):
        table = atpy.Table()
        read(table, filename, hdu=hdu, verbose=verbose)
        self.tables.append(table)


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

    _check_pyfits_installed()

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    primary = pyfits.PrimaryHDU()
    for key in self.keywords:
        if len(key) > 8:
            keyname = "hierarch " + key
        else:
            keyname = key
        primary.header.update(keyname, self.keywords[key])

    for comment in self.comments:
        primary.header.add_comment(comment)

    hdulist = [primary]
    for i, table in enumerate(self.tables):
        hdulist.append(_to_hdu())
    hdulist = pyfits.HDUList(hdulist)
    hdulist.writeto(filename)
