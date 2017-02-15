# -*- coding: utf-8 -*-
# pylint: disable=C0103

""" This module implements tests to handle errors """

from urlparse import urljoin

import pytest

from tornado.httpclient import HTTPRequest, HTTPError
from sid.api import __version__
from sid.api.http_server import create_app

@pytest.fixture
def app():
    """ Create wrong app fixture for following tests """

    return create_app('tests/fixtures/gitolite/error')

@pytest.mark.gen_test
def test_not_available(http_client, base_url):
    """ When Pytolite config is not available """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
            method='GET'
        ))
        assert False
    except HTTPError as err:
        assert err.code == 503

@pytest.mark.gen_test
def test_not_implemented(http_client, base_url):
    """ When a route is not yet implemented """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects/my-project/settings/my-setting'),
            method='GET'
        ))
        assert False
    except HTTPError as err:
        assert err.code == 501
