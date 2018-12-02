# -*- coding: utf-8 -*-

"""
file: module_combinatorial_setlike_test.py

Unit tests for graphit 'set' like math operations functions
"""

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph
from graphit.graph_combinatorial.graph_setlike_operations import *


class TestGraphCombinatorialSetlike(UnittestPythonCompatibility):

    def setUp(self):
        """
        Setup two graphs for combinatorial tests
        """

        self.graph1 = Graph(auto_nid=False)
        self.graph1.add_nodes(range(1, 11))
        self.graph1.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (5, 6), (4, 7), (6, 8), (7, 8), (8, 9), (9, 10)])

        self.graph2 = Graph(auto_nid=False)
        self.graph2.add_nodes(range(6, 16))
        self.graph2.add_edges([(6, 8), (7, 8), (8, 9), (9, 10), (10, 11), (10, 12), (12, 13), (11, 14), (13, 15),
                               (14, 15)])

    def test_combinatorial_intersection(self):
        """
        Test intersection between two graphs
        """

        intr = graph_intersection(self.graph1, self.graph2)

        self.assertItemsEqual(intr.nodes.keys(), range(6, 11))
        self.assertItemsEqual(intr.edges.keys(), [(8, 9), (6, 8), (9, 8), (9, 10), (8, 7), (8, 6), (7, 8), (10, 9)])

        self.assertFalse(intr.nodes.is_view)
        self.assertFalse(intr.edges.is_view)
        self.assertEqual(intr, intr.origin)

    def test_combinatorial_intersection_edgediff(self):
        """
        Test intersection between two graphs with a different edge population
        """

        self.graph2.remove_edge(8, 9)
        intr = graph_intersection(self.graph1, self.graph2)

        self.assertItemsEqual(intr.nodes.keys(), range(6, 11))
        self.assertItemsEqual(intr.edges.keys(), [(6, 8), (9, 10), (8, 7), (8, 6), (7, 8), (10, 9)])

        self.assertFalse(intr.nodes.is_view)
        self.assertFalse(intr.edges.is_view)
        self.assertEqual(intr, intr.origin)

    def test_combinatorial_difference(self):
        """
        Test difference between two graphs
        """

        diff = graph_difference(self.graph1, self.graph2)

        self.assertItemsEqual(diff.nodes.keys(), range(1, 6))
        self.assertItemsEqual(diff.edges.keys(), [(1, 2), (3, 2), (2, 1), (2, 3), (4, 3), (5, 3), (3, 4), (3, 5)])

        self.assertFalse(diff.nodes.is_view)
        self.assertFalse(diff.edges.is_view)
        self.assertEqual(diff, diff.origin)

        diff = graph_difference(self.graph2, self.graph1)

        self.assertItemsEqual(diff.nodes.keys(), range(11, 16))
        self.assertItemsEqual(diff.edges.keys(), [(14, 11), (13, 12), (15, 13), (12, 13), (13, 15), (14, 15), (11, 14),
                                                  (15, 14)])

        self.assertFalse(diff.nodes.is_view)
        self.assertFalse(diff.edges.is_view)
        self.assertEqual(diff, diff.origin)

    def test_combinatorial_difference_edgediff(self):
        """
        Test difference between two graphs using edge oriented difference.
        """

        diff = graph_difference(self.graph1, self.graph2, edge_diff=True)

        self.assertItemsEqual(diff.nodes.keys(), range(1, 8))
        self.assertItemsEqual(diff.edges.keys(), [(1, 2), (3, 2), (2, 1), (2, 3), (4, 3), (5, 3), (3, 4), (3, 5),
                                                  (5, 6), (6, 5), (4, 7), (7, 4)])

        self.assertFalse(diff.nodes.is_view)
        self.assertFalse(diff.edges.is_view)
        self.assertEqual(diff, diff.origin)

        diff = graph_difference(self.graph2, self.graph1, edge_diff=True)

        self.assertItemsEqual(diff.nodes.keys(), range(10, 16))
        self.assertItemsEqual(diff.edges.keys(), [(14, 11), (13, 12), (15, 13), (12, 13), (13, 15), (14, 15), (11, 14),
                                                  (15, 14), (10, 11), (11, 10), (10, 12), (12, 10)])

        self.assertFalse(diff.nodes.is_view)
        self.assertFalse(diff.edges.is_view)
        self.assertEqual(diff, diff.origin)

    def test_combinatorial_symmetric_difference(self):
        """
        Test symmetric difference between two graphs using edge oriented
        difference. Returns a new graph
        """

        diff = graph_symmetric_difference(self.graph1, self.graph2, edge_diff=True)

        self.assertItemsEqual(diff.nodes.keys(), [1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15])
        self.assertItemsEqual(diff.edges.keys(), [(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3), (3, 5), (5, 3),
                                                  (11, 14), (14, 11), (12, 13), (13, 12), (14, 15), (15, 14), (13, 15),
                                                  (15, 13), (4, 7), (7, 4), (5, 6), (6, 5), (10, 11), (11, 10),
                                                  (10, 12), (12, 10)])

        self.assertFalse(diff.nodes.is_view)
        self.assertFalse(diff.edges.is_view)
        self.assertEqual(diff, diff.origin)

    def test_combinatorial_symmetric_difference_edgediff(self):
        """
        Test symmetric difference between two graphs. Returns a new graph
        """

        diff = graph_symmetric_difference(self.graph1, self.graph2)

        self.assertItemsEqual(diff.nodes.keys(), [1, 2, 3, 4, 5, 11, 12, 13, 14, 15])
        self.assertItemsEqual(diff.edges.keys(), [(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3), (3, 5), (5, 3),
                                                  (11, 14), (14, 11), (12, 13), (13, 12), (14, 15), (15, 14), (13, 15),
                                                  (15, 13)])

        self.assertFalse(diff.nodes.is_view)
        self.assertFalse(diff.edges.is_view)
        self.assertEqual(diff, diff.origin)

    def test_combinatorial_union(self):
        """
        Test union between two graphs. Returns a new graph
        """

        union = graph_union(self.graph1, self.graph2)

        self.assertItemsEqual(union.nodes.keys(), range(1, 16))
        self.assertItemsEqual(union.edges.keys(), [(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3), (3, 5), (5, 3),
                                                       (5, 6), (6, 5), (4, 7), (7, 4), (6, 8), (8, 6), (7, 8), (8, 7),
                                                       (8, 9), (9, 8), (9, 10), (10, 9), (10, 11), (11, 10), (12, 10),
                                                       (10, 12), (12, 13), (13, 12), (11, 14), (14, 11), (13, 15),
                                                       (15, 13), (14, 15), (15, 14)])

        self.assertFalse(union.nodes.is_view)
        self.assertFalse(union.edges.is_view)
        self.assertEqual(union, union.origin)

    def test_combinatorial_issubset(self):
        """
        Test graph 1 issubset of graph 2
        """

        graph2 = Graph(auto_nid=False)
        graph2.add_nodes(range(7, 11))
        graph2.add_edges([(7, 8), (8, 9), (9, 10)])

        self.assertTrue(graph_issubset(graph2, self.graph1))
        self.assertFalse(graph_issubset(self.graph1, graph2))

    def test_combinatorial_issuperset(self):
        """
        Test graph 1 issuperset of graph 2
        """

        graph2 = Graph(auto_nid=False)
        graph2.add_nodes(range(7, 11))
        graph2.add_edges([(7, 8), (8, 9), (9, 10)])

        self.assertFalse(graph_issuperset(graph2, self.graph1))
        self.assertTrue(graph_issuperset(self.graph1, graph2))
