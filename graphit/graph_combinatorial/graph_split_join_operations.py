# -*- coding: utf-8 -*-

"""
file: graph_split_join_operations.py

Functions to split or combine graphs.
"""

import logging

from graphit import __module__, check_graphbase_instance
from graphit.graph_exceptions import GraphitException

__all__ = ['graph_join']
logger = logging.getLogger(__module__)


def graph_join(graph1, graph2, links=None):
    """
    Add graph2 as subgraph to graph1

    All nodes and edges of graph 2 are added to graph 1. Final links between
    nodes in graph 1 and newly added nodes of graph 2 are defined by the edges
    in the `links` list.

    :param graph1: graph to add to
    :type graph1:  GraphAxis
    :param graph2: graph added
    :type graph2:  GraphAxis
    :param links:  links between nodes in graph1 and graph2
    :type links:   :py:list

    :return:       node mapping
    :rtype:        :py:dict
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    # Check if graph 1 link nodes exist
    if links:
        for link in links:
            if not link[0] in graph1.nodes:
                raise GraphitException('Link node {0} not in graph1'.format(link[0]))
            if not link[1] in graph2.nodes:
                raise GraphitException('Link node {0} not in graph1'.format(link[1]))

    # Add all nodes and attributes of graph 2 to 1 and register node mapping
    mapping = {}
    for nid, attr in graph2.nodes.items():
        newnid = graph1.add_node(node=nid, **attr)
        mapping[nid] = newnid

    # Transfer edges and attributes from graph 2 to graph 1 and map node IDs
    for eid, attr in graph2.edges.items():
        if eid[0] in mapping and eid[1] in mapping:
            graph1.add_edge(mapping[eid[0]], mapping[eid[1]], directed=True, **attr)

    # Link graph 2 nodes to graph 1
    attach_nids = []
    if links:
        for link in links:
            graph1.add_edge(link[0], mapping[link[1]], directed=graph1.directed)
            attach_nids.append(mapping[link[1]])

    return mapping
