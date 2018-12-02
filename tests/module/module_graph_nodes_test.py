# -*- coding: utf-8 -*-

"""
file: module_graph_nodes_test.py

Unit tests for Graph node related methods
"""

import os

from tests.module.unittest_baseclass import UnittestPythonCompatibility, UNICODE_TYPE

from graphit import Graph
from graphit.graph import GraphitException


class TestGraphAddNode(UnittestPythonCompatibility):
    """
    Test Graph add_node method with the Graph.auto_nid set to False
    mimicking the behaviour of many popular graph packages
    """
    currpath = os.path.dirname(__file__)
    image = os.path.join(currpath, '../', 'files', 'graph_tgf.png')

    def setUp(self):
        """
        Build empty graph to add a node to and test default state
        """

        self.graph = Graph(auto_nid=False)

        # empty before addition
        self.assertTrue(len(self.graph) == 0)
        self.assertTrue(len(self.graph.nodes) == 0)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 0)

        # auto_nid
        self.assertFalse(self.graph.auto_nid)

    def tearDown(self):
        """
        Test state after node addition
        """

        nid = list(self.graph.nodes)

        # The nid should equal the node
        self.assertEqual(nid, [self.node])

        # The _id is still set
        self.assertEqual(self.graph.nodes[self.node]['_id'], 1)
        self.assertEqual(self.graph._nodeid, 2)

        # filled after addition
        self.assertTrue(len(self.graph) == 1)
        self.assertTrue(len(self.graph.nodes) == 1)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 1)

        # no adjacency
        self.assertTrue(len(self.graph.adjacency[nid[0]]) == 0)

        # node key
        self.assertItemsEqual(self.graph.keys(), [self.node])

    def test_add_node_string(self):
        """
        Test adding a single node, string type
        """

        self.node = 'first'
        nid = self.graph.add_node(self.node)

        # Added string should be unicode
        self.assertIsInstance(self.graph.nodes[nid][self.graph.key_tag], UNICODE_TYPE)

    def test_add_node_int(self):
        """
        Test adding a single node, int type
        """

        self.node = 100
        self.graph.add_node(self.node)

    def test_add_node_float(self):
        """
        Test adding a single node, float type
        """

        self.node = 4.55
        self.graph.add_node(self.node)

    def test_add_node_bool(self):
        """
        Test adding a single node, float bool
        """

        self.node = False
        self.graph.add_node(self.node)

    def test_add_node_function(self):
        """
        Test adding a single node, function type
        """

        self.node = map
        self.graph.add_node(self.node)

    def test_add_node_object(self):
        """
        Test adding an object as a single node.
        In this case the object is file
        """

        self.node = open(self.image, 'r')
        self.graph.add_node(self.node)


class TestGraphAddNodeAutonid(UnittestPythonCompatibility):
    """
    Test Graph add_node method using different input with the Graph class
    set to default auto_nid = True
    """
    currpath = os.path.dirname(__file__)
    image = os.path.join(currpath, '../', 'files', 'graph_tgf.png')

    def setUp(self):
        """
        Build empty graph to add a node to and test default state
        """

        self.graph = Graph()

        # empty before addition
        self.assertTrue(len(self.graph) == 0)
        self.assertTrue(len(self.graph.nodes) == 0)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 0)

        # auto_nid
        self.assertTrue(self.graph.auto_nid)
        self.assertEqual(self.graph._nodeid, 1)

    def tearDown(self):
        """
        Test state after node addition
        """

        nid = list(self.graph.nodes)

        # auto_nid
        self.assertItemsEqual(nid, [1])
        self.assertEqual(self.graph._nodeid, 2)

        # filled after addition
        self.assertTrue(len(self.graph) == 1)
        self.assertTrue(len(self.graph.nodes) == 1)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 1)

        # no adjacency
        self.assertTrue(len(self.graph.adjacency[nid[0]]) == 0)

        # node key
        self.assertItemsEqual(self.graph.keys(), [self.node])

    def test_add_node_string(self):
        """
        Test adding a single node, string type
        """

        self.node = 'first'
        nid = self.graph.add_node(self.node)

        # Added string should be unicode
        self.assertIsInstance(self.graph.nodes[nid][self.graph.key_tag], UNICODE_TYPE)

    def test_add_node_int(self):
        """
        Test adding a single node, int type
        """

        self.node = 100
        self.graph.add_node(self.node)

    def test_add_node_float(self):
        """
        Test adding a single node, float type
        """

        self.node = 4.55
        self.graph.add_node(self.node)

    def test_add_node_bool(self):
        """
        Test adding a single node, float bool
        """

        self.node = False
        self.graph.add_node(self.node)

    def test_add_node_function(self):
        """
        Test adding a single node, function type
        """

        self.node = map
        self.graph.add_node(self.node)

    def test_add_node_list(self):
        """
        Test adding a single node, list type
        """

        self.node = [1.22, 4.5, 6]
        self.graph.add_node(self.node)

    def test_add_node_set(self):
        """
        Test adding a single node, set type
        """

        self.node = {1.22, 4.5, 6}
        self.graph.add_node(self.node)

    def test_add_node_object(self):
        """
        Test adding an object as a single node.
        In this case the object is file
        """

        self.node = open(self.image, 'rb')
        self.graph.add_node(self.node)

    def test_add_node_image(self):
        """
        Test adding an object as a single node.
        In this case the object is file and we do not convert it to unicode
        """

        self.node = open(self.image, 'rb').read()
        self.graph.add_node(self.node, unicode_convert=False)


