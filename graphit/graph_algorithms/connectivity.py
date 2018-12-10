# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: connectivity.py

"""
Functions for calculating node connectivity.
"""

import logging

from graphit import __module__
from graphit.graph_algorithms.shortest_path import dijkstra_shortest_path

logger = logging.getLogger(__module__)

__all__ = ['adjacency', 'is_reachable', 'nodes_are_interconnected']


def adjacency(graph, directed=False, reverse=False, stochastic=False, heuristic=None):
    """
    An edge weight map indexed by node id's.

    A dictionary indexed by node id1's in which each value is a
    dictionary of connected node id2's linking to the edge weight.
    If directed, edges go from id1 to id2, but not the other way.
    If stochastic, all the weights for the neighbors of a given node sum to 1.
    A heuristic can be a function that takes two node id's and returns
    an additional cost for movement between the two nodes.
    """

    v = {}
    for n in graph.nodes:
        v[n] = {}

    for e in graph.edges:
        id1, id2 = e
        if reverse:
            id1, id2 = reversed(e)

        v[id1][id2] = 1.0 - graph.edges[e].get('weight', 1.0) * 0.5

        if heuristic:
            v[id1][id2] += heuristic(id1, id2)

        if not directed:
            v[id2][id1] = v[id1][id2]

    if stochastic:
        for id1 in v:
            d = sum(v[id1].values())
            for id2 in v[id1]:
                v[id1][id2] /= d

    return v


def is_reachable(graph, root, destination):
    """
    Returns True if given node can be reached over traversable edges.

    :param graph:       Graph to query
    :type graph:        :graphit:Graph
    :param root:        source node ID
    :type root:         :py:int
    :param destination: destintion node ID
    :type destination:  :py:int

    :rtype:             :py:bool
    """

    if root in graph.nodes and destination in graph.nodes:
        connected_path = dijkstra_shortest_path(graph, root, destination)
        return destination in connected_path
    else:
        logger.error('Root or destination nodes not in graph')


def nodes_are_interconnected(graph, nodes):
    """
    Are all the provided nodes directly connected with one another

    :param graph: Graph to query
    :type graph:  :graphit:Graph
    :param nodes: nodes to test connectivity for
    :type nodes:  :py:list

    :rtype:       :py:bool
    """

    nodes = [node.nid if hasattr(node, 'nid') else node for node in nodes]

    nid_list = []
    for node in nodes:
        if node in graph.nodes:
            nid_list.append(node)
        else:
            raise 'Node not in graph {0}'.format(node)

    nid_list = set(nid_list)

    collection = []
    for nid in nid_list:
        query = set(graph.adjacency[nid] + [nid])
        collection.append(query.intersection(nid_list) == nid_list)

    return all(collection)
