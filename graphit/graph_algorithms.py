# -*- coding: utf-8 -*-

import heapq
import logging

from itertools import count

from graphit import __module__

__all__ = ['node_neighbors', 'degree', 'dfs', 'dfs_paths', 'dijkstra_shortest_path',
           'brandes_betweenness_centrality', 'eigenvector_centrality', 'adjacency',
           'is_reachable', 'nodes_are_interconnected', 'size']

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


def dfs(graph, root, method='dfs', max_depth=10000):
    """
    General implementation of depth-first-search algorithm.
    
    The real power of the dfs method is combining it with the
    graph query methods. These allow sub graphs to be selected
    based on node or edge attributes such as graph directionality
    or edge weight.
    
    :param graph:     graph to search
    :type graph:      graph class instance
    :param root:      root node to start the search from
    :type root:       node ID or Node object
    :param method:    search method. Depth-first search (dfs, default)
                      and Breath-first search (bfs) supported.
    :type method:     :py:str
    :param max_depth: maximum search depth
    :type max_depth:  int, default equals 10000
    """
    
    # Get node object from node ID
    root = graph.getnodes(root)
    
    # Define the search method
    stack_pop = -1
    if method == 'bfs':
        stack_pop = 0
    
    visited = []
    stack = [root.nid]
    depth = 0
    
    while stack or depth == max_depth:
        node = stack.pop(stack_pop)
        
        if node not in visited:
            visited.append(node)
            stack.extend(
                [x for x in node_neighbors(graph, node) if x not in visited])
            depth += 1
    
    return visited


def dfs_paths(graph, start, goal, method='dfs'):
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
    
    :rtype:           :py:list
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
            if next_node == goal:
                yield path + [next_node]
            else:
                stack.append((next_node, path + [next_node]))


def dijkstra_shortest_path(graph, start, goal, weight='weight'):
    """
    Dijkstra algorithm for finding shortest paths.
    
    In contrast to depth- or breath first search, Dijkstra's algorithm
    supports weighted graphs using a priority queue.
    
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
    
    q = [(0, start, ())]
    visited = []
    while len(q):
        (cost1, v1, path) = heapq.heappop(q)
        if v1 not in visited:
            visited.append(v1)
        if v1 == goal:
            return list(flatten(path))[::-1] + [v1]
        path = (v1, path)
        for v2 in adj[v1]:
            if v2 not in visited:
                cost2 = graph.edges[(v1, v2)].get(weight, 1)
                heapq.heappush(q, (cost1 + cost2, v2, path))

    return []


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
    :type graph:       Graph class instance
    :param normalized: normalize betweenness centrality measure between 0 and 1
    :type normalized:  bool
    :param weight:     edge attribute to use as edge weight
    :type weight:      string
    
    :rtype:            :py:dict
    """

    betweenness = dict.fromkeys(graph.nodes, 0.0)
    nodes = nodes or graph.nodes

    for node in nodes:
        # single source shortest paths
        S = []
        P = {}
        for v in graph.nodes:
            P[v] = []
        D = {}
        sigma = dict.fromkeys(graph.nodes, 0.0)
        sigma[node] = 1.0
        if weight is None:  # use BFS
            D[node] = 0
            Q = [node]
            while Q:  # use BFS to find shortest paths
                v = Q.pop(0)
                S.append(v)
                Dv = D[v]
                sigmav = sigma[v]
                for w in graph.adjacency[v]:
                    if w not in D:
                        Q.append(w)
                        D[w] = Dv + 1
                    if D[w] == Dv + 1:  # this is a shortest path, count paths
                        sigma[w] += sigmav
                        P[w].append(v)  # predecessors

        else:
            # use Dijkstra's algorithm
            seen = {node: 0}
            c = count()
            Q = []  # use Q as heap with (distance,node id) tuples
            heapq.heappush(Q, (0, next(c), node, node))
            while Q:
                (dist, _, pred, v) = heapq.heappop(Q)
                if v in D:
                    continue  # already searched this node.
                sigma[v] += sigma[pred]  # count paths
                S.append(v)
                D[v] = dist
                for w in graph.adjacency[v]:
                    vw_dist = dist + graph.edges[(v, w)].get(weight, 1)
                    if w not in D and (w not in seen or vw_dist < seen[w]):
                        seen[w] = vw_dist
                        heapq.heappush(Q, (vw_dist, next(c), v, w))
                        sigma[w] = 0.0
                        P[w] = [v]
                    elif vw_dist == seen[w]:  # handle equal paths
                        sigma[w] += sigma[v]
                        P[w].append(v)

        # accumulation
        delta = dict.fromkeys(S, 0)
        correction = 1 if endpoints else 0
        if endpoints:
            betweenness[node] += len(S) - correction
        while S:
            w = S.pop()
            coeff = (1 + delta[w]) / sigma[w]
            for v in P[w]:
                delta[v] += sigma[v] * coeff
            if w != node:
                betweenness[w] += delta[w] + correction

    # Rescale betweenness values
    scale = 0.5 if graph.directed else None
    nr_nodes = float(len(graph))
    if normalized:
        scale = None
        if endpoints and nr_nodes >= 2:
            scale = 1 / (nr_nodes * (nr_nodes - 1))
        elif nr_nodes > 2:
            scale = 1 / ((nr_nodes - 1) * (nr_nodes - 2))

    if scale is not None:
        scale = scale * nr_nodes / len(nodes)
        for v in betweenness:
            betweenness[v] *= scale

    return betweenness


