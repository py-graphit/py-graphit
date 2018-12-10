# -*- coding: utf-8 -*-

"""
file: graph_mixin.py

NodeTools and EdgeTools classes for axis based graphs (GraphAxis class)
"""

from graphit.graph_mixin import NodeTools, EdgeTools
from graphit.graph_algorithms.shortest_path import dijkstra_shortest_path

__all__ = ['NodeAxisTools']


class NodeAxisTools(NodeTools):
    
    def __getattr__(self, key):
        """
        Implement class __getattr__
        
        Expose child nodes as class attributes using their primary key (usually
        defined by the key_tag). If not found, call __getattr__ on the
        parent class which uses attribute lookup.
        
        :param key: node key
        :type key:  :py:str
        
        :return:    node
        """
        
        # Look for key amongst node children `key_tag`
        for child in self:
            if child.get(self.key_tag) == key:
                return child
        
        return super(NodeAxisTools, self).__getattr__(key)
    
    def __iter__(self):
        """
        Implement class __iter__
        
        Iterate over the nodes children
        
        :return: single node graph
        :rtype:  :py:Graph
        """
        
        for child in self.children(return_nids=True):
            yield self.getnodes(child)
    
    def path(self, key=None, sep="."):
        """
        Build a breadcrumb (path) trail from the root node to the
        current node.
        
        :param key: parameter key to build breadcrumb path from
        :type key:  :py:str
        :param sep: breadcrumb path seperator character
        :type sep:  :py:str
        
        :return:    breadcrumb path
        :rtype:     :py:str
        """
        
        key = key or self.key_tag
        
        shortest_path = dijkstra_shortest_path(self.origin, self.root, self.nid)
        breadcrumbs = [str(self.origin.nodes[nid][key]) for nid in shortest_path]
        
        return sep.join(breadcrumbs)


class EdgeAxisTools(EdgeTools):
    
    pass
