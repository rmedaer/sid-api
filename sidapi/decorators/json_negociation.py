from json import loads
from jsonschema import validate, ValidationError
from tornado.web import HTTPError

def parse_json_body(schema=None):
    def parse_json_body_decorator(func):
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
                except ValidationError as ve:
                    raise HTTPError(
                        status_code=400,
                        log_message='JSON error: %s' % ve.message
                    )

            # Set json to current object
            args[0].json = data

            # Execute function
            return func(*args, **kwargs)
        return wrapper
    return parse_json_body_decorator
