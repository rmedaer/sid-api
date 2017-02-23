"""
This module contains helpers to do HTTP stuff.
"""

import os
import posixpath
import json
import urlparse

from rfc7231 import accepted_content_type, available_content_type
from rfc7159 import parse_json_body
from encoder import Encoder

def join_url_path(url, *paths):
    """
    Join URL path with given one.

    Keyword arguments:
    url -- Base URL.
    additional_path -- Path to join.
    """
    scheme, loc, path, query, fragments = urlparse.urlsplit(url)
    for additional_path in paths:
        path = posixpath.join(path, additional_path)
    return urlparse.urlunsplit((scheme, loc, path, query, fragments))

def json_serializer(handler_class):
    """
    Monkey patch 'write' function of RequestHandler to encode known objects
    into JSON.

    This function MUST be used as a class decorator for RequestHandler.
    """

    def wrap_write(handler_write):
        """
        This function generate the monkey patch based on original function.
        """

        def write(self, chunk, *args, **kwargs):
            """
            Encode in JSON known objects if outgoing 'Content-Type' is 'application/json'.
            """
            # TODO What happening on encoding failure ? Do we have to handle that
            # with a HTTPError 500 ?
            if self._headers['Content-Type'] == 'application/json':
                return handler_write(self, json.dumps(chunk, cls=Encoder, sort_keys=True), *args, **kwargs)
            else:
                return handler_write(self, chunk, *args, **kwargs)

        return write

    # Monkey patch 'write' function with our decorator
    handler_class.write = wrap_write(handler_class.write)
    return handler_class

def json_error_handling(handler_class):
    """
    Monkey patch 'write_error' function of handler class to replace default
    HTML error handling by JSON format.

    This function MUST be used as a class decorator for RequestHandler.
    """

    def wrap_write_error():
        """
        This function generate the monkey patch.
        """

        def write_error(self, status_code, *args, **kwargs):
            """
            Write error replacement procedure. Analyze the HTTPError and generate
            standardize JSON content.
            """

            # Fetch error message
            _, err, _ = kwargs['exc_info']
            log_message = err.log_message if hasattr(err, 'log_message') else None

            # Complete known messages when error raised by tornado itself
            if status_code == 405 and not log_message:
                log_message = 'This method is not allowed.'
            if status_code == 500 and not log_message:
                log_message = 'An internal error occured, please contact your system administrator'

            # Send error object
            self.set_header('Content-Type', 'application/json')
            self.write({
                'code': status_code,
                'message': log_message
            })

        return write_error

    # Monkey patch 'write_error' function with our decorator
    handler_class.write_error = wrap_write_error()
    return handler_class

def is_safe_path(base, path, follow_symlinks=True):
    """
    This function check the given path and make sure it's safe.

    Keyword arguments:
    base -- Base directory
    path -- Path relative or absolute to the base
    follow_symlinks -- Define if we have to follow symlinks (default: True)
    """
    if follow_symlinks:
        return os.path.realpath(path).startswith(base)
    else:
        return os.path.abspath(path).startswith(base)
