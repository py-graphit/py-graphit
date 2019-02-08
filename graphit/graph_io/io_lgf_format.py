# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_lgf_format.py

"""
Functions for reading and writing graphs defined in the LEMONG Graph Format

Reference:  http://lemon.cs.elte.hu/pub/doc/1.3/a00002.html

Citation:   Balázs Dezső, Alpár Jüttner, Péter Kovács "LEMON – an Open Source
            C++ Graph Template Library" (2011) Electronic Notes in Theoretical
            Computer Science, 264(5), 23-45
"""

import logging
import time
import shlex

from graphit import Graph, version, __module__
from graphit.graph_py2to3 import StringIO, PY_STRING
from graphit.graph_io.io_helpers import coarse_type, open_anything

logger = logging.getLogger(__module__)

__all__ = ['read_lgf', 'write_lgf']


class ExportTable(object):
    """
    Export nodes or edges in tabular format
    """

    def __init__(self, storage, header=None, column_gap=' '):
        """

        :param storage:    node/edge attribute source
        :param header:     labels to export
        :type header:      :py:list
        :param column_gap: characters used as spacing between table columns
        :type column_gap:  :py:str
        """

        self._storage = storage
        self._header = header
        self._row_formatter = None
        self._column_gap = column_gap

        self.parse_header()

    @property
    def header(self):
        """
        :return: header string or None of no header
        """

        if len(self._header):
            return self._column_gap.join(self._header)
        return None

    def parse_header(self):
        """
        Build list of header labels based on all nodes/edges attribute keys.
        Build a row formatter for export of all node/edge value with padding
        defined by the header label length
        """

        header = set()
        for node_attr in self._storage.values():
            header.update(set(node_attr.keys()))

        self._header = sorted(header)
        if '_id' in self._header:
            self._header.remove('_id')

        format_string = []
        for label in self._header:
            format_string.append('{:<' + str(len(label)) + '}')

        self._row_formatter = self._column_gap.join(format_string)

    def export_row(self, attributes, default='-'):
        """
        Export node/edge attributes as single table row

        :param attributes: node/edge attributes
        :type attributes:  :py:dict
        :param default:    default value to export if header label not found

        :return:           table row
        :rtype:            :py:str
        """

        attr = [attributes.get(label, default) for label in self._header]
        attr = ['"{0}"'.format(value) if isinstance(value, PY_STRING) and not value == default
                else value for value in attr]
        return self._row_formatter.format(*attr)


def split_line(line):
    """
    Split LGF file line related to node/edge/arc maps into columns
    corresponding to the column headers or the attributes.

    :param line: line to split
    :type line:  :py:str

    :rtype:      :py:list
    """

    return [coarse_type(n) for n in shlex.split(line)]


def parse_nodes(line, header, graph, **kwargs):
    """
    Parse LGF 'nodes'

    :param line:    node identifiers and attributes
    :type line:     :py:str
    :param header:  attribute column headers
    :type header:   :py:list
    :param graph:   graph to add nodes to
    :type graph:    :graphit:Graph
    :param kwargs:  additional keyword arguments
    :type kwargs:   :py:dict
    """

    line = split_line(line)
    d = dict(zip(header, line))

    graph.add_node(line[0], **d)


def parse_edges(line, header, graph, directed=None, did_parse_nodes=True, **kwargs):
    """
    Parse LGF 'edges'

    Edges are undirectional in LGF
    By default nodes are added before edges/arc in a LGF document.
    If they are reversed then the `did_parse_nodes` will be False and the
    nodes corresponding to the edges will be added. Node attributes will the be
    updated afterwards.

    :param line:            edge node identifiers and attributes
    :type line:             :py:str
    :param header:          attribute column headers
    :type header:           :py:list
    :param directed:        add edge in directed or undirected mode
    :type directed:         :py:bool
    :param did_parse_nodes: if nodes not yet parsed, create nodes from edges
    :type did_parse_nodes:  :py:bool
    :param graph:           graph to add edges to
    :type graph:            :graphit:Graph
    :param kwargs:          additional keyword arguments
    :type kwargs:           :py:dict
    """

    line = split_line(line)
    d = dict(zip(header, line[2:]))

    graph.add_edge(line[0], line[1], directed=directed, node_from_edge=not did_parse_nodes, **d)


