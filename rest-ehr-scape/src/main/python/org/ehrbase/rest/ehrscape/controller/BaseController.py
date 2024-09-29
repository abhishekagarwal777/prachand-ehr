import urllib.parse
from datetime import datetime
from typing import List
from flask import request, url_for

# Mock HttpHeaders to replicate Spring functionality
class HttpHeaders(dict):
    def add(self, key, value):
        self[key] = value

# Base controller class in Python
class BaseController:
    TEMPLATE = "template"
    API_ECIS_CONTEXT_PATH_WITH_VERSION = "/rest/ecis/v1"
    COMPOSITION = "composition"

    def get_context_path(self) -> str:
        """
        Returns the current context path of the application, similar to ServletUriComponentsBuilder.
        """
        return request.host_url.rstrip("/")

    def create_location_uri(self, *path_segments: str) -> str:
        """
        Constructs a URI using the base context path and appending the provided path segments.
        Path segments are URL-encoded to ensure safe usage in a URI.
        """
        base_uri = self.get_context_path() + self.API_ECIS_CONTEXT_PATH_WITH_VERSION
        encoded_segments = [urllib.parse.quote(segment, safe='') for segment in path_segments]
        full_uri = base_uri + "/" + "/".join(encoded_segments)
        return full_uri

    SWAGGER_EHR_SCAPE_API = "swagger-ui/index.html?urls.primaryName=2.%20EhrScape%20API#"
    SWAGGER_OPENEHR_API = "swagger-ui/index.html?urls.primaryName=1.%20openEHR%20API#"

    def deprecation_headers(self, deprecated_path: str, successor_version: str) -> HttpHeaders:
        """
        Creates HTTP headers that indicate the deprecation of an API path and suggest a successor version.
        """
        headers = HttpHeaders()
        headers.add("Deprecated", "Mon, 22 Jan 2024 00:00:00 GMT")

        # Create deprecation and successor links
        links = [
            '<{}/{}{}>; rel="deprecation"; type="text/html"'.format(
                self.get_context_path(),
                self.SWAGGER_EHR_SCAPE_API,
                urllib.parse.quote(deprecated_path, encoding='ascii')
            ),
            '<{}/{}{}>; rel="successor-version"'.format(
                self.get_context_path(),
                self.SWAGGER_OPENEHR_API,
                urllib.parse.quote(successor_version, encoding='ascii')
            )
        ]
        headers.add("Link", ", ".join(links))

        # Uncomment below line when sunset date is confirmed
        # headers.add("Sunset", "Tue, 31 Dec 2024 00:00:00 GMT")

        return headers
