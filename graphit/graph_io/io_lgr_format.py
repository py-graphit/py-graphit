# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_gml_format.py

"""
Reading and writing graphs in LEDA format (.gw, .lgr).

The Library of Efficient Data types and Algorithms (LEDA) is a propitiatory
licensed software library providing C++ implementations of a broad variety of
algorithms for graph theory and computational geometry.

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

The LEDA graph format is a simple and a fast format always separated in a
header, nodes and edges section. The header always starts with LEDA.GRAPH
followed by the data type for node and edge data as string, int, float or
boolean or 'void' if no data defined. The fourth line described directionality
of the graph as directed (-1) or undirected (-2).
The nodes section starts with the number of nodes followed by an ordered list
of node labels (between |{}|) that are sequentially number starting from 1.
The node labels are converted to the respective types as indicated in the
header section.
The edge section is similar to nodes but list for each edge the source and
target nodes following the sequential number of the nodes, reversal number
(not used) and edge data label (between |{}|).
"""

import logging

from graphit import __module__, Graph
from graphit.graph_exceptions import GraphitException
from graphit.graph_py2to3 import StringIO
from graphit.graph_io.io_helpers import open_anything

logger = logging.getLogger(__module__)
data_types = {'string': str, 'int': int, 'bool': bool, 'float': float}

__all__ = ['read_lgr', 'write_lgr']


def read_lgr(lgr, graph=None, edge_label='label'):
    """
    Read graph in LEDA format

    Nodes are added to the graph using a unique ID or with the node data
    as label depending if the graph.data.auto_nid is True or False.
    Edge data is added to the edge attributes using `edge_label` as key.
    The data types for both nodes and edges is set according to the
    specifications in the LEDA header as either string, int, float or bool.

    :param lgr:             LEDA graph data.
    :type lgr:              File, string, stream or URL
    :param graph:           Graph object to import LEDA data in
    :type graph:            :graphit:Graph
    :param edge_label:      edge data label name
    :type edge_label:       :py:str

    :return:                Graph object
    :rtype:                 :graphit:Graph
    :raises:                TypeError if node/edge type conversion failed
                            GraphitException in case of malformed LEDA file
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

    # Node and edge data types and graph directionality
    node_type = data_types.get(header[1])
    edge_type = data_types.get(header[2])
    graph.directed = int(header[3]) == -1

    # Parse LEDA nodes
    node_mapping = {}
    for i, node in enumerate(nodes[1:], start=1):
        data = node.strip('|{}|') or None
        if node_type and data:
            data = node_type(data)
        nid = graph.add_node(data)
        node_mapping[i] = nid

    # Parse LEDA edges
    for edge in edges[1:]:
        try:
            source, target, reversal, label = edge.split()
        except ValueError:
            raise GraphitException('Too few fields in LEDA edge {0}'.format(edge))

        attr = {edge_label: label.strip('|{}|') or None}
        if edge_type and attr[edge_label]:
            attr[edge_label] = edge_type(attr[edge_label])
        graph.add_edge(node_mapping[int(source)], node_mapping[int(target)], **attr)

    return graph


def write_lgr(graph, node_key=None, edge_key=None, node_data_type='void', edge_data_type='void'):
    """
    Export a graph to an LGR data format

    The LEDA format allows for export of only one node or edge data type
    (as: |{data type}|). For nodes this is usually the node label and for
    edges any arbitrary data key,value pair. In both cases the data type
    is required to be of either: string, int, float or bool.

    Nodes and edges are exported by iterating over them using `iternodes`
    and `iteredges`. Iteration uses the graphit Object Relations Mapper (ORM)
    allowing full control over the data export by overriding the `get`
    method globally in the 'NodeTools' or 'EdgeTools' classes or using custom
    classes registered with the ORM.
    Data returned by the `get` method will be serialized regardless the return
    type.

    The node and edge data types are registered globally in the LENA file using
    `node_data_type` and `edge_data_type` set to 'void' (no data) by default.

    :param graph:           Graph to export
    :type graph:            :graphit:Graph
    :param node_key:        key name of node data to export
    :type node_key:         :py:str
    :param edge_key:        key name of edge data to export
    :type edge_key:         :py:str
    :param node_data_type:  primitive data type of exported node data
    :type node_data_type:   :py:str
    :param edge_data_type:  primitive data type of exported edge data
    :type edge_data_type:   :py:str

    :return:                Graph exported as LGR format
    :rtype:                 :py:str
    :raises:                GraphitException
    """

    # Default node_key to graph.data.key_tag
    if node_key is None:
        node_key = graph.data.key_tag

    # If export of node/edge data corresponding data types need to be defined
    if (node_key is not None and node_data_type == 'void') or (edge_key is not None and edge_data_type == 'void'):
        raise GraphitException('Define node_data_type and/or edge_data_type')

    # Create empty file buffer
    string_buffer = StringIO()

    # Print header
    string_buffer.write('#header section\nLEDA.GRAPH\n{0}\n{1}\n'.format(node_data_type, edge_data_type))
    string_buffer.write('{0}\n'.format(-1 if graph.directed else -2))

    # Print nodes
    string_buffer.write('#nodes section\n{0}\n'.format(len(graph.nodes)))
    node_mapping = {}
    for i, node in enumerate(graph.iternodes(), start=1):
        string_buffer.write('|{{{0}}}|\n'.format(str(node.get(node_key, default=''))))
        node_mapping[node.nid] = i

    # Print edges
    string_buffer.write('#edges section\n{0}\n'.format(len(graph.edges)))
    for edge in graph.iteredges():
        source, target = edge.nid
        string_buffer.write('{0} {1} 0 |{{{2}}}|\n'.format(node_mapping[source], node_mapping[target],
                                                           str(edge.get(edge_key, default=''))))

    logger.info('Graph {0} exported in LEDA format'.format(repr(graph)))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
