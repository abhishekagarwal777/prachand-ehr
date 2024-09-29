from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from typing import List

# Create FastAPI app instance
app = FastAPI()

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Basic Authentication instance
security = HTTPBasic()

# In-memory user store
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin_password"),
        "roles": ["ADMIN"]
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": pwd_context.hash("user_password"),
        "roles": ["USER"]
    }
}

# Function to authenticate users
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if user and pwd_context.verify(password, user['hashed_password']):
        return user
    return None

# Dependency to get the current user
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate_user(credentials.username, credentials.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

# Dependency to check roles
def require_role(role: str, current_user: dict = Depends(get_current_user)):
    if role not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

# Example of role-based routes
@app.get("/rest/admin/secure-endpoint")
async def secure_endpoint(current_user: dict = Depends(lambda: require_role("ADMIN"))):
    return {"message": "This is an admin endpoint"}

@app.get("/management/secure-endpoint")
async def management_endpoint(current_user: dict = Depends(lambda: require_role("USER"))):
    return {"message": "This is a management endpoint"}

@app.get("/error/any-endpoint")
async def error_endpoint():
    return {"message": "This is an error endpoint"}

# Configuration of middlewares if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
