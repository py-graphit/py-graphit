# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_gml_format.py

"""
Reading and writing graphs in RCSB Protein DataBank format (.pdb).

The PDB molecular structure format is represented as GraphAxis graph using the
Model-Segment-Residue-Atom (MSRA) hierarchical structure. The reader and
writer support the official wwPDB guidelines for MODEL, ATOM, HETATM and CONECT
records. Other records are not supported.

Reference and specification:
    - https://www.wwpdb.org/documentation/file-format-content/format33/v3.3.html
"""

import logging

from graphit import __module__, GraphAxis
from graphit.graph_exceptions import GraphitException
from graphit.graph_py2to3 import StringIO
from graphit.graph_io.io_helpers import open_anything

logger = logging.getLogger(__module__)
write_column_format = "{label:6}{atnum:>5} {atname:^4}{atalt:1}{resname:>3} {chain}{resnum:>4}{insert:1}   " \
                      "{xcoor:8.3f}{ycoor:8.3f}{zcoor:8.3f}{occ:6.2f}{b:6.2f}   {segid:>4}{elem:>2}{charge:>2}\n"
read_column_format = {'label': (slice(0, 6), str),
                      'atnum': (slice(6, 12), int),
                      'atname': (slice(12, 16), str),
                      'atalt': (slice(16, 17), str),
                      'resname': (slice(17, 21), str),
                      'chain': (slice(21, 22), str),
                      'resnum': (slice(22, 26), int),
                      'insert': (slice(26, 30), str),
                      'xcoor': (slice(30, 38), float),
                      'ycoor': (slice(38, 46), float),
                      'zcoor': (slice(46, 54), float),
                      'occ': (slice(54, 60), float),
                      'b': (slice(60, 66), float),
                      'segid': (slice(72, 76), str),
                      'elem': (slice(76, 78), str),
                      'charge': (slice(78, 80), float)}

__all__ = ['read_pdb', 'write_pdb']


def read_pdb(pdb_file, graph=None, column_format=read_column_format):
    """
    Parse RCSB Protein Data Bank (PDB) structure files to a graph

    Builds a Model-Segment-Residue-Atom (MSRA) hierarchy of the structure
    in a GraphAxis graph. Primary structure data will be extracted from the
    columns in ATOM and HETATM lines. The data label, character positions
    and required type conversion are described by the `column_format`
    dictionary by default supporting wwPDB version 3.3 guidelines.
    CONECT records will represented as edges between atoms. These edges can
    be identified by the 'label=conect' attribute.

    .. note:: The GraphAxis 'auto_nid' functionality will be enabled for the
              import to uniquely represent structures possibly sharing similar
              atom numbers (MODELS).

    :param pdb_file:       PDB data to parse
    :type pdb_file:        File, string, stream or URL
    :param graph:          Graph object to import dictionary data in
    :type graph:           :graphit:Graph
    :param column_format:  ATOM/HETATM line label based slice records
    :type column_format:   :py:dict

    :return:               GraphAxis object
    :rtype:                :graphit:GraphAxis
    """

    # User defined or default Graph object
    if graph is None:
        graph = GraphAxis()
    elif not isinstance(graph, GraphAxis):
        raise GraphitException('Unsupported graph type {0}'.format(type(graph)))

    # Enable auto_nid
    graph.data['auto_nid'] = True

    # Parse PDB file
    pdb_file = open_anything(pdb_file)
    curr_chain = None
    curr_resnum = None
    curr_model = graph.add_node('model', id=1, label='msra')
    first_model = True
    nid_atnum_mapping = {}
    for lc, line in enumerate(pdb_file.readlines()):

        # Line label
        line_label = line[0:6].strip()

        # Add new model
        if line_label == 'MODEL':
            try:
                model_id = int(line[10:14])
            except ValueError:
                raise GraphitException('Invalid or missing model serial number in line {0}'.format(lc))

            if first_model:
                graph[curr_model]['id'] = model_id
                first_model = False
            else:
                curr_model = graph.add_node('model', id=model_id)

            nid_atnum_mapping = {}

        # Process CONECT lines as edges
        elif line_label == 'CONECT':
            conect = map(int, line.split()[1:])
            if not all([i in nid_atnum_mapping for i in conect]):
                raise GraphitException('Invalid CONECT, atom numbers do not exist: {0}'.format(line.strip()))

            for edge in [(conect[0], n) for n in conect[1:]]:
                graph.add_edge(nid_atnum_mapping[edge[0]], nid_atnum_mapping[edge[1]], label='conect')

        # Process ATOM/HETATM lines
        elif line_label in ('ATOM', 'HETATM'):

            # Parse PDB line according to `column_format` definitions
            record = dict.fromkeys(column_format.keys())
            for column, sliceval in column_format.items():
                slicer, valtype = sliceval
                value = line[slicer].strip()
                if value:
                    try:
                        record[column] = valtype(value)
                    except ValueError:
                        raise GraphitException('PDB parsing error for "{0}" in line: {1}'.format(column, line.strip()))

            # Set chain node
            if curr_chain is None or graph.nodes[curr_chain]['chain'] != record['chain']:
                curr_chain = graph.add_node('segment', chain=record['chain'], segid=record['segid'])
                graph.add_edge(curr_model, curr_chain, label='msra')

            # Set residue node
            if curr_resnum is None or graph.nodes[curr_resnum]['resnum'] != record['resnum']:
                curr_resnum = graph.add_node('residue', resnum=record['resnum'], resname=record['resname'],
                                             insert=record['insert'])
                graph.add_edge(curr_chain, curr_resnum, label='msra')

            # Set atom node
            curr_atom = graph.add_node(line_label.lower(), atnum=record['atnum'], atname=record['atname'],
                                       atalt=record['atalt'], label=record['label'],
                                       coord=[record[c] for c in ('xcoor', 'ycoor', 'zcoor')],
                                       elem=record['elem'], charge=record['charge'], b=record['b'],
                                       occ=record['occ'])
            graph.add_edge(curr_resnum, curr_atom, label='msra')
            nid_atnum_mapping[record['atnum']] = curr_atom

    graph.root = curr_model

    return graph


