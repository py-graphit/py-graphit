# -*- coding: utf-8 -*-

"""
file: graph_storage_views.py

Contains classes that provide various types of 'views' on the data in the
main node and edge storage.

These classes use the common storage driver API for nodes and edges and
therefor they should work for every storage driver. A driver can implement
it's own version of a view for performance purposes for instance.
"""

from graphit.graph_py2to3 import colabc
from graphit.graph_exceptions import GraphitNodeNotFound

__all__ = ['AdjacencyView', 'DataView']


class AdjacencyView(object):
    """
    Adjacency View class

    Makes class adjacency information available through a dict-like API.
    Adjacency is based on the graphs nodes and edges. When the latter two
    are 'views' then AdjacencyView als behaves as a view.
    """

    def __init__(self, nodes, edges):
        """
        Implements class __init__

        :param nodes: Graph nodes storage instance
        :param edges: Graph edges storage instance
        """

        self.edges = edges
        self.nodes = nodes

    def __call__(self):
        """
        Implements class __call__

        :return:  Returns adjacency of the full graph or 'view' thereof
        :rtype:  :py:dict
        """

        return self._build_adjacency(self.nodes)

    def __contains__(self, node):
        """
        Implements class __contains__

        Test if node is in adjacency. This equals the membership test for nodes.

        :param node: node to check membership for
        :rtype:      :py:bool
        """

        return node in self.nodes

    def __getitem__(self, node):
        """
        Implements class __getitem__

        :param node: Node ID to return adjacency for
        :type node:  :py:int or :py:str

        :return:     Returns the adjacency for a given node
        :rtype:      :py:list
        """

        adj = self._build_adjacency([node])
        return adj[node]

    def __iter__(self):
        """
        Implements class __iter__

        :return: Iterator over node/adjacency pairs
        """

        return iter(self.items())

    def __len__(self):
        """
        Implements class __len__

        :return: Number of nodes in adjacency. Equals number of nodes in graph.
        :rtype:  :py:int
        """

        return len(self.nodes)

    def _build_adjacency(self, nodes):
        """
        Build the adjacency dictionary for each call to the AdjacencyView
        instance for all nodes or a selection.

        :param nodes:   Nodes to determine adjacency for
        :type nodes:    :py:list

        :return:        adjacency
        :rtype:         :py:dict
        """

        adj = {}
        for node in nodes:
            if node in self.nodes:
                adj[node] = []
            else:
                raise GraphitNodeNotFound(node)

        for edge in self.edges:
            if edge[0] in adj:
                adj[edge[0]].append(edge[1])

        return adj

    @property
    def is_view(self):

        return True

    def degree(self, nodes=None, method='degree', weight=None):
        """
        Return the degree of nodes in the graph

        Reports a dictionary with for every node in the graph the number of
        connected edges of type:

        * indegree: edges from others to self
        * outdegree: edges from self to others
        * degree: indegree and outdegree combined

        Edges connected to self are counted twice when using 'degree' as method

        :param nodes:   Nodes to return degree for
        :type nodes:    :py:list
        :param method:  degree type as 'indegree', 'outdegree' or both 'degree'
        :type method:   :py:str
        :param weight:  Name of edge weight attribute. If None, then each edge
                        has weight 1. The degree is the sum of the edge weights
                        adjacent to the node.
        :type weight:   :py:str

        :return:        Degree
        :rtype:         :py:dict
        """

        adj = self._build_adjacency(nodes or self.nodes)

        degree = dict.fromkeys(adj, 0)
        if weight is None:
            for node in adj:

                # outdegree
                if method in ('degree', 'outdegree'):
                    degree[node] += len(adj[node])

                # indegree including self loops
                if method in ('degree', 'indegree'):
                    degree[node] += sum([1 if node in adj[n] else 0 for n in adj])
        else:
            for node in adj:

                # outdegree
                if method in ('degree', 'outdegree'):
                    degree[node] += sum([self.edges[(node, n)].get(weight, 1) for n in adj[node]])

                # indegree including self loops
                if method in ('degree', 'indegree'):
                    degree[node] += sum([self.edges[(n, node)].get(weight, 1) if node in adj[n] else 0 for n in adj])

        return degree

    def get(self, node, default=None):
        """
        Implements dict-like `get` method

        :param node:    Node to get adjacency for
        :param default: Default return value if node not in adjacency dict

        :return:        adjacency
        :rtype:         :py:list
        """

        if node not in self.nodes:
            return default
        return self.__getitem__(node)

    def items(self):
        """
        Implements dict-like `items` method

        :return:  Adjacency dict items tuples
        :rtype:   :py:list
        """

        return self._build_adjacency(self.nodes).items()

    def keys(self):
        """
        Implements dict-like `keys` method

        :return:  Adjacency dict keys
        :rtype:   :py:list
        """

        return self._build_adjacency(self.nodes).keys()

    def predecessors(self, node):
        """
        Return a list for all predecessors nodes of 'node'.

        These are all nodes for which there exist an edge from other
        nodes to self (node).

        :return:  predecessors nodes
        :rtype:   :py:list
        """

        if node in self.nodes:
            return [edge[0] for edge in self.edges if edge[1] == node]

        raise GraphitNodeNotFound(node)

    def successors(self, node):
        """
        Return a list for all successor nodes of 'node'.

        These are all nodes for which there exist and edge from 'node'
        to other. This is the same as the neighbours of 'node' or self[node].

        :return:  successor nodes
        :rtype:   :py:list
        """

        return self._build_adjacency([node])[node]

    def values(self):
        """
        Implements dict-like `values` method

        :return:  Adjacency dict values
        :rtype:   :py:list
        """

        return self._build_adjacency(self.nodes).values()


