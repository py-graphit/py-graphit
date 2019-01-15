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
import copy

from graphit import __module__
from graphit.graph_exceptions import GraphitException
from graphit.graph_py2to3 import return_instance_type, PY_DATA_OBJECTS, PY_PRIMITIVES
from graphit.graph_orm import GraphORM
from graphit.graph_axis.graph_axis_class import GraphAxis
from graphit.graph_axis.graph_axis_mixin import NodeAxisTools
from graphit.graph_io.io_helpers import resolve_root_node

__all__ = ['read_pydata', 'write_pydata']

logger = logging.getLogger(__module__)
excluded_keys = ('_id', 'format', 'type')


class PyDataNodeTools(NodeAxisTools):
    """
    Default data serialization and deserialization methods from and to nodes.
    """

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey=None, rnid=None):
        """
        Deserialize Python primitives or objects to nodes

        :param data:            data to deserialize
        :param graph:           graph to add nodes to
        :type graph:            :graphit:GraphAxis
        :param parser_classes:  parser classes used to deserialize list items
        :param dkey:            data node key_tag
        :type dkey:             :py:str
        :param rnid:            nid of node to connect list node to
        :type rnid:             :py:int
        """

        dtype = 'primative' if isinstance(data, PY_PRIMITIVES) else 'object'
        nid = graph.add_node(dkey, format=type(data).__name__, type=dtype)
        if rnid:
            graph.add_edge(rnid, nid)

        if not isinstance(data, PY_DATA_OBJECTS) and hasattr(data, '__iter__'):
            for i, value in enumerate(data, start=1):
                parser = parser_classes.get(return_instance_type(value), parser_classes['fallback'])
                p = parser()
                p.deserialize(value, graph, parser_classes, dkey='item-{0}'.format(i), rnid=nid)
        else:
            node = graph.getnodes(nid)
            node.set(graph.value_tag, data)

    def serialize(self, **kwargs):
        """
        Serialize Graph node data

        This method is a general (catch all) node data serializer that returns
        single data key/value pairs or a dictionary depending on the graph
        structure as:

        **Node if a leaf node**
        A leaf node has no children meaning it contains no nested data
        structures from a graph perspective. In this case the serializer
        returns one key/value pair defined by the nodes 'key_tag' and
        'value_tag'

        **Node has children**
        If the node has children the serializer returns a dictionary named
        according to the nodes 'key_tag' and containing key/value pairs
        returned by calling the serialize methods on all of the nodes children.

        **Node contains more data**
        By default only the data represented by a nodes 'key_tag', 'value_tag'
        pair is serialized. Additional data a node may have as key/value pairs
        can be serialized by using the `export_all` argument. This excludes
        administrative data used by graphit itself such as the _id, format and
        type keywords.

        :param allow_none:  serialize None values
        :type allow_none:   :py:bool
        :param export_all:  serialize all node attributes except the ones in
                            the `exclude_keys` list.
        :type export_all:   :py:bool
        :param default:     default value to return if value is None
        """

        attributes = {}

        # Export all node keys instead of default key_tag/value_tag pair
        if kwargs.get('export_all', False):
            for key in self.nodes[self.nid].keys():
                if key in excluded_keys or key == self.key_tag:
                    continue

                value = self.get(key, default=kwargs.get('default'))
                if not kwargs.get('allow_none') and value is None:
                    continue

                attributes[key] = value

        # Iterate child attributes if any
        for cid in self.children(return_nids=True):
            child_node = self.getnodes(cid)
            key, value = child_node.serialize(**kwargs)

            # Check for dictionary key overload
            if key in attributes:
                logging.warning('Key {0} already defined. Values will be updated'.format(key))

            attributes[key] = value

        if not attributes:
            return self.get(self.key_tag), self.get(self.value_tag, default=kwargs.get('default'))

        return self.get(self.key_tag), attributes


