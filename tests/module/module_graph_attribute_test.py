# -*- coding: utf-8 -*-

"""
file: module_graph_iteration_test.py

Unit tests for Graph node/edge attribute methods
"""

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph
from graphit.graph_exceptions import GraphitException


class TestGraphNodeAttribute(UnittestPythonCompatibility):
    """
    Test methods to get and set node attributes using a node storage driver.
    `DictStorage` is the default driver tested here.
    """

    def setUp(self):
        """
        Build default Graph with node and edge attributes
        """

        self.graph = Graph()
        self.graph.add_nodes([('g', {'weight': 1.0, 'value': 'gr'}), ('r', {'weight': 1.5, 'value': 'ra'}),
                              ('a', {'weight': 2.0, 'value': 'ap'}), ('p', {'weight': 2.5, 'value': 'ph'}),
                              ('h', {'weight': 3.0})])
        self.graph.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)], value=True, weight=43.2, key='edge')

    def test_graph_node_attr_storeget(self):
        """
        Test getting node attributes directly from the `nodes` storage
        """

        self.assertEqual(self.graph.nodes[1]['weight'], 1.0)
        self.assertEqual(self.graph.nodes[3]['value'], 'ap')

    def test_graph_node_attr_storeset(self):
        """
        Test setting node attributes directly from the `nodes` storage
        """

        self.graph.nodes[1]['weight'] = 5.0
        self.graph.nodes[3]['value'] = 'dd'

        self.assertEqual(self.graph.nodes[1]['weight'], 5.0)
        self.assertEqual(self.graph.nodes[3]['value'], 'dd')

    def test_graph_node_attr_key_tag(self):
        """
        Test get attributes based on `key_tag`
        """

        self.assertEqual(self.graph.nodes[1][self.graph.key_tag], 'g')
        self.assertEqual(self.graph.nodes[3][self.graph.key_tag], 'a')
        self.assertEqual(self.graph.get(1), 'g')  # uses default node data tag

    def test_graph_node_attr_value_tag(self):
        """
        Test get attributes based on `value_tag`
        """

        self.assertEqual(self.graph.nodes[1][self.graph.value_tag], 'gr')
        self.assertEqual(self.graph.nodes[3][self.graph.value_tag], 'ap')

    def test_graph_node_attr_dict(self):
        """
        Test if the returned full attribute dictionary is of expected format
        """

        self.assertDictEqual(self.graph.nodes[1], {'_id': 1, 'key': 'g', 'weight': 1.0, 'value': 'gr'})
        self.assertDictEqual(self.graph.nodes[3], {'_id': 3, 'key': 'a', 'weight': 2.0, 'value': 'ap'})

    def test_graph_node_attr_exception(self):
        """
        Test `nodes` exception if node not present
        """

        self.assertRaises(GraphitException, self.graph.__getitem__, 10)
        self.assertIsNone(self.graph.nodes.get(10))

    def test_graph_node_attr_graphget(self):
        """
        Test access node attributes by nid using the (sub)graph 'get' method
        """

        self.assertEqual(self.graph.get(4), 'p')
        self.assertEqual(self.graph.get(4, 'weight'), 2.5)

        # Key does not exist
        self.assertIsNone(self.graph.get(4, key='no_key'))

        # Key does not exist return defaultkey
        self.assertEqual(self.graph.get(4, key='no_key', defaultattr='weight'), 2.5)

    def test_graph_node_attr_singlenode_get(self):
        """
        Test getting node attribute values directly using the single node
        Graph API which has the required methods (node_tools) added to it.
        """

        node = self.graph.getnodes(5)
        self.assertEqual(node['key'], 'h')
        self.assertEqual(node.key, 'h')
        self.assertEqual(node.get('key'), 'h')

        self.assertEqual(node['weight'], 3.0)
        self.assertEqual(node.weight, 3.0)
        self.assertEqual(node.get('weight'), 3.0)

    def test_graph_node_attr_singlenode_set(self):
        """
        Test setting node attribute values directly using the single node
        Graph API which has the required methods (node_tools) added to it.
        """

        node = self.graph.getnodes(5)
        node.weight = 5.0
        node['key'] = 'z'
        node.set('value', True)

        self.assertEqual(node.nodes[5]['weight'], 5.0)
        self.assertEqual(node.nodes[5]['key'], 'z')
        self.assertEqual(node.nodes[5]['value'], True)

    def test_graph_node_attr_singlenode_exception(self):
        """
        Test exceptions in direct access to node attributes in a single graph
        class
        """

        node = self.graph.getnodes(5)
        self.assertEqual(node.get(), None)  # Default get returns value, not set
        self.assertRaises(KeyError, node.__getitem__, 'no_key')
        self.assertRaises(AttributeError, node.__getattr__, 'no_key')

    def test_graph_nodes_dict_keys(self):
        """
        Test graph dict-like 'keys' support.
        """

        self.assertListEqual(self.graph.keys(), ['g', 'r', 'a', 'p', 'h'])
        self.assertListEqual(self.graph.keys('weight'), [1.0, 1.5, 2.0, 2.5, 3.0])

    def test_graph_nodes_dict_values(self):
        """
        Test graph dict-like 'values' support.
        """

        self.assertListEqual(self.graph.values(), ['gr', 'ra', 'ap', 'ph', None])
        self.assertItemsEqual(self.graph.values('no_value'), [None, None, None, None, None])

    def test_graph_nodes_dict_items(self):
        """
        Test graph dict-like 'items' support.
        """

        self.assertItemsEqual(self.graph.items(), [('g', 'gr'), ('r', 'ra'), ('a', 'ap'), ('p', 'ph'), ('h', None)])
        self.assertItemsEqual(self.graph.items(valuestring='_id'), [('g', 1), ('r', 2), ('a', 3), ('p', 4), ('h', 5)])
        self.assertItemsEqual(self.graph.items(keystring='_id', valuestring='weight'), [(1, 1.0), (2, 1.5), (3, 2.0),
                                                                                        (4, 2.5), (5, 3.0)])


