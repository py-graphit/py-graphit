# -*- coding: utf-8 -*-

"""
file: graph_py2to3.py

Python 2.x and 3.x compatibility code
"""

import sys

MAJOR_PY_VERSION = sys.version_info[0]


# Library and function compatibility
if MAJOR_PY_VERSION < 3:
    from cStringIO import StringIO
    import urlparse
    import urllib2 as urllib
    import collections as colabc
else:
    from io import StringIO
    import urllib
    from urllib import parse as urlparse
    import collections.abc as colabc

# Type definitions
PY_DATASTORES = (dict, list, tuple, set)
if MAJOR_PY_VERSION < 3:
    PY_STRING = (str, unicode)
    PY_PRIMITIVES = (int, float, bool, long, str, unicode)
    PY_DATA_OBJECTS = (int, float, bool, long, str, unicode, dict, list, tuple, set)
else:
    PY_STRING = str
    PY_PRIMITIVES = (int, float, bool, str)
    PY_DATA_OBJECTS = (int, float, bool, str, dict, list, tuple, set)


def to_unicode(data, convert=True, encoding='utf-8'):
    """
    Convert all strings to unicode with `encoding`

    The actual conversion is only performed if `convert` equals True.
    This allows a user to decide if the `data` should be converted to unicode
    which will not always work for instance with the content of files. The
    later may be read as string or bytes but to Python are considered as string
    and could contain characters that cannot be converted or wrongly converted
    to unicode.

    :param data:     data to convert to unicode
    :param convert:  commence with conversion
    :type convert:   :py:bool
    :param encoding: unicode encoding
    :type encoding:  :py:str

    :return:         string encoded in unicode
    """

    if not convert:
        return data

    # Python 2.x, if type 'str' encode
    if MAJOR_PY_VERSION < 3:
        if isinstance(data, str):
            return unicode(data, encoding=encoding)
        return data

    # Python 3.x, strings are always unicode
    return data


def prepaire_data_dict(data):
    """
    Make a copy of the input data dictionary converting all non-unicode
    string to unicode if needed

    :param data:    input data
    :type data:     :py:dict

    :return:        sanitized data dictionary
    :rtype:         :py:dict
    """

    new_dict = {}
    for key, value in data.items():
        new_dict[to_unicode(key)] = to_unicode(value)

    return new_dict


def return_instance_type(data):
    for t in PY_DATA_OBJECTS:
        if isinstance(data, t):
            return t.__name__
