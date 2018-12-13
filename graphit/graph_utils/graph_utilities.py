# -*- coding: utf-8 -*-

import copy
import logging

from graphit import __module__

logger = logging.getLogger(__module__)


def graph_undirectional_to_directional(graph):
    """
    Convert a undirectional to a directional graph

    Returns a deep copy of the full graph with all undirectional edges
    duplicated as directional ones.

    In an undirectional edge the egde pair shares a single attribute
    dictionary. This dictionary gets duplicated to the unique directional
    edges.

    :param graph: Graph to convert
    :type graph:  :graphit:Graph

    :return:      Directional graph
    :rtype:       :graphit:Graph
    """

    if graph.directed:
        logging.info('Graph already configured as directed graph')

    graph_copy = graph.copy(deep=True)
    graph_copy.directed = True
    graph_copy.edges.clear()

    # copy directional edges in emptied edge store
    for edge, attr in graph.edges.items():
        graph_copy.add_edge(*edge, **attr)

    return graph_copy


def graph_directional_to_undirectional(graph):
    """
    Convert a directional to an undirectional graph

    Returns a deep copy of the full graph with all directional edges
    duplicated as undirectional ones.
    Undirectional edges share the same data dictionary. In converting
    directional to undirectional edges their data dictionaries will
    be merged.

    .. Note:: dictionary merging may result in undesirable results due
              to data overwrite.

    :param graph: Graph to convert
    :type graph:  :graphit:Graph

    :return:      Directional graph
    :rtype:       :graphit:Graph
    """

    if not graph.directed:
        logging.info('Graph already configured as undirected graph')

    graph_copy = graph.copy(deep=True)
    graph_copy.directed = False
    graph_copy.edges.clear()

    edges = list(graph.edges.keys())
    while len(edges):
        edge = edges.pop()
        attr = copy.deepcopy(graph.edges[edge])

        # Look for reverse edge. Update common attributes.
        reverse_edge = edge[::-1]
        if reverse_edge in edges:
            attr.update(graph.edges[reverse_edge])
            edges.remove(reverse_edge)

        # Add undirectional edge
        graph_copy.add_edge(*edge, **attr)

    return graph_copy