class DataView(colabc.Set):
    """
    A read-only DataView class on node/edge data

    This class allows iteration over the data store primary keys (nodes
    or edges) and data attributes in a read-only fashion.
    The full data dictionary is considered by default. If the 'data'
    attribute is defined to something other then a boolean that parameter
    will be used as lookup key for the data dictionary only returning the
    corresponding value or 'default' if not found.

    This class is available to provide compatibility with the NodeDataView
    and EdgeDataView classes from the NetworkX library.
    The same functionality can be achieved using the 'iteritems' or
    'itervalues' methods of the default storage driver class that provide
    iterators over the attribute data in the node/edge data store.
    """

    __slots__ = ('_storage', '_data', '_default')

    def __init__(self, storage, data, default=None):
        """
        Implement class __init__

        :param storage: node or edge storage instance
        :param data:    data to return
        :param default: default value to return
        """

        self._storage = storage
        self._data = data
        self._default = default

    def __len__(self):
        """
        Implement class __len__

        Returns the number of items in the _storage or the selective view on it.
        """

        return len(self._storage)

    def __contains__(self, item):
        """
        Implement class __contains__

        Validate if the data store contains the tuple (node/edge ID, dict) or
        (node/edge ID, data value).
        """

        if not isinstance(item, tuple):
            raise TypeError('Tuple required of type (node/edge ID, attribute data)')

        try:
            return self[item[0]] == item[1]
        except (TypeError, ValueError):
            return False

    def __getitem__(self, item):
        """
        Implement class __getitem__

        Return attribute data dict or specific value based on node/edge ID
        Will return default value if specific key lookup failed.

        :param item:    node/edge primary key

        :return:        data dictionary or attribute value
        """

        value = self._storage[item]
        if self._data is True:
            return value
        return value.get(self._data, self._default)

    def __iter__(self):
        """
        Implement class __iter__

        Iterator returning tuples of (node/edge ID, dict) or
        (node/edge ID, data value).

        :return: iterator
        """

        if self._data is True:
            return iter(self._storage.iteritems())

        if self._data is not True:
            return ((key, value.get(self._data, self._default)) for key, value in self._storage.iteritems())

    def __str__(self):
        """
        Implement class __str__
        """

        return str(list(self))

    def __repr__(self):
        """
        Implement class __get__
        """

        if self._data is True:
            return '{0}({1})'.format(self.__class__.__name__, dict(self))

        return '{0}({1}, data={2})'.format(self.__class__.__name__, dict(self), self._data)

    def get(self, item, default=None):
        """
        Implement dict-like 'get' method

        Return node/edge attribute dictionary or specific value (_data).
        If _data key was not found return default value.

        :param item:    node/edge primary key
        :param default: default value to return

        :return:        data dictionary or attribute value
        """

        data = self[item]

        if not isinstance(data, dict):
            if data == self._default and default != self._default:
                return default

        return data
