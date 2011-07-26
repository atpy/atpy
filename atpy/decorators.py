import urllib2
import tempfile
import gzip
import bz2

from decorator import decorator


def auto_download_to_file(f):
    return decorator(_auto_download_to_file, f)


def _auto_download_to_file(read, table, filename, *args, **kwargs):

    if isinstance(filename, basestring):

        # Check whether filename is in fact a URL
        for protocol in ['http', 'ftp']:

            if filename.lower().startswith('%s://' % protocol):

                # Retrieve file
                req = urllib2.Request(filename)
                response = urllib2.urlopen(req)
                result = response.read()

                # Write it out to a temporary file
                output = tempfile.NamedTemporaryFile()
                output.write(result)
                output.flush()

                # Call read method
                return read(table, output.name, *args, **kwargs)

    # Otherwise just proceed as usual
    return read(table, filename, *args, **kwargs)


def auto_decompress_to_fileobj(f):
    return decorator(_auto_decompress_to_fileobj, f)


def _auto_decompress_to_fileobj(read, table, filename, *args, **kwargs):

    if isinstance(filename, basestring):

        # Read in first few characters from file to determine compression
        header = open(filename, 'rb').read(4)

        if header[:2] == '\x1f\x8b':  # gzip compression
            return read(table, gzip.GzipFile(filename), *args, **kwargs)
        elif header[:3] == 'BZh':  # bzip compression
            return read(table, bz2.BZ2File(filename), *args, **kwargs)
        else:
            return read(table, filename, *args, **kwargs)

    return read(table, filename, *args, **kwargs)


def auto_fileobj_to_file(f):
    return decorator(_auto_fileobj_to_file, f)


def _auto_fileobj_to_file(read, table, filename, *args, **kwargs):

    if hasattr(filename, 'read'):  # is a file object

        # Write it out to a temporary file
        output = tempfile.NamedTemporaryFile()
        output.write(filename.read())
        output.flush()

        # Update filename
        filename = output.name

    return read(table, filename, *args, **kwargs)
