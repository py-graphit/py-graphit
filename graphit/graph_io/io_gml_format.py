# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_gml_format.py

"""
Functions for exporting and importing graphs to and from graph modelling
language (GML) format as described in the online documentation:

    https://en.wikipedia.org/wiki/Graph_Modelling_Language
    http://www.fim.uni-passau.de/index.php?id=17297&L=1
"""

import logging
import shlex

from itertools import izip_longest

from graphit import __module__, Graph
from graphit.graph_mixin import NodeTools, EdgeTools
from graphit.graph_py2to3 import StringIO, PY_PRIMITIVES, PY_STRING
from graphit.graph_io.io_helpers import coarse_type, open_anything, StreamReader

logger = logging.getLogger(__module__)

gml_syntax_arguments = ('node', 'edge', 'graph', 'id', 'source', 'target', 'directed')

__all__ = ['read_gml']


class Record(object):
    """
    GML format block data store

    Parses GML format '[]' enclosed data blocks of the type:

        block name [ key value key value ..]

    The records form an intermediate data representation before
    building a graphit Graph out of them
    """

    def __init__(self, gml_stream, name=None):
        """
        Implement class __init__

        :param gml_stream:  GML file as stream reader class
        :type gml_stream:   :graphit:StreamReader:
        :param name:        data block name
        :type name:         :py:str
        """

        self.name = name
        self.attr = []
        self.rec = []

        self.parse_block(gml_stream)

    def __repr__(self):
        """
        Implement class __repr__

        :return: String representation of the class for testing
        """

        return '<Record: {0}. {1} children, {2} attributes>'.format(self.name, len(self.rec), len(self.attr))

    def __iter__(self):
        """
        Implement class __iter__

        :return: Iterate over child Record instances
        """

        for child_record in self.rec:
            yield(child_record)

    @staticmethod
    def parse_args(line, n=2, fillvalue=None):
        """
        Parse GML arguments as key, value pairs.

        Uses shlex to split arguments in a line followed by parsing to
        Python primary types. The argument list is then split in tuples
        of length `n` (key,value) with None added in case of argument
        lists of uneven length.

        :param line:      argument line to parse
        :type line:       :py:str
        :param n:         split argument list in groups of `n`
        :type n:          :py:int
        :param fillvalue: missing value

        :return:          GML arguments as list of tuples
        :rtype:           :py:list
        """

        split = shlex.split(line)
        split = [coarse_type(a) for a in split]

        args = [iter(split)] * n
        return list(izip_longest(*args, fillvalue=fillvalue))

    def parse_block(self, gml_stream):
        """
        Parse one GML data block using the StreamReader

        :param gml_stream:  GML file as stream reader class
        :type gml_stream:   :graphit:StreamReader
        """

        parse = True
        while parse or gml_stream.has_more:

            # Parser lines between GML block delimiters ([])
            line, char = gml_stream.read_upto_char(('[', ']', '\n'), keep=False)
            if char:

                line = line.strip() if line else ''

                # Lines starting with '#' are comments
                if line.startswith('#'):
                    continue

                # Reached new block start delimiter, append new Record as child
                if char == '[':
                    self.rec.append(Record(gml_stream, name=line))

                # Reached block end delimiter, parse last arguments and return
                elif char == ']':
                    self.attr.extend(self.parse_args(line))
                    return

                # Parse block arguments as key,value pairs
                else:
                    self.attr.extend(self.parse_args(line))

            else:
                parse = False

    def to_dict(self, return_dict):

        attr_to_dict = dict(self.attr)
        if len(attr_to_dict) != len(self.attr):
            attr_to_dict = self.attr

        if len(attr_to_dict):
            if isinstance(attr_to_dict, list):
                return_dict[self.name] = attr_to_dict
            else:
                return_dict.update(attr_to_dict)

        # Store child dicts as list if any of the record names are identical
        # else store as dictionary
        names = [r.name for r in self.rec if r.name not in gml_syntax_arguments]
        to_list = len(names) != len(set(names))

        list_col = []
        for child_rec in self.rec:
            if child_rec.name in names:
                rec = child_rec.to_dict({})

                if to_list:
                    list_col.append({child_rec.name: rec})
                else:
                    return_dict[child_rec.name] = rec

        if to_list:
            return list_col

        return return_dict


