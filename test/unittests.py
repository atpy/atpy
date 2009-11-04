import unittest
import warnings
import os
import string
import random
import getpass

import atpy
import numpy as np

# Size of the test table
SIZE = 100

# SQL connection parameters
username = getpass.getuser()
password = "C2#uwQsk"


def random_int_array(dtype, n):
    n = n * np.iinfo(dtype).bits / 8
    s = "".join(chr(random.randrange(0, 256)) for i in xrange(n))
    return np.fromstring(s, dtype=dtype)


def random_float_array(dtype, n):
    if dtype == np.float32:
        n = n * 4
    else:
        n = n * 8
    s = "".join(chr(random.randrange(0, 256)) for i in xrange(n))
    array = np.fromstring(s, dtype=dtype)
    if np.sum(np.isnan(array)):
        array[np.isnan(array)] = random_float_array(dtype, np.sum(np.isnan(array)))
    return array

numpy_types = [np.bool, np.int8, np.int16, np.int32, np.int64, np.uint8, \
               np.uint16, np.uint32, np.uint64, np.float32, np.float64, \
               np.dtype('|S100')]


def random_int64(size):
    a0 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a1 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a2 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a3 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a = a0 + (a1<<16) + (a2 << 32) + (a3 << 48)
    return a.view(dtype=np.int64)


def random_uint64(size):
    print "calling random uint64"
    a0 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a1 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a2 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a3 = np.random.random_integers(0, 0xFFFF, size=size).astype(np.uint64)
    a = a0 + (a1<<16) + (a2 << 32) + (a3 << 48)
    return a


def random_generic(dtype, name, n):

    if 'int' in name:
        values = random_int_array(dtype, n)
    elif 'float' in name:
        values = random_float_array(dtype, n)
    elif 'bool' in name:
        values = np.random.random(n) > 0.5
    else:
        values = np.zeros((n, ), dtype=dtype)
        for i in range(n):
            s = ""
            for k in range(dtype.itemsize):
                s += random.choice(string.letters + string.digits)
            values[i] = s

    return values


def generate_table():

    table = atpy.Table(name='atpy_test')

    for dtype in numpy_types:

        try:
            name = dtype.__name__
        except:
            name = dtype.type.__name__

        values = random_generic(dtype, name, SIZE)

        table.add_column('col_'+name, values, dtype=dtype)

    return table


def generate_simple_table(dtype):

    table = atpy.Table(name='atpy_test')

    try:
        name = dtype.__name__
    except:
        name = dtype.type.__name__

    values = random_generic(dtype, name, SIZE)

    table.add_column('col_'+name, values, dtype=dtype)

    return table


