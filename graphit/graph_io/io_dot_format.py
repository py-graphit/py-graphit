# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_dot_format.py

"""
Functions for exporting and importing graphs to and from graph description
language (DOT) format
"""

import logging
import json
import re
import shlex

from graphit import __module__, version, Graph
from graphit.graph_py2to3 import StringIO, PY_PRIMITIVES
from graphit.graph_io.io_helpers import coarse_type, open_anything, StreamReader

direction_splitter = re.compile('(--|->)')
attribute_splitter = re.compile('(?<=[^0-9]),(?=[^0-9]+)')

logger = logging.getLogger(__module__)

__all__ = ['write_dot']


def parse_graph_type(reader, graph):
    """
    Parse the start of a DOT graph and create a new Graphit graph for it.

    DOT syntax defines a graph as:

        <'graph' or 'digraph'> <"optional title"> {

    :param reader: StreamReader instance
    :type reader:  StreamReader

    :return:       Graphit Graph
    :rtype:        :graphit:Graph
    """

    line, graph_type = reader.read_upto_block(['graph', 'digraph'], keep=True)
    if graph_type:
        line, char = reader.read_upto_char('{')
        line = shlex.split(line)
        if line:
            graph.data.title = line[0]

        graph.directed = True if graph_type == 'digraph' else False
        graph.data.auto_nid = False

        logging.info('Graph type "{0}" with title: {1}'.format(graph_type, graph.data.get('title', '')))
        return graph

    return None


def parse_edge(line, graph, attr={}):
    """
    Add DOT edges to the graphit Graph

    :param line:  line with edges to parse
    :type line:   :py:str
    :param graph: Graph to add edges to
    :type graph:  :graphit:Graph
    :param attr:  attributes to add to edges
    :type attr:   :py:dict

    :return:      added edges
    :rtype:       :py:list
    """

    added_edges = []

    edges = [e.strip() for e in direction_splitter.split(line)]
    for n in [i for i, x in enumerate(edges) if x in ('--', '->')]:
        start_edge, direction, target_edge = edges[n-1:n+2]
        target_edge = target_edge.strip(' {} ').split()

        directed = True if direction == '->' else False
        for edge in target_edge:
            node_from_edge = start_edge not in graph.nodes or edge not in graph.nodes
            added_edges.append(graph.add_edge(start_edge, edge,
                                              directed=directed,
                                              node_from_edge=node_from_edge,
                                              **attr))

    return added_edges


def parse_attributes(line):
    """
    Parse DOT keyword attributes

    :param line:  line with attributes to parse
    :type line:   :py:str

    :return:      attributes
    :rtype:       :py:dict
    """

    part = ' '.join(shlex.split(line))
    block = attribute_splitter.split(part)

    attributes = {}
    for attr in block:
        attr = attr.split('=')
        attributes[attr[0].strip()] = attr[1].strip()

    return attributes


def parse_nodes(line, graph):
    """
    Add DOT nodes to the graphit Graph

    :param line:  line with nodes to parse
    :type line:   :py:str
    :param graph: Graph to add nodes to
    :type graph:  :graphit:Graph

    :return:      added nodes
    :rtype:       :py:list
    """

    nodes = [l.strip(',') for l in shlex.split(line)]

    for node in nodes:
        if node not in graph.nodes:
            graph.add_node(node)

    return nodes


