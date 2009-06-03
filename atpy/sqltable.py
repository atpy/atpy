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


accept = ['postgres','mysql'] # sqlite is automatically included, regardless of this 'accept' list.


def _smart_dialect(dbname,dbtype,username='',password='',port='',host=''):
    dialect = ['postgres','mysql']
    
    if dbtype is 'sqlite':
        engine = sql.create_engine(dbtype+':///'+dbname)
        
    elif dbtype in dialect:
        
        if port is not '':
            port = ':' + port
        
        engine = sql.create_engine(dbtype+'://'+username+':'+password+'@'+host+port+'/'+dbname)
    
    else:
        print 'Your dbtype '+str(dbtype)+' was not recognized. \nSQLTable(Set) only accepts sqlite, postgres, or mysql as a dbtype.'
        
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
    Class for working with reading and writing tables in databases.
    '''
    
    def read(self,dbname,tid=-1,dbtype='sqlite',username='',password='',port='',host=''):
        '''
        Required Arguments:
            
            *dbname*: [ string ]
                The SQL database to write the tables to
        
        Optional Keyword Arguments:
            *tid*: [ integer ]
                If you get a return from the read function stating that
                there's more than one table, pick the corresponding integer
                to which table you want to load, with tid = N, where N is
                and integer.
            
            *dbtype*: [ 'sqlite' | 'postgres' | 'mysql']
                Choosing which database format to write in.
            
            *username*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *password*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *port*: [ string ]
                Port number is sometimes needed depending on setup of
                database manager. If using sqlite, this field is not necessary.
            
            *host*: [ string ]
                Typically 'localhost' or some ip address, depending on where the
                database is located. If using sqlite, this field is not necessary.
        
        '''
        
        # Erase existing content
        self.reset()
        
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        
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
                tbl = sql.Table(tbl_names[tid], metadata, autoload=True)
                self.table_name = tbl_names[tid]
            except:
                print 'Table name '+str(tid)+' is not recognized.'
                return
        
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
    
    
    def write(self,dbname,dbtype='sqlite',username='',password='',port='',host=''):
        '''
        Required Arguments:
            
            *dbname*: [ string ]
                The SQL database to write the tables to
        
        Optional Keyword Arguments:
            
            *dbtype*: [ 'sqlite' | 'postgres' | 'mysql']
                Choosing which database format to write in.
            
            *username*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *password*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *port*: [ string ]
                Port number is sometimes needed depending on setup of
                database manager. If using sqlite, this field is not necessary.
            
            *host*: [ string ]
                Typically 'localhost' or some ip address, depending on where the
                database is located. If using sqlite, this field is not necessary.
        
        '''
        
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
    '''
    Class for working with reading and writing sets of tables in databases.
    '''
    
    def _single_table(self,table):
        return SQLTable(table)
    
    def read(self,dbname,dbtype='sqlite',username='',password='',port='',host=''):
        '''
        Required Arguments:
            
            *dbname*: [ string ]
                The SQL database to write the tables to
        
        Optional Keyword Arguments:
            
            *dbtype*: [ 'sqlite' | 'postgres' | 'mysql']
                Choosing which database format to write in.
            
            *username*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *password*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *port*: [ string ]
                Port number is sometimes needed depending on setup of database manager.
                If using sqlite, this field is not necessary.
            
            *host*: [ string ]
                Typically 'localhost' or some ip address, depending on where the database is located.
                If using sqlite, this field is not necessary.
        '''
        
        self.tables = []
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        
        for i,tid in enumerate(_list_tables(engine)):
            table = SQLTable()
            table.read(dbname,tid=i,dbtype=dbtype,username=username,password=password,port=port,host=host)
            self.tables.append(table)
    
    
    def write(self,dbname,dbtype='sqlite',username='',password='',port='',host=''):
        '''
        Write all tables to a SQL file
        
        Required Arguments:
            
            *dbname*: [ string ]
                The SQL database to write the tables to
        
        Optional Keyword Arguments:
            
            *dbtype*: [ 'sqlite' | 'postgres' | 'mysql']
                Choosing which database format to write in.
            
            *username*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *password*: [ string ]
                If not using sqlite, then username is most likely needed.
            
            *port*: [ string ]
                Port number is sometimes needed depending on setup of database manager.
                If using sqlite, this field is not necessary.
            
            *host*: [ string ]
                Typically 'localhost' or some ip address, depending on where the database is located.
                If using sqlite, this field is not necessary.
        '''
        
        engine = _smart_dialect(dbname=dbname,dbtype=dbtype,username=username,password=password,port=port,host=host)
        conn = engine.connect() # Maybe change this part?
        
        for i,table in enumerate(self.tables):
            metadata = sql.MetaData()
            tbl = sql.Table(table.table_name, metadata)
            for j, col_name in enumerate(np.array(table.names).astype(str)):
                tbl.columns.add(sql.Column(col_name,
                type_dict_out[type(table.array[col_name][0])]
                ))
            
            metadata.create_all(engine)
            
            sources = []
            
            for j in range(len(table.array[self.tables[i].names[0].encode()])):
                source = {}
                for col_name in np.array(table.names).astype(str):
                    source[col_name] = table.array[col_name][j]
                sources.append(source)
            
            # Insert values into database
            conn.execute(tbl.insert(),sources)
        
        conn.close()
    