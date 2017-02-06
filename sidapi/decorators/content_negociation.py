
import mimeparse
from tornado.web import RequestHandler, HTTPError

def accepted_content_type(accepted):
    def accepted_content_type_decorator(func):
        def wrapper(*args, **kwargs):
            if not accepted:
               raise HTTPError(
                   status_code=500
               )

            header = args[0].request.headers.get('Content-Type')
            if not header:
               raise HTTPError(
                   status_code=400,
                   log_message='Missing \'Content-type\' header.'
               )

            try:
               content_type = mimeparse.best_match(accepted, header)
            except ValueError:
               raise HTTPError(
                   status_code=400,
                   log_message='Malformed \'Content-Type\' header.'
               )

            if not content_type:
               raise HTTPError(
                   status=415,
                   log_message='Given Content-Type is not allowed.'
               )

            return func(*args, **kwargs)
        return wrapper
    return accepted_content_type_decorator

def negociate_content_type(accepted):
    def negociate_content_type_decorator(func):
        def wrapper(*args, **kwargs):
            # If not any content_type given, it returns a internal server error
            if not accepted:
                raise HTTPError(
                    status_code=500
                )

            # Try to find best match between accepted mime types and 'Accept' header
            try:
                content_type = mimeparse.best_match(accepted, args[0].request.headers.get('Accept', '*/*'))
            except ValueError: # NOTE should be replaced by MimeTypeParseException (mimeparse >= 1.5.2)
                raise HTTPError(
                    status_code=400,
                    log_message='Malformed \'Accept\' header.'
                )

            # If not any match found, return a unsupported media type error
            if not content_type:
                raise HTTPError(
                    status_code=415,
                    log_message='Content type negociation failed. Accepted media type are unsupported.'
                )

            return func(*args, **kwargs)
        return wrapper
    return negociate_content_type_decorator
