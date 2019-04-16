# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_xml_format.py

"""
Reading and writing graphs in GEXF format.

GEXF (Graph Exchange XML Format) is a language for describing complex
network structures, their associated data and dynamics.

Reference and specification:
    - https://gephi.org/gexf/format/schema.html
    - https://gephi.org/gexf/1.2draft/gexf-12draft-primer.pdf
"""

import logging
import datetime
import xml.etree.cElementTree as et

from xml.dom import minidom

from graphit import __module__, Graph
from graphit.graph_py2to3 import PY_PRIMITIVES
from graphit.graph_exceptions import GraphitException
from graphit.graph_mixin import NodeTools, EdgeTools
from graphit.graph_io.io_helpers import open_anything

__all__ = ['read_gexf', 'write_gexf']
logger = logging.getLogger(__module__)


class GEXFNodeTools(NodeTools):

    def get(self, key=None, default=None, defaultattr=None):
        """
        Serialize attribute values

        :param key:         node value attribute name. If not defined then
                            attempt to use class wide `value_tag` attribute.
        :type key:          mixed
        :param defaultattr: node or edge value attribute to use as source of
                            default data when `key` attribute is not present.
        :type defaultattr:  mixed
        :param default:     value to return when all fails
        :type default:      mixed
        """

        target = self.nodes[self.nid]

        key = key or self.data.value_tag
        if key in target:
            return str(target[key])
        return str(target.get(defaultattr, default))

    def add_attrvalues(self, element, attelements):

        attvalues = et.SubElement(element, 'attvalues')
        for a in attelements:
            attvalue = et.SubElement(attvalues, 'attvalue')
            attvalue.attrib = dict([(k, str(v)) for k, v in self.nodes[self.nid][a].items()])
            attvalue.attrib['for'] = str(a)

    def serialize(self, tree):
        """
        Serialize node to GEXF XML element

        :param tree:    ElementTree XML parent element to add node to as
                        new XML SubElement
        :type tree:     :py:xml:etree:ElementTree:Element

        :return:        new node XML ElementTree element
        :rtype:         :py:xml:etree:ElementTree:Element
        """

        element = et.SubElement(tree, 'node')

        attelements = []
        attrib_dict = {'id': str(self.nid)}
        for key, value in self.nodes[self.nid].items():

            # If Dictionary value, add as 'attvalue' elements later on
            if isinstance(value, dict):
                attelements.append(key)
                continue

            # Data should be serializable
            if not isinstance(value, PY_PRIMITIVES):
                logger.warning('Unable to serialize to XML: {0}, {1}'.format(key, repr(value)))
                continue

            attrib_dict[key] = self.get(key=key)

        element.attrib = attrib_dict

        if attelements:
            self.add_attrvalues(element, attelements)

        return element


