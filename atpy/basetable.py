import numpy as np

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
        
    def __getattr__(self,attribute):
        
        if attribute in self.names:
            return self.array[attribute]
        else:
            raise AttributeError(attribute)
        
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

            raise Exception("Column "+name+" does not exist")
    
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
        
    def describe(self,):
        
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

class BaseTableSet(object):

    def append(self,table):

        self.tables.append(table)

    def describe(self):

        for table in self.tables:
            table.describe()