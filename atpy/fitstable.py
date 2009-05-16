import numpy as np
import pyfits

from basetable import BaseTable, BaseTableSet

standard_keys = ['XTENSION','NAXIS','NAXIS1','NAXIS2','TFIELDS','PCOUNT','GCOUNT','BITPIX']

# Define type conversion dictionary
type_dict = {}
type_dict[np.uint8] = "B"
type_dict[np.int16] = "I"
type_dict[np.int32] = "J"
type_dict[np.int64] = "K"
type_dict[np.float32] = "E"
type_dict[np.float64] = "D"
type_dict[np.str] = "A"
type_dict[np.string_] = "A"
type_dict[str] = "A"

def _list_tables(filename):
    hdulist = pyfits.open(filename)
    tables = {}
    for i,hdu in enumerate(hdulist[1:]):
        if hdu.header['XTENSION'] == 'BINTABLE' or hdu.header['XTENSION'] == 'ASCIITABLE':
            tables[i+1] = hdu.name
    return tables

class FITSTable(BaseTable):
    """ A class for reading and writing a single FITS table."""
    
    def read(self,filename,hdu=None):
        '''
        Read a table from a FITS file
        
        Required Arguments:
            
            *filename*: [ string ]
                The file to read the FITS table from
        
        Optional Keyword Arguments:
            
            *hdu*: [ integer ]
                The HDU to read the FITS table from (this is only required
                if there are more than one tables in the FITS file)
        '''
        
        self.reset()
        
        # If no hdu is requested, check that there is only one table
        if not hdu:
            tables = _list_tables(filename)
            if len(tables) == 1:
                hdu = tables.keys()[0]
            else:
                print "-"*56
                print " There is more than one table in the requested file"
                print " Please specify the HDU desired with the hdu= argument"
                print " The available tables are:"
                print ""
                for table in tables:
                    print " hdu=%i : %s" % (table,tables[table])
                print "-"*56
                return
        
        hdu = pyfits.open(filename)[hdu]
        
        table = hdu.data
        header = hdu.header
        cols = hdu.columns.names
        
        for name in cols:
            self.add_column((name,table.field(name)))
        
        for key in header.keys():
            if not key[:4] in ['TFOR','TDIS','TDIM','TTYP','TUNI'] and not key in standard_keys:
                self.add_keyword(key,header[key])
        
        for comment in header.get_comment():
            self.add_comment(comment)
        
        self.table_name = hdu.name
    
    def _hdu(self):
        '''
        Return the current table as a pyfits HDU object
        '''
        
        columns = []
        
        for name in self.names:
            
            array = self.array[name]
            unit = self.units[name]
            
            if unit == None: unit = ''
            
            elemtype,elemwidth = type(array[0]),1
            
            if elemtype == np.ndarray:
                elemtype,elemwidth = type(array[0][0]),len(array[0])
            
            if elemtype in [np.str,np.string_,str]:
                elemwidth = array.itemsize
            
            if type_dict.has_key(elemtype):
                format = str(elemwidth) + type_dict[elemtype]
            else:
                raise Exception("cannot use numpy type "+str(elemtype))
            
            columns.append(pyfits.Column(name=name,format=format,unit=unit,array=array))
        
        hdu = pyfits.new_table(pyfits.ColDefs(columns))
        hdu.name = self.table_name
        
        for key in self.keywords:
            if len(key) > 8:
                keyname = "hierarch "+key
            else:
                keyname = key
            hdu.header.update(keyname,self.keywords[key])
        
        for comment in self.comments:
            hdu.header.add_comment(comment)
        
        return hdu
    
    def write(self,filename,overwrite=False):
        '''
        Write the table to a FITS file
        
        Required Arguments:
            
            *filename*: [ string ]
                The file to write the FITS table to
        
        Optional Keyword Arguments:
            
            *overwrite*: [ True | False ]
                Whether to overwrite any existing file without warning
        '''
        
        self._hdu().writeto(filename,clobber=overwrite)

class FITSTableSet(BaseTableSet):
    """ A class for reading and writing a set of FITS tables."""
    
    def __init__(self,*args):
        '''
        Create a FITS table set
        
        This can be called in three different ways:
        
        FITSTableSet(): creates an empty instance of a FITS table set
        
        FITSTableSet(list): where list is a list of individual tables
        (which can have inhomogeneous types)
        
        FITSTableSet(tableset): where tableset can be a table set of any type
        '''
        
        if len(args) > 1:
            raise Exception("FITSTableSet either takes no or one argument")
        elif len(args) == 1:
            data = args[0]
        else:
            data = None
        
        self.tables = []
        
        if data:
            if type(data) == list:
                for table in data:
                    self.tables.append(FITSTable(table))
            elif isinstance(data,BaseTableSet):
                for table in data.tables:
                    self.tables.append(FITSTable(table))
            else:
                raise Exception("Unknown type: "+type(data))
    
    def read(self,filename):
        '''
        Read all tables from a FITS file
        
        Required Arguments:
            
            *filename*: [ string ]
                The name of the file to read the tables from
        '''
        
        self.tables = []
        
        for hdu in _list_tables(filename):
            table = FITSTable()
            table.read(filename,hdu=hdu)
            self.tables.append(table)
    
    def write(self,filename,overwrite=False):
        '''
        Write the tables to a FITS file
        
        Required Arguments:
            
            *filename*: [ string ]
                The file to write the FITS table to
        
        Optional Keyword Arguments:
            
            *overwrite*: [ True | False ]
                Whether to overwrite any existing file without warning
        '''
        
        hdulist = [pyfits.PrimaryHDU()]
        for i,table in enumerate(self.tables):
            hdulist.append(table._hdu())
        hdulist = pyfits.HDUList(hdulist)
        hdulist.writeto(filename,clobber=overwrite)
