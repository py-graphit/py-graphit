# -*- coding: utf-8 -*-

"""
file: module_graph_directionality_test.py

Unit tests for Graphit directional, undirectional and mixed graphs

Tests are conducted using the following simple graph with automatically
assigned (auto_nid) node IDs:

        1 - 2 - 3 - 6
            | / |
            4 - 5

The edges will either be undirected or directed together resulting in a
graph that is fully undirectional, directional or has a mixed character.
"""

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph
from graphit.graph_helpers import graph_directionality
from graphit.graph_utils.graph_utilities import graph_undirectional_to_directional, graph_directional_to_undirectional


class TestGraphUndirectional(UnittestPythonCompatibility):
    """
    Test graph with undirected edges
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph()
        self.graph.add_edges([(1, 2), (2, 3), (2, 4), (4, 5), (4, 3), (3, 5), (3, 6)],
                             node_from_edge=True, arg1=1.22, arg2=False)

    def test_graph_is_undirected(self):

        self.assertFalse(self.graph.directed)
        self.assertEqual(graph_directionality(self.graph), 'undirectional')
        self.assertTrue(all([not edge.is_directed for edge in self.graph.iteredges()]))
        self.assertTrue(len(self.graph.edges) == 14)  # 2 * 7

    def test_graph_contains(self):
        """
        Test if pair of directed edges is contained in undirected edge
        """

        for edge in self.graph.edges:
            self.assertTrue(edge in self.graph.edges)
            self.assertTrue(tuple(reversed(edge)) in self.graph.edges)

    def test_graph_adjacency(self):
        """
        Node adjacency in a undirected graph reflects the pairs of directed
        edges that exists between nodes. This is also seen in the adjacency
        'link count' and 'degree' metrics for nodes.
        """

        # Number of edges equals the link count of the full node adjacency
        self.assertEqual(len(self.graph.edges), self.graph.adjacency.link_count())

        # Undirected degree is bidirectional. It equals the number of
        # connected edges to a node
        degree = self.graph.adjacency.degree()
        for node in self.graph:
            self.assertEqual(degree[node.nid], len(node.connected_edges()))

    def test_graph_degree(self):
        """
        Total degree equals sum of equal inwards and outwards degree
        """

        degree = self.graph.adjacency.degree()
        indegree = self.graph.adjacency.degree(method='indegree')
        outdegree = self.graph.adjacency.degree(method='outdegree')

        self.assertDictEqual(indegree, outdegree)
        self.assertEqual(sum(indegree.values()) * 2, sum(degree.values()))

    def test_graph_edge_removal_undirected(self):
        """
        Undirected edge removal removes pair of directed edges
        """

        self.graph.remove_edge(2, 3)

        self.assertFalse((2, 3) in self.graph.edges)
        self.assertFalse((3, 2) in self.graph.edges)
        self.assertEqual(len(self.graph.edges), 12)

    def test_graph_edge_removal_directed(self):
        """
        Directed removal in a undirected graph is supported
        """

        self.graph.remove_edge(2, 3, directed=True)

        self.assertFalse((2, 3) in self.graph.edges)
        self.assertTrue((3, 2) in self.graph.edges)
        self.assertEqual(len(self.graph.edges), 13)

        self.assertFalse(self.graph.directed)  # globally still marked as undirected
        self.assertEqual(graph_directionality(self.graph), 'mixed')

    def test_graph_undirectional_to_directional(self):
        """
        Test conversion of a undirectional to directional graph
        Conversion essentially breaks all linked edge pairs by removing the
        data reference pointer.
        """

        directional = graph_undirectional_to_directional(self.graph)

        # directed attribute changed to True
        self.assertTrue(directional.directed)
        self.assertNotEqual(id(directional), id(self.graph))

        # directional graph still contains same nodes and edges
        self.assertEqual(directional, self.graph)

        # data reference pointers determine directionality
        self.assertEqual(graph_directionality(directional), 'directional')
        self.assertEqual(graph_directionality(directional, has_data_reference=False), 'undirectional')

        # directional edge pair no longer point to same value
        directional_checked = []
        for edge in directional.edges:
            directional_checked.append(id(directional.edges[edge]) != id(directional.edges[(edge[1], edge[0])]))
        self.assertTrue(all(directional_checked))

    def test_graph_undirected_linked_values(self):
        """
        Test setting and getting linked edge data
        """

        self.graph.edges[(2, 3)]['test'] = True

        # In storage backend only one edge of the pair has the data
        self.assertTrue('test' in self.graph.edges._storage[(2, 3)])
        self.assertFalse('test' in self.graph.edges._storage[(3, 2)])

        # transparent getting and setting of linked data
        self.assertTrue(self.graph.edges[(2, 3)]['test'])
        self.assertTrue(self.graph.edges[(3, 2)]['test'])

        self.graph.edges[(3, 2)]['test'] = False
        self.assertFalse(self.graph.edges[(2, 3)]['test'])
        self.assertFalse(self.graph.edges[(3, 2)]['test'])


class TestGraphDirectional(UnittestPythonCompatibility):
    """
    Test graph with directed edges

        1 - 2 - 3 - 6
            | / |
            4 - 5
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph(directed=True)
        self.graph.add_edges([(1, 2), (2, 3), (3, 6), (3, 5), (5, 4), (4, 3), (4, 2)],
                             node_from_edge=True, arg1=1.22, arg2=False)

    def test_graph_is_directed(self):

        self.assertTrue(self.graph.directed)
        self.assertEqual(graph_directionality(self.graph), 'directional')
        self.assertTrue(all([edge.is_directed for edge in self.graph.iteredges()]))
        self.assertTrue(len(self.graph.edges) == 7)

    def test_graph_contains(self):
        """
        Only forward edge present
        """

        for edge in self.graph.edges:
            self.assertTrue(edge in self.graph.edges)
            self.assertFalse(tuple(reversed(edge)) in self.graph.edges)

    def test_graph_adjacency(self):
        """
        Node adjacency in a directed graph reflects the presence of only a
        forward edge connecting nodes. This is also seen in the adjacency
        'link count' and 'degree' metrics for nodes.
        """

        # Number of edges equals the link count of the full node adjacency
        self.assertEqual(len(self.graph.edges), self.graph.adjacency.link_count())

        # Directed degree is unidirectional. It equals the number of
        # connected edges to a node
        degree = self.graph.adjacency.degree()
        for node in self.graph:
            self.assertEqual(degree[node.nid], len(node.connected_edges()))

    def test_graph_degree(self):
        """
        The total degree equals the sum of inwards and outwards degrees but the
        latter two are not equals
        """

        degree = self.graph.adjacency.degree()
        indegree = self.graph.adjacency.degree(method='indegree')
        outdegree = self.graph.adjacency.degree(method='outdegree')

        self.assertEqual(sum(degree.values()), sum(indegree.values()) + sum(outdegree.values()))
        self.assertNotEqual(indegree, outdegree)

    def test_graph_directional_to_undirectional(self):
        """
        Test conversion of a undirectional to directional graph
        """

        # Set/overwrite a few values
        self.graph.edges[(3, 6)]['arg1'] = 2.44
        self.graph.edges[(5, 4)]['arg3'] = 'test'

        undirectional = graph_directional_to_undirectional(self.graph)

        # directed attribute changed to True
        self.assertFalse(undirectional.directed)
        self.assertNotEqual(undirectional, self.graph)

        # data reference pointers determine directionality
        self.assertEqual(graph_directionality(undirectional), 'undirectional')
        self.assertEqual(graph_directionality(undirectional, has_data_reference=False), 'undirectional')

        # directional edge pair point to same value
        undirectional_checked = []
        for edge in undirectional.edges:
            undirectional_checked.append(id(undirectional.edges[edge]) == id(undirectional.edges[(edge[1], edge[0])]))
        self.assertTrue(all(undirectional_checked))

        # edge argument equality
        self.assertDictEqual(undirectional.edges[(3, 6)], {'arg1': 2.44, 'arg2': False})
        self.assertDictEqual(undirectional.edges[(6, 3)], {'arg1': 2.44, 'arg2': False})
        self.assertDictEqual(undirectional.edges[(5, 4)], {'arg1': 1.22, 'arg2': False, 'arg3': 'test'})
        self.assertDictEqual(undirectional.edges[(4, 5)], {'arg1': 1.22, 'arg2': False, 'arg3': 'test'})
