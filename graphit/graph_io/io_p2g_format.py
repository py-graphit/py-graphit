# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_pgf_format.py

"""
Reading and writing graphs defined in P2G Graph Format (.p2g) used for
representing metabolic pathways from the KEGG database.

A file that describes a uniquely labeled graph (with extension ".gr") format
looks like the following:

name
3 4
a
1 2
b

c
0 2

"name" is simply a description of what the graph corresponds to. The second
line displays the number of nodes and number of edges, respectively.
This sample graph contains three nodes labeled "a", "b", and "c". The rest of
the graph contains two lines for each node. The first line for a node contains
the node label.
After the declaration of the node label, the out-edges of that node in the
graph are provided. For instance, "a" is linked to nodes 1 and 2, which are
labeled "b" and "c", while the node labeled "b" has no outgoing edges.
Observe that node labeled "c" has an outgoing edge to itself.
Indeed, self-loops are allowed. Node index starts from 0.
"""

import logging

from graphit import Graph, __module__
from graphit.graph_exceptions import GraphitException
from graphit.graph_io.io_helpers import open_anything
from graphit.graph_py2to3 import StringIO

__all__ = ['read_p2g', 'write_p2g']
logger = logging.getLogger(__module__)


def read_p2g(p2g_file, graph=None):
    """
    Read graph in P2G format

    :param p2g_file:      P2G data to parse
    :type p2g_file:       File, string, stream or URL
    :param graph:         Graph object to import to or Graph by default
    :type graph:          :graphit:Graph

    :return:              Graph instance
    :rtype:               :graphit:Graph
    """

    if not graph:
        graph = Graph()

    # P2G graphs are directed
    graph.directed = True

    graph_name = None
    graph_layout = None
    curr_node = None
    nodes = {}
    p2g_file = open_anything(p2g_file)
    for i, line in enumerate(p2g_file.readlines()):

        line = line.strip()
        if line:

            # Parse p2g graph name (first line)
            sline = line.split()
            if not graph_name:
                graph_name = line
                continue

            # Parse number of nodes and edges (second line)
            elif not graph_layout:
                try:
                    graph_layout = map(int, sline)
                except ValueError:
                    raise GraphitException('P2G import error: line {0} - {1}'.format(i, line))
                continue

            # Parse nodes and edges
            if len(sline) == 1:
                nodes[line] = []
                curr_node = line
            elif len(sline) == 2:
                try:
                    nodes[curr_node] = map(int, sline)
                except ValueError:
                    raise GraphitException('P2G import error: malformed edge on line {0} - {1}'.format(i, line))
            else:
                raise GraphitException('P2G import error: line {0} - {1}'.format(i, line))

    graph.data['name'] = graph_name

    # Add nodes
    mapped_nodes = graph.add_nodes(nodes.keys())

    # Add edges
    for i, nid in enumerate(nodes.keys()):
        for e in nodes[nid]:
            if e < len(mapped_nodes):
                graph.add_edge(mapped_nodes[i], mapped_nodes[e])
            else:
                raise GraphitException('P2G import error: edge node index {0} not in graph'.format(e))

    if len(nodes) != graph_layout[0] or (len(graph.edges)) != graph_layout[1]:
        logging.warning('P2G import warning: declared number of nodes and edges {0}-{1} does not match {2}-{3}'.format(
            graph_layout[0], graph_layout[1], len(nodes), len(graph.edges)))

    return graph


def write_p2g(graph, graph_name_label='name'):
    """
    Export a graphit graph to P2G format

    :param graph:            Graph object to export
    :type graph:             :graphit:Graph
    :param graph_name_label: graph.data attribute label for the graph name
    :type graph_name_label:  :py:str

    :return:                 P2G graph representation
    :rtype:                  :py:str
    """

    # Create empty file buffer
    string_buffer = StringIO()

    # Write graph meta-data
    string_buffer.write('{0}\n'.format(graph.data.get(graph_name_label, 'graph')))
    string_buffer.write('{0} {1}\n'.format(len(graph.nodes), len(graph.edges)))

    # Write nodes and edges
    key_tag = graph.data['key_tag']
    nodes = sorted(graph.nodes.keys())
    for node in nodes:
        string_buffer.write('{0}\n'.format(graph[node].get(key_tag)))
        string_buffer.write('{0}\n'.format(' '.join([str(nodes.index(n)) for n in graph.adjacency[node]])))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()