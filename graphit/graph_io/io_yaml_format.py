# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_yaml_format.py

"""
Functions for importing and exporting graphs in YAML format.
Relies on PyYAML.
"""

import logging

from graphit import __module__
from graphit.graph_io.io_pydata_format import read_pydata, write_pydata
from graphit.graph_io.io_helpers import open_anything
from graphit.graph_combinatorial.graph_split_join_operations import graph_join

logger = logging.getLogger(__module__)

try:
    import yaml
except ImportError:
    logger.exception('PyYAML package required')

__all__ = ['read_yaml', 'write_yaml']


def read_yaml(yaml_file, graph=None, **kwargs):
    """
    Parse (hierarchical) YAML data structure to a graph

    YAML files are parsed to a Python data structure that is converted
    to graph using the `read_pydata` mehtod.
    Additional keyword arguments (kwargs) are passed to `read_pydata`

    :param yaml_file:      yaml data to parse
    :type yaml_file:       File, string, stream or URL
    :param graph:          Graph object to import dictionary data in
    :type graph:           :graphit:Graph

    :return:               GraphAxis object
    :rtype:                :graphit:GraphAxis
    """

    # Try parsing the string using default Python yaml parser
    yaml_file = open_anything(yaml_file)
    try:
        yaml_file = yaml.safe_load(yaml_file)
    except IOError:
        logger.error('Unable to decode YAML string')
        return

    if not isinstance(yaml_file, list):
        yaml_file = [yaml_file]

    base_graph = read_pydata(yaml_file[0], graph=graph, **kwargs)

    for yaml_object in yaml_file[1:]:
        sub_graph = read_pydata(yaml_object)

        # If sub-graph root is of type 'root', connect children to base_graph
        root = sub_graph.getnodes(sub_graph.root)
        if root[sub_graph.key_tag] == 'root':
            links = [(base_graph.root, child) for child in root.children(return_nids=True)]
        else:
            links = [(base_graph.root, sub_graph.root)]

        graph_join(base_graph, sub_graph, links=links)

    return base_graph


def write_yaml(graph, default=None, include_root=False, allow_none=True):
    """
    Export a graph to a (nested) JSON structure

    Convert graph representation of the dictionary tree into JSON
    using a nested or flattened representation of the dictionary hierarchy.

    Dictionary keys and values are obtained from the node attributes using
    `key_tag` and `value_tag`.  The key_tag is set to graph
    key_tag by default.

    :param graph:           Graph object to export
    :type graph:            :graphit:GraphAxis
    :param default:         value to use when node value was not found using
                            value_tag.
    :type default:          mixed
    :param include_root:    Include the root node in the hierarchy
    :type include_root:     :py:bool
    :param allow_none:      allow None values in the output
    :type allow_none:       :py:bool

    :rtype:                 :py:yaml
    """

    return yaml.dump(write_pydata(graph, default=default, include_root=include_root, allow_none=allow_none))
