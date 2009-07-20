# NOTE: docstring is long and so only written once!
#       It is copied for the other routines

import numpy as np
import sqlhelper as sql


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

            *tid*: [ integer ]
                The ID of the table to read from the database (this is only
                required if there are more than one table in the database)

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

        if 'tid' in kwargs:
            tid = kwargs.pop('tid')
        else:
            tid = None

        # Erase existing content
        self.reset()

        connection, cursor = sql.connect_database(dbtype, *args, **kwargs)

        # If no table is requested, check that there is only one table

        table_names = sql.list_tables(cursor, dbtype)

        if tid==None:
            if len(table_names) == 1:
                tid = 1
            else:
                print "-"*56
                print " There is more than one table in the requested file"
                print " Please specify the table desired with the tid="
                print " argument. The available tables are:"
                print ""
                for tid in table_names:
                    print " tid=%i : %s" % (tid, table_names[tid])
                print "-"*56
                return

        table_name = table_names[tid]

        column_names, column_types = sql.column_info(cursor, dbtype, \
            table_name)

        cursor = connection.cursor()

        for i, column_name in enumerate(column_names):
            column_type = column_types[i]
            cursor.execute('select ' + sql.quote[dbtype] + column_name + \
                sql.quote[dbtype] + ' from ' + table_name)
            result = cursor.fetchall()
            self.add_column(column_name, \
                np.array(result, column_type).ravel())

        self.table_name = table_name

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
                raise Exception("Table already exists - use overwrite to \
                    replace existing table")

        # Create table
        sql.create_table(cursor, dbtype, table_name, self.names, self.types)

        # Insert row
        for i in range(self.__len__()):
            sql.insert_row(cursor, dbtype, table_name, \
                self.row(i, python_types=True))

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

        for tid in table_names:
            kwargs['tid'] = tid
            table = self._single_table_class()
            table.sql_read(dbtype, *args, **kwargs)
            self.tables.append(table)

    sql_read.__doc__ = SQLMethods.sql_read.__doc__

    def sql_write(self, dbtype, *args, **kwargs):

        for i, table in enumerate(self.tables):
            table.sql_write(dbtype, *args, **kwargs)

    sql_write.__doc__ = SQLMethods.sql_read.__doc__