class DefaultTestCase():

    def assertAlmostEqualSig(test, first, second, significant=7, msg=None):
        format = "%%.%ig" % significant
        if format % first <> format % second:
            raise test.failureException, \
            (msg or '%r != %r within %r significant digits' % (first, second, significant))

    def test_uint8(self):
        self.writeread(np.uint8)
        before, after = self.table_orig.data['col_uint8'], self.table_new.data['col_uint8']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_uint16(self):
        self.writeread(np.uint16)
        before, after = self.table_orig.data['col_uint16'], self.table_new.data['col_uint16']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_uint32(self):
        self.writeread(np.uint32)
        before, after = self.table_orig.data['col_uint32'], self.table_new.data['col_uint32']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_uint64(self):
        self.writeread(np.uint64)
        before, after = self.table_orig.data['col_uint64'], self.table_new.data['col_uint64']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_int8(self):
        self.writeread(np.int8)
        before, after = self.table_orig.data['col_int8'], self.table_new.data['col_int8']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_int16(self):
        self.writeread(np.int16)
        before, after = self.table_orig.data['col_int16'], self.table_new.data['col_int16']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_int32(self):
        self.writeread(np.int32)
        before, after = self.table_orig.data['col_int32'], self.table_new.data['col_int32']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_int64(self):
        self.writeread(np.int64)
        before, after = self.table_orig.data['col_int64'], self.table_new.data['col_int64']
        self.assertEqual(before.shape, after.shape)
        for i in range(len(self.table_orig)):
            self.assertEqual(before[i], after[i])

    def test_float32(self):
        self.writeread(np.float32)
        before, after = self.table_orig.data['col_float32'], self.table_new.data['col_float32']
        self.assertEqual(before.shape, after.shape)
        self.assertEqual(before.dtype.type, after.dtype.type)
        for i in range(len(self.table_orig)):
            if(np.isnan(before[i])):
                self.failUnless(np.isnan(after[i]))
            elif(np.isinf(before[i])):
                self.failUnless(np.isinf(after[i]))
            else:
                if self.format == 'mysql':
                    self.assertAlmostEqualSig(before[i], after[i], significant=5)
                if self.format == 'postgres':
                    self.assertAlmostEqualSig(before[i], after[i], significant=5)
                else:
                    self.assertEqual(before[i], after[i])

    def test_float64(self):
        self.writeread(np.float64)
        before, after = self.table_orig.data['col_float64'], self.table_new.data['col_float64']
        self.assertEqual(before.shape, after.shape)
        self.assertEqual(before.dtype.type, after.dtype.type)
        for i in range(len(self.table_orig)):
            if(np.isnan(before[i])):
                self.failUnless(np.isnan(after[i]))
            elif(np.isinf(before[i])):
                self.failUnless(np.isinf(after[i]))
            else:
                if self.format == 'mysql':
                    self.assertAlmostEqualSig(before[i], after[i], significant=12)
                elif self.format == 'postgres':
                        self.assertAlmostEqualSig(before[i], after[i], significant=12)
                else:
                    self.assertEqual(before[i], after[i])

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

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('test_atpy.fits', verbose=False, overwrite=True)
            self.table_new = atpy.Table('test_atpy.fits', verbose=False)
            os.remove('test_atpy.fits')

except:
    pass

try:
    import vo

    class VOTestCase(unittest.TestCase, DefaultTestCase):

        format = 'vo'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('test_atpy.xml', verbose=False)
            self.table_new = atpy.Table('test_atpy.xml', verbose=False)
            os.remove('test_atpy.xml')

except:
    pass


class IPACTestCase(unittest.TestCase, DefaultTestCase):

    format = 'ipac'

    def writeread(self, dtype):

        self.table_orig = generate_simple_table(dtype)
        self.table_orig.write('test_atpy.tbl', verbose=False, overwrite=True)
        self.table_new = atpy.Table('test_atpy.tbl', verbose=False)
        os.remove('test_atpy.tbl')

try:
    import sqlite3

    class SQLiteTestCase(unittest.TestCase, DefaultTestCase):

        format = 'sqlite'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('sqlite', 'test_atpy.db', verbose=False, overwrite=True)
            self.table_new = atpy.Table('sqlite', 'test_atpy.db', verbose=False)
            os.remove('test_atpy.db')

except:
    pass

try:
    import MySQLdb

    class MySQLTestCase(unittest.TestCase, DefaultTestCase):

        format = 'mysql'

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('mysql', db='python', overwrite=True, verbose=False, user=username, passwd=password)
            self.table_new = atpy.Table('mysql', db='python', verbose=False, user=username, passwd=password, table='atpy_test')

    class MySQLTestCaseQuery(unittest.TestCase, DefaultTestCase):

        format = 'mysql'

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('mysql', db='python', overwrite=True, verbose=False, user=username, passwd=password)
            self.table_new = atpy.Table('mysql', db='python', verbose=False, user=username, passwd=password, table='atpy_test', query='select * from atpy_test')

except:
    pass

try:
    import pgdb

    class PostGreSQLTestCase(unittest.TestCase, DefaultTestCase):

        format = 'postgres'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('postgres', database='python', overwrite=True, verbose=False, user=username, password=password)
            self.table_new = atpy.Table('postgres', database='python', verbose=False, user=username, password=password, table='atpy_test')

    class PostGreSQLTestCaseQuery(unittest.TestCase, DefaultTestCase):

        format = 'postgres'

        test_uint64 = None # unsupported

        def writeread(self, dtype):

            self.table_orig = generate_simple_table(dtype)
            self.table_orig.write('postgres', database='python', overwrite=True, verbose=False, user=username, password=password)
            self.table_new = atpy.Table('postgres', database='python', verbose=False, user=username, password=password, table='atpy_test', query='select * from atpy_test')


except:
    pass

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unittest.main()
