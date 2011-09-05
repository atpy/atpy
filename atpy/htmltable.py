import numpy as np


def write(self, filename):

    f = open(filename, 'wb')

    f.write("<html>\n")
    f.write("  <head>\n")
    f.write("  </head>\n")
    f.write("  <body>\n")
    f.write("    <table border=1>\n")

    f.write("    <tr>\n")
    for name in self.names:
        f.write("      <td><b>%s</b></td>\n" % name)
    f.write("    </tr>\n")

    f.write("    <tr>\n")
    for name in self.names:
        f.write("      <td><i>%s</i></td>\n" % self.columns[name].unit)
    f.write("    </tr>\n")

    for i in range(self.__len__()):

        f.write("    <tr>\n")

        for name in self.names:

            if self.columns[name].dtype == np.uint64:
                item = (("%" + self.columns[name].format) % long(self.data[name][i]))
            else:
                item = (("%" + self.columns[name].format) % self.data[name][i])

            f.write("      <td>%s</td>\n" % item.strip())

        f.write("    </tr>\n")

    f.write("    </table>\n")
    f.write("  </body>\n")
    f.write("  </html>\n")

    f.close()
