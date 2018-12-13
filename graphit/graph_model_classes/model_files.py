# -*- coding: utf-8 -*-

"""
file: model_files.py

Graph model classes for working with files
"""

import os
import logging
import shutil

from graphit import __module__
from graphit.graph_mixin import NodeEdgeToolsBaseClass

__all__ = ['FilePath']
logger = logging.getLogger(__module__)


class FilePath(NodeEdgeToolsBaseClass):

    @property
    def exists(self):

        path = self.get()
        if path:
            return os.path.exists(path)
        return False

    @property
    def iswritable(self):

        return os.access(self.get(), os.W_OK)

    def set(self, key, value=None, absolute=True):

        if key == self.value_tag and value and absolute:
            value = os.path.abspath(value)

        self.nodes[self.nid][key] = value

    def makedirs(self):
        """
        Recursively create the directory structure of the path

        :return:        Absolute path to working directory
        :rtype:         :py:str
        """

        path = self.get()
        if self.exists and self.iswritable:
            logger.info('Directory exists and writable: {0}'.format(path))
            return path

        try:
            os.makedirs(path, 0o755)
        except OSError:
            logger.error('Unable to create project directory: {0}'.format(path))

        logger.info('Create directory {0}'.format(path))
        return path

    def remove(self, ignore_errors=True):
        """
        Remove the path

        Uses `shutil.rmtree` to recursively remove files and directories.

        :param ignore_errors:   remove read-only files.
        :type ignore_errors:    :py:bool
        """

        path = self.get()
        if path:
            shutil.rmtree(path, ignore_errors=ignore_errors)
            logger.info('Remove path {0}'.format(path))
