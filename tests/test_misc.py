# -*- coding: utf-8 -*-

""" This module implements miscellaneous tests. """

from urlparse import urljoin

import json
import pytest

from sidapi import __version__
from sidapi.http_server import create_app

@pytest.fixture
def app():
    """ Create app fixture for following tests """

    return create_app('tests/fixtures/gitolite/gitolite.conf')

@pytest.mark.gen_test
def test_version(http_client, base_url):
    """ Testing version route """

    response = yield http_client.fetch(urljoin(base_url, '/version'))
    assert response.code == 200
    assert json.loads(response.body) == dict(
        version=__version__
    )
