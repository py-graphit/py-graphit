# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_cwl_format.py

"""
Functions for importing data structures in Common Workflow Language format.

The Common Workflow Language (CWL) is a specification for describing analysis
workflows and tools in a way that makes them portable and scalable across a
variety of software and hardware environments, from workstations to cluster,
cloud, and high performance computing (HPC) environments.

CWL data structures are stored in JSON or YAML format.
The lie_graph CWL parser supports syntax version 1.0.2 as described here:
    https://www.commonwl.org/v1.0/

Citation:
    Peter Amstutz, Michael R. Crusoe, Nebojša Tijanić (editors), Brad Chapman,
    John Chilton, Michael Heuer, Andrey Kartashov, Dan Leehr, Hervé Ménager,
    Maya Nedeljkovich, Matt Scales, Stian Soiland-Reyes, Luka Stojanovic (2016):
    Common Workflow Language, v1.0. Specification, Common Workflow Language
    working group. https://w3id.org/cwl/v1.0/ doi:10.6084/m9.figshare.3115156.v2

For more information on CWL consult:
    https://www.commonwl.org
"""

import os
import logging

from graphit import __module__
from graphit.graph_io.io_yaml_format import read_yaml

logger = logging.getLogger(__module__)

__all__ = ['read_cwl']


def read_cwl(cwl_file, graph=None, **kwargs):
    """
    Parse Common Wokflow Language data structures to a graph

    Additional keyword arguments (kwargs) are passed to `read_pydata`

    :param cwl_file:       CWL data to parse
    :type cwl_file:        File, string, stream or URL
    :param graph:          Graph object to import dictionary data in
    :type graph:           :graphit:Graph

    :return:               GraphAxis object
    :rtype:                :graphit:GraphAxis
    """

    cwl_graph = read_yaml(cwl_file, graph=graph, level=0, **kwargs)

    # Parse referenced CWL files (steps) as relative paths to the base cwl file
    refs = cwl_graph.query_nodes({cwl_graph.key_tag: 'run'})
    base_path = os.getcwd()
    for ref in refs:
        ref_cwl_path = os.path.join(base_path, ref())
        if os.path.isfile(ref_cwl_path):
            ref_cwl_graph = read_yaml(ref_cwl_path, graph=graph, level=0, **kwargs)
            logging.info('Inline include referenced CWL file: {0}'.format(ref_cwl_path))
        else:
            raise IOError('Referenced CWL file {0} not found'.format(ref_cwl_path))

    return cwl_graph
