import numpy as np


def append_field(sta, data, dtype=None, position=None):
    newdtype = sta.dtype.descr
    if np.equal(position,None):
        newdtype.append(dtype)
    else:
        newdtype.insert(position, dtype)
    newdtype = np.dtype(newdtype)
    newsta = np.empty(sta.shape, dtype=newdtype)
    for field in sta.dtype.fields:
        newsta[field] = sta[field]
    newsta[dtype[0]] = data
    return newsta

def drop_fields(sta, names):

    names = set(names)

    newdtype = np.dtype([(name, sta.dtype[name]) for name in sta.dtype.names
                       if name not in names])

    newsta = np.empty(sta.shape, dtype=newdtype)
    
    for field in newdtype.fields:
        newsta[field] = sta[field]

    return newsta