# -*- coding: utf-8 -*-

"""
file: module_graph_edges_test.py

Unit tests for the Graph edge related methods
"""

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph
from graphit.graph import GraphitException


class TestGraphAddEdge(UnittestPythonCompatibility):
    """
    Test Graph add_edge method with the Graph.auto_nid set to False
    mimicking the behaviour of many popular graph packages
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph(auto_nid=False)
        self.graph.add_nodes('graph')

        # Only nodes no edges yet
        self.assertTrue(len(self.graph) == 5)
        self.assertTrue(len(self.graph.nodes) == 5)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 5)
        self.assertTrue(all([len(a) == 0 for a in self.graph.adjacency.values()]))

        # auto_nid
        self.assertFalse(self.graph.auto_nid)

    def tearDown(self):
        """
        Test state after edge addition
        """

        # If undirected, add reversed edges
        if not self.graph.directed:
            self.edges.extend([e[::-1] for e in self.edges if e[::-1] not in self.edges])

        for edge in self.edges:

            # Edge should be present
            self.assertTrue(edge in self.graph.edges)

            # Nodes connected should be present
            self.assertTrue(all([node in self.graph.nodes for node in edge]))

            # Adjacency setup
            self.assertTrue(edge[1] in self.graph.adjacency[edge[0]])

            # If directional, reverse edge not in graph
            if self.graph.directed:
                rev_edge = edge[::-1]
                if rev_edge not in self.edges:
                    self.assertTrue(rev_edge not in self.graph.edges)

        # filled after addition
        self.assertTrue(len(self.graph) == 5)
        self.assertTrue(len(self.graph.nodes) == 5)
        self.assertTrue(len(self.graph.edges) == len(self.edges))
        self.assertTrue(len(self.graph.adjacency) == 5)

    def test_add_edge_undirectional(self):
        """
        Test adding a single un-directional edge
        """

        self.edges = [('g', 'r')]
        self.graph.add_edge(*self.edges[0])

    def test_add_edges_undirectional(self):
        """
        Test adding multiple un-directional edges
        """

        self.edges = [('g', 'r'), ('r', 'a'), ('a', 'p'), ('a', 'h'), ('p', 'h')]
        self.graph.add_edges(self.edges)

    def test_add_edge_directional(self):
        """
        Test adding a single directional edge
        """

        self.edges = [('g', 'r')]
        self.graph.directed = False
        self.graph.add_edge(*self.edges[0])

    def test_add_edges_directional(self):
        """
        Test adding multiple directional edges
        """

        self.edges = [('g', 'r'), ('r', 'a'), ('a', 'p'), ('a', 'h'), ('p', 'h')]
        self.graph.directed = False
        self.graph.add_edges(self.edges)

    def test_add_nodes_and_edges(self):
        """
        Test adding edges and creating the nodes from the edges.
        Auto_nid is set to False automatically to force identical
        node/edge names. When node exists, no message.
        """

        self.graph = Graph()

        self.edges = [('g', 'r'), ('r', 'a'), ('a', 'p'), ('a', 'h'), ('p', 'h')]
        self.graph.add_edges(self.edges, node_from_edge=True)


class TestGraphAddEdgeAutonid(UnittestPythonCompatibility):
    """
    Test Graph add_edge method with the Graph.auto_nid set to True
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph()
        self.graph.add_nodes('graph')

        # Only nodes no edges yet
        self.assertTrue(len(self.graph) == 5)
        self.assertTrue(len(self.graph.nodes) == 5)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 5)
        self.assertTrue(all([len(a) == 0 for a in self.graph.adjacency.values()]))

        # auto_nid
        self.assertTrue(self.graph.auto_nid)

    def tearDown(self):
        """
        Test state after edge addition
        """

        # If undirected, add reversed edges
        if not self.graph.directed:
            self.edges.extend([e[::-1] for e in self.edges if e[::-1] not in self.edges])

        for edge in self.edges:

            # Edge should be present
            self.assertTrue(edge in self.graph.edges)

            # Nodes connected should be present
            self.assertTrue(all([node in self.graph.nodes for node in edge]))

            # Adjacency setup
            self.assertTrue(edge[1] in self.graph.adjacency[edge[0]])

            # If directional, reverse edge not in graph
            if self.graph.directed:
                rev_edge = edge[::-1]
                if rev_edge not in self.edges:
                    self.assertTrue(rev_edge not in self.graph.edges)

        # filled after addition
        self.assertTrue(len(self.graph) == 5)
        self.assertTrue(len(self.graph.nodes) == 5)
        self.assertTrue(len(self.graph.edges) == len(self.edges))
        self.assertTrue(len(self.graph.adjacency) == 5)

    def test_add_edge_undirectional(self):
        """
        Test adding a single un-directional edge
        """

        self.edges = [(1, 2)]
        self.graph.add_edge(*self.edges[0])

    def test_add_edges_undirectional(self):
        """
        Test adding multiple un-directional edges
        """

        self.edges = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]
        self.graph.add_edges(self.edges)

    def test_add_edge_directional(self):
        """
        Test adding a single directional edge
        """

        self.edges = [(1, 2)]
        self.graph.directed = False
        self.graph.add_edge(*self.edges[0])

    def test_add_edges_directional(self):
        """
        Test adding multiple directional edges
        """

        self.edges = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]
        self.graph.directed = False
        self.graph.add_edges(self.edges)

    def test_add_nodes_and_edges(self):
        """
        Test adding edges and creating the nodes from the edges.
        Auto_nid is set to False automatically to force identical
        node/edge names. When node exists, no message.
        """

        self.graph = Graph()

        self.edges = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]
        self.graph.add_edges(self.edges, node_from_edge=True)


