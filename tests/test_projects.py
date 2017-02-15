# -*- coding: utf-8 -*-

""" This module implements projects tests. """

from urlparse import urljoin

import os
import json
import pytest

from tornado.httpclient import HTTPRequest, HTTPError
from sid.api.http_server import create_app
from .fixture import gitolite_fixture

@pytest.fixture
def app():
    """ Create app fixture for following tests """

    path = os.path.join(os.getcwd(), 'tests', 'fixtures', 'gitolite')
    admin_config = gitolite_fixture(path)

    return create_app(admin_config)

@pytest.mark.gen_test
def test_project_list(http_client, base_url):
    """
    Try to fetch project listing.
    """

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
def test_fetch_project(http_client, base_url):
    """
    Try to fetch an existing project.
    """

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
def test_project_not_found(http_client, base_url):
    """
    When client try to get a project which doesn't exist,
    server should return an error 404.
    """

    try:
        yield http_client.fetch(urljoin(base_url, '/projects/nice-try'))
        assert False
    except HTTPError as err:
        assert err.code == 404

@pytest.mark.gen_test
def test_project_already_exist(http_client, base_url):
    """
    When client try to add a new project which already exist,
    server answer with error 409.
    """

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

@pytest.mark.gen_test
def test_add_project(http_client, base_url):
    """
    Try to add a new project.
    """

    response = yield http_client.fetch(HTTPRequest(
        urljoin(base_url, '/projects'),
        method='POST',
        headers={
            'Content-Type': 'application/json'
        },
        body=json.dumps({
            "name": "my-new-project",
            "rules": [
                {
                    "perm": "RW",
                    "users": ["alice", "bob", "eve"]
                }
            ]
        })
    ))
    assert response.code == 200
