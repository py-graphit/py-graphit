# -*- coding: utf-8 -*-

"""
file: module_graphorm_test.py

Unit tests for the Graph Object Relations Mapper (orm)
"""

import os

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit.graph_io.io_tgf_format import read_tgf
from graphit.graph_orm import GraphORM


# ORM test classes
class ORMtestMo(object):

    @staticmethod
    def get_label():

        return "mo class"


class ORMtestBi(object):

    @staticmethod
    def get_label():

        return "bi class"


class ORMtestTgf6(object):

    def get_label(self):

        return "tgf6 class {0}".format(self.add)


class ORMtestTgf9(object):

    def get_label(self):

        return "tgf9 class {0}".format(self.add)


class TestGraphORMRegistration(UnittestPythonCompatibility):

    def setUp(self):
        """
        Init empty GraphORM object
        """

        self.orm = GraphORM()

    def test_graph_orm_exception_noneclass(self):
        """
        Registration 'class' argument should be a class else raise exception.
        """

        self.assertRaises(TypeError, self.orm.node_mapping.add, 'not_a_class', lambda x: x.get('key') == 'two')
        self.assertRaises(TypeError, self.orm.edge_mapping.add, 'not_a_class', lambda x: x.get('key') == 'two')

    def test_graph_orm_exception_nonefunction(self):
        """
        Registration 'match_func' argument should be a fucntion else raise
        exception.
        """

        self.assertRaises(TypeError, self.orm.node_mapping.add, ORMtestMo, 'not_a_function')
        self.assertRaises(TypeError, self.orm.edge_mapping.add, ORMtestMo, 122)

    def test_graph_orm_duplicate_registration(self):
        """
        Duplicate registration of node and edge mapping is not allowed
        """

        for n in range(2):
            self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')
        self.assertEqual(len(self.orm.node_mapping), 1)

        for n in range(2):
            self.orm.edge_mapping.add(ORMtestBi, lambda x: x.get('label') == 'bi')
        self.assertEqual(len(self.orm.edge_mapping), 1)

    def test_graph_orm_mapping_add(self):
        """
        Test adding mapping for node/edge
        """

        idx = self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')

        self.assertEqual(idx, 1)
        self.assertEqual(len(self.orm.node_mapping), 1)
        self.assertEqual(list(self.orm.node_mapping.keys()), [1])
        self.assertEqual(self.orm.node_mapping[1]['class'], ORMtestTgf6)
        self.assertEqual(self.orm.node_mapping[1]['mro_pos'], 0)

    def test_graph_orm_mapping_remove(self):
        """
        Test removal of mapping based on mapping ID
        """

        idx = self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')
        self.orm.node_mapping.remove(idx)

        self.assertEqual(len(self.orm.node_mapping), 0)
        self.assertTrue(idx not in self.orm.node_mapping)

    def test_graph_orm_mapping_update(self):
        """
        Test update of registered mapping based on mapping ID
        """

        idx = self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')
        self.orm.node_mapping[idx]['class'] = ORMtestTgf9

        self.assertEqual(self.orm.node_mapping[1]['class'], ORMtestTgf9)

    def test_graph_orm_mapping_update_from_mapping(self):
        """
        Test update from other orm mapping
        """

        self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')

        # Build second ORM
        second_orm = GraphORM()
        for cls in (ORMtestTgf9, ORMtestBi):
            second_orm.node_mapping.add(cls, lambda x: x.get('key') == 'six')

        # Update
        self.orm.node_mapping.update(second_orm.node_mapping)
        self.assertEqual(len(self.orm.node_mapping), 3)

    def test_graph_orm_mapping_update_from_mapping_with_duplicate(self):
        """
        Test update from other orm mapping
        """

        self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')

        # Build second ORM
        second_orm = GraphORM()
        for cls in (ORMtestTgf9, ORMtestTgf6, ORMtestBi):
            second_orm.node_mapping.add(cls, lambda x: x.get('key') == 'six')

        # Update
        self.orm.node_mapping.update(second_orm.node_mapping)
        self.assertEqual(len(self.orm.node_mapping), 3)

    def test_graph_orm_mapping_auto_increment_index(self):
        """
        Test automatic mapping index ID increment
        """

        # Add 3 mappings
        idx_list = [self.orm.node_mapping.add(cls, lambda x: x.get('key') == 'six') for
                    cls in (ORMtestTgf9, ORMtestTgf6, ORMtestBi)]

        self.assertEqual(len(self.orm.node_mapping), 3)
        self.assertEqual(list(self.orm.node_mapping.keys()), idx_list)

        # Remove index 2 and add new mapping. Index should be 4 and index 2
        # will not be reused
        self.orm.node_mapping.remove(2)
        idx = self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')
        self.assertEqual(idx, 4)


