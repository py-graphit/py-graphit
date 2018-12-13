# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_json_format.py

"""
Functions for importing and exporting JSON data into a graph data structure
"""

import logging
import json

from graphit import __module__
from graphit.graph_io.io_helpers import open_anything
from graphit.graph_io.io_pydata_format import read_pydata, write_pydata

__all__ = ['read_json', 'write_json']
logger = logging.getLogger(__module__)


def read_json(json_file, graph=None, **kwargs):
    """
    Parse (hierarchical) JSON data structure to a graph

    Use the default Python json parser to parse the JSON file to a dictionary
    followed by io_dict_format.read_pydata to parse to a graph structure.

    Additional keyword arguments (kwargs) are passed to `read_pydata`

    :param json_file:      json data to parse
    :type json_file:       File, string, stream or URL
    :param graph:          Graph object to import dictionary data in
    :type graph:           :graphit:Graph

    :return:               GraphAxis object
    :rtype:                :graphit:GraphAxis
    """

    # Try parsing the string using default Python json parser
    json_file = open_anything(json_file)
    try:
        json_file = json.load(json_file)
    except IOError:
        logger.error('Unable to decode JSON string')
        return

    return read_pydata(json_file, graph=graph, **kwargs)


def write_json(graph, default=None, include_root=False, allow_none=True, **kwrags):
    """
    Export a graph to a (nested) JSON structure

    Convert graph representation of the dictionary tree into JSON
    using a nested or flattened representation of the dictionary hierarchy.

    Dictionary keys and values are obtained from the node attributes using
    `key_tag` and `value_tag`.  The key_tag is set to graph
    key_tag by default.

    Additional keyword arguments (kwargs) are passed to json.dumps()

    :param graph:           Graph object to export
    :type graph:            :graphit:GraphAxis
    :param default:         value to use when node value was not found using
                            value_tag.
    :type default:          mixed
    :param include_root:    Include the root node in the hierarchy
    :type include_root:     :py:bool
    :param root_nid:        root node ID in graph hierarchy
    :param allow_none:      allow None values in the output
    :type allow_none:       :py:bool

    :rtype:                 :py:json
    """

    to_dict = write_pydata(graph, default=default, include_root=include_root, allow_none=allow_none, export_all=True)

    return json.dumps(to_dict, **kwrags)
