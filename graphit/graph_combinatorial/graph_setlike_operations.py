# -*- coding: utf-8 -*-

"""
file: graph_setlike_operations.py

Functions to perform Python [set-like](https://docs.python.org/3/library/
stdtypes.html#set-types-set-frozenset) operation on graphs.

These functions aim to return a view-based result graph (subgraph) as often
as possible by checking if the input graphs share te same origin graph.
If returning a view is not possible or explicitly not requested the returned
graph is based on a deep copy of the first graph provided as argument to the
function.

The set-like combinatorial operations are based on (dis)-similarity in node
and edge ID's regardless of the `auto_nid` setting.
Set-like operations based on node and/or edge attributes is possible by first
performing a node/edge query followed by the set operation.

A general concept in (graphit) Graphs is that nodes do not need to have edges
but edges cannot exist without their respective nodes. While union and
intersection operations will always return graphs that meet these requirements,
difference operations do not. If the difference between two graphs is an edge
returning that edge alone as Graph object without the corresponding nodes is
not allowed. Therefore, by default, the difference functions are node oriented.
In calculating the difference between a sub graph and its parent graph this
approach will result in a desired graph subtraction operation where the edges
linking sub graph and parent are removed.
However, these functions have a `edge_diff` flag that will switch the function
to calculate the edge oriented difference that will include nodes to return a
valid graph.

.. note:: These functions do not update node and/or edge attributes in the
          resulting graph as might be required in for instance a union or
          intersection operation.
"""

from graphit import check_graphbase_instance
from graphit.graph_combinatorial.graph_split_join_operations import graph_join
from graphit.graph_helpers import share_common_origin

__all__ = ['graph_union', 'graph_intersection', 'graph_difference', 'graph_issubset',
           'graph_issuperset', 'graph_symmetric_difference']


def graph_union(*args, **kwargs):
    """
    Return a graph with the union of the input graphs

    The union represents the combined unique nodes and edges present in
    the graphs. Similarity is based on ID.

    Nodes and edges are added without updating the respective attributes.
    The latter can be done by calling the `update` function afterwards.

    If the graphs share a common origin graph and `return_copy` is False
    the returned intersection graph will be a view on the origin, else it is
    a new graph.
    In both cases, the first graph in the argument list is used as basis
    for the returned union graph.

    :param args:        graphs to return the union for
    :type args:         :py:list
    :param return_copy: force return a new graph as deep copy based on graph1
    :type return_copy:  :py:bool

    :return:            union graph
    :rtype:             :graphit:Graph
    :raises:            AttributeError, if arguments no instance of Graph class
    """

    if not len(args) > 1:
        raise AttributeError('At least two input Graphs required')

    # Validate if all arguments are Graphs
    check_graphbase_instance(*args)

    all_share_common_origin = all([share_common_origin(args[0], n) for n in args[1:]])
    if all_share_common_origin and not kwargs.get('return_copy', False):

        nids = []
        for graph in args:
            nids.extend([n for n in graph.nodes if n not in nids])

        eids = []
        for graph in args:
            eids.extend([e for e in graph.edges if e not in eids])

        result = args[0].origin.getnodes(nids)
        result.edges.set_view(eids)
        return result
    else:

        # make a deep copy of the first graph
        result = args[0].copy(deep=True, copy_view=False)

        # we need control over the node ID to add
        # temporary turn off auto_nid if needed
        auto_nid = result.auto_nid
        result.auto_nid = False

        for graph in args[1:]:
            for node, attrib in graph.nodes.items():
                if node not in result.nodes:
                    result.add_node(node, **attrib)

            for edge, attrib in graph.edges.items():
                if edge not in result.edges:
                    result.add_edge(*edge, **attrib)

        # Restore auto_nid
        result.auto_nid = auto_nid

        return result


