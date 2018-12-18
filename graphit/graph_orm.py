# -*- coding: utf-8 -*-

"""
file: graph_orm.py

Defines the Graph Object Relation Mapper (ORM)
"""

import inspect
import logging

from graphit import __module__
from graphit.graph_py2to3 import colabc
from graphit.graph_storage_drivers.graph_dictstorage_driver import DictStorage

__all__ = ['GraphORM']
logger = logging.getLogger(__module__)


class MappingDictStorage(DictStorage):

    mapping_index = 0

    @classmethod
    def _check_duplicate_mapping(self, source, target):
        """
        Equality of functions is determined by checking code object equality

        :param source:
        :param target:
        :return:
        """

        return target['class'] == source['class'] and \
               hash(target['match_func'].__code__) == hash(source['match_func'].__code__)

    def add(self, cls, match_func, mro_pos=0):
        """
        Map a custom class based on node or edge attributes

        A mapped class is included in a new Graph or GraphAxis class by the
        ORM class factory based on a match in the node or edge attributes.

        Every node/edge mapped using the `add` method results in a unique map.
        Use the `update` method to update an existing mapping using the map ID.

        :param cls:        class to map
        :type cls:         :py:class
        :param match_func: attribute matching function
        :type match_func:  :py:func
        :param mro_pos:    preferred index of class in Python MRO
        :type mro_pos:     :py:int

        :return:           mapping identifier
        :rtype:            :py:int
        :raises:           TypeError
        """

        if not inspect.isclass(cls):
            raise TypeError('"cls" argument is not a class (got {0})'.format(type(cls)))

        if not callable(match_func):
            raise TypeError('"match_func" argument is not a function (got {0})'.format(match_func))

        # Build mapping dictionary and check if it already exists
        mapping_dict = {'mro_pos': mro_pos, 'class': cls, 'match_func': match_func}
        for mapidx, mapping in self._storage.items():
            if self._check_duplicate_mapping(mapping, mapping_dict):
                logger.info('Mapping {0} already defined. Use update to make changes'.format(mapidx))
                return mapidx

        # Add to mapping dictionary
        self.mapping_index += 1
        self._storage[self.mapping_index] = mapping_dict

        return self.mapping_index

    def update(self, *args, **kwargs):
        """
        Update the current node or edge orm mapping with those defined by
        another orm instance

        :param mapper: node or edge mapping dictionary
        :type mapper:  :py:dict

        :raises:       TypeError
        """

        mapping = kwargs
        if len(args):
            mapping = args[0]

        if not isinstance(mapping, colabc.MutableMapping):
            raise TypeError('Requires dict-like storage class to update from')

        # Update node mapping for all unique mappings in other ORM
        to_add = []
        for other_id, other_mapping in mapping.items():
            similar = False
            for self_mapping in self.values():
                similar = self._check_duplicate_mapping(self_mapping, other_mapping)
                if similar:
                    logger.info('Identical mapping for {0}: {1}'.format(other_id, other_mapping['class']))
                    continue

            if not similar:
                to_add.append(other_id)

        for map_id in to_add:
            self.mapping_index += 1
            self[self.mapping_index] = mapping[map_id]

        logging.debug('Add {0} ORM mappings after update'.format(len(to_add)))

    def match(self, graph, node_edge_ids):
        """
        Match attributes of node or edge based on ID against registered
        matching functions.
        Sort mapped classes according to preferred MRO order (mro_pos).

        :param graph:           Graph containing nodes or edges to match
        :param node_edge_ids:   List of node or edge ID's

        :return:                Sorted classes to be used in the ORM class
                                factory method
        :rtype:                 :py:list
        """

        mro_class_stack = []
        for i in node_edge_ids:

            # Get node or edge attributes
            if isinstance(i, tuple):
                attributes = graph.origin.edges.get(i)
            else:
                attributes = graph.origin.nodes.get(i)

            for mapping in self.values():
                matching_result = mapping['match_func'](attributes or {})
                if isinstance(matching_result, bool) and matching_result:
                    mro_class_stack.append((mapping['mro_pos'], mapping['class']))

        # Sort mapped classes according to preferred MRO order (mro_pos)
        orm_classes = [c[1] for c in sorted(mro_class_stack, key=lambda x: x[0])]

        return orm_classes


