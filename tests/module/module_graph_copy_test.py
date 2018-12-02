# -*- coding: utf-8 -*-

"""
file: module_graph_copy_test.py

Unit tests for Graph copy related methods
"""

import copy

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit import Graph


class TestGraphCopy(UnittestPythonCompatibility):
    """
    Test Graph copy and deepcopy methods
    """

    def setUp(self):
        """
        Build default graph with nodes, edges and attributes
        """

        self.graph = Graph()
        self.graph.add_nodes([('g', {'weight': 1.0}), ('r', {'weight': 1.5}), ('a', {'weight': 2.0}),
                              ('p', {'weight': 2.5}), ('h', {'weight': 3.0})])
        self.graph.add_edges([(1, 2), (2, 3), (3, 4), (3, 5), (4, 5)], isedge=True)

    def tearDown(self):
        """
        Test copied state
        Testing equality in node, edge and adjacency data stores is based on
        the internal '_storage' object and not so much the storage object
        itself which is often just a wrapper.
        """

        # Main Graph object is new
        self.assertTrue(id(self.copied) != id(self.graph))

        if self.shallow:

            # Internal node and edge stores point to parent.
            self.assertEqual(id(self.copied.nodes._storage), id(self.graph.nodes._storage))
            self.assertEqual(id(self.copied.edges._storage), id(self.graph.edges._storage))

            # ORM and origin objects point to parent
            self.assertEqual(id(self.copied.orm), id(self.graph.orm))
            self.assertEqual(id(self.copied.origin), id(self.graph.origin))

        else:

            # Internal node and edge stores point to parent.
            self.assertNotEqual(id(self.copied.nodes._storage), id(self.graph.nodes._storage))
            self.assertNotEqual(id(self.copied.edges._storage), id(self.graph.edges._storage))

            # ORM and origin objects point to parent
            self.assertNotEqual(id(self.copied.orm), id(self.graph.orm))
            self.assertNotEqual(id(self.copied.origin), id(self.graph.origin))

    def test_graph_copy_shallow(self):
        """
        Test making a shallow copy of a graph. This essentially copies the
        Graph object while linking tot the data store in the parent Graph
        """

        self.shallow = True
        self.copied = self.graph.copy(deep=False)

    def test_graph_copy_deep(self):
        """
        Test making a deep copy of a graph (default) copying everything
        """

        self.shallow = False
        self.copied = self.graph.copy()

    def test_graph_buildin_copy_shallow(self):
        """
        Test making a shallow copy of a graph using the 'copy' method of the
        copy class. This calls the Graph.copy method
        """

        self.shallow = True
        self.copied = copy.copy(self.graph)

    def test_graph_buildin_copy_deep(self):
        """
        Test making a deep copy of a graph using the 'deepcopy' method of the
        copy class. This calls the Graph.copy method
        """

        self.shallow = False
        self.copied = copy.deepcopy(self.graph)

    def test_graph_buildin_copy_deep_view(self):
        """
        Test copying subgraphs either with the set 'view' only or the full
        origin graph (full graph)
        """

        # Regular copy
        self.shallow = False
        self.copied = copy.deepcopy(self.graph)

        # Build subgraph, same origin
        view = self.graph.getnodes([3,4,5])
        self.assertEqual(id(view.origin), id(self.graph.origin))

        # Deep copy with or without view, different origin
        copy_view = view.copy(deep=True, copy_view=False)
        copy_full = view.copy(deep=True, copy_view=True)
        self.assertNotEqual(id(copy_view.origin), id(self.graph.origin))
        self.assertNotEqual(id(copy_full.origin), id(self.graph.origin))

        # Subgraph 'view' should be identical to the original
        # regardless the copy mode
        self.assertEqual(copy_view.nodes.keys(), view.nodes.keys())
        self.assertEqual(copy_view.edges.keys(), view.edges.keys())
        self.assertEqual(copy_view.adjacency.keys(), view.adjacency.keys())
        self.assertEqual(copy_full.nodes.keys(), view.nodes.keys())
        self.assertEqual(copy_full.edges.keys(), view.edges.keys())
        self.assertEqual(copy_full.adjacency.keys(), view.adjacency.keys())

        # The view copy origin should either be identical to the view
        # (copy_view = True) or to the full graph (copy_view = False)
        self.assertEqual(list(copy_view.nodes._storage.keys()), list(view.nodes.keys()))
        self.assertEqual(list(copy_full.nodes._storage.keys()), list(view.origin.nodes.keys()))

        # The copy_full has its origin equals self and thus copy_full.origin.nodes
        # equals copy_full.nodes. However, the view is also set which means that
        # by default the full graph is not accessible without resetting it
        copy_full.nodes.reset_view()
        self.assertEqual(copy_full.nodes.keys(), self.graph.nodes.keys())
