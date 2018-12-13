# -*- coding: utf-8 -*-

"""
file: model_user.py

Graph model classes for dealing with user information
"""

import getpass

from graphit.graph_mixin import NodeEdgeToolsBaseClass

__all__ = ['User']

class User(NodeEdgeToolsBaseClass):

    @staticmethod
    def username():
        """
        Get user name of current system user
        """

        return getpass.getuser()

    def set(self, key=None, value=None, **kwargs):
        """
        Set to current system user if called without arguments.
        """

        key = key or self.value_tag
        if key == self.value_tag and not value:
            value = self.username()

        self.nodes[self.nid][key] = value
