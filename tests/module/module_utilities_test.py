# -*- coding: utf-8 -*-

"""
file: module_utilities.test.py

Unit tests for the graphit utility functions
"""

from tests.module.unittest_baseclass import UnittestPythonCompatibility, PY_VERSION

from graphit import Graph
from graphit.graph_utils.graph_utilities import *


class TestUtilityFunctions(UnittestPythonCompatibility):

    def setUp(self):

        self.graph = Graph()
        self.graph.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (5, 6), (6, 2)],
                             node_from_edge=True, arg1=1.22, arg2=False)

    def test_graph_undirectional_to_directional(self):
        """
        Test convert a undirectional to a directional graph.
        Returns a deep copy.
        """

        dg = graph_undirectional_to_directional(self.graph)

        self.assertTrue(dg.directed)
        self.assertNotEqual(id(dg), id(self.graph))

        directional_checked = []
        for edge in self.graph.edges:
            directional_checked.append(id(dg.edges[edge]) != id(dg.edges[(edge[1], edge[0])]))
        self.assertTrue(all(directional_checked))

    def test_graph_directional_to_undirectional(self):
        """
        Test convert a directional to undirectional graph.
        Returns a deep copy.
        """

        # Already undirectional
        ug = graph_directional_to_undirectional(self.graph)

        self.assertFalse(ug.directed)
        self.assertEqual(ug, self.graph)

        # Make a directed graph
        dg = Graph(directed=True)
        dg.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (5, 6), (6, 2)],
                             node_from_edge=True, arg1=1.22, arg2=False)
        dg.add_edges([(3, 2), (2, 6)], arg1=2.66)

        ug2 = graph_directional_to_undirectional(dg)

        self.assertFalse(ug2.directed)
        self.assertEqual(ug2, self.graph)

        # Attribute overwrite. Different dict update behaviour between PY 2/3
        if PY_VERSION == '3.6':
            self.assertEqual(ug2.edges[(2, 3)]['arg1'], 1.22)
            self.assertEqual(ug2.edges[(3, 2)]['arg1'], 1.22)
        else:
            self.assertEqual(ug2.edges[(2, 3)]['arg1'], 2.66)
            self.assertEqual(ug2.edges[(3, 2)]['arg1'], 2.66)

        undirectional_checked = []
        for edge in ug2.edges:
            undirectional_checked.append(id(ug2.edges[edge]) == id(ug2.edges[(edge[1], edge[0])]))
        self.assertTrue(all(undirectional_checked))
