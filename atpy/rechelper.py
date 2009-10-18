import numpy as np


def append_field(rec, data, dtype=None):
    newdtype = np.dtype(rec.dtype.descr + [dtype])
    newrec = np.recarray(rec.shape, dtype=newdtype)
    for field in rec.dtype.fields:
        newrec[field] = rec[field]
    newrec[dtype[0]] = data
    return newrec


def drop_fields(rec, names):

    names = set(names)

    newdtype = np.dtype([(name, rec.dtype[name]) for name in rec.dtype.names
                       if name not in names])

    newrec = np.recarray(rec.shape, dtype=newdtype)
    
    for field in newdtype.fields:
        newrec[field] = rec[field]

    return newrec
