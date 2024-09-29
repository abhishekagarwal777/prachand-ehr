from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Union
import logging

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CustomException(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Bad Request", "message": str(exc)},
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning(f"Pydantic validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Bad Request", "message": str(exc)},
    )

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error(f"Custom error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Custom Error", "message": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "An internal error has occurred. Please contact your administrator."},
    )

@app.get("/example")
async def example_endpoint():
    raise CustomException(detail="This is a custom exception", status_code=418)  # Example usage

# Define other endpoints as needed
