from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, UnsupportedMediaType, Conflict, PreconditionFailed
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Custom exceptions
class GeneralRequestProcessingException(Exception):
    pass

class InvalidApiParameterException(Exception):
    pass

class UnprocessableEntityException(Exception):
    pass

class ValidationException(Exception):
    pass

class AqlFeatureNotImplementedException(Exception):
    pass

class IllegalAqlException(Exception):
    pass

class ObjectNotFoundException(Exception):
    pass

class NotAcceptableException(Exception):
    pass

class StateConflictException(Exception):
    pass

class UnsupportedMediaTypeException(Exception):
    pass

class PreconditionFailedException(Exception):
    def __init__(self, message, url=None, current_version_uid=None):
        super().__init__(message)
        self.url = url
        self.current_version_uid = current_version_uid

# Exception handler
@app.errorhandler(Exception)
def handle_exception(ex):
    if isinstance(ex, (BadRequest, HTTPException)):
        return handle_bad_request(ex)
    elif isinstance(ex, Forbidden):
        return handle_access_denied_exception(ex)
    elif isinstance(ex, NotFound):
        return handle_object_not_found_exception(ex)
    elif isinstance(ex, NotAcceptableException):
        return handle_not_acceptable_exception(ex)
    elif isinstance(ex, StateConflictException):
        return handle_state_conflict_exception(ex)
    elif isinstance(ex, PreconditionFailedException):
        return handle_precondition_failed_exception(ex)
    elif isinstance(ex, UnsupportedMediaType):
        return handle_unsupported_media_type_exception(ex)
    else:
        return handle_uncaught_exception(ex)

def handle_bad_request(ex):
    response = {
        "error": "Bad Request",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 400

def handle_access_denied_exception(ex):
    response = {
        "error": "Forbidden",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 403

def handle_object_not_found_exception(ex):
    response = {
        "error": "Not Found",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 404

def handle_not_acceptable_exception(ex):
    response = {
        "error": "Not Acceptable",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 406

def handle_state_conflict_exception(ex):
    response = {
        "error": "Conflict",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 409

def handle_precondition_failed_exception(ex):
    headers = {}
    if ex.url and ex.current_version_uid:
        headers['ETag'] = f'"{ex.current_version_uid}"'
        headers['Location'] = ex.url

    response = {
        "error": "Precondition Failed",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 412, headers

def handle_unsupported_media_type_exception(ex):
    response = {
        "error": "Unsupported Media Type",
        "message": str(ex)
    }
    logger.warning(str(ex))
    return jsonify(response), 415

def handle_uncaught_exception(ex):
    response = {
        "error": "Internal Server Error",
        "message": "An internal error has occurred. Please contact your administrator."
    }
    logger.error(str(ex))
    return jsonify(response), 500

if __name__ == "__main__":
    app.run(debug=True)
