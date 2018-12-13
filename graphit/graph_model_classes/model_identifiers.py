# -*- coding: utf-8 -*-

"""
file: model_identifiers.py

Graph model classes for working (unique) identifiers
"""

import re
import uuid

from graphit.graph_py2to3 import PY_STRING
from graphit.graph_mixin import NodeEdgeToolsBaseClass
from graphit.graph_exceptions import GraphitValidationError

__all__ = ['UUID']
UUID_REGEX = re.compile(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')


class UUID(NodeEdgeToolsBaseClass):

    @staticmethod
    def create():

        return str(uuid.uuid1())

    def set(self, key, value=None, **kwargs):

        if key == self.value_tag:
            if isinstance(value, PY_STRING) and UUID_REGEX.match(value):
                pass
            else:
                raise GraphitValidationError('No valid UUID: {0}'.format(value), self)

        self.nodes[self.nid][key] = value
