# -*- coding: utf-8 -*-

"""
file: graph_dictstorage_driver.py

Unified view based dictionary class used by the Graph class to store node, edge
and adjacency information.

Based on GraphDriverBaseClass it implements key, value and items abstract
methods using the Python 3.x concept of view based representations with the
added feature to define views as data mask on the storage level.
"""

import copy
import weakref

from graphit.graph_py2to3 import colabc, to_unicode, prepaire_data_dict
from graphit.graph_storage_drivers.graph_driver_baseclass import GraphDriverBaseClass
from graphit.graph_storage_drivers.graph_storage_views import AdjacencyView

__all__ = ['DictStorage', 'init_dictstorage_driver']


def init_dictstorage_driver(nodes, edges):
    """
    DictStorage specific driver initiation method

    Returns a DictStorage instance for nodes and edges and a AdjacencyView
    for adjacency based on the initiated nodes and edges stores.

    :param nodes: Nodes to initiate nodes DictStorage instance
    :type nodes:  :py:list, :py:dict,
                  :graphit:graph_dictstorage_driver:DictStorage
    :param edges: Edges to initiate edges DictStorage instance
    :type edges:  :py:list, :py:dict,
                  :graphit:graph_dictstorage_driver:DictStorage

    :return:      Nodes and edges storage instances and Adjacency view.
    """

    node_storage = DictStorage(nodes)
    edge_storage = DictStorage(edges)
    adjacency_storage = AdjacencyView(node_storage, edge_storage)

    return node_storage, edge_storage, adjacency_storage


class DictWrapper(dict):
    """
    Dummy wrapper around Python's native dict class to allow it to be weakly
    referenced by the weakref module.
    """
    pass


class KeysView(colabc.KeysView):
    """
    Handling dictionary key based views
    
    Extends the collections ABC KeysView class
    """
    
    __slots__ = ()

    def __str__(self):
        """
        Implements class __str__
        
        :return: keys in KeysView as set
        :rtype:  str
        """
        
        return repr(list(self))
    
    def __repr__(self):
        """
        Implements class __repr__
        
        :return: KeysView instance representation
        :rtype:  str
        """
        
        return ''.join((type(self).__name__, '(', repr(set(self)), ')'))


class ItemsView(colabc.ItemsView):
    """
    Handling dictionary items based views
    
    Extends the collections ABC ItemsView class
    """
    
    __slots__ = ()

    def __str__(self):
        """
        Implements class __str__
        
        :return: items in ItemsView as set
        :rtype:  str
        """
        
        return repr(tuple(self))
    
    def __repr__(self):
        """
        Implements class __repr__
        
        :return: ItemsView instance representation
        :rtype:  str
        """
        
        return ''.join((type(self).__name__, '(', repr(tuple(self)), ')'))


class ValuesView(colabc.ValuesView):
    """
    Handling dictionary value based views
    
    Extends the collections ABC ValuesView class
    """
    
    __slots__ = ()
    
    def __and__(self, other):
        """
        Implement class __and__
        
        Implements the bitwise 'and' (or &) which equals the intersection
        between the keys of self and other.

        :rtype:  :py:list
        """

        return [value for value in self if value in other]
    
    def __or__(self, other):
        """
        Implement class __or__
        
        Implements the bitwise 'or' (or |) which equals the union between the
        keys of this self and other.

        :rtype: :py:list
        """
        
        union = list(self)
        union.extend([value for value in other if value not in union])

        return union
    
    def __xor__(self, other):
        """
        Implement class __and__
        
        Implements the bitwise 'xor' (or ^) which equals the
        symmetric_difference between the keys of this and other.

        :rtype:  :py:list
        """

        sym_diff = [value for value in self if value not in other]
        sym_diff.extend([value for value in other if value not in self])

        return sym_diff
    
    def __sub__(self, other):
        """
        Implements class __sub__
        
        :return: difference between values in other with respect to self
        :rtype:  :py:list
        """
        
        return [value for value in self if value not in other]

    def __str__(self):
        """
        Implements class __str__
        
        :return: values in ValuesView as set
        :rtype:  str
        """
        
        return repr(self)
    
    def __repr__(self):
        """
        Implements class __repr__
        
        :return: ValuesView instance representation
        :rtype:  str
        """
        
        return ''.join((type(self).__name__, '(', repr(tuple(self)), ')'))


