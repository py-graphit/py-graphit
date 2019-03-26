# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_helpers.py

import sys
import os
import unicodedata
import locale
import logging

from graphit import __module__, version
from graphit.graph_py2to3 import StringIO, urllib, urlparse, PY_STRING, to_unicode

__all__ = ['initial_node', 'resolve_root_node', 'coarse_type', 'check_graphit_version', 'open_anything',
           'FormatDetect', 'StreamReader']

logger = logging.getLogger(__module__)


def initial_node(nodes):
    """
    Return node ID of node with smallest _ID identifier.

    :param nodes: graph 'nodes' object

    :return:      node ID
    """

    minid = min([n['_id'] for n in nodes.values()])
    for node, attr in nodes.items():
        if attr['_id'] == minid:
            return node


def resolve_root_node(graph):
    """
    Resolve the node ID of the root node of the graph.

    For Graph objects there is no strict concept of a root node and by default
    the 'root' attribute of the grpah is not defined. Here, the root will
    resolve to the node nid with the smallest _id number which usually is the
    first node added when the graph was created.

    For GraphAxis object a root is essential for defining the graph hierarchy
    and thus, the graph 'root' attribute should be defined. If it is not
    defined it will also default to the node nid with the smallest _id number.
    If the user defined or default root is in the (sub)graph it is returned.
    If not, an attempt will be made to resolve it following:

    * If the graph is a single node, its node ID will be root.
    * If the graph has multiple nodes and the root is defined in the full_graph,
      return the node ID closest to the root

    :param graph: graph to resolve root node for
    :type grpah:  Graph or GraphAxis object

    :return:      root node ID
    """

    # Default graph root node
    root = graph.root or initial_node(graph.nodes())

    # If root in current (sub)graph, return
    if root in graph.nodes:
        return root

    # If one node, return as root
    if len(graph) == 1:
        return list(graph.nodes.keys())[0]

    # If multiple nodes, resolve closest to root
    if root in graph.origin.nodes():
        return initial_node(graph.nodes())


def coarse_type(n):

    if n.isdigit():
        return int(n)
    try:
        return float(n)
    except ValueError:
        return n


def check_graphit_version(file_version):
    """
    Check if the graph version of the file is (backwards) compatible with
    the current graphit module version

    :param file_version: graphit version to check
    :type file_version:  :py:str
    """

    try:
        file_version = float(file_version)
    except TypeError:
        logger.error('No valid graphit version identifier {0}'.format(file_version))
        return False

    curr_version = version(digits=2)
    if file_version > float(curr_version):
        logger.error('Graph made with a newer version of graphit {0}, you have {1}'.format(file_version, curr_version))
        return False

    return True


def open_anything(source, mode='r'):
    """
    Open input available from a file, a Python file like object, standard
    input, a URL or a string and return a uniform Python file like object
    with standard methods.

    :param source: Input as file, Python file like object, standard
                   input, URL or a string
    :type source:  mixed
    :param mode:   file access mode, defaults to 'r'
    :type mode:    string
    :return:       Python file like object
    """

    # Check if the source is a file and open
    if os.path.isfile(source):
        logger.debug('Reading file from disk {0}'.format(source))
        return open(source, mode)

    # Check if source is file already openend using 'open' or 'file' return
    if hasattr(source, 'read'):
        logger.debug('Reading file {0} from file object'.format(source.name))
        return source

    # Check if source is standard input
    if source == '-':
        logger.debug('Reading file from standard input')
        return sys.stdin

    else:
        # Check if source is a URL and try to open
        try:
            if urlparse.urlparse(source)[0] == 'http':
                result = urllib.urlopen(source)
                logger.debug("Reading file from URL with access info:\n {0}".format(result.info()))
                return result
        except IOError:
            logger.info("Unable to access URL")

        # Check if source is file and try to open else regard as string
        try:
            return open(source)
        except IOError:
            logger.debug("Unable to access as file, try to parse as string")
            return StringIO(str(source))