class GEXFEdgeTools(EdgeTools):

    def get(self, key=None, default=None, defaultattr=None):
        """
        Serialize attribute values

        :param key:         node value attribute name. If not defined then
                            attempt to use class wide `value_tag` attribute.
        :type key:          mixed
        :param defaultattr: node or edge value attribute to use as source of
                            default data when `key` attribute is not present.
        :type defaultattr:  mixed
        :param default:     value to return when all fails
        :type default:      mixed
        """

        target = self.edges[self.nid]

        key = key or self.data.value_tag
        if key in target:
            return str(target[key])
        return str(target.get(defaultattr, default))

    def add_attrvalues(self, element, attelements):

        attvalues = et.SubElement(element, 'attvalues')
        for a in attelements:
            attvalue = et.SubElement(attvalues, 'attvalue')
            attvalue.attrib = dict([(k, str(v)) for k, v in self.edges[self.nid][a].items()])
            attvalue.attrib['for'] = str(a)

    def serialize(self, tree):
        """
        Serialize edge to GEXF XML element

        :param tree:    ElementTree XML parent element to add edge to as
                        new XML SubElement
        :type tree:     :py:xml:etree:ElementTree:Element

        :return:        new edge XML ElementTree element
        :rtype:         :py:xml:etree:ElementTree:Element
        """

        element = et.SubElement(tree, 'edge')

        attelements = []
        attrib_dict = {'source': str(self.nid[0]), 'target': str(self.nid[1])}
        for key, value in self.edges[self.nid].items():

            # If Dictionary value, add as 'attvalue' elements later on
            if isinstance(value, dict):
                attelements.append(key)
                continue

            # Data should be serializable
            if not isinstance(value, PY_PRIMITIVES):
                logger.warning('Unable to serialize to XML: {0}, {1}'.format(key, repr(value)))
                continue

            attrib_dict[key] = str(value)

        # Edge directionality different that global graph directionality
        if self.is_directed != self.directed:
            attrib_dict['type'] = 'directed' if self.is_directed else 'undirected'

        element.attrib = attrib_dict

        if attelements:
            attvalues = et.SubElement(element, 'attvalues')
            for a in attelements:
                attvalue = et.SubElement(attvalues, 'attvalue')
                attvalue.attrib = dict([(k, str(v)) for k, v in self.nodes[self.nid][a].items()])
                attvalue.attrib['for'] = str(a)

        return element


def parse_attvalue_elements(element, attr, xmlns=''):
    """
    Parse GEXF node/edge attvalue elements

    :param element: parent node or edge element
    :type element:  :py:xml:etree:ElementTree:Element
    :param attr:    attribute dictionary to add results to
    :type attr:     :py:dict
    :param xmlns:   document XMLNS declaration
    :type xmlns:    :py:str

    :return:        node/edge attribute directory
    :rtype:         :py:dict
    """
    for attvalue in element.findall('./{0}attvalues/{0}attvalue'.format(xmlns)):
        key = attvalue.get('for')
        if key not in attr:
            attr[key] = attvalue.attrib
        else:
            logging.warning('GEXF attrvalue {0} already defined as key in graph node/edge attributes'.format(key))

    return attr


def read_gexf(gexf_file, graph=None):
    """
    Read graphs in GEXF format

    Uses the Python build-in etree cElementTree parser to parse the XML
    document and convert the elements into nodes.
    The XML element tag becomes the node key, XML text becomes the node
    value and XML attributes are added to the node as additional attributes.

    :param gexf_file:      XML data to parse
    :type gexf_file:       File, string, stream or URL
    :param graph:          Graph object to import dictionary data in
    :type graph:           :graphit:Graph

    :return:               GraphAxis object
    :rtype:                :graphit:GraphAxis
    """

    gexf_file = open_anything(gexf_file)

    # User defined or default Graph object
    if graph is None:
        graph = Graph()
    elif not isinstance(graph, Graph):
        raise GraphitException('Unsupported graph type {0}'.format(type(graph)))

    # Try parsing the string using default Python cElementTree parser
    try:
        tree = et.fromstring(gexf_file.read())
    except et.ParseError as error:
        logging.error('Unable to parse GEXF file. cElementTree error: {0}'.format(error))
        return

    # Get XMLNS namespace from root
    xmlns = None
    for elem in tree.iter():
        if elem.tag.endswith('gexf'):
            xmlns = elem.tag.split('}')[0] + '}'
            break

    if xmlns is None:
        raise GraphitException('Invalid GEXF file format, "gexf" tag not found')

    # Add graph meta-data and XMLNS namespace
    for meta in tree.iter('{0}meta'.format(xmlns)):
        graph.data.update(meta.attrib)
        for meta_data in meta:
            tag = meta_data.tag.split('}')[1]
            graph.data[tag] = meta_data.text

    # GEXF node and edge labels are unique, turn off auto_nid
    graph.data['auto_nid'] = False

    graph_tag = tree.find('{0}graph'.format(xmlns))
    graph.directed = graph_tag.get('defaultedgetype', 'directed') == 'directed'
    graph.data.update(graph_tag.attrib)

    # Parse all nodes
    nodes = tree.findall('.//{0}node'.format(xmlns))
    if not len(nodes):
        raise GraphitException('GEXF file containes no "node" elements')
    for node in nodes:
        attr = node.attrib
        attr = parse_attvalue_elements(node, attr, xmlns=xmlns)
        graph.add_node(attr['id'], **dict([n for n in attr.items() if n[0] != 'id']))

    # Parse all edges
    edges = tree.findall('.//{0}edge'.format(xmlns))
    for edge in edges:
        attr = edge.attrib

        # Edge direction differs from global graph directionality
        edge_directed = graph.directed
        if 'type' in attr:
            edge_directed = attr['type'] == 'directed'

        attr = parse_attvalue_elements(edge, attr, xmlns=xmlns)
        graph.add_edge(attr['source'], attr['target'], directed=edge_directed,
                       **dict([n for n in attr.items() if n[0] not in ('source', 'target')]))

    logger.info('Import graph in GEXF format. XMLNS: {0}'.format(xmlns))

    return graph


