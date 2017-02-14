# -*- coding: utf-8 -*-
# pylint: disable=C0103

""" This module implements tests for HTTP requests and responses. """

from urlparse import urljoin

import json
import pytest

from tornado.httpclient import HTTPRequest, HTTPError
from tornado.web import Application
from sidapi.handlers.error import ErrorHandler
from sidapi.handlers.default import DefaultHandler
from sidapi.decorators.content_negociation import available_content_type, accepted_content_type
from sidapi.decorators.json_negociation import parse_json_body

class TestHandler(ErrorHandler):
    """ Test handler. """

    @available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        self.write(json.dumps({
            'name': 'value'
        }))

    @accepted_content_type(['application/json'])
    @available_content_type(['application/json'])
    @parse_json_body({
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            }
        },
        "required": [
            "name"
        ],
        "additionalProperties": False
    })
    def post(self, *args, **kwargs):
        self.write(json.dumps({
            'name': 'value'
        }))

    @accepted_content_type(['application/json'])
    @available_content_type(['application/json'])
    @parse_json_body({
        "type": "invalid"
    })
    def put(self, *args, **kwargs):
        pass

class InvalidContentTypeNegociation(ErrorHandler):
    """ Invalid handler. """

    @available_content_type([])
    def get(self, *args, **kwargs):
        """ Using available_content_type decorator with empty parameter """
        pass

    @accepted_content_type([])
    def post(self, *args, **kwargs):
        """ Using accepted_content_type decorator with empty parameter """
        pass

@pytest.fixture
def app():
    """ Create application fixture with testing handler. """

    return Application([
        (r"/test", TestHandler),
        (r"/invalid_content_type_negociation", InvalidContentTypeNegociation),
        (r".*", DefaultHandler)
    ])

@pytest.mark.gen_test
def test_route_not_found(http_client, base_url):
    """
    When a route is not found, server should answer with "404 - Not Found"
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/not-found')
        ))
        assert False
    except HTTPError as err:
        assert err.code == 404

@pytest.mark.gen_test
def test_method_not_allowed(http_client, base_url):
    """
    When a method is not define in handler,
    server shoud answer with "405 - Method not allowed"
    """

    try:
        http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='PATCH',
            body=''
        ))
    except HTTPError as err:
        assert err.code == 405

@pytest.mark.gen_test
def test_invalid_accept_header(http_client, base_url):
    """
    When client send invalid 'Accept' header,
    server should answer with "400 - Bad request"
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            headers={
                "Accept": "invalid"
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_asked_content_type_not_supported(http_client, base_url):
    """
    When client accepted content-type not allowed by server,
    it should anwser with error 415.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            headers={
                "Accept": "text/plain"
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 415

@pytest.mark.gen_test
def test_missing_content_type(http_client, base_url):
    """
    When client post without 'Content-Type',
    server should return error 400.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='POST',
            body='',
            headers={
                'Content-Type': ''
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_invalid_content_type(http_client, base_url):
    """
    When client post with invalid 'Content-Type',
    server should return error 400.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='POST',
            body=json.dumps({}),
            headers={
                'Content-Type': 'invalid'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_content_type_not_supported(http_client, base_url):
    """
    When client post with unsupported 'Content-Type',
    server should answer error 415.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='POST',
            body='',
            headers={
                'Content-Type': 'text/plain'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 415

@pytest.mark.gen_test
def test_invalid_json_body(http_client, base_url):
    """
    When client post with 'application/json' content_type,
    the body should be parsed in JSON otherwise server return error 400.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='POST',
            body='It should be a JSON doc but it\'s not',
            headers={
                'Content-Type': 'application/json'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_invalid_json_body_schema(http_client, base_url):
    """
    When client post JSON which is not valid according to schema,
    the server should return error 400.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='POST',
            body=json.dumps({
                "no-name": "should not be valid"
            }),
            headers={
                'Content-Type': 'application/json'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_invalid_json_schema(http_client, base_url):
    """
    When developer made a mistake in JSON schema,
    server should answer with error 500.
    """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/test'),
            method='PUT',
            body=json.dumps({
            }),
            headers={
                'Content-Type': 'application/json'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 500

@pytest.mark.gen_test
def test_no_output_content_type(http_client, base_url):
    """
    When developer made a mistake on 'available_content_type' decorator,
    server should answer with error 500.
    """
    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/invalid_content_type_negociation'),
            method='GET',
            headers={
                'Content-Type': 'application/json'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 500

@pytest.mark.gen_test
def test_no_input_content_type(http_client, base_url):
    """
    When developer made a mistake on 'accepted_content_type' decorator,
    server should answer with error 500.
    """
    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/invalid_content_type_negociation'),
            method='POST',
            body=json.dumps({}),
            headers={
                'Content-Type': 'application/json'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 500
