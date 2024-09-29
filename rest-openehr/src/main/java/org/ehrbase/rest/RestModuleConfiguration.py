from collections import defaultdict
from typing import Dict, Any
from urllib.parse import parse_qs
from flask import Flask, request, g
from functools import wraps

app = Flask(__name__)

# Equivalent to the @Configuration, @ComponentScan, and @EnableAspectJAutoProxy annotations
class RestModuleConfiguration:
    NONE = "none"

    def __init__(self, auth_type: str):
        self.auth_type = auth_type

    def add_interceptors(self):
        if self.auth_type.lower() == self.NONE:
            app.before_request(self.security_context_cleanup_interceptor)

    def add_formatters(self):
        app.url_map.converters['query'] = QueryParameterConverter

    @staticmethod
    def security_context_cleanup_interceptor():
        # Equivalent to SecurityContextHolder.clearContext()
        g.user = None
        return None


class QueryParameterConverter:
    # Equivalent to the QueryParameterConverter class in Java

    PARAM_ASSIGN = '='
    PARAM_DELIM = '&'

    @staticmethod
    def to_python(value: str) -> Dict[str, Any]:
        """
        Convert the string query parameter into a Python dictionary
        :param value: String query parameter like 'x=1&ehrId=b907e17a-0dc0-49ef-b126-95b9abb4f906'
        :return: Dictionary with parsed query parameters
        """
        params = parse_qs(value)
        result = defaultdict(str)

        for key, values in params.items():
            result[key] = values[0] if len(values) == 1 else values

        return result


# Flask interceptor equivalent to `HandlerInterceptor`
def interceptor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # SecurityContextCleanupInterceptor logic: equivalent to clearing security context
        g.user = None
        return f(*args, **kwargs)
    return decorated_function


# Example Flask endpoint
@app.route('/api/resource', methods=['GET'])
@interceptor
def get_resource():
    # Logic for the resource handling
    return {"message": "Resource accessed"}


# Setting up the RestModuleConfiguration
config = RestModuleConfiguration(auth_type="none")
config.add_interceptors()
config.add_formatters()

if __name__ == "__main__":
    app.run(debug=True)
