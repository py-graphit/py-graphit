# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_pydata_format.py

"""
Functions for importing and exporting (nested) Python data structures into
graph data structures.
"""

import logging

from graphit import __module__
from graphit.graph_exceptions import GraphitException
from graphit.graph_mixin import NodeTools
from graphit.graph_py2to3 import return_instance_type
from graphit.graph_orm import GraphORM
from graphit.graph_axis.graph_axis_class import GraphAxis
from graphit.graph_axis.graph_axis_mixin import NodeAxisTools
from graphit.graph_io.io_helpers import flatten_nested_dict, resolve_root_node

__all__ = ['read_pydata', 'write_pydata']

logger = logging.getLogger(__module__)
excluded_keys = ('_id', 'format', 'type')


class PyDataNodeTools(NodeTools):

    def serialize(self, **kwargs):
        """
        Serialize graph nodes to a Python dictionary

        This default `serialize` method is used when no python data type
        specific or custom method is returned by the ORM.
        It will serialize the current node children if any to a Python
        dictionary and return them with the current node key.

        :param kwargs:
        :return:
        """

        attributes = {}
        if kwargs.get('export_all'):
            for key in self.nodes[self.nid].keys():
                if key in excluded_keys or key == self.key_tag:
                    continue

                value = self.get(key, default=kwargs.get('default'))
                if not kwargs.get('allow_none') and value is None:
                    continue

                attributes[key] = value
        else:
            attributes[self.value_tag] = self.get(self.value_tag, default=kwargs.get('default'))

        # Iterate child attributes
        for cid in self.children(return_nids=True):
            child_node = self.getnodes(cid)

            if not hasattr(child_node, 'serialize'):
                continue

            key, value = child_node.serialize(**kwargs)

            # Check for dictionary key overload
            if key in attributes:
                logging.warning('Key {0} already defined. Values will be updated'.format(key))

            attributes[key] = value

        if len(attributes) == 1:
            return self.get(self.key_tag), list(attributes.values())[0]

        return self.get(self.key_tag), attributes


class ParseDictionaryType(NodeAxisTools):
    
    @staticmethod
    def deserialize(data, graph, parser_classes, dkey='root', rnid=None):

        nid = graph.add_node(dkey, format=return_instance_type(data), type='object')
        if rnid:
            graph.add_edge(rnid, nid)
        
        for key, value in sorted(data.items(), key=lambda x: str(x[0])):
            parser = parser_classes.get(return_instance_type(value), parser_classes['fallback'])
            p = parser()
            p.deserialize(value, graph, parser_classes, dkey=key, rnid=nid)
    
    def serialize(self, **kwargs):
        """
        Serialize a node as Python dictionary
        
        :param allow_none:  serialize None values
        :type allow_none:   :py:bool
        :param default:     default value to return if value is None
        
        :return:            dictionary name (node key) and dictionary
        """
        
        attributes = {}
        
        # collect node attribute
        for key in self.nodes[self.nid].keys():
            if key in excluded_keys or key == self.key_tag:
                continue
            
            value = self.get(key, default=kwargs.get('default'))
            if not kwargs.get('allow_none') and value is None:
                continue
            
            attributes[key] = value

        # Iterate child attributes
        for cid in self.children(return_nids=True):
            child_node = self.origin.getnodes(cid)

            if not hasattr(child_node, 'serialize'):
                continue

            key, value = child_node.serialize(**kwargs)

            # Check for dictionary key overload
            if key in attributes:
                logging.warning('Key {0} already defined. Values will be updated'.format(key))
            
            attributes[key] = value

        return self.get(self.key_tag), attributes


class ParseListType(NodeAxisTools):

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey='root', rnid=None):
        
        nid = graph.add_node(dkey, format=return_instance_type(data), type='array')
        if rnid:
            graph.add_edge(rnid, nid)
        
        for i, value in enumerate(data, start=1):
            parser = parser_classes.get(return_instance_type(value), ParseListItem)
            p = parser()
            p.deserialize(value, graph, parser_classes, dkey='item-{0}'.format(i), rnid=nid)
    
    def serialize(self, **kwargs):
        """
        Serialize a node as Python list
        
        # TODO: Serialization of children when switching to 'return_nids = True'
        # Refactor ORM to properly deal with the inherit = False option and make
        # that an option you can set for every registered node/edge.
        
        :param allow_none:  serialize None values
        :type allow_none:   :py:bool
        
        :return:            list name (node key) and list
        """

        new = []
        for cid in self.children(return_nids=True):
            child_node = self.origin.getnodes(cid)
            
            key, value = child_node.serialize(**kwargs)
            if not kwargs.get('allow_none') and value is None:
                continue
            
            new.append(value)
        
        return self.get(self.key_tag), new