class GMLTools(object):
    """
    Node and edge attribute GML serialize methods.
    """

    def serialize(self, attr, string_buffer, indent=0, class_name=None):
        """
        Main serialize method exporting an attribute record calling
        dedicated serializers for dictionaries, lists, tuples or
        primitive types.

        :param attr:          attribute to export
        :param string_buffer: StringIO buffer to write to
        :type string_buffer:  :py:StringIO
        :param indent:        indentation level
        :type indent:         :py:int
        :param class_name:    record name
        :type class_name:     :py:str
        """

        if class_name:
            string_buffer.write('{0}{1} [\n'.format(' ' * indent, class_name))
            indent += 2

        if isinstance(attr, dict):
            self.export_dict(attr, string_buffer, indent=indent)
        elif isinstance(attr, list):
            self.export_list(attr, string_buffer, indent=indent)
        elif isinstance(attr, tuple) and len(attr) == 2:
            self.export_primitive(attr[0], attr[1], string_buffer, indent=indent)

        if class_name:
            string_buffer.write('{0}]\n'.format(' ' * (indent - 2)))

    @staticmethod
    def export_primitive(key, value, string_buffer, indent=0):
        """
        Export Python primitive types to GML.
        Strings are double quoted and booleans are 0 or 1

        :param key:           attribute name
        :type key:            :py:str
        :param value:         attribute value
        :type value:          :py:bool, :py:str, :py:int, py:float
        :param string_buffer: StringIO buffer to write to
        :type string_buffer:  :py:StringIO
        :param indent:        indentation level
        :type indent:         :py:int
        """

        # Do not export graphit internal attributes
        if key in ['_id']:
            return

        if isinstance(value, PY_STRING):
            value = '"{0}"'.format(value)
        elif isinstance(value, bool):
            value = 0 if value is False else 1
        string_buffer.write('{0}{1} {2}\n'.format(' ' * indent, key, value))

    def export_list(self, attr, string_buffer, indent=0):
        """
        Export Python list to GML.

        :param attr:          list to export
        :type attr:           :py:list
        :param string_buffer: StringIO buffer to write to
        :type string_buffer:  :py:StringIO
        :param indent:        indentation level
        :type indent:         :py:int
        """

        for item in attr:
            self.serialize(item, string_buffer, indent=indent)

    def export_dict(self, attr, string_buffer, indent=0):
        """
        Export Python dict to GML.

        :param attr:          dictionary to export
        :type attr:           :py:dict
        :param string_buffer: StringIO buffer to write to
        :type string_buffer:  :py:StringIO
        :param indent:        indentation level
        :type indent:         :py:int
        """

        # Serialize primary attributes
        primary_attr = [key for key, value in attr.items() if isinstance(value, PY_PRIMITIVES)]

        for key in primary_attr:
            self.export_primitive(key, attr[key], string_buffer, indent=indent)

        for key, value in attr.items():
            if key not in primary_attr:
                self.serialize(value, string_buffer, indent=indent, class_name=key)


def build_nodes(graph, record):
    """
    Add nodes to graphit Graph based on GML node records

    :param graph:   graphit Graph to add nodes to
    :type graph:    :graphit:Graph
    :param record:  intermediate GML record hierarchy containing nodes
    :type record:   :Record:

    :return:        Graph with nodes added
    :rtype:         :graphit:Graph
    """

    if record.name == 'node':
        nid = None
        for attr in record.attr:
            if attr[0] == 'id':
                nid = attr[1]
                break

        if nid is not None:
            graph.add_node(nid, **record.to_dict({}))
        else:
            logging.error("GML import, skipping node without 'id'")

    for child_record in record:
        build_nodes(graph, child_record)


