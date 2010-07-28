import unittest
import warnings
import os
import string
import random
import getpass
import sys

import atpy
import numpy as np
np.seterr(all='ignore')

# Size of the test table
shape = (100, )
shape_vector = (100, 10)

# SQL connection parameters
username = getpass.getuser()
password = "C2#uwQsk"


def random_int_array(dtype, shape):
    n = np.product(shape)
    n = n * np.iinfo(dtype).bits / 8
    s = "".join(chr(random.randrange(0, 256)) for i in xrange(n))
    return np.fromstring(s, dtype=dtype).reshape(shape)


def random_float_array(dtype, shape):
    n = np.product(shape)
    if dtype == np.float32:
        n = n * 4
    else:
        n = n * 8
    s = "".join(chr(random.randrange(0, 256)) for i in xrange(n))
    array = np.fromstring(s, dtype=dtype)
    if np.sum(np.isnan(array)):
        array[np.isnan(array)] = random_float_array(dtype, array[np.isnan(array)].shape)
    return array.reshape(shape)


numpy_types = [np.bool, np.int8, np.int16, np.int32, np.int64, np.uint8, \
               np.uint16, np.uint32, np.uint64, np.float32, np.float64, \
               np.dtype('|S100')]


def random_generic(dtype, name, shape):

    if 'int' in name:
        values = random_int_array(dtype, shape)
    elif 'float' in name:
        values = random_float_array(dtype, shape)
    elif 'bool' in name:
        values = np.random.random(shape) > 0.5
    else:
        values = np.zeros(shape, dtype=dtype)
        for i in range(shape[0]):
            s = ""
            for k in range(dtype.itemsize):
                s += random.choice(string.letters + string.digits)
            values[i] = s

    return values


def generate_simple_table(dtype, shape):

    table = atpy.Table(name='atpy_test')

    try:
        name = dtype.__name__
    except:
        name = dtype.type.__name__

    values = random_generic(dtype, name, shape)

    table.add_column('col_'+name, values, dtype=dtype)

    return table


class ColumnsDefaultTestCase():

    def test_uint8(self):
        self.generic_test(np.uint8)

    def test_uint16(self):
        self.generic_test(np.uint16)

    def test_uint32(self):
        self.generic_test(np.uint32)

    def test_uint64(self):
        self.generic_test(np.uint64)

    def test_int8(self):
        self.generic_test(np.int8)

    def test_int16(self):
        self.generic_test(np.int16)

    def test_int32(self):
        self.generic_test(np.int32)

    def test_int64(self):
        self.generic_test(np.int64)

    def test_float32(self):
        self.generic_test(np.float32)

    def test_float64(self):
        self.generic_test(np.float64)

    def test_string(self):
        self.generic_test(np.dtype('|S100'))

class EmptyColumnsTestCase(unittest.TestCase, ColumnsDefaultTestCase):

    def generic_test(self, dtype):
        try:
            t = atpy.Table()
            t.add_empty_column('a', dtype, shape=shape)
            t.add_empty_column('b', dtype)
            t.add_empty_column('c', dtype)
        except:
            self.fail(sys.exc_info()[1])

class EmptyVectorColumnsTestCase(unittest.TestCase, ColumnsDefaultTestCase):

    def generic_test(self, dtype):
        try:
            t = atpy.Table()
            t.add_empty_column('a', dtype, shape=shape_vector)
            t.add_empty_column('b', dtype)
            t.add_empty_column('c', dtype, shape=shape_vector)
        except:
            self.fail(sys.exc_info()[1])

class DefaultTestCase():

    def assertAlmostEqualSig(test, first, second, significant=7, msg=None):
        ratio = first / second
        if np.abs(ratio - 1.) > 10.**(-significant+1):
            raise unittest.TestCase.failureException(msg or '%r != %r within %r significant digits' % (first, second, significant))

    def integer_test(self, dtype):
        colname = 'col_%s' % dtype.__name__
        self.writeread(dtype)
        before, after = self.table_orig.data[colname], self.table_new.data[colname]
        self.assertEqual(before.shape, after.shape)
        if before.ndim == 1:
            for i in range(before.shape[0]):
                self.assertEqual(before[i], after[i])
        else:
            for i in range(before.shape[0]):
                for j in range(before.shape[1]):
                    self.assertEqual(before[i, j], after[i, j])

    def test_uint8(self):
        self.integer_test(np.uint8)

    def test_uint16(self):
        self.integer_test(np.uint16)

    def test_uint32(self):
        self.integer_test(np.uint32)

    def test_uint64(self):
        self.integer_test(np.uint64)

    def test_int8(self):
        self.integer_test(np.int8)

    def test_int16(self):
        self.integer_test(np.int16)

    def test_int32(self):
        self.integer_test(np.int32)

    def test_int64(self):
        self.integer_test(np.int64)

    def float_test(self, dtype, significant=None):
        colname = 'col_%s' % dtype.__name__
        self.writeread(dtype)
        before, after = self.table_orig.data[colname], self.table_new.data[colname]
        self.assertEqual(before.shape, after.shape)
        self.assertEqual(before.dtype.type, after.dtype.type)
        if before.ndim == 1:
            for i in range(before.shape[0]):
                if(np.isnan(before[i])):
                    self.failUnless(np.isnan(after[i]))
                elif(np.isinf(before[i])):
                    self.failUnless(np.isinf(after[i]))
                else:
                    if significant:
                        self.assertAlmostEqualSig(before[i], after[i], significant=significant)
                    else:
                        self.assertEqual(before[i], after[i])
        else:
            for i in range(before.shape[0]):
                for j in range(before.shape[1]):
                    if(np.isnan(before[i, j])):
                        self.failUnless(np.isnan(after[i, j]))
                    elif(np.isinf(before[i, j])):
                        self.failUnless(np.isinf(after[i, j]))
                    else:
                        if significant:
                            self.assertAlmostEqualSig(before[i, j], after[i, j], significant=significant)
                        else:
                            self.assertEqual(before[i, j], after[i, j])

    def test_float32(self):
        if self.format == 'mysql':
            self.float_test(np.float32, significant=6)
        elif self.format == 'postgres':
            self.float_test(np.float32, significant=6)
        else:
            self.float_test(np.float32)

    def test_float64(self):
        if self.format == 'mysql':
            self.float_test(np.float64, significant=15)
        elif self.format == 'postgres':
            self.float_test(np.float64, significant=12)
        else:
            self.float_test(np.float64)

    def test_string(self):
        self.writeread(np.dtype('|S100'))
        before, after = self.table_orig.data['col_string_'], self.table_new.data['col_string_']
        self.assertEqual(before.shape, after.shape)
        self.assertEqual(before.dtype.type, after.dtype.type)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

