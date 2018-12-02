# -*- coding: utf-8 -*-

"""
file: graph_storage_views.py

Contains classes that provide various types of 'views' on the data in the
main node and edge storage.

These classes use the common storage driver API for nodes and edges and
therefor they should work for every storage driver. A driver can implement
it's own version of a view for performance purposes for instance.
"""

__all__ = ['AdjacencyView']


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

        adj = dict([(node, []) for node in nodes])
        for edge in self.edges:
            if edge[0] in adj:
                adj[edge[0]].append(edge[1])

        return adj

    @property
    def is_view(self):

        return True

    def degree(self, nodes):
        """
        Return the degree of nodes in the graph

        The degree (or valency) of a graph node are the number of edges
        connected to the node, with loops counted twice.
        For weighted degree pleae use the dedicated
        'graphit.graph_algorithms.degree' function.

        :param nodes: Nodes to return degree for
        :type nodes:  :py:list

        :return:      Degree
        :rtype:       :py:dict
        """

        adj = self._build_adjacency(nodes)

        degree = {}
        for node in adj:
            degree[node] = len(adj[node])
            if node in adj[node]:
                degree[node] += 1

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

    def values(self):
        """
        Implements dict-like `values` method

        :return:  Adjacency dict values
        :rtype:   :py:list
        """

        return self._build_adjacency(self.nodes).values()

    def keys(self):
        """
        Implements dict-like `keys` method

        :return:  Adjacency dict keys
        :rtype:   :py:list
        """

        return self._build_adjacency(self.nodes).keys()

    def items(self):
        """
        Implements dict-like `items` method

        :return:  Adjacency dict items tuples
        :rtype:   :py:list
        """

        return self._build_adjacency(self.nodes).items()
