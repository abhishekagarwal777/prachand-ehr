from typing import Dict, Any
from flask import make_response, jsonify  # Using Flask for REST API responses
from werkzeug.http import HTTP_STATUS_CODES  # To map status codes to phrases
from http import HTTPStatus

class RestEndpointSupport:
    def __init__(self):
        # Prevent instantiation just like the private constructor in Java
        raise NotImplementedError("This class cannot be instantiated")

    @staticmethod
    def prepare_error_response(ex: Exception, message: str, headers: Dict[str, str], status: HTTPStatus):
        """
        Prepare an error response for the given exception and message.

        Args:
            ex (Exception): The exception that occurred.
            message (str): The error message to include in the response.
            headers (Dict[str, str]): Any additional headers for the response.
            status (HTTPStatus): The HTTP status to use for the response.

        Returns:
            Response: A Flask Response object with the error message, headers, and status.
        """
        # Create the response body as a dictionary (similar to the Java Map)
        body: Dict[str, Any] = {
            "error": HTTP_STATUS_CODES.get(status.value, "Unknown Error"),  # Map status to reason phrase
            "message": message
        }

        # Use Flask's make_response to create a Response object, with body, headers, and status
        response = make_response(jsonify(body), status.value)

        # Add custom headers to the response
        for key, value in headers.items():
            response.headers[key] = value

        return response
