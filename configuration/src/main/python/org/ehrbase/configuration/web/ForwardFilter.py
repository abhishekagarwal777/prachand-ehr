from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.forwarded import ForwardedHeaderMiddleware
from starlette.middleware.forwarded import ForwardedMiddleware
from fastapi import FastAPI

class CustomForwardedHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Initialize any additional properties if needed

    async def dispatch(self, request, call_next):
        # Custom processing for forwarded headers if needed
        response = await call_next(request)
        return response

# Define the FastAPI application with custom middleware
app = FastAPI(
    middleware=[
        Middleware(CustomForwardedHeaderMiddleware),
        Middleware(ForwardedHeaderMiddleware)
    ]
)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# To run the application, use: uvicorn filename:app --reload
