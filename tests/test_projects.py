# -*- coding: utf-8 -*-

""" This module implements projects tests. """

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
def test_project_list(http_client, base_url):
    """ Testing projects list """

    response = yield http_client.fetch(urljoin(base_url, '/projects'))
    assert response.code == 200
    assert json.loads(response.body) == [
        {
            "name": "my-first-project",
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
            "name": "my-next-project",
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
    """ Fetch an existing project """

    response = yield http_client.fetch(urljoin(base_url, '/projects/my-next-project'))
    assert response.code == 200
    assert json.loads(response.body) == {
        "name": "my-next-project",
        "rules": [
            {
                "perm": "RW",
                "users": ["alice", "bob", "eve"]
            }
        ]
    }

@pytest.mark.gen_test
def test_template_fetch_not_found(http_client, base_url):
    """ Fetch a project which should not exist """

    try:
        yield http_client.fetch(urljoin(base_url, '/projects/nice-try'))
        assert False
    except HTTPError as err:
        assert err.code == 404

@pytest.mark.gen_test
def test_template_add(http_client, base_url):
    """ Add a project which alread exists """

    try:
        yield http_client.fetch(HTTPRequest(
            urljoin(base_url, '/projects'),
            method='POST',
            headers={
                'Content-Type': 'application/json'
            },
            body=json.dumps({
                'name': 'my-first-project'
            })
        ))
        assert False
    except HTTPError as err:
        assert err.code == 409