def build_edges(graph, record):
    """
    Add edges to graphit Graph based on GML edge records

    :param graph:   graphit Graph to add edges to
    :type graph:    :graphit:Graph
    :param record:  intermediate GML record hierarchy containing edges
    :type record:   :Record:

    :return:        Graph with edges added
    :rtype:         :graphit:Graph
    """

    if record.name == 'edge':
        source = None
        target = None
        for attr in record.attr:
            if attr[0] == 'source':
                source = attr[1]
            elif attr[0] == 'target':
                target = attr[1]

        if source is not None and target is not None:
            graph.add_edge(source, target, **record.to_dict({}))
        else:
            logging.error("GML import, skipping edge without 'source' and/or 'target'")

    for child_record in record:
        build_edges(graph, child_record)


def read_gml(gml, graph=None):
    """
    Read graph in GML format

    :param gml:             GML graph data.
    :type gml:              File, string, stream or URL
    :param graph:           Graph object to import GML data in
    :type graph:            :graphit:Graph

    :return:                Graph object
    :rtype:                 :graphit:Graph
    """

    if not isinstance(graph, Graph):
        graph = Graph()

    # Parse GML into nested structure of Record class instances
    gml_stream = StreamReader(open_anything(gml))
    records = Record(gml_stream, name='root')

    gml_graphs = [g for g in records if g.name == 'graph']
    if len(gml_graphs) > 1:
        logging.warning("GML file contains {0} 'graph' objects. Only parse first".format(len(gml_graphs)))
    gml_graph_record = gml_graphs[0]

    # GML node and edge labels are unique, turn off auto_nid
    graph.data['auto_nid'] = False

    # Set graph meta-data and attributes
    graph_attr = gml_graph_record.to_dict({})
    graph.directed = True
    if 'directed' in graph_attr:
        directed = graph_attr.pop('directed')
        graph.directed = True if directed == 1 else False

    graph.data.update(graph_attr)

    # Build graph from records
    build_nodes(graph, gml_graph_record)
    build_edges(graph, gml_graph_record)

    return graph


def write_gml(graph, node_tools=None, edge_tools=None):
    """
    Export a graphit graph to GML format

    Export graphit Graph data, nodes and edges in Graph Modelling Language
    (GML) format. The function replaces the graph NodeTools and EdgeTools
    with a custom version exposing a `serialize` method responsible for
    serializing the node/edge attributes in a GML format. The NodeTools
    class is also used to export Graph.data attributes.

    Custom serializers may be introduced as custom NodeTools or EdgeTools
    classes using the `node_tools` and/or `edge_tools` attributes.
    In addition, the graph ORM may be used to inject tailored `serialize`
    methods in specific nodes or edges.

    :param graph:       Graph object to export
    :type graph:        :graphit:Graph
    :param node_tools:  NodeTools class with node serialize method
    :type node_tools:   :graphit:NodeTools
    :param edge_tools:  EdgeTools class with edge serialize method
    :type edge_tools:   :graphit:EdgeTools

    :return:            GML graph representation
    :rtype:             :py:str
    """

    # Set current node and edge tools aside and register GML ones for export
    curr_nt = graph.node_tools
    curr_et = graph.edge_tools
    graph.node_tools = node_tools or type('GMLNodeTools', (GMLTools, NodeTools), {})
    graph.edge_tools = edge_tools or type('GMLEdgeTools', (GMLTools, EdgeTools), {})

    # Create empty file buffer
    string_buffer = StringIO()

    # Serialize main graph instance
    gs = graph.node_tools()
    string_buffer.write('graph [\n')
    gs.serialize(graph.data.to_dict(), string_buffer, indent=2)

    # Serialize nodes
    for node in graph.iternodes(sort_key=int):
        node.serialize(node.nodes[node.nid], string_buffer, indent=2, class_name='node')

    # Serialize edges
    for edge in graph.iteredges():
        edge.serialize(edge.edges[edge.nid], string_buffer, indent=2, class_name='edge')

    string_buffer.write(']\n')

    # Restore original node and edge tools
    graph.node_tools = curr_nt
    graph.edge_tools = curr_et

    logger.info('Graph {0} exported in GML format'.format(repr(graph)))

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