class ParseDictionaryType(NodeAxisTools):
    """
    Deserialize methods from Python dictionaries.
    The default PyDataNodeTools.serialize method is used for serialization as
    it return dictionaries by default.
    """

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey='root', rnid=None):
        """
        Deserialize key/value pairs in a dictionary to nodes

        :param data:            list data to deserialize
        :type data:             :py:list
        :param graph:           graph to add nodes to
        :type graph:            :graphit:GraphAxis
        :param parser_classes:  parser classes used to deserialize list items
        :param dkey:            list node key_tag
        :type dkey:             :py:str
        :param rnid:            nid of node to connect list node to
        :type rnid:             :py:int
        """

        nid = graph.add_node(dkey, format=return_instance_type(data), type='object')
        if rnid:
            graph.add_edge(rnid, nid)

        for key, value in sorted(data.items(), key=lambda x: str(x[0])):
            parser = parser_classes.get(return_instance_type(value), parser_classes['fallback'])
            p = parser()
            p.deserialize(value, graph, parser_classes, dkey=key, rnid=nid)


class ParseDictionaryTypeLevel1(NodeAxisTools):
    """
    Deserialize methods from Python dictionaries.
    The default PyDataNodeTools.serialize method is used for serialization as
    it return dictionaries by default.
    """

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey='root', rnid=None):
        """
        Level based deserialize key/value pairs in a dictionary

        All key/value pairs at the same level in a (nested) dictionary for
        for which the value itself is not a dictionary are stored in the
        same node.

        :param data:            dictionary data to deserialize
        :type data:             :py:dict
        :param graph:           graph to add nodes to
        :type graph:            :graphit:GraphAxis
        :param parser_classes:  parser classes used to deserialize list items
        :param dkey:            dictionary item node key_tag
        :type dkey:             :py:str
        :param rnid:            nid of node to connect list node to
        :type rnid:             :py:int
        """

        nid = graph.add_node(dkey, format=return_instance_type(data), type='object')
        if rnid:
            graph.add_edge(rnid, nid)

        for key, value in sorted(data.items(), key=lambda x: str(x[0])):
            if isinstance(value, dict):
                parser = parser_classes['dict']
                p = parser()
                p.deserialize(value, graph, parser_classes, dkey=key, rnid=nid)
            else:
                graph.nodes[nid][key] = value


class ParseListType(NodeAxisTools):
    """
    Serialize and deserialize methods to and from Python lists
    """

    @staticmethod
    def deserialize(data, graph, parser_classes, dkey='root', rnid=None):
        """
        Deserialize the items in an ordered list to nodes.

        The same method is also used to deserialize Python tuple and set types
        by using the ParseListType as base class.
        Lists, tuples and sets are the same from a graph perspective as
        mutability and order are not considered in graphs although it could be.

        :param data:            list data to deserialize
        :type data:             :py:list
        :param graph:           graph to add nodes to
        :type graph:            :graphit:GraphAxis
        :param parser_classes:  parser classes used to deserialize list items
        :param dkey:            list node key_tag
        :type dkey:             :py:str
        :param rnid:            nid of node to connect list node to
        :type rnid:             :py:int
        """

        nid = graph.add_node(dkey, format=return_instance_type(data), type='array')
        if rnid:
            graph.add_edge(rnid, nid)

        # Deserialize all list items in order
        for i, value in enumerate(data, start=1):
            parser = parser_classes.get(return_instance_type(value), parser_classes['fallback'])
            p = parser()
            p.deserialize(value, graph, parser_classes, dkey='item-{0}'.format(i), rnid=nid)

    def serialize(self, **kwargs):
        """
        Serialize a node as Python list

        TODO: How can we guaranty list order if nodes get inserted/removed

        :param allow_none:  serialize None values
        :type allow_none:   :py:bool

        :return:            list name (node key) and list
        """

        return_list = []
        for cid in self.children(return_nids=True):
            child_node = self.origin.getnodes(cid)

            key, value = child_node.serialize(**kwargs)
            if not kwargs.get('allow_none', False) and value is None:
                continue

            return_list.append(value)

        return self.get(self.key_tag), return_list


class ParseTupleType(ParseListType):
    """
    Serialize method to Python tuples. Deserialize method inherited
    from ParseListType class
    """

    def serialize(self, **kwargs):
        """
        Serialize a node as Python tuple

        Calls the list serializer and parses the returned list to a tuple

        :param allow_none:  serialize None values
        :type allow_none:   :py:bool

        :return:            tuple name (node key) and tuple
        """

        key, value = super(ParseTupleType, self).serialize(**kwargs)
        return key, tuple(value)


