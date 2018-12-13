# -*- coding: utf-8 -*-

"""
file: module_algorithms_test.py

Unit tests for the graphit component
"""

#import networkx

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph
from graphit.graph_exceptions import GraphitAlgorithmError
from graphit.graph_algorithms.path_traversal import dfs_nodes, dfs_paths, dfs_edges
from graphit.graph_algorithms.shortest_path import dijkstra_shortest_path
from graphit.graph_algorithms.connectivity import is_reachable
from graphit.graph_algorithms.centrality import brandes_betweenness_centrality, eigenvector_centrality

from graphit.graph_networkx import NetworkXGraph


class TestGraphAlgorithms(UnittestPythonCompatibility):

    def setUp(self):

        edges = {(1, 2): {'weight': 1.0}, (2, 3): {'weight': 1.0}, (2, 4): {'weight': 1.0},
                 (3, 5): {'weight': 1.0}, (4, 5): {'weight': 1.0}, (4, 7): {'weight': 1.0},
                 (5, 7): {'weight': 0.75}, (3, 14): {'weight': 2.0}, (14, 15): {'weight': 2.0},
                 (14, 16): {'weight': 1.0}, (15, 12): {'weight': 2.0}, (22, 24): {'weight': 1.0},
                 (12, 13): {'weight': 2.0}, (13, 28): {'weight': 1.0}, (5, 8): {'weight': 1.0},
                 (8, 9): {'weight': 0.5}, (8, 10): {'weight': 3.0}, (9, 12): {'weight': 0.5},
                 (10, 11): {'weight': 3.0}, (11, 13): {'weight': 1.0}, (7, 25): {'weight': 1.0},
                 (25, 26): {'weight': 1.0}, (26, 27): {'weight': 1.0}, (11, 26): {'weight': 1.0},
                 (7, 17): {'weight': 1.0}, (17, 18): {'weight': 1.0}, (18, 19): {'weight': 2.0},
                 (18, 20): {'weight': 1.0}, (20, 21): {'weight': 1.0}, (21, 22): {'weight': 1.0},
                 (22, 23): {'weight': 1.0}}

        # Regular graphit Graph
        self.graph = Graph(auto_nid=False)
        self.graph.directed = True

        # NetworkX graphit Graph
        self.gn = NetworkXGraph(auto_nid=False)
        self.gn.directed = True

        # NetworkX graph
        #self.nx = networkx.DiGraph()

        for eid in edges:
            self.graph.add_edge(node_from_edge=True, *eid, **edges[eid])
            self.gn.add_edge(node_from_edge=True, *eid, **edges[eid])
            #self.nx.add_edge(*eid, **edges[eid])

    def test_algorithm_degree(self):
        """
        Test degree method part of the Adjacency view
        """

        # Degree
        self.assertDictEqual(self.graph.adjacency.degree(), {
            1: 1, 2: 3, 3: 3, 4: 3, 5: 4, 7: 4, 14: 3, 15: 2, 16: 1, 12: 3, 22: 3, 24: 1, 13: 3, 28: 1, 8: 3, 9: 2,
            10: 2, 11: 3, 25: 2, 26: 3, 27: 1, 17: 2, 18: 3, 19: 1, 20: 2, 21: 2, 23: 1})

        # Outdegree
        self.assertDictEqual(self.graph.adjacency.degree(method='outdegree'), {
            1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 7: 2, 14: 2, 15: 1, 16: 0, 12: 1, 22: 2, 24: 0, 13: 1, 28: 0, 8: 2, 9: 1,
            10: 1, 11: 2, 25: 1, 26: 1, 27: 0, 17: 1, 18: 2, 19: 0, 20: 1, 21: 1, 23: 0})

        # Indegree
        self.assertDictEqual(self.graph.adjacency.degree(method='indegree'), {
            1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 7: 2,14: 1, 15: 1, 16: 1, 12: 2, 22: 1, 24: 1, 13: 2, 28: 1, 8: 1, 9: 1,
            10: 1, 11: 1, 25: 1, 26: 2, 27: 1, 17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 23: 1})

        # Weighted degree
        self.assertDictEqual(self.graph.adjacency.degree(weight='weight'), {
            1: 1.0, 2: 3.0, 3: 4.0, 4: 3.0, 5: 3.75, 7: 3.75, 14: 5.0, 15: 4.0, 16: 1.0, 12: 4.5, 22: 3.0, 24: 1.0,
            13: 4.0, 28: 1.0, 8: 4.5, 9: 1.0, 10: 6.0, 11: 5.0, 25: 2.0, 26: 3.0, 27: 1.0, 17: 2.0, 18: 4.0, 19: 2.0,
            20: 2.0, 21: 2.0, 23: 1.0})

    def test_algorithm_dijkstra_shortest_path(self):
        """
        Test Dijkstra shortest path method, weighted and non-weighted.
        """

        # Shortest path in fully directed graph
        self.assertListEqual(dijkstra_shortest_path(self.graph, 1, 28), [1, 2, 3, 14, 15, 12, 13, 28])

        # Shortest path in fully directed graph considering weights
        self.assertListEqual(dijkstra_shortest_path(self.graph, 1, 28, weight='weight'),
                             [1, 2, 3, 5, 8, 9, 12, 13, 28])

        # Reverse directionality of edge (14, 15)
        self.graph.add_edge(15, 14)
        self.graph.remove_edge(14, 15)

        self.assertListEqual(dijkstra_shortest_path(self.graph, 1, 28), [1, 2, 3, 5, 8, 10, 11, 13, 28])

    def test_algorithm_dfs_paths(self):
        """
        Test depth-first search of all paths between two nodes
        """

        self.assertListEqual(list(dfs_paths(self.graph, 2, 26)), [
            [2, 4, 7, 25, 26], [2, 4, 5, 7, 25, 26], [2, 4, 5, 8, 10, 11, 26], [2, 3, 5, 7, 25, 26],
            [2, 3, 5, 8, 10, 11, 26]])

        # Nodes 13 and 26 not connected via directional path
        self.assertListEqual(list(dfs_paths(self.graph, 13, 26)), [])

        # Switch to breath-first search
        self.assertListEqual(list(dfs_paths(self.graph, 2, 26, method='bfs')), [[2, 4, 7, 25, 26], [2, 3, 5, 7, 25, 26],
                                            [2, 4, 5, 7, 25, 26], [2, 3, 5, 8, 10, 11, 26], [2, 4, 5, 8, 10, 11, 26]])

        # dfs_path with path length cutoff
        self.assertListEqual(list(dfs_paths(self.graph, 2, 26, cutoff=5)), [[2, 4, 7, 25, 26], [2, 4, 5, 7, 25, 26],
                                                                            [2, 3, 5, 7, 25, 26]])

    def test_algorithm_dfs_edges(self):
        """
        Test graph dfs_edges method in depth-first-search (dfs) and
        breath-first-search (bfs) mode.
        """

        self.assertListEqual(list(dfs_edges(self.graph, 5)), [
            (5, 7), (7, 17), (17, 18), (18, 19), (18, 20), (20, 21), (21, 22), (22, 23), (22, 24), (7, 25), (25, 26),
            (26, 27), (5, 8), (8, 9), (9, 12), (12, 13), (13, 28), (8, 10), (10, 11)])

        self.assertListEqual(list(dfs_edges(self.graph, 8)), [
            (8, 9), (9, 12), (12, 13), (13, 28), (8, 10), (10, 11),(11, 26), (26, 27)])

        # Breath-first search
        self.assertListEqual(list(dfs_edges(self.graph, 8, method='bfs')), [
            (8, 9), (8, 10), (9, 12), (10, 11), (12, 13), (11, 26), (13, 28), (26, 27)])

        # With depth limit
        self.assertListEqual(list(dfs_edges(self.graph, 5, max_depth=2)), [
            (5, 7), (7, 17), (7, 25), (5, 8), (8, 9), (8, 10)])

    def test_algorithm_dfs_edges__edge_based(self):
        """
        Test graph dfs_edges in True edge traversal mode
        """

        # Use true edge oriented DFS method
        self.assertListEqual(list(dfs_edges(self.graph, 8, edge_based=True)), [
            (8, 9), (9, 12), (12, 13), (13, 28), (8, 10), (10, 11), (11, 13), (11, 26), (26, 27)])

    def test_algorithm_dfs_nodes(self):
        """
        Test graph dfs_nodes method in depth-first-search (dfs) and
        breath-first-search (bfs) mode
        """

        # Connectivity information using Depth First Search / Breath first search
        self.assertListEqual(list(dfs_nodes(self.graph, 8)), [8, 9, 12, 13, 28, 10, 11, 26, 27])
        self.assertListEqual(list(dfs_nodes(self.graph, 8, method='bfs')), [8, 9, 10, 12, 11, 13, 26, 28, 27])

    def test_algorithm_is_reachable(self):
        """
        Test is_reachable method to test connectivity between two nodes
        """

        self.assertTrue(is_reachable(self.graph, 3, 21))

        # Reverse directionality of edge (20, 21)
        self.graph.add_edge(21, 20)
        self.graph.remove_edge(20, 21)
        self.assertFalse(is_reachable(self.graph, 7, 23))

    def test_algorithm_brandes_betweenness_centrality(self):
        """
        Test graph Brandes betweenness centrality measure
        """

        # Non-weighted Brandes betweenness centrality
        self.assertDictEqual(brandes_betweenness_centrality(self.graph),
                             {1: 0.0, 2: 0.038461538461538464, 3: 0.026153846153846153, 4: 0.04461538461538461,
                              5: 0.047692307692307694, 7: 0.08461538461538462, 8: 0.03230769230769231,
                              9: 0.00923076923076923, 10: 0.016923076923076923, 11: 0.013846153846153847,
                              12: 0.023076923076923078, 13: 0.01846153846153846, 14: 0.023076923076923078,
                              15: 0.01846153846153846, 16: 0.0, 17: 0.06461538461538462, 18: 0.06461538461538462,
                              19: 0.0, 20: 0.04923076923076923, 21: 0.04153846153846154, 22: 0.03076923076923077,
                              23: 0.0, 24: 0.0, 25: 0.01846153846153846, 26: 0.015384615384615385, 27: 0.0, 28: 0.0})

        # Weighted Brandes betweenness centrality
        self.assertDictEqual(brandes_betweenness_centrality(self.graph, weight='weight'),
                             {1: 0.0, 2: 0.038461538461538464, 3: 0.021538461538461538, 4: 0.04923076923076923,
                              5: 0.06153846153846154, 7: 0.08461538461538462, 8: 0.046153846153846156,
                              9: 0.027692307692307693, 10: 0.012307692307692308, 11: 0.00923076923076923,
                              12: 0.027692307692307693, 13: 0.01846153846153846, 14: 0.00923076923076923,
                              15: 0.004615384615384615, 16: 0.0, 17: 0.06461538461538462, 18: 0.06461538461538462,
                              19: 0.0, 20: 0.04923076923076923, 21: 0.04153846153846154, 22: 0.03076923076923077,
                              23: 0.0, 24: 0.0, 25: 0.01846153846153846, 26: 0.015384615384615385, 27: 0.0, 28: 0.0})

        # Non-Normalized Brandes betweenness centrality
        self.assertDictEqual(brandes_betweenness_centrality(self.graph, normalized=False),
                             {1: 0.0, 2: 25.0, 3: 17.0, 4: 29.0, 5: 31.0, 7: 55.0, 8: 21.0, 9: 6.0, 10: 11.0, 11: 9.0,
                              12: 15.0, 13: 12.0, 14: 15.0, 15: 12.0, 16: 0.0, 17: 42.0, 18: 42.0, 19: 0.0, 20: 32.0,
                              21: 27.0, 22: 20.0, 23: 0.0, 24: 0.0, 25: 12.0, 26: 10.0, 27: 0.0, 28: 0.0})

    def test_algorithm_eigenvector_centrality(self):
        """
        Test graph node eigenvector centrality
        """

        # Default eigenvector centrality
        self.assertDictAlmostEqual(eigenvector_centrality(self.graph, max_iter=1000),
                             {1: 4.625586668162422e-22, 2: 2.585702947502789e-19, 3: 7.21415747939946e-17,
                              4: 7.21415747939946e-17, 5: 2.6788916354749308e-14, 7: 3.737126037589252e-12,
                              8: 3.723731579643154e-12, 9: 4.133449353873311e-10, 10: 4.133449353873311e-10,
                              11: 3.816675918922932e-08, 12: 3.8373431692993267e-08, 13: 6.049668071167027e-06,
                              14: 1.3394458408653937e-14, 15: 1.861865919106721e-12, 16: 1.861865919106721e-12,
                              17: 4.152068010478676e-10, 18: 3.837343162085218e-08, 19: 3.0343757153351047e-06,
                              20: 3.0343757153351047e-06, 21: 0.0002095723846317974, 22: 0.012842890187130716,
                              23: 0.7070483707650801, 24: 0.7070483707650801, 25: 4.152068010478676e-10,
                              26: 3.0536657740585734e-06, 27: 0.00021109911510684646, 28: 0.0004176371258851023},
                                   places=14)

        # Weighted eigenvector centrality
        self.assertDictAlmostEqual(eigenvector_centrality(self.graph, max_iter=1000, weight='weight'),
                             {1: 8.688902566026301e-23, 2: 5.899764842331867e-20, 3: 2.0000289704530646e-17,
                              4: 2.0000289704530646e-17, 5: 9.026876112472413e-15, 7: 1.148684996586023e-12,
                              8: 1.5255620780686783e-12, 9: 1.029772476508652e-10, 10: 6.178634859047565e-10,
                              11: 2.0822457823635333e-07, 12: 6.607834043233963e-09, 13: 2.131713811356956e-05,
                              14: 9.026876112472416e-15, 15: 3.051124156050468e-12, 16: 1.5255620780686783e-12,
                              17: 1.5522865250051764e-10, 18: 1.745502542904305e-08, 19: 3.359775472482072e-06,
                              20: 1.679887736241036e-06, 21: 0.00014125541592609745, 22: 0.010542254842300024,
                              23: 0.7070653405331172, 24: 0.7070653405331172, 25: 1.5522865250051764e-10,
                              26: 2.0037291488250496e-05, 27: 0.0016833983234686718, 28: 0.0017929426478924984},
                                   places=14)

        # Non-convergence exception
        self.assertRaises(GraphitAlgorithmError, eigenvector_centrality, self.graph, max_iter=100)