try:
    import pyfits

    class FITSTestCase(unittest.TestCase, DefaultTestCase):

        format = 'fits'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('test_atpy.fits', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.fits', verbose=False)
            os.remove('test_atpy.fits')

    class FITSTestCaseVector(unittest.TestCase, DefaultTestCase):

        format = 'fits'

        test_string = None # unsupported
        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape_vector)
            self.table_orig.write('test_atpy.fits', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.fits', verbose=False)
            os.remove('test_atpy.fits')

except:
    pass

try:
    import h5py

    class HDF5TestCase(unittest.TestCase, DefaultTestCase):

        format = 'hdf5'

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('test_atpy.hdf5', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.hdf5', verbose=False)
            os.remove('test_atpy.hdf5')

    class HDF5TestCaseVector(unittest.TestCase, DefaultTestCase):

        format = 'hdf5'

        test_string = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape_vector)
            self.table_orig.write('test_atpy.hdf5', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.hdf5', verbose=False)
            os.remove('test_atpy.hdf5')

except:
    pass

try:
    import vo

    class VOTestCase(unittest.TestCase, DefaultTestCase):

        format = 'vo'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('test_atpy.xml', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.xml', verbose=False)
            os.remove('test_atpy.xml')

    class VOTestCaseVector(unittest.TestCase, DefaultTestCase):

        format = 'vo'

        test_string = None # unsupported
        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape_vector)
            self.table_orig.write('test_atpy.xml', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.xml', verbose=False)
            os.remove('test_atpy.xml')

except:
    pass


class IPACTestCase(unittest.TestCase, DefaultTestCase):

    format = 'ipac'

    def writeread(self, dtype):

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('test_atpy.tbl', verbose=False, overwrite=True)
        self.table_new = atpy.Table('test_atpy.tbl', verbose=False)
        os.remove('test_atpy.tbl')

try:
    import sqlite3

    class SQLiteTestCase(unittest.TestCase, DefaultTestCase):

        format = 'sqlite'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('sqlite', 'test_atpy.db', verbose=False, overwrite=True)
            self.table_new = atpy.Table('sqlite', 'test_atpy.db', verbose=False)
            os.remove('test_atpy.db')

    class SQLiteTestCaseQuery(unittest.TestCase, DefaultTestCase):

        format = 'sqlite'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('sqlite', 'test_atpy.db', verbose=False, overwrite=True)
            self.table_new = atpy.Table('sqlite', 'test_atpy.db', verbose=False, query='select * from atpy_test')
            os.remove('test_atpy.db')

except:
    pass

try:
    import MySQLdb

    class MySQLTestCase(unittest.TestCase, DefaultTestCase):

        format = 'mysql'

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('mysql', db='python', overwrite=True, verbose=False, user=username, passwd=password)
            self.table_new = atpy.Table('mysql', db='python', verbose=False, user=username, passwd=password, table='atpy_test')

    class MySQLTestCaseQuery(unittest.TestCase, DefaultTestCase):

        format = 'mysql'

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('mysql', db='python', overwrite=True, verbose=False, user=username, passwd=password)
            self.table_new = atpy.Table('mysql', db='python', verbose=False, user=username, passwd=password, query='select * from atpy_test')

except:
    pass

try:
    import pgdb

    class PostGreSQLTestCase(unittest.TestCase, DefaultTestCase):

        format = 'postgres'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('postgres', database='python', overwrite=True, verbose=False, user=username, password=password)
            self.table_new = atpy.Table('postgres', database='python', verbose=False, user=username, password=password, table='atpy_test')

    class PostGreSQLTestCaseQuery(unittest.TestCase, DefaultTestCase):

        format = 'postgres'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype, shape)
            self.table_orig.write('postgres', database='python', overwrite=True, verbose=False, user=username, password=password)
            self.table_new = atpy.Table('postgres', database='python', verbose=False, user=username, password=password, query='select * from atpy_test')


except:
    pass

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unittest.main()
