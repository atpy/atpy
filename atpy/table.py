from fitstable import FITSTable
from sqltable_dbapi import SQLTable2
from votable import VOTable
from ipactable import IPACTable

class Table(FITSTable,SQLTable2,VOTable,IPACTable):
    
    read       = None
    write      = None
    FITS_read  = FITSTable.read
    FITS_write = FITSTable.write
    SQL_read   = SQLTable2.read
    SQL_write  = SQLTable2.write
    VO_read    = VOTable.read
    VO_write   = VOTable.write
    IPAC_read  = IPACTable.read
    IPAC_write = IPACTable.write
