# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: graph_driver_baseclass.py

"""
Storage driver abstract base class

Graphit uses dedicated data stores for node and edge data. Access is enabled
using an API that reassembles a Python dictionary with a node or edge ID as
'key' and a node/edge data dictionary as 'value'.

The API is formalized in the `GraphDriverBaseClass` base class that defines
abstract and derived methods required for the dict-like API similar to the
'MutableMapping' abstract base class from the `collections` module.
The data stores are decoupled from the main graph object structure by weak
referencing through Pythons `weakref` module.

The `GraphDriverBaseClass` uses data 'views' to allow instances of the driver
class to represent a subset of nodes/edges while still having the same weak
reference to the full data storage object. A 'view' is a simple list (_view)
storing the node/edge primary keys.

The `GraphDriverBaseClass` facilitates easy creation of different storage
backends that can be transparently used as Python dictionaries in graphit
graphs.

.. note::
    The developer of new a new storage driver is responsible for initializing
    an empty '_view' list and providing support for 'views' in the
    implementation of the abstract methods.
"""

import abc
import copy
import logging

from graphit import __module__
from graphit.graph_py2to3 import to_unicode, colabc
from graphit.graph_storage_drivers.graph_storage_views import DataView

__all__ = ['GraphDriverBaseClass']
logger = logging.getLogger(__module__)


