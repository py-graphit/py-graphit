# -*- coding: utf-8 -*-

"""
file: graph_exceptions.py

Graphit specific exceptions
"""

import logging

from graphit import __module__

__all__ = ['GraphitException', 'GraphitAlgorithmError', 'GraphitEdgeNotFound', 'GraphitNodeNotFound',
           'GraphitValidationError']

logger = logging.getLogger(__module__)


class GraphitException(Exception):
    """
    Base class for Graphit specific exceptions

    Logs the exception as critical before raising.
    """

    def __init___(self, message='', *args, **kwargs):

        logger.critical(message)
        Exception.__init__(self, *args, **kwargs)


class GraphitValidationError(GraphitException):
    """
    Exception raised if validation on a (sub)graph failed
    """

    def __init__(self, message, graph):

        message = "ValidationError on instance {0}: {1}".format(graph.path(), message)
        super(GraphitValidationError, self).__init__(message)


class GraphitNodeNotFound(GraphitException):
    """
    Exception raised if node is not present in the graph
    """


class GraphitEdgeNotFound(GraphitException):
    """
    Exception raised if edge is not present in the graph
    """


class GraphitAlgorithmError(GraphitException):
    """Exception for unexpected termination of algorithms."""
