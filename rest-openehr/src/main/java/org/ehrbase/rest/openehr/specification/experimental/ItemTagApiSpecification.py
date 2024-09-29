from typing import List, Optional, TypeVar, Union
from uuid import UUID

from fastapi import APIRouter, Query, Body, Header, Response
from pydantic import BaseModel

# Define the ItemTagDto class based on the structure used in Java
class ItemTagDto(BaseModel):
    key: str
    value: str
    target_path: str

# ResponseEntity equivalent in Python can just be a response object in FastAPI
ResponseEntity = Response

# Define the FastAPI router
router = APIRouter()

# Type variable for item tag identifiers
ItemTagIdentifier = TypeVar('ItemTagIdentifier', str, UUID)

# --- Common Documentation ---

class ItemTagApiSpecification:
    
    @router.post("/item-tags/upsert", response_model=List[UUID], tags=["EHR_STATUS"])
    async def upsert_ehr_status_item_tags(
            openehr_version: str,
            openehr_audit_details: str,
            prefer: Optional[str] = Header(None),
            ehr_id_string: str = Query(...),
            versioned_object_uid: str = Query(...),
            item_tags: List[ItemTagDto] = Body(...)
    ) -> ResponseEntity:
        """
        Create or Update tags.
        Bulk creation/update of tags. Tags without IDs are created, those with IDs are updated.
        """
        pass  # Implementation goes here

    @router.get("/item-tags", response_model=List[ItemTagDto], tags=["EHR_STATUS"])
    async def get_ehr_status_item_tags(
            openehr_version: str,
            openehr_audit_details: str,
            ehr_id_string: str = Query(...),
            versioned_object_uid: str = Query(...),
            ids: Optional[List[str]] = Query(None),
            keys: Optional[List[str]] = Query(None)
    ) -> ResponseEntity:
        """
        Get tags.
        Returns all tags for or filters based on the given ids and/or keys.
        """
        pass  # Implementation goes here

    @router.delete("/item-tags", response_model=None, tags=["EHR_STATUS"])
    async def delete_ehr_status_item_tags(
            openehr_version: str,
            openehr_audit_details: str,
            ehr_id_string: str = Query(...),
            versioned_object_uid: str = Query(...),
            item_tags_or_uuids: List[ItemTagIdentifier] = Body(...)
    ) -> ResponseEntity:
        """
        Deletes tags.
        Deletes all tags for matching the given uuid or ItemTag.id.
        """
        pass  # Implementation goes here

    # --- COMPOSITION ---

    @router.post("/composition/item-tags/upsert", response_model=List[UUID], tags=["ITEM_TAG"])
    async def upsert_composition_item_tags(
            openehr_version: str,
            openehr_audit_details: str,
            prefer: Optional[str] = Header(None),
            ehr_id_string: str = Query(...),
            versioned_object_uid: str = Query(...),
            item_tags: List[ItemTagDto] = Body(...)
    ) -> ResponseEntity:
        """
        Create or Update tags.
        Bulk creation/update of tags. Tags without IDs are created, those with IDs are updated.
        """
        pass  # Implementation goes here

    @router.get("/composition/item-tags", response_model=List[ItemTagDto], tags=["ITEM_TAG"])
    async def get_composition_item_tags(
            openehr_version: str,
            openehr_audit_details: str,
            ehr_id_string: str = Query(...),
            versioned_object_uid: str = Query(...),
            ids: Optional[List[str]] = Query(None),
            keys: Optional[List[str]] = Query(None)
    ) -> ResponseEntity:
        """
        Get tags.
        Returns all tags for or filters based on the given ids and/or keys.
        """
        pass  # Implementation goes here

    @router.delete("/composition/item-tags", response_model=None, tags=["ITEM_TAG"])
    async def delete_composition_item_tags(
            openehr_version: str,
            openehr_audit_details: str,
            ehr_id_string: str = Query(...),
            versioned_object_uid: str = Query(...),
            item_tags_or_uuids: List[ItemTagIdentifier] = Body(...)
    ) -> ResponseEntity:
        """
        Deletes tags.
        Deletes all tags for matching the given uuid or ItemTag.id.
        """
        pass  # Implementation goes here

