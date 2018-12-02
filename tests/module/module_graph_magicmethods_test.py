# -*- coding: utf-8 -*-

"""
file: module_graph_magicmethods_test.py

Unit tests for Graph magic methods
"""

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

    def test_magic_method_eq(self):
        """
        Test Graph equality __eq__ (==) test
        """

        self.assertTrue(self.graph == self.graph)
        self.assertTrue(self.graph.getnodes([1, 3, 4]) == self.graph.getnodes([1, 3, 4]))
        self.assertTrue(self.graph == self.graph.copy(deep=True))

        self.assertFalse(self.graph.getnodes([1, 2]) == self.graph.getnodes([2, 3]))
        self.assertFalse(self.graph.getedges([(1, 2), (2, 3)]) == self.graph.getnodes([2, 3]))

    def test_magic_method_add(self):
        """
        Test Graph addition __add__ (+) support
        """

        # Adding self to self does not change anything
        self.assertEqual(self.graph + self.graph, self.graph)

        # Adding sub graphs together to yield the full graph only works if
        # there is an overlap in the graphs connecting them together. Without
        # the overlap the connecting edges are lost
        sub1 = self.graph.getnodes([1, 2, 3])
        sub2 = self.graph.getnodes([3, 4, 5])
        self.assertEqual(sub1 + sub2, self.graph)

        sub1 = self.graph.getnodes([1, 2, 3])
        sub2 = self.graph.getnodes([4, 5])
        self.assertNotEqual(sub1 + sub2, self.graph)

        # Sub graphs are still views on the origin
        combined = sub1  + sub2
        self.assertTrue(combined.nodes.is_view)
        self.assertTrue(combined.edges.is_view)
        self.assertEqual(id(combined.origin), id(self.graph.origin))

        # Adding graphs together that do not share a common origin
        sub1_copy = sub1.copy()
        combined = sub1_copy  + sub2
        self.assertFalse(combined.nodes.is_view)
        self.assertFalse(combined.edges.is_view)
        self.assertNotEqual(id(combined.origin), id(self.graph.origin))

    def test_magic_method_iadd(self):
        """
        Test Graph in place addition __iadd__ (+=) support
        """

        # Adding sub graphs together to yield the full graph only works if
        # there is an overlap in the graphs connecting them together. Without
        # the overlap the connecting edges are lost
        sub1 = self.graph.getnodes([1, 2, 3])
        sub2 = self.graph.getnodes([3, 4, 5])
        sub1 += sub2
        self.assertEqual(sub1, self.graph)

        sub1 = self.graph.getnodes([1, 2, 3])
        sub2 = self.graph.getnodes([4, 5])
        sub1 += sub2
        self.assertNotEqual(sub1, self.graph)

        # Sub graphs are still views on the origin
        self.assertTrue(sub1.nodes.is_view)
        self.assertTrue(sub1.edges.is_view)
        self.assertEqual(id(sub1.origin), id(self.graph.origin))

        # Adding graphs together that do not share a common origin
        sub1_copy = sub1.copy()
        sub1_copy += sub2
        self.assertFalse(sub1_copy.nodes.is_view)
        self.assertFalse(sub1_copy.edges.is_view)
        self.assertNotEqual(id(sub1_copy.origin), id(self.graph.origin))

    def test_magic_method_contains(self):
        """
        Test Graph contains __contains__ test
        """

        # Equal graphs also contain each other
        self.assertTrue(self.graph in self.graph)

        sub1 = self.graph.getnodes([1, 2, 3])
        sub2 = self.graph.getnodes([4, 5])
        self.assertTrue(sub1 in self.graph)
        self.assertFalse(sub2 in sub1)

    def test_magic_method_getitem(self):
        """
        Test Graph dictionary style __getitem__ item lookup
        """

        self.assertEqual(self.graph[2], self.graph.getnodes(2))
        self.assertEqual(self.graph[(2, 3)], self.graph.getedges((2, 3)))

        # Support for slicing
        self.assertEqual(self.graph[2:], self.graph.getnodes([2, 3, 4, 5]))
        self.assertEqual(self.graph[2:4], self.graph.getnodes([2, 3]))
        self.assertEqual(self.graph[1:5:2], self.graph.getnodes([1, 3]))
        self.assertTrue(self.graph[1:-1].empty())

    def test_magic_method_ge(self):
        """
        Test Graph greater-then or equal __ge__ (>=) to support
        """

        sub = self.graph.getnodes([2, 3, 4])

        self.assertTrue(self.graph >= sub)
        self.assertFalse(sub >= self.graph)
        self.assertTrue(sub >= sub)

    def test_magic_method_gt(self):
        """
        Test Graph greater-then __gt__ (>) support
        """

        sub = self.graph.getnodes([2, 3, 4])

        self.assertTrue(self.graph > sub)
        self.assertFalse(sub > self.graph)

    def test_magic_method_len(self):
        """
        Test Graph length __len__ support
        """

        self.assertEqual(len(self.graph), 5)

    def test_magic_method_le(self):
        """
        Test Graph less-then or equal __le__ (<=) to support
        """

        sub = self.graph.getnodes([2, 3, 4])

        self.assertTrue(sub <= self.graph)
        self.assertFalse(self.graph <= sub)
        self.assertTrue(sub <= sub)

    def test_magic_method_lt(self):
        """
        Test Graph greater-then __lt__ (<) support
        """

        sub = self.graph.getnodes([2, 3, 4])

        self.assertTrue(sub < self.graph)
        self.assertFalse(self.graph < sub)

    def test_magic_method_ne(self):
        """
        Test Graph equality __ne__ (!=) test
        """

        self.assertFalse(self.graph != self.graph)
        self.assertFalse(self.graph.getnodes([1, 3, 4]) != self.graph.getnodes([1, 3, 4]))
        self.assertFalse(self.graph != self.graph.copy(deep=True))

        self.assertTrue(self.graph.getnodes([1, 2]) != self.graph.getnodes([2, 3]))
        self.assertTrue(self.graph.getedges([(1, 2), (2, 3)]) != self.graph.getnodes([2, 3]))

    def test_magic_method_sub(self):
        """
        Test Graph subtract __sub__ (-) support
        """

        sub = self.graph.getnodes([2, 3, 4])
        self.assertEqual(self.graph - sub, self.graph.getnodes([1,5]))
        self.assertTrue(len(sub - self.graph) == 0)

    def test_magic_method_isub(self):
        """
        Test Graph inplace subtract __isub__ (-=) support
        """

        cp = self.graph.copy()
        self.graph -= self.graph.getnodes([2, 3, 4])
        self.assertEqual(self.graph, cp.getnodes([1,5]))
