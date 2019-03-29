# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_xml_format.py

"""
Functions for exporting and importing XML documents in a graph structure.
"""

import logging
import xml.etree.cElementTree as et

from graphit import __module__
from graphit.graph_exceptions import GraphitException
from graphit.graph_mixin import NodeTools
from graphit.graph_axis.graph_axis_class import GraphAxis
from graphit.graph_io.io_helpers import open_anything, resolve_root_node

__all__ = ['read_xml', 'write_xml']
logger = logging.getLogger(__module__)


def create_attrib(node):

    not_export = ('tail', '_id', node.data.value_tag, node.data.key_tag)

    attrib_dict = {}
    for key, value in node.nodes[node.nid].items():
        if key in not_export:
            continue

        # Data should be serializable
        if not isinstance(value, (str, int, float, bool)):
            logger.warning('Unable to serialize to XML: {0}, {1}'.format(key, repr(value)))
            continue

        attrib_dict[key] = value

    return attrib_dict


def walk_element_tree(element, graph, parent=None):
    """
    Recursively add XML ElementTree elements as nodes to the Graph connecting
    the element to its parent.

    :param element: XML element to add
    :type element:  :xml:etree:cElementTree:Element
    :param graph:   graph to add XML elements to
    :type graph:    :graphit:Graph
    :param parent:  parent node ID to connect new element to
    :type parent:   :py:int
    """

    for child in element:
        child_data = child.attrib
        if child.text and len(child.text.strip()):
            child_data[graph.data.value_tag] = child.text.strip()

        nid = graph.add_node(child.tag, **child_data)
        graph.add_edge(parent, nid)

        walk_element_tree(child, graph, parent=nid)


class XMLNodeTools(NodeTools):

    def serialize(self, tree=None):
        """
        Serialize node to XML

        :param tree:    ElementTree XML parent element to add node to as
                        new XML SubElement
        :type tree:     :py:xml:etree:ElementTree:Element
        """

        if tree is None:
            element = et.Element(self[self.data.key_tag])
        else:
            element = et.SubElement(tree, self[self.data.key_tag])

        element.attrib = create_attrib(self)
        element.text = self.get(self.data.value_tag)
        element.tail = self.get('tail')

        # Iterate child attributes
        for cid in self.children(return_nids=True):
            child_node = self.getnodes(cid)

            if not hasattr(child_node, 'serialize'):
                continue

            child_node.serialize(element)

        return element


def read_xml(xml_file, graph=None):
    """
    Parse hierarchical XML data structure to a graph

    Uses the Python build-in etree cElementTree parser to parse the XML
    document and convert the elements into nodes.
    The XML element tag becomes the node key, XML text becomes the node
    value and XML attributes are added to the node as additional attributes.

    :param xml_file:       XML data to parse
    :type xml_file:        File, string, stream or URL
    :param graph:          Graph object to import dictionary data in
    :type graph:           :graphit:Graph

    :return:               GraphAxis object
    :rtype:                :graphit:GraphAxis
    """

    xml_file = open_anything(xml_file)

    # User defined or default GraphAxis object
    if graph is None:
        graph = GraphAxis()
    elif not isinstance(graph, GraphAxis):
        raise GraphitException('Unsupported graph type {0}'.format(type(graph)))

    # Try parsing the string using default Python cElementTree parser
    try:
        tree = et.fromstring(xml_file.read())
    except et.ParseError as error:
        logging.error('Unable to parse XML file. cElementTree error: {0}'.format(error))
        return

    is_empty = graph.empty()

    # Add root element
    element_data = tree.attrib
    if tree.text and len(tree.text.strip()):
        element_data[graph.data.value_tag] = tree.text.strip()
    rid = graph.add_node(tree.tag, **element_data)

    if is_empty:
        graph.root = rid

    # Recursive add XML elements as nodes
    walk_element_tree(tree, graph, parent=graph.root)

    return graph


def write_xml(graph, node_tools=XMLNodeTools):
    """
    Export a graph to an XML data format

    Custom XML serializers may be introduced as a custom NodeTools
    class using the `node_tools` attribute. In addition, the graph
    ORM may be used to inject tailored `serialize` methods in specific
    nodes or edges.

    :param graph:       Graph to export
    :type graph:        :graphit:Graph
    :param node_tools:  NodeTools class with node serialize method
    :type node_tools:   :graphit:NodeTools

    :return:            Graph exported as a hierarchical XML node structure
    :rtype:             :py:str
    """

    # Graph should be of type GraphAxis with a root node nid defined
    if not isinstance(graph, GraphAxis):
        raise TypeError('Unsupported graph type {0}'.format(type(graph)))
    if graph.root is not None:
        raise GraphitException('No graph root node defines')

    # Set current NodeTools aside and register new one
    if not isinstance(node_tools, NodeTools):
        raise GraphitException('Node_tools ({0}) needs to inherit from the NodeTools class'.format(type(node_tools)))
    curr_nt = graph.node_tools
    graph.node_tools = node_tools

    # Define start node for recursive export
    if len(graph) > 1:
        root = graph.getnodes(resolve_root_node(graph))
    else:
        root = graph.getnodes(graph.nid)

    # Start recursive parsing
    tree = root.serialize()

    # Restore original NodeTools
    graph.node_tools = curr_nt

    return et.tostring(tree)