class TestGraphORM(UnittestPythonCompatibility):
    currpath = os.path.dirname(__file__)
    _gpf_graph = os.path.abspath(os.path.join(currpath, '../files/graph.tgf'))

    def setUp(self):
        """
        ConfigHandlerTests class setup

        Load graph from file and assign custom classes to labels and register
        with the ORM.
        """

        self.graph = read_tgf(self._gpf_graph)

        self.orm = GraphORM()
        self.orm.edge_mapping.add(ORMtestMo, lambda x: x.get('label') == 'mo')
        self.orm.edge_mapping.add(ORMtestBi, lambda x: x.get('label') == 'bi')
        self.orm.node_mapping.add(ORMtestTgf6, lambda x: x.get('key') == 'six')
        self.orm.node_mapping.add(ORMtestTgf9, lambda x: x.get('key') == 'nine' or x.get('ids') == 'edi')

        self.graph.orm = self.orm
        self.graph.nodes[6]['add'] = 6
        self.graph.nodes[6]['ids'] = 'edi'

    def test_graph_orm_mapping(self):
        """
        Test the class list resolved for a node mapping
        """

        d = self.graph.orm.node_mapping.match(self.graph, [6])
        self.assertEqual(d, [ORMtestTgf6, ORMtestTgf9])

    def test_graph_orm_node(self):
        """
        Test ORM class mapping for nodes
        """

        self.assertEqual(self.graph.getnodes(6).add, 6)
        self.assertTrue(hasattr(self.graph.getnodes(6), 'get_label'))
        self.assertEqual(self.graph.getnodes(6).get_label(), "tgf6 class 6")

        # Node 9 has a custom class but misses the 'add' attribute
        self.assertFalse(hasattr(self.graph.getnodes(9), 'add'))
        self.assertTrue(hasattr(self.graph.getnodes(9), 'get_label'))
        self.assertRaises(AttributeError, self.graph.getnodes(9).get_label)

    def test_graph_orm_edge(self):
        """
        Test ORM class mapping for edges
        """

        for e, v in self.graph.edges.items():
            label = v.get('label')
            if label == 'bi':
                self.assertTrue(hasattr(self.graph.getedges(e), 'get_label'))
                self.assertEqual(self.graph.getedges(e).get_label(), "bi class")
            elif label == 'mo':
                self.assertTrue(hasattr(self.graph.getedges(e), 'get_label'))
                self.assertEqual(self.graph.getedges(e).get_label(), "mo class")

    def test_graph_orm(self):
        """
        Test dynamic inheritance
        """

        # Get node 6 from the full graph and then children of 6 from node 6 object
        self.graph.root = 1
        node6 = self.graph.getnodes(6)
        children = node6.getnodes(9)

        # Node 6 should have node6 specific get_label method
        self.assertEqual(node6.get_label(), 'tgf6 class 6')

        # Changing the custom class 'add' attribute only affects the
        # particular node
        node6.add += 1
        self.assertEqual(node6.add, 7)
        self.assertRaises(AttributeError, children.get_label)

    def test_graph_orm_inherit(self):
        """
        Test inheritance of non-package classes in ORM generated classes
        """

        # Turn inheritance of
        self.graph.orm.inherit = False

        # First call to ORM from base, node 6 should still have 'add' attribute
        node6 = self.graph.getnodes(6)
        self.assertTrue('add' in node6)

        # Second call to ORM from node 6, node 9 should not have 'add'
        node9 = node6.getnodes(9)
        self.assertFalse(hasattr(node9, 'add'))

    def test_graph_mro(self):
        """
        Test python Method Resolution Order management
        """

        # Default behaviour
        d = self.graph.orm.get_nodes(self.graph, [6])
        dmro = [cls.__name__ for cls in d.mro()]
        self.assertEqual(dmro, ['GraphBase', 'ORMtestTgf6', 'ORMtestTgf9', 'GraphBase', 'object'])

        # ORMtestTgf9 first
        self.graph.orm.node_mapping[2]['mro_pos'] = -10
        d = self.graph.orm.get_nodes(self.graph, [6])
        dmro = [cls.__name__ for cls in d.mro()]
        self.assertEqual(dmro, ['GraphBase', 'ORMtestTgf9', 'ORMtestTgf6', 'GraphBase', 'object'])
