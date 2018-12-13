# -*- coding: utf-8 -*-

"""
file: module_compatibility_networkx_test.py

Unit tests for the compatibility of the NetworkXGraph with the NetworkX package
"""

no_nx = False
try:
    import networkx
except ImportError:
    no_nx = True

from unittest import skipIf
from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit.graph_networkx import NetworkXGraph


@skipIf(no_nx == True, 'NetworkX not installed, skipping compatibility tests')
class TestGraphNetworkxCompatibility(UnittestPythonCompatibility):
    """
    Unit tests for the compatibility of the NetworkXGraph with the NetworkX
    package.
    """

    def setUp(self):
        """
        Create same graph using Graphit and NetworkX
        """

        nodes = [1, 2, 3, 4, 5, 6, 7, 8]
        edges = [(1, 2), (2, 3), (2, 4), (3, 4), (5, 4), (6, 4), (5, 7), (7, 8)]

        self.gn = NetworkXGraph()
        self.gn.add_nodes(nodes)
        self.gn.add_edges(edges)

        self.nx = networkx.Graph()
        for node in nodes:
            self.nx.add_node(node, _id=node, key=node)
        self.nx.add_edges_from(edges)

    def test_graph_magic_methods(self):
        """
        Test similarity in graph class magic methods between graphit and networkx
        """

        # NetworkX has 3 different ways to get the length of a graph (number of nodes)
        self.assertEqual(len(self.gn), len(self.nx))
        self.assertEqual(self.gn.order(), self.nx.order())  # same as __len__
        self.assertEqual(self.gn.number_of_nodes(), self.nx.number_of_nodes())  # same as __len__

    def test_graph_directionality(self):

        self.assertEqual(self.gn.is_directed(), self.nx.is_directed())

    def test_graph_to_directional(self):

        nx_dir = self.nx.to_directed()
        gn_dir = self.gn.to_directed()

        self.assertTrue(nx_dir.is_directed())
        self.assertTrue(gn_dir.is_directed())

    def test_graph_nodes(self):

        print(self.nx.nodes)
        print(self.nx.nodes(data='_id'))
        print(repr(self.nx.nodes))
        print(self.nx.nodes.keys())
        print(self.nx.nodes.items())
        print(self.nx.nodes.values())

        self.assertListEqual(list(self.gn.nodes), list(self.nx.nodes))
        self.assertDictEqual(self.gn.nodes[2], self.nx.nodes[2])

    def test_graph_add_nodes(self):
        """
        Graphit has add_nodes and NetworkX add_nodes_from
        """

        gn = NetworkXGraph()
        gn.add_nodes_from([1, 2, 3, 4])

        nx = networkx.Graph()
        nx.add_nodes_from([1, 2, 3, 4])

        self.assertListEqual(list(gn.nodes), list(nx.nodes))

        gn.add_nodes_from([(5, {'test': True}), (6, {'test': False})])
        nx.add_nodes_from([(5, {'test': True}), (6, {'test': False})])

        d = nx.nodes[5]
        d.update({u'_id': 5, u'key': 5})
        self.assertDictEqual(gn.nodes[5], d)

    def test_graph_edges(self):
        """
        Edges are not equal because NetworkX stores a single edge to represent
        both directions in a undirectional graph while graphit stores both.
        """

        self.assertNotEqual(list(self.gn.edges), list(self.nx.edges))
        self.assertItemsEqual([e for e in self.gn.edges if e[0] < e[1]], list(self.nx.edges))

    def test_graph_add_edges(self):
        """
        Graphit has add_edges and NetworkX add_edges_from
        """

        gn = NetworkXGraph()
        gn.add_nodes([1, 2, 3, 4])
        gn.add_edges_from([(1, 2), (2, 3), (2, 4)])

        nx = networkx.Graph()
        nx.add_nodes_from([1, 2, 3, 4])
        nx.add_edges_from([(1, 2), (2, 3), (2, 4)])

        self.assertNotEqual(list(gn.edges), list(nx.edges))
        self.assertItemsEqual([e for e in gn.edges if e[0] < e[1]], list(nx.edges))

    def test_graph_remove_nodes(self):
        """
        Graphit has remove_nodes and NetworkX remove_nodes_from
        """

        self.gn.remove_nodes_from([3, 4])
        self.nx.remove_nodes_from([3, 4])

        self.assertListEqual(list(self.gn.nodes), list(self.nx.nodes))

    def test_graph_remove_edges(self):
        """
        Graphit has remove_edges and NetworkX remove_edges_from
        """

        self.gn.remove_edges_from([(1, 2), (2, 4)])
        self.nx.remove_edges_from([(1, 2), (2, 4)])

        self.assertNotEqual(list(self.gn.edges), list(self.nx.edges))
        self.assertItemsEqual([e for e in self.gn.edges if e[0] < e[1]], list(self.nx.edges))

    def test_graph_size(self):
        """
        Test 'size' which is a method in NetworkX and a function in Graphit
        """

        gn = NetworkXGraph()
        gn.add_edge('a', 'b', node_from_edge=True, weight=2)
        gn.add_edge('b', 'c', node_from_edge=True, weight=4)

        nx = networkx.Graph()
        nx.add_edge('a', 'b', weight=2)
        nx.add_edge('b', 'c', weight=4)

        self.assertEqual(gn.size(), nx.size())
        self.assertEqual(gn.size(weight='weight'), nx.size(weight='weight'))
        self.assertEqual(gn.number_of_edges(), nx.number_of_edges())

    def test_graph_attributes(self):

        for a in self.gn.nodes.items():
            print(a)
