import numpy as np
from copy import copy

default_format = {}
default_format[None.__class__] = 16,'.9e'
default_format[np.int16] = 10,'i'
default_format[np.int32] = 10,'i'
default_format[np.int64] = 10,'i'
default_format[np.float32] = 11,'.4e'
default_format[np.float64] = 16,'.9e'
default_format[np.str] = 10,'s'
default_format[np.string_] = 10,'s'
default_format[str] = 10,'s'
default_format[np.unicode_] = 10,'s'

class BaseTable(object):
    
    def __init__(self,*args,**kwargs):
        '''
        Create a table instance
        
        Optional Arguments:
        
            If no arguments are given, and empty table is created
            
            If one argument is given, it can either be:
            
                - the name of a file to read the table from

                - a table instance (can be of any type). In this
                  case, the entire contents of the passed instance
                  are copied into the new table.
        
        Optional Keyword Arguments:
        
            Any keyword arguments are passed to read() method if a
            filename is specified.
        
        '''
        
        self.reset()
        
        # If more than one argument is provided, raise an exception
        if len(args) > 1:
            raise Exception("table() received too many arguments")
        
        # Otherwise transfer the data to the new instance
        elif len(args) == 1:
            
            arg = args[0]
            
            if isinstance(arg,BaseTable):
                table = arg
                self.table_name = table.table_name
                self.names = table.names
                self.array = table.array
                self.units = table.units
                self.descriptions = table.descriptions
                self.keywords = table.keywords
                self.comments = table.comments
                self.nulls = table.nulls
                self.formats = table.formats
            elif type(arg) == str:
                filename = arg
                self.read(filename,**kwargs)
            else:
                raise Exception("Unknown argument type: "+str(type(arg)))
        
        # Supplied table name overrides name passed through table
        if kwargs.has_key('name'):
            self.table_name = kwargs['name']
        
        # Update shape
        self._update_shape()
        
        return
    
    def __getattr__(self,attribute):
                
        if attribute in self.names:
            return self.array[attribute]
        else:
            raise AttributeError(attribute)
    
    def __len__(self):
        if len(self.names) == 0:
            return 0
        else:
            return len(self.array[self.names[0]])
    
    def reset(self):
        self.table_name = ""
        self.names = []
        self.array = {}
        self.units = {}
        self.descriptions = {}
        self.nulls = {}
        self.formats = {}
        self.keywords = {}
        self.comments = []
        return
    
