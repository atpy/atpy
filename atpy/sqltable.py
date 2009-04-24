import numpy as np
import sqlalchemy as sql
from basetable import BaseTable, BaseTableSet
import decimal

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

class SQLTable(BaseTable):
    """
    Class for working with SQLTable read and write
    """
    
    def read(self,dbname,dbtype='sqlite',username='',password='',host='localhost'):
        """
        You can read in a SQL table with this method. 
        
        Example: 
        st = SQLTable(name='Some Table') 
        st.read('a_file_that_you_want_to_read.db')
        
        # Want to convert the data from SQL to VOTable?
        
        vt = VOTable(st)
        vt.write('file_name.xml') # You're done. It's all set!
        """
        
        def uni2str(array):
            if type(array) == np.unicode_:
                array = array.astype(np.str)
            else:
                pass
            return array
        
        # Erase existing content
        self.reset()
        
        if dbtype is 'sqlite':
            engine = sql.create_engine(dbtype+':///'+dbname)
            metadata = sql.MetaData(engine)
            
            tbl_names = np.array(engine.table_names()).astype(np.str)
            print tbl_names
            
            tbl = sql.Table(tbl_names[0].encode(), metadata, autoload=True)
            self.table_name = tbl_names[0].encode()
            
            #s = table.select().where().where()
            results = engine.execute(tbl.select()).fetchall()
            for col in tbl.columns.keys():
                column = []
                for row in results:
                    elem = row[col]
                    if type(elem)==decimal.Decimal:
                        elem = float(elem)
                    column.append(elem)
                self.add_column((col,uni2str(np.array(column))))
    
    
    def write(self,dbname,dbtype='sqlite',username='',password='',host='localhost'):
        engine = sql.create_engine(dbtype+':///'+dbname)
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