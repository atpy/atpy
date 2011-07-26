import os
import numpy as np
import warnings

from helpers import smart_mask
from decorators import auto_download_to_file, auto_decompress_to_fileobj, auto_fileobj_to_file

# Define type conversion from IPAC table to numpy arrays
type_dict = {}
type_dict['i'] = np.int64
type_dict['int'] = np.int64
type_dict['integer'] = np.int64
type_dict['long'] = np.int64
type_dict['double'] = np.float64
type_dict['float'] = np.float32
type_dict['real'] = np.float32
type_dict['char'] = np.str
type_dict['date'] = np.str

type_rev_dict = {}
type_rev_dict[np.bool_] = "int"
type_rev_dict[np.int8] = "int"
type_rev_dict[np.int16] = "int"
type_rev_dict[np.int32] = "int"
type_rev_dict[np.int64] = "int"
type_rev_dict[np.uint8] = "int"
type_rev_dict[np.uint16] = "int"
type_rev_dict[np.uint32] = "int"
type_rev_dict[np.uint64] = "int"
type_rev_dict[np.float32] = "float"
type_rev_dict[np.float64] = "double"
type_rev_dict[np.str] = "char"
type_rev_dict[np.string_] = "char"
type_rev_dict[str] = "char"

invalid = {}
invalid[np.int32] = -np.int64(2**31-1)
invalid[np.int64] = -np.int64(2**63-1)
invalid[np.float32] = np.float32(np.nan)
invalid[np.float64] = np.float64(np.nan)