def graph_intersection(graph1, graph2, return_copy=False):
    """
    Return a graph with the intersection in nodes and edges between the two
    input graphs

    The intersection represents the nodes and edges connecting them present
    in both graphs. Node and edge similarity is based on ID.

    If the graphs share a common origin graph and `return_copy` is False
    the returned intersection graph will be a view on the origin, else it is
    a new graph.

    :param graph1:      first graph
    :type graph1:       :graphit:Graph
    :param graph2:      second graph
    :type graph2:       :graphit:Graph
    :param return_copy: force return a new graph as deep copy based on graph1
    :type return_copy:  :py:bool

    :return:            intersection graph
    :rtype:             :graphit:Graph
    :raises:            AttributeError, if arguments no instance of Graph class
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    # Compute node/edge intersection
    intersect_nodes = graph1.nodes.intersection(graph2.nodes)
    intersect_edges = graph1.edges.intersection(graph2.edges)

    if share_common_origin(graph1, graph2) and not return_copy:

        # First get node intersection then edges
        result = graph1.origin.getnodes(intersect_nodes)
        result.edges.set_view(intersect_edges)
        return result
    else:
        result = graph1.getnodes(intersect_nodes)
        result.edges.set_view(intersect_edges)
        return result.copy(deep=True, copy_view=False)


def graph_difference(graph1, graph2, edge_diff=False, return_copy=False):
    """
    Return a graph with the difference in nodes and edges of `graph1` with
    respect to `graph2`.

    The difference represents the nodes and edges connecting them that are
    present in `graph1` but not in `graph2`. Difference is based on ID.
    The difference is node driven resulting in edges being removed when the
    nodes on either end are removed. Use the `edge_diff` argument to switch
    to an edge driven difference calculation,

    If the graphs share a common origin graph and `return_copy` is False
    the returned intersection graph will be a view on the origin, else it is
    a new graph.

    :param graph1:      first graph
    :type graph1:       :graphit:Graph
    :param graph2:      second graph
    :type graph2:       :graphit:Graph
    :param edge_diff:   switch from node to edge driven difference calculation
    :type edge_diff:    :py:bool
    :param return_copy: force return a new graph as deep copy based on graph1
    :type return_copy:  :py:bool

    :return:            difference graph
    :rtype:             :graphit:Graph
    :raises:            AttributeError, if arguments no instance of Graph class
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    # Compute edge or node difference.
    if edge_diff:
        difference_edges = graph1.edges.difference(graph2.edges)
    else:
        difference_nodes = graph1.nodes.difference(graph2.nodes)

    if share_common_origin(graph1, graph2) and not return_copy:
        if edge_diff:
            return graph1.origin.getedges(difference_edges)
        return graph1.origin.getnodes(difference_nodes)
    else:
        if edge_diff:
            result = graph1.getedges(difference_edges)
        else:
            result = graph1.getnodes(difference_nodes)
        return result.copy(deep=True, copy_view=False)


def graph_symmetric_difference(graph1, graph2, edge_diff=False, return_copy=False):
    """
    Return a new graph with the symmetric difference in nodes and edges of two
    graphs.

    The symmetric difference represents the nodes and edges connecting them
    that are present in `graph1` but not in `graph2` and vice versa.
    It is thus the opposite of the `graph_intersection`.
    The difference is node driven resulting in edges being removed when the
    nodes on either end are removed. Use the `edge_diff` argument to switch
    to an edge driven difference calculation,

    If the graphs share a common origin graph and `return_copy` is False
    the returned intersection graph will be a view on the origin, else it is
    a new graph.

    :param graph1:      first graph
    :type graph1:       :graphit:Graph
    :param graph2:      second graph
    :type graph2:       :graphit:Graph
    :param edge_diff:   switch from node to edge driven difference calculation
    :type edge_diff:    :py:bool
    :param return_copy: force return a new grpah as deep copy based on graph1
    :type return_copy:  :py:bool

    :return:            symmetric difference graph
    :rtype:             :graphit:Graph
    :raises:            AttributeError, if arguments no instance of Graph class
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    # Compute node or edge symmetric difference.
    if edge_diff:
        symdiff_edges = graph1.edges.symmetric_difference(graph2.edges)
    else:
        symdiff_nodes = graph1.nodes.symmetric_difference(graph2.nodes)

    if share_common_origin(graph1, graph2) and not return_copy:
        if edge_diff:
            return graph1.origin.getedges(symdiff_edges)
        return graph1.origin.getnodes(symdiff_nodes)
    else:
        # Get node or edge difference for both and join them in a new graph
        if edge_diff:
            result = graph1.getedges(symdiff_edges.difference(graph2.edges)).copy(deep=True, copy_view=False)
            graph_join(result, graph2.getedges(symdiff_edges.difference(graph1.edges)))
        else:
            result = graph1.getnodes(symdiff_nodes.difference(graph2.nodes)).copy(deep=True, copy_view=False)
            graph_join(result, graph2.getnodes(symdiff_nodes.difference(graph1.nodes)))

        return result


def graph_issubset(graph1, graph2):
    """
    Test if graph1 is a subset of graph2 two in terms of nodes and edges.

    :param graph1:  first graph
    :type graph1:   :graphit:Graph
    :param graph2:  second graph
    :type graph2:   :graphit:Graph

    :return:        issubset or not
    :rtype:         :py:bool
    :raises:        AttributeError, if arguments no instance of Graph class
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    return graph1.nodes.issubset(graph2.nodes) and graph1.edges.issubset(graph2.edges)


def graph_issuperset(graph1, graph2):
    """
    Test if graph1 is a superset of graph2 two in terms of nodes and edges.

    :param graph1:  first graph
    :type graph1:   :graphit:Graph
    :param graph2:  second graph
    :type graph2:   :graphit:Graph

    :return:        issuperset or not
    :rtype:         :py:bool
    :raises:        AttributeError, if arguments no instance of Graph class
    """

    # Validate if all arguments are Graphs
    check_graphbase_instance(graph1, graph2)

    return graph1.nodes.issuperset(graph2.nodes) and graph1.edges.issuperset(graph2.edges)