class TestGraphAddNodesAutonid(UnittestPythonCompatibility):
    """
    Test Graph the add_nodes method using different input with the Graph class
    set to default auto_nid = True
    """

    def setUp(self):
        """
        Build empty graph to add nodes to and test default state
        """

        self.graph = Graph()

        # empty before addition
        self.assertTrue(len(self.graph) == 0)
        self.assertTrue(len(self.graph.nodes) == 0)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 0)

        # auto_nid
        self.assertTrue(self.graph.auto_nid)
        self.assertEqual(self.graph._nodeid, 1)

    def tearDown(self):
        """
        Test state after node addition
        """

        length = len(self.itr)
        nids = range(1, length+1)

        # auto_nid
        self.assertItemsEqual(list(self.graph.nodes), nids)
        self.assertEqual(self.graph._nodeid, length+1)

        # filled after addition
        self.assertTrue(len(self.graph) == length)
        self.assertTrue(len(self.graph.nodes) == length)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == length)

        # node key
        self.assertItemsEqual(self.graph.keys(), self.itr)

    def test_add_nodes_from_list(self):
        """
        Test adding multiple nodes from a list
        """

        self.itr = [1, 2, 3]
        self.graph.add_nodes(self.itr)

    def test_add_nodes_from_tuple(self):
        """
        Test adding multiple nodes from a tuple
        """

        self.itr = [1, 2, 3]
        self.graph.add_nodes(tuple(self.itr))

    def test_add_nodes_from_set(self):
        """
        Test adding multiple nodes from a set
        """

        self.itr = [1, 2, 3]
        self.graph.add_nodes(set(self.itr))

    def test_add_nodes_from_dict(self):
        """
        Test adding multiple nodes from a dict
        """

        self.itr = [1, 2, 3]
        self.graph.add_nodes({1: 'one', 2: 'two', 3: 'three'})

    def test_add_nodes_from_string(self):
        """
        Test adding multiple nodes from a string
        """

        self.itr = ['g', 'r', 'a', 'p', 'h']
        self.graph.add_nodes(''.join(self.itr))

    def test_add_nodes_from_range(self):
        """
        Test adding multiple nodes from a range
        """

        self.itr = range(5)
        self.graph.add_nodes(self.itr)

    def test_add_nodes_from_graph(self):
        """
        Test adding multiple nodes from another graph
        """

        self.itr = [1, 2, 3]
        g = Graph()
        g.add_nodes(self.itr)

        self.graph.add_nodes(g.nodes)


class TestGraphAddNodeExceptionWarning(UnittestPythonCompatibility):
    """
    Test logged warnings and raised Exceptions by Graph add_node.
    Same as for add_nodes
    """

    def setUp(self):
        """
        Build empty graph to add a node to and test default state
        """

        self.graph = Graph()

    def test_add_node_none(self):
        """
        Unable to add 'None' node when auto_nid False
        """

        # no problem when auto_nid
        self.graph.add_node()
        self.assertTrue(len(self.graph) == 1)

        self.graph.auto_nid = False
        self.assertRaises(GraphitException, self.graph.add_node, None)

    def test_add_node_hasable(self):
        """
        When auto_nid equals False, the nid should be a hashable object
        :return:
        """

        self.graph.auto_nid = False
        self.assertRaises(GraphitException, self.graph.add_node, [1, 2])

    def test_add_node_duplicate(self):
        """
        Duplication is no problem with auto_nid but without the previous node
        is updated with the attributes of the new one. A warning is logged.
        """

        # With auto_nid
        self.graph.add_nodes([1, 1])
        self.assertEqual(len(self.graph), 2)

        # Without auto_nid
        self.graph.auto_nid = False
        self.graph.add_nodes([3, 3])
        self.assertEqual(len(self.graph), 3)

        self.assertItemsEqual(self.graph.keys(), [1, 1, 3])
        self.assertItemsEqual(self.graph.keys('_id'), [1, 2, 3])