class ParseTupleType(ParseListType):
    
    def serialize(self, **kwargs):
        
        new = []
        for cid in self.children(return_nids=True):
            child_node = self.origin.getnodes(cid)
            
            key, value = child_node.serialize(**kwargs)
            if not kwargs.get('allow_none') and value is None:
                continue
            
            new.append(value)
        
        return self.get(self.key_tag), tuple(new)


class ParseSetType(ParseListType):
    
    def serialize(self, **kwargs):
        
        new = []
        for cid in self.children(return_nids=True):
            child_node = self.origin.getnodes(cid)
            
            key, value = child_node.serialize(**kwargs)
            if not kwargs.get('allow_none') and value is None:
                continue
            
            new.append(value)
        
        return self.get(self.key_tag), set(new)


class ParseListItem(NodeAxisTools):
    
    @staticmethod
    def deserialize(data, graph, parser_classes, dkey=None, rnid=None):
        
        nid = graph.add_node(dkey, type=type(data).__name__)
        if rnid:
            graph.add_edge(rnid, nid)
        
        node = graph.getnodes(nid)
        node.set(graph.value_tag, data)


class ParseBasicTypesLevel0(NodeAxisTools):

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey=None, rnid=None):

        nid = graph.add_node(dkey, type=type(data).__name__)
        if rnid:
            graph.add_edge(rnid, nid)

        node = graph.getnodes(nid)
        node.set(graph.value_tag, data)


class ParseBasicTypesLevel1(NodeAxisTools):

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey=None, rnid=None):

        dkey = dkey or graph.value_tag

        node = graph.getnodes(rnid)
        node.set(dkey, data)


ORMDEFS_LEVEL0 = {'dict': ParseDictionaryType,
                  'list': ParseListType,
                  'set': ParseSetType,
                  'tuple': ParseTupleType,
                  'fallback': ParseBasicTypesLevel0}


ORMDEFS_LEVEL1 = {'dict': ParseDictionaryType,
                  'list': ParseListType,
                  'set': ParseSetType,
                  'tuple': ParseTupleType,
                  'fallback': ParseBasicTypesLevel1}


def read_pydata(data, graph=None, parser_classes=ORMDEFS_LEVEL1, level=1):
    """
    Parse (hierarchical) python data structures to a graph

    Many data formats are first parsed to a python structure before they are
    converted to a graph using the `read_pydata` function.
    The function supports any object that is an instance of, or behaves as, a
    Python dictionary, list, tuple or set and converts these (nested)
    structures to graph nodes and edges for connectivity. Data is stored in
    nodes using the node and edge 'key_tag' and 'value_tag' attributes in the
    Graph class.

    Data type and format information are also stored as part of the nodes to
    enable reconstruction of the Python data structure on export using the
    `write_pydata` function. Changing type and format on a node or edge
    allows for customized data export.

    Parsing of data structures to nodes and edges is handled by parser classes
    that need to define the methods `deserialize` for reading and `serialize`
    for writing. In `write_pydata` these classes are registered with the ORM
    to fully customize the use of the `serialize` method. In the `read_pydata`
    function the ORM cannot be used because the nodes/edges themselves do not
    yet exist. Instead they are provided as a dictionary through the
    `parser_classes` argument. The dictionary defined the string representation
    of the Python data type as key and parser class as value.

    Parser customization is important as Python data structures can be
    represented as a graph structure in different ways. This is certainly true
    for dictionaries where key/value pairs can be part of the node attributes,
    as separate nodes or as a combination of the two.
    `read_pydata` has quick support for two scenario's using the `level`
    argument:

        * level 0: every dictionary key/value pair is represented as a node
          regardless of its position in the nested data structure
        * level 1: all keys at the same level in the hierarchy that have a
          primitive type value are stored as part of the node attributes.

    If the `graph` is empty, the first node added to the graph is assigned
    as root node. If the `graph` is not empty, new nodes and edges will be
    added to it as subgraph. Edge connections between the two will have to be
    made afterwards.
    
    :param data:            Python (hierarchical) data structure
    :param graph:           GraphAxis object to import dictionary data in
    :type graph:            :graphit:GraphAxis
    :param parser_classes:  parser class definition for different Python data
                            types
    :type parser_classes:   :py:dict
    :param level:           dictionary parsing mode
    :type level:            :py:int
    
    :return:                GraphAxis object
    :rtype:                 :graphit:GraphAxis
    """
    
    # User defined or default GraphAxis object
    if graph is None:
        graph = GraphAxis()
    if not isinstance(graph, GraphAxis):
        raise TypeError('Unsupported graph type {0}'.format(type(graph)))

    # Define the parser classes based on level if not a custom dict.
    if parser_classes in (ORMDEFS_LEVEL0, ORMDEFS_LEVEL1):
        if level == 0:
            parser_classes = ORMDEFS_LEVEL0

    # Define root
    if graph.empty():
        graph.root = graph._nodeid
    
    # Start recursive parsing by calling the `deserialize` method on the parser object
    parser = parser_classes.get(return_instance_type(data), parser_classes['fallback'])
    p = parser()
    p.deserialize(data, graph, parser_classes)
    
    return graph


