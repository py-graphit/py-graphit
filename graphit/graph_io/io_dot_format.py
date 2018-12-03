# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_dot_format.py

"""
Functions for exporting and importing graphs to and from graph description
language (DOT) format
"""

import json

from graphit import __module__, __version__
from graphit.graph_py2to3 import StringIO, PY_PRIMITIVES

__all__ = ['write_dot']


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
    string_buffer.write('//Created by {0} version {1}\n'.format(__module__, __version__))
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