def write_gexf(graph, node_tools=GEXFNodeTools, edge_tools=GEXFEdgeTools):
    """
    Export a graph to an GEXF data format

    Custom XML serializers may be introduced as a custom NodeTools
    class using the `node_tools` attribute. In addition, the graph
    ORM may be used to inject tailored `serialize` methods in specific
    nodes or edges.

    :param graph:       Graph to export
    :type graph:        :graphit:Graph
    :param node_tools:  NodeTools class with node serialize method
    :type node_tools:   :graphit:NodeTools
    :param edge_tools:  EdgeTools class with node serialize method
    :type edge_tools:   :graphit:EdgeTools

    :return:            Graph exported as a hierarchical XML node structure
    :rtype:             :py:str
    """

    # Set current NodeTools and EdgeTools aside and register new one
    if not issubclass(node_tools, NodeTools):
        raise GraphitException('Node_tools ({0}) needs to inherit from the NodeTools class'.format(type(node_tools)))
    if not issubclass(edge_tools, EdgeTools):
        raise GraphitException('Edge_tools ({0}) needs to inherit from the NodeTools class'.format(type(edge_tools)))

    curr_nt = graph.node_tools
    curr_et = graph.edge_tools
    graph.node_tools = node_tools
    graph.edge_tools = edge_tools

    # Create GEXF root element and add meta-data
    root = et.Element('gexf')
    root.attrib = {'xmlns': 'http://www.gexf.net/1.2draft', 'version': '1.2',
                   'xmlns:xsi': graph.data.get('xmlns:xsi', 'http://www.w3/org/2001/XMLSchema-instance'),
                   'xsi.schemaLocation': graph.data.get('xsi.schemaLocation',
                                   'http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd')}

    root_meta = et.SubElement(root, 'meta')
    root_meta.attrib = {'lastmodifieddate': str(datetime.date.today())}
    for key, value in graph.data.items():
        if key not in ('mode', 'lastmodifieddate'):
            meta = et.SubElement(root_meta, key)
            meta.text = str(value)

    root_graph = et.SubElement(root, 'graph')
    root_graph.attrib = {'mode': graph.data.get('mode', 'static'),
                         'defaultedgetype': 'directed' if graph.directed else 'undirected'}

    # Add nodes
    if len(graph.nodes):
        root_nodes = et.SubElement(root_graph, 'nodes')
        for node in graph.iternodes():
            node.serialize(tree=root_nodes)

    # Add edges
    if len(graph.edges):
        root_edges = et.SubElement(root_graph, 'edges')
        for edge in graph.iteredges():
            edge.serialize(tree=root_edges)

    # Restore original NodeTools and EdgeTools
    graph.node_tools = curr_nt
    graph.edge_tools = curr_et

    # Return pretty printed XML using minidom.parseString
    return minidom.parseString(et.tostring(root)).toprettyxml(indent="   ")