def write_pydata(graph, nested=True, sep='.', default=None, allow_none=True, export_all=False, include_root=False):
    """
    Export a graph to a (nested) dictionary
    
    Convert graph representation of the dictionary tree into a dictionary
    using a nested or flattened representation of the dictionary hierarchy.
    
    In a flattened representation, the keys are concatenated using the `sep`
    separator.
    Dictionary keys and values are obtained from the node attributes using
    `key_tag` and `value_tag`. The key_tag is set to
    graph key_tag by default.
    
    Exporting only primary key_tag/value_tag pairs is default
    behaviour. Use the 'export_all' argument to export the full node
    dictionary.
    
    TODO: include ability to export multiple isolated subgraphs
    
    :param graph:          Graph object to export
    :type graph:           :graphit:GraphAxis
    :param nested:         return a nested or flattened dictionary
    :type nested:          :py:bool
    :param sep:            key separator used in flattening the dictionary
    :type sep:             :py:str
    :param default:        value to use when node value was not found using
                           value_tag.
    :type default:         mixed
    :param allow_none:     allow None values in the output
    :type allow_none:      :py:bool
    :param export_all:     Export the full node storage dictionary.
    :type export_all:      :py:bool
    
    :rtype:                :py:dict
    """
    
    # No nodes, return empty dict
    if graph.empty():
        logging.info('Graph is empty: {0}'.format(repr(graph)))
        return {}
    
    # Graph should be of type GraphAxis with a root node nid defined
    if not isinstance(graph, GraphAxis):
        raise TypeError('Unsupported graph type {0}'.format(type(graph)))
    if graph.root is None:
        raise GraphitException('No graph root node defines')
    
    # Build ORM with format specific conversion classes
    pydataorm = GraphORM(inherit=False)
    pydataorm.node_mapping.add(ParseDictionaryType, lambda x: x.get('format') == 'dict')
    pydataorm.node_mapping.add(ParseListType, lambda x: x.get('format') == 'list')
    pydataorm.node_mapping.add(ParseSetType, lambda x: x.get('format') == 'set')
    pydataorm.node_mapping.add(ParseTupleType, lambda x: x.get('format') == 'tuple')
    
    # Set current ORM aside and register new one.
    curr_orm = graph.orm
    graph.orm = pydataorm
    
    # Set current NodeTools aside and register new one
    curr_nt = graph.node_tools
    graph.node_tools = PyDataNodeTools
    
    # Define start node for recursive export
    if len(graph) > 1:
        root = graph.getnodes(resolve_root_node(graph))
    else:
        root = graph.getnodes(list(graph.nodes.keys()))
    
    # If we export the full node dictionary, also export None key/value pairs
    if export_all:
        allow_none = True
    
    # Start recursive parsing
    root_key, data = root.serialize(allow_none=allow_none, export_all=export_all, default=default)
    
    # Include root_key or not
    if include_root and root_key:
        data = {root_key: data}
    
    # Flatten the dictionary if needed
    if not nested:
        data = flatten_nested_dict(data, sep=sep)
    
    # Restore original ORM and NodeTools
    graph.node_tools = curr_nt
    graph.orm = curr_orm
    
    return data
