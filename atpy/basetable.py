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
                self.null = table.null
                self.formats = table.formats
            elif type(arg) == str:
                filename = arg
                self.read(filename)
            else:
                raise Exception("Unknown argument type: "+str(type(arg)))
        
        # Supplied table name overrides name passed through table
        if kwargs.has_key('name'):
            self.table_name = kwargs['name']
            
        # Update shape
        self._update_shape()
        
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
        self.null = {}
        self.formats = {}
        self.keywords = {}
        self.comments = []
        
    def populate(self,columns):
        
        self.reset()
        
        for column in columns:
            self.add_column(column)
            
        # Update shape
        self._update_shape()
        
    def add_column(self,column,unit='',null='',description='',format=None):
                
        name,array = column
        
        self.names.append(name)
        self.array[name] = np.array(array)
        self.units[name] = unit
        self.descriptions[name] = description
        self.null[name] = null
                
        column_type = type(array.ravel()[0])        
        
        if format:
            self.formats[name] = format
        else:
            self.formats[name] = str(default_format[column_type][0])+default_format[column_type][1]
            
        # Update shape
        self._update_shape()
                
    def add_comment(self,comment):
        self.comments.append(comment.strip())
        
    def add_keyword(self,key,value):
        if type(value) == str:
            value = value.strip()
        self.keywords[key.strip()] = value
        
    def remove_column(self,remove_name):
        
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
    
    def remove_columns(self,remove_names):
        
        if type(remove_names) == str:
            remove_names = [remove_names]
            
        for name in remove_names:
            self.remove_column(name)
    
    def keep_columns(self,keep_names):
        
        if type(keep_names) == str:
            keep_names = [keep_names]
        
        remove_names = list( set(self.names) - set(keep_names) )

        if len(remove_names) == len(self.names):
            raise Exception("No columns to keep")

        self.remove_columns(remove_names)        
    
    def rename_column(self,old_name,new_name):
        
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

                self.null[new_name] = self.null[old_name]
                del self.null[old_name]

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
        
    def where(self,mask):
        
        new_table = self.__class__()
                
        new_table.table_name = copy(self.table_name)
        new_table.names = copy(self.names)
        new_table.array = copy(self.array)
        new_table.units = copy(self.units)
        new_table.descriptions = copy(self.descriptions)
        new_table.keywords = copy(self.keywords)
        new_table.comments = copy(self.comments)
        new_table.null = copy(self.null)
        new_table.formats = copy(self.formats)
                                
        for name in new_table.names:
            new_table.array[name] = self.array[name][mask]
            
        new_table._update_shape()
            
        return new_table
        
    def _update_shape(self):
        n_rows = self.__len__()
        n_cols = len(self.names)
        self.shape = (n_rows,n_cols)

class BaseTableSet(object):

    def append(self,table):

        self.tables.append(table)

    def describe(self):

        for table in self.tables:
            table.describe()