class ParseSetType(ParseListType):
    """
    Serialize method to Python sets. Deserialize method inherited from
    ParseListType class
    """

    def serialize(self, **kwargs):
        """
        Serialize a node as Python set

        Calls the list serializer and parses the returned list to a set

        :param allow_none:  serialize None values
        :type allow_none:   :py:bool

        :return:            set name (node key) and set
        """

        key, value = super(ParseSetType, self).serialize(**kwargs)
        return key, set(value)


# Default pydata deserialization parser classes
ORMDEFS_LEVEL0 = {'dict': ParseDictionaryType,
                  'list': ParseListType,
                  'set': ParseSetType,
                  'tuple': ParseTupleType,
                  'fallback': PyDataNodeTools}


# Equal to ORMDEFS_LEVEL0 but with dictionary deserializer collecting all
# key/value pairs in same (nested) dictionary level as data in the same node.
ORMDEFS_LEVEL1 = {'dict': ParseDictionaryTypeLevel1,
                  'list': ParseListType,
                  'set': ParseSetType,
                  'tuple': ParseTupleType,
                  'fallback': PyDataNodeTools}


def read_pydata(data, graph=None, parser_classes=None, level=0):
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
    `parser_classes` argument. The dictionary defines the string representation
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
                            types. Updates default classes for level 0 or 1
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

    # Determine parser classes to use based on level
    assert level in (0, 1), GraphitException('Unsupported level {0}. Required to be 0 or 1'.format(level))
    if level == 0:
        parser_class_dict = copy.copy(ORMDEFS_LEVEL0)
    else:
        parser_class_dict = copy.copy(ORMDEFS_LEVEL1)

    # Update parser_class_dict with custom classes if any
    if isinstance(parser_classes, dict):
        parser_class_dict.update(parser_classes)

    # Define root
    if graph.empty():
        graph.root = graph._nodeid

    # Start recursive parsing by calling the `deserialize` method on the parser object
    parser = parser_class_dict.get(return_instance_type(data), parser_class_dict['fallback'])
    p = parser()
    p.deserialize(data, graph, parser_class_dict)

    return graph


def write_pydata(graph, default=None, allow_none=True, export_all=False, include_root=False):
    """
    Export a graph to a (nested) dictionary

    Convert graph representation of the dictionary tree into a dictionary
    using a nested representation of the dictionary hierarchy.

    Dictionary keys and values are obtained from the node attributes using
    `key_tag` and `value_tag`. The key_tag is set to graph key_tag by default.
    Export using these primary key_tag/value_tag pairs is de default
    behaviour. If a node contains more data these can be exported as part of
    a dictionary using the `export_all` argument.

    .. note:: `export_all` is important when dictionary data structures where
              imported using level=1 in `read_pydata`. In this case, all key
              value pairs at the same dictionary level are contained in the
              same node.

    Node values that are 'None' are exported by default unless `allow_none`
    equals False.
    If the key_tag exists but value_tag is absent use `default` as default.

    .. note:: if a graph is composed out of multiple, independent subgraphs
              only the subgraph for which the root node is defined will be
              exported. To export all, iterate over the subgraphs and define
              the appropriate root for each of them.

    :param graph:          Graph object to export
    :type graph:           :graphit:GraphAxis
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
    curr_nt = graph.origin.node_tools
    graph.origin.node_tools = PyDataNodeTools

    # Define start node for recursive export
    if len(graph) > 1:
        root = graph.getnodes(resolve_root_node(graph))
    else:
        root = graph.getnodes(list(graph.nodes.keys()))

    # Start recursive parsing
    # If we export the full node dictionary, also export None key/value pairs
    root_key, data = root.serialize(allow_none=True if export_all else allow_none,
                                    export_all=export_all, default=default)

    # Include root_key or not
    if include_root and root_key:
        data = {root_key: data}

    # Restore original ORM and NodeTools
    graph.origin.node_tools = curr_nt
    graph.orm = curr_orm

    return data
