# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_jgf_format.py

"""
Functions for reading and writing graph files in the graphit .jgf JSON format

This is a propitiatory format in which the graph meta-data, the nodes, edges
and their data dictionaries are stored in JSON format.
"""

import json
import logging

from graphit import __version__, __module__, Graph, GraphAxis
from graphit.graph_py2to3 import PY_PRIMITIVES, MAJOR_PY_VERSION
from graphit.graph_io.io_helpers import check_graphit_version, open_anything

__all__ = ['read_jgf', 'write_jgf']
logger = logging.getLogger(__module__)


def read_jgf(jgf_format, graph=None):
    """
    Read JSON graph format (.jgf)

    This is a propitiatory format in which the graph meta-data, the nodes,
    edges and their data dictionaries are stored in JSON format.

    Format description. Primary key/value pairs:
    * graph: Graph class meta-data. Serializes all class attributes of type
             int, float, bool, long, str or unicode.
    * nodes: Graph node identifiers (keys) and attributes (values)
    * edges: Graph enumerated edge identifiers
    * edge_attr: Graph edge attributes

    :param jgf_format:  JSON encoded graph data to parse
    :type jgf_format:   :py:str
    :param graph:       Graph object to import TGF data in
    :type graph:        :graphit:Graph

    :return:            Graph object
    :rtype:             Graph or GraphAxis object
    """

    # Try parsing the string using default Python json parser
    if isinstance(jgf_format, dict):
        parsed = jgf_format
    else:
        jgf_format = open_anything(jgf_format)
        try:
            parsed = json.load(jgf_format)
        except IOError:
            logger.error('Unable to decode JSON string')
            return

    # Check graphit version and format validity
    if not check_graphit_version(parsed.get('graphit_version')):
        return
    keywords = ['graph', 'nodes', 'edges', 'edge_attr']
    if not set(keywords).issubset(set(parsed.keys())):
        logger.error('JSON format does not contain required graph data')
        return

    # Determine graph class to use
    if not isinstance(graph, Graph):
        if parsed['graph'].get('root') is not None:
            graph = GraphAxis()
        else:
            graph = Graph()

    # Init graph meta-data attributes
    for key, value in parsed['graph'].items():
        setattr(graph, key, value)

    # Init graph nodes
    for node_key, node_value in parsed['nodes'].items():

        # JSON objects don't accept integers as dictionary keys
        # If graph.auto_nid equals True, course node_key to integer
        if graph.auto_nid:
            node_key = int(node_key)

        graph.nodes[node_key] = node_value

    # Init graph edges
    for edge_key, edge_value in parsed['edges'].items():
        edge_value = tuple(edge_value)
        graph.edges[edge_value] = parsed['edge_attr'].get(edge_key, {})

    # Set auto nid
    graph._set_auto_nid()

    return graph


def write_jgf(graph, indent=2, encoding="utf-8", **kwargs):
    """
    Write JSON graph format

    This is a propitiatory format in which the graph meta-data, the nodes,
    edges and their data dictionaries are stored in JSON format.

    Format description. Primary key/value pairs:
    * graph: Graph class meta-data. Serializes all class attributes of type
             int, float, bool, long, str or unicode.
    * nodes: Graph node identifiers (keys) and attributes (values)
    * edges: Graph enumerated edge identifiers
    * edge_attr: Graph edge attributes

    :param graph:    graph object to serialize
    :type graph:     Graph or GraphAxis object
    :param indent:   JSON indentation count
    :type indent:    :py:int
    :param encoding: JSON string encoding
    :type encoding:  :py:str
    :param kwargs:   additional data to be stored as file meta data
    :type kwargs:    :py:dic

    :return:         JSON encoded graph dictionary
    :rtype:          :py:str
    """

    # Init JSON format envelope
    json_format = {
        'graphit_version': '{0:d}.{1:d}'.format(*__version__),
        'graph': {},
        'nodes': {},
        'edges': {},
        'edge_attr': {}
    }

    # Update envelope with metadata
    for key, value in kwargs.items():
        if key not in json_format:
            json_format[key] = value

    # Store graph meta data
    for key in graph.__slots__:
        value = getattr(graph, key)
        if not key.startswith('_') and isinstance(value, PY_PRIMITIVES):
            json_format['graph'][key] = value

    # Update nodes with graph node attributes
    json_format['nodes'].update(graph.nodes.to_dict())

    # JSON cannot encode dictionaries with tuple as keys
    # Split the two up
    edgedata = graph.edges.to_dict()
    for i, edge in enumerate(edgedata):
        json_format['edges'][i] = edge
        if edgedata[edge]:
            json_format['edge_attr'][i] = edgedata[edge]

    if MAJOR_PY_VERSION == 3:
        return json.dumps(json_format, indent=indent)
    return json.dumps(json_format, indent=indent, encoding=encoding)
