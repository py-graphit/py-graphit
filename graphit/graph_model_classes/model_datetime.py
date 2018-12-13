# -*- coding: utf-8 -*-

"""
file: model_date_time.py

Graph model classes for dealing with date/time definitions
"""

import pytz
import logging

from datetime import datetime, date, time
from dateutil.parser import parse

from graphit import __module__
from graphit.graph_py2to3 import PY_STRING
from graphit.graph_mixin import NodeEdgeToolsBaseClass
from graphit.graph_exceptions import GraphitValidationError

__all__ = ['Date', 'DateTime', 'Time']
logger = logging.getLogger(__module__)


def to_datetime(value, instance):
    """
    Parse a string representation of a datetime, date or time to their
    respective Python datetime.datetime, datetime.date and datetime.time object

    :param value:    string to parse
    :param instance: datetime, date or time objects the string should represent

    :return:         Python datetime.datetime, datetime.date or datetime.time object
    """

    # If value is a datetime object, parse to string
    if isinstance(value, instance):
        return value

    # If it is a string, try parse to datetime object
    elif isinstance(value, PY_STRING):

        try:
            parsed = parse(value)
        except ValueError:
            logger.error('{0} is not a valid date-time representation')
            return

        # fix for python < 3.6
        if not parsed.tzinfo:
            parsed = parsed.replace(tzinfo=pytz.utc)

        return parsed


class DateTime(NodeEdgeToolsBaseClass):

    @staticmethod
    def now():
        """
        Return a Python datetime.datetime object representing the current
        date-time respecting local timezone.

        :rtype: :py:datetime:datetime
        """

        dt = datetime.now(tz=pytz.utc)
        return dt.replace(microsecond=(dt.microsecond // 1000) * 1000)

    def datetime(self):
        """
        Return a Python datetime object representing the stored date-time

        :rtype: :py:datetime:datetime
        """

        return to_datetime(self.get(), datetime)

    def timestamp(self):
        """
        Return a seconds since epoch timestamp

        :rtype: :py:int
        """

        dt = self.datetime()
        if dt:
            return int(dt.strftime('%s'))

    def set(self, key=None, value=None):
        """
        Set and validate an ISO string representation of a date-time instance
        in accordance to RFC 3339.
        Set to current date-time if called without arguments.
        """

        key = key or self.value_tag
        if key == self.value_tag:
            if not value:
                value = self.now()
            dt = to_datetime(value, datetime)
            if dt:
                value = dt.astimezone(pytz.utc).isoformat()
            else:
                raise GraphitValidationError('Unsupported format for date-time: {0}'.format(type(value)), self)

        self.nodes[self.nid][key] = value


class Date(NodeEdgeToolsBaseClass):

    @staticmethod
    def now():
        """
        Return a Python datetime.datetime object representing the current date.

        :rtype: :py:datetime:date
        """

        return datetime.now(tz=pytz.utc).date()

    def datetime(self):
        """
        Return a Python datetime object representing the stored date

        :rtype: :py:datetime:date
        """

        return to_datetime(self.get(), date)

    def timestamp(self):
        """
        Return a seconds since epoch timestamp

        :rtype: :py:int
        """

        dt = self.datetime()
        if dt:
            return int(dt.strftime('%s'))

    def set(self, key=None, value=None):
        """
        Set and validate an ISO string representation of a date instance
        in accordance to RFC 3339
        """

        if key == self.value_tag:
            if not value:
                value = self.now()
            dt = to_datetime(value, date)
            if dt:
                value = dt.isoformat()
            else:
                logger.error('Unsupported format for date-time {0}'.format(type(value)))
                return

        self.nodes[self.nid][key] = value


class Time(NodeEdgeToolsBaseClass):

    @staticmethod
    def now():
        """
        Return a Python datetime.datetime object representing the current
        time respecting local timezone.

        :rtype: :py:datetime:time
        """

        return datetime.now(tz=pytz.utc).time()

    def datetime(self):
        """
        Return a Python datetime object representing the stored time

        :rtype: :py:datetime:time
        """

        return to_datetime(self.get(), time)

    def timestamp(self):
        """
        Return a seconds since epoch timestamp

        :rtype: :py:int
        """

        dt = self.datetime()
        if dt:
            return int(dt.strftime('%s'))

    def set(self, key=None, value=None, **kwargs):
        """
        Set and validate an ISO string representation of a time instance
        in accordance to RFC 3339
        """

        key = key or self.value_tag
        if key == self.value_tag:
            if not value:
                value = self.now()
            dt = to_datetime(value, time)
            if dt:
                value = dt.isoformat()
            else:
                logger.error('Unsupported format for date-time {0}'.format(type(value)))
                return

        self.nodes[self.nid][key] = value
