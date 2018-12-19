# -*- coding: utf-8 -*-

"""
file: module_io_test.py

Unit tests for import and export of graph data formats
"""

import os
import unittest

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph, GraphAxis
from graphit.graph_py2to3 import PY_STRING
from graphit.graph_helpers import graph_directionality
from graphit.graph_io.io_tgf_format import read_tgf, write_tgf
from graphit.graph_io.io_jgf_format import read_jgf, write_jgf
from graphit.graph_io.io_pydata_format import read_pydata, write_pydata
from graphit.graph_io.io_web_format import read_web, write_web
from graphit.graph_io.io_jsonschema_format import read_json_schema
from graphit.graph_io.io_jsonschema_format_drafts import GraphitValidationError

FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../files/'))

# Check if PyYAML is installed
try:
    from graphit.graph_io.io_yaml_format import read_yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class FloatArray(object):

    def set(self, key, value):
        if not isinstance(value, list):
            raise AssertionError

        float_array = []
        for v in value:
            float_array.append(float(v))

        self.nodes[self.nid][key] = float_array


class WebParserTest(UnittestPythonCompatibility):
    """
    Unit tests for parsing Spider serialized data structures (.web format)
    """

    web_file = os.path.join(FILEPATH, 'graph.web')
    tempfiles = []

    def tearDown(self):
        """
        tearDown method called after each unittest to cleanup
        the files directory
        """

        for tmp in self.tempfiles:
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_format_import(self):
        """
        Test import of format
        """

        graph = read_web(self.web_file, auto_parse_format=False)

        # Default graph attributes set
        self.assertEqual(len(graph), 694)
        self.assertEqual(len(graph.edges), 1386)
        self.assertEqual(graph.directed, False)
        self.assertEqual(graph_directionality(graph), 'undirectional')
        self.assertEqual(graph.root, 1)
        self.assertTrue(isinstance(graph, GraphAxis))

        # No ORM or format auto detect set, all values should be strings
        self.assertTrue(isinstance(graph.query_nodes({'key': 'ntrials'}).value, PY_STRING))
        self.assertTrue(isinstance(graph.query_nodes({'key': 'rotate180_0'}).value, PY_STRING))

        for node in graph.query_nodes({'key': 'activereslist'}):
            self.assertTrue(isinstance(node.value, list))

        for node in graph.query_nodes({'type': 'FloatArray'}):
            self.assertTrue(all([isinstance(n, str) for n in node.get()]))

    def test_format_import_autoformatparse(self):
        """
        Test import of format with automatic parsing of data types (default)
        """

        graph = read_web(self.web_file)

        self.assertTrue(isinstance(graph.query_nodes({'key': 'ntrials'}).value, int))
        self.assertTrue(isinstance(graph.query_nodes({'key': 'rotate180_0'}).value, bool))

        for node in graph.query_nodes({'key': 'activereslist'}):
            self.assertTrue(isinstance(node.value, list))

        for node in graph.query_nodes({'type': 'FloatArray'}):
            self.assertTrue(all([isinstance(n, float) for n in node.get()]))

    def test_format_import_orm(self):
        """
        Test import of format with custom ORM classes
        """

        web = GraphAxis()
        web.orm.node_mapping.add(FloatArray, lambda x: x.get('type') == 'FloatArray')
        web = read_web(self.web_file, graph=web)

        for node in web.query_nodes({'type': 'FloatArray'}):
            self.assertTrue(all([isinstance(n, str) for n in node.get()]))

    def test_format_export(self):
        """
        Test export of format
        """

        graph = read_web(self.web_file)

        # Export graph as .web to file
        web = write_web(graph)
        outfile = os.path.join(FILEPATH, 'test_export.web')
        with open(outfile, 'w') as otf:
            otf.write(web)
            self.tempfiles.append(outfile)

        self.assertTrue(os.path.isfile(outfile))

        # Import again and compare source graph
        graph1 = read_web(outfile)
        self.assertEqual(len(graph), len(graph1))
        self.assertEqual(len(graph.edges), len(graph1.edges))


class TGFParserTest(UnittestPythonCompatibility):
    """
    Unit tests for parsing graphs in Trivial Graph Format (TGF)
    """
    tempfiles = []

    def tearDown(self):
        """
        tearDown method called after each unittest to cleanup
        the files directory
        """

        for tmp in self.tempfiles:
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_format_import(self):
        """
        Test import of format
        """

        tgf_file = os.path.join(FILEPATH, 'graph.tgf')
        graph = read_tgf(tgf_file)

        # Default graph attributes set
        self.assertEqual(len(graph), 11)
        self.assertEqual(len(graph.edges), 11)
        self.assertEqual(graph.directed, False)
        self.assertEqual(graph_directionality(graph), 'directional')
        self.assertEqual(graph.root, None)
        self.assertTrue(isinstance(graph, Graph))

        # auto_nid is False, arbitrary node ID's supported
        self.assertTrue('eleven' in graph.nodes)
        self.assertTrue(10 in graph.nodes)

    def test_format_export(self):
        """
        Test export of format
        """

        tgf_file = os.path.join(FILEPATH, 'graph.tgf')
        graph = read_tgf(tgf_file)

        # Export graph as TGF to file
        tgf = write_tgf(graph)
        outfile = os.path.join(FILEPATH, 'test_export.tgf')
        with open(outfile, 'w') as otf:
            otf.write(tgf)
            self.tempfiles.append(outfile)

        self.assertTrue(os.path.isfile(outfile))

        # Import again and compare source graph
        graph1 = read_tgf(outfile)

        self.assertTrue(graph1 == graph)

    def test_format_custom_import(self):
        """
        Test TGF import with custom Graph instance
        """

        # Graph axis class with custom nid ID's
        graph = GraphAxis()
        graph.auto_nid = False
        graph.directed = True

        tgf_file = os.path.join(FILEPATH, 'graph.tgf')
        graph = read_tgf(tgf_file, graph=graph)

        # Custom graph attributes set and string based node IDs supported
        self.assertEqual(len(graph), 11)
        self.assertEqual(len(graph.edges), 11)
        self.assertEqual(graph.directed, True)
        self.assertEqual(graph_directionality(graph), 'directional')
        self.assertTrue(isinstance(graph, GraphAxis))
        self.assertTrue('eleven' in graph.nodes)


