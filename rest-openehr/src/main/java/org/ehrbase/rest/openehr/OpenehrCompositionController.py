from fastapi import FastAPI, HTTPException, Depends, Header, Path, Query, Request
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List, Callable
from datetime import datetime
from some_module import CompositionService, SystemService, InternalResponse, CompositionResponseData, CompositionDto

app = FastAPI()

class CompositionRepresentation:
    media_type: str
    format: str

class OpenehrCompositionController:

    def __init__(self, composition_service: CompositionService, system_service: SystemService):
        self.composition_service = composition_service
        self.system_service = system_service

    @app.post("/{ehr_id}/composition", status_code=201)
    async def create_composition(
        self,
        ehr_id: str,
        composition: str,
        content_type: str = Header(...),
        accept: Optional[str] = Header(None),
        prefer: Optional[str] = Header(None),
        template_id: Optional[str] = Query(None),
        format: Optional[str] = Query(None),
    ):
        ehr_uuid = self.get_ehr_uuid(ehr_id)
        request_representation = self.extract_composition_representation(content_type, format)
        response_representation = self.extract_composition_representation(accept, format)

        compo_obj = self.composition_service.build_composition(composition, request_representation.format, template_id)
        composition_uuid = await self.composition_service.create(ehr_uuid, compo_obj)

        if composition_uuid is None:
            raise HTTPException(status_code=500, detail="Failed to create composition")

        uri = self.create_location_uri("EHR", ehr_uuid, "COMPOSITION", composition_uuid)
        header_list = ["LOCATION", "ETAG", "LAST_MODIFIED"]

        resp_data = await self.build_composition_response_data(
            ehr_uuid, composition_uuid, 1, response_representation, uri, header_list,
            lambda: CompositionResponseData(None, None) if prefer == "RETURN_REPRESENTATION" else None
        )

        return resp_data

    @app.put("/{ehr_id}/composition/{versioned_object_uid}")
    async def update_composition(
        self,
        ehr_id: str,
        versioned_object_uid: str,
        composition: str,
        if_match: str = Header(...),
        content_type: Optional[str] = Header(None),
        accept: Optional[str] = Header(None),
        prefer: Optional[str] = Header(None),
        template_id: Optional[str] = Query(None),
        format: Optional[str] = Query(None),
    ):
        ehr_uuid = self.get_ehr_uuid(ehr_id)
        versioned_object_uid_uuid = self.get_composition_versioned_object_uid(versioned_object_uid)

        request_representation = self.extract_composition_representation(content_type, format)
        response_representation = self.extract_composition_representation(accept, format)

        compo_obj = self.composition_service.build_composition(composition, request_representation.format, template_id)

        input_uuid = self.get_uid_from(compo_obj)
        if input_uuid and input_uuid != self.extract_versioned_object_uid(input_uuid):
            raise HTTPException(status_code=412, detail="UUID from input must match given versioned_object_uid in request URL")

        try:
            composition_version_uid = await self.composition_service.update(ehr_uuid, if_match, compo_obj)
            uri = self.create_location_uri("EHR", ehr_uuid, "COMPOSITION", composition_version_uid)

            header_list = ["LOCATION", "ETAG", "LAST_MODIFIED"]
            resp_data = await self.build_composition_response_data(
                ehr_uuid, self.extract_versioned_object_uid(composition_version_uid), 
                int(if_match.split(".")[1]) + 1, response_representation, uri, header_list,
                lambda: CompositionResponseData(None, None) if prefer == "RETURN_REPRESENTATION" else None
            )
            return resp_data
        except ObjectNotFoundException:
            raise HTTPException(status_code=404, detail="Composition not found")

    @app.delete("/{ehr_id}/composition/{preceding_version_uid}")
    async def delete_composition(
        self,
        ehr_id: str,
        preceding_version_uid: str,
        openehr_version: Optional[str] = Header(None),
        openehr_audit_details: Optional[str] = Header(None),
    ):
        ehr_uuid = self.get_ehr_uuid(ehr_id)
        headers = {}

        try:
            target_obj_id = preceding_version_uid
            await self.composition_service.delete(ehr_uuid, target_obj_id)

            uri = self.create_location_uri("EHR", ehr_uuid, "COMPOSITION", target_obj_id)
            headers["Location"] = uri

            return Response(status_code=204, headers=headers)
        except ObjectNotFoundException:
            raise HTTPException(status_code=404, detail="Composition not available")

    @app.get("/{ehr_id}/composition/{versioned_object_uid}")
    async def get_composition(
        self,
        ehr_id: str,
        versioned_object_uid: str,
        accept: Optional[str] = Header(None),
        format: Optional[str] = Query(None),
        version_at_time: Optional[str] = Query(None),
    ):
        ehr_uuid = self.get_ehr_uuid(ehr_id)
        response_representation = self.extract_composition_representation(accept, format)

        composition_uid = self.extract_versioned_object_uid(versioned_object_uid)
        version = self.extract_version_from_version_uid(versioned_object_uid) or await self.composition_service.get_last_version_number(composition_uid)

        if await self.composition_service.is_deleted(ehr_uuid, composition_uid, version):
            raise HTTPException(status_code=204)

        uri = self.create_location_uri("EHR", ehr_uuid, "COMPOSITION", versioned_object_uid)
        header_list = ["LOCATION", "ETAG", "LAST_MODIFIED"]

        resp_data = await self.build_composition_response_data(
            ehr_uuid, composition_uid, version, response_representation, uri, header_list,
            lambda: CompositionResponseData(None, None)
        )

        return resp_data

    async def build_composition_response_data(
        self,
        ehr_id: UUID,
        composition_id: UUID,
        version: int,
        response_representation: CompositionRepresentation,
        uri: str,
        header_list: List[str],
        factory: Callable[[], Optional[CompositionResponseData]]
    ) -> JSONResponse:
        minimal_or_representation = factory()

        resp_headers = {}
        for header in header_list:
            if header == "LOCATION":
                resp_headers["Location"] = uri
            elif header == "ETAG":
                resp_headers["ETag"] = f'"{composition_id}::{self.system_service.get_system_id()}::{version}"'
            elif header == "LAST_MODIFIED":
                resp_headers["Last-Modified"] = datetime.now().timestamp()

        template_id = None

        if minimal_or_representation:
            composition_dto = await self.composition_service.retrieve(ehr_id, composition_id, version)
            if composition_dto is None:
                raise HTTPException(status_code=404, detail="Couldn't retrieve composition")

            structured_string = await self.composition_service.serialize(composition_dto, response_representation.format)
            minimal_or_representation.value = structured_string.value
            minimal_or_representation.format = structured_string.format

            resp_headers["Content-Type"] = response_representation.media_type

        if not template_id:
            template_id = await self.composition_service.retrieve_template_id(composition_id)

        resp_headers["X-Template-ID"] = template_id
        return JSONResponse(content=minimal_or_representation, headers=resp_headers)

    def get_ehr_uuid(self, ehr_id: str) -> UUID:
        # Convert ehr_id string to UUID
        return UUID(ehr_id)

    def extract_composition_representation(self, content_type: str, format: Optional[str]) -> CompositionRepresentation:
        # Logic to extract composition representation
        return CompositionRepresentation(media_type=content_type, format=format)

    def create_location_uri(self, *args) -> str:
        # Construct URI based on provided arguments
        return f"/{'/'.join(args)}"

    def get_uid_from(self, composition) -> Optional[str]:
        return composition.uid if composition else None

    def get_composition_versioned_object_uid(self, versioned_object_uid: str) -> UUID:
        return UUID(versioned_object_uid)

    def extract_versioned_object_uid(self, versioned_object_uid: str) -> UUID:
        # Extract UUID from versioned object UID
        return UUID(versioned_object_uid.split("::")[0])

    def extract_version_from_version_uid(self, versioned_object_uid: str) -> Optional[int]:
        # Extract version number from versioned object UID
        try:
            return int(versioned_object_uid.split("::")[2])
        except (IndexError, ValueError):
            return None

controller = OpenehrCompositionController(CompositionService(), SystemService())