class TestGraphAddNodeAttributes(UnittestPythonCompatibility):
    """
    Test additional attribute storage for Graph add_node
    """

    def setUp(self):
        """
        Build empty graph to add a node to and test default state
        """

        self.graph = Graph()

    def tearDown(self):
        """
        Test state after node addition
        """

        self.attr.update({'_id': 1, self.graph.key_tag: 10})
        self.assertDictEqual(self.graph.nodes[1], self.attr)

    def test_add_node_no_attribute(self):
        """
        No attributes added should yield the default '_id' and 'key'
        """

        self.attr = {}
        self.graph.add_node(10, **self.attr)

    def test_add_node_single_attribute(self):
        """
        Add a single attribute
        """

        self.attr = {'weight': 2.33}
        self.graph.add_node(10, **self.attr)

    def test_add_node_multiple_attribute(self):
        """
        Add a multiple attributes
        """

        self.attr = {'test': True, 'pv': 1.44}
        self.graph.add_node(10, **self.attr)

    def test_add_node_protected_attribute(self):
        """
        The '_id' attribute is protected
        """

        self.attr = {}
        self.graph.add_node(10, _id=5)

    def test_add_node_nested_attribute(self):
        """
        Test adding nested attributed, e.a. dict in dict
        """

        self.attr = {'func': len, 'nested': {'weight': 1.22, 'leaf': True}}
        self.graph.add_node(10, **self.attr)


class TestGraphAddNodesAttributes(UnittestPythonCompatibility):
    """
    Test additional attribute storage for Graph add_nodes
    """

    def setUp(self):
        """
        Build empty graph to add a node to and test default state
        """

        self.graph = Graph()

    def tearDown(self):
        """
        Test state after node addition
        """

        match = [set(self.attr.items()).issubset(set(n.items())) for n in self.graph.nodes.values()]
        self.assertTrue(all(match))

    def test_add_nodes_single_attribute(self):
        """
        Test adding identical attribute for all nodes using add_nodes
        """

        self.attr = {'weight': 2.33}
        self.graph.add_nodes('graph', **self.attr)

    def test_add_nodes_attribute_dict(self):
        """
        Test adding multiple nodes with unique attributes using a tuple in add_nodes
        """

        self.attr = {}
        nodes = [('g', {'weight': 1.0}), ('r', {'weight': 1.5}), ('a', {'weight': 2.0}),
                 ('p', {'weight': 2.5}), ('h', {'weight': 3.0, 'pv': True})]
        self.graph.add_nodes(nodes)

        match = []
        for i in nodes:
            for node in self.graph.nodes.values():
                if node[self.graph.key_tag] == i[0]:
                    match.append(set(i[1].items()).issubset(set(node.items())))
        self.assertTrue(all(match))

    def test_add_nodes_attribute_dict2(self):
        """
        Test adding multiple nodes with unique attributes using a tuple in add_nodes
        Also add one attribute that is identical everywhere
        """

        self.attr = {}
        nodes = [('g', {'weight': 1.0}), ('r', {'weight': 1.5}), ('a', {'weight': 2.0}),
                 ('p', {'weight': 2.5}), ('h', {'weight': 3.0, 'pv': True})]
        self.graph.add_nodes(nodes, extra='yes')

        match = []
        for i in nodes:
            i[1]['extra'] = 'yes'
            for node in self.graph.nodes.values():
                if node[self.graph.key_tag] == i[0]:
                    match.append(set(i[1].items()).issubset(set(node.items())))
        self.assertTrue(all(match))


class TestGraphRemoveNodes(UnittestPythonCompatibility):
    """
    Test removal of single or multiple nodes
    """

    def setUp(self):
        """
        Build default graph with few nodes and edges
        """

        self.graph = Graph()
        self.graph.add_nodes('graph', isnode=True)
        self.graph.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)], isedge=True)

    def tearDown(self):
        """
        Test state after node remove
        """

        for node in self.to_remove:
            self.assertTrue(node not in self.graph.nodes)

            # node not in edges
            self.assertTrue(all([node not in e for e in self.graph.edges]))

            # node not in adjacency
            self.assertTrue(node not in self.graph.adjacency)
            self.assertTrue(all([node not in a for a in self.graph.adjacency.values()]))

        # Nodes not in removed should still be there
        for node in {1, 2, 3, 4, 5}.difference(set(self.to_remove)):
            self.assertTrue(node in self.graph.nodes)
            self.assertTrue(node in self.graph.adjacency)

    def test_remove_node(self):
        """
        Test removal of single node
        """

        self.to_remove = [3]
        self.graph.remove_node(self.to_remove[0])

    def test_remove_nodes(self):
        """
        Test removal of multiple nodes
        """

        self.to_remove = [1, 3, 4]
        self.graph.remove_nodes(self.to_remove)

    def test_graph_clear(self):
        """
        Test clear method to removal all nodes and edges
        """

        self.to_remove = [1, 2, 3, 4, 5]
        self.graph.clear()

        self.assertTrue(len(self.graph) == 0)
        self.assertTrue(len(self.graph.nodes) == 0)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 0)