def write_pdb(graph, atom_format=write_column_format):
    """
    Export a Model-Segment-Residue-Atom (MSRA) graph structure as
    RCSB Protein Data Bank (PDB) structure file

    PDB ATOM and HETATM lines are formatted using the `atom_format` string
    formatter using Python's keyword based format() mini-language.

    :param graph:        Graph to export
    :type graph:         :graphit:graph
    :param atom_format:  String formater for ATOM/HETATM lines
    :type atom_format:   :py:str

    :return:             RCSB PDB string
    :rtype:              :py:str
    """

    key = graph.data.key_tag
    models = graph.query_nodes({key: 'model'})

    # Create empty file buffer
    string_buffer = StringIO()

    # Export MSRA structure. Build adjacency only once
    with graph.adjacency as adj:

        models = [models] if len(models) == 1 else list(models)
        for model in models:

            # Export models if multiple exist
            if len(models) > 1:
                string_buffer.write('MODEL {0}\n'.format(model.id))

            hetatm = []
            segments = model.children().query_nodes({key: 'segment'})
            for segid, segment in sorted(segments.items()):
                seg_dict = segment.nodes[segment.nid]

                residues = segment.children(parent=model.nid).query_nodes({key: 'residue'})
                for resnum, residue in sorted(residues.items(keystring='resnum')):
                    res_dict = residue.nodes[residue.nid]

                    atoms = residue.children(parent=segment.nid).query_nodes(lambda k,v: v[key] in ('atom', 'hetatm'))
                    for atom_nid in atoms.nodes:

                        line_dict = {}
                        line_dict.update(seg_dict)
                        line_dict.update(res_dict)
                        line_dict.update(graph.nodes[atom_nid])

                        # Format atom coordinates from list
                        line_dict['xcoor'], line_dict['ycoor'], line_dict['zcoor'] = line_dict['coord']

                        # Replace all None values by strings
                        for k in line_dict.keys():
                            if line_dict[k] is None:
                                line_dict[k] = ''

                        if line_dict[key] == 'hetatm':
                            hetatm.append(atom_format.format(**line_dict))
                        else:
                            string_buffer.write(atom_format.format(**line_dict))

                # Multiple segment closing record
                if len(segments) > 1 and not line_dict[key] == 'hetatm':
                    string_buffer.write('TER\n')

            # Export HETATM records
            for htm in hetatm:
                string_buffer.write(htm)

            # Export CONECT statements
            conected = graph.query_edges({u'label': u'conect'})
            if conected:
                conected.masked = True
                source_mapping = dict([(value['atnum'], key) for key, value in conected.nodes.items()])
                for source in sorted(source_mapping.keys()):
                    neighbors = conected.neighbors(node=source_mapping[source])
                    string_buffer.write('CONECT {0} {1}\n'.format(source,
                                                        ' '.join([str(i['atnum']) for i in neighbors.nodes.values()])))

            # Model closing record
            if len(models) > 1:
                string_buffer.write('ENDMDL\n'.format(model.id))

        # Structure closing record
        string_buffer.write('END\n')

    # Reset buffer cursor
    string_buffer.seek(0)
    return string_buffer.read()
