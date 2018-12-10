# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: shortest_path.py

"""
Functions for calculating the shortest paths in a graph.
"""

import logging
import heapq

from graphit import __module__

logger = logging.getLogger(__module__)

__all__ = ['dijkstra_shortest_path']


def dijkstra_shortest_path(graph, start, goal=None, weight=None):
    """
    Dijkstra algorithm for finding shortest paths.

    In contrast to depth- or breath first search, Dijkstra's algorithm
    supports weighted graphs using a priority queue.
    The `weight` attribute defined the edge data attribute to use as
    weight which defaults to 1 if not defined or not found.

    If the target node is not specified, the path search will continue untill
    the leaf node(s) are reached.

    Original publication:
    Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs"
    Numerische Mathematik 1: 269–271. doi:10.1007/BF01386390.

    :param graph:     graph to search
    :type graph:      graph class instance
    :param start:     root node to start the search from
    :type start:      :py:int
    :param goal:      target node
    :type goal:       :py:int
    :param weight:    edge attribute to use as edge weight
    :type weight:     :py:str

    :rtype:           :py:list
    """

    adj = graph.adjacency()

    # Flatten linked list of form [0,[1,[2,[]]]]
    def flatten(linked_list):
        while len(linked_list) > 0:
            yield linked_list[0]
            linked_list = linked_list[1]

    queue = [(0, start, ())]
    visited_nodes = []
    path = None
    while len(queue):
        (cost1, node1, path) = heapq.heappop(queue)
        if node1 not in visited_nodes:
            visited_nodes.append(node1)
        if node1 == goal:
            return list(flatten(path))[::-1] + [node1]
        path = (node1, path)
        for node2 in adj[node1]:
            if node2 not in visited_nodes:
                cost2 = 1
                if weight is not None:
                    cost2 = graph.edges[(node1, node2)].get(weight, 1)
                heapq.heappush(queue, (cost1 + cost2, node2, path))

    # Without a goal node continue search up to leaf node
    if not goal and path:
        return list(flatten(path))[::-1]
    return []