def read_dot(dot, graph=None):
    """
    Read graph in DOT format

    :param dot:             DOT graph data.
    :type dot:              File, string, stream or URL
    :param graph:           Graph object to import DOT data in
    :type graph:            :graphit:Graph

    :return:                Graph object
    :rtype:                 :graphit:Graph
    """

    dot_stream = StreamReader(open_anything(dot))
    if not isinstance(graph, Graph):
        graph = Graph()

    block = None
    node_attr = {}
    edges = []
    nodes = []

    parse = True
    init_graph = False
    while parse or dot_stream.has_more:

        # Parse start graph block
        if not init_graph:
            graph = parse_graph_type(dot_stream, graph)
            if graph is not None:
                init_graph = True

        # Parse up to DOT reserved chars
        line, char = dot_stream.read_upto_char(('\n', ';', '[', ']', '}'))
        line = line.strip() if line else ''

        if line:

            # Comment line
            if line[0] in ('/', '#'):
                logging.info('Skip DOT comment line: "{0}"'.format(line))

                # Read till end of line
                if char != '\n':
                    dot_stream.read_upto_char('\n')

            # Grouping not supported
            elif line[0] == '{':
                nxt_line, nxt_char = dot_stream.read_upto_char('}')
                logging.info('Skip group: {0}{1}{2}{3}'.format(line, char, nxt_line, nxt_char))

            # Subgraphs
            elif 'subgraph' in line:
                block = 'subgraph'
                node_attr[block] = shlex.split(line)[1]

            # Node attribute block
            elif 'node' in line:
                block = 'node'
                node_attr = {}

            # Parse edges
            elif '--' in line or '->' in line:

                attr = {}
                if char == '[':
                    attr = parse_attributes(dot_stream.read_upto_char(']')[0])
                edges.extend(parse_edge(line, graph, attr=attr))

            else:
                if '=' in line:
                    if block in ('subgraph', 'node'):
                        node_attr.update(parse_attributes(line))
                    else:
                        graph.data.update(parse_attributes(line))
                else:
                    nodes.extend(parse_nodes(line, graph))

        elif (char == '}' and block == 'subgraph') or block == 'node':
            logging.info('Stop parsing {0} group at position: {1}'.format(block, dot_stream.block_pos[1]))

            nodes.extend(list(set(sum(edges, ()))))
            for node in nodes:
                graph.nodes[node].update(node_attr)

            node_attr = {}
            edges = []
            nodes = []
            block = None

        else:
            parse = False

    return graph


def write_dot(graph, graph_name='graph', dot_directives=None):
    """
    DOT graphs are either directional (digraph) or undirectional, mixed mode
    is not supported.

    Basic types for node and edge attributes are supported.

    :param graph:          Graph object to export
    :type graph:           :graphit:Graph
    :param graph_name:     graph name to include
    :type graph_name:      :py:str
    :param dot_directives: special DOT format rendering directives
    :type dot_directives:  :py:dict

    :return:               DOT graph representation
    :rtype:                :py:str
    """

    indent = ' ' * 4
    link = '->' if graph.directed else '--'

    # Create empty file buffer
    string_buffer = StringIO()

    # Write header comment and graph container
    string_buffer.write('//Created by {0} version {1}\n'.format(__module__, version()))
    string_buffer.write('{0} "{1}" {2}\n'.format('digraph' if graph.directed else 'graph', graph_name, '{'))

    # Write special DOT directives
    if isinstance(dot_directives, dict):
        for directive, value in dot_directives.items():
            string_buffer.write('{0}{1}={2}\n'.format(indent, directive, value))

    # Export nodes
    string_buffer.write('{0}//nodes\n'.format(indent))
    for node in graph.iternodes():
        attr = ['{0}={1}'.format(k, json.dumps(v)) for k,v in node.nodes[node.nid].items() if
                isinstance(v, PY_PRIMITIVES) and not k.startswith('$')]
        if attr:
            string_buffer.write('{0}{1} [{2}];\n'.format(indent, node.nid, ','.join(attr)))

    # Export adjacency
    string_buffer.write('{0}//edges\n'.format(indent))
    done = []
    for node, adj in graph.adjacency.items():
        for a in adj:
            edges = [(node, a), (a, node)]

            if all([e not in done for e in edges]):
                attr = {}
                for edge in edges:
                   attr.update(graph.edges.get(edge, {}))
                attr = ['{0}={1}'.format(k, json.dumps(v)) for k, v in attr.items() if
                        isinstance(v, PY_PRIMITIVES) and not k.startswith('$')]

                if attr:
                    string_buffer.write('{0}{1} {2} {3} [{4}];\n'.format(indent, node, link, a, ','.join(attr)))
                else:
                    string_buffer.write('{0}{1} {2} {3};\n'.format(indent, node, link, a))

            done.extend(edges)

    # Closing curly brace
    string_buffer.write('}\n')

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
