from typing import List, Type
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from pydantic import BaseModel

class SecurityProperties(BaseModel):
    class AccessType:
        ADMIN_ONLY = "ADMIN_ONLY"
        PRIVATE = "PRIVATE"
        PUBLIC = "PUBLIC"

    management_endpoints_access_type: str = AccessType.ADMIN_ONLY

class SecurityConfig:
    def __init__(self, app: FastAPI, web_endpoint_properties: dict, access_type: str):
        self.app = app
        self.web_endpoint_properties = web_endpoint_properties
        self.access_type = access_type
        self.logger = self.setup_logger()

    def setup_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def configure_http_security(self, http_security: Type[BaseHTTPMiddleware]) -> None:
        # Example implementation - adjust according to your needs
        if self.access_type == SecurityProperties.AccessType.ADMIN_ONLY:
            self.app.add_middleware(BaseHTTPMiddleware, dispatch=self.admin_only_middleware)
        elif self.access_type == SecurityProperties.AccessType.PRIVATE:
            self.app.add_middleware(BaseHTTPMiddleware, dispatch=self.private_access_middleware)
        elif self.access_type == SecurityProperties.AccessType.PUBLIC:
            self.app.add_middleware(BaseHTTPMiddleware, dispatch=self.public_access_middleware)
        else:
            raise ValueError("Invalid access type")

    async def admin_only_middleware(self, request: Request, call_next):
        self.logger.info("Management endpoint access type %s", self.access_type)
        # Implement your admin-only logic here
        response = await call_next(request)
        return response

    async def private_access_middleware(self, request: Request, call_next):
        self.logger.info("Management endpoint access type %s", self.access_type)
        # Implement your private access logic here
        response = await call_next(request)
        return response

    async def public_access_middleware(self, request: Request, call_next):
        self.logger.info("Management endpoint access type %s", self.access_type)
        # Implement your public access logic here
        response = await call_next(request)
        return response

# Example usage
app = FastAPI()
web_endpoint_properties = {"base_path": "/management"}

# Initialize SecurityConfig with the desired access type
security_config = SecurityConfig(app, web_endpoint_properties, SecurityProperties.AccessType.ADMIN_ONLY)
security_config.configure_http_security(BaseHTTPMiddleware)

# Define your API routes here
@app.get("/management/secure-endpoint")
async def secure_endpoint():
    return {"message": "This is a secure endpoint"}
