# -*- coding: utf-8 -*-

import logging

from graphit import __module__

logger = logging.getLogger(__module__)


def node_neighbors(graph, nid):
    """
    Return de neighbor nodes of the node.
    
    This method is not hierarchical and thus the root node has no effect.
    
    Directed graphs and/or masked behaviour: masked nodes or directed
    nodes not having an edge from source to node will not be returned.
    
    :param graph: Graph to query
    :type graph:  Graph class instance
    :param nid:   node ID to return neighbors for
    :type nid:    :py:int
    """
    
    if nid is None:
        return []
    
    if graph.masked:
        nodes = set(graph.nodes.keys())
        adjacency = set(graph.adjacency[nid])
    else:
        nodes = set(graph.origin.nodes.keys())
        adjacency = set(graph.origin.adjacency[nid])
    
    return sorted(nodes.intersection(adjacency))


def degree(graph, nodes=None, weight=None):
    """
    Return the degree of nodes in the graph
    
    The degree (or valency) of a graph node are the number of edges
    connected to the node, with loops counted twice.
    The method supports weighted degrees in which the connected
    nodes are multiplied by a weight factor stored as attribute in
    the edges.
    
    :param graph:  Graph to return the degree of nodes for
    :type graph:   Graph class instance
    :param nodes:  nodes to return the degree for, None uses all
                   nodes in the graph.
    :type nodes:   list
    :param weight: Weight factor attribute in the edges
    :type weight:  string
    :return:       degree of each node
    :rtype:        list of tuples (node, degree)
    """
    
    if nodes is None:
        nodes = graph.nodes
    else:
        not_in_graph = [nid for nid in nodes if nid not in graph.nodes]
        if not_in_graph:
            logger.error('Nodes {0} not in graph'.format(not_in_graph))
    
    results = {}
    if weight:
        for node in nodes:
            results[node] = sum([graph.edges[(node, n)].get(weight, 1) for n in graph.adjacency[node]])
            if node in graph.adjacency[node]:
                results[node] += graph.edges[(node, node)].get(weight, 1)
    else:
        for node in nodes:
            results[node] = len(graph.adjacency[node])
            if node in graph.adjacency[node]:
                results[node] += 1
    
    return results


def size(graph, weight=None, is_directed=None):
    """
    The graph `size` equals the total number of edges it contains
    
    :param graph:   graph to calculate size for
    :type graph:    :graphit:Graph
    :param weight:  edge attribute name containing a weight value
    :type weight:   :py:str
    
    :return:        graph size
    :rtype:         :py:int, :py:float
    """
    
    if is_directed is None:
        is_directed = graph.is_directed()
    
    graph_degree = degree(graph, weight=weight)
    graph_size = sum(graph_degree.values())
    
    if is_directed:
        return graph_size
    
    return graph_size // 2 if weight is None else graph_size / 2
