import decimal
import numpy as np
import sqlalchemy as sql

from basetable import BaseTable, BaseTableSet


# Define type conversion dictionary
type_dict = {}
type_dict[np.uint8] = "Unicode"
type_dict[np.int16] = "Integer"
type_dict[np.int32] = "Integer"
type_dict[np.int64] = "Integer"
type_dict[np.float32] = "Float"
type_dict[np.float64] = "Float"
type_dict[np.str] = "Text"
type_dict[np.string_] = "Text"
type_dict[str] = "Text"

type_dict_out ={}
type_dict_out[np.int16] = sql.Integer()
type_dict_out[np.int32] = sql.Integer()
type_dict_out[np.int64] = sql.Integer()
type_dict_out[np.float32] = sql.Float()
type_dict_out[np.float64] = sql.Float()
type_dict_out[np.str] = sql.String()
type_dict_out[np.string_] = sql.String()
type_dict_out[str] = sql.String()
type_dict_out[np.unicode_] = sql.String()
type_dict_out[None.__class__] = sql.Float()


def _smart_dialect(dbname,dbtype='sqlite',username='',password='',port='',host=''):
    if dbtype is 'sqlite':
        engine = sql.create_engine(dbtype+':///'+dbname)
    """
    elif dbtype is 'postgres':
        
        if port is not '':
            port = ':' + port
            
        engine = sql.create_engine(dbtype+'://'+username+':'+password+'@'+host+port+'/'+dbname)
    
    # elif dbtype is 'mysql':
    """
    return engine

def _list_tables(engine):
    sqltables = np.array(engine.table_names()).astype(np.str)
    tables = {}
    for i,table in enumerate(sqltables):
        tables[i] = table
    return tables

def uni2str(array):
    if type(array) == np.unicode_:
        array = array.astype(np.str)
    else:
        pass
    return array


class SQLTable(BaseTable):
    '''
    Class for working with SQLTable read and write
    '''
    
    def read(self,dbname,tid=-1,dbtype='sqlite',username='',password='',port='',host=''):
        '''
        You can read in an SQL table with this method. 
        
        Example: 
        st = SQLTable(name='Some Table') 
        st.read('a_file_that_you_want_to_read.db')
        
        # Want to convert the data from SQL to VOTable?
        
        vt = VOTable(st)
        vt.write('file_name.xml') # You're done. It's all set!
        '''
        
        def uni2str(array):
            if type(array) == np.unicode_:
                array = array.astype(np.str)
            else:
                pass
            return array
        
        # Erase existing content
        self.reset()
        
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        
        else:
            # print 'The dbtype, '+dbtype+' is not recognized. \nThe available dbtypes in ATpy are \n1) "sqlite" \n2) "postgres" \n3) "mysql"'
            print 'The dbtype, '+dbtype+' is not recognized. \n"sqlite" is the only recognized dbtype at the moment. '
        
        metadata = sql.MetaData(engine)
        
        tbl_names = np.array(engine.table_names()).astype(np.str)
        
        # If no table is requested, check that there is only one table
        if tid==-1:
            tables = _list_tables(engine)
            if len(tables) == 1:
                tid = 0
            else:
                print "-"*56
                print " There is more than one table in the requested file"
                print " Please specify the table desired with the tid= argument"
                print " The available tables are:"
                print ""
                for tid in tables:
                    print " tid=%i : %s" % (tid,tables[tid])
                print "-"*56
                return
        
        metadata = sql.MetaData(engine)
        tbl_names = np.array(engine.table_names()).astype(np.str)
        
        if tid != -1:
            try:
                tbl = sql.Table(tid, metadata, autoload=True)
                self.table_name = tid
            except:
                print 'Table name '+str(tid)+' is not recognized.'
        
        else:
            tbl = sql.Table(tbl_names[tid].encode(), metadata, autoload=True)
            self.table_name = tbl_names[0].encode()
        
        
        results = engine.execute(tbl.select()).fetchall()
        for col in tbl.columns.keys():
            column = []
            for row in results:
                elem = row[col]
                if type(elem)==decimal.Decimal:
                    elem = float(elem)
                column.append(elem)
            self.add_column(str(col),uni2str(np.array(column)))
    
    
    def write(self,dbname,dbtype='sqlite',username='',password='',host=''):
        
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        
        metadata = sql.MetaData()
        tbl = sql.Table(self.table_name, metadata)
        for i, col_name in enumerate(np.array(self.names).astype(str)):
            tbl.columns.add(sql.Column(col_name,
            type_dict_out[type(self.array[col_name][0])]
            ))
        
        metadata.create_all(engine)
        
        sources = []
        
        for i in range(len(self.array[self.names[0].encode()])):
            source = {}
            for col_name in np.array(self.names).astype(str):
                source[col_name] = self.array[col_name][i]
            sources.append(source)
                
        
        # Insert values into database
        conn = engine.connect()
        conn.execute(tbl.insert(),sources)
        conn.close()
    


class SQLTableSet(BaseTableSet):
    
    def _single_table(self,table):
        return SQLTable(table)
    
    def read(self,dbname,dbtype='sqlite',username='',password='',port='',host=''):
        '''
        Read all tables from a SQL file
        
        Required Arguments:
        
            *dbname*: [ string ]
                The SQL database to read the tables from
        '''
        
        self.tables = []
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        
        for tid in _list_tables(engine):
            table = SQLTable()
            table.read(dbname,tid=tid,dbtype=dbtype,username=username,password=password,port=port,host=host)
            self.tables.append(table)
    
    def write(self,dbname,dbtype='sqlite',username='',password='',host=''):
        '''
        Write all tables to a SQL file
        
        Required Arguments:
        
            *dbname*: [ string ]
                The SQL database to write the tables to
                
        Optional Keyword Arguments:
        
            *dbtype*: [ 'sqlite' | 'postgres' | 'mysql']
                Choosing which database format to write in
        '''
        
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        
        for table in self.tables:
            metadata = sql.MetaData()
            tbl = sql.Table(table.table_name, metadata)
            for i, col_name in enumerate(np.array(table.names).astype(str)):
                tbl.columns.add(sql.Column(col_name,
                type_dict_out[type(table.array[col_name][0])]
                ))

            metadata.create_all(engine)

            sources = []

            for i in range(len(table.array[self.names[0].encode()])):
                source = {}
                for col_name in np.array(table.names).astype(str):
                    source[col_name] = table.array[col_name][i]
                sources.append(source)

            # Insert values into database
            conn = engine.connect() # Maybe change this part?
            conn.execute(tbl.insert(),sources)
            
        conn.close()
        