class StreamReader(object):
    """
    StreamReader class

    Extention of the Python file like object (io class) to read data as
    flexible streams. Enables a stream to be read by character, or block
    of characters crossing file lines.

    :param stream:  textual data that can be parsed as file-like object.
    """

    def __init__(self, stream):

        self.stream = stream
        if isinstance(stream, str):
            self.stream = StringIO(stream)

        self.has_more = True
        self.block_pos = None

        self._line = None
        self._pos = 0
        self._cursor = self.stream.tell()

    def __getitem__(self, position):
        """
        Return character(s) at position

        Accepts a Python 'slice' object.
        Restores the cursor to the position before the call to __getitem__
        was made.

        :param position:    position of characters relative to document start
        :type postion:      :py:int or slice operator

        :rtype:             :py:str
        """

        # Key is a slice object
        if isinstance(position, slice):
            return self.slice(position.start, position.stop, step=position.step)

        curpos = self.tell()
        self.stream.seek(position, 0)

        line = self.stream.readline()
        self.stream.seek(curpos, 0)

        return line[0]

    def __iter__(self):
        """
        Implement class __iter__

        Iteration managed by 'next' method
        """

        return self

    def next(self):
        """
        Iterator next method

        Returns next character in the iterations as long as there are
        characters left in the file-like object

        :raises: StopIteration, if no more characters
        """

        if self._line is None:
            self._line = self.stream.readline()
            if not self._line:
                self.has_more = False
                raise StopIteration
            self._pos = self._cursor

        pos = self._cursor - self._pos
        if pos < len(self._line):
            self._cursor += 1
            return self._line[pos]
        else:
            self._line = None
            return self.next()

    __next__ = next

    def readline(self):
        """
        Returns 'readline' method of the base file-like object
        """

        line = self.stream.readline()
        self._cursor = self.stream.tell()

        return line

    def set_cursor(self, position):
        """
        Move the file reader cursor to a new position in the file

        :param position:    position to move to
        :type position:     :py:int
        """

        self.stream.seek(position, 0)
        self._line = None
        self._pos = 0
        self._cursor = position

    def read_upto_char(self, chars, keep=False):
        """
        Return characters from active position up to a certain
        character or the first occurrence of one of multiple
        characters.

        :param chars:   character(s) to search for.
        :type chars:    :py:str, :py:list, :py:tuple
        :param keep:    keep the character to search for as part of the
                        returned string
        :type keep:     :py:bool

        :return:        tuple of text segment and termination character
        :rtype:         :py:tuple
        """

        if not isinstance(chars, (list, tuple)):
            chars = [chars]

        curpos = self.tell()
        for char in self:
            if char in chars:
                stop = self.tell()
                if not keep:
                    stop -= 1
                self.block_pos = (curpos, stop)
                return self.slice(*self.block_pos), char

        return None, None

    def read_upto_block(self, blocks, sep=(' ', '\n'), keep=False):
        """
        Return characters from active position up to a certain block of
        characters or the first occurrence of one of multiple blocks.
        A block is defined as a sequence of characters bounded by separator
        characters `sep` usually spaces and newline characters.

        :param blocks:   block(s) to search for.
        :type blocks:    :py:str, :py:list, :py:tuple
        :param sep:      block seperation characters
        :type sep:       :py:tuple, :py:list
        :param keep:     keep the block to search for as part of the
                         returned string
        :type keep:      :py:bool

        :return:         tuple of text segment and termination character
        :rtype:          :py:tuple
        """

        if not isinstance(blocks, (list, tuple)):
            blocks = [blocks]

        curpos = self.tell()
        block = []
        for char in self:
            block.append(char)
            if char in sep:
                blockj = ''.join(block).strip()
                if len(block) and blockj in blocks:
                    self._cursor -= 1
                    if not keep:
                        self._cursor -= len(block)
                    self.block_pos = (curpos, self.tell())
                    return self.slice(*self.block_pos), blockj
                else:
                    block = []

        return None, None

    def slice(self, start, stop, step=1):
        """
        Text slice method.

        Returns a segment of text defined by a start and stop character
        position relative to the start of the text.

        :param start:   start character position
        :type start:    :py:int
        :param stop:    stop character position
        :type stop:     :py:str

        :rtype:         :py:str
        """

        if stop < start:
            return ''

        curpos = self.tell()
        self.stream.seek(start, 0)

        text_slice = []
        progress = self.stream.tell()
        read = True
        while read:
            line = self.stream.readline()
            if not line:
                read = False
                break
            if stop < self.stream.tell():
                text_slice.append(line[0:stop - progress])
                read = False
            else:
                text_slice.append(line)
                progress += len(line)

        self.stream.seek(curpos, 0)

        return ''.join(text_slice)

    def tell(self):
        """
        Return current position of file cursor

        :rtype: :py:int
        """

        return self._cursor


