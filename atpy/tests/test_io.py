from __future__ import division

import unittest
import string
import random
import sys
import tempfile

import numpy as np
np.seterr(all='ignore')

import pytest
from astropy.tests.helper import pytest
from astropy.utils.misc import NumpyRNGContext

from .. import Table

# Size of the test table
shape = (100, )
shape_vector = (100, 10)


def random_int_array(dtype, shape):
    random.seed('integer')
    n = np.product(shape)
    n = n * np.iinfo(dtype).bits // 8
    if sys.version_info[0] > 2:
        s = bytes([random.randrange(0, 256) for i in range(n)])
    else:
        s = "".join(chr(random.randrange(0, 256)) for i in range(n))
    return np.fromstring(s, dtype=dtype).reshape(shape)


def random_float_array(dtype, shape):
    random.seed('float')
    n = np.product(shape)
    if dtype == np.float32:
        n = n * 4
    else:
        n = n * 8
    if sys.version_info[0] > 2:
        s = bytes([random.randrange(0, 256) for i in range(n)])
    else:
        s = "".join(chr(random.randrange(0, 256)) for i in range(n))
    array = np.fromstring(s, dtype=dtype)
    if np.sum(np.isnan(array)):
        array[np.isnan(array)] = random_float_array(dtype, array[np.isnan(array)].shape)
    return array.reshape(shape)


numpy_types = [np.bool, np.int8, np.int16, np.int32, np.int64, np.uint8,
               np.uint16, np.uint32, np.uint64, np.float32, np.float64,
               np.dtype('|S100')]


def random_generic(dtype, name, shape):

    random.seed('generic')

    if 'int' in name:
        values = random_int_array(dtype, shape)
    elif 'float' in name:
        values = random_float_array(dtype, shape)
    elif 'bool' in name:
        with NumpyRNGContext(12345):
            values = np.random.random(shape) > 0.5
    else:
        values = np.zeros(shape, dtype=dtype)
        for i in range(shape[0]):
            s = ""
            for k in range(dtype.itemsize):
                s += random.choice(string.ascii_letters + string.digits)
            values[i] = s

    return values


def generate_simple_table(dtype, shape):

    table = Table(name='atpy_test')

    try:
        name = dtype.__name__
    except:
        name = dtype.type.__name__

    if name == 'bytes_':
        name = 'string_'

    values = random_generic(dtype, name, shape)

    table.add_column('col_' + name, values, dtype=dtype)

    return table


class ColumnsDefaultTestCase():

    def test_bool(self):
        self.generic_test(np.bool_)

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
            t = Table()
            t.add_empty_column('a', dtype, shape=shape)
            t.add_empty_column('b', dtype)
            t.add_empty_column('c', dtype)
        except:
            self.fail(sys.exc_info()[1])


class EmptyVectorColumnsTestCase(unittest.TestCase, ColumnsDefaultTestCase):

    def generic_test(self, dtype):
        try:
            t = Table()
            t.add_empty_column('a', dtype, shape=shape_vector)
            t.add_empty_column('b', dtype)
            t.add_empty_column('c', dtype, shape=shape_vector)
        except:
            self.fail(sys.exc_info()[1])


class DefaultTestCase():

    def assertAlmostEqualSig(test, first, second, significant=7, msg=None):
        ratio = first / second
        if np.abs(ratio - 1.) > 10. ** (-significant + 1):
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

    def test_bool(self):
        self.integer_test(np.bool_)

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
        for i in range(len(self.table_orig)):
            if type(before[i]) == type(after[i]):
                self.assertEqual(before[i], after[i])
            elif type(before[i]) == np.bytes_:
                self.assertEqual(before[i], after[i].encode('utf-8'))
            else:
                self.assertEqual(before[i].encode('utf-8'), after[i])


