from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
import logging
from typing import List, Optional

# Initialize logger
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for your use case
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSRF Protection (Simulated)
csrf_exempt_paths = ["/rest/", "/plugin/", "/error/"]

def csrf_protected(path: str):
    if any(path.startswith(exempt_path) for exempt_path in csrf_exempt_paths):
        return True
    # Simulate CSRF protection; in real implementations, you would check tokens or headers
    return False

# OAuth2 configuration
class SecurityProperties(BaseModel):
    oauth2_user_role: str
    oauth2_admin_role: str
    management_endpoints_csrf_validation_enabled: bool

security_properties = SecurityProperties(
    oauth2_user_role="user_role",
    oauth2_admin_role="admin_role",
    management_endpoints_csrf_validation_enabled=True
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://example.com/oauth/authorize",
    tokenUrl="https://example.com/oauth/token"
)

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

@app.middleware("http")
async def csrf_middleware(request, call_next):
    if not csrf_protected(request.url.path):
        # Simulate CSRF token check (e.g., header or form data)
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or csrf_token != "expected_token":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing or invalid"
            )
    response = await call_next(request)
    return response

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

@app.get("/plugin/")
async def plugin_area():
    return {"message": "Plugin area"}
