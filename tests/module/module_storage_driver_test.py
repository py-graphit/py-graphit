# -*- coding: utf-8 -*-

"""
file: module_storage_driver_test.py

Unit tests graph nodes and edges storage drivers
"""

import random

from tests.module.unittest_baseclass import UnittestPythonCompatibility, MAJOR_PY_VERSION

from graphit.graph_storage_drivers.graph_dictstorage_driver import DictStorage
from graphit.graph_storage_drivers.graph_arraystorage_driver import ArrayStorage
from graphit.graph_storage_drivers.graph_storage_views import DataView


class _BaseStorageDriverTests(object):
    """
    Base class for storage driver unit tests

    Tests all of the abstract and derived methods in the 'GraphDriverBaseClass'
    base class inherited by storage specific drivers.

    TODO: Test set node/edge primary keys in directional/undirectional graph
    """

    # Abstract methods from MutableMapping class
    def test_storagedriver__delitem__(self):
        """
        Test Python dict-like __delitem__ method
        """

        key_to_remove = random.choice(list(self.mapping.keys()))

        # Remove key
        del self.storage[key_to_remove]
        self.assertTrue(key_to_remove not in self.storage)

        # Remove key that does not exist
        self.assertRaises(KeyError, self.storage.__delitem__, 'nokey')

    def test_storagedriver__getitem__(self):
        """
        Test Python dict-like __getitem__ method
        """

        for node, attr in self.mapping.items():
            self.assertDictEqual(attr, self.storage[node])

        # Get key that does not exist
        self.assertRaises(KeyError, self.storage.__getitem__, 'nokey')

    def test_storagedriver__len__(self):
        """
        Test Python dict-like __len__ method
        """

        self.assertEqual(len(self.storage), len(self.mapping))
        self.assertEqual(len(self.storage), len(self.storage.keys()))

    def test_storagedriver__setitem__(self):
        """
        Test Python dict-like __setitem__ method
        """

        key_to_change = random.choice(list(self.mapping.keys()))

        # Change value for existing key
        self.storage[key_to_change] = {'key': 2, 'extra': False}
        self.assertDictEqual({'key': 2, 'extra': False}, self.storage[key_to_change])

        # Add newkey, value pair
        self.storage[self.new_key] = {'key': 6}
        self.assertDictEqual({'key': 6}, self.storage[self.new_key])

    def test_storagedriver__iter__(self):
        """
        Test Python dict-like __iter__ method
        """

        for k in self.storage:
            self.assertTrue(k in self.mapping)

    # Derived methods from 'Mapping' class
    def test_storagedriver__contains__(self):
        """
        Test Python dict-like __contains__ method
        """

        self.assertTrue(random.choice(list(self.mapping.keys())) in self.storage)
        self.assertFalse(self.new_key in self.storage)

    def test_storagedriver__eq__(self):
        """
        Test Python dict-like __eq__ method
        """

        graph1 = self.storage_instance({'three': 3, 'four': 4, 'six': 6})
        self.assertFalse(self.storage == graph1)

        self.assertFalse(self.storage == ['four', 'six', 'three'])

    def test_storagedriver__ne__(self):
        """
        Test Python dict-like __ne__ method
        """

        graph1 = self.storage_instance({'three': 3, 'four': 4, 'six': 6})
        self.assertTrue(self.storage != graph1)

        self.assertTrue(self.storage != ['four', 'six', 'three'])

    def test_storagedriver_get(self):
        """
        Test Python dict-like get method
        """

        for node, attr in self.mapping.items():
            self.assertDictEqual(attr, self.storage.get(node))

        # Default getter
        self.assertTrue(self.storage.get(self.new_key, 6), 6)
        self.assertEqual(self.storage.get(self.new_key), None)

    def test_storagedriver_items(self, items=None):
        """
        Test Python dict-like items method.
        Return object may be a list or generator/view-like object
        """

        if items is None:
            items = self.storage.items()

        self.assertViewEqual(self.mapping.items(), list(items))

    def test_storagedriver_keys(self, keys=None):
        """
        Test Python dict-like keys method.
        Return object may be a list or generator/view-like object
        """

        if keys is None:
            keys = self.storage.keys()

        self.assertViewEqual(self.mapping.keys(), list(keys))

    def test_storagedriver_values(self, values=None):
        """
        Test Python dict-like values method.
        Return object may be a list or generator/view-like object
        """

        if values is None:
            values = self.storage.values()

        self.assertViewEqual(self.mapping.values(), list(values))

    # Derived methods from 'MutableMapping' class
    def test_storagedriver_clear(self):
        """
        Test Python dict-like clear method
        """

        self.storage.clear()
        self.assertEqual(len(self.storage), 0)

    def test_storagedriver_pop(self):
        """
        Test Python dict-like pop method.
        """

        key = random.choice(list(self.mapping.keys()))

        pop = self.storage.pop(key)
        self.assertDictEqual(self.mapping[key], pop)
        self.assertTrue(key not in self.storage)

    def test_storagedriver_popitem(self):
        """
        Test Python dict-like popitem method.
        """

        popitem = self.storage.popitem()
        self.assertTrue(popitem not in list(self.storage.items()))

    def test_storagedriver_update(self):
        """
        Test Python dict-like update method.
        """

        update = dict(zip(random.sample(self.mapping.keys(), 2),
                          [{'key': 8}, {'key': 9, 'last': True}]))

        self.storage.update(update)
        self.mapping.update(update)

        for node, attr in self.mapping.items():
            self.assertDictEqual(attr, self.storage[node])

        kw = {self.new_key: 6}
        self.storage.update(kw)
        self.assertTrue(self.new_key in self.storage)

    def test_storagedriver_setdefault(self):
        """
        Test Python dict-like setdefault method.
        """

        self.storage.setdefault(self.new_key, 10)
        self.assertTrue(self.new_key in self.storage)

    # Default class magic methods
    def test_storagedriver__str__(self):
        """
        Test Python __str__ method
        """

        self.assertEqual(str(sorted(self.storage)), str(sorted(self.mapping.keys())))

    def test_storagedriver__repr__(self):
        """
        Test Python __repr__ method
        """

        self.assertEqual(repr(self.storage), '<{0} object {1}: {2} items>'.format(type(self.storage).__name__,
                                                                                  id(self.storage), len(self.storage)))

    def test_storagedriver__getattr__(self):
        """
        Test Python dict-like __getattr__ method.
        Only for string based access so no edges
        """

        if isinstance(self.new_key, str):
            for node, attr in self.mapping.items():
                self.assertDictEqual(attr, getattr(self.storage, node))

        self.assertRaises(AttributeError, self.storage.__getattr__, 'nokey')

    # Derived dict-like methods
    def test_storagedriver_set(self):
        """
        Test dictionary set method.
        Not a default Python dict method
        """

        self.storage.set(self.new_key, 6)
        self.assertTrue(self.new_key in self.storage)

    def test_storagedriver_set_empty(self):
        """
        Test Python dict-like set without attributes
        equals adding only a node or edge with empty attribute store.
        """

        self.storage[self.new_key] = {}
        self.assertDictEqual({}, self.storage[self.new_key])

    def test_storagedriver_set_attributes(self):
        """
        Test Python dict-like set behaviour on node/edge attribute stores.
        """

        key = random.choice(list(self.mapping.keys()))
        attr = self.storage[key]

        # Check attribute get
        self.assertEqual(attr['key'], self.mapping[key]['key'])

        # Check setting existing key
        attr['key'] = 20
        self.assertEqual(self.storage[key]['key'], 20)

        # Check setting new key
        attr['new'] = True
        self.assertEqual(self.storage[key]['new'], True)

    def test_storagedriver_iteritems(self):
        """
        Iteritems and viewitems should be testable by regular items test
        """

        self.test_storagedriver_items(items=self.storage.iteritems())
        self.test_storagedriver_items(items=self.storage.viewitems())

    def test_storagedriver_iterkeys(self):
        """
        Iterkeys and viewkeys should be testable by regular keys test
        """

        self.test_storagedriver_keys(keys=self.storage.iterkeys())
        self.test_storagedriver_keys(keys=self.storage.viewkeys())

    def test_storagedriver_itervalues(self):
        """
        Itervalues and viewvalues should be testable by regular values test
        """

        self.test_storagedriver_values(values=self.storage.itervalues())
        self.test_storagedriver_values(values=self.storage.viewvalues())

    # 'View' based methods
    def test_storagedriver_view_get(self):
        """
        Test storage getter methods after a 'view' has been set on nodes or
        edges as primary keys.
        """

        # Select view and none view primary keys
        viewkeys = random.sample(self.mapping.keys(), 2)
        noneviewkeys = [k for k in self.mapping.keys() if k not in viewkeys]

        # Set and check the view
        self.storage.set_view(viewkeys)
        self.assertTrue(self.storage.is_view)

        # Get primary key based attributes
        self.assertEqual(self.storage.get(noneviewkeys[0], 2), 2)
        self.assertDictEqual(self.mapping[viewkeys[0]], self.storage.get(viewkeys[0], 2))
        self.assertRaises(KeyError, self.storage.__getitem__, noneviewkeys[0])

    def test_storagedriver_view_set(self):
        """
        Test storage setter methods after a 'view' has been set on nodes or
        edges as primary keys.
        """

        # Select view and none view primary keys
        viewkeys = random.sample(self.mapping.keys(), 2)
        noneviewkeys = [k for k in self.mapping.keys() if k not in viewkeys]
        sub = dict([(k, v) for k, v in self.mapping.items() if k in viewkeys])

        # Set and check the view
        self.storage.set_view(viewkeys)
        self.assertTrue(self.storage.is_view)

        # View based storage should equal the selection
        self.assertDictEqual(sub, self.storage.to_dict())
        self.assertRaises(KeyError, self.storage.__getitem__, noneviewkeys[0])

    def test_storagedriver_view_del(self):
        """
        Test storage delete methods after a 'view' has been set on nodes or
        edges as primary keys.
        """

        # Select view and none view primary keys
        viewkeys = random.sample(self.mapping.keys(), 2)
        noneviewkeys = [k for k in self.mapping.keys() if k not in viewkeys]

        # Set and check the view
        self.storage.set_view(viewkeys)
        self.assertTrue(self.storage.is_view)

        # Remove key that is in view
        del self.storage[viewkeys[0]]
        self.assertFalse(viewkeys[0] in self.storage)

        # Remove key that is not in view
        self.assertRaises(KeyError, self.storage.__delitem__, noneviewkeys[0])

    def test_storagedriver_view_clear(self):
        """
        Test storage clear method after a 'view' has been set on nodes or
        edges as primary keys.
        """

        # Select view and none view primary keys
        viewkeys = random.sample(self.mapping.keys(), 2)
        noneviewkeys = [k for k in self.mapping.keys() if k not in viewkeys]

        # Set and check the view
        self.storage.set_view(viewkeys)
        self.assertTrue(self.storage.is_view)

        # Graph clear only operates on selection if is_view
        self.storage.clear()
        self.assertTrue(len(self.storage) == 0)

        self.storage.reset_view()
        self.assertItemsEqual(self.storage.keys(), noneviewkeys)
        self.storage.clear()
        self.assertTrue(len(self.storage) == 0)

    def test_storagedriver_view_pop(self):
        """
        Test storage pop method after a 'view' has been set on nodes or
        edges as primary keys.
        """

        # Select view and none view primary keys
        viewkeys = random.sample(self.mapping.keys(), 2)
        noneviewkeys = [k for k in self.mapping.keys() if k not in viewkeys]

        # Set and check the view
        self.storage.set_view(viewkeys)
        self.assertTrue(self.storage.is_view)

        # View contains key
        pop = self.storage.pop(viewkeys[0])
        self.assertDictEqual(self.mapping[viewkeys[0]], pop)
        self.assertTrue(noneviewkeys[0] not in self.storage)

        # View does not contain key
        self.assertRaises(KeyError, self.storage.pop, noneviewkeys[0])

    def test_dictstorage_view_popitem(self):
        """
        Test storage popitem method after a 'view' has been set on nodes or
        edges as primary keys.
        """

        # Select view and none view primary keys
        viewkeys = random.sample(self.mapping.keys(), 2)
        noneviewkeys = [k for k in self.mapping.keys() if k not in viewkeys]

        # Set and check the view
        self.storage.set_view(viewkeys)
        self.assertTrue(self.storage.is_view)

        popitem = self.storage.popitem()
        self.assertTrue(popitem not in list(self.storage.items()))

        if not isinstance(popitem[1], dict):
            popitem = (popitem[0], popitem[1].to_dict())
        self.assertDictEqual(self.mapping[popitem[0]], popitem[1])

    def test_dictstorage_dataview_attrdict(self):
        """
        Test DataView that iterates over full attribute dictionaries
        """

        data = self.storage(data=True)

        self.assertIsInstance(data, DataView)

        # Iterate
        mapitem = self.mapping.items()
        for item in data:
            self.assertTrue(item in mapitem)

        # contains
        for item in mapitem:
            self.assertTrue(item in data)

        # getter
        for key, value in self.mapping.items():
            self.assertDictEqual(value, data[key])

        # getter with non-existing primary key raises KeyError
        self.assertRaises(KeyError, self.storage.__getitem__, 'nokey')

    def test_dictstorage_dataview_attrkey(self):
        """
        Test DataView that iterates over specific key/value pairs
        """

        data = self.storage(data='weight', default=1.00)

        self.assertIsInstance(data, DataView)

        # Iterate
        mapitem = [(k, v.get('weight', 1.00)) for k,v in self.mapping.items()]
        for item in data:
            self.assertTrue(item in mapitem)

        # contains
        for item in mapitem:
            self.assertTrue(item in data)

        # getter
        for key, value in self.mapping.items():
            self.assertEqual(value.get('weight', 1.00), data[key])

    # Other methods
    def test_storagedriver_creation(self):
        """
        Test default Python dict-like creation from iterable and/or mappings
        """

        # Storage from a native dict
        fromdict = self.storage_instance(self.mapping)
        self.assertViewEqual(self.mapping, fromdict)

        # Storage from keyword arguments (only for nodes)
        if all([isinstance(k, str) for k in self.mapping]):
            frommap = self.storage_instance(**self.mapping)
            self.assertViewEqual(self.mapping, frommap)

        # Storage from list of tuples
        frommap = self.storage_instance(self.mapping.items())
        self.assertViewEqual(self.mapping, frommap)

        # Storage from a list of keys
        keys = random.sample(self.mapping.keys(), 2)
        new_d = fromdict.fromkeys(keys, 1)
        self.assertDictEqual(self.mapping.fromkeys(keys, 1), new_d.to_dict())

    def test_storagedriver_copy(self):
        """
        Test copy storage instance copy method
        """

        # Copy full storage instance
        copy = self.storage.copy()
        self.assertFalse(id(self.storage) == id(copy))
        self.assertFalse(id(self.storage._storage) == id(copy._storage))

        # Copy full storage instance including view
        viewkeys = random.sample(self.mapping.keys(), 2)
        self.storage.set_view(viewkeys)

        copy = self.storage.copy()
        self.assertFalse(id(self.storage) == id(copy))
        self.assertFalse(id(self.storage._storage) == id(copy._storage))
        self.assertEqual(len(self.storage), len(copy))
        self.assertTrue(len(copy) < len(copy._storage))

    def test_storagedriver_truethtest(self):
        """
        Test methods for 'existence' truth test
        """

        # An empty storage instance
        empty = self.storage_instance()
        self.assertIsNotNone(empty is None)
        self.assertEqual(len(empty), 0)

        # A storage instance with content
        self.assertIsNotNone(self.storage is None)
        self.assertNotEqual(len(self.storage), 0)

    def test_storagedriver_comparison(self):
        """
        Test rich key based comparison operators between two storage objects
        """

        if isinstance(self.new_key, str):
            graph1 = self.storage_instance({'three': 3, 'four': 4, 'six': 6})
            graph2 = self.storage_instance({'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6})

            self.assertEqual(self.storage.intersection(graph1), {'four', 'three'})
            self.assertEqual(self.storage.difference(graph1), {'five', 'two', 'one'})
            self.assertEqual(self.storage.symmetric_difference(graph1), {'six', 'five', 'two', 'one'})
            self.assertEqual(self.storage.union(graph1), {'six', 'three', 'one', 'four', 'five', 'two'})
            self.assertFalse(self.storage.isdisjoint(graph1))
            self.assertFalse(self.storage.issubset(self.storage, propper=True))
            self.assertTrue(self.storage.issubset(self.storage, propper=False))
            self.assertTrue(graph2.issuperset(self.storage, propper=True))
            self.assertTrue(self.storage.issuperset(self.storage, propper=False))

            # Comparison operators between DictStorage Instances
            self.assertEqual(self.storage & graph1, {'four', 'three'})
            self.assertEqual(self.storage ^ graph1, {'six', 'five', 'two', 'one'})
            self.assertEqual(self.storage | graph1, {'six', 'three', 'one', 'four', 'five', 'two'})
            self.assertFalse(self.storage < self.storage)
            self.assertTrue(self.storage <= self.storage)
            self.assertTrue(graph2 > self.storage)
            self.assertTrue(self.storage >= self.storage)

            # Comparison operators between DictStorage Instance and other instance
            # that can be converted to set representation
            self.assertEqual(self.storage & ['four', 'six', 'three'], {'four', 'three'})
            self.assertEqual(self.storage ^ ['four', 'six', 'three'], {'six', 'five', 'two', 'one'})
            self.assertEqual(self.storage | ['four', 'six', 'three'], {'six', 'three', 'one', 'four', 'five', 'two'})


class TestDictStorageNodes(_BaseStorageDriverTests, UnittestPythonCompatibility):
    """
    Unit tests for DictStorage class storing nodes
    """

    def setUp(self):

        self.new_key = 'six'
        self.mapping = {'one': {'key': 1},
                        'two': {'key': 2, 'extra': True},
                        'three': {'key': 3, 'type': 'node'},
                        'four': {'key': 4, 'weight': 1.33},
                        'five': {'key': 5, 'weight': 3.11}}

        self.storage_instance = DictStorage
        self.storage = DictStorage(self.mapping)

    def test_dictstorage_view_magicmethods(self):
        """
        Test dictionary magic methods for a default dictionary
        and for on with a selective view on the main dict.
        """

        # Selective view
        self.storage.set_view(['one', 'three'])
        self.assertEqual(len(self.storage), 2)
        self.assertTrue('one' in self.storage)
        self.assertFalse('five' in self.storage)

        if MAJOR_PY_VERSION == 2:
            self.assertEqual(str(self.storage), "[u'one', u'three']")
        else:
            self.assertEqual(str(self.storage), "['one', 'three']")
        self.assertEqual(repr(self.storage), '<DictStorage object {0}: 2 items>'.format(id(self.storage)))

    def test_dictstorage_keysview_comparison(self):
        """
        Test the DictStorage view based keys comparison methods
        """

        keyview = self.storage.keys()
        other = DictStorage({'two': 2, 'three': 3, 'four': 4, 'six': 6})

        self.assertSetEqual(keyview & other.keys(), {'four', 'two', 'three'})
        self.assertSetEqual(keyview | other.keys(), {'six', 'three', 'two', 'four', 'five', 'one'})
        self.assertSetEqual(keyview - other.keys(), {'five', 'one'})
        self.assertSetEqual(keyview ^ other.keys(), {'five', 'one', 'six'})

    def test_dictstorage_valuesview_comparison(self):
        """
        Test the DictStorage view based values comparison methods
        """

        values = self.storage.values()
        self.storage[self.new_key] = 6

        other = DictStorage(dict([(k, v) for k, v in self.mapping.items() if k in ['two', 'three', 'four']]))
        other[self.new_key] = 6

        self.assertItemsEqual(values & other.values(), [6, {'key': 3, 'type': 'node'}, {'key': 4, 'weight': 1.33},
                                                       {'extra': True, 'key': 2}])
        self.assertItemsEqual(values | other.values(), [6, {'key': 3, 'type': 'node'}, {'key': 1},
                                                       {'key': 4, 'weight': 1.33}, {'key': 5, 'weight': 3.11},
                                                       {'extra': True, 'key': 2}])
        self.assertItemsEqual(values - other.values(), [{'key': 1}, {'key': 5, 'weight': 3.11}])
        self.assertItemsEqual(values ^ other.values(), [{'key': 1}, {'key': 5, 'weight': 3.11}])

    def test_dictstorage_valuesview_contain(self):
        """
        Test valuesview __contain__
        """

        values = self.storage.values()

        key = random.choice(list(self.mapping.keys()))
        self.assertTrue(self.mapping[key] in values)

    def test_dictstorage_itemsview_contain(self, items=None):
        """
        Test itemview __contain__
        """

        items = self.storage.items()

        key = random.choice(list(self.mapping.keys()))
        self.assertTrue((key, self.mapping[key]) in items)

    def test_dictstorage_itemsview(self):
        """
        Test Python dict items method. This should be the python 3.x compatible
        items view object.
        """

        items = self.storage.items()

        # Adding a new item should be reflected in the Values View
        self.storage[self.new_key] = 6
        self.mapping[self.new_key] = 6

        self.assertTrue(len(items) == 6)
        self.assertViewEqual(self.mapping.items(), items)

    def test_dictstorage_keysview(self):
        """
        Test Python dict keys method. This should be the python 3.x compatible
        keys view object.
        """

        keys = self.storage.keys()

        # Adding a new item should be reflected in the Keys View
        self.storage[self.new_key] = 6
        self.mapping[self.new_key] = 6

        self.assertTrue(len(keys) == 6)
        self.assertViewEqual(self.mapping.keys(), keys)

    def test_dictstorage_valuesview(self):
        """
        Test Python dict values method. This should be the python 3.x compatible
        values view object.
        """

        values = self.storage.values()

        # Adding a new item should be reflected in the Values View
        self.storage[self.new_key] = 6
        self.mapping[self.new_key] = 6

        self.assertTrue(len(values) == 6)
        self.assertViewEqual(self.mapping.values(), values)


class TestDictStorageEdges(_BaseStorageDriverTests, UnittestPythonCompatibility):
    """
    Unit tests for DictStorage class storing nodes
    """

    def setUp(self):

        self.new_key = (5, 6)
        self.mapping = {(1, 2): {'key': 1},
                        (2, 1): {'key': 2, 'extra': True},
                        (3, 2): {'key': 3, 'type': 'node'},
                        (4, 5): {'key': 4, 'weight': 1.33},
                        (2, 5): {'key': 5, 'weight': 3.11}}

        self.storage_instance = DictStorage
        self.storage = DictStorage(self.mapping)


class TestArrayStorageNodes(_BaseStorageDriverTests, UnittestPythonCompatibility):
    """
    Unit tests for ArrayStorage class storing nodes
    """

    def setUp(self):

        self.new_key = 'six'
        self.mapping = {'one': {'key': 1},
                        'two': {'key': 2, 'extra': True},
                        'three': {'key': 3, 'type': 'node'},
                        'four': {'key': 4, 'weight': 1.33},
                        'five': {'key': 5, 'weight': 3.11}}

        self.storage_instance = ArrayStorage
        self.storage = ArrayStorage(self.mapping)

    def assertDictEqual(self, expected_seq, actual_seq, msg=None):
        """
        Convert actual_seq to dictionary

        The actual_seq is a DataFrame or Series in a ArrayStore. Although they
        behave as dictionaries they will not pass the isinstance == dict test
        of the default assertDictEqual.

        Convert actual_seq to dictionary explicitly by calling its 'to_dict'
        method then passing it to assertDictEqual.
        """

        if not isinstance(actual_seq, dict):
            actual_seq = actual_seq.to_dict()

        return super(UnittestPythonCompatibility, self).assertDictEqual(expected_seq, actual_seq)

    def assertViewEqual(self, expected_seq, actual_seq, msg=None):
        """
        Test equality in items even if they are 'view' based
        """

        new = []
        for item in actual_seq:
            if isinstance(item, tuple):
                if hasattr(item[1], 'to_dict'):
                    new.append((item[0], item[1].to_dict()))
                else:
                    new.append(item)
            else:
                if hasattr(item, 'to_dict'):
                    new.append(item.to_dict())
                else:
                    new.append(item)

        return all([t in new for t in expected_seq]) and all([t in expected_seq for t in new])

    def test_arraystorage_dataframe_methods(self):
        """
        Test access to DataFrame methods from the ArrayStorage instance
        """

        self.assertIsNotNone(self.storage.describe())
        self.assertIsNotNone(self.storage.index)


class TestArrayStorageEdges(_BaseStorageDriverTests, UnittestPythonCompatibility):
    """
    Unit tests for ArrayStorage class storing nodes
    """

    def setUp(self):

        self.new_key = (5, 6)
        self.mapping = {(1, 2): {'key': 1},
                        (2, 1): {'key': 2, 'extra': True},
                        (3, 2): {'key': 3, 'type': 'node'},
                        (4, 5): {'key': 4, 'weight': 1.33},
                        (2, 5): {'key': 5, 'weight': 3.11}}

        self.storage_instance = ArrayStorage
        self.storage = ArrayStorage(self.mapping)

    def assertDictEqual(self, expected_seq, actual_seq, msg=None):
        """
        Convert actual_seq to dictionary

        The actual_seq is a DataFrame or Series in a ArrayStore. Although they
        behave as dictionaries they will not pass the isinstance == dict test
        of the default assertDictEqual.

        Convert actual_seq to dictionary explicitly by calling its 'to_dict'
        method then passing it to assertDictEqual.
        """

        if not isinstance(actual_seq, dict):
            actual_seq = actual_seq.to_dict()

        return super(TestArrayStorageEdges, self).assertDictEqual(expected_seq, actual_seq)

    def assertViewEqual(self, expected_seq, actual_seq, msg=None):
        """
        Test equality in items even if they are 'view' based
        """

        new = []
        for item in actual_seq:
            if isinstance(item, tuple):
                if hasattr(item[1], 'to_dict'):
                    new.append((item[0], item[1].to_dict()))
                else:
                    new.append(item)
            else:
                if hasattr(item, 'to_dict'):
                    new.append(item.to_dict())
                else:
                    new.append(item)

        return all([t in new for t in expected_seq]) and all([t in expected_seq for t in new])

    def test_arraystorage_dataframe_methods(self):
        """
        Test access to DataFrame methods from the ArrayStorage instance
        """

        self.assertIsNotNone(self.storage.describe())
        self.assertIsNotNone(self.storage.index)
