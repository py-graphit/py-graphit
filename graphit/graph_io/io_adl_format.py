# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_pgf_format.py

"""
Reading and writing graphs as adjacency lists (.adl)

Adjacency lists are a simple textual representation of node identifiers
and their linkage (adjacency) to one another.

The graph with edges a-b, a-c, d-e can be represented as the following
adjacency list (anything following the # in a line is a comment):

     a b c # source target target
     d e
"""

import logging

from graphit import Graph, __module__
from graphit.graph_io.io_helpers import open_anything
from graphit.graph_py2to3 import StringIO

__all__ = ['read_adl', 'write_adl']
logger = logging.getLogger(__module__)


def read_adl(adl_file, graph=None):
    """
    Construct a graph from a adjacency list (ADL)

    .. note:: the directionality of the graph is not defined explicitly
              in the adjacency list and thus depends on the graph.directional
              attribute that is False (undirectional) by default.

    :param adl_file:        ADL graph data.
    :type adl_file:         File, string, stream or URL
    :param graph:           Graph object to import ADL data in
    :type graph:            :graphit:Graph

    :return:                Graph object
    :rtype:                 :graphit:Graph
    """

    if graph is None:
        graph = Graph()

    # ADL node labels are unique, turn off auto_nid
    graph.data['auto_nid'] = False

    adl_file = open_anything(adl_file)
    for line in adl_file.readlines():

        # Ignore comments (# ..)
        line = line.split('#')[0].strip()
        if line:

            nodes = line.split()
            graph.add_nodes(nodes)
            if len(nodes) > 1:
                graph.add_edges([(nodes[0], n) for n in nodes[1:]])

    return graph


def write_adl(graph):
    """
    Export graph as adjacency list (ADL)

    .. note:: This format does not store graph, node, or edge data.

    :param graph:   Graph object to export
    :type graph:    :graphit:Graph

    :return:        Graph object
    :rtype:         :py:str
    """

    # Create empty file buffer
    string_buffer = StringIO()

    # Process nodes with adjacency
    adjacency = graph.adjacency()
    adj_done = []
    for node, adj in adjacency.items():
        if len(adj):
            string_buffer.write('{0} {1}\n'.format(node, ' '.join([str(n) for n in adj])))
            adj_done.extend(adj)

    # Process isolated nodes
    for node, adj in adjacency.items():
        if not len(adj) and node not in adj_done:
            string_buffer.write('{0}\n'.format(node))

    logger.info('Graph {0} exported in Adjacency list format'.format(repr(graph)))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