class TestGraphEdgeAttribute(UnittestPythonCompatibility):
    """
    Test methods to get and set edge attributes using an edge storage driver.
    `DictStorage` is the default driver tested here which happens to be the
    same as for nodes.
    """

    def setUp(self):
        """
        Build default Graph with node and edge attributes
        """

        self.graph = Graph()
        self.graph.add_nodes([('g', {'weight': 1.0, 'value': 'gr'}), ('r', {'weight': 1.5, 'value': 'ra'}),
                              ('a', {'weight': 2.0, 'value': 'ap'}), ('p', {'weight': 2.5, 'value': 'ph'}),
                              ('h', {'weight': 3.0})])
        self.graph.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)], value=True, weight=43.2, key='edge')

    def test_graph_edge_attr_storeget(self):
        """
        Test getting edge attributes directly from the `edges` storage
        """

        self.assertEqual(self.graph.edges[(1, 2)]['value'], True)
        self.assertEqual(self.graph.edges[(1, 2)]['weight'], 43.2)

    def test_graph_edge_attr_storeset(self):
        """
        Test setting node attributes directly from the `edges` storage
        """

        self.graph.edges[(1, 2)]['weight'] = 5.0
        self.graph.edges[(2, 3)]['value'] = 'dd'

        self.assertEqual(self.graph.edges[(1, 2)]['weight'], 5.0)
        self.assertEqual(self.graph.edges[(2, 3)]['value'], 'dd')

    def test_graph_edge_attr_key_tag(self):
        """
        Test get attributes based on `key_tag`
        """

        self.assertEqual(self.graph.edges[(1, 2)][self.graph.key_tag], 'edge')
        self.assertEqual(self.graph.get((1, 2)), 'edge')  # uses default node data tag

    def test_graph_edge_attr_value_tag(self):
        """
        Test get attributes based on `value_tag`
        """

        self.assertEqual(self.graph.edges[(4, 5)][self.graph.value_tag], True)

    def test_graph_edge_attr_dict(self):
        """
        Test if the returned full attribute dictionary is of expected format
        """

        self.assertDictEqual(self.graph.edges[(4, 5)], {'value': True, 'weight': 43.2, 'key': 'edge'})

    def test_graph_edge_attr_exception(self):
        """
        Test `edges` exception if edge not present
        """

        self.assertRaises(GraphitException, self.graph.__getitem__, (5, 6))
        self.assertIsNone(self.graph.nodes.get((5, 6)))

    def test_graph_edge_attr_graphget(self):
        """
        Test access edge attributes by nid using the (sub)graph 'get' method
        """

        self.assertEqual(self.graph.get((1, 2)), 'edge')
        self.assertEqual(self.graph.get((1, 2), 'weight'), 43.2)

        # Key does not exist
        self.assertIsNone(self.graph.get((1, 2), key='no_key'))

        # Key does not exist return defaultkey
        self.assertEqual(self.graph.get((1, 2), key='no_key', defaultattr='weight'), 43.2)

    def test_graph_edge_attr_singleedge_set(self):
        """
        Test setting edge attribute values directly using the single edge
        Graph API which has the required methods (edge_tools) added to it.
        """

        edge = self.graph.getedges((1, 2))
        edge.weight = 4.5
        edge['key'] = 'edge_set'
        edge.set('value', False)

        self.assertEqual(edge.edges[(1, 2)]['weight'], 4.5)
        self.assertEqual(edge.edges[(1, 2)]['key'], 'edge_set')
        self.assertEqual(edge.edges[(1, 2)]['value'], False)

    def test_graph_edge_attr_singleedge_exception(self):
        """
        Test exceptions in direct access to edge attributes in a single graph
        class
        """

        edge = self.graph.getedges((1, 2))

        self.assertEqual(edge.get(), True)
        self.assertRaises(KeyError, edge.__getitem__, 'no_key')
        self.assertRaises(AttributeError, edge.__getattr__, 'no_key')

    def test_graph_edge_attr_undirectional(self):
        """
        Undirectional edge has one attribute store
        """

        # True for DictStorage but may be different for other drivers
        self.assertEqual(id(self.graph.edges[(1, 2)]), id(self.graph.edges[(2, 1)]))

        self.assertDictEqual(self.graph.edges[(1, 2)], self.graph.edges[(2, 1)])

        self.graph.edges[(1, 2)]['key'] = 'edge_modified'
        self.assertTrue(self.graph.edges[(2, 1)]['key'] == 'edge_modified')

    def test_graph_edge_attr_directional(self):
        """
        Directional edge has two separated attribute stores
        """

        self.graph.add_edge(2, 5, directed=True, attr='to')
        self.graph.add_edge(5, 2, directed=True, attr='from')

        # True for DictStorage but may be different for other drivers
        self.assertNotEqual(id(self.graph.edges[(2, 5)]), id(self.graph.edges[(5, 2)]))

        self.assertNotEqual(self.graph.edges[(2, 5)], self.graph.edges[(5, 2)])

        self.graph.edges[(5, 2)]['attr'] = 'return'
        self.assertTrue(self.graph.edges[(2, 5)]['attr'] == 'to')
        self.assertTrue(self.graph.edges[(5, 2)]['attr'] == 'return')