class GraphDriverBaseClass(colabc.MutableMapping):
    """
    Abstract base class for graph data storage drivers

    This is the boilerplate class for the implementation of node and edge
    storage driver classes in graphit.
    It exposes a Python dict-like API by using the 'MutableMapping' abstract
    base class from the 'collections' module. In addition it implements
    support for several methods to provide support for list-like method and
    rich set-like comparison methods.

    The following abstract methods from the 'MutableMapping' class are
    required:

        * __getitem__, __setitem__, __delitem__, __iter__, __len__

    The following abstract methods for dictionary 'view' like iteration are
    required:

        * iterkeys, itervalues, iteritems

    All other methods are derived from the abstract methods but may be
    overloaded if it benefits efficiency for a given storage backend for
    instance.

    .. note::

        please note that the 'GraphDriverBaseClass' uses data 'views' to
        allow instances of the driver class to represent a subset of nodes
        edges while still having the same weak reference to the full data
        storage object. A 'view' is a simple list (_view) storing the node
        edge primary keys.
        The empty '_view' list needs to be initialized by the storage driver
        and support for 'views' needs to be implemented for the abstract
        methods.
    """

    @abc.abstractmethod
    def iteritems(self):
        """
        Implement Python 3.x dictionary like 'items' iterator method that
        returns a view on the items in the data store.
        The `viewitems` equals `iteritems` and implements the Python 2.7
        equivalent.

        If the storage instance does not support view based iterations then
        `iteritems` should default to the `items` method

        :return: data items as tuple of key/value pairs
        :rtype:  items view instance
        """

        return

    @abc.abstractmethod
    def iterkeys(self):
        """
        Implement Python 3.x dictionary like 'keys' iterator method that
        returns a view on the keys in the data store.
        The `viewkeys` equals `iterkeys` and implements the Python 2.7
        equivalent.

        If the storage instance does not support view based iterations then
        `iterkeys` should default to the `keys` method

        :return: data keys
        :rtype:  keys view instance
        """

        return

    @abc.abstractmethod
    def itervalues(self):
        """
        Implement Python 3.x dictionary like 'values' iterator method that
        returns a view on the values in the data store.
        The `viewvalues` equals `itervalues` and implements the Python 2.7
        equivalent.

        If the storage instance does not support view based iterations then
        `itervalues` should default to the `values` method

        :return: data values
        :rtype:  values view instance
        """

        return

    def __and__(self, other):
        """
        Implement class __and__

        Implements the bitwise 'and' (or &) which
        equals the intersection between the keys
        of this _store and the other _store.
        """

        return self.intersection(other)

    def __call__(self, data=False, default=None):
        """
        Implement class __call__

        Returns a Python dictionary representation of the full data store or
        the view on it by calling the `to_dict` method.

        If `data` is not None a `DataView` object is returned that allows
        iterating over node/edge data attributes in a way similar to the
        NodeDataView and EdgeDataView classes in NetworkX. In fact, this
        feature is added to provide compatibility with NetworkX.

        :param data:    return a DataView of the storage instance. The full
                        attribute store is considered by default. If 'data'
                        is an attribute dictionary key then only that key/value
                        pair is considered in the DataView
        :param default: default value returned by the DataView when the
                        target parameter (data) is not defined.

        :rtype:         :py:dict
        """

        if data is not False:
            return DataView(self, data, default)

        return self.to_dict()

    def __ge__(self, other):
        """
        Implement class __ge__

        Implements the class greater or equal to (>=) operator calling
        issuperset.

        :rtype: :py:bool
        """

        return self.issuperset(other, propper=False)

    def __gt__(self, other):
        """
        Implement class __gt__

        Implements the class greater then (>) operator calling issuperset.

        :rtype: :py:bool
        """

        return self.issuperset(other)

    # Mappings are not hashable by default, but subclasses can change this
    __hash__ = None

    def __le__(self, other):
        """
        Implement class __le__

        Implements the class less then or equal to (<=) operator calling
        issubset

        :rtype: :py:bool
        """

        return self.issubset(other, propper=False)

    def __lt__(self, other):
        """
        Implement class __ge__

        Implements the class less then (<) operator calling issubset.

        :rtype: :py:bool
        """

        return self.issubset(other)

    def __or__(self, other):
        """
        Implement class __or__

        Implements the bitwise 'or' (or |) which equals the union between the
        keys of this _store and the other _store.
        """

        return self.union(other)

    def __getattr__(self, key):
        """
        Implement class __getattr__

        Expose data by key as class attributes.
        Uses the class `get` method to return the value. If the key is not
        present, pass along to the default __getattribute__ method

        :param key: attribute name

        :return:    attribute value
        """

        if key in self:
            return self[key]

        return object.__getattribute__(self, key)

    def __repr__(self):
        """
        Implement class __repr__

        Returns a string representation of the object meta-data
        """

        return '<{0} object {1}: {2} items>'.format(self.__class__.__name__, id(self), len(self))

    def __setattr__(self, key, value):
        """
        Implement class __setattr__

        Set data and class attributes. If the attribute is not yet defined in
        either of these cases it is considered a standard class attribute.
        Use the `set` method to define new data key, value pairs.

        __setattr__ is resolved in the following order:

        1 self.__dict__ setter at class initiation
        2 graph setter handled by property methods
        3 `set` method for existing nodes/edges dictionary attributes.
        3 self.__dict__ only for existing and new class attributes

        :param key:  attribute name.
        :param value: attribute value
        """

        propobj = getattr(self.__class__, key, None)

        if '_initialised' not in self.__dict__:
            return dict.__setattr__(self, key, value)
        elif isinstance(propobj, property) and propobj.fset:
            propobj.fset(value)
        elif key in self:
            self.__setitem__(key, value)
        else:
            self.__dict__[key] = value

    def __str__(self):
        """
        Returns a sorted string representation of the dictionary keys.

        :rtype: :py:str
        """

        return str(sorted(self.keys(), key=str))

    def __xor__(self, other):
        """
        Implement class __and__

        Implements the bitwise 'xor' (or ^) which equals the
        symmetric_difference between the keys of this data store and the other
        data store.
        """

        return self.symmetric_difference(other)

    @classmethod
    def _get_class_object(cls):
        """
        Returns the current class object.
        Used by the copy method to return a copy of _storage wrapped in the
        current driver class.
        """

        return cls

    @property
    def is_view(self):
        """
        Does the current DictStorage represent a selective view on the
        parent dictionary?

        :rtype: bool
        """

        return self._view is not None

    def copy(self):
        """
        Return a deep copy of the storage class with the same view as
        the parent instance.

        :return:    deep copy of storage instance
        :rtype:     DictStorage
        """

        deepcopy = self._get_class_object()(copy.deepcopy(self._storage))
        if self.is_view:
            deepcopy.set_view(self._view)

        return deepcopy

    def difference(self, other):
        """
        Return the difference between the key set of self and other

        :rtype: :py:class:set
        """

        return set(self.keys()).difference(set(other))

    def fromkeys(self, keys, value=None):
        """
        Return a shallow copy of the dictionary for selected keys.

        If the DictStorage instance represent a selective view of the main
        dictionary, only those keys will be considered.

        :param keys:  keys to return dictionary copy for
        :param value: Default value keys
        """

        return self._get_class_object()([(k, value) for k in keys if k in self])

    def intersection(self, other):
        """
        Return the intersection between the key set of self and other

        :param other:   object to compare to
        :type other:    :py:dict

        :rtype:         :py:class:set
        """

        return set(self.keys()).intersection(set(other))

    def isdisjoint(self, other):
        """
        Returns a Boolean stating whether the key set in self overlap with the
        specified key set or iterable of other.

        :param other:   object to compare to
        :type other:    :py:dict

        :rtype:         :py:bool
        """

        return len(self.intersection(other)) == 0

    def issubset(self, other, propper=True):
        """
        Keys in self are also in other but other contains more keys
        (propper = True)

        :param other:   object to compare to
        :type other:    :py:dict
        :param propper: ensure that both key lists are not the same.
        :type propper:  :py:bool

        :rtype:         :py:bool
        """

        self_keys = set(self.keys())
        other_keys = set(other)
        if propper:
            return self_keys.issubset(other_keys) and self_keys != other_keys
        else:
            return self_keys.issubset(other_keys)

    def issuperset(self, other, propper=True):
        """
        Keys in self are also in other but self contains more keys
        (propper = True)

        :param other:   object to compare to
        :type other:    :py:dict
        :param propper: ensure that both key lists are not the same.
        :type propper:  :py:bool

        :rtype:         :py:bool
        """

        self_keys = set(self.keys())
        other_keys = set(other)
        if propper:
            return self_keys.issuperset(other_keys) and self_keys != other_keys
        else:
            return self_keys.issuperset(other_keys)

    def remove(self, key):
        """
        Implements list-like key removal

        :param key: key to remove
        """

        del self[key]

    def reset_view(self):
        """
        Reset the selective view on the DataFrame
        """

        self._view = None

    def query(self, match_func):
        """
        Storage query method

        Use Python lambda functions to query the storage based on primary
        storage keys (node ID/egde ID) and values (attribute dictionary).
        Other function are allowed as well as long as they match the
        function signature described below.

        The used lambda function may except two arguments in the following
        order: the primary key first and the attribute dictionary (value)
        as seconds argument.

        Example:    lambda k,v: v['weight'] > 2 and k == 13

        :param match_func:  lambda query function
        :type match_func:   :py:lambda

        :return:            list of primary storage identifiers (keys) matching
                            the lambda query
        :rtype:             :py:list
        """

        if not callable(match_func):
            raise TypeError('"match_func" argument is not a function (got {0})'.format(match_func))

        results = []
        for k in self:
            try:
                match = match_func(k, self[k])
                if match:
                    results.append(k)
            except Exception as e:
                logging.warn('Error in lambda query function: {0}'.format(e))

        return results

    def set(self, key, value):
        """
        Implement dictionary setter

        ..  note::  Do not use this method directly to add new nodes or edges
            to the graph. Use the graph add_node or add_edge methods for this
            purpose instead.

        :param key:   dictionary key to add or update
        :param value: key value
        """

        self.__setitem__(key, value)

    def set_view(self, keys):
        """
        Register keys to represent a selective view on the dictionary

        :param keys: keys to set
        :type keys:  list or tuple
        """

        keys = [to_unicode(key) for key in keys if key in self]
        self._view = keys

    def symmetric_difference(self, other):
        """
        Return the symmetric difference between the key set of self and other

        :rtype: :py:class:set
        """

        return set(self.keys()).symmetric_difference(set(other))

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

        view_copy = None
        if self.is_view and return_full:
            view_copy = copy.deepcopy(self._view)
            self.reset_view()

        return_dict = dict(self.items())

        if view_copy:
            self.set_view(view_copy)

        return return_dict

    def union(self, other):
        """
        Return the union between the key set of self and other

        :rtype: :py:class:set
        """

        return set(self.keys()).union(set(other))

    def viewitems(self):
        """
        Implement Python 2.7 dictionary like 'items' iterator method that
        returns a view on the items in the data store.
        It redirects the call to the `iteritems` method which is the Python
        3.x equivalent and abstract method.

        :return: data items as tuple of key/value pairs
        :rtype:  items view instance
        """

        return self.iteritems()

    def viewkeys(self):
        """
        Implement Python 2.7 dictionary like 'keys' iterator method that
        returns a view on the values in the data store.
        It redirects the call to the `iterkeys` method which is the Python
        3.x equivalent and abstract method.

        :return: data keys
        :rtype:  keys view instance
        """

        return self.iterkeys()

    def viewvalues(self):
        """
        Implement Python 2.7 dictionary like 'values' iterator method that
        returns a view on the values in the data store.
        It redirects the call to the `itervalues` method which is the Python
        3.x equivalent and abstract method.

        :return: data values
        :rtype:  values view instance
        """

        return self.itervalues()
