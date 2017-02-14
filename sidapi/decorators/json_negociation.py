# -*- coding: utf-8 -*-

""" This module contains decorator which parse HTTP request body in JSON """

from json import loads
from jsonschema import validate, ValidationError, SchemaError
from tornado.web import HTTPError

def parse_json_body(schema=None):
    """ Decorate to parse HTTP body in JSON """

    # pylint: disable=C0111
    def parse_json_body_decorator(func):
        # pylint: disable=C0111
        def wrapper(*args, **kwargs):
            # Try to parse body to JSON
            try:
                data = loads(args[0].request.body)
            except ValueError:
                raise HTTPError(
                    status_code=400,
                    log_message='Unable to parse request body.'
                )

            # Validate JSON body if schema given
            if schema is not None:
                try:
                    validate(data, schema)
                except ValidationError as vlde:
                    raise HTTPError(
                        status_code=400,
                        log_message='JSON error: %s' % vlde.message
                    )
                except SchemaError:
                    # TODO log SchemaError for administrators and developpers
                    # TODO implement test... not mandatory since it's a internal
                    # validation of schemas...
                    raise HTTPError(
                        status_code=500,
                        log_message='Invalid JSON schema. '
                                    'Please contact your administrator.'
                    )

            # Set json to current object
            kwargs['json'] = data

            # Execute function
            return func(*args, **kwargs)
        return wrapper
    return parse_json_body_decorator
