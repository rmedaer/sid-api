# -*- coding: utf-8 -*-

""" This module implements templates tests. """

from urlparse import urljoin

import json
import pytest

from sidapi.http_server import create_app

@pytest.fixture
def app():
    """ Create app fixture for following tests """

    return create_app('tests/fixtures/gitolite/gitolite.conf')

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
