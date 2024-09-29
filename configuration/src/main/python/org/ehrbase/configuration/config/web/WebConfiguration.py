from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseSettings
from typing import List
import datetime
from starlette.middleware.base import BaseHTTPMiddleware

class CorsProperties(BaseSettings):
    allowed_origins: List[str] = []
    allowed_origin_patterns: List[str] = []
    allowed_methods: List[str] = []
    allowed_headers: List[str] = []
    exposed_headers: List[str] = []
    allow_credentials: Optional[bool] = None
    max_age: datetime.timedelta = datetime.timedelta(seconds=1800)

    def to_cors_configuration(self):
        return {
            "allow_origins": self.allowed_origins,
            "allow_origin_regex": self.allowed_origin_patterns,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
            "expose_headers": self.exposed_headers,
            "allow_credentials": self.allow_credentials,
            "max_age": self.max_age.total_seconds()
        }

class WebConfiguration:
    def __init__(self, app: FastAPI, cors_properties: CorsProperties):
        self.app = app
        self.cors_properties = cors_properties

        self.setup()

    def setup(self):
        cors_config = self.cors_properties.to_cors_configuration()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config["allow_origins"],
            allow_origin_regex=cors_config["allow_origin_regex"],
            allow_methods=cors_config["allow_methods"],
            allow_headers=cors_config["allow_headers"],
            expose_headers=cors_config["expose_headers"],
            allow_credentials=cors_config["allow_credentials"],
            max_age=cors_config["max_age"]
        )

        # Register custom converters, similar to Spring's FormatterRegistry
        # (e.g., date/time converters) if needed

# Usage
cors_properties = CorsProperties()  # Load from environment or configuration
app = FastAPI()
web_config = WebConfiguration(app, cors_properties)
