"""
This module contains helpers to do HTTP stuff.
"""

import posixpath
from urlparse import urlsplit, urlunsplit

from rfc7231 import accepted_content_type, available_content_type
from rfc7159 import parse_json_body

def join_url_path(url, *paths):
    """
    Join URL path with given one.

    Keyword arguments:
    url -- Base URL.
    additional_path -- Path to join.
    """
    scheme, loc, path, query, fragments = urlsplit(url)
    for additional_path in paths:
        path = posixpath.join(path, additional_path)
    return urlunsplit((scheme, loc, path, query, fragments))
