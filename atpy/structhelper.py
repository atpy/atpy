import numpy as np
import numpy.ma as ma


def append_field(sta, data, dtype=None, position='undefined'):
    newdtype = sta.dtype.descr
    if position == 'undefined':
        newdtype.append(dtype)
    else:
        newdtype.insert(position, dtype)
    newdtype = np.dtype(newdtype)
    newsta = ma.empty(sta.shape, dtype=newdtype)
    for field in sta.dtype.fields:
        newsta[field] = sta[field]
    newsta[dtype[0]] = data
    return newsta

def drop_fields(sta, names):

    names = set(names)

    newdtype = np.dtype([(name, sta.dtype[name]) for name in sta.dtype.names
                       if name not in names])

    newsta = ma.empty(sta.shape, dtype=newdtype)
    
    for field in newdtype.fields:
        newsta[field] = sta[field]

    return newsta