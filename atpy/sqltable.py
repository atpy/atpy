# NOTE: docstring is long and so only written once!
#       It is copied for the other routines

import warnings

import numpy as np
import sqlhelper as sql

from exceptions import TableException, ExistingTableException

invalid = {}
invalid[np.uint8] = np.iinfo(np.uint8).max
invalid[np.uint16] = np.iinfo(np.uint16).max
invalid[np.uint32] = np.iinfo(np.uint32).max
invalid[np.uint64] = np.iinfo(np.int64).max
invalid[np.int8] = np.iinfo(np.int8).max
invalid[np.int16] = np.iinfo(np.int16).max
invalid[np.int32] = np.iinfo(np.int32).max
invalid[np.int64] = np.iinfo(np.int64).max
invalid[np.float32] = np.float32(np.nan)
invalid[np.float64] = np.float64(np.nan)


class SQLMethods(object):
    '''
    Class for working with reading and writing tables in databases.
    '''

    def sql_read(self, dbtype, *args, **kwargs):
        '''
        Required Arguments:

            *dbtype*: [ 'sqlite' | 'mysql' | 'postgres' ]
                The SQL database type

        Optional arguments (only for Table.read() class):

            *table*: [ string ]
                The name of the table to read from the database (this is only
                required if there are more than one table in the database)

            *query*: [ string ]
                An arbitrary SQL query to construct a table from. This can be
                any valid SQL command provided that the result is a single
                table.

        The remaining arguments depend on the database type:

        * SQLite:

            Arguments are passed to sqlite3.connect(). For a full list of
            available arguments, see the help page for sqlite3.connect(). The
            main arguments are listed below.

            Required arguments:

                *dbname*: [ string ]
                    The name of the database file

        * MySQL:

            Arguments are passed to MySQLdb.connect(). For a full list of
            available arguments, see the documentation for MySQLdb. The main
            arguments are listed below.

            Optional arguments:

                *host*: [ string ]
                    The host to connect to (default is localhost)

                *user*: [ string ]
                    The user to conenct as (default is current user)

                *passwd*: [ string ]
                    The user password (default is blank)

                *db*: [ string ]
                    The name of the database to connect to (no default)

                *port* [ integer ]
                    The port to connect to (default is 3306)

        * PostGreSQL:

            Arguments are passed to pgdb.connect(). For a full list of
            available arguments, see the help page for pgdb.connect(). The
            main arguments are listed below.

            *host*: [ string ]
                The host to connect to (default is localhost)

            *user*: [ string ]
                The user to conenct as (default is current user)

            *password*: [ string ]
                The user password (default is blank)

            *database*: [ string ]
                The name of the database to connect to (no default)
        '''

        if 'table' in kwargs:
            table = kwargs.pop('table')
        else:
            table = None

        if 'verbose' in kwargs:
            verbose = kwargs.pop('verbose')
        else:
            verbose = True

        if 'query' in kwargs:
            query = kwargs.pop('query')
        else:
            query = None

        # Erase existing content
        self.reset()

        connection, cursor = sql.connect_database(dbtype, *args, **kwargs)

        # If no table is requested, check that there is only one table

        table_names = sql.list_tables(cursor, dbtype)

        if table==None:
            if len(table_names) == 1:
                table_name = table_names.keys()[0]
            else:
                raise TableException(table_names, 'table')
        else:
            table_name = table_names[table]

        # Find overall names and types for the table
        column_names, column_types, primary_keys = sql.column_info(cursor, dbtype, \
            table_name)

        if query:

            # Execute the query
            cursor.execute(query)

            column_types_dict = dict(zip(column_names, column_types))

            # Override column names and types
            column_names, column_types = sql.column_info_desc(dbtype, cursor.description, column_types_dict)

        else:

            cursor = connection.cursor()

            cursor.execute('select * from ' + table_name)

        results = cursor.fetchall()

        if results:
            results = np.rec.fromrecords(list(results), \
                            names = column_names)
        else:
            raise Exception("SQL query did not return any records")

        for i, column in enumerate(results.dtype.names):
            if column_types[i] in invalid:
                null = invalid[column_types[i]]
                results[column][np.equal(results[column], None)] = null
            else:
                null = 'None'

            self.add_column(column, results[column], dtype=column_types[i], null=null)

        self.table_name = table_name

        # Set primary key if present
        if len(primary_keys) == 1:
            self.set_primary_key(primary_keys[0])
        elif len(primary_keys) > 1:
            warnings.warn("ATpy does not yet support multiple primary keys in a single table - ignoring primary key information")

    def sql_write(self, dbtype, *args, **kwargs):

        self._raise_vector_columns()

        # Check if table overwrite is requested
        if 'overwrite' in kwargs:
            overwrite = kwargs.pop('overwrite')
        else:
            overwrite = False

        # Open the connection
        connection, cursor = sql.connect_database(dbtype, *args, **kwargs)

        # Check that table name is set
        if not self.table_name:
            raise Exception("Table name is not set")
        else:
            table_name = self.table_name

        # Check that table name is ok
        # todo

        # lowercase because pgsql automatically converts
        # table names to lower case

        # Check if table already exists

        existing_tables = sql.list_tables(cursor, dbtype).values()
        if table_name in existing_tables or \
            table_name.lower() in existing_tables:
            if overwrite:
                sql.drop_table(cursor, table_name)
            else:
                raise ExistingTableException()

        # Create table
        columns = [(name, self.columns[name].dtype.type) \
                                            for name in self.names]
        sql.create_table(cursor, dbtype, table_name, columns, primary_key=self._primary_key)


        # Insert row
        float_column = [self.columns[name].dtype.type in [np.float32, np.float64] for name in self.names]

        for i in range(self.__len__()):
            row = []
            row_orig = self.row(i, python_types=True)
            for j, name in enumerate(self.names):
                item = row_orig[j]
                if (float_column[j] and np.isnan(item)) or item == self.columns[name].null:
                    item = None
                row.append(item)
            row = tuple(row)

            sql.insert_row(cursor, dbtype, table_name, row)

        # Close connection
        connection.commit()
        cursor.close()

    sql_write.__doc__ = sql_read.__doc__


class SQLSetMethods(object):

    def sql_read(self, dbtype, *args, **kwargs):

        self.tables = []

        connection, cursor = sql.connect_database(dbtype, *args, **kwargs)
        table_names = sql.list_tables(cursor, dbtype)
        cursor.close()

        for table in table_names:
            kwargs['table'] = table
            table = self._single_table_class()
            table.sql_read(dbtype, *args, **kwargs)
            self.tables.append(table)

    sql_read.__doc__ = SQLMethods.sql_read.__doc__

    def sql_write(self, dbtype, *args, **kwargs):

        for i, table in enumerate(self.tables):
            table.sql_write(dbtype, *args, **kwargs)

    sql_write.__doc__ = SQLMethods.sql_read.__doc__