class TestFITS(unittest.TestCase, DefaultTestCase):

    format = 'fits'

    test_uint64 = None  # unsupported

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.fits')

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestFITSVector(unittest.TestCase, DefaultTestCase):

    format = 'fits'

    test_string = None  # unsupported
    test_uint64 = None  # unsupported

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.fits')

        self.table_orig = generate_simple_table(dtype, shape_vector)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestHDF5(unittest.TestCase, DefaultTestCase):

    format = 'hdf5'

    def writeread(self, dtype):

        try:
            import h5py
        except ImportError:
            pytest.skip()

        filename = tempfile.mktemp(suffix='.hdf5')

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestHDF5Vector(unittest.TestCase, DefaultTestCase):

    format = 'hdf5'

    test_string = None  # unsupported

    def writeread(self, dtype):

        try:
            import h5py
        except ImportError:
            pytest.skip()

        filename = tempfile.mktemp(suffix='.hdf5')

        self.table_orig = generate_simple_table(dtype, shape_vector)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestVO(unittest.TestCase, DefaultTestCase):

    format = 'vo'

    test_uint64 = None  # unsupported

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.xml')

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestVOVector(unittest.TestCase, DefaultTestCase):

    format = 'vo'

    test_string = None  # unsupported
    test_uint64 = None  # unsupported

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.xml')

        self.table_orig = generate_simple_table(dtype, shape_vector)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestIPAC(unittest.TestCase, DefaultTestCase):

    format = 'ipac'

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.tbl')

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write(filename, verbose=False, overwrite=True)
        self.table_new = Table(filename, verbose=False)


class TestSQLite(unittest.TestCase, DefaultTestCase):

    format = 'sqlite'

    test_uint64 = None  # unsupported

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.db')

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('sqlite', filename, verbose=False, overwrite=True)
        self.table_new = Table('sqlite', filename, verbose=False)


class TestSQLiteQuery(unittest.TestCase, DefaultTestCase):

    format = 'sqlite'

    test_uint64 = None  # unsupported

    def writeread(self, dtype):

        filename = tempfile.mktemp(suffix='.db')

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('sqlite', filename, verbose=False, overwrite=True)
        self.table_new = Table('sqlite', filename, verbose=False, query='select * from atpy_test')


# SQL connection parameters
USERNAME = "testuser"
PASSWORD = "testpassword"


class MySQLTestCase(unittest.TestCase, DefaultTestCase):

    format = 'mysql'

    test_uint64 = None # unsupported

    def writeread(self, dtype):

        try:
            import MySQLdb
        except ImportError:
            pytest.skip()

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('mysql', db='python', overwrite=True, verbose=False, user=USERNAME, passwd=PASSWORD)
        self.table_new = Table('mysql', db='python', verbose=False, user=USERNAME, passwd=PASSWORD, table='atpy_test')


class MySQLTestCaseQuery(unittest.TestCase, DefaultTestCase):

    format = 'mysql'

    test_uint8 = None # unsupported
    test_uint16 = None # unsupported
    test_uint32 = None # unsupported
    test_uint64 = None # unsupported

    def writeread(self, dtype):

        try:
            import MySQLdb
        except ImportError:
            pytest.skip()

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('mysql', db='python', overwrite=True, verbose=False, user=USERNAME, passwd=PASSWORD)
        self.table_new = Table('mysql', db='python', verbose=False, user=USERNAME, passwd=PASSWORD, query='select * from atpy_test')


class PostGreSQLTestCase(unittest.TestCase, DefaultTestCase):

    format = 'postgres'

    test_uint64 = None # unsupported

    def writeread(self, dtype):

        try:
            import pgdb
        except ImportError:
            pytest.skip()

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('postgres', database='python', overwrite=True, verbose=False, user=USERNAME, password=PASSWORD)
        self.table_new = Table('postgres', database='python', verbose=False, user=USERNAME, password=PASSWORD, table='atpy_test')


class PostGreSQLTestCaseQuery(unittest.TestCase, DefaultTestCase):

    format = 'postgres'

    test_uint64 = None # unsupported

    def writeread(self, dtype):

        try:
            import pgdb
        except ImportError:
            pytest.skip()

        self.table_orig = generate_simple_table(dtype, shape)
        self.table_orig.write('postgres', database='python', overwrite=True, verbose=False, user=USERNAME, password=PASSWORD)
        self.table_new = Table('postgres', database='python', verbose=False, user=USERNAME, password=PASSWORD, query='select * from atpy_test')
