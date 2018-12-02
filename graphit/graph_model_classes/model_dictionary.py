# -*- coding: utf-8 -*-

"""
file: model_dictionary.py

Graph mixin class to add method to a Graph base class that will have it
behave like a python dictionary.
"""

__all__ = ['PythonDictionary']


class PythonDictionary(object):

    def items(self, keystring=None, valuestring=None):
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

    def keys(self, keystring=None):
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

    def values(self, valuestring=None):
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