def parse_arcs(line, header, graph, **kwargs):
    """
    Parse LGF 'arcs'

    Arcs are directional edges.
    Uses parse_edges with directed attribute set to True

    :param line:    arc node identifiers and attributes
    :type line:     :py:str
    :param header:  attribute column headers
    :type header:   :py:list
    :param graph:   graph to add edges to
    :type graph:    :graphit:Graph
    :param kwargs:  additional keyword arguments
    :type kwargs:   :py:dict
    """

    parse_edges(line, header, graph, directed=True, **kwargs)


def read_lgf(lgf, graph=None):
    """
    Read graph in LEMON Graph Format (LGF)

    :param lgf:             LGF graph data.
    :type lgf:              File, string, stream or URL
    :param graph:           Graph object to import LGF data in
    :type graph:            :graphit:Graph

    :return:                Graph object
    :rtype:                 :graphit:Graph
    """

    lgf_file = open_anything(lgf)
    if not isinstance(graph, Graph):
        graph = Graph()

    # LGF node and edge labels are unique, turn off auto_nid
    graph.data.auto_nid = False

    parser = None
    header = None
    did_parse_nodes = False
    is_directed = False
    for line in lgf_file.readlines():
        line = line.strip()

        # Skip empty lines and comment lines
        if not len(line) or line.startswith('#'):
            parser = None
            continue

        # Define parser
        if line.startswith('@') or parser is None:
            if 'nodes' in line:
                parser = parse_nodes
                did_parse_nodes = True
            elif line.startswith('@edges'):
                parser = parse_edges
            elif line.startswith('@arcs'):
                parser = parse_arcs
                is_directed = True
            elif line.startswith('@attributes'):
                logging.warning('Not importing LGF @attributes. Graph attributes not supported by graphit')
            header = None
            continue

        # Immediately after parser definition, parse table column headers
        if header is None:
            header = split_line(line)
            continue

        parser(line, header, graph, did_parse_nodes=did_parse_nodes)

    # Set graph to 'directed' if arcs where parsed
    if is_directed:
        graph.directed = True

    return graph


def write_lgf(graph):
    """
    Write graph in LEMON Graph Format (LGF)

    :param lgf:             LGF graph data.
    :type lgf:              File, string, stream or URL
    :param graph:           Graph object to import LGF data in
    :type graph:            :graphit:Graph

    :return:                Graph object
    :rtype:                 :graphit:Graph
    """

    # Define node and edge data tags to export
    key_tag = graph.data.key_tag

    # Create empty file buffer
    string_buffer = StringIO()

    # Export meta-data
    string_buffer.write('# Graphit graph exported in LEMON Graph Format\n')
    string_buffer.write('# Graphit version: {0}, date: {1}\n'.format(version(), time.ctime()))

    # Export nodes
    if len(graph.nodes):
        string_buffer.write('\n@nodes\n')

        table = ExportTable(graph.nodes)
        string_buffer.write('id  {0}\n'.format(table.header))

        for node, attr in graph.nodes.items():
            string_buffer.write('{0}  {1}\n'.format(node, table.export_row(attr)))

    # Export edges
    if len(graph.edges):
        string_buffer.write('\n@argcs\n' if graph.directed else '\n@edges\n')

        table = ExportTable(graph.edges)
        string_buffer.write('      {0}\n'.format(table.header or '_'))

        for edge, attr in graph.edges.items():
            string_buffer.write('{0}  {1}  {2}\n'.format(edge[0], edge[1], table.export_row(attr)))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
