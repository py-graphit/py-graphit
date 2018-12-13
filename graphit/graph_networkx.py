# -*- coding: utf-8 -*-

"""
file: graph_networkx.py

Provides a NetworkX compliant Graph class.
"""

from graphit.graph import GraphBase
from graphit.graph_exceptions import GraphitException, GraphitNodeNotFound
from graphit.graph_algorithms import degree, size
from graphit.graph_utils.graph_utilities import graph_undirectional_to_directional, graph_directional_to_undirectional


class NetworkXGraph(GraphBase):

    def __init__(self, *args, **kwargs):
        """
        Init a NetworkX graph type

        Differences with regular Graph:
        - 'auto_nid' is unknown in NetworkX, set to False

        :param args:    arguments to Graph __init__
        :param kwargs:  keyword arguments to Graph __init__
        """

        kwargs['auto_nid'] = False
        super(NetworkXGraph, self).__init__(*args, **kwargs)

    def __contains__(self, node):

        return self.has_node(node)

    def __getitem__(self, key):
        """
        Implement class __getitem__

        Return adjacency based on node ID or edge on edge ID.

        :return: adjacency nodes or an edge
        :rtype:  :py:list
        """

        # Return edge using edge ID
        if isinstance(key, tuple):
            return self.edges[key]

        # Return adjacency nodes
        # TODO: this should return a view but that is not fully compliant to NetworkX yet
        else:
            return dict([(nid, self.nodes[nid]) for nid in self.adjacency[key]])

    def __iter__(self):
        """
        Implement class __iter__

        Iterate over nodes IDs

        :return: Node identifier (nid)
        """

        # Always reset node view
        for nid in self.nodes:
            yield nid

    @property
    def adj(self):

        return self.adjacency

    def add_nodes_from(self, nodes, **kwargs):

        return self.add_nodes(nodes, **kwargs)

    def add_edges_from(self, edges, **kwargs):

        return self.add_edges(edges, **kwargs)

    def add_weighted_edges_from(self, edges, weight='weight', **kwargs):
        """
        Add edges with a numeric weight factor

        :param edges:   edges as iterable of tuples with length 3 containing
                        (node1, node2, weight value)
        :param weight:  edge weight attribute name
        :type weight:   :py:str
        :param kwargs:  additional keyword arguments passed to add_edge

        :return:        list of edge ids for the objects added in
                        the same order as th input iterable.
        :rtype:         :py:list
        """

        return self.add_edges(edges, weight=weight, **kwargs)

    @property
    def degree(self):

        return degree(self, self.nodes.keys())

    def get_edge_data(self, n1, n2, default=None):

        edge = (n1, n2)
        if edge not in self.edges:
            return default
        return self.edges[edge]

    def has_edge(self, n1, n2):

        return (n1, n2) in self.edges

    def has_node(self, node):

        return node in self.nodes

    def is_directed(self):
        """
        Return graph directionality

        A graph with mixed edges (partly directed, partly undirected) is
        considered a directed graph.

        :return: directed or undirected graph
        :rtype:  :py:bool
        """

        return self.directed

    def nbunch_iter(self, nodes=None):

        if nodes:
            nodes = [node for node in nodes if node in self.nodes]
        else:
            nodes = self.nodes.keys()

        return self.iternodes(nodes)

    def neighbors(self, node):

        if node not in self.nodes:
            raise GraphitNodeNotFound()
        return iter(self.adjacency[node])

    def number_of_edges(self, first=None, second=None):

        if first is None:
            return int(self.size())
        if second is not None and second in self.adjacency[first]:
            return 1
        return 0

    def order(self):
        """
        Return the number of nodes in the graph similar to __len__

        :return: Number of nodes
        :rtype:  :py:int
        """

        return len(self)

    number_of_nodes = order

    def remove_nodes_from(self, *args, **kwargs):

        return self.remove_nodes(*args, **kwargs)

    def remove_edges_from(self, *args, **kwargs):

        return self.remove_edges(*args, **kwargs)

    def size(self, weight=None):

        return size(self, weight=weight)

    def subgraph(self, nodes):

        return self.getnodes(nodes)

    def edge_subgraph(self, edges):

        return self.getedges(edges)

    def to_directed(self):

        return graph_undirectional_to_directional(self)

    def to_undirected(self):

        return graph_directional_to_undirectional(self)

    def update(self, edges=None, nodes=None):

        if edges is not None:
            if nodes is not None:
                self.add_nodes(nodes)
                self.add_edges(edges)
            else:
                if hasattr(edges, 'nodes') and hasattr(edges, 'edges'):
                    for node, attr in edges.nodes.items():
                        self.add_node(node, **attr)
                    for edge, attr in edges.edges.items():
                        self.add_edge(*edge, **attr)
                else:
                    self.add_edges(edges)
        elif nodes is not None:
            self.add_nodes(nodes)
        else:
            raise GraphitException("update needs nodes or edges input")
