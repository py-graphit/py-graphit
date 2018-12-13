# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: centrality.py

"""
Functions for calculating node centrality measures in a graph
"""

import logging
import heapq

from math import sqrt
from itertools import count

from graphit import __module__
from graphit.graph_exceptions import GraphitAlgorithmError

logger = logging.getLogger(__module__)

__all__ = ['brandes_betweenness_centrality', 'eigenvector_centrality']


def brandes_betweenness_centrality(graph, nodes=None, normalized=True, weight=None, endpoints=False):
    """
    Brandes algorithm for betweenness centrality.

    Betweenness centrality is an indicator of a node's centrality in a network.
    It is equal to the number of shortest paths from all vertices to all others
    that pass through that node. A node with high betweenness centrality has a
    large influence on the transfer of items through the network, under the
    assumption that item transfer follows the shortest paths.

    Original publication:
    Brandes, Ulrik. "A faster algorithm for betweenness centrality*."
    Journal of mathematical sociology 25.2 (2001): 163-177.

    :param graph:      Graph to calculate Brandes betweenness centrality
    :type graph:       :graphit:Graph
    :param nodes:      nodes to calculate centrality for. Defaults to all nodes
    :type nodes:       :py:list
    :param normalized: normalize betweenness centrality measure between 0 and 1
    :type normalized:  bool
    :param endpoints:  include the endpoints in the shortest path counts
    :type endpoints:   :py:bool
    :param weight:     edge attribute to use as edge weight
    :type weight:      string

    :rtype:            :py:dict
    """

    betweenness = dict.fromkeys(graph.nodes, 0.0)

    nodes = nodes or graph.nodes
    for node in nodes:
        path = []
        path_node_count = {}
        p = dict([(n, []) for n in graph.nodes])
        sigma = dict.fromkeys(graph.nodes, 0.0)
        sigma[node] = 1.0

        # Weight is None, use breath-first-search
        if weight is None:
            path_node_count[node] = 0
            queue = [node]
            while queue:
                next_node = queue.pop(0)
                path.append(next_node)
                dv = path_node_count[next_node]
                for w in graph.adjacency[next_node]:
                    if w not in path_node_count:
                        queue.append(w)
                        path_node_count[w] = dv + 1
                    if path_node_count[w] == dv + 1:
                        sigma[w] += sigma[next_node]
                        p[w].append(next_node)

        # If weight, use Dijkstra shortest path
        else:
            adj = graph.adjacency()
            seen = {node: 0}
            c = count()
            queue = []
            heapq.heappush(queue, (0, next(c), node, node))
            while queue:
                (dist, _, pred, v) = heapq.heappop(queue)
                if v in path_node_count:
                    continue  # already searched this node.
                sigma[v] += sigma[pred]  # count paths
                path.append(v)
                path_node_count[v] = dist
                for w in adj[v]:
                    vw_dist = dist + graph.edges[(v, w)].get(weight, 1)
                    if w not in path_node_count and (w not in seen or vw_dist < seen[w]):
                        seen[w] = vw_dist
                        heapq.heappush(queue, (vw_dist, next(c), v, w))
                        sigma[w] = 0.0
                        p[w] = [v]
                    elif vw_dist == seen[w]:  # handle equal paths
                        sigma[w] += sigma[v]
                        p[w].append(v)

        # accumulation
        delta = dict.fromkeys(path, 0)
        correction = 1 if endpoints else 0
        if endpoints:
            betweenness[node] += len(path) - correction
        while path:
            w = path.pop()
            coeff = (1 + delta[w]) / sigma[w]
            for v in p[w]:
                delta[v] += sigma[v] * coeff
            if w != node:
                betweenness[w] += delta[w] + correction

    # Rescale betweenness values
    nr_nodes = float(len(graph))
    scale = None
    if normalized:
        if endpoints:
            if nr_nodes >= 2:
                scale = 1 / (nr_nodes * (nr_nodes - 1))
        elif nr_nodes > 2:
            scale = 1 / ((nr_nodes - 1) * (nr_nodes - 2))
    else:
        scale = None if graph.directed else 0.5

    if scale is not None:
        for v in betweenness:
            betweenness[v] *= scale

    return betweenness


def eigenvector_centrality(graph, max_iter=100, tolerance=1.0e-6, weight=None, start_value=None):
    """
    Eigenvector centrality for nodes in the graph (like Google's PageRank).

    Eigenvector centrality is a measure of the importance of a node in a directed network.
    It rewards nodes with a high potential of (indirectly) connecting to high-scoring nodes.
    Nodes with no incoming connections have a score of zero.
    If you want to measure outgoing connections, reversed should be False.

    The eigenvector calculation is done by the power iteration method.
    It has no guarantee of convergence.
    A starting vector for the power iteration can be given in the start dict.

    You can adjust the importance of a node with the rating dictionary,
    which links node id's to a score.

    The algorithm is adapted from NetworkX, Aric Hagberg (hagberg@lanl.gov):
    https://networkx.lanl.gov/attachment/ticket/119/eigenvector_centrality.py

    :param graph:       Graph to calculate eigenvector centrality for
    :type graph:        :graphit:Graph
    :param max_iter:    maximum number of iterations to reach convergance
    :type max_iter:     :py:int
    :param weight:      edge attribute to use as weight. 1 if not defined
    :type weight:       string
    :param tolerance:   iteration convergence criterion
    :type tolerance:    :py:float
    :param start_value: starting value of eigenvector iteration for each node
    :type start_value:  :py:dict

    :return:            eigenvector centrality for each node in the graph
    :rtype:             :py:dict
    """

    if len(graph) == 0:
        raise GraphitAlgorithmError('Cannot compute centrality for graph without nodes')

    # If no initial vector is provided, start with the all-ones vector.
    if isinstance(start_value, dict):
        if all(v == 0 for v in start_value.values()):
            raise GraphitAlgorithmError('initial vector cannot have all zero values')
    else:
        start_value = {v: 1.0 for v in graph.nodes}

    # Normalize initial vector, ensure floats
    start_values_sum = sum(start_value.values())
    vector = {node: float(eigen_value) / start_values_sum for node, eigen_value in start_value.items()}

    nnodes = len(graph.nodes)
    for i in range(max_iter):
        previous_vector = vector
        vector = previous_vector.copy()

        # Perform y^T = x^T A (left eigenvector)
        for n1 in vector:
            for n2 in graph.adjacency[n1]:
                vector[n2] += previous_vector[n1] * graph.edges[(n1, n2)].get(weight, 1)

        # Normalize the vector. Should not be zero according to Perron-Frobenius
        # theorem. Assumed to be one in case of numerical error.
        norm = sqrt(sum(z ** 2 for z in vector.values())) or 1
        vector = {node: eigen_value / norm for node, eigen_value in vector.items()}

        # Check for convergence (in the L_1 norm).
        if sum(abs(vector[n] - previous_vector[n]) for n in vector) < nnodes * tolerance:
            return vector

    raise GraphitAlgorithmError('Unable to convergen in {0} iterations'.format(max_iter))
