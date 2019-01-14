# -*- coding: utf-8 -*-

"""
file: module_io_pydata_test.py

Unit tests for import and export of Python data objects
"""

from tests.module.unittest_baseclass import UnittestPythonCompatibility

from graphit.graph_io.io_pydata_format import read_pydata, write_pydata


class IterableObject(object):

    data = [1, 'two', 3.44, False]

    def __iter__(self):

        for item in self.data:
            yield item


class PyDataTest(UnittestPythonCompatibility):

    def test_pydata_list(self):
        """
        Test import/export of plain python list
        """

        intype = [1, 'two', False]
        graph = read_pydata(intype)

        self.assertListEqual(intype, write_pydata(graph))

    def test_pydata_list_nested(self):
        """
        Test import/export of nested python list
        """

        intype = [1, ['two', 'three'], [1, 2, 3, 4.33]]
        graph = read_pydata(intype)

        self.assertListEqual(intype, write_pydata(graph))

    def test_pydata_tuple(self):
        """
        Test import/export of plain python tuple
        """

        intype = (1, 'two', False)
        graph = read_pydata(intype)

        self.assertTupleEqual(intype, write_pydata(graph))

    def test_pydata_tuple_nested(self):
        """
        Test import/export of nested python tuple
        """

        intype = (1, ('two', 'three'), (1, 2, 3, 4.33))
        graph = read_pydata(intype)

        self.assertTupleEqual(intype, write_pydata(graph))

    def test_pydata_mixed_tuple_list(self):
        """
        Test import/export of mixed tuple list type
        """

        intype = [u'type', (1, 2, 3), False, [4.33, 2.33, 7.33]]
        graph = read_pydata(intype)

        self.assertListEqual(intype, write_pydata(graph))

    def test_pydata_dict(self):
        """
        Test import/export of python dict type
        """

        intype = {'one': 1, 'two': 2, 3: 'three', 'four': False}

        # Test level 0 import/export
        graph = read_pydata(intype, level=0)
        self.assertDictEqual(intype, write_pydata(graph))

        # Test level 1 import/export
        graph = read_pydata(intype, level=1)
        self.assertDictEqual(intype, write_pydata(graph, export_all=True))

    def test_pydata_dict_nested(self):
        """
        Test import/export of python nested dict type
        """

        intype = {'one': 1, 'two': {'extra': False}, 3: 'three', 'four': {'extra': True, 22: 'ok'}}

        # Test level 0 import/export
        graph = read_pydata(intype, level=0)
        self.assertDictEqual(intype, write_pydata(graph))

        # Test level 1 import/export
        graph = read_pydata(intype, level=1)
        self.assertDictEqual(intype, write_pydata(graph, export_all=True))

    def test_pydata_dict_single(self):
        """
        Test import/export of python dictionaries with only one key/value pair
        """

        intype = {'one': 1}

        # Test level 0 import/export
        graph = read_pydata(intype, level=0)
        self.assertDictEqual(intype, write_pydata(graph))

        # Test level 1 import/export
        graph = read_pydata(intype, level=1)
        self.assertDictEqual(intype, write_pydata(graph, export_all=True))

    def test_pydata_mixed_dict(self):
        """
        Test import/export of python mixed dict types
        """

        intype = {'one': 1, 'two': [1, 2, 3, 4], 3: ('a', 'b', 'c'), 'four': {'extra': True, 22: 'ok'}}

        # Test level 0 import/export
        graph = read_pydata(intype, level=0)
        self.assertDictEqual(intype, write_pydata(graph))

        # Test level 1 import/export
        graph = read_pydata(intype, level=1)
        self.assertDictEqual(intype, write_pydata(graph, export_all=True))

    def test_python_set(self):
        """
        Test import/export of python set type
        """

        intype = {'one', 'two', 3, False}
        graph = read_pydata(intype)

        self.assertSetEqual(intype, write_pydata(graph))
