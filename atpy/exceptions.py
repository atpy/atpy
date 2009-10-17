class ExistingTableException(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return "Table already exists - use overwrite to replace existing table"


class TableException(Exception):

    def __init__(self, tables, arg):
        self.tables = tables
        self.arg = arg

    def __str__(self):

        table_list = ""
        for table in self.tables:

            if type(table) == int:
                table_list += "    " + self.arg + \
                    "=%i : %s\n" % (table, self.tables[table])
            elif type(table) == str:
                table_list += "    " + self.arg + \
                    "=%s\n" % table
            else:
                raise Exception("Unexpected table index type: %s" %
                                                            str(type(table)))

        message = "There is more than one table in the requested file. " + \
            "Please specify the table desired with the " + self.arg + \
            "= argument. The available tables are:\n\n" + table_list

        return message


class VectorException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "This table contains vector columns:\n\n" + \
        self.value + "\n\n" + \
        "but the output format selected does not. Remove these " + \
        "columns using the remove_columns() method and try again."
