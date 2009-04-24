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
    
    def read(self,filename,echo=False,hdu=None):
    
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
            
    def hdu(self):

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
        
    def write(self,filename,clobber=False):        
        self.hdu().writeto(filename,clobber=clobber)
        
class FITSTableSet(BaseTableSet):
    """ A class for reading and writing a set of FITS tables."""

    def __init__(self,tables=None):

        self.tables = []

        if tables:
            if type(tables) == list:
                self.tables = tables
            elif isinstance(tables,BaseTableSet):
                for table in tables.tables:
                    self.tables.append(FITSTable(table))
            else:
                raise Exception("Unknown type: "+type(tables))

    def read(self,filename):
        hdus = _list_tables(filename)
        self.tables = []
        for hdu in hdus:
            t = FITSTable()
            t.read(filename,hdu=hdu)
            self.tables.append(t)

    def write(self,filename,clobber=False):
        hdulist = [pyfits.PrimaryHDU()]
        for i,table in enumerate(self.tables):
            hdulist.append(table.hdu())
        hdulist = pyfits.HDUList(hdulist)
        hdulist.writeto(filename,clobber=clobber)
