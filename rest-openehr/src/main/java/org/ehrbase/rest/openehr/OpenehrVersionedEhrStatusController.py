from datetime import datetime
from typing import Optional, Dict, List, Callable, Any
from fastapi import APIRouter, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import UUID
import collections

# Assuming necessary services and classes are already implemented in Python equivalent
from services import EhrService, ContributionService
from models import EhrStatusDto, VersionedEhrStatusDto, OriginalVersionResponseData, RevisionHistoryResponseData, ContributionDto
from util import RmConstants

router = APIRouter(
    prefix="/api/v1/ehr/{ehr_id}/versioned_ehr_status",
    responses={404: {"description": "Not found"}},
)

REVISION_HISTORY = "revision_history"
VERSION = "version"
EHR_ID = "ehr_id"

ehr_service = EhrService()  # These would be injected dependencies in a real application
contribution_service = ContributionService()


class InvalidApiParameterException(Exception):
    pass


class ObjectNotFoundException(Exception):
    pass


def extract_version_from_version_uid(version_uid: str) -> Optional[int]:
    # Dummy implementation for version extraction
    try:
        return int(version_uid.split("::")[1])
    except (IndexError, ValueError):
        return None


def extract_versioned_object_uid_from_version_uid(version_uid: str) -> Optional[UUID]:
    # Dummy implementation for UID extraction
    try:
        return UUID(version_uid.split("::")[0])
    except (IndexError, ValueError):
        return None


def decode_version_at_time(version_at_time: str) -> Optional[datetime]:
    # Decode version time to datetime object
    try:
        return datetime.fromisoformat(version_at_time)
    except ValueError:
        return None


def create_rest_context(ehr_id: UUID, query_params: Dict[str, str], *path_segments: str):
    # Create context to hold HTTP-related details like location and parameters
    uri = f"/ehr/{ehr_id}/versioned_ehr_status"
    if path_segments:
        uri += "/" + "/".join(path_segments)
    if query_params:
        uri += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())

    HttpRestContext.register(
        EHR_ID,
        ehr_id,
        HttpRestContext.LOCATION,
        uri
    )


@router.get("/", response_model=VersionedEhrStatusDto)
def retrieve_versioned_ehr_status_by_ehr(ehr_id: UUID = Path(...)):
    create_rest_context(ehr_id, {})

    versioned_ehr_status = ehr_service.get_versioned_ehr_status(ehr_id)
    versioned_ehr_status_dto = VersionedEhrStatusDto(
        uid=versioned_ehr_status.uid,
        owner_id=versioned_ehr_status.owner_id,
        time_created=versioned_ehr_status.time_created.isoformat()
    )

    return JSONResponse(content=versioned_ehr_status_dto.dict())


@router.get("/revision_history", response_model=RevisionHistoryResponseData)
def retrieve_versioned_ehr_status_revision_history_by_ehr(ehr_id: UUID = Path(...)):
    revision_history = ehr_service.get_revision_history_of_versioned_ehr_status(ehr_id)
    create_rest_context(ehr_id, {}, REVISION_HISTORY)

    return JSONResponse(content=RevisionHistoryResponseData(revision_history=revision_history).dict())


@router.get("/version", response_model=OriginalVersionResponseData[EhrStatusDto])
def retrieve_version_of_ehr_status_by_time(
    ehr_id: UUID = Path(...),
    version_at_time: Optional[str] = Query(None)
):
    if version_at_time:
        time = decode_version_at_time(version_at_time)
        if time is None:
            raise HTTPException(status_code=400, detail="Invalid version_at_time format")
        object_version_id = ehr_service.get_ehr_status_version_by_timestamp(ehr_id, time)
        context_params = {"version_at_time": version_at_time}
    else:
        object_version_id = ehr_service.get_latest_version_uid_of_status(ehr_id)
        context_params = {}

    version = extract_version_from_version_uid(object_version_id.value)
    if version is None:
        raise HTTPException(status_code=400, detail="Invalid version UID format")

    ehr_status_id = extract_versioned_object_uid_from_version_uid(object_version_id.value)

    return retrieve_version_of_ehr_status(
        ehr_id, ehr_status_id, version, lambda version_id: create_rest_context(ehr_id, context_params, VERSION)
    )


@router.get("/version/{version_uid}", response_model=OriginalVersionResponseData[EhrStatusDto])
def retrieve_version_of_ehr_status_by_version_uid(
    ehr_id: UUID = Path(...),
    version_uid: str = Path(...)
):
    try:
        ehr_status_id = extract_versioned_object_uid_from_version_uid(version_uid)
        version = extract_version_from_version_uid(version_uid)
        if version is None:
            raise ValueError("No version found")
    except Exception as e:
        raise InvalidApiParameterException(f"VERSION UID parameter has wrong format: {str(e)}")

    return retrieve_version_of_ehr_status(
        ehr_id, ehr_status_id, version, lambda version_id: create_rest_context(ehr_id, {}, VERSION, str(version_id))
    )


def retrieve_version_of_ehr_status(
    ehr_id: UUID, ehr_status_id: UUID, version: int, init_context: Callable[[UUID], None]
) -> JSONResponse:
    HttpRestContext.register(VERSION, version)

    original_version = ehr_service.get_ehr_status_at_version(ehr_id, ehr_status_id, version)
    if original_version is None:
        raise ObjectNotFoundException(f"Couldn't retrieve EhrStatus with given parameters")

    contribution_ref = original_version.contribution
    contribution_id = UUID(contribution_ref.id.value)

    contribution_dto = contribution_service.get_contribution(ehr_id, contribution_id)

    original_version_response_data = OriginalVersionResponseData(
        original_version=original_version, contribution=contribution_dto
    )
    init_context(original_version_response_data.version_id)

    return JSONResponse(content=original_version_response_data.dict())
