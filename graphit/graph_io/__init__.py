#TODO: make walk and serialization methods to customize format export
#TODO: add easy check for undirectional edges where both edge directions are
#      present in edges but one is a pointer to the other to keep attributes
#      in sinc, for export we should then only export one of the edges.

"""
Importing and exporting data structures as graphit graphs.

These include both data structures in a format dedicated to representing graphs
and other (hierarchical) data that has a structure that could be represented as
a graph.
"""

# Dedicated graph formats
from graphit.graph_io.io_dot_format import *
from graphit.graph_io.io_jgf_format import *
from graphit.graph_io.io_pgf_format import *
from graphit.graph_io.io_tgf_format import *

# General (hierarchical) data structures
from graphit.graph_io.io_json_format import *
from graphit.graph_io.io_pydata_format import *
from graphit.graph_io.io_web_format import *
from graphit.graph_io.io_xml_format import *
from graphit.graph_io.io_yaml_format import *

# Specific data formats
from graphit.graph_io.io_cwl_format import *
from graphit.graph_io.io_jsonschema_format import *
