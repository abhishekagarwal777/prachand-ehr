from typing import List, Optional
from pydantic import BaseModel, Field
import datetime

class CorsProperties(BaseModel):
    allowed_origins: List[str] = Field(default_factory=list, alias='allowedOrigins')
    allowed_origin_patterns: List[str] = Field(default_factory=list, alias='allowedOriginPatterns')
    allowed_methods: List[str] = Field(default_factory=list, alias='allowedMethods')
    allowed_headers: List[str] = Field(default_factory=list, alias='allowedHeaders')
    exposed_headers: List[str] = Field(default_factory=list, alias='exposedHeaders')
    allow_credentials: Optional[bool] = Field(None, alias='allowCredentials')
    max_age: datetime.timedelta = Field(default=datetime.timedelta(seconds=1800), alias='maxAge')

    class Config:
        allow_population_by_field_name = True

    def to_cors_configuration(self):
        from starlette.middleware.cors import CORSMiddleware

        if not self.allowed_origins and not self.allowed_origin_patterns:
            return None

        return CORSMiddleware(
            app=None,
            allow_origins=self.allowed_origins,
            allow_origin_regex=self.allowed_origin_patterns,
            allow_methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
            expose_headers=self.exposed_headers,
            allow_credentials=self.allow_credentials,
            max_age=self.max_age.total_seconds()
        )
