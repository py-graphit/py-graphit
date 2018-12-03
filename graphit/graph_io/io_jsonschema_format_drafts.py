# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018
# Author:  Marc van Dijk (marcvdijk@gmail.com)
# file: io_jsonschema_format_drafts.py

"""
Classes representing JSON Schema draft version as specified by
http://json-schema.org.
"""

import re

from graphit.graph_axis.graph_axis_mixin import NodeAxisTools
from graphit.graph_orm import GraphORM
from graphit.graph_exceptions import GraphitValidationError
from graphit.graph_py2to3 import PY_STRING
from graphit.graph_model_classes.model_email import Email
from graphit.graph_model_classes.model_datetime import DateTime, Date, Time
from graphit.graph_model_classes.model_networking import IP4Address, IP6Address, Hostname, URI

__all__ = ['JSONSchemaORMDraft07', 'StringType', 'IntegerType', 'BooleanType', 'NumberType', 'ArrayType']


class JSONSchemaValidatorDraft07(NodeAxisTools):
    
    def schema_validate(self, value):
        
        enum = self.get('enum')
        if enum and value not in enum:
            raise GraphitValidationError('"{0}" should be of type {1}, got {2}'.format(self.get(self.key_tag),
                                                                                       repr(enum), value), self)
        
        return value
    
    def set(self, key, value=None):
        """
        Set node attribute values.
        
        :param key:   node attribute key
        :param value: node attribute value
        """
        
        if key == self.value_tag:
            value = self.schema_validate(value)
        self.nodes[self.nid][key] = value


class StringType(JSONSchemaValidatorDraft07):
    
    def set(self, key, value=None):
        
        if key == self.value_tag:
            if not isinstance(value, PY_STRING):
                raise GraphitValidationError('{0} should be of type "string" got "{1}"'.format(key, type(value)), self)
            
            value = self.schema_validate(value)
            
            # String specific validation
            length = len(value)
            if length > self.get('maxLength', length):
                raise GraphitValidationError('Length of string {0} ({1}) larger then maximum {2}'.format(value, length,
                                                                                                         self.get('maxLength')), self)
            if length < self.get('minLength', length):
                raise GraphitValidationError('Length of string {0} ({1}) smaller then minimum {2}'.format(value, length,
                                                                                                          self.get('minLength')), self)
            # Regular expression pattern matching
            if self.get('pattern'):
                pattern = re.compile(self.get('pattern'))
                if not pattern.match(value):
                    raise GraphitValidationError('String {0} does not match regex pattern {1}'.format(value,
                                                                                                      self.get('pattern')), self)
        
        self.nodes[self.nid][key] = value


class IntegerType(JSONSchemaValidatorDraft07):
    
    def set(self, key, value=None):
        
        if key == self.value_tag:
            if not isinstance(value, int):
                raise GraphitValidationError('{0} should be of type "integer" got "{1}"'.format(key, type(value)), self)
            
            value = self.schema_validate(value)
            
            # Integer specific validation
            if value > self.get('maximum', value):
                raise GraphitValidationError('{0} is larger than maximum allowed {1}'.format(value,
                                                                                             self.get('maximum')), self)
            if value >= self.get('exclusiveMaximum', value+1):
                raise GraphitValidationError('{0} is larger than maximum allowed {1}'.format(value,
                                                                                             self.get('exclusiveMaximum')), self)
            if value < self.get('minimum', value):
                raise GraphitValidationError('{0} is smaller than minimum allowed {1}'.format(value,
                                                                                              self.get('minimum')), self)
            if value <= self.get('exclusiveMinimum', value-1):
                raise GraphitValidationError('{0} is larger than minimum allowed {1}'.format(value,
                                                                                             self.get('exclusiveMinimum')), self)
            if value != 0:
                if self.get('multipleOf', value) % value != 0:
                    raise GraphitValidationError('{0} is not a multiple of {1}'.format(value,
                                                                                       self.get('multipleOf')), self)
        
        self.nodes[self.nid][key] = value


