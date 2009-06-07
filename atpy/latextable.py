from basetable import BaseTable
import numpy as np

class LaTeXTable(BaseTable):
        
    def write(self,filename):
        
        # Open file for writing
        f = file(filename,'wb')
        
        for i in range(self.__len__()):
            
            line = ""
            
            for j,name in enumerate(self.names):
                if j > 0: line += ' & '
                line += (("%"+self.format(name)) % self.array[name][i])
            
            line = line + " \\\\ \n"
            
            f.write(line)
            
        f.close()