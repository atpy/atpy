# need to add check for 2D arrays (don't support it)

import numpy as np
import sqlhelper as sql
from basetable import BaseTable,BaseTableSet

class SQLTable2(BaseTable):
    '''
    Class for working with reading and writing tables in databases.
    '''
    
    def read(self,dbtype,*args,**kwargs):
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
        
        if kwargs.has_key('tid'):
            tid = kwargs.pop('tid')
        else:
            tid = None
        
        # Erase existing content
        self.reset()
        
        connection,cursor = sql.connect_database(dbtype,*args,**kwargs)
        
        # If no table is requested, check that there is only one table
        
        table_names = sql.list_tables(cursor,dbtype)
        
        if tid==None:
            if len(table_names) == 1:
                tid = 1
            else:
                print "-"*56
                print " There is more than one table in the requested file"
                print " Please specify the table desired with the tid= argument"
                print " The available tables are:"
                print ""
                for tid in table_names:
                    print " tid=%i : %s" % (tid,table_names[tid])
                print "-"*56
                return
        
        table_name = table_names[tid]
        
        column_names,column_types = sql.column_info(cursor,dbtype,table_name)
        
        cursor = connection.cursor()
        
        for i,column_name in enumerate(column_names):
            column_type = column_types[i]
            cursor.execute('select '+sql.quote[dbtype]+column_name+sql.quote[dbtype]+' from '+table_name)
            result = cursor.fetchall()
            self.add_column(column_name,np.array(result,column_type).ravel())
        
        self.table_name = table_name
    
    def write(self,dbtype,*args,**kwargs):
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
        
        # Check if table overwrite is requested
        if kwargs.has_key('overwrite'):
            overwrite = kwargs.pop('overwrite')
        else:
            overwrite = False
        
        # Open the connection
        connection,cursor = sql.connect_database(dbtype,*args,**kwargs)
        
        # Check that table name is set
        if not self.table_name:
            raise Exception("Table name is not set")
        else:
            table_name = self.table_name
        
        # Check that table name is ok
        # todo
        
        # lowercase because pgsql automatically converts table names to lower case
        
        # Check if table already exists
        
        existing_tables = sql.list_tables(cursor,dbtype).values()
        if table_name in existing_tables or table_name.lower() in existing_tables:
            if overwrite:
                sql.drop_table(cursor,table_name)
            else:
                raise Exception("Table already exists - use overwrite to replace existing table")
        
        # Create table
        sql.create_table(cursor,dbtype,table_name,self.names,self.types)
        
        # Insert row
        for i in range(self.__len__()):
            sql.insert_row(cursor,dbtype,table_name,self.row(i,python_types=True))
        
        # Close connection
        connection.commit()
        cursor.close()

class SQLTableSet2(BaseTableSet):
    
    def _single_table(self,table):
        return SQLTable2(table)
    
    def read(self,dbtype,*args,**kwargs):
        
        self.tables = []
        
        connection,cursor = sql.connect_database(dbtype,*args,**kwargs)
        table_names = sql.list_tables(cursor,dbtype)
        cursor.close()
        
        for tid in table_names:
            kwargs['tid'] = tid
            table = SQLTable2()
            table.read(dbtype,*args,**kwargs)
            self.tables.append(table)
    
    def write(self,dbtype,*args,**kwargs):
        
        for i,table in enumerate(self.tables):
            self.write(dbtype,*args,**kwargs)