@auto_download_to_file
@auto_decompress_to_fileobj
@auto_fileobj_to_file
def read(self, filename, definition=3, verbose=True, smart_typing=False):
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

        *smart_typing*: [ True | False ]

            Whether to try and save memory by using the smallest
            integer type that can contain a column. For example,
            a column containing only values between 0 and 255 can
            be stored as an unsigned 8-bit integer column. The
            default is false, so that all integer columns are
            stored as 64-bit integers.
    '''

    if not definition in [1, 2, 3]:
        raise Exception("definition should be one of 1/2/3")

    self.reset()

    # Open file for reading
    f = file(filename, 'rb')

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
            key, value = line[1:pos], line[pos + 1:]
            value = value.replace("'", "").replace('"', '')
            key, value = key.strip(), value.strip()
            self.add_keyword(key, value)

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

            line = line.replace('-', ' ').strip()

            # Find all pipe symbols
            pipes = []
            for i, c in enumerate(line):
                if c=='|':
                    pipes.append(i)

            # Find all names
            names = line.replace(" ", "").split("|")[1:-1]

        elif l==1: # Data types

            line = line.replace('-', ' ').strip()

            types = dict(zip(names, \
                line.replace(" ", "").split("|")[1:-1]))

        elif l==2: # Units

            units = dict(zip(names, \
                line.replace(" ", "").split("|")[1:-1]))

        else: # Null values

            nulls = dict(zip(names, \
                line.replace(" ", "").split("|")[1:-1]))

        line = f.readline()
        l = l + 1

    if len(pipes) <> len(names) + 1:
        raise "An error occured while reading the IPAC table"

    if len(units)==0:
        for name in names:
            units[name]=''

    if len(nulls)==0:
        nulls_given = False
        for name in names:
            nulls[name]=''
    else:
        nulls_given = True

    # Pre-compute numpy column types
    numpy_types = {}
    for name in names:
        numpy_types[name] = type_dict[types[name]]

    # Data

    array = {}
    for name in names:
        array[name] = []


    while True:

        if line.strip() == '':
            break

        for i in range(len(pipes)-1):

            first, last = pipes[i] + 1, pipes[i + 1]

            if definition==1:
                last = last + 1
                if first==1:
                    first=0
            elif definition==2:
                first = first - 1

            if i + 1==len(pipes)-1:
                item = line[first:].strip()
            else:
                item = line[first:last].strip()

            if item.lower() == 'null' and nulls[names[i]] <> 'null':
                if nulls[names[i]] == '':
                    if verbose:
                        print "WARNING: found unexpected 'null' value. Setting null value for column "+names[i]+" to 'null'"
                    nulls[names[i]] = 'null'
                    nulls_given = True
                else:
                    raise Exception("null value for column "+names[i]+" is set to "+nulls[i]+" but found value 'null'")
            array[names[i]].append(item)

        line = f.readline()

    # Check that null values are of the correct type
    if nulls_given:
        for name in names:
            try:
                n = numpy_types[name](nulls[name])
                nulls[name] = n
            except:
                n = invalid[numpy_types[name]]
                for i, item in enumerate(array[name]):
                    if item == nulls[name]:
                        array[name][i] = n
                if verbose:
                    if len(str(nulls[name]).strip()) == 0:
                        print "WARNING: empty null value for column "+name+" set to "+str(n)
                    else:
                        print "WARNING: null value for column "+name+" changed from "+str(nulls[name])+" to "+str(n)
                nulls[name] = n

    # Convert to numpy arrays
    for name in names:

        if smart_typing:

            dtype = None

            low = min(array[name])
            high = max(array[name])

            if types[name] in ['i', 'int', 'integer']:
                low, high = long(low), long(high)
                for nt in [np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64]:
                    if low >= np.iinfo(nt).min and high <= np.iinfo(nt).max:
                        dtype = nt
                        break
            elif types[name] in ['long']:
                low, high = long(low), long(high)
                for nt in [np.uint64, np.int64]:
                    if low >= np.iinfo(nt).min and high <= np.iinfo(nt).max:
                        dtype = nt
                        break
            elif types[name] in ['float', 'real']:
                low, high = float(low), float(high)
                for nt in [np.float32, np.float64]:
                    if low >= np.finfo(nt).min and high <= np.finfo(nt).max:
                        dtype = nt
                        break
            else:
                dtype = type_dict[types[name]]

        else:
            dtype = type_dict[types[name]]

            # If max integer is larger than 2**63 then use uint64
            if dtype == np.int64:
                if max([long(x) for x in array[name]]) > 2**63:
                    dtype = np.uint64
                    warnings.warn("using type uint64 for column %s" % name)

        array[name] = np.array(array[name], dtype=dtype)

        if smart_typing:
            if np.min(array) >= 0 and np.max(array) <= 1:
                array = array == 1

        if self._masked:
            self.add_column(name, array[name], \
                mask=smart_mask(array[name], nulls[name]), unit=units[name], \
                fill=nulls[name])
        else:
            self.add_column(name, array[name], \
                null=nulls[name], unit=units[name])


def write(self, filename, overwrite=False):
    '''
    Write the table to an IPAC file

    Required Arguments:

        *filename*: [ string ]
            The IPAC file to write the table to
    '''

    self._raise_vector_columns()

    if os.path.exists(filename):
        if overwrite:
            os.remove(filename)
        else:
            raise Exception("File exists: %s" % filename)

    # Open file for writing
    f = file(filename, 'wb')

    for key in self.keywords:
        value = self.keywords[key]
        f.write("\\" + key + "=" + str(value) + "\n")

    for comment in self.comments:
        f.write("\\ " + comment + "\n")

    # Compute width of all columns

    width = {}
    format = {}

    line_names = ""
    line_types = ""
    line_units = ""
    line_nulls = ""

    width = {}

    for name in self.names:

        dtype = self.columns[name].dtype

        coltype = type_rev_dict[dtype.type]
        colunit = self.columns[name].unit

        if self._masked:
            colnull = self.data[name].fill_value
        else:
            colnull = self.columns[name].null

        if colnull:
            colnull = ("%" + self.format(name)) % colnull
        else:
            colnull = ''

        # Adjust the format for each column

        width[name] = self.columns[name].format[0]

        max_width = max(len(name), len(coltype), len(colunit), \
            len(colnull))

        if max_width > width[name]:
            width[name] = max_width

        sf = "%" + str(width[name]) + "s"
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
    if len(line_units.replace("|", "").strip()) > 0:
        f.write(line_units)
    if len(line_nulls.replace("|", "").strip()) > 0:
        f.write(line_nulls)

    for i in range(self.__len__()):

        line = ""

        for name in self.names:
            if self.columns[name].dtype == np.uint64:
                item = (("%" + self.format(name)) % long(self.data[name][i]))
            else:
                item = (("%" + self.format(name)) % self.data[name][i])
            item = ("%" + str(width[name]) + "s") % item
            line = line + " " + item

        line = line + " \n"

        f.write(line)

    f.close()
