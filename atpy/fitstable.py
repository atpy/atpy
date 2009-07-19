import numpy as np
import pkg_resources

pyfits_minimum_version = "2.1"

try:
    pkg_resources.require('pyfits>='+pyfits_minimum_version)
    import pyfits
    pyfits_installed = True
except:
    print "WARNING - pyfits "+pyfits_minimum_version+" or later required"
    print "          FITS table reading/writing has been disabled"
    pyfits_installed = False

def _check_pyfits_installed():
    if not pyfits_installed:
        raise Exception("Cannot read/write FITS files - pyfits "+pyfits_minimum_version+" or later required")

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

class FITSMethods(object):
    ''' A class for reading and writing a single FITS table.'''
    
    def fits_read(self,filename,hdu=None):
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
        columns = hdu.columns
                        
        for i,name in enumerate(columns.names):
            self.add_column(name,table.field(name),unit=columns.units[i],null=columns.nulls[i])
        
        for key in header.keys():
            if not key[:4] in ['TFOR','TDIS','TDIM','TTYP','TUNI'] and not key in standard_keys:
                self.add_keyword(key,header[key])
        
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
            
            array = self.data[name]
            unit = self.units[name]
            null = self.nulls[name]
            
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
            
            columns.append(pyfits.Column(name=name,format=format,unit=unit,null=null,array=array))
        
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
    
    def fits_write(self,filename,overwrite=False):
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
        
        self._to_hdu().writeto(filename,clobber=overwrite)

class FITSSetMethods(object):
    ''' A class for reading and writing a set of FITS tables.'''
    
    def fits_read(self,filename):
        '''
        Read all tables from a FITS file
        
        Required Arguments:
            
            *filename*: [ string ]
                The FITS file to read the tables from
        '''
        
        _check_pyfits_installed()
        
        self.tables = []
        
        for hdu in _list_tables(filename):
            table = self._single_table_class()
            table.fits_read(filename,hdu=hdu)
            self.tables.append(table)
    
    def fits_write(self,filename,overwrite=False):
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
        
        hdulist = [pyfits.PrimaryHDU()]
        for i,table in enumerate(self.tables):
            hdulist.append(table._to_hdu())
        hdulist = pyfits.HDUList(hdulist)
        hdulist.writeto(filename,clobber=overwrite)
