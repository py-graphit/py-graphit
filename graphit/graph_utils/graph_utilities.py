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

    In an undirectional edge the edge pair shares a single attribute
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

    # remove all $ref pointers between undirectional edge pairs
    for edge in graph_copy.edges:
        if graph_copy.edges.has_data_reference(edge):
            graph_copy.edges.del_data_reference(edge)

            # Update reverse edge with data from forwards edge
            reverse_edge = tuple(reversed(edge))
            if reverse_edge in graph_copy.edges:
                graph_copy.edges[reverse_edge].update(graph_copy.edges[edge])

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

    done = []
    for edge in graph.edges:
        reverse_edge = tuple(reversed(edge))
        values = copy.deepcopy(graph.edges[edge])

        if edge in done or reverse_edge in done:
            continue

        if reverse_edge in graph.edges:
            values.update(graph.edges[reverse_edge])
            done.append(reverse_edge)

        graph_copy.add_edge(*edge, **values)
        done.append(edge)

    return graph_copy


def edges_parent_to_subgraph(subgraph, parent=None):
    """
    Return edges connecting a subgraph with the parent graph

    'subgraph.origin' is used as parent graph by default to derive connections.
    This will no longer work in case a copy is made of the subgraph as it will
    reset the link to the parent.
    The `parent` argument can be used to specify a dedicated parent graph in
    these and all other cases where connected edges between two separate graphs
    that share the same node ID's needs to be determined.

    :param subgraph:   subgraph
    :type subgraph:    :graphit:Graph
    :param parent:     dedicated parent graph to derive connections to/from
    :type parent:      :graphit:Graph

    :return:           edges connecting graphs
    :rtype:            :py:list
    """

    if parent is None:
        parent = subgraph

    connected = []
    for nid in subgraph.nodes():
        node = parent.getnodes(nid)
        connected.extend(node.connected_edges())

    return list(set(connected).difference(subgraph.edges))
