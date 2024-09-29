import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI
import logging

# Set up logging configuration (adjust as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        # Attach the trace ID to the request's state
        request.state.trace_id = trace_id

        # Log the trace ID for the current request
        logger.info(f"Set traceId {trace_id} for current request")

        response = await call_next(request)
        return response

# Define the FastAPI application with custom middleware
app = FastAPI(
    middleware=[
        Middleware(LoggingContextMiddleware)
    ]
)

@app.get("/")
async def read_root(request: Request):
    # Access the trace ID from the request state
    trace_id = getattr(request.state, 'trace_id', None)
    return {"message": "Hello World", "traceId": trace_id}

# To run the application, use: uvicorn filename:app --reload