class NumberType(JSONSchemaValidatorDraft07):
    
    def set(self, key, value=None):
        
        if key == self.value_tag:
            if isinstance(value, int):
                value = float(value)

            if not isinstance(value, float):
                raise GraphitValidationError('{0} should be of type "float" got "{1}"'.format(key, type(value)), self)
            
            value = self.schema_validate(value)
            
            # Number specific validation
            if value > self.get('maximum', value):
                raise GraphitValidationError('{0} is larger than maximum allowed {1}'.format(value,
                                                                                             self.get('maximum')), self)
            if value >= self.get('exclusiveMaximum', value+1):
                raise GraphitValidationError('{0} is larger than maximum allowed {1}'.format(value,
                                                                                             self.get('exclusiveMaximum')), self)
            if value < self.get('minimum', value):
                raise GraphitValidationError('{0} is smaller than minimum allowed {1}'.format(value,
                                                                                              self.get('minimum')), self)
            if value <= self.get('exclusiveMinimum', value-1):
                raise GraphitValidationError('{0} is larger than minimum allowed {1}'.format(value,
                                                                                             self.get('exclusiveMinimum')), self)
            if value != 0:
                if self.get('multipleOf', value) % value != 0:
                    raise GraphitValidationError('{0} is not a multiple of {1}'.format(value,
                                                                                       self.get('multipleOf')), self)
        
        self.nodes[self.nid][key] = value


class BooleanType(JSONSchemaValidatorDraft07):
    
    def set(self, key, value=None):
        
        if key == self.value_tag:
            if value not in (True, False):
                raise GraphitValidationError('{0} should be of type "boolean" got "{1}"'.format(key, type(value)), self)
            
            value = self.schema_validate(value)
        
        self.nodes[self.nid][key] = value


class ArrayType(JSONSchemaValidatorDraft07):
    
    def set(self, key, value=None):
        
        if key == self.value_tag:
            if not isinstance(value, list):
                raise GraphitValidationError('{0} should be of type "array" got "{1}"'.format(key, type(value)), self)
            
            value = self.schema_validate(value)
            
            # Array specific validation
            length = len(value)
            if length > self.get('maxItems', length):
                raise GraphitValidationError('Length of array {0} ({1}) larger then maximum {2}'.format(key, length,
                                                                                                        self.get('maxItems')), self)
            if length < self.get('minItems', length):
                raise GraphitValidationError('Length of array {0} ({1}) smaller then minimum {2}'.format(key, length,
                                                                                                         self.get('minItems')), self)
            if self.get('uniqueItems', False):
                if len(set(value)) > 1:
                    raise GraphitValidationError('Items in array {0} must be unique, got: {1}'.format(key,
                                                                                                      set(value)), self)
        
        self.nodes[self.nid][key] = value


JSONSchemaORMDraft07 = GraphORM()
JSONSchemaORMDraft07.node_mapping.add(StringType, lambda x: x.get('type') == 'string')
JSONSchemaORMDraft07.node_mapping.add(IntegerType, lambda x: x.get('type') == 'integer')
JSONSchemaORMDraft07.node_mapping.add(NumberType, lambda x: x.get('type') == 'number')
JSONSchemaORMDraft07.node_mapping.add(BooleanType, lambda x: x.get('type') == 'boolean')
JSONSchemaORMDraft07.node_mapping.add(ArrayType, lambda x: x.get('type') == 'array')
JSONSchemaORMDraft07.node_mapping.add(Email, lambda x: x.get('type') == 'email')
JSONSchemaORMDraft07.node_mapping.add(Email, lambda x: x.get('type') == 'idn-email')
JSONSchemaORMDraft07.node_mapping.add(DateTime, lambda x: x.get('type') == 'date-time')
JSONSchemaORMDraft07.node_mapping.add(Date, lambda x: x.get('type') == 'date')
JSONSchemaORMDraft07.node_mapping.add(Time, lambda x: x.get('type') == 'time')
JSONSchemaORMDraft07.node_mapping.add(IP4Address, lambda x: x.get('type') == 'ipv4')
JSONSchemaORMDraft07.node_mapping.add(IP6Address, lambda x: x.get('type') == 'ipv6')
JSONSchemaORMDraft07.node_mapping.add(Hostname, lambda x: x.get('type') == 'hostname')
JSONSchemaORMDraft07.node_mapping.add(Hostname, lambda x: x.get('type') == 'idn-hostname')
JSONSchemaORMDraft07.node_mapping.add(URI, lambda x: x.get('type') == 'uri')
