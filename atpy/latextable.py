import numpy as np


class LaTeXTable(object):

    def latex_write(self, filename):

        # Open file for writing
        f = file(filename, 'wb')

        for i in range(self.__len__()):

            line = ""

            for j, name in enumerate(self.names):
                if j > 0:
                    line += ' & '
                line += (("%" + self.format(name)) % self.data[name][i])

            line = line + " \\\\ \n"

            f.write(line)

        f.close()
