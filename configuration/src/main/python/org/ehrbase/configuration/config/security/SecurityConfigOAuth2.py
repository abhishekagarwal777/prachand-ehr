from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from pydantic import BaseModel
from typing import List
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI()

# OAuth2 configuration
class SecurityProperties(BaseModel):
    oauth2_user_role: str
    oauth2_admin_role: str

security_properties = SecurityProperties(
    oauth2_user_role="user_role",
    oauth2_admin_role="admin_role"
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://example.com/oauth/authorize",
    tokenUrl="https://example.com/oauth/token"
)

# Initialize and log OAuth2 settings
def initialize():
    logger.info("Using OAuth2 authentication")
    logger.debug("Using user role: %s", security_properties.oauth2_user_role)
    logger.debug("Using admin role: %s", security_properties.oauth2_admin_role)

# Call initialize function
initialize()

# Dependency to get the current user (mock implementation)
def get_current_user(token: str = Depends(oauth2_scheme)):
    # In real implementation, decode the token and validate roles
    # For example purposes, assume the token is valid and return a mock user
    return {"roles": ["user_role"]}

# OAuth2 role check dependency
def role_required(role: str):
    def role_checker(user: dict = Depends(get_current_user)):
        if role not in user["roles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {role} required"
            )
        return user
    return role_checker

@app.get("/")
async def root():
    return {"message": "Welcome to the open endpoint"}

@app.get("/rest/admin/")
async def admin_area(user: dict = Depends(role_required(security_properties.oauth2_admin_role))):
    return {"message": "Admin area"}

@app.get("/management/")
async def management_area(user: dict = Depends(role_required(security_properties.oauth2_user_role))):
    return {"message": "Management area"}

@app.get("/error/")
async def error_endpoint():
    return {"message": "This is an open error endpoint"}
