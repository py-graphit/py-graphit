# -*- coding: utf-8 -*-

"""
file: graph_arraystorage_driver.py

Classes that store nodes, edges and their attributes as numpy arrays using the
Pandas package
"""

import weakref
import logging

from collections import MutableMapping
from numpy import nan as Nan
from pandas import DataFrame, Series

from graphit import __module__
from graphit.graph_storage_drivers.graph_driver_baseclass import GraphDriverBaseClass
from graphit.graph_storage_drivers.graph_storage_views import AdjacencyView

__all__ = ['ArrayStorage', 'init_arraystorage_driver']
logger = logging.getLogger(__module__)


def init_arraystorage_driver(nodes, edges):
    """
    ArrayStorage specific driver initiation method

    Returns a ArrayStorage instance for nodes and edges and a AdjacencyView
    for adjacency based on the initiated nodes and edges stores.

    :param nodes: Nodes to initiate nodes DictStorage instance
    :type nodes:  :py:list, :py:dict,
                  :graphit:graph_arraystorage_driver:DictStorage
    :param edges: Edges to initiate edges DictStorage instance
    :type edges:  :py:list, :py:dict,
                  :graphit:graph_arraystorage_driver:DictStorage

    :return:      Nodes and edges storage instances and Adjacency view.
    """

    node_storage = ArrayStorage(nodes)
    edge_storage = ArrayStorage(edges)
    adjacency_storage = AdjacencyView(node_storage, edge_storage)

    return node_storage, edge_storage, adjacency_storage


class SeriesStorage(MutableMapping):
    """
    SeriesStorage class

    Wrapper around the pandas Series object making it fully compliant with the
    native Python dict API by using the `collections.MutableMapping` abstract
    base class.
    Access to the native pandas Series methods is preserved.
    """

    __slots__ = ('_storage', '_dropna')

    def __init__(self, series):
        """
        Implement class __init__

        Registers the Pandas series object in the _storage attribute.
        The '_dropna' attribute controls if rows with Nan values are
        removed before returning elements from the series

        :param series: Pandas Series instance
        :type series:  :pandas:Series
        """

        self._storage = series
        self._dropna = True

    def __getattr__(self, attr):
        """
        Implement class __getattr__

        Exposes data by key as class attributes with support for calling
        methods on the pandas Series instance.
        If the key is not present, pass along to the default __getattribute__
        method.

        :param key: attribute name

        :return:    attribute value
        """

        if hasattr(self._storage, attr):
            return getattr(self._storage, attr)

        return object.__getattribute__(self, attr)

    def __getitem__(self, key):
        """
        Implement class __getitem__

        :param key: key name

        :return:    key value
        """

        if self._dropna:
            return self._storage.dropna()[key]
        return self._storage[key]

    def __setitem__(self, key, value):
        """
        Implement class __setitem__

        :param key:     key name
        :param value:   value to set
        """

        self._storage.loc[key] = value

    def __delitem__(self, key):
        """
        Implement class __delitem__

        Inplace removal (drop) of the key in the Series object.
        The Series is a view on the origin DataFrame where the key will thus be
        removed.

        :param key: key name
        """

        self._storage.drop(labels=key, inplace=True)

    def __iter__(self):
        """
        Implement class __iter__

        Iterate over the keys of a Series after dropping rows with Nan values.

        :return: Series keys
        """

        if self._dropna:
            return iter(self._storage.dropna().index)
        return iter(self._storage.index)

    def __len__(self):
        """
        Implement class __len__

        Return the number of key,value pairs in the Series after dropping Nan
        values.
        """

        if self._dropna:
            return len(self._storage.dropna())
        return len(self._storage)

    @property
    def series(self):
        """
        :return: the original pandas Series object
        :rtype:  :pandas:Series
        """

        return self._storage

    def to_dict(self, dropna=True):
        """
        Return a shallow copy of the Series as dictionary.

        :param dropna: drop Series rows having Nan values
        :type dropna:  :py:bool

        :rtype:        :py:dict
        """

        if self._dropna or dropna:
            return self._storage.dropna().to_dict()
        return self._storage.to_dict()


