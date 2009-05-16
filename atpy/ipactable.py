from basetable import BaseTable
import numpy as np

# Define type conversion from IPAC table to numpy arrays
type_dict = {}
type_dict['i'] = np.int
type_dict['int'] = np.int
type_dict['integer'] = np.int
type_dict['double'] = np.float64
type_dict['float'] = np.float32
type_dict['real'] = np.float32
type_dict['char'] = np.str
type_dict['date'] = np.str

type_rev_dict = {}
type_rev_dict[np.int16] = "int"
type_rev_dict[np.int32] = "int"
type_rev_dict[np.int64] = "int"
type_rev_dict[np.float32] = "float"
type_rev_dict[np.float64] = "double"
type_rev_dict[np.str] = "char"
type_rev_dict[np.string_] = "char"
type_rev_dict[str] = "char"

class IPACTable(BaseTable):
    ''' A class for reading and writing a single IPAC table.'''
    
    def read(self,filename,definition=3):
        '''
        Read a table from a IPAC file
        
        Required Arguments:
            
            *filename*: [ string ]
                The IPAC file to read the table from
        
        Optional Keyword Arguments:
            
            *definition*: [ 1 | 2 | 3 ]
                
                The definition to use to read IPAC tables:
                
                1: any character below a pipe symbol belongs to the
                   column on the left, and any characters below the
                   first pipe symbol belong to the first column.
                2: any character below a pipe symbol belongs to the
                   column on the right.
                3: no characters should be present below the pipe
                   symbols (default).
        '''
        
        if not definition in [1,2,3]:
            raise Exception("definition should be one of 1/2/3")
        
        # Erase existing content
        self.reset()
        
        # Open file for reading
        f = file(filename,'rb')
        
        line = f.readline()
        
        # Read in comments and keywords
        while True:
            
            char1 = line[0:1]
            char2 = line[1:2]
            
            if char1 <> '\\':
                break
            
            if char2==' ' or not '=' in line: # comment
                self.add_comment(line[1:])
            else:          # keyword
                pos = line.index('=')
                key,value = line[1:pos],line[pos+1:]
                value = value.replace("'","").replace('"','')
                key,value   = key.strip(),value.strip()
                self.add_keyword(key,value)
            
            line = f.readline()
        
        
        # Column headers
        
        l = 0
        units = {}
        nulls = {}
        
        while True:
            
            char1 = line[0:1]
            
            if char1 <> "|":
                break
            
            if l==0: # Column names
                
                line = line.replace('-',' ').strip()
                
                # Find all pipe symbols
                pipes = []
                for i,c in enumerate(line):
                    if c=='|':
                        pipes.append(i)
                
                # Find all names
                names = line.replace(" ","").split("|")[1:-1]
            
            elif l==1: # Data types
                
                line = line.replace('-',' ').strip()
                
                types = dict(zip(names,line.replace(" ","").split("|")[1:-1]))
            
            elif l==2: # Units
                
                units = dict(zip(names,line.replace(" ","").split("|")[1:-1]))
            
            else: # Null values
                
                nulls = dict(zip(names,line.replace(" ","").split("|")[1:-1]))
            
            line = f.readline()
            l = l + 1
        
        if len(pipes) <> len(names) + 1:
            raise "An error occured while reading the IPAC table"
        
        if len(units)==0:
            for name in names:
                units[name]=''
        
        if len(nulls)==0:
            for name in names:
                nulls[name]=''
        
        # Data
        
        array = {}
        for name in names:
            array[name] = []
        
        
        while True:
            
            if line.strip() == '':
                break
            
            for i in range(len(pipes)-1):
                
                first,last = pipes[i]+1,pipes[i+1]
                
                if definition==1:
                    last = last + 1
                    if first==1:
                        first=0
                elif definition==2:
                    first = first - 1
                
                if i+1==len(pipes)-1:
                    item = line[first:].strip()
                else:
                    item = line[first:last].strip()
                
                if item == nulls[names[i]]:
                    item = 'NaN'
                array[names[i]].append(item)
            
            line = f.readline()
        
        # Convert to numpy arrays
        for name in names:
            array[name] = np.array(array[name],dtype=type_dict[types[name]])
            self.add_column(name,array[name],null=nulls[name],unit=units[name])
    
    def write(self,filename):
        '''
        Write the table to an IPAC file
        
        Required Arguments:
            
            *filename*: [ string ]
                The IPAC file to write the table to
        '''
        
        # Open file for writing
        f = file(filename,'wb')
        
        for key in self.keywords:
            value = self.keywords[key]
            f.write("\\"+key+"="+str(value)+"\n")
        
        for comment in self.comments:
            f.write("\\ "+comment+"\n")
        
        # Compute width of all columns
        
        width = {}
        format = {}
        
        line_names = ""
        line_types = ""
        line_units = ""
        line_nulls = ""
        
        for name in self.names:
            
            coltype = type_rev_dict[type(self.array[name][0])]
            colunit = self.units[name]
            colnull = self.nulls[name]
            
            # Adjust the format for each column
            
            width = int(self.formats[name].replace("i","").replace("s","").replace("f","").replace("e","").split(".")[0])
            suffix = self.formats[name][len(str(width)):]
            
            max_width = max(len(name),len(coltype),len(colunit),len(colnull))
            
            if coltype == 'char':
                for item in self.array[name]:
                    if len(item) > max_width:
                        max_width = len(item)
            
            if max_width > width:
                width = max_width
            
            format[name] = str(width)+suffix
            
            sf = "%"+str(width)+"s"
            line_names = line_names + "|" + (sf % name)
            line_types = line_types + "|" + (sf % coltype)
            line_units = line_units + "|" + (sf % colunit)
            line_nulls = line_nulls + "|" + (sf % colnull)
        
        line_names = line_names + "|\n"
        line_types = line_types + "|\n"
        line_units = line_units + "|\n"
        line_nulls = line_nulls + "|\n"
        
        f.write(line_names)
        f.write(line_types)
        if len(line_units.replace("|","").strip()) > 0:
            f.write(line_units)
        if len(line_nulls.replace("|","").strip()) > 0:
            f.write(line_nulls)
        
        for i in range(len(self.array[self.names[0]])):
            
            line = ""
            
            for name in self.names:
                line = line + " " + (("%"+format[name]) % self.array[name][i])
            
            line = line + " \n"
            
            f.write(line)
        
        f.close()