class DictStorage(GraphDriverBaseClass, dict):
    """
    DictStorage class
    
    Provides a Python native dict like class with unified keys, values, and
    items based dictionary views across Python distributions.
    The class supports weak referencing of the internal dictionary (_storage)
    using the weakref module to reduce memory footprint and enable true
    synchronized views across different instances of the DictStorage class.
    """

    __slots__ = ('_storage', '_view')

    def __init__(self, *args, **kwargs):
        """
        Implement class __init__
        
        Initiate the internal _storage dictionary.
        If a DictStorage instance is provided, a _storage dictionary has been
        created and we will setup a weak reference to it. Otherwise init
        a new dictionary using args and/or kwargs as input to the native
        Python dict constructor.
        """

        self._view = None
        self._storage = None

        if len(args):
            if not len(args) == 1:
                raise TypeError('update expected at most 1 arguments, got {0}'.format(len(args)))
            mappable = args[0]
            
            # mappable is DictStorage instance, setup weakref to _storage
            if isinstance(mappable, DictStorage):
                self._storage = weakref.ref(mappable._storage)()
            
            # mappable is any type accepted by the dict class constructor
            elif mappable is not None:
                self._storage = DictWrapper(mappable)
            
            # no mappable, setup default DictWrapper with optional kwargs
            else:
                self._storage = DictWrapper(**kwargs)
        else:
            self._storage = DictWrapper(**kwargs)

    def __getstate__(self):
        """
        Implement class __getstate__

        Enables the class to be pickled. Required because the class uses
        __slots__

        :return:    object content for pickling
        :rtype:     :py:dict
        """

        state = {}
        for key in self.__slots__:
            state[key] = getattr(self, key)

        return state

    def __setstate__(self, state):
        """
        Implement class __setstate__

        Enables the class to be unpickled. Required because the class uses
        __slots__

        :param state:    object content for unpickling
        :type state:     :py:dict
        """

        for key, value in state.items():
            if key in self.__slots__:
                setattr(self, key, value)

    def __iter__(self):
        """
        Implement class __iter__

        Iterate over keys in _storage
        """

        if self.is_view:
            return iter(self._view)

        return iter(self._storage)
    
    def __len__(self):
        """
        Implement class __len__

        Returns the number of items in the _storage or the selective
        view on it.
        """

        if self.is_view:
            return len(self._view)

        return len(self._storage)

    def copy(self):
        """
        Return a deep copy of the storage class with the same view as
        the parent instance.

        :return:    deep copy of storage instance
        :rtype:     DictStorage
        """

        deepcopy = DictStorage(copy.deepcopy(self._storage))
        if self.is_view:
            deepcopy.set_view(self._view)

        return deepcopy

    def to_dict(self, return_full=False):
        """
        Return a shallow copy of the full dictionary.
        
        If the current DictStorage represent a selective view on the parent
        dictionary then only return a dictionary with a shallow copy of the
        keys in the selective view.
        
        :param return_full: ignores is_view and return the full dictionary
        :type return_full:  bool
        
        :rtype:             :py:dict
        """
        
        return_dict = self._storage
        if self.is_view and not return_full:
            return_dict = {k: v for k, v in return_dict.items() if k in self._view}
        
        return return_dict

    def fromkeys(self, keys, value=None):
        """
        Return a shallow copy of the dictionary for selected keys.

        If the DictStorage instance represent a selective view of the main
        dictionary, only those keys will be considered.

        TODO: value=None results in a KeyError for View based comparison methods

        :param keys:  keys to return dictionary copy for
        :param value: Default value keys
        """

        return DictStorage([(k, value) for k in keys if k in self])

    def get(self, key, default=None):
        """
        Implement dictionary getter
        
        If the DictStorage instance represent a selective view of the main
        dictionary, only allow item getter for keys in the respective view.
        
        ..  note:: Do not use this method directly to add nodes or edges
                   from the graph as it may leave the graph in a funny state.
                   Use the graph add_node or add_edge methods instead.
        
        :param key:     dictionary key to get value for
        :param default: default value to return if key does not exist
        """
        
        if self.is_view:
            if key in self._view:
                return self._storage[key]
            return default
        
        return self._storage.get(key, default)
    
    def items(self):
        """
        Implement Python 3 dictionary like 'items' method that returns a
        DictView class.
        
        :return: dictionary items as tuple of key/value pairs
        :rtype:  ItemsView instance
        """
        
        return ItemsView(self)
    
    iteritems = items
    viewitems = items
    
    def keys(self):
        """
        Implement Python 3 dictionary like 'keys' method that returns a DictView
        class.
        
        :return: dictionary keys
        :rtype:  KeysView instance
        """
        
        return KeysView(self)
    
    iterkeys = keys
    viewkeys = keys
    
    def remove(self, key):
        """
        Remove key, value pairs from the dictionary
        
        If the DictStorage instance represent a selective view of the main
        dictionary, only allow item deletion for keys in the respective view.
        
        ..  note:: Do not use this method directly to remove nodes or edges
                   from the graph as it may leave the graph in a funny state.
                   Use the graph remove_node or remove_edge methods instead.
        
        :param key: dictionary key to remove
        """

        if key not in self.keys():
            raise KeyError('"{0}" not in storage or not part of selective view'.format(key))

        if self.is_view:
            self._view.remove(key)
        
        del self._storage[key]

    def set(self, key, value):
        """
        Implement dictionary setter
        
        ..  note::  Do not use this method directly to add new nodes or edges
            to the graph. Use the graph add_node or add_edge methods for this
            purpose instead.
        
        :param key:   dictionary key to add or update
        :param value: key value
        """
        
        self._storage[key] = to_unicode(value)
        if self.is_view:
            self._view.add(to_unicode(key))

    def update(self, *args, **kwargs):
        """
        Update key/value pairs also updating the view if needed
        
        :param other: other key/value pairs
        :type other:  :py:dict
        """

        kwargs = prepaire_data_dict(kwargs)

        self._storage.update(*args, **kwargs)
        if self.is_view:
            other = []
            if args:
                other = list(args[0].keys())
            self._view.update(other + list(kwargs.keys()))
    
    def values(self):
        """
        Implement Python 3 dictionary like 'values' method that returns a DictView
        class.
        
        :return: dictionary values
        :rtype:  ValuesView instance
        """
        
        return ValuesView(self)
    
    itervalues = values
    viewvalues = values
