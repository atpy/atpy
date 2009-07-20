import numpy as np
import pkg_resources

# SQLite

try:
    import sqlite3
    sqlite3_installed = True
except:
    print "WARNING - sqlite3 required"
    print "          SQLite table reading/writing has been disabled"
    sqlite3_installed = False


def _check_sqlite3_installed():
    if not sqlite3_installed:
        raise Exception("Cannot read/write SQLite tables - sqlite3 required")

# SQLite

MySQLdb_minimum_version = "1.2.2"

try:
    pkg_resources.require('MySQL-python>=' + MySQLdb_minimum_version)
    import MySQLdb
    MySQLdb_installed = True
except:
    print "WARNING - MySQL-python " + MySQLdb_minimum_version + " or " + \
        "later required. MySQL table reading/writing has been disabled"
    MySQLdb_installed = False


def _check_MySQLdb_installed():
    if not MySQLdb_installed:
        raise Exception("Cannot read/write MySQL tables - MySQL-python " + \
            MySQLdb_minimum_version + " or later required")

 # SQLite

PyGreSQL_minimum_version = "3.8.1"

try:
    pkg_resources.require('PyGreSQL>=' + PyGreSQL_minimum_version)
    import pgdb
    PyGreSQL_installed = True
except:
    print "WARNING - PyGreSQL " + PyGreSQL_minimum_version + " or later " + \
        "required. PostGreSQL table reading/writing has been disabled"
    PyGreSQL_installed = False


def _check_PyGreSQL_installed():
    if not PyGreSQL_installed:
        raise Exception("Cannot read/write PostGreSQL tables - PyGreSQL " + \
            PyGreSQL_minimum_version + " or later required")

# Type conversion dictionary

type_dict = {}

type_dict[np.uint8] = "TINYINT"
type_dict[np.int16] = "SMALLINT"
type_dict[np.int32] = "INT"
type_dict[np.int64] = "BIGINT"

type_dict[np.float32] = "REAL"

type_dict[np.float64] = "DOUBLE PRECISION"

type_dict[np.str] = "TEXT"
type_dict[np.string_] = "TEXT"
type_dict[str] = "TEXT"

# Reverse type conversion dictionary

type_dict_rev = {}

type_dict_rev['smallint'] = np.int16
type_dict_rev['int2'] = np.int16

type_dict_rev['int'] = np.int32
type_dict_rev['int4'] = np.int32
type_dict_rev['INTEGER'] = np.int32

type_dict_rev['int8'] = np.int64

type_dict_rev['float4'] = np.float32
type_dict_rev['float8'] = np.float64
type_dict_rev['double'] = np.float64
type_dict_rev['FLOAT'] = np.float64
type_dict_rev['REAL'] = np.float64

type_dict_rev['text'] = np.str
type_dict_rev['TEXT'] = np.str
type_dict_rev['varchar'] = np.str
type_dict_rev['VARCHAR'] = np.str
type_dict_rev['BLOB'] = np.str

type_dict_rev['date'] = np.str


# Define symbol to use in insert statement

insert_symbol = {}
insert_symbol['sqlite'] = "?"
insert_symbol['mysql'] = "%s"
insert_symbol['postgres'] = "%s"

# Define quote symbol for column names

quote = {}
quote['sqlite'] = '`'
quote['mysql'] = '`'
quote['postgres'] = '"'


def numpy_type(sql_type):
    '''
    Returns the numpy type corresponding to an SQL type

    Required arguments:

        *sql_type*: [ string ]
            The SQL type to find the numpy type for
    '''
    sql_type = sql_type.split('(')[0]
    if not sql_type in type_dict_rev:
        raise Exception("need to define reverse type for " + str(sql_type))
    return type_dict_rev[sql_type]


def list_tables(cursor, dbtype):
    '''
    List all tables in a given SQL database

    Required Arguments:

        *cursor*: [ DB API cursor object ]
            A cursor for the current database in the DB API formalism

        *dbtype*: [ 'sqlite' | 'mysql' | 'postgres' ]
            The type of database
    '''
    tables = {}
    if dbtype=='sqlite':
        table_names = cursor.execute("select name from sqlite_master where \
            type = 'table'").fetchall()
        if len(table_names) == 1:
            table_names = table_names[0]
        for i, table_name in enumerate(table_names):
            if type(table_name) == tuple:
                table_name = table_name[0]
            tables[i + 1] = str(table_name.encode())
    elif dbtype=='mysql':
        cursor.execute('SHOW TABLES;')
        for i, table_name in enumerate(cursor):
            tables[i + 1] = str(table_name[0])
    elif dbtype=='postgres':
        cursor.execute("SELECT table_name FROM information_schema.tables \
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema');")
        for i, table_name in enumerate(cursor.fetchall()):
            tables[i + 1] = str(table_name[0])
    else:
        raise Exception('dbtype should be one of sqlite/mysql/postgres')
    return tables


