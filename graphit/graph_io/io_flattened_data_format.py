# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_flattened_data_format.py

"""
Functions for importing and exporting flattened (dot seperated) data structures
"""

import logging

from graphit import __module__
from graphit.graph_py2to3 import StringIO
from graphit.graph_exceptions import GraphitException
from graphit.graph_axis.graph_axis_class import GraphAxis
from graphit.graph_axis.graph_axis_methods import node_leaves
from graphit.graph_axis.graph_axis_mixin import NodeAxisTools

__all__ = ['read_flattened', 'write_flattened']

logger = logging.getLogger(__module__)


def read_flattened():

    pass


def write_flattened(graph, sep='.', default=None, allow_none=False, **kwargs):

    # No nodes, return empty dict
    if graph.empty():
        logging.info('Graph is empty: {0}'.format(repr(graph)))
        return {}

    # Graph should be of type GraphAxis with a root node nid defined
    if not isinstance(graph, GraphAxis):
        raise TypeError('Unsupported graph type {0}'.format(type(graph)))
    if graph.root is None:
        raise GraphitException('No graph root node defines')

    # Set current NodeTools aside and register new one
    curr_nt = graph.node_tools
    graph.origin.node_tools = NodeAxisTools

    # Create empty file buffer
    string_buffer = StringIO()

    value_tag = graph.value_tag
    for leaf in node_leaves(graph):
        node = graph.getnodes(leaf)
        value = node.get(value_tag, default=default)

        if value is None and not allow_none:
            continue

        path = '{0}{1}{2}\n'.format(node.path(sep=sep, **kwargs), sep, value)
        string_buffer.write(path)

    # Restore original NodeTools
    graph.origin.node_tools = curr_nt

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
