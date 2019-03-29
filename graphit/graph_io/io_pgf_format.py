# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_pgf_format.py

"""
Reading and writing graphs defined in Propitiatory Graph Format (.pgf) a
format specific to the graphit module.

PGF stores graphit graph data as plain text python dictionaries or as
serialized byte stream using the Python `pickle` module. Graphit graphs can
contain any hashable Python object as node (not just integers and strings).
Storing a graph by "Pickling" it is probably the best way of representing
arbitrary hashable data types.
Both storage options are feature rich but not portable as they are (so far)
only supported by graphit.
"""

import pprint
import logging
import ast

from graphit import Graph, __module__
from graphit.graph_exceptions import GraphitException
from graphit.graph_io.io_helpers import open_anything
from graphit.graph_py2to3 import StringIO

try:
    import cPickle as pickle
except ImportError:
    import pickle

__all__ = ['read_pgf', 'write_pgf']
logger = logging.getLogger(__module__)


def read_pgf(pgf_file, graph=None, pickle_graph=False):
    """
    Import graph from Graph Python Format file

    PGF format is the modules own file format consisting of a serialized
    graph data, nodes and edges dictionaries. Import either as plain text
    serialized dictionary or pickled graph object.
    The format is feature rich with good performance but is not portable.

    :param pgf_file:      PGF data to parse
    :type pgf_file:       File, string, stream or URL
    :param graph:         Graph object to import to or Graph by default
    :type graph:          :graphit:Graph
    :param pickle_graph:  PGF format is a pickled graph
    :type pickle_graph:   :py:bool

    :return:              Graph instance
    :rtype:               :graphit:Graph
    """

    # Unpickle pickled PGF format
    if pickle_graph:
        pgf_file = open_anything(pgf_file, mode='rb')
        pgraph = pickle.load(pgf_file)

        # Transfer data from unpickled graph to graph if defined
        if graph:
            graph.origin.nodes, graph.origin.edges, graph.origin.adjacency, graph.origin.data = graph.storagedriver(
                pgraph.nodes, pgraph.edges, pgraph.data)
            return graph
        return pgraph

    pgf_file = open_anything(pgf_file)

    # Import graph from serialized Graph Python Format
    if graph is None:
        graph = Graph()
    elif not isinstance(graph, Graph):
        raise GraphitException('Unsupported graph type {0}'.format(type(graph)))

    pgf_eval = ast.literal_eval(pgf_file.read())
    if not isinstance(pgf_eval, dict):
        raise GraphitException('Invalid PGF file format')

    missing_data = [d for d in pgf_file if d not in ('data', 'nodes', 'edges')]
    if missing_data:
        raise GraphitException('Invalid PGF file format, missing required attributes: {0}'.format(
            ','.join(missing_data)))

    graph.origin.nodes, graph.origin.edges, graph.origin.adjacency, graph.origin.data = graph.storagedriver(
        pgf_eval['nodes'], pgf_eval['edges'], pgf_eval['data'])

    return graph


def write_pgf(graph, pickle_graph=False):
    """
    Export graph as Graph Python Format file

    PGF format is the modules own file format consisting of a serialized
    graph data, nodes and edges dictionaries. Exports either as plain text
    serialized dictionary or pickled graph object.
    The format is feature rich with good performance but is not portable.

    :param graph:        Graph object to export
    :type graph:         :graphit:Graph
    :param pickle_graph: serialize the Graph using Python pickle
    :type pickle_graph:  :py:bool

    :return:             Graph in GPF graph representation
    :rtype:              :py:str
    """

    # Pickle or not
    if pickle_graph:
        return pickle.dumps(graph)

    # Export graph as serialized Graph Python Format
    pp = pprint.PrettyPrinter(indent=2)
    string_buffer = StringIO()
    string_buffer.write('{')

    # Export graph data dictionary
    string_buffer.write('"data": {0},\n'.format(pp.pformat(graph.data.to_dict())))

    # Export nodes as dictionary
    string_buffer.write('"nodes": {0},\n'.format(pp.pformat(graph.nodes.to_dict())))

    # Export edges as dictionary
    string_buffer.write('"edges": {0},\n'.format(pp.pformat(graph.edges.to_dict())))
    string_buffer.write('}')

    logger.info('Graph {0} exported in PGF format'.format(repr(graph)))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