class GraphORM(object):
    """
    Graph Object Relation Mapper (ORM) class

    An Object Relation Mapper encapsulates data in an object based on a series
    of rules. It is an often used concept in database bindings in particular
    for dynamically typed languages such as Python.

    graphit uses an ORM to return customized versions of the Graph/GraphAxis
    classes at runtime based on rules matched against node or edge attributes.
    It is a powerful method to extend the Graph base class with new methods or
    override existing ones.

    **How it works**
    ORM mapping is performed by registering custom classes for nodes or edges
    together with a matching function using the `add` method on the
    `node_mapping` and `edge_mapping` methods respectively. For each call to
    the `get_nodes` or `get_edges` methods of the ORM, all registered matching
    functions will be evaluated and the classes for positive matches will be
    included in the newly generated Graph/GraphAxis class together with other
    classes defined by the `orm_cls` argument of the `getnodes` or `getedges`
    methods.

    **Matching functions**
    Matching is based on a match function (`match_func` argument) that requires
    the node or edge attribute dictionary as input and needs to return a boolean
    for the matching result.

    An example of a matching function where x is the node or edge dictionary:

        lambda x: x.get('arg') == 1 and 'conf' in x

    A lambda function is convenient but any function accepting a dictionary and
    returning a boolean will do. The benefit of using functions is the freedom
    in defining the matching criteria.

    **Class inheritance**
    Class inheritance is respected by the ORM and can be controlled.
    By default, the base class used in a mapping is the one from which the call
    to the `getnodes` or `getedges` methods was made. This includes the Graph
    base class and any custom methods added to it by the user or previous calls
    to the ORM.
    Inheritance can be disabled by setting the `inherit` variable on the ORM
    class to False.

    **The Method Resolution Order (mro)**
    A new class is dynamically build by the class factory of the ORM from a
    list of classes that include required graph base classes and custom classes.
    The ORM ensures that the right Python method resolution order is defined.
    When multiple classes in the mro have similarly named methods the order
    affects the final class behaviour through method override.

    The mro can be controlled using the `mro_pos` argument that can be defined
    as part of a registered custom node or edge (`add` method).
    This argument influence the sort order of resolved classes in the MRO
    following the rule: smaller indices are resolved first.
    The mro_pos index may be both a negative to large positive number to force
    first or last resolution respectively.
    This is also important when using Pythons build-in 'super' function to call
    similar named method up the MRO stack.

    **Current scope of the ORM**
    The ORM is used in the `getnodes` and `getedges` methods of the Graph class
    but only when a single node or edge is requested as it is currently
    designed to only match against the attributes of a single node or edge.
    This is primarily done to guard performance by limiting the amount of ORM
    matching evaluations performed. In addition the number of edges that need
    evaluation for a single node and vice versa depends on graph directionality
    and masking which may cause ambiguous behaviour for now.

    However, both `getnodes` and `getedges` will accept custom classes that
    will be included in the newly generated Graph class regardless of the ORM
    results (orm_cls argument). This allows to partly bypass current limitations
    of the ORM by writing custom evaluation code.
    """

    __slots__ = ('node_mapping', 'edge_mapping', 'inherit')

    def __init__(self, node_mapping=None, edge_mapping=None, inherit=True):
        """
        Implement class __init__

        Initiate empty MappingDictStorage for the node and edge mapping.
        Update these objects with any node or edge MappingDictStorage
        objects passed as argument.

        :param node_mapping:  object that stores a dictionary of node mappings
                              as ID:mapping
        :type node_mapping:   MappingDictStorage instance
        :param edge_mapping:  object that stores a dictionary of edge mappings
                              as ID:mapping
        :type edge_mapping:   MappingDictStorage instance
        :param inherit:
        :type inherit:        :py:bool
        """

        self.node_mapping = MappingDictStorage(node_mapping)
        self.edge_mapping = MappingDictStorage(edge_mapping)
        self.inherit = inherit

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

    def __repr__(self):
        """
        Implement class __repr__

        String representation of the class listing node and edge mapping.

        :rtype: :py:str
        """

        msg = '<{0} object {1}: {2} node and {3} edge mappings>'
        return msg.format(type(self).__name__, id(self), len(self.node_mapping), len(self.edge_mapping))

    def orm_class_factory(self, base_cls, classes, exclude_node_edge=False):
        """
        Factory for custom Graph classes

        Build custom Graph class by adding classes to base_cls.
        The factory resolves the right method resolution order (mro).

        Use the `exclude_node_edge` argument to prevent inheritance of classes
        that operate on single node or edge graphs such as the NodeTools class.
        This is important in for instance a query returning multiple nodes
        called from a single node object.
        Classes are identified by having the __isnetbc__ class variable part of
        the NodeEdgeToolsBaseClass abstract base class that custom node or edge
        classes should inherit from.

        :param base_cls:          graph base class. Needs to be based on Graph
        :type base_cls:           :py:class
        :param classes:           additional classes to include in base class
                                  when building custom Graph class sorted
                                  according to the desired method resolution
                                  order
        :type classes:            :py:list
        :param exclude_node_edge: prevent including specific single node or
                                  edge classes (such as NodeTools) when
                                  returning an interface to multiple nodes or
                                  edges.
        :type exclude_node_edge:  :py:bool

        :return:                  custom Graph class
        :rtype:                   :py:class
        """

        # Get method resolution order for base_cls excluding ORM build classes
        base_cls_mro = [c for c in base_cls.mro() if not self.__module__ == c.__module__]

        # Inherit previous custom modules or only graph module classes
        if not self.inherit:
            base_cls_mro = [c for c in base_cls_mro if c.__name__ in ('GraphBase', 'GraphAxis') and
                            c.__module__.startswith('graphit')]

        # Prevent including single node or edge classes
        if exclude_node_edge:
            base_cls_mro = [n for n in base_cls_mro if '__isnetbc__' not in dir(n)]

        # Add custom classes to the base class mro
        for n in reversed(classes):
            if n not in base_cls_mro:
                base_cls_mro.insert(0, n)

        # Build the new base class
        return type(base_cls.__name__, tuple(base_cls_mro), {})

    def get_nodes(self, graph, nodes, classes=None):
        """
        Resolve mapped nodes

        Node mapping and construction of custom classes is only performed when
        a single node is provided.
        For multiple nodes or when the query yields no result, the same class
        is returned base on the Graph instance making the call to the get
        method including any custom classes defined.

        :param graph:    a graph to match against
        :type graph:     :graphit:graph:Graph
        :param nodes:    one or more nodes
        :type nodes:     :py:list
        :param classes:  additional classes to include in the base class when
                         building the custom Graph class
        :type classes:   :py:list or :py:tuple

        :return:         new Graph class instance
        """

        customcls = classes or []
        if len(nodes) > 1:
            return self.orm_class_factory(graph._get_class_object(), customcls, exclude_node_edge=True)

        # Perform query
        orm_classes = self.node_mapping.match(graph, nodes)

        # Build new (custom) Graph class
        orm_classes.extend(customcls)
        return self.orm_class_factory(graph._get_class_object(), orm_classes)

    def get_edges(self, graph, edges, classes=None):
        """
        Resolve mapped edges

        Edge mapping and construction of custom classes is only performed when
        a single edge is provided.
        For multiple edges or when the query yields no result, the same class
        is returned base on the Graph instance making the call to the get
        method including any custom classes defined.

        :param graph:    a graph to match against
        :type graph:     :graphit:graph:Graph
        :param edges:    one or more edges
        :type edges:     :py:list
        :param classes:  additional classes to include in the base class when
                         building the custom Graph class
        :type classes:   :py:list or :py:tuple

        :return:         new Graph class instance
        """

        customcls = classes or []
        if len(edges) > 1:
            return self.orm_class_factory(graph._get_class_object(), customcls, exclude_node_edge=True)

        # Perform query
        orm_classes = self.edge_mapping.match(graph, edges)

        # Build new (custom) Graph class
        orm_classes.extend(customcls)
        return self.orm_class_factory(graph._get_class_object(), orm_classes)
