from distutils import version
import warnings
import tempfile

vo_minimum_version = version.LooseVersion('0.3')

try:
    import vo.conesearch as vcone
    vo_installed = True
except:
    vo_installed = False

def _check_vo_installed():
    if not vo_installed:
        raise Exception("Cannot query the VO - vo " +  \
            vo_minimum_version.vstring + " or later required")


def read(self, catalog=None, ra=None, dec=None, radius=None, verb=1,
         pedantic=False, **kwargs):
    '''

    Query a VO catalog using the STScI vo module

    This docstring has been adapted from the STScI vo conesearch module:

        *catalog* [ None | string | VOSCatalog | list ]

            May be one of the following, in order from easiest to use to most
            control:

            - None: A database of conesearch catalogs is downloaded from
              STScI. The first catalog in the database to successfully return
              a result is used.

            - catalog name: A name in the database of conesearch catalogs at
              STScI is used. For a list of acceptable names, see
              vo_conesearch.list_catalogs().

            - url: The prefix of a url to a IVOA Cone Search Service. Must end
              in either ? or &.

            - A VOSCatalog instance: A specific catalog manually downloaded
              and selected from the database using the APIs in the
              STScI vo.vos_catalog module.

            - Any of the above 3 options combined in a list, in which case
              they are tried in order.

        *pedantic* [ bool ]
            When pedantic is True, raise an error when the returned VOTable
            file violates the spec, otherwise issue a warning.

        *ra* [ float ]
            A right-ascension in the ICRS coordinate system for the position
            of the center of the cone to search, given in decimal degrees.

        *dec* [ float ]
            A declination in the ICRS coordinate system for the position of
            the center of the cone to search, given in decimal degrees.

        *radius* [ float]
            The radius of the cone to search, given in decimal degrees.

        *verb* [ int ]
            Verbosity, 1, 2, or 3, indicating how many columns are to be
            returned in the resulting table. Support for this parameter by a
            Cone Search service implementation is optional. If the service
            supports the parameter, then when the value is 1, the response
            should include the bare minimum of columns that the provider
            considers useful in describing the returned objects. When the
            value is 3, the service should return all of the columns that are
            available for describing the objects. A value of 2 is intended for
            requesting a medium number of columns between the minimum and
            maximum (inclusive) that are considered by the provider to most
            typically useful to the user. When the verb parameter is not
            provided, the server should respond as if verb = 2. If the verb
            parameter is not supported by the service, the service should
            ignore the parameter and should always return the same columns for
            every request.

        Additional keyword arguments may be provided to pass along to the
        server. These arguments are specific to the particular catalog being
        queried.
    '''

    _check_vo_installed()

    self.reset()

    # Perform the cone search
    VOTable = vcone.conesearch(catalog_db=catalog, pedantic=pedantic,
                               ra=ra, dec=dec, sr=radius, verb=verb, **kwargs)

    # Write table to temporary file
    output = tempfile.NamedTemporaryFile()
    VOTable._votable.to_xml(output)
    output.flush()

    # Read it in using ATpy VO reader
    self.read(output.name, type='vo', verbose=False)

    # Check if table is empty
    if len(self) == 0:
        warnings.warn("Query returned no results, so the table will be empty")

    # Remove temporary file
    output.close()


def list_catalogs():

    _check_vo_installed()

    for catalog in vcone.list_catalogs():
        if "BROKEN" in catalog:
            continue
        print "%30s" % (catalog)
