import uuid
from urllib.parse import quote
from flask import request, jsonify, Response, url_for
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest
from typing import Optional
from functools import wraps
from datetime import datetime

# Constants from the original BaseController
API_ECIS_CONTEXT_PATH_WITH_VERSION = "/rest/ecis/v1"
COMPOSITION = "composition"

# Mocking ResponseEntity for Flask-based application
class ResponseEntity:
    @staticmethod
    def created(location):
        return Response(status=201, headers={"Location": location})

    @staticmethod
    def ok(headers=None, body=None):
        response = Response(status=200)
        if headers:
            response.headers.update(headers)
        if body:
            response.set_data(jsonify(body).get_data(as_text=True))
        return response

    @staticmethod
    def not_found(headers=None):
        response = Response(status=404)
        if headers:
            response.headers.update(headers)
        return response


# Decorator to mark deprecated methods
def deprecated(since, for_removal=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Flask-like Controller to replicate CompositionController in Python
class CompositionController(BaseController):

    def __init__(self, composition_service, system_service):
        self.composition_service = composition_service
        self.system_service = system_service

    @deprecated(since="2.0.0", for_removal=True)
    def create_composition(self, format="XML", template_id=None, ehr_id=None, content=None):
        """
        Handles POST request to create a composition.
        """
        if format in ["FLAT", "STRUCTURED", "ECISFLAT"] and not template_id:
            raise BadRequest(f"Template Id needs to be specified for format {format}")

        composition = self.composition_service.build_composition(content, format, template_id)
        composition_uuid = self.composition_service.create(ehr_id, composition)
        if not composition_uuid:
            raise InternalServerError("Failed to create composition")

        response_data = {
            "action": "CREATE",
            "compositionUid": f"{composition_uuid}::{self.system_service.get_system_id()}::1",
            "meta": self.build_meta(f"{composition_uuid}::{self.system_service.get_system_id()}::1")
        }

        return ResponseEntity.created(self.build_meta(f"{composition_uuid}").get("href"))

    @deprecated(since="2.0.0", for_removal=True)
    def get_composition(self, composition_uid, format="XML"):
        """
        Handles GET request to retrieve a composition.
        """
        identifier = self.get_composition_identifier(composition_uid)
        version = self.get_composition_version(composition_uid) if self.is_full_composition_uid(composition_uid) else None
        ehr_id = self.get_ehr_id_for_composition(identifier)

        composition_dto = self.composition_service.retrieve(ehr_id, identifier, version)
        if composition_dto:
            serialized_data = self.composition_service.serialize(composition_dto, format)
            response_data = {
                "composition": serialized_data,
                "action": "RETRIEVE",
                "format": format,
                "templateId": composition_dto.get_template_id(),
                "compositionUid": f"{composition_dto.get_uuid()}::{self.system_service.get_system_id()}::{self.composition_service.get_last_version_number(composition_dto.get_uuid())}",
                "ehrId": composition_dto.get_ehr_id(),
                "meta": self.build_meta(f"{composition_dto.get_uuid()}::{self.system_service.get_system_id()}::1")
            }

            return ResponseEntity.ok(headers=self.deprecation_headers("COMPOSITION/getComposition", "COMPOSITION/getComposition"), body=response_data)
        else:
            return ResponseEntity.not_found(headers=self.deprecation_headers("COMPOSITION/getComposition", "COMPOSITION/getComposition"))

    @deprecated(since="2.0.0", for_removal=True)
    def update_composition(self, composition_uid, format="XML", template_id=None, content=None):
        """
        Handles PUT request to update a composition.
        """
        if format in ["FLAT", "STRUCTURED", "ECISFLAT"] and not template_id:
            raise BadRequest(f"Template Id needs to be specified for format {format}")

        object_version_id = self.get_object_version_id(composition_uid)
        composition_identifier = self.get_composition_identifier(composition_uid)
        ehr_id = self.get_ehr_id_for_composition(composition_identifier)

        updated_composition = self.composition_service.build_composition(content, format, template_id)
        composition_version_uid = self.composition_service.update(ehr_id, object_version_id, updated_composition)
        if not composition_version_uid:
            raise InternalServerError("Failed to update composition")

        response_data = {
            "action": "UPDATE",
            "meta": self.build_meta(composition_version_uid)
        }
        return ResponseEntity.ok(headers=self.deprecation_headers("COMPOSITION/update", "COMPOSITION/updateComposition"), body=response_data)

    @deprecated(since="2.0.0", for_removal=True)
    def delete_composition(self, composition_uid):
        """
        Handles DELETE request to delete a composition.
        """
        object_version_id = self.get_object_version_id(composition_uid)
        composition_identifier = self.get_composition_identifier(composition_uid)
        ehr_id = self.get_ehr_id_for_composition(composition_identifier)

        self.composition_service.delete(ehr_id, object_version_id)
        response_data = {
            "action": "DELETE",
            "meta": self.build_meta("")
        }
        return ResponseEntity.ok(headers=self.deprecation_headers("COMPOSITION/delete", "COMPOSITION/deleteComposition"), body=response_data)

    # Utility methods (replicating Java helper functions)
    def build_meta(self, composition_uid):
        return {
            "href": self.create_location_uri(COMPOSITION, composition_uid)
        }

    def is_full_composition_uid(self, composition_uid):
        return "::" in composition_uid

    def get_composition_identifier(self, composition_uid):
        if self.is_full_composition_uid(composition_uid):
            return uuid.UUID(composition_uid.split("::")[0])
        return uuid.UUID(composition_uid)

    def get_composition_version(self, composition_uid):
        if "::" not in composition_uid:
            raise ValueError("UID of the composition does not contain domain and version parts")
        return int(composition_uid.split("::")[-1])

    def get_object_version_id(self, composition_uid):
        if self.is_full_composition_uid(composition_uid):
            return composition_uid
        return self.get_latest_version_id(uuid.UUID(composition_uid))

    def get_latest_version_id(self, composition_id):
        return f"{composition_id}::{self.system_service.get_system_id()}::{self.composition_service.get_last_version_number(composition_id)}"

    def get_ehr_id_for_composition(self, composition_uid):
        ehr_id = self.composition_service.get_ehr_id_for_composition(composition_uid)
        if not ehr_id:
            raise NotFound(f"Composition with id {composition_uid} does not exist")
        return ehr_id
