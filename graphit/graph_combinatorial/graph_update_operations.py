# -*- coding: utf-8 -*-

"""
file: graph_update_operations.py

Functions that return new graphs with updated nodes and edges including their
attributes based on node/edge ID's.

These functions have equivalents in the `graph_setlike_operations` library
where the focus is on returning `views` as often as possible and attributes
are not updated.
"""

import logging

from graphit import __module__, check_graphbase_instance

from graphit.graph_combinatorial.graph_setlike_operations import graph_difference

__all__ = ['graph_add', 'graph_subtract', 'graph_update', 'graph_axis_update']
logger = logging.getLogger(__module__)


def graph_add(*args, **kwargs):
    """
    Add graphs together

    Using the first graph as base graph, add all nodes and edges in the
    remaining graphs to the first graph based on node and edge ID.
    Attributes are updated for nodes and edges already in the graph one or
    multiple times.
    Node and edge attribute update can be switched on/off using the
    `update_node_attributes` and `update_edge_attributes` respectively.

    .. note:: in case multiple graphs are added together that have overlapping
              nodes or edges defining similar attributes the final value of the
              attribute in the result graph equals the last input graph that
              defines that attribute.

    Please use the `graph_setlike_operations.graph_union` function to create a
    union between input graphs that will not update attributes and return
    `views` in case of a common origin graph.

    .. note:: This function will not create any new nodes or edges that are not
              already available in on of the input graphs. This may yield a
              result graph with isolated sub graphs.

    :param args:                   graphs to add together
    :type args:                    :py:list
    :param update_node_attributes: update existing node attributes
    :type update_node_attributes:  :py:bool
    :param update_edge_attributes: update existing edge attributes
    :type update_edge_attributes:  :py:bool

    :return:                       new Graph joining input graphs
    :rtype:                        :graphit:Graph
    """

    if not len(args) > 1:
        raise AttributeError('At least two input Graphs required')

    # Validate if all arguments are Graphs
    check_graphbase_instance(*args)

    # Make a deep copy of the first graph to serve as base graph for adding
    result = args[0].copy(deep=True)

    # Temporary turn off auto_nid to ensure true addition based on node and
    # edge ID instead of auto generated node ID's
    auto_nid = result.auto_nid
    result.auto_nid = False

    update_node_attributes = kwargs.get('update_node_attributes', True)
    update_edge_attributes = kwargs.get('update_edge_attributes', True)
    for graph in args[1:]:
        for nid, attr in graph.nodes.items():
            if nid in result.nodes and not update_node_attributes:
                continue
            result.add_node(nid, **attr)

        for eid, attr in graph.edges.items():
            if eid in result.edges and not update_edge_attributes:
                continue
            result.add_edge(*eid, **attr)

    result.auto_nid = auto_nid

    return result


def graph_subtract(graph1, graph2):
    """
    Subtract the second graph from the first

    Subtracting equals calculating the graph difference between graph1 and
    graph2 using a node oriented difference and returning a copy.

    :param graph1:      first graph
    :type graph1:       :graphit:Graph
    :param graph2:      second graph
    :type graph2:       :graphit:Graph

    :return:            new Graph with differences between graph1, graph2
    :rtype:             :graphit:Graph
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    # Subtract equals topological difference computed by graph_difference
    return graph_difference(graph1, graph2, edge_diff=False, return_copy=True)


def graph_update(graph1, graph2, update_edges=True, update_nodes=True):
    """
    Update graph1 with the content of graph2

    Requires graph2 to be fully contained in graph1 based on graph topology
    measured as equality between nodes and edges assessed by node and edge ID.

    :param graph1:  target graph
    :type graph1:   Graph
    :param graph2:  source graph
    :type graph2:   Graph
    :param update_edges: update edge data
    :type update_edges:  bool
    :param update_nodes: update node data
    :type update_nodes:  bool
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    if graph2 in graph1:
        if update_edges:
            for edge, value in graph2.edges.items():
                graph1.edges[edge].update(value)
        if update_nodes:
            for node, value in graph2.nodes.items():
                graph1.nodes[node].update(value)

    return graph1


def graph_axis_update(graph, data):
    """
    Recursive update graph nodes from dictionary or other graph

    :param graph: graph to update
    :type graph:  GraphAxis
    :param data:  dictionary or graph to update from
    """

    # TODO: restructure module organisation to avoid circular import
    from graphit.graph_axis.graph_axis_class import GraphAxis
    from graphit.graph_io.io_pydata_format import write_pydata

    # Get data as dictionary
    if isinstance(data, GraphAxis):
        data = write_pydata(data)
    if not isinstance(data, dict):
        raise TypeError('Dictionary required')

    # (Recursive) update data
    value_tag = graph.value_tag

    def recursive_update(block, params):

        for key, value in params.items():
            data_node = block.query_nodes(key=key)

            # Key does not exist
            if data_node.empty():
                logger.error('No parameter named "{0}" in data block "{1}"'.format(key, repr(graph)))
                continue

            # Value is dictionary, nested update
            if isinstance(value, dict):
                recursive_update(data_node.descendants(include_self=True), value)
                continue

            # Set single value
            if len(data_node) == 1:
                data_node.set(value_tag, value)
                logger.debug('Update parameter "{0}" on node {1}'.format(key, data_node))

    recursive_update(graph, data)