class JGFParserTest(UnittestPythonCompatibility):
    """
    Unit tests for parsing graphs in graphit module specific JSON format
    (.jgf file format)
    """
    tempfiles = []

    def tearDown(self):
        """
        tearDown method called after each unittest to cleanup
        the files directory
        """

        for tmp in self.tempfiles:
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_format_import(self):
        """
        Test import of format. The graph defines a root and thus will be
        imported as a GraphAxis object.
        """

        jgf_file = os.path.join(FILEPATH, 'graph_axis.jgf')
        graph = read_jgf(jgf_file)

        # Default graph attributes set
        self.assertEqual(len(graph), 35)
        self.assertEqual(len(graph.edges), 72)
        self.assertEqual(graph.directed, False)
        self.assertEqual(graph_directionality(graph), 'undirectional')
        self.assertEqual(graph.root, 1)
        self.assertTrue(isinstance(graph, GraphAxis))

        # Because default auto_nid is True, string based node IDs not supported
        self.assertTrue('eleven' not in graph.nodes)
        self.assertTrue(11 in graph.nodes)

    def test_format_export(self):
        """
        Test export of format
        """

        jgf_file = os.path.join(FILEPATH, 'graph_axis.jgf')
        graph = read_jgf(jgf_file)

        # Export graph as JSON to file
        jgfout = write_jgf(graph)
        outfile = os.path.join(FILEPATH, 'test_export.jgf')
        with open(outfile, 'w') as otf:
            otf.write(jgfout)
            self.tempfiles.append(outfile)

        self.assertTrue(os.path.isfile(outfile))

        # Import again and compare source graph
        graph1 = read_jgf(outfile)
        self.assertTrue(graph1 == graph)


class PydataParserTest(UnittestPythonCompatibility):
    """
    Unit test for parsing a Python data structure to a graph and vice versa

    NOTE: Python data structure parsers are customizable. Users can choose
    which data gets added as nodes or as node attributes.
    For the example below the parser level is set to 0 which indicates that
    every dictionary key/value pair is added as a node to the graph.
    The other option would be level 1 in which key/value pairs at the same
    level get added as node attributes and each nested structure gets added
    as new node.
    """
    test_dict = {'one': 1, 'two': {'value': 2, 'extra': True}, 'three': {'value': 3, 'extra': False},
                 4: {'value': 'four', 'five': {'value': 5, 'extra': [2.22, 4.67]}}}

    def test_format_import(self):
        """
        Test import of format.
        """

        graph = read_pydata(self.test_dict, level=0)

        # Default graph attributes set
        self.assertEqual(len(graph), 15)
        self.assertEqual(len(graph.edges), 28)
        self.assertEqual(graph.directed, False)
        self.assertEqual(graph_directionality(graph), 'undirectional')
        self.assertEqual(graph.root, 1)
        self.assertTrue(isinstance(graph, GraphAxis))

        # Because default auto_nid is True, string based node IDs not supported
        self.assertTrue('three' not in graph.nodes)
        self.assertTrue(8 in graph.nodes)

        # Test hierarchy
        self.assertItemsEqual(graph.children().keys(desc=False), [4, u'one', u'three', u'two'])
        self.assertItemsEqual(graph.leaves().values(), [2.22, 4.67, 5, u'four', 1, False, 3, True, 2])
        self.assertEqual(graph.getnodes(7).value, 5)

        query = graph.query_nodes({'key': 'five'})
        self.assertEqual(query.children().items(), [('extra', graph.getnodes(4)), ('value', 5)])

    def test_format_export(self):
        """
        Test export of format
        """

        graph = read_pydata(self.test_dict, level=0)

        # Export to dict again
        export = write_pydata(graph)
        self.assertDictEqual(export, self.test_dict)

        # Export including root
        export = write_pydata(graph, include_root=True)
        self.assertDictEqual(export, {'root': self.test_dict})


class JSONSchemaParserTests(UnittestPythonCompatibility):

    def test_jsonschema_import(self):
        """
        Test import of JSON schema
        """

        schema = os.path.join(FILEPATH, 'jsonschema1.json',)
        graph = read_json_schema(schema)

        # Test "enum" validation keyword
        node = graph.query_nodes(key='fstype')
        self.assertRaises(GraphitValidationError, node.set, 'value', 'ff')


@unittest.skipIf(HAS_YAML == False, 'PyYAML package not installed')
class YAMLParserTests(UnittestPythonCompatibility):

    def test_yaml_import(self):
        """
        Test import of JSON schema
        """

        schema = os.path.join(FILEPATH, 'graph.yaml',)
        graph = read_yaml(schema)

        self.assertItemsEqual(graph.children().keys(), [u'martin', u'tabitha'])
