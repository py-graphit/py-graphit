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
    
    not_export = ('tail', '_id', node.value_tag, node.key_tag)
    
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


class XMLNodeTools(NodeTools):
    
    def serialize(self, tree=None):
        """
        Serialize to XML
        
        :param tree:    ElementTree XML parent element to add node to as
                        new XML SubElement
        :type tree:     :py:xml:etree:ElementTree:Element
        """
        
        if tree is None:
            element = et.Element(self[self.key_tag])
        else:
            element = et.SubElement(tree, self[self.key_tag])
        
        element.attrib = create_attrib(self)
        element.text = self.get(self.value_tag)
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
    
    # User defined or default GraphAxis object
    if graph is None:
        graph = GraphAxis()
    if not isinstance(graph, GraphAxis):
        raise TypeError('Unsupported graph type {0}'.format(type(graph)))
    
    # Try parsing the string using default Python cElementTree parser
    xml_file = open_anything(xml_file)
    try:
        tree = et.fromstring(xml_file.read())
    except et.ParseError as error:
        logging.error('Unable to parse XML file. cElementTree error: {0}'.format(error))
        return
    
    def walk_element_tree(element, parent=None):
        
        for child in element:
            child_data = child.attrib
            if child.text and len(child.text.strip()):
                child_data[graph.value_tag] = child.text.strip()
            
            nid = graph.add_node(child.tag, **child_data)
            graph.add_edge(parent, nid)
            
            walk_element_tree(child, parent=nid)
    
    is_empty = graph.empty()
    
    # Add root element
    element_data = tree.attrib
    if tree.text and len(tree.text.strip()):
        element_data[graph.value_tag] = tree.text.strip()
    rid = graph.add_node(tree.tag, **element_data)
    
    if is_empty:
        graph.root = rid
    
    # Recursive add XML elements as nodes
    walk_element_tree(tree, parent=graph.root)
    
    return graph


def write_xml(graph):
    """
    Export a graph to an XML data format
    
    :param graph:
    :return:
    """
    
    # Graph should be of type GraphAxis with a root node nid defined
    if not isinstance(graph, GraphAxis):
        raise TypeError('Unsupported graph type {0}'.format(type(graph)))
    if graph.root is not None:
        raise GraphitException('No graph root node defines')
    
    # Set current NodeTools aside and register new one
    curr_nt = graph.node_tools
    graph.node_tools = XMLNodeTools
    
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
