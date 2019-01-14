# -*- coding: utf-8 -*-

"""
file: io_json_format.py

Functions for importing OpenAPI RESTfull API definitions into a functional
API object
"""

import logging
import requests

from graphit import __module__
from graphit.graph_orm import GraphORM
from graphit.graph_io.io_pydata_format import write_pydata
from graphit.graph_axis.graph_axis_class import GraphAxis
from graphit.graph_axis.graph_axis_mixin import NodeAxisTools

__all__ = ['OpenAPIORM', 'OpenAPI']
logger = logging.getLogger(__module__)


class OpenAPI(GraphAxis):
    """
    Base Graph class for OpenAPI definition version 2.0 formally known as
    swagger version 2.0
    """

    def schemes(self):
        """
        Return supported HTTP schemes

        :rtype: :py:list
        """

        root = self.get_root()
        return root.xpath('//schemes').descendants().values()

    def list_methods(self):

        paths = self.xpath('//paths')
        return list(paths.children())

    def get_method(self, method_name):

        for method in self.list_methods():
            if method.name() == method_name:
                return method

        logging.warning('No service endpoint with name: {0}'.format(method_name))


class OpenAPIMethod(NodeAxisTools):
    """
    Service endpoint methods as defined in OpenAPI version 2.0
    """

    def name(self):
        """
        Return the name of the service endpoint
        """
        return self.get(self.key_tag).lstrip('/')

    def url(self, scheme='https'):
        """
        Build the endpoint url

        Concatenates the schema, host/server name, basePath and endpoint path
        to a valid URL.

        :return: endpoint URL
        :rtype:  :py:str
        """

        root = self.get_root()

        # Get (preferred) schema
        supported_schemes = self.schemes()
        if supported_schemes and scheme not in supported_schemes:
            scheme = supported_schemes[0]

        return '{0}://{1}{2}{3}'.format(scheme, root.host(), root.basePath(), self.get(self.key_tag))

    def http_method(self):

        method = self.children().keys()
        if len(method) > 1:
            print('More than one http method for service: {0}'.format(', '.join(method)))
        return method[0]

    def parameters(self, loc='query'):
        """
        Get endpoint parameters

        :param loc: parameters in query or path
        :return:
        """

        if loc not in ('query', 'path'):
            raise TypeError('"loc" needs to be "query" or "path", got: {0}'.format(loc))

        param_list = []
        params = self.descendants().query_nodes({self.key_tag: 'parameters'})
        for param in params:
            if loc in param.xpath('//in').values():
                param_list.append(write_pydata(param))

        return param_list

    def info(self):

        print('Service endpoint: {0}'.format(self.name()))
        print('url: {0}'.format(self.url()))
        print('http method: {0}\n'.format(self.http_method()))

        print('parameters')
        parameters = self.parameters(loc='query') + self.parameters(loc='path')
        for param in parameters:
            for description, value in param.items():
                print('  {0}: {1}'.format(description, value))
            print('')

    @classmethod
    def _process_parameters(self, params, reference):

        checked_params = {}
        for ref in reference:
            if ref['name'] in params:

                if 'enum' in ref and not reference[ref['name']] in ref['enum']:
                    logging.error('Parameter {0} should be in {1} got {2}'.format(ref['name'],
                                                                                  ref['enum'],
                                                                                  params[ref['name']]))
                    return

                checked_params[ref['name']] = params[ref['name']]

            elif ref.get('required') and not 'default' in ref:
                logging.error('Parameter {0} is required but not defined'.format(ref['name']))

            else:
                checked_params[ref['name']] = ref['required']

        return checked_params

    def call(self, **kwargs):

        query_params = self._process_parameters(kwargs, self.parameters(loc='query'))
        path_params = self._process_parameters(kwargs, self.parameters(loc='path'))
        url = self.url()
        url = url.format(**path_params)

        http_method = self.http_method()
        if http_method == 'get':
            response = requests.get(url, params=query_params)
        elif http_method == 'post':
            response = requests.post(url, params=query_params)

        status_code = str(response.status_code)
        logging.debug('Called: {0}'.format(response.url))
        logging.debug('Response in {0} with status code {1}'.format(response.elapsed, status_code))

        status_response = self.xpath('//{0}'.format(status_code))
        if not status_response.empty():
            logging.info(status_response.description)

        return response.text


OpenAPIORM = GraphORM()
OpenAPIORM.node_mapping.add(OpenAPIMethod, lambda x: x.get('key', '').startswith('/'))
