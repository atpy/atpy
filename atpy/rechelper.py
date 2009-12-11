import numpy as np


def append_field(rec, data, dtype=None, position='undefined'):
    newdtype = rec.dtype.descr
    if position == 'undefined':
        newdtype.append(dtype)
    else:
        newdtype.insert(position, dtype)
    newdtype = np.dtype(newdtype)
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