class ArrayStorage(GraphDriverBaseClass):
    """
    ArrayStorage class

    Provides a Pandas DataFrame based storage for nodes and edges.
    The class supports weak referencing of the internal DataFrame (_storage)
    using the weakref module to reduce memory footprint and enable true
    synchronized views across different instances of the DictStorage class.
    """

    __slots__ = ('_storage', '_view')

    def __init__(self, *args, **kwargs):
        """
        Implement class __init__

        Initiate the internal _storage DataFrame.
        If an ArrayStorage instance is provided, a _storage dictionary has been
        created and we will setup a weak reference to it. Otherwise init
        a new DataFrame using args and/or kwargs as input.
        """

        self._storage = DataFrame()
        self._view = None

        if len(args):
            if not len(args) == 1:
                raise TypeError('update expected at most 1 arguments, got {0}'.format(len(args)))
            mappable = args[0]

            # mappable is ArrayStorage instance, setup weakref to _storage
            if isinstance(mappable, ArrayStorage):
                self._storage = weakref.ref(mappable._storage)()

            # mappable is any type accepted by the DataFrame constructor
            elif mappable is not None:
                mappable = dict(mappable)
                try:
                    self._storage = DataFrame(mappable)
                except:
                    mappable = dict([(k, [v]) for k, v in mappable.items()])
                    self._storage = DataFrame(mappable)

            # no mappable, setup default DataFrame with optional kwargs
            else:
                self._storage = DataFrame(kwargs)
        else:
            self._storage = DataFrame(kwargs)

    def __delitem__(self, key):

        if key not in self:
            raise KeyError(key)

        if self.is_view:
            self._view.remove(key)

        self._storage.drop([key], axis=1, inplace=True)

    def __getitem__(self, key):
        """
        Implement class __getitem__

        :param key: key name

        :return:    key value
        """

        view = self._view_select()
        result = view.loc[:, key]
        if isinstance(result, Series):
            return SeriesStorage(result)

        return result

    def __getattr__(self, key):
        """
        Implement class __getattr__

        Exposes data by key as class attributes with support for calling
        methods on the DataFrame instance.
        If the key is not present, pass along to the default __getattribute__
        method.

        :param key: attribute name

        :return:    attribute value
        """

        if hasattr(self._storage, key):
            view_selection = self._view_select()

            result = getattr(view_selection, key)
            if isinstance(result, Series):
                return SeriesStorage(result)
            return result

        return object.__getattribute__(self, key)

    def __iter__(self):
        """
        Implement class __iter__

        Iterate over keys in _storage
        """

        view = self._view_select()
        for key in view.keys():
            yield key

    def __len__(self):

        if self.is_view:
            return len(self._view)
        return len(self.keys())

    def __setitem__(self, key, value):

        self.set(key, value)

    @property
    def dataframe(self):
        """
        :return: the original pandas DataFrame object
        :rtype:  :pandas:DataFrame
        """

        return self._storage

    def _view_select(self):

        view = self._storage
        if self.is_view:
            view = self._storage.loc[:, self._storage.columns.intersection(self._view)]

        if isinstance(view, Series):
            return SeriesStorage(view)
        return view

    def copy(self):
        """
        Return a deep copy of the storage class with the same view as
        the parent instance.

        :return:    deep copy of storage instance
        :rtype:     ArrayStorage
        """

        deepcopy = ArrayStorage(self._storage.copy(deep=True))
        if self.is_view:
            deepcopy.set_view(self._view)

        return deepcopy

    def get(self, key, default=None):

        view_selection = self._view_select()
        result = view_selection.get(key, default=default)

        if isinstance(result, Series):
            return SeriesStorage(result)
        return result

    def set(self, key, value):

        try:
            value = dict(value)
        except (ValueError, TypeError):
            logging.debug('Unable to convert value to dictionary: {0}'.format(type(value)))

        index = ['key']
        if isinstance(value, dict):
            index = value.keys()

        # Convert input dict to Series
        s = Series(value, index=index)

        # Add new series keys as row to DataFrame
        for name in s.index:
            if name not in self._storage.index:
                self._storage.loc[name, :] = Nan

        # Update DataFrame
        self._storage[key] = s

        # If new key and is_view, add to view
        if self.is_view:
            self._view.append(key)

    def to_dict(self, return_full=False):
        """
        Return a shallow copy of the full dictionary.

        If the current ArrayStorage represent a selective view on the parent
        dictionary then only return a dictionary with a shallow copy of the
        keys in the selective view.

        :param return_full: ignores is_view and return the full dictionary
        :type return_full:  bool

        :rtype:             :py:dict
        """

        view = self._storage
        if not return_full:
            view = self._view_select()

        # Single row then single value per column index
        if len(view.index) == 1:
            row = view.loc[view.index[0], :]
            return dict(zip(view.columns, row.values))

        return_dict = {}
        for k, v in view.items():
            return_dict[k] = v.dropna().to_dict()

        return return_dict

    def keys(self):
        """
        Implements a Python dict style 'keys' method

        Returns the keys of the DataFrame which equal the columns returned as
        pandas Index object. This is subsequently returned as plain list.

        :return:    dataframe column indexes (keys)
        :rtype:     :py:list
        """

        view = self._view_select()
        return list(view.keys())

    iterkeys = keys
    viewkeys = keys

    def items(self):

        view = self._view_select()
        for k, v in view.items():
            yield (k, SeriesStorage(v))

    iteritems = items
    viewitems = items

    def values(self):

        for item in self.items():
            yield item[1]

    itervalues = values
    viewvalues = values
