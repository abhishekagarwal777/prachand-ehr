from fastapi import FastAPI, HTTPException, Query, Header, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from uuid import UUID
from typing import Optional, List
import datetime
import json

app = FastAPI()

# Exception classes
class InvalidApiParameterException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class ObjectNotFoundException(Exception):
    def __init__(self, object_type: str, detail: str):
        self.object_type = object_type
        self.detail = detail

# Data Models
class Folder(BaseModel):
    uid: str
    name: str
    details: Optional[str] = None
    folders: List['Folder'] = []
    items: List[str] = []

class DirectoryResponseData(BaseModel):
    uid: str
    name: str
    details: Optional[str] = None
    folders: List[Folder] = []
    items: List[str] = []

# In-memory storage for example purposes
directory_service = {}

# Utility functions
def validate_version_uid(version_uid: str):
    if not version_uid:
        raise InvalidApiParameterException("A valid version UID must be provided.")

def assert_valid_path(path: Optional[str]):
    if path is not None:
        try:
            if len(path.split('/')) > 0:  # Simple validation, can be enhanced
                return
        except Exception:
            raise InvalidApiParameterException("The value of path parameter is invalid")

# Controller
@app.post("/ehr/{ehr_id}/directory", response_model=DirectoryResponseData)
async def create_directory(
    ehr_id: UUID,
    openEhrVersion: Optional[str] = Header(None),
    openEhrAuditDetails: Optional[str] = Header(None),
    content_type: str = Header(...),
    accept: str = Header("application/json"),
    prefer: str = Header("return-minimal"),
    folder: Folder = Body(...)
):
    created_folder = directory_service.get(ehr_id, folder.uid)
    if created_folder:
        raise HTTPException(status_code=400, detail="Folder already exists.")
    
    directory_service[ehr_id] = folder
    return JSONResponse(content=folder.dict(), status_code=201)

@app.put("/ehr/{ehr_id}/directory", response_model=DirectoryResponseData)
async def update_directory(
    ehr_id: UUID,
    folder_id: str = Header(...),
    content_type: str = Header(...),
    accept: str = Header("application/json"),
    prefer: str = Header("return-minimal"),
    openEhrVersion: Optional[str] = Header(None),
    openEhrAuditDetails: Optional[str] = Header(None),
    folder: Folder = Body(...)
):
    assert_valid_path(folder_id)

    if ehr_id not in directory_service:
        raise ObjectNotFoundException("directory", "Folder not found.")
    
    updated_folder = directory_service[ehr_id] = folder
    return updated_folder

@app.delete("/ehr/{ehr_id}/directory")
async def delete_directory(
    ehr_id: UUID,
    openEhrVersion: Optional[str] = Header(None),
    openEhrAuditDetails: Optional[str] = Header(None),
    folder_id: str = Header(...)
):
    assert_valid_path(folder_id)

    if ehr_id not in directory_service:
        raise ObjectNotFoundException("directory", "Folder not found.")
    
    del directory_service[ehr_id]
    return JSONResponse(status_code=204)

@app.get("/ehr/{ehr_id}/directory/{version_uid}", response_model=DirectoryResponseData)
async def get_folder_in_directory(
    ehr_id: UUID,
    version_uid: str,
    path: Optional[str] = Query(None),
    accept: str = Header("application/json")
):
    validate_version_uid(version_uid)
    assert_valid_path(path)

    folder = directory_service.get(ehr_id)
    if not folder:
        raise ObjectNotFoundException("directory", f"Folder with id {version_uid} does not exist.")

    return folder

@app.get("/ehr/{ehr_id}/directory")
async def get_folder_in_directory_version_at_time(
    ehr_id: UUID,
    version_at_time: Optional[str] = Query(None),
    path: Optional[str] = Query(None),
    accept: Optional[str] = Header("application/json")
):
    assert_valid_path(path)

    folder = directory_service.get(ehr_id)
    if not folder:
        raise ObjectNotFoundException("folder", f"The FOLDER for ehrId {ehr_id} and path {path} does not exist.")

    return folder

# Error Handling
@app.exception_handler(InvalidApiParameterException)
async def invalid_api_param_exception_handler(request, exc: InvalidApiParameterException):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail},
    )

@app.exception_handler(ObjectNotFoundException)
async def object_not_found_exception_handler(request, exc: ObjectNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail},
    )
