# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_gml_format.py

"""
Reading and writing graphs in LEDA format (.gw, .lgr).

LEDA is a C++ class library for efficient data types and algorithms.

Specifications:
    http://www.algorithmic-solutions.info/leda_guide/graphs/leda_native_graph_fileformat.html

Example:

    #header section
    LEDA.GRAPH
    string
    int
    -1
    #nodes section
    5
    |{v1}|
    |{v2}|
    |{v3}|
    |{v4}|
    |{v5}|

    #edges section
    7
    1 2 0 |{4}|
    1 3 0 |{3}|
    2 3 0 |{2}|
    3 4 0 |{3}|
    3 5 0 |{7}|
    4 5 0 |{6}|
    5 1 0 |{1}|
"""

import logging

from graphit import __module__, Graph
from graphit.graph_exceptions import GraphitException
from graphit.graph_py2to3 import StringIO
from graphit.graph_io.io_helpers import coarse_type, open_anything

logger = logging.getLogger(__module__)

__all__ = ['read_lgr', 'write_lgr']


def read_lgr(lgr, graph=None):
    """
    Read graph in LEDA format

    :param lgr:             LEDA graph data.
    :type lgr:              File, string, stream or URL
    :param graph:           Graph object to import LEDA data in
    :type graph:            :graphit:Graph

    :return:                Graph object
    :rtype:                 :graphit:Graph
    """

    # User defined or default Graph object
    if graph is None:
        graph = Graph()
    elif not isinstance(graph, Graph):
        raise GraphitException('Unsupported graph type {0}'.format(type(graph)))

    # Parse LEDA file
    lgr_file = open_anything(lgr)
    header = []
    nodes = []
    edges = []
    container = header
    for line in lgr_file.readlines():
        line = line.strip()

        if line:
            if line.startswith('#header'):
                container = header
                continue
            if line.startswith('#nodes'):
                container = nodes
                continue
            if line.startswith('#edges'):
                container = edges
                continue

            container.append(line)

    # Parse LEDA header
    if not header[0] == 'LEDA.GRAPH':
        raise GraphitException('File is not a valid LEDA graph format')

    graph.directed = int(header[3]) == -1

    # Parse LEDA nodes
    node_mapping = {}
    for i, node in enumerate(nodes[1:], start=1):
        nid = graph.add_node(node.strip('|{}|'))
        node_mapping[i] = nid

    # Parse LEDA edges
    for edge in edges[1:]:
        try:
            source, target, reversal, label = edge.split()
        except ValueError:
            raise GraphitException('Too few fields in LEDA edge {0}'.format(edge))

        attr = {}
        label = label.strip('|{}|')
        if label:
            attr['label'] = coarse_type(label)
        graph.add_edge(node_mapping[int(source)], node_mapping[int(target)], **attr)

    return graph


def write_lgr(graph):
    """
    Export a graph to an LGR data format

    :param graph:       Graph to export
    :type graph:        :graphit:Graph

    :return:            Graph exported as LGR format
    :rtype:             :py:str
    """

    # Create empty file buffer
    string_buffer = StringIO()

    # Print header
    string_buffer.write('#header section\nLEDA.GRAPH\nstring\nint\n')
    string_buffer.write('{0}\n'.format(-1 if graph.directed else -2))

    # Print nodes
    string_buffer.write('#nodes section\n{0}\n'.format(len(graph.nodes)))
    node_mapping = {}
    for i, node in enumerate(graph.iternodes(), start=1):
        string_buffer.write('|{{{0}}}|\n'.format(node.get(graph.data.key_tag, default='')))
        node_mapping[node.nid] = i

    # Print edges
    string_buffer.write('#edges section\n{0}\n'.format(len(graph.edges)))
    for edge in graph.iteredges():
        source, target = edge.nid
        string_buffer.write('{0} {1} 0 |{{{2}}}|\n'.format(node_mapping[source], node_mapping[target],
                            ' '.join([str(n) for n in edge.edges[edge.nid].values()])))

    logger.info('Graph {0} exported in LEDA format'.format(repr(graph)))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
