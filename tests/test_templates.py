# -*- coding: utf-8 -*-

""" This module implements templates tests. """

from urlparse import urljoin

import os
import json
import pytest

from tornado.httpclient import HTTPRequest, HTTPError
from sidapi.http_server import create_app
from .fixture import gitolite_fixture

@pytest.fixture
def app():
    """ Create app fixture for following tests """

    path = os.path.join(os.getcwd(), 'tests', 'fixtures', 'gitolite')
    admin_config = gitolite_fixture(path)

    return create_app(admin_config)

@pytest.mark.gen_test
def test_template_list(http_client, base_url):
    """ Testing template list route """

    response = yield http_client.fetch(urljoin(base_url, '/templates'))
    assert response.code == 200
    assert json.loads(response.body) == [
        {
            "name": "my-first-template",
            "rules": [
                {
                    "perm": "R",
                    "users": ["alice"]
                },
                {
                    "perm": "RW",
                    "users": ["bob"]
                },
                {
                    "perm": "C",
                    "users": ["eve"]
                }
            ]
        },
        {
            "name": "my-next-template",
            "rules": [
                {
                    "perm": "RW",
                    "users": ["alice", "bob", "eve"]
                }
            ]
        }
    ]

@pytest.mark.gen_test
def test_template_fetch_ok(http_client, base_url):
    """ Fetch a template """

    response = yield http_client.fetch(urljoin(base_url, '/templates/my-next-template'))
    assert response.code == 200
    assert json.loads(response.body) == {
        "name": "my-next-template",
        "rules": [
            {
                "perm": "RW",
                "users": ["alice", "bob", "eve"]
            }
        ]
    }

@pytest.mark.gen_test
def test_template_not_found(http_client, base_url):
    """ When a template is not found """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/templates/unknown-template'),
            method='GET',
        ))
        assert False
    except HTTPError as err:
        assert err.code == 404
