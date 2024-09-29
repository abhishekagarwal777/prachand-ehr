from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Clear security context equivalent (if needed)
        # This is just a placeholder. FastAPI and Starlette do not use a context like Spring Security.
        response = await call_next(request)
        return response

app = FastAPI()

# Add the middleware to the app
app.add_middleware(SecurityMiddleware)
