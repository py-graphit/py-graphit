# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_pgf_format.py

"""
Reading and writing graphs defined in Propitiatory Graph Format
(.pgf) a format specific to the graphit module.

Graph nodes, edges and adjacency are stored as plain python dictionaries
"""

import os
import pprint
import logging

from graphit import Graph, __module__

__all__ = ['read_graph', 'write_graph']
logger = logging.getLogger(__module__)


def write_graph(graph, path=os.path.join(os.getcwd(), 'graph.gpf')):
    """
    Export graph as Graph Python Format file

    GPF format is the modules own file format consisting out of a serialized
    nodes and edges dictionary.
    The format is feature rich wth good performance but is not portable.

    :param graph:        Graph object to export
    :type graph:         Graph instance
    :param path:         File path to write to
    :type path:          path as string

    :return: Graph instance
    """

    # Export graph as serialized Graph Python Format
    pp = pprint.PrettyPrinter(indent=2)
    with open(path, 'w') as output:

        # Export nodes as dictionary
        output.write('nodes = {0}\n'.format(pp.pformat(graph.nodes.dict())))

        # Export edges as dictionary
        output.write('edges = {0}\n'.format(pp.pformat(graph.edges.dict())))

    logger.info('Graph exported in GPF format to file: {0}'.format(path))


def read_graph(graph_file, graph=None):
    """
    Import graph from Graph Python Format file

    GPF format is the modules own file format consisting out of a serialized
    nodes and edges dictionary.
    The format is feature rich wth good performance but is not portable.

    :param graph_file:    File path to read from
    :type graph_file:     :py:str
    :param graph:         Graph object to import to or Graph by default
    :type graph:          :graphit:Graph

    :return:              Graph instance
    :rtype:               :graphit:Graph
    """

    if not graph:
        graph = Graph()

    # Import graph from serialized Graph Python Format
    with open(graph_file) as f:
        code = compile(f.read(), "GPF_file", 'exec')
        exec(code)

    return graph
