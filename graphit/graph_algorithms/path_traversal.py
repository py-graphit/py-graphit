# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: path_traversal.py

"""
Functions for traversing graph nodes and edges in depth-first-search
and breath-first-search order.
"""

import logging

from graphit import __module__
from graphit.graph_algorithms import node_neighbors

logger = logging.getLogger(__module__)

__all__ = ['dfs_paths', 'dfs_nodes', 'dfs_edges']


def dfs_nodes(graph, start, method='dfs', max_depth=None):
    """
    Node implementation of depth-first-search and breath-first-search

    :param graph:     graph to search
    :type graph:      graph class instance
    :param start:     root node to start the search from
    :type start:      node ID or Node object
    :param method:    search method. Depth-first search (dfs, default)
                      and Breath-first search (bfs) supported.
    :type method:     :py:str
    :param max_depth: maximum search depth
    :type max_depth:  :py:int, default equals number of nodes in graph

    :return:	      A generator of nodes in dfs or bfs mode.
    :rtype:           :py:generator
    """

    edges_path = dfs_edges(graph, start, method=method, max_depth=max_depth)

    yield start
    for edge in edges_path:
        yield edge[1]


def dfs_edges(graph, start,  method='dfs', max_depth=None, edge_based=False):
    """
    Edge implementation of depth-first-search and breath-first-search

    This function uses dfs or bfs to traverse the nodes of the graph reporting
    the connected edges. A list of visited nodes is used to guide graph
    traversal but this does not guaranty that all edges will be visited.
    Use the `edge_based` argument to switch to a true edge based graph
    traversal.

    :param graph:       graph to search
    :type graph:        graph class instance
    :param start:       root node to start the search from
    :type start:        node ID or Node object
    :param method:      search method. Depth-first search (dfs, default)
                        and Breath-first search (bfs) supported.
    :type method:       :py:str
    :param max_depth:   maximum search depth
    :type max_depth:    :py:int, default equals number of nodes in graph
    :param edge_based:  traverse over edges instead of nodes
    :type edge_based:   :py:bool

    :return:	        A generator of edges in dfs or bfs mode.
    :rtype:             :py:generator
    """

    # Get node object from node ID
    start = graph.getnodes(start)

    # Define the search method
    stack_pop = -1
    if method == 'bfs':
        stack_pop = 0

    # Set the depth limit
    if max_depth is None:
        max_depth = len(graph.nodes)

    visited = {start.nid}
    adjacency = graph.adjacency()
    stack = [(start.nid, max_depth, iter(sorted(adjacency[start.nid])))]
    while stack:
        parent, depth_now, children = stack[stack_pop]
        try:
            child = next(children)

            # Use true edge or node DFS method
            if edge_based:
                visited_object = (parent, child)
            else:
                visited_object = child

            if visited_object not in visited:
                yield parent, child
                visited.add(visited_object)
                if depth_now > 1:
                    stack.append((child, depth_now - 1, iter(sorted(adjacency[child]))))
        except StopIteration:
            stack.pop(stack_pop)


def dfs_paths(graph, start, goal, method='dfs', cutoff=None):
    """
    Return all possible paths between two nodes.

    Setting method to 'bfs' returns the shortest path first

    :param graph:     graph to search
    :type graph:      graph class instance
    :param start:     root node to start the search from
    :type start:      :py:int
    :param goal:      target node
    :type goal:       :py:int
    :param method:    search method. Depth-first search (dfs, default)
                      and Breath-first search (bfs) supported.
    :type method:     :py:str
    :param cutoff:    only return paths with length up to cutoff
    :type cutoff:     :py:int

    :rtype:           generator object
    """

    # Define the search method
    stack_pop = -1
    if method == 'bfs':
        stack_pop = 0

    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop(stack_pop)
        neighbors = node_neighbors(graph, vertex)
        for next_node in set(neighbors) - set(path):
            if cutoff and len(path) > cutoff:
                break
            if next_node == goal:
                yield path + [next_node]
            else:
                stack.append((next_node, path + [next_node]))
