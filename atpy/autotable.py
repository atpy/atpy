import warnings

def _determine_type(string, verbose):

    s = string.lower()

    extension = s.split('.')[-1]

    if extension in ['gz', 'bzip2', 'Z']:
        extension = s.split('.')[-2]

    if extension in ['fits', 'fit']:
        if verbose:
            print "Auto-detected input type: FITS table"
        table_type = 'fits'

    elif extension in ['xml', 'vot']:
        if verbose:
            print "Auto-detected input type: VO table"
        table_type = 'vo'

    elif extension in ['tbl', 'ipac']:
        if verbose:
            print "Auto-detected input type: IPAC table"
        table_type = 'ipac'

    elif s in ['sqlite', 'postgres', 'mysql']:
        if verbose:
            print "Auto-detected input type: SQL table"
        table_type = 'sql'

    else:
        raise Exception('Could not determine input type')

    return table_type


class AutoMethods(object):

    def read(self, *args, **kwargs):
        '''
        Read in a table or table set from a file/database.

        This method attempts to automatically guess the file/database format
        based on the arguments supplied. The type can be overridden by
        specifying type=string where string can be one of:

            * ``fits``
            * ``ipac``
            * ``sql``
            * ``vo``

        The arguments to supply to ``read()`` depend on the type of the input.
        For more information, see the help pages for the following methods:

           * ``fits_read``
           * ``ipac_read``
           * ``sql_read``
           * ``vo_read``
        '''

        if 'verbose' in kwargs:
            verbose = kwargs['verbose']
        else:
            verbose = True

        if 'type' in kwargs:
            table_type = kwargs.pop('type').lower()
        elif type(args[0]) == str:
            table_type = _determine_type(args[0], verbose)
        else:
            raise Exception('Could not determine input type')

        original_filters = warnings.filters[:]

        if verbose:
            warnings.simplefilter("always")
        else:
            warnings.simplefilter("ignore")

        try:

            if verbose:
                warnings.simplefilter("always")
            else:
                warnings.simplefilter("ignore")

            if table_type == 'fits':
                self.fits_read(*args, **kwargs)
            elif table_type == 'vo':
                self.vo_read(*args, **kwargs)
            elif table_type == 'ipac':
                self.ipac_read(*args, **kwargs)
            elif table_type == 'sql':
                self.sql_read(*args, **kwargs)
            else:
                raise Exception("Unknown table type: " + table_type)

        finally:
            warnings.filters = original_filters

        return

    def write(self, *args, **kwargs):
        '''
        Write out a table or table set to a file/database.

        This method attempts to automatically guess the file/database format
        based on the arguments supplied. The type can be overridden by
        specifying type=string where string can be one of:

            * ``fits``
            * ``ipac``
            * ``sql``
            * ``vo``

        The arguments to supply to ``write()`` depend on the type of the
        output. For more information, see the help pages for the following
        methods:

           * ``fits_write``
           * ``ipac_write``
           * ``sql_write``
           * ``vo_write``
        '''

        if 'verbose' in kwargs:
            verbose = kwargs.pop('verbose')
        else:
            verbose = True

        if 'type' in kwargs:
            table_type = kwargs['type'].lower()
        elif type(args[0]) == str:
            table_type = _determine_type(args[0], verbose)
        else:
            raise Exception('Could not determine input type')

        original_filters = warnings.filters[:]

        if verbose:
            warnings.simplefilter("always")
        else:
            warnings.simplefilter("ignore")

        try:

            if table_type == 'fits':
                self.fits_write(*args, **kwargs)
            elif table_type == 'vo':
                self.vo_write(*args, **kwargs)
            elif table_type == 'ipac':
                self.ipac_write(*args, **kwargs)
            elif table_type == 'sql':
                self.sql_write(*args, **kwargs)
            else:
                raise Exception("Unknown table type: " + table_type)

        finally:
            warnings.filters = original_filters

        return
