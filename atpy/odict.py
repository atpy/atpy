import numpy as np

class odict(object):

    def __init__(self):
        self.keys = []
        self.values = []

    def __setitem__(self, key, value):
        if type(key) == int:
            if key > len(self.keys) - 1:
                raise Exception("Element %i does not exist" % key)
            else:
                self.values[key] = value
        elif type(key) in [str, np.string_, unicode]:
            if key in self.keys:
                index = self.keys.index(key)
                self.values[index] = value
            else:
                self.keys.append(key)
                self.values.append(value)
        else:
            raise Exception("Wrong type for key: %s" % type(key))

    def __getitem__(self, key):
        if type(key) == int:
            return self.values[key]
        elif type(key) in [str, np.string_]:
            index = self.keys.index(key)
            return self.values[index]
        else:
            raise Exception("Wrong type for key: %s" % type(key))

    def __repr__(self):
        string = "{"
        for i, key in enumerate(self.keys):
            if i > 0:
                string += ", "
            string += "\n%s : %s" % (key, self.values[i])
        string += "\n}"
        return string

    def __contains__(self, key):
        return key in self.keys

    def pop(self, key):
        index = self.keys.index(key)
        self.keys.pop(index)
        self.values.pop(index)

    def __len__(self):
        return len(self.keys)

    def rename(self, oldkey, newkey):
        index = self.keys.index(oldkey)
        self.keys[index] = newkey
        return

    def insert(self, position, key, value):
        self.keys.insert(position, key)
        self.values.insert(position, value)
        return

    def __iter__(self):
        return iter(self.keys)
