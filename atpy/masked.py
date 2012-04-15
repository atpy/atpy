import os
import warnings

from ConfigParser import SafeConfigParser

__masked__ = False


def set_masked_default(choice):
    'Set whether tables should be masked or not by default (True or False)'
    global __masked__
    __masked__ = choice

filename = os.path.expanduser('~/.atpyrc')
config = SafeConfigParser()
config.read(filename)
if config.has_option('general', 'masked_default'):
    if config.getboolean('general', 'masked_default'):
        warnings.warn(".atpyrc file found - masked arrays are ON by default")
        set_masked_default(True)
    else:
        warnings.warn(".atpyrc file found - masked arrays are OFF by default")
        set_masked_default(False)
