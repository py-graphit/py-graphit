# -*- coding: utf-8 -*-

"""
file: graph.py

Graph base class implementing a graph based data storage with support
for dictionary like storage of data in graph nodes and edges, rich
graph comparison, query and traversal method and a Object Relations
Mapper.

TODO: Would it be possible and usefull to create support for config files
      to configure a Graph and function arguments?
"""

import collections
import copy
import logging
import weakref

from graphit import __module__
from graphit.graph_py2to3 import to_unicode, prepaire_data_dict
from graphit.graph_storage_drivers.graph_dictstorage_driver import init_dictstorage_driver
from graphit.graph_mixin import NodeTools, EdgeTools
from graphit.graph_orm import GraphORM
from graphit.graph_algorithms.connectivity import nodes_are_interconnected
from graphit.graph_combinatorial.graph_setlike_operations import graph_union, graph_issubset
from graphit.graph_combinatorial.graph_update_operations import graph_update, graph_subtract
from graphit.graph_exceptions import GraphitException
from graphit.graph_helpers import (edges_between_nodes, edge_list_to_nodes, make_edges, share_common_origin,
                                   check_nodes_in_graph)

__all__ = ['GraphBase']
logger = logging.getLogger(__module__)


class GraphBase(object):
    """
    Graph base class

    *Graph root*
    By default a graph is an undirected and non-rooted network of nodes.
    Many graph methods however require the definition of a root relative to
    which a calculation will be performed.

    The graph class defines a `root` attribute for this purpose that is
    undefined by default. It will be set automatically in the following cases:

    * Node traversal: the first node selected (getnodes method) will be assigned
      root and traversal to `child` nodes will be done relative to the `root`.
      If multiple nodes are selected using `getnodes`, the root node is
      ambiguous and will be set to the node with the lowest nid.
    """

    __slots__ = ('orm', 'adjacency', 'nodes', 'edges', 'directed', 'masked', 'auto_nid', 'root', 'key_tag', 'value_tag',
                 'node_tools', 'edge_tools', '_nodeid', 'origin', 'storagedriver', '__weakref__')

    def __init__(self, auto_nid=True, edges=None, directed=False, nodes=None, key_tag=u'key',
                 value_tag=u'value', root=None, orm=None, storagedriver=init_dictstorage_driver):
        """
        Implement class __init__

        Initiate a Graph object with storage objects for node and edge data.
        The type of storage object is controlled by the storage driver
        initiation function defined by the `storagedriver` argument.
        `storagedriver` defaults to the DictStorage driver.

        :param nodes:         object that stores the dictionary of node ID/node
                              data pairs
        :type nodes:          :py:dict or other format accepted by the storage
                              driver
        :param edges:         object that stores the dictionary of edge ID/edge
                              data pairs
        :type edges:          :py:dict or other format accepted by the storage
                              driver
        :param orm:           graph Object Relations Mapper
        :type orm:            GraphORM object
        :param directed:      Rather the graph is directed or undirected
        :type directed:       :py:bool
        :param auto_nid:      Use integers as node ID, automatically assigned
                              and internally managed. If False, the node object
                              added will itself be used as node ID as long as
                              it is hashable. In the latter case, nodes are
                              enforced to be unique, duplicate nodes will be
                              ignored.
        :type auto_nid:       :py:bool
        :param key_tag:       dictionary key used to store node/edge data key
        :type key_tag:        :py:str
        :param value_tag:     dictionary key used to store node/edge data value
        :type value_tag:      :py:str
        :param root:          root node nid used by various methods when
                              traversing the graph in a directed fashion where
                              the notion of a origin is important.
        :type root:           mixed
        :param storagedriver: storage driver initiation function responsible
                              for creating the node, edge and adjacency storage
                              objects. The graph dict storage is the default
                              driver.
        """

        self.storagedriver = storagedriver
        self.orm = orm or GraphORM()

        # Init nodes, edges and adjacency storage using a dedicated storage
        # driver initiation method
        self.nodes, self.edges, self.adjacency = self.storagedriver(nodes, edges)

        # Graph attributes, set directly
        self.directed = directed
        self.masked = False
        self.auto_nid = auto_nid
        self.root = root
        self.key_tag = to_unicode(key_tag)
        self.value_tag = to_unicode(value_tag)
        self.node_tools = NodeTools
        self.edge_tools = EdgeTools

        # Graph internal attributes, do not set manually.
        # Automatically assigned node ID's always increment the highest
        # integer ID in the graph
        self._nodeid = 1
        self._set_auto_nid()
        self.origin = self

    def __add__(self, other):
        """
        Implement class __add__, addition (+).

        This method updates the node and edge attributes of the current graph
        with those of 'other' if needed.
        If the two graphs share a common origin graph then an addition will
        not update the attributes as that will also affect all other subgraphs
        derived from it.

        The addition (or union) of the two graphs is handeled by the
        `graph_union` function and attribute update by `graph_update`.

        :param other: other Graph instance
        :type other:  :graphit:Graph

        :return:      The true union of the two graphs as new graph
        :rtype:       :graphit:Graph
        """

        newgraph = graph_union(self, other)

        # If both graph share the same origin no node/edge updates required.
        if share_common_origin(self, other):
            return newgraph

        return graph_update(newgraph, other)

    def __contains__(self, other):
        """
        Implement class __contains__

        Test if other is identical to, or a subgraph of self with respect to
        its node and edge topology.

        .. warning:: This comparison does not consider identity in node or
                     edge attributes.
        """

        return any([other == self, graph_issubset(other, self)])

    def __copy__(self):
        """
        Copy directives for this class
        """

        return self.copy(deep=False)

    def __deepcopy__(self, memo):
        """
        Deepcopy directives for this class
        """

        return self.copy(deep=True)

    def __eq__(self, other):
        """
        Implement class __eq__

        Evaluate equality based on graph topology

        .. warning:: This comparison does not consider identity in node or
                     edge attributes.
        """

        if not isinstance(other, GraphBase):
            return False

        return self.nodes.keys() == other.nodes.keys() and self.edges.keys() == other.edges.keys()

    def __getitem__(self, key):
        """
        Implement class __getitem__

        Return nodes or edges in a (sub)graph by dictionary lookup.
        This function is overloaded in (sub)graphs containing single nodes or
        edges to provide access to node or edge attributes.

        __getitem__ accepts a Python slice object ([start:stop:step]) to
        retrieve integer based nodes. The slice object is used to build a
        range of integers representing the nodes.

        :return: nodes or edges.
        :rtype:  Node ID as integer or edge ID as tuple of 2 node ID's.
        """

        # Key is a edge ID
        if isinstance(key, (tuple, list)):
            return self.getedges(key)

        # Key is a slice object
        if isinstance(key, slice):
            key = list(range(key.start, key.stop or max(self.nodes)+1, key.step or 1))

        return self.getnodes(key)

    def __getstate__(self):
        """
        Implement class __getstate__

        Enables the class to be pickled. Required because the class uses
        __slots__

        :return:    object content for pickling
        :rtype:     :py:dict
        """

        state = {}
        for key in self.__slots__:
            state[key] = getattr(self, key)

        return state

    def __ge__(self, other):
        """
        Implement class __ge__

        Evaluates if self is greater-then or equal to other in overall size
        which is a combination of number of nodes and edges.
        """

        if not isinstance(other, GraphBase):
            raise GraphitException('Object {0} not instance of Graph base class'.format(type(other).__name__))

        return all([self.edges.keys() >= other.edges.keys(), self.nodes.keys() >= other.nodes.keys()])

    def __gt__(self, other):
        """
        Implement class __gt__

        Evaluates if self is greater-then other in overall size which is a
        combination of number of nodes and edges.
        """

        if not isinstance(other, GraphBase):
            raise GraphitException('Object {0} not instance of Graph base class'.format(type(other).__name__))

        return all([self.edges.keys() > other.edges.keys(), self.nodes.keys() > other.nodes.keys()])

    def __iadd__(self, other):
        """
        Implements class __iadd__, inplace addition (+=).

        This method updates the node and edge attributes of the current graph
        with those of 'other' if needed.
        If the two graphs share a common origin graph then an addition will
        not update the attributes as that will also affect all other subgraphs
        derived from it.

        :param other: Graph to add
        :type other:  :graphit:Graph

        :return:      self with other added
        :rtype:       :graphit:Graph
        :raises:      GraphitException, if other is not a Graph
        """

        result = graph_union(self, other)
        if share_common_origin(self, other):
            return result

        # Inplace update node and edge stores
        result = graph_update(result, other)
        self.nodes, self.edges, self.adjacency = self.storagedriver(result.nodes, result.edges)

        return self

    def __isub__(self, other):
        """
        Implement class __isub__, inplace subtraction (-=).

        If the two graphs share a common origin graph then an inplace
        subtraction will not update the attributes because attribute
        removal will also affect all other subgraphs derived from it.

        Graph subtraction is handled by the `graph_subtract` function.

        :param other: Graph to subtract
        :type other:  :graphit:Graph

        :return:      self with other subtracted
        :rtype:       :graphit:Graph
        :raises:      GraphitException, if other is not a Graph
        """

        if not isinstance(other, GraphBase):
            raise GraphitException("Object {0} not instance of Graph base class".format(type(other).__name__))

        result = graph_subtract(self, other)
        if share_common_origin(self, other):
            return result

        # Inplace update node and edge stores
        self.nodes, self.edges, self.adjacency = self.storagedriver(result.nodes, result.edges)

        return self

    def __iter__(self):
        """
        Implement class __iter__

        Iterate over nodes using iternodes

        :return: single node Graph
        :rtype:  :graphit:Graph
        """

        return self.iternodes()

    def __len__(self):
        """
        Implement class __len__

        Represent the length of the graph as the number of nodes

        :return: number of nodes
        :rtype:  int
        """

        return len(self.nodes)

    def __le__(self, other):
        """
        Implement class __le__

        Evaluates if self is less-then or equal to other in overall size
        which is a combination of number of nodes and edges.
        """

        if not isinstance(other, GraphBase):
            raise GraphitException("Object {0} not instance of Graph base class".format(type(other).__name__))

        return all([self.edges.keys() <= other.edges.keys(), self.nodes.keys() <= other.nodes.keys()])

    def __lt__(self, other):
        """
        Implement class __lt__

        Evaluates if self is less-then other in overall size which is a
        combination of number of nodes and edges.
        """

        if not isinstance(other, GraphBase):
            raise GraphitException("Object {0} not instance of Graph base class".format(type(other).__name__))

        return all([self.edges.keys() < other.edges.keys(),
                    self.nodes.keys() < other.nodes.keys()])

    def __ne__(self, other):
        """
        Implement class __ne__

        Evaluate non-equality based on graph topology

        .. warning:: This comparison does not consider identity in node or
                     edge attributes.
        """

        if not isinstance(other, GraphBase):
            return False

        return not self.__eq__(other)

    def __repr__(self):
        """
        Implement class __repr__

        String representation of the class listing node and edge count.

        :rtype: :py:str
        """

        return '<{0} object {1}: {2} nodes, {3} edges>'.format(
            type(self).__name__, id(self), len(self.nodes), len(self.edges))

    def __setstate__(self, state):
        """
        Implement class __setstate__

        Enables the class to be unpickled. Required because the class uses
        __slots__

        :param state:    object content for unpickling
        :type state:     :py:dict
        """

        for key, value in state.items():
            if key in self.__slots__:
                setattr(self, key, value)

    def __sub__(self, other):
        """
        Implement class __sub__, subtraction (-).

        If the two graphs share a common origin graph then a subtraction
        will not update the attributes because attribute removal will also
        affect all other subgraphs derived from it.

        Graph subtraction is handled by the `graph_subtract` function.

        :param other: Graph to subtract
        :type other:  :graphit:Graph

        :return:      difference graph
        :rtype:       :graphit:Graph
        :raises:      GraphitException, if other is not a Graph
        """

        if not isinstance(other, GraphBase):
            raise GraphitException("Object {0} not instance of Graph base class".format(type(other).__name__))

        return graph_subtract(self, other)

    @classmethod
    def _get_class_object(cls):
        """
        Returns the current class object. Used by the graph ORM to construct
        new Graph based classes
        """

        return cls

    def _set_auto_nid(self):
        """
        Set the automatically assigned node ID (nid) based on the '_id' node
        attributes in the current graph
        """

        _id = [attr.get('_id', 0) for attr in self.nodes.values()]
        if len(_id):
            self._nodeid = max(_id) + 1

    def _set_origin(self, graph):
        """
        Set a weak reference to the full graph

        :param graph: Graph instance
        """

        if isinstance(graph, GraphBase):
            self.origin = weakref.ref(graph.origin)()

    def add_edge(self, nd1, nd2, directed=None, node_from_edge=False, unicode_convert=True, run_edge_new=True,
                 **kwargs):
        """
        Add edge between two nodes to the graph

        An edge is defined as a connection between two node ID's.
        Edge metadata defined as a dictionary allows it to be queried
        by the various graph query functions.

        After de new edge is created the edge class 'new' method is called once
        to allow any custom edge initiation to be performed. This feature can
        be customized by overloading the 'new' method in the
        NodeEdgeToolsBaseClass abstract base class.
        Calling the 'new' method can be disabled using the run_node_new flag.

        :param nd1:             first node in edge node pair. Source node in
                                directed graph.
        :param nd2:             second node in edge node pair. Target node in
                                directed graph.
        :param directed:        override the graph definition for directed
                                for the added edge.
        :type directed:         :py:bool
        :param node_from_edge:  make node for edge node id's not in graph
        :type node_from_edge:   :py:bool
        :param unicode_convert: convert string types to unicode
        :type unicode_convert:  :py:bool
        :param run_edge_new:    run the custom initiation method (new method) of
                                the new edge once.
        :type run_edge_new:     :py:bool
        :param kwargs:          any additional keyword arguments to be added as
                                edge metadata.

        :return:                edge ID
        :rtype:                 :py:tuple
        """

        # If node_from_edge than set auto_nid to false forcing identical node
        # and edge ID's
        curr_auto_nid = self.auto_nid
        if node_from_edge:
            self.auto_nid = False

        nd1 = to_unicode(nd1, convert=unicode_convert)
        nd2 = to_unicode(nd2, convert=unicode_convert)
        for nodeid in (nd1, nd2):
            if nodeid not in self.nodes:
                if node_from_edge:
                    self.add_node(nodeid)
                else:
                    raise GraphitException('Node with id {0} not in graph.'.format(nodeid))

        # Create edge tuples, directed or un-directed (local override possible for mixed graph).
        if directed is None:
            directed = self.directed
        edges_to_add = make_edges((nd1, nd2), directed=directed)

        edges_added = []
        for i, edge in enumerate(edges_to_add):
            if edge in self.edges:
                logger.warning('Edge between nodes {0}-{1} exists. Use edge update to change attributes.'.format(*edge))
                continue

            # Undirectional edge: second edge points to first edge attributes
            if i == 1 and not directed:
                self.edges[edge] = self.edges[edges_to_add[0]]
            else:
                # Make a deepcopy of the added attributes
                self.edges[edge] = prepaire_data_dict(copy.deepcopy(kwargs))

            edges_added.append(edge)
            logger.debug('Add edge between node {0}-{1}'.format(*edge))

        # Call 'new' method of new edges once to allow for custom initiation
        if run_edge_new:
            for edge in edges_added:
                self.getedges(edge).new()

        # If node_from_edge, restore auto_nid setting
        self.auto_nid = curr_auto_nid

        return edges_to_add[0]

    def add_edges(self, edges, node_from_edge=False, unicode_convert=True, run_edge_new=True, **kwargs):
        """
        Add multiple edges to the graph.

        This is the iterable version of the add_edge methods allowing
        multiple edge additions from any iterable.
        If the iterable yields a tuple with a dictionary as third
        argument the key/value pairs of that dictionary will be added
        as attributes to the new edge along with any keyword arguments
        passed to the method.

        The latter functionality can be used to add the edges of one
        graph to those of another by using graph.edges.items() as
        argument to `add_edges`.

        :param edges:           Objects to be added as edges to the graph
        :type edges:            Iterable of hashable objects
        :param node_from_edge:  make node for edge node id's not in graph
        :type node_from_edge:   :py:bool
        :param unicode_convert: convert string types to unicode
        :type unicode_convert:  :py:bool
        :param run_edge_new:    run the custom initiation method (new method) of
                                the new edges once.
        :type run_edge_new:     :py:bool

        :return:                list of edge ids for the objects added in
                                the same order as th input iterable.
        :rtype:                 :py:list
        """

        edges_added = []
        for edge in edges:
            if len(edge) == 3 and isinstance(edge[2], dict):
                attr = {}
                attr.update(edge[2])
                attr.update(kwargs)
                edges_added.append(self.add_edge(edge[0], edge[1], node_from_edge=node_from_edge,
                                                 unicode_convert=unicode_convert, run_edge_new=run_edge_new, **attr))
            else:
                edges_added.append(self.add_edge(edge[0], edge[1], unicode_convert=unicode_convert,
                                                 node_from_edge=node_from_edge, run_edge_new=run_edge_new, **kwargs))

        return edges_added

    def add_node(self, node=None, unicode_convert=True, run_node_new=True, **kwargs):
        """
        Add a node to the graph

        All nodes are stored using a dictionary like data structure that can be
        represented like:

            {nid: {'_id': auto_nid, attribute_key: attribute_value, ....}}

        'nid' is the primary node identifier which is either an auto-incremented
        unique integer value if `Graph.auto_nid` equals True or a custom value
        when False.

        If `Graph.auto_nid` equals True, the `node` parameter is stored as part
        of the node attributes (value in the above dict example) using the
        `Graph.key_tag` as key unless overloaded by any additional keyword
        arguments provided to the method.
        Using the key_tag and value_tag is a convenient way of storing node
        data that should be accessible using the same key. The key_tag and
        value_tag are used as default in the various dictionary style set and
        get methods of the graph, node and edge classes.

        When `Graph.auto_nid` equals False, the `node` parameter becomes the
        primary node identifier that can be any hashable object except None.

        .. note:: With auto_nid disabled the method checks if there is a node
                  with nid in the graph already. If found, a warning is logged
                  and the attributes of the existing node are updated.

        The node attribute dictionary contains at least the '_id' attribute
        representing the unique auto-incremented integer node identifier and
        any additional keyword argument provided to the method (kwargs)

        After de new node is created the node class 'new' method is called once
        to allow any custom node initiation to be performed. This feature can
        be customized by overloading the 'new' method in the
        NodeEdgeToolsBaseClass abstract base class.
        Calling the 'new' method can be disabled using the run_node_new flag.

        :param node:            object representing the node
        :type node:             any hashable object
        :param unicode_convert: convert string types to unicode
        :type unicode_convert:  :py:bool
        :param run_node_new:    run the custom initiation method (new method) of
                                the new node once.
        :type run_node_new:     :py:bool
        :param kwargs:          any additional keyword arguments to be added as
                                node attributes.

        :return:                node ID (nid)
        :rtype:                 int
        """

        # Use internal nid or node as node ID
        if self.auto_nid:
            nid = self._nodeid
        else:

            # Node should not be None
            if node is None:
                raise GraphitException('Node ID required when auto_nid is disabled')

            # Node needs to be hashable
            nid = to_unicode(node, convert=unicode_convert)
            if not isinstance(nid, collections.Hashable):
                raise GraphitException('Node {0} of type {1} not a hashable object'.format(nid, type(nid).__name__))

            # If node exist, log a warning, update attributes and return
            if nid in self.nodes:
                logger.warning('Node with identifier "{0}" already assigned'.format(nid))
                self.nodes[nid].update(copy.deepcopy(kwargs))
                return nid

        logger.debug('Add node. id: {0}, type: {1}'.format(nid, type(node).__name__))

        # Prepare node data dictionary, always set a unique ID.
        node_data = {self.key_tag: to_unicode(node, convert=unicode_convert)}
        node_data.update(prepaire_data_dict(copy.deepcopy(kwargs)))
        node_data[u'_id'] = self._nodeid
        self._nodeid += 1

        self.nodes[nid] = node_data

        # Call 'new' method of the new node once to allow for custom initiation
        if run_node_new:
            self.getnodes(nid).new()

        return nid

    def add_nodes(self, nodes, unicode_convert=True, run_node_new=True, **kwargs):
        """
        Add multiple nodes to the graph.

        This is the iterable version of the add_node methods allowing
        multiple node additions from any iterable.
        If the iterable yields a tuple with a dictionary as seconds
        argument the key/value pairs of that dictionary will be added
        as attributes to the new node along with any keyword arguments
        passed to the method.

        The latter functionality can be used to add the nodes of one
        graph to those of another by using graph.nodes.items() as
        argument to `add_nodes`.

        :param nodes:           Objects to be added as nodes to the graph
        :type nodes:            Iterable of hashable objects
        :param unicode_convert: convert string types to unicode
        :type unicode_convert:  :py:bool
        :param run_node_new:    run the custom initiation method (new method) of
                                the new nodes once.
        :type run_node_new:     :py:bool

        :return:                list of node ids for the objects added in the
                                same order as th input iterable.
        :rtype:                 :py:list
        """

        node_collection = []
        for node in nodes:

            # Check if node has argument dictionary
            if isinstance(node, (tuple, list)):
                if len(node) == 2 and isinstance(node[1], dict):
                    attr = {}
                    attr.update(node[1])
                    attr.update(kwargs)
                    node_collection.append(self.add_node(node[0], unicode_convert=unicode_convert,
                                                         run_node_new=run_node_new, **attr))
            else:
                node_collection.append(self.add_node(node, unicode_convert=unicode_convert,
                                                     run_node_new=run_node_new, **kwargs))

        return node_collection

    def clear(self):
        """
        Clear nodes and edges in the graph.

        If the Graph instance represents a sub graph, only those nodes and edges
        will be removed.
        """

        self.nodes.clear()
        self.edges.clear()

        # Reset node ID counter if the full graph is cleared
        if len(self) == len(self.origin):
            self._nodeid = 0

    def copy(self, deep=True, copy_view=False):
        """
        Return a (deep) copy of the graph

        The copy method offers shallow and deep copy functionality for graphs
        similar to Pythons building copy and deepcopy functions.

        A shallow copy (python `copy`) will copy the class and its attributes
        except for the nodes, edges, orm and origin objects that are referenced.
        As such the copy will not be independent from the source Graph.

        Using deep=True, a deep copy (python `deepcopy`) will be returned that
        is a new and fully independent copy of the source Graph.
        A new graph with only those nodes and edges represented by the node and
        edge 'views' will be returned by default. Setting the `copy_view`
        attribute to True will copy the full nodes and edges data set of the
        origin graph together with the views to the new graph.

        :param deep:        return a deep copy of the Graph object
        :type deep:         :py:bool
        :param copy_view:   make a deep copy of the full nodes and edges
                            dictionary and set any 'views'. Otherwise, only make
                            a deep copy of the 'view' state.
        :type copy_view:    :py:bool

        :return:            copy of the graph
        :rtype:             Graph object
        """

        # Make a new instance of the current class
        base_cls = self._get_class_object()

        # Make a deep copy
        if deep:
            class_copy = base_cls(nodes=copy.deepcopy(self.nodes.to_dict(return_full=copy_view)),
                                  edges=copy.deepcopy(self.edges.to_dict(return_full=copy_view)))

            # Copy node view
            if copy_view and self.nodes.is_view:
                class_copy.nodes.set_view(self.nodes.keys())

            # Copy edge view
            if copy_view and self.edges.is_view:
                class_copy.edges.set_view(self.edges.keys())

            # Copy ORM
            class_copy.orm.node_mapping.update(copy.deepcopy(self.orm.node_mapping.to_dict()))
            class_copy.orm.node_mapping.update(copy.deepcopy(self.orm.edge_mapping.to_dict()))

        # Make a shallow copy
        else:
            class_copy = base_cls(nodes=self.nodes, edges=self.edges, orm=self.orm)
            class_copy.origin = self.origin

        # Copy class attributes except fixed
        for key in self.__slots__:
            if key not in ('edges', 'nodes', 'adjacency', 'origin', 'orm', '__weakref__'):
                setattr(class_copy, key, copy.deepcopy(getattr(self, key)))

        # Reset the graph root if needed
        if class_copy.root and class_copy.root not in class_copy.nodes:
            class_copy.root = min(class_copy.nodes)
            logger.debug('Reset graph root to {0}'.format(class_copy.root))

        logger.debug(
            'Return {0} copy of graph {1}'.format('deep' if deep else 'shallow', repr(self)))

        return class_copy

    def empty(self):
        """
        Report if the graph is empty (no nodes)

        :rtype: :py:bool
        """

        return len(self) == 0

    def get(self, nid, key=None, default=None, defaultattr=None):
        """
        Return (sub)graph values.

        This is a placeholder method that can be overloaded by custom classes
        to return a value for (sub)graphs containing more than one edge or
        node in contrast to the single node or edge graph classes for which
        the get method returns attribute values.
        The `get` method has the latter functionality by default and will
        return single node or edge attributes based on nid.

        :param nid:         node or edge identifier to return data for. If not
                            defined attempt to resolve using `nid` property.
        :type nid:          mixed
        :param key:         node or edge value attribute name. If not defined
                            then attempt to use class wide `key_tag`
                            attribute.
        :type key:          mixed
        :param defaultattr: node or edge value attribute to use as source of
                            default data when `key` attribute is not present.
        :type defaultattr:  mixed
        :param default:     value to return when all fails
        :type default:      mixed
        """

        # Get node or edge
        if isinstance(nid, (tuple, list)):
            target = self.edges.get(tuple(nid))
        else:
            target = self.nodes.get(nid)

        if target:

            # Get key or default class node/edge data key
            key = key or self.key_tag

            if key in target:
                return target[key]

        if defaultattr:
            return target.get(defaultattr, default)
        return default

    def getedges(self, edges, orm_cls=None, add_edge_tools=True):
        """
        Get an edge as graph object

        Returns a new Graph with a 'view' on the selected nodes and the edges
        connecting them. If nodes equals None or empty list, the returned Graph
        object will have no nodes and is basically 'empty'.

        Getedges calls the Graph Object Relation Mapper (GraphORM) class
        to customize the returned (sub) Graph class. Next to the custom classes
        registered with the ORM mapper, the `getedges` method allows for
        further customization of the returned Graph object through the
        orm_cls attribute. In addition, for sub graphs containing single edges,
        the EdgeTools class is added.

        The addition of the EdgeTools class changes the behaviour of the Graph
        class to a state where it provides direct access to edge attributes for
        that particular edge. This may be undesirable in cases where one wants
        to iterate over graphs even if they contain only one edge.
        The `add_edge_tools` attribute prevents addition of EdgeTools for these
        cases.

        :param edges:           edge id
        :type edges:            iterable of length 2 containing integers
        :param orm_cls:         custom classes to construct new edge oriented
                                Graph class from.
        :type orm_cls:          :py:list
        :param add_edge_tools:  add edge tools to Graph instance if one edge
        :type add_edge_tools:   :py:bool
        """

        # Coerce to list
        if all(isinstance(e, (tuple, list)) for e in edges):
            edges = [tuple(e) for e in edges]
        elif len(edges) == 2:
            edges = [tuple(edges)]

        # Edges need to be in graph
        if edges:
            edges_not_present = [e for e in edges if e not in self.edges]
            if edges_not_present:
                raise GraphitException('Edges not in graph {0}'.format(edges_not_present))
        else:
            edges = []

        # Build custom class list. Default EdgeTools need to be included in
        # case of single edges and not overloaded in MRO.
        custom_orm_cls = []
        if orm_cls:
            if not isinstance(orm_cls, list):
                raise GraphitException('Custom edge classes need to be defined as list')
            custom_orm_cls.extend(orm_cls)
        if len(edges) == 1 and add_edge_tools:
            custom_orm_cls.append(self.edge_tools)

        base_cls = self.orm.get_edges(self, edges, classes=custom_orm_cls)
        w = base_cls(nodes=self.nodes, edges=self.edges, orm=self.orm)

        # Set views for nodes and edges
        w.edges.set_view(edges)
        w.nodes.set_view(edge_list_to_nodes(edges))

        # copy class attributes except fixed
        for key in self.__slots__:
            if key not in ('nodes', 'edges', 'adjacency', 'orm', '__weakref__'):
                setattr(w, key, getattr(self, key))
        w._set_origin(self.origin)

        # If root node set and masked, reset root to node in new sub(graph)
        # to prevent a root node that is not in the new subgraph.
        if w.root is not None and self.masked:
            if w.root not in w.nodes() and len(w.nodes):
                w.root = min(w.nodes[n].get('_id', n) for n in w.nodes())

        return w

    def getnodes(self, nodes, orm_cls=None, add_node_tools=True):
        """
        Get one or multiple nodes as new sub graph instance

        Returns a new Graph with a 'view' on the selected nodes and the edges
        connecting them. If nodes equals None or empty list, the returned Graph
        object will have no nodes and is basically 'empty'.

        Getnodes calls the Graph Object Relation Mapper (GraphORM) class
        to customize the returned (sub) Graph class. Next to the custom classes
        registered with the ORM mapper, the `getnodes` method allows for
        further customization of the returned Graph object through the
        orm_cls attribute. In addition, for sub graphs containing single nodes,
        the NodeTools class is added.

        The addition of the NodeTools class changes the behaviour of the Graph
        class to a state where it provides direct access to node attributes for
        that particular node. This may be undesirable in cases where one wants
        to iterate over graphs even if they contain only one node.
        The `add_node_tools` attribute prevents addition of NodeTools for these
        cases.

        :param nodes:           single node ID or an iterable of multiple node
                                ID's
        :param orm_cls:         custom classes to construct new node oriented
                                Graph class from.
        :type orm_cls:          :py:list
        :param add_node_tools:  add node tools to Graph instance if single node
        :type add_node_tools:   :py:bool

        :return:                Graph instance reflecting the node selection
        :rtype:                 :graphit:Graph
        :raises:                GraphitException, node check fails
        """

        # Coerce to list
        if not isinstance(nodes, (list, tuple, set)):
            nodes = [nodes]

        if nodes:
            check_nodes_in_graph(self.origin, nodes)

        # Build custom class list. Default NodeTools need to be included in
        # case of single nodes and not overloaded in MRO.
        custom_orm_cls = []
        if orm_cls:
            if not isinstance(orm_cls, list):
                raise GraphitException('Custom node classes need to be defined as list')
            custom_orm_cls.extend(orm_cls)
        if len(nodes) == 1 and add_node_tools:
            custom_orm_cls.append(self.node_tools)

        base_cls = self.orm.get_nodes(self, nodes, classes=custom_orm_cls)
        w = base_cls(nodes=self.nodes, edges=self.edges, orm=self.orm)

        # Set views for nodes and edges.
        w.nodes.set_view(nodes)
        w.edges.set_view(edges_between_nodes(self, nodes))

        # copy class attributes except fixed
        for key in self.__slots__:
            if key not in ('nodes', 'edges', 'adjacency', 'orm', '__weakref__'):
                setattr(w, key, getattr(self, key))
        w._set_origin(self.origin)

        # If root node set and masked, reset root to node in new sub(graph)
        # to prevent a root node that is not in the new subgraph.
        if w.root is not None and self.masked:
            if w.root not in w.nodes() and len(w.nodes):
                w.root = min(w.nodes[n].get('_id', n) for n in w.nodes())

        return w

    def insert(self, node, between):
        """
        Insert a new node in between two other

        :param node:    node to add
        :param between: nodes to add new node in between
        """

        if len(between) > 2:
            raise Exception('Insert is only able to insert between two nodes')

        if nodes_are_interconnected(self, between):
            nid = self.add_node(node)
            for n in between:
                self.add_edge(nid, n)

            del self.edges[between]

    def iteredges(self, orm_cls=None, reverse=False, sort_key=str):
        """
        Graph edge iterator

        Returns a new graph view object for the given edge and it's nodes.

        :param orm_cls:  custom classes to construct new Graph class from for
                         every edge that is returned
        :type orm_cls:   list
        :param reverse:  switch between ascending and descending sort order of
                         the returned edges
        :type reverse:   :py:bool
        :param sort_key: function for sorting edge IDs. Equivalent to the 'key'
                         argument to Pythons 'sorted' build in function.

        :return:         single edge Graph object
        :rtype:          :graphit:Graph
        """

        for edge in sorted(self.edges.keys(), reverse=reverse, key=sort_key):
            yield self.getedges(edge, orm_cls=orm_cls)

    def iternodes(self, orm_cls=None, reverse=False, sort_key=str):
        """
        Graph node iterator

        Returns a new graph view object for the given node and it's edges.
        The dynamically created object contains additional node tools.
        Nodes are returned in node ID sorted order.

        :param orm_cls:  custom classes to construct new Graph class from for
                         every node that is returned
        :type orm_cls:   list
        :param reverse:  switch between ascending and descending sort order of
                         the returned nodes
        :type reverse:   :py:bool
        :param sort_key: function for sorting node IDs. Equivalent to the 'key'
                         argument to Pythons 'sorted' build in function.

        :return:         single node Graph object
        :rtype:          :graphit:Graph
        """

        for node in sorted(self.nodes.keys(), reverse=reverse, key=sort_key):
            yield self.getnodes(node, orm_cls=orm_cls)

    def query_edges(self, query=None, orm_cls=None, add_edge_tools=True, **kwargs):
        """
        Select edges based on edge data query

        The query is executed by the `query` method of the respective edge
        storage driver class. That query method accepts a query function often
        as lambda function allowing for rich query functionality.
        The `query_edges` method accepts three different input arguments that
        are passed to the `query` method with some conversion if needed:

            1 A dictionary where the key, value pairs are converted to a
              lambda function evaluation 'key == value' against the edge
              attributes.
            2 Additional keyword arguments used in the same way as in 1.
            3 A custom (lambda) function passed to as is.

        Matching edges are passed on to the `getedges` method and returned.

        :param query:           query function as input to storage driver
                                `query` method
        :type query:            :py:func
        :param orm_cls:         custom classes added to new Graph class.
        :type orm_cls:          :py:list
        :param add_edge_tools:  add edge tools to Graph instance if single edge
        :type add_edge_tools:   :py:bool
        :param kwargs:          if `query` is None, build lambda function from
                                keyword arguments

        :return:                edges subgraph
        :rtype:                 :graphit:Graph
        """

        if isinstance(query, dict):
            kwargs.update(query)
            query = None

        if query is None:
            query = lambda key, value: all([value.get(k) == v for k, v in kwargs.items()])

        edges = self.edges.query(query)
        return self.getedges(edges, orm_cls=orm_cls, add_edge_tools=add_edge_tools)

    def query_nodes(self, query=None, orm_cls=None, add_node_tools=True, **kwargs):
        """
        Select nodes based on node data query

        The query is executed by the `query` method of the respective node
        storage driver class. That query method accepts a query function often
        as lambda function allowing for rich query functionality.
        The `query_nodes` method accepts three different input arguments that
        are passed to the `query` method with some conversion if needed:

            1 A dictionary where the key, value pairs are converted to a
              lambda function evaluation 'key == value' against the node
              attributes.
            2 Additional keyword arguments used in the same way as in 1.
            3 A custom (lambda) function passed to as is.

        Matching nodes are passed on to the `getnodes` method and returned.

        :param query:           query function as input to storage driver
                                `query` method
        :type query:            :py:func
        :param orm_cls:         custom classes added to new Graph class.
        :type orm_cls:          :py:list
        :param add_node_tools:  add node tools to Graph instance if single node
        :type add_node_tools:   :py:bool
        :param kwargs:          if `query` is None, build lambda function from
                                keyword arguments

        :return:                nodes subgraph
        :rtype:                 :graphit:Graph
        """

        if isinstance(query, dict):
            kwargs.update(query)
            query = None

        if query is None:
            query = lambda key, value: all([value.get(k) == v for k, v in kwargs.items()])

        nodes = self.nodes.query(query)
        return self.getnodes(nodes, orm_cls=orm_cls, add_node_tools=add_node_tools)

    def remove_edge(self, nd1, nd2, directed=None):
        """
        Removing an edge from the graph

        Checks if the graph contains the edge, then removes it. If the graph is
        undirectional, try to remove both edges of the undirectional pair.
        Force directed removal of the edge using the 'directed' argument.
        Useful in mixed (un)-directional graphs.

        If the graph is a (sub)graph representing a `view` on the origin graph,
        the edge is removed from the view and not from the origin.

        :param nd1:        first node in edge node pair. Source node in
                           directed graph.
        :param nd2:        second node in edge node pair. Target node in
                           directed graph.
        :param directed:   force directed removal of the edge
        :type directed:    :py:bool

        :raises:           GraphitException, if edge not in graph
        """

        if not isinstance(directed, bool):
            directed = self.directed

        # Make edges, directed or undirected based on graph settings
        for edge in make_edges((nd1, nd2), directed=directed):
            if edge in self.edges:
                del self.edges[edge]
                logger.debug('Removed edge {0} from graph'.format(edge))
            else:
                raise GraphitException('Unable to remove edge {0}. No such edge ID'.format(edge))

    def remove_edges(self, edges, directed=None):
        """
        Remove multiple edges from the graph.

        This is the iterable version of the remove_edge methods allowing
        mutliple edge removal from any iterable.

        :param edges:     Iterable of edges to remove
        :type edges:      Iterable of edges defined as tuples of two node ID's
        :param directed:  force directed removal of the edge
        :type directed:   :py:bool
        """

        for edge in edges:
            self.remove_edge(*edge, directed=directed)

    def remove_node(self, node):
        """
        Removing a node from the graph

        Checks if the graph contains the node and if the node is connected with
        edges. Removes the node and associated edges.

        If the graph is a (sub)graph representing a `view` on the origin graph,
        the node is removed from the view and not from the origin.

        :param node: Node to remove
        :type node: mixed
        """

        if node in self.nodes:

            # Get edges connected to node and remove them
            edges = [edge for edge in self.edges if node in edge]
            for edge in edges:
                del self.edges[edge]

            # Remove node from nodes object
            del self.nodes[node]

            msg = 'Removed node {0} with {1} connecting edges from graph'
            logger.debug(msg.format(node, len(edges)))

        else:
            msg = 'Unable to remove node {0}. No such node ID'.format(node)
            logger.warning(msg)

    def remove_nodes(self, nodes):
        """
        Remove multiple nodes from the graph.

        This is the iterable version of the remove_node methods allowing
        multiple nodes to be removed from any iterable.

        :param nodes: Nodes to remove
        :type nodes: mixed
        """

        for node in nodes:
            self.remove_node(node)

    def items(self, keystring=None, valuestring=None, **kwargs):
        """
        Python dict-like function to return node items in the (sub)graph.

        Keystring defines the value lookup key in the node data dict.
        This defaults to the graph key_tag.
        Valuestring defines the value lookup key in the node data dict.

        :param keystring:   Data key to use for dictionary keys.
        :type keystring:    :py:str
        :param valuestring: Data key to use for dictionary values.
        :type valuestring:  :py:str

        :return:            List of keys, value pairs
        :rtype:             :py:list
        """

        keystring = keystring or self.key_tag
        valuestring = valuestring or self.value_tag

        return [(n.get(keystring), n.get(valuestring)) for n in self.iternodes()]

    def keys(self, keystring=None, **kwargs):
        """
        Python dict-like function to return node keys in the (sub)graph.

        Keystring defines the value lookup key in the node data dict.
        This defaults to the graph key_tag.

        :param keystring:   Data key to use for dictionary keys.
        :type keystring:    :py:str

        :return:            List of keys
        :rtype:             :py:list
        """

        keystring = keystring or self.key_tag
        return [n.get(keystring) for n in self.iternodes()]

    def values(self, valuestring=None, **kwargs):
        """
        Python dict-like function to return node values in the (sub)graph.

        Valuestring defines the value lookup key in the node data dict.

        :param valuestring: Data key to use for dictionary values.
        :type valuestring:  :py:str

        :return:            List of values
        :rtype:             :py:list
        """

        valuestring = valuestring or self.value_tag
        return [n.get(valuestring) for n in self.iternodes()]