def column_info(cursor, dbtype, table_name):
    '''
    List all columns in a given SQL table

    Required Arguments:

        *cursor*: [ DB API cursor object ]
            A cursor for the current database in the DB API formalism

        *dbtype*: [ 'sqlite' | 'mysql' | 'postgres' ]
            The type of database

        *table_name*: [ string ]
            The name of the table to get column information about
    '''
    names, types = [], []
    if dbtype=='sqlite':
        for column in cursor.execute('pragma table_info(' + \
            table_name + ')').fetchall():
            names.append(str(column[1]))
            types.append(numpy_type(column[2]))
    elif dbtype=='mysql':
        cursor.execute('DESCRIBE ' + table_name)
        for column in cursor:
            types.append(numpy_type(column[1]))
            names.append(str(column[0]))
    elif dbtype=='postgres':
        cursor.execute('SELECT * FROM ' + table_name + ' WHERE 1=0')
        for column in cursor.description:
            types.append(numpy_type(column[1]))
            names.append(str(column[0]))
    return names, types


def connect_database(dbtype, *args, **kwargs):
    '''
    Connect to a database and return a connection handle

    Required Arguments:

    *dbtype*: [ 'sqlite' | 'mysql' | 'postgres' ]
        The type of database

    All other arguments are passed to the relevant modules, specifically:
        - sqlite3.connect() for SQLite
        - MySQLdb.connect() for MySQL
        - pgdb.connect() for PostgreSQL
    '''
    if dbtype == 'sqlite':
        _check_sqlite3_installed()
        connection = sqlite3.connect(*args, **kwargs)
    elif dbtype == 'mysql':
        _check_MySQLdb_installed()
        connection = MySQLdb.connect(*args, **kwargs)
    elif dbtype == 'postgres':
        _check_PyGreSQL_installed()
        connection = pgdb.connect(*args, **kwargs)
    else:
        raise Exception('dbtype should be one of sqlite/mysql/postgres')
    cursor = connection.cursor()
    return connection, cursor


def drop_table(cursor, table_name):
    '''
    Drop a table form a given SQL database

    Required Arguments:

        *cursor*: [ DB API cursor object ]
            A cursor for the current database in the DB API formalism

        *table_name*: [ string ]
            The name of the table to get column information about
    '''
    cursor.execute('DROP TABLE ' + table_name + ';')
    return


def create_table(cursor, dbtype, table_name, column_names, column_types):
    '''
    Create a table in an SQL database

    Required Arguments:

        *cursor*: [ DB API cursor object ]
            A cursor for the current database in the DB API formalism

        *dbtype*: [ 'sqlite' | 'mysql' | 'postgres' ]
            The type of database

        *table_name*: [ string ]
            The name of the table to get column information about

        *column_names*: [ list of strings ]
            The names of all the columns

        *column_types*: [list of type objects ]
            The numpy types of all the columns
    '''

    query = 'create table ' + table_name + ' ('

    for i, column_name in enumerate(column_names):
        if i > 0:
            query += ", "
        column_type = type_dict[column_types[column_name]]
        query += quote[dbtype] + column_name + quote[dbtype] + " " + \
            column_type

    query += ")"

    cursor.execute(query)

    return


def insert_row(cursor, dbtype, table_name, row):
    '''
    Insert a row into an SQL database (assumes all columns are specified)

    Required Arguments:

        *cursor*: [ DB API cursor object ]
            A cursor for the current database in the DB API formalism

        *dbtype*: [ 'sqlite' | 'mysql' | 'postgres' ]
            The type of database

        *table_name*: [ string ]
            The name of the table to get column information about

        *row*: [ tuple ]
            A tuple containing all the values to insert into the row
    '''
    query = 'insert into ' + table_name + ' values ('
    query += (insert_symbol[dbtype] + ', ') * (len(row) - 1)
    query += insert_symbol[dbtype] + ")"
    cursor.execute(query, row)
    return