def eigenvector_centrality(graph, normalized=True, reverse=True, rating=None,
                           start=None, iterations=100, tolerance=0.0001):
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
    
    TODO: Implementation does not work yet. Need to look into adjacency function
    """
    
    if rating is None:
        rating = {}
    
    G = graph.nodes.keys()
    W = adjacency(graph, directed=True, reverse=reverse)
    
    def _normalize(x):
        s = sum(x.values())
        if s != 0:
            s = 1.0 / s
        for k in x:
            x[k] *= s
    
    x = start
    if x is None:
        x = dict([(n, random()) for n in G])
    _normalize(x)
    
    # Power method: y = Ax multiplication.
    for i in range(iterations):
        x0 = x
        x = dict.fromkeys(x0.keys(), 0)
        for n in x:
            for nbr in graph.adjacency[n]:
                r = 1
                if n in rating:
                    r = rating[n]
                x[n] += 0.01 + x0[nbr] * graph.adjacency[n][nbr] * r
        _normalize(x)
        e = sum([abs(x[n] - x0[n]) for n in x])
        if e < len(graph.nodes) * tolerance:
            if normalized:
                # Normalize between 0.0 and 1.0.
                m = max(x.values())
                if m == 0:
                    m = 1
                x = dict([(id, w / m) for id, w in x.iteritems()])
            return x
    
    # raise NoConvergenceError
    logger.warning("node weight is 0 because eigenvector_centrality() did not converge.")
    return dict([(n, 0) for n in G])


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
    
    :param graph: Graph to query
    :type graph: Graph class instance
    :param root: source node ID
    :type root: int
    :param destination: destintion node ID
    :type destination: int
    :return: bool
    """
    
    if root in graph.nodes and destination in graph.nodes:
        connected_path = dfs(graph, root)
        return destination in connected_path
    else:
        logger.error('Root or destination nodes not in graph')


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


def nodes_are_interconnected(graph, nodes):
    """
    Are all the provided nodes directly connected with one another
    
    :param graph: Graph to query
    :type graph:  :graphit:Graph
    :param nodes: nodes to test connectivity for
    :type nodes:  :py:list

    :rtype:       :py:bool
    """
    
    nid_list = []
    for node in nodes:
        if hasattr(node, 'nid'):
            nid_list.append(node.nid)
        elif node in graph.nodes:
            nid_list.append(node)
        else:
            raise 'Node not in graph {0}'.format(node)

    nid_list = set(nid_list)

    collection = []
    for nid in nid_list:
        query = set(graph.adjacency[nid] + [nid])
        collection.append(query.intersection(nid_list) == nid_list)
    
    return all(collection)


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
