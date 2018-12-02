# -*- coding: utf-8 -*-

"""
file: module_graph_iteration_test.py

Unit tests for Graph iteration related methods
"""

import types

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph


class TestGraphIteration(UnittestPythonCompatibility):
    """
    Test methods for iteration over nodes and edges in a graph
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

    def test_iterators_isgenerator(self):
        """
        Node and edge iterators return a generator
        """

        self.assertTrue(isinstance(self.graph.iternodes(), types.GeneratorType))
        self.assertTrue(isinstance(self.graph.iteredges(), types.GeneratorType))

    def test_iterators_iternodes(self):
        """
        Iternodes returns single node graphs based on sorted node ID which in
        case of auto_nid returns the nodes in the order they where added.
        """

        for i, n in enumerate(self.graph.iternodes(), start=1):
            self.assertIsInstance(n, Graph)
            self.assertEqual(n.nid, i)

        # The Graph '__iter__' magic method points to iternodes
        for i, n in enumerate(self.graph, start=1):
            self.assertIsInstance(n, Graph)
            self.assertEqual(n.nid, i)

    def test_iterators_iternodes_reversed(self):
        """
        Iterate over nodes in reversed order based on node ID
        """

        self.assertListEqual([n.nid for n in self.graph.iternodes(reverse=True)], [5, 4, 3, 2, 1])

    def test_iterators_iternodes_subgraph(self):
        """
        Iternodes on a subgraph will only iterate over the nodes in the subgraph
        """

        sub = self.graph.getnodes([1, 3, 4])
        self.assertEqual(len(sub), 3)
        self.assertEqual([n.nid for n in sub.iternodes()], [1, 3, 4])
        self.assertEqual([n.nid for n in sub], [1, 3, 4])

    def test_iterators_iteredges(self):
        """
        Iteredges returns single edge graphs based on sorted edge ID.
        """

        edges = []
        for e in self.graph.iteredges():
            self.assertIsInstance(e, Graph)
            edges.append(e.nid)

        self.assertListEqual(edges, [(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4)])

    def test_iterators_iteredges_reversed(self):
        """
        Iterate over edges in reversed order based on edge ID
        """

        self.assertListEqual([e.nid for e in self.graph.iteredges(reverse=True)],
                             [(5, 4), (5, 3), (4, 5), (4, 3), (3, 5), (3, 4), (3, 2), (2, 3), (2, 1), (1, 2)])