class FormatDetect(object):
    """
    Type cast string or unicode objects to float, integer or boolean.

    Uses localization to identify

    TODO: comma separated strings fail if one comma
    """

    def __init__(self, set_locale='en_US.UTF-8', decimal_point=None, thousands_sep=None):

        # Determine current localization and switch to international
        # en_US localization or other.
        self.curr_locale = locale.getdefaultlocale()
        if self.curr_locale != set_locale:
            logger.debug('Switch localization: {0} to {1}'.format('.'.join(self.curr_locale), set_locale))
            locale.setlocale(locale.LC_ALL, set_locale)

        # Register localization specific decimal and thousands seperator
        locenv = locale.localeconv()
        self.decimal_point = decimal_point or locenv['decimal_point']
        self.thousands_sep = thousands_sep or locenv['thousands_sep']

        # Register Boolean types
        self.true_types = ['true']
        self.false_types = ['false']

    @staticmethod
    def to_integer(value):

        if isinstance(value, PY_STRING):
            return locale.atoi(value)
        return int(value)

    @staticmethod
    def to_number(value):

        if isinstance(value, (PY_STRING)):
            return locale.atof(value)
        return float(value)

    @staticmethod
    def to_string(value):

        return to_unicode(value)

    def to_boolean(self, value):

        if value.lower() in self.true_types:
            return True
        if value.lower() in self.false_types:
            return False

        return value

    def to_detect(self, value):

        # if string contains spaces or very long, return
        if ' ' in value or len(value) > 100:
            return value

        # str to unicode
        value = self.to_string(value)
        unicode_cats = [unicodedata.category(i)[0] for i in value]

        # Comma separated string
        if value.count(self.thousands_sep) > 1:
            return self.to_string(value)

        # first try to convert unicode to float
        try:
            parsed = locale.atof(value)
        except ValueError:
            parsed = value

        if isinstance(parsed, float):

            # Maybe it was an integer
            allnumbers = all([n[0] == 'N' for n in unicode_cats])
            if value.isdigit() or value.isnumeric() or allnumbers:
                parsed = locale.atoi(value)
            if value.count(self.decimal_point) == 0:
                parsed = int(parsed)

            return parsed

        # Try convert unicode to integer
        try:
            parsed = self.to_integer(value)
        except ValueError:
            parsed = value

        if not isinstance(parsed, int):

            # Cases that are fully numeric with thousand separators (e.g. 123.222.12)
            if value.count(self.decimal_point) > 1 and value.count(self.thousands_sep) == 0:
                parsed = int(value.replace(self.decimal_point, ''))

            # Unicode could be a boolean
            parsed = self.to_boolean(value)

        return parsed

    def parse(self, value, target_type=None):
        """
        Parse an unknown value to a float, integer, boolean or else
        remain in unicode.

        :param value:       value to parse
        :param target_type: type to convert to as 'integer', 'number', 'string',
                            'boolean' or automatic 'detect'
        :return:            parsed value
        """

        # target type not defined then try detect
        if not target_type:

            # if value already parsed to a type other than str or unicode return
            if not isinstance(value, PY_STRING):
                return value

            target_type = 'detect'

        parse_method = getattr(self, 'to_{0}'.format(target_type), None)
        if parse_method is None:
            raise AssertionError('Unknown type: {0}'.format(target_type))
        else:
            return parse_method(value)