class TestGraphEdgeDirectionality(UnittestPythonCompatibility):
    """
    Test adding edges in directional or un-directional way
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph()
        self.graph.add_nodes([1, 2, 3])

        # Only nodes no edges yet
        self.assertTrue(len(self.graph) == 3)
        self.assertTrue(len(self.graph.nodes) == 3)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 3)
        self.assertTrue(all([len(a) == 0 for a in self.graph.adjacency.values()]))

    def tearDown(self):
        """
        Test state after edge addition
        """

        # If undirected, add reversed edges
        if not self.graph.directed:
            self.edges.extend([e[::-1] for e in self.edges if e[::-1] not in self.edges])

        for edge in self.edges:

            # Edge should be present
            self.assertTrue(edge in self.graph.edges)

            # Nodes connected should be present
            self.assertTrue(all([node in self.graph.nodes for node in edge]))

            # Adjacency setup
            self.assertTrue(edge[1] in self.graph.adjacency[edge[0]])

            # If directional, reverse edge not in graph
            if self.graph.directed:
                rev_edge = edge[::-1]
                if rev_edge not in self.edges:
                    self.assertTrue(rev_edge not in self.graph.edges)

        # filled after addition
        self.assertTrue(len(self.graph) == 3)
        self.assertTrue(len(self.graph.nodes) == 3)
        self.assertTrue(len(self.graph.edges) == len(self.edges))
        self.assertTrue(len(self.graph.adjacency) == 3)

    def test_add_edge_undirectional_graph(self):
        """
        Test default add edge in undirected graph
        """

        self.graph.directed = False
        self.edges = [(1, 2), (2, 3)]

        self.graph.add_edges(self.edges)

    def test_add_edge_directional_graph(self):
        """
        Test default add edge in directed graph
        """

        self.graph.directed = True
        self.edges = [(1, 2), (2, 3)]

        self.graph.add_edges(self.edges)

    def test_add_edge_mixed_graph(self):
        """
        Add edges with local override in directionality yielding a mixed
        directional graph
        """

        self.edges = [(1, 2), (2, 3), (3, 2)]

        self.graph.add_edge(1, 2, directed=True)
        self.graph.add_edge(2, 3)

        self.graph.directed = True


class TestGraphAddEdgeExceptionWarning(UnittestPythonCompatibility):
    """
    Test logged warnings and raised Exceptions by Graph add_edge.
    Same as for add_nodes
    """

    def setUp(self):
        """
        Build empty graph to add a node to and test default state
        """

        self.graph = Graph()

    def test_add_edge_node_not_exist(self):
        """
        Test adding edges for nodes that do not exist
        """

        self.assertRaises(GraphitException, self.graph.add_edge, 1, 2)

    def test_add_edge_exist(self):
        """
        Test adding edges that already exist. A warning is logged
        but edge ID is returned
        """

        self.graph.add_nodes([1, 2])
        self.graph.add_edge(1, 2)

        eid = self.graph.add_edge(1, 2)
        self.assertTrue(eid, (1, 2))

    def test_remove_edge_exist(self):
        """
        Test removal of edges that do not exist
        """

        self.graph.add_nodes([1, 2])
        self.assertRaises(GraphitException, self.graph.remove_edge, 1, 2)


class TestGraphAddEdgeAttributes(UnittestPythonCompatibility):
    """
    Test additional attribute storage for Graph add_edge
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph()
        self.graph.add_nodes('graph')

        # Only nodes no edges yet
        self.assertTrue(len(self.graph) == 5)
        self.assertTrue(len(self.graph.nodes) == 5)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 5)
        self.assertTrue(all([len(a) == 0 for a in self.graph.adjacency.values()]))

        # auto_nid
        self.assertTrue(self.graph.auto_nid)

    def tearDown(self):
        """
        Test state after edge attribute addition
        """

        # If undirected, add reversed edges
        if not self.graph.directed:
            for edge, attr in list(self.edges.items()):
                self.edges[edge[::-1]] = attr

        for edge, attr in self.edges.items():

            self.assertTrue(edge in self.graph.edges)
            self.assertDictEqual(self.graph.edges[edge], attr)

    def test_add_edge_no_attribute(self):
        """
        No attributes added should yield empty dict
        """

        self.edges = {(1, 2): {}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_single_attribute_undirected(self):
        """
        Add a single attribute
        :return:
        """

        self.edges = {(1, 2): {'weight': 2.33}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_multiple_attributes_undirected(self):
        """
        Add a single attribute
        """

        self.edges = {(1, 2): {'test': True, 'pv': 1.44}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_nested_attribute_undirected(self):
        """
        Test adding nested attributed, e.a. dict in dict
        """

        self.edges = {(1, 2): {'func': len, 'nested': {'weight': 1.22, 'leaf': True}}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_single_attribute_directed(self):
        """
        Add a single attribute, directed
        :return:
        """

        self.graph.directed = True
        self.edges = {(1, 2): {'weight': 2.33}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_multiple_attributes_directed(self):
        """
        Add a single attribute, directed
        """

        self.graph.directed = True
        self.edges = {(1, 2): {'test': True, 'pv': 1.44}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_nested_attribute_directed(self):
        """
        Test adding nested attributed, e.a. dict in dict, directed
        """

        self.graph.directed = True
        self.edges = {(1, 2): {'func': len, 'nested': {'weight': 1.22, 'leaf': True}}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, **attr)

    def test_add_edge_single_attribute_mixed(self):
        """
        Add a single attribute, override undirected graph
        """

        self.edges = {(1, 2): {'weight': 2.33}}

        for edge, attr in self.edges.items():
            self.graph.add_edge(*edge, directed=True, **attr)

        self.graph.directed = True


class TestGraphAddEdgesAttributes(UnittestPythonCompatibility):
    """
    Test additional attribute storage for Graph add_edges.
    Add_edges is a wrapper around add_edge, here we only test attribute
    addition.
    """

    def setUp(self):
        """
        Build Graph with a few nodes but no edges yet
        """

        self.graph = Graph()
        self.graph.add_nodes('graph')

    def test_add_edges_no_attribute(self):
        """
        No attributes added should yield empty dict
        """

        edges = [(1, 2), (2, 3), (3, 4), (3, 5)]
        self.graph.add_edges(edges)

        self.assertTrue(all([len(e) == 0 for e in self.graph.edges.values()]))

    def test_add_edges_single_global_attribute(self):
        """
        Test adding a single global attribute to all edges
        """

        edge_dict = {'weight': 2.33}
        edges = [(1, 2), (2, 3), (3, 4), (3, 5)]
        self.graph.add_edges(edges, **edge_dict)

        for attr in self.graph.edges.values():
            self.assertDictEqual(attr, edge_dict)

    def test_add_edges_multiple_global_attribute(self):
        """
        Test adding a multiple global attributes to all edges
        """

        edge_dict = {'test': True, 'pv': 1.44}
        edges = [(1, 2), (2, 3), (3, 4), (3, 5)]
        self.graph.add_edges(edges, **edge_dict)

        for attr in self.graph.edges.values():
            self.assertDictEqual(attr, edge_dict)

    def test_add_edges_global_attribute_directed(self):
        """
        Test adding a single global attribute to directed edges
        """

        edge_dict_one = {'test': True, 'pv': 1.44}
        edges_one = [(1, 2), (2, 3), (3, 4), (3, 5)]
        edge_dict_two = {'test': False, 'pv': 5.44}
        edges_two = [(2, 1), (3, 2), (4, 3), (5, 3)]

        self.graph.directed = True
        self.graph.add_edges(edges_one, **edge_dict_one)
        self.graph.add_edges(edges_two, **edge_dict_two)

        for edge in edges_one:
            self.assertDictEqual(self.graph.edges[edge], edge_dict_one)
        for edge in edges_two:
            self.assertDictEqual(self.graph.edges[edge], edge_dict_two)

    def test_add_edges_unique_attributes(self):
        """
        Test add unique edge attributes included two tuple
        """

        edges = [(1, 2, {'weight': 1.0}), (2, 3, {'weight': 1.5}),
                 (3, 4, {'weight': 2.0}), (3, 5, {'weight': 2.5})]

        self.graph.add_edges(edges)

        for edge in edges:
            e = (edge[0], edge[1])
            self.assertDictEqual(self.graph.edges[e], edge[2])
            self.assertDictEqual(self.graph.edges[e[::-1]], edge[2])

    def test_add_edges_global_unique_attributes(self):
        """
        Test add unique edge attributes included two tuple and add a
        single global attribute to it
        """

        edges = [(1, 2, {'weight': 1.0}), (2, 3, {'weight': 1.5}),
                 (3, 4, {'weight': 2.0}), (3, 5, {'weight': 2.5})]

        self.graph.add_edges(edges, pv=True)

        for edge in edges:
            e = (edge[0], edge[1])
            attr = edge[2]
            attr['pv'] = True
            self.assertDictEqual(self.graph.edges[e], attr)
            self.assertDictEqual(self.graph.edges[e[::-1]], attr)


class TestGraphRemoveEdges(UnittestPythonCompatibility):
    """
    Test removal of edges in directed and undirected way
    """

    def setUp(self):
        """
        Build Graph with nodes and edges
        """

        self.graph = Graph()
        self.graph.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)], node_from_edge=True)

        self.assertTrue(len(self.graph) == 5)
        self.assertTrue(len(self.graph.nodes) == 5)
        self.assertTrue(len(self.graph.edges) == 10)
        self.assertTrue(len(self.graph.adjacency) == 5)

    def tearDown(self):
        """
        Test state after edge removal
        """

        if self.edges:

            # If undirected, add reversed edges
            if not self.graph.directed:
                self.edges.extend([e[::-1] for e in self.edges if e[::-1] not in self.edges])

            for edge in self.edges:

                # Edge should be removed
                self.assertTrue(edge not in self.graph.edges)

                # Nodes connected should still be there
                self.assertTrue(all([node in self.graph.nodes for node in edge]))

                # Adjacency should be corrected
                self.assertTrue(edge[1] not in self.graph.adjacency[edge[0]])

                # If directional, reverse edge still in graph
                if self.graph.directed:
                    rev_edge = edge[::-1]
                    if rev_edge not in self.edges:
                        self.assertTrue(rev_edge in self.graph.edges)

            # filled after addition
            self.assertTrue(len(self.graph) == 5)
            self.assertTrue(len(self.graph.nodes) == 5)
            self.assertTrue(len(self.graph.edges) == 10 - len(self.edges))
            self.assertTrue(len(self.graph.adjacency) == 5)

    def test_remove_edge_single_undirected(self):
        """
        Test removal of single undirected edge
        """

        self.edges = [(1, 2)]
        self.graph.remove_edge(*self.edges[0])

    def test_remove_edge_single_directed(self):
        """
        Test removal of single directed edge
        """

        self.graph.directed = True
        self.edges = [(1, 2)]
        self.graph.remove_edge(*self.edges[0])

    def test_remove_edge_multiple_undirected(self):
        """
        Test removal of multiple undirected edges
        """

        self.edges = [(1, 2), (2, 3), (4, 5)]
        self.graph.remove_edges(self.edges)

    def test_remove_edge_multiple_directed(self):
        """
        Test removal of multiple directed edges
        """

        self.graph.directed = True
        self.edges = [(1, 2), (2, 3), (4, 5)]
        self.graph.remove_edges(self.edges)

    def test_remove_edge_single_mixed(self):
        """
        Test removal of a single directed edge in a global undirected graph
        using local override of directionality
        """

        self.edges = [(1, 2)]
        self.graph.remove_edge(*self.edges[0], directed=True)

        self.graph.directed = True

    def test_remove_edge_multiple_mixed(self):
        """
        Test removal of multiple directed edges in a global undirected graph
        using local override of directionality
        """

        self.edges = [(1, 2), (2, 3), (4, 5)]
        self.graph.remove_edges(self.edges, directed=True)

        self.graph.directed = True

    def test_graph_clear(self):
        """
        Test clear method to removal all nodes and edges
        """

        self.edges = []
        self.graph.clear()

        self.assertTrue(len(self.graph) == 0)
        self.assertTrue(len(self.graph.nodes) == 0)
        self.assertTrue(len(self.graph.edges) == 0)
        self.assertTrue(len(self.graph.adjacency) == 0)
