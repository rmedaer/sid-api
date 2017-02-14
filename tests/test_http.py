# -*- coding: utf-8 -*-
# pylint: disable=C0103

""" This module implements tests for HTTP requests and responses. """

from urlparse import urljoin

import json
import pytest

from tornado.httpclient import HTTPRequest, HTTPError
from sidapi.http_server import create_app

@pytest.fixture
def app():
    """ Create app fixture for following tests """

    return create_app('tests/fixtures/gitolite/gitolite.conf')

@pytest.mark.gen_test
def test_method_not_allowed(http_client, base_url):
    """ Testing method not allowed """

    try:
        http_client.fetch(HTTPRequest(
            urljoin(base_url, '/version'),
            method='POST',
            body=''
        ))
    except HTTPError as err:
        assert err.code == 405


@pytest.mark.gen_test
def test_route_not_found(http_client, base_url):
    """ Testing route not found """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/brol')
        ))
        assert False
    except HTTPError as err:
        assert err.code == 404

@pytest.mark.gen_test
def test_invalid_accepted_content_type(http_client, base_url):
    """ Testing invalid 'Accept' header """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/version'),
            headers={
                "Accept": "invalid"
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_wrong_accepted_content_type(http_client, base_url):
    """ Testing wrong 'Accept' header """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/version'),
            headers={
                "Accept": "text/plain"
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 415

@pytest.mark.gen_test
def test_missing_content_type(http_client, base_url):
    """ Testing wrong 'Content-Type' header """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
            method='POST',
            body='This is not JSON',
            headers={
                'Content-Type': ''
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_invalid_content_type(http_client, base_url):
    """ Testing invalid 'Content-Type' header """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
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
def test_wrong_content_type(http_client, base_url):
    """ Testing wrong 'Content-Type' header """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
            method='POST',
            body='This is not JSON',
            headers={
                'Content-Type': 'text/plain'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 415

@pytest.mark.gen_test
def test_wrong_json_content(http_client, base_url):
    """ Testing wrong body """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
            method='POST',
            body='It should be json but it\'s not',
            headers={
                'Content-Type': 'application/json'
            }
        ))
        assert False
    except HTTPError as err:
        assert err.code == 400

@pytest.mark.gen_test
def test_wrong_json_schema(http_client, base_url):
    """ Testing json body """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
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
