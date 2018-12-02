# -*- coding: utf-8 -*-

"""
file: module_algorithms_test.py

Unit tests for the graphit component
"""

import itertools
import networkx

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph
from graphit.graph_algorithms import *
from graphit.graph_networkx import NetworkXGraph


class TestGraphAlgorithms(UnittestPythonCompatibility):

    def setUp(self):

        edges = {(5, 4): {'type': 'universal'}, (5, 6): {'type': 'universal'}, (11, 9): {'type': 'universal'},
                 (3, 2): {'type': 'universal'}, (2, 1): {'type': 'monotone'}, (9, 10): {'type': 'universal'},
                 (2, 3): {'type': 'universal'}, (9, 6): {'type': 'universal'}, (6, 5): {'type': 'universal'},
                 (1, 2): {'type': 'monotone'}, ('object', 12): {'type': 'universal'},
                 (6, 9): {'type': 'universal'}, (6, 7): {'type': 'universal'}, (12, 13): {'type': 'monotone'},
                 (7, 8): {}, (7, 6): {'type': 'universal'}, (13, 12): {'type': 'monotone'},
                 (3, 8): {'type': 'universal'}, (4, 5): {'type': 'universal'}, (12, 'object'): {'type': 'universal'},
                 (9, 11): {'type': 'universal'}, (4, 3): {'type': 'universal'}, (8, 3): {'type': 'universal'},
                 (3, 4): {'type': 'universal'}, (10, 9): {'type': 'universal'}}

        self.graph = Graph(auto_nid=False)
        self.graph.directed = True

        self.gn = NetworkXGraph()
        self.gn.directed = True

        self.nx = networkx.DiGraph()

        weight = 0
        for node in range(1, 14):
            self.graph.add_node(node, weight=weight)
            self.gn.add_node(node, weight=weight)
            self.nx.add_node(node, _id=node, key=node, weight=weight)
            weight += 1
        self.graph.add_node('object')
        self.gn.add_node('object')
        self.nx.add_node('object', _id=node+1, key='object')

        weight = 0
        for eid in sorted(edges.keys(), key=lambda x: str(x[0])):
            self.graph.add_edge(*eid, weight=weight)
            self.gn.add_edge(*eid, weight=weight)
            self.nx.add_edge(*eid, weight=weight)
            weight += 0.05

    def test_graph_shortest_path_method(self):
        """
        Test Dijkstra shortest path method
        """

        from networkx.algorithms.shortest_paths.generic import shortest_path
        from networkx.algorithms.traversal.depth_first_search import dfs_preorder_nodes

        print(shortest_path(self.nx, 8, 10))
        print(list(dfs_preorder_nodes(self.nx, 8)))

        # In a mixed directed graph where 7 connects to 8 but not 8 to 7
        self.assertEqual(dijkstra_shortest_path(self.graph, 8, 10), [8, 3, 4, 5, 6, 9, 10])
        self.assertEqual(list(dfs_paths(self.graph, 8, 10)), [[8, 3, 4, 5, 6, 9, 10]])
        self.assertEqual(list(dfs_paths(self.graph, 8, 10, method='bfs')), [[8, 3, 4, 5, 6, 9, 10]])

        # Fully connect 7 and 8
        self.graph.add_edge(8, 7, directed=True)
        self.assertEqual(dijkstra_shortest_path(self.graph, 8, 10), [8, 7, 6, 9, 10])
        self.assertEqual(list(dfs_paths(self.graph, 8, 10)), [[8, 7, 6, 9, 10], [8, 3, 4, 5, 6, 9, 10]])
        self.assertEqual(list(dfs_paths(self.graph, 8, 10, method='bfs')), [[8, 7, 6, 9, 10], [8, 3, 4, 5, 6, 9, 10]])

    def test_graph_dfs_method(self):
        """
        Test graph depth-first-search and breath-first-search
        """

        # Connectivity information using Depth First Search / Breath first search
        self.assertListEqual(dfs(self.graph, 8), [8, 3, 4, 5, 6, 9, 11, 10, 7, 2, 1])
        self.assertListEqual(dfs(self.graph, 8, method='bfs'), [8, 3, 2, 4, 1, 5, 6, 7, 9, 10, 11])

    def test_graph_node_reachability_methods(self):
        """
        Test graph algorithms
        """

        # Test if node is reachable from other node (uses dfs internally)
        self.assertTrue(is_reachable(self.graph, 8, 10))
        self.assertFalse(is_reachable(self.graph, 8, 12))

    def test_graph_centrality_method(self):
        """
        Test graph Brandes betweenness centrality measure
        """

        # Return Brandes betweenness centrality
        self.assertDictEqual(brandes_betweenness_centrality(self.graph),
                             {1: 0.0, 2: 0.11538461538461538, 3: 0.26282051282051283, 4: 0.21474358974358973,
                              5: 0.22756410256410256, 6: 0.3205128205128205, 7: 0.0673076923076923,
                              8: 0.060897435897435896, 9: 0.21794871794871795, 10: 0.0, 11: 0.0,
                              12: 0.01282051282051282, 13: 0.0, u'object': 0.0})

        print(brandes_betweenness_centrality(self.graph, weight='weight'))
        print(brandes_betweenness_centrality(self.graph, normalized=False))

        # Test against NetworkX if possible
        if self.nx is not None:

            from networkx.algorithms.centrality.betweenness import betweenness_centrality

            # Regular Brandes betweenness centrality
            nx_between = betweenness_centrality(self.nx)
            gn_between = brandes_betweenness_centrality(self.graph)
            self.assertDictEqual(gn_between, nx_between)

            # Weighted Brandes betweenness centrality
            nx_between = betweenness_centrality(self.nx, weight='weight')
            gn_between = brandes_betweenness_centrality(self.graph, weight='weight')
            self.assertDictEqual(gn_between, nx_between)

            # Normalized Brandes betweenness centrality
            nx_between = betweenness_centrality(self.nx, normalized=False)
            gn_between = brandes_betweenness_centrality(self.graph, normalized=False)
            self.assertDictEqual(gn_between, nx_between)

    def test_graph_nodes_are_interconnected(self):
        """
        Test if all nodes directly connected with one another
        """

        nodes = [1, 2, 3, 4, 5, 6]

        self.graph = Graph()
        self.graph.add_nodes(nodes)
        for edge in itertools.combinations(nodes, 2):
            self.graph.add_edge(*edge)
        self.graph.remove_edge(5, 6)

        self.assertTrue(nodes_are_interconnected(self.graph, [1, 2, 4]))
        self.assertFalse(nodes_are_interconnected(self.graph, [3, 5, 6]))

    def test_graph_degree(self):
        """
        Test (weighted) degree method
        """

        self.assertDictEqual(degree(self.graph, [1, 3, 12]), {1: 1, 3: 3, 12: 2})

        # Directed graphs behave the same as undirected
        self.graph.directed = False
        self.assertDictEqual(degree(self.graph, [1, 3, 12]), {1: 1, 3: 3, 12: 2})
        self.assertDictEqual(degree(self.graph, [1, 3, 12], weight='weight'),
                             {1: 0, 3: 1.3499999999999999, 12: 0.35000000000000003})

        # Loops counted twice
        self.graph.add_edge(12, 12)
        self.assertDictEqual(degree(self.graph, [1, 3, 12]), {1: 1, 3: 3, 12: 4})
        self.assertDictEqual(degree(self.graph, [1, 3, 12], weight='weight'),
                             {1: 0, 3: 1.3499999999999999, 12: 2.3499999999999996})