#    def add_columns(self,names,data):
#        self.reset()
#        for column in columns:
#            self.add_column(names,data)
#        self._update_shape()
#        return
    
    def add_column(self,name,data,unit='',null='',description='',format=None):
        '''
        Add a column to the table
        
        Required Arguments:
            
            *name*: [ string ]
                The name of the column to add
                
            *data*: [ numpy array ]
                The column data
        
        Optional Keyword Arguments:
            
            *unit*: [ string ]
                The unit of the values in the column
            
            *null*: [ same type as data ]
                The values corresponding to 'null', if not NaN
            
            *description*: [ string ]
                A description of the content of the column
            
            *format*: [ string ]
                The format to use for ASCII printing
        '''
                
        self.names.append(name)
        self.array[name] = np.array(data)
        self.units[name] = unit
        self.descriptions[name] = description
        self.nulls[name] = null
        
        column_type = type(data.ravel()[0])
        
        if format:
            self.formats[name] = format
        else:
            self.formats[name] = str(default_format[column_type][0])+default_format[column_type][1]
        
        self._update_shape()
        return
    
    def add_comment(self,comment):
        '''
        Add a comment to the table
        
        Required Argument:
            
            *comment*: [ string ]
                The comment to add to the table
        '''
        
        self.comments.append(comment.strip())
        return
    
    def add_keyword(self,key,value):
        '''
        Add a keyword/value pair to the table
        
        Required Arguments:
            
            *key*: [ string ]
                The name of the keyword
            
            *value*: [ string | float | integer | bool ]
                The value of the keyword
        '''
        
        if type(value) == str:
            value = value.strip()
        self.keywords[key.strip()] = value
        return
    
    def remove_column(self,remove_name):
        '''
        Remove a column from the table
        
        Required Argument:
            
            *remove_name*: [ string ]
                The name of the column to remove
        '''
        
        try:
            
            colnum = self.names.index(remove_name)
            self.names.pop(colnum)
            
            self.array.pop(remove_name)
            self.units.pop(remove_name)
            self.descriptions.pop(remove_name)
        
        except ValueError,KeyError:
            
            raise Exception("Column "+remove_name+" does not exist")
        
        # Update shape
        self._update_shape()
        return
    
    def remove_columns(self,remove_names):
        '''
        Remove several columns from the table
        
        Required Argument:
            
            *remove_names*: [ list of strings ]
                A list containing the names of the columns to remove
        '''
        
        if type(remove_names) == str:
            remove_names = [remove_names]
        
        for name in remove_names:
            self.remove_column(name)
        
        return
    
    def keep_columns(self,keep_names):
        '''
        Keep only specific columns in the table (remove the others)
        
        Required Argument:
            
            *keep_names*: [ list of strings ]
                A list containing the names of the columns to keep.
                All other columns will be removed.
        '''
        
        if type(keep_names) == str:
            keep_names = [keep_names]
        
        remove_names = list( set(self.names) - set(keep_names) )
        
        if len(remove_names) == len(self.names):
            raise Exception("No columns to keep")
        
        self.remove_columns(remove_names)
        
        return
    
    def rename_column(self,old_name,new_name):
        '''
        Rename a column from the table
        
        Require Arguments:
            
            *old_name*: [ string ]
                The current name of the column.
            
            *new_name*: [ string ]
                The new name for the column
        '''
        
        if new_name in self.names:
            raise Exception("Column "+new_name+" already exists")
        
        if not old_name in self.names:
            raise Exception("Column "+old_name+" not found")
        
        for i,name in enumerate(self.names):
            if name == old_name:
                self.names[i] = new_name
                
                self.array[new_name] = self.array[old_name]
                del self.array[old_name]
                
                self.units[new_name] = self.units[old_name]
                del self.units[old_name]
                
                self.descriptions[new_name] = self.descriptions[old_name]
                del self.descriptions[old_name]
                
                self.nulls[new_name] = self.nulls[old_name]
                del self.nulls[old_name]
                
                self.formats[new_name] = self.formats[old_name]
                del self.formats[old_name]
        
        return
    
    def describe(self):
        
        print "Table : "+self.table_name
        
        # Find maximum column widths
        len_name_max,len_unit_max,len_datatype_max,len_formats_max = 4,4,4,6
        for name in self.names:
            len_name_max = max(len(name),len_name_max)
            len_unit_max = max(len(str(self.units[name])),len_unit_max)
            len_datatype_max = max(len(str(type(self.array[name][0]))),len_datatype_max)
            len_formats_max = max(len(self.formats[name]),len_formats_max)
        
        # Print out table
        
        format = "| %"+str(len_name_max)+"s | %"+str(len_unit_max)+"s | %"+str(len_datatype_max)+"s | %"+str(len_formats_max)+"s |"
        len_tot = len_name_max+len_unit_max+len_datatype_max+len_formats_max+13
        
        print "-"*len_tot
        print format % ("Name","Unit","Type","Format")
        print "-"*len_tot
        
        for name in self.names:
            print format % (name,str(self.units[name]),str(type(self.array[name][0])),self.formats[name])
        
        print "-"*len_tot
        
        return
    
    def where(self,mask):
        
        new_table = self.__class__()
        
        new_table.table_name = copy(self.table_name)
        new_table.names = copy(self.names)
        new_table.array = copy(self.array)
        new_table.units = copy(self.units)
        new_table.descriptions = copy(self.descriptions)
        new_table.keywords = copy(self.keywords)
        new_table.comments = copy(self.comments)
        new_table.nulls = copy(self.nulls)
        new_table.formats = copy(self.formats)
        
        for name in new_table.names:
            new_table.array[name] = self.array[name][mask]
        
        new_table._update_shape()
        
        return new_table
    
    def _update_shape(self):
        n_rows = self.__len__()
        n_cols = len(self.names)
        self.shape = (n_rows,n_cols)
        
        return

class BaseTableSet(object):
    
    def __init__(self,*args):
        '''
        Create a table set instance
        
        Optional Arguments:
        
            If no arguments are given, and empty table set is created
            
            If one argument is given, it can either be:
            
                - a list of individual tables (which can have inhomogeneous types)
            
                - a table set of any type
        '''
        
        if len(args) > 1:
            raise Exception(self.__name__+" either takes no or one argument")
        elif len(args) == 1:
            data = args[0]
        else:
            data = None
        
        self.tables = []
        
        if data:
            if type(data) == list:
                for table in data:
                    self.tables.append(self._single_table(table))
            elif isinstance(data,BaseTableSet):
                for table in data.tables:
                    self.tables.append(self._single_table(table))
            else:
                raise Exception("Unknown type: "+type(data))
        
        return
    
    def append(self,table):
        '''
        Append a table to the table set
        
        Required Arguments:
            
            *table*: [ a table instance ]
                This can be a table of any type, which will be converted
                to a table of the same type as the parent set (e.g. adding
                a single VOTable to a FITSTableSet will convert the VOTable
                to a FITSTable inside the set)
        '''
        self.tables.append(self._single_table(table))
        return
    
    def describe(self):
        '''
        Describe all the tables in the set
        '''
        for table in self.tables:
            table.describe()
        return