import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from urllib.parse import quote
from uuid import UUID

# Constants
OPENEHR_AUDIT_DETAILS = "openEHR-AUDIT_DETAILS"
OPENEHR_VERSION = "openEHR-VERSION"
PREFER = "Prefer"
RETURN_MINIMAL = "return=minimal"
RETURN_REPRESENTATION = "return=representation"
CONTENT_TYPE = "Content-Type"
ACCEPT = "Accept"
REQ_CONTENT_TYPE = "Client may request content format"
REQ_ACCEPT = "Client should specify expected format"
RESP_CONTENT_TYPE_DESC = "Format of response"
LOCATION = "Location"
ETAG = "ETag"
LAST_MODIFIED = "Last-Modified"
IF_MATCH = "If-Match"

# API Resource Constants
EHR = "ehr"
EHR_STATUS = "ehr_status"
VERSIONED_EHR_STATUS = "versioned_ehr_status"
VERSIONED_COMPOSITION = "versioned_composition"
COMPOSITION = "composition"
DIRECTORY = "directory"
CONTRIBUTION = "contribution"
QUERY = "query"
DEFINITION = "definition"
TEMPLATE = "template"
API_CONTEXT_PATH = "/rest/openehr"
API_CONTEXT_PATH_WITH_VERSION = f"{API_CONTEXT_PATH}/v1"
ADMIN_API_CONTEXT_PATH = "/rest/admin"


class BaseController:
    api_context_path_with_version: str = API_CONTEXT_PATH_WITH_VERSION

    def get_context_path(self) -> str:
        # Get current context path (FastAPI's equivalent is typically the base path)
        return self.api_context_path_with_version

    def create_location_uri(self, *path_segments: str) -> str:
        """
        Returns a URI for a list of segments.
        The segments are appended to the base path and encoded to ensure safe usage in a URI.
        :param path_segments: List of segments to append to the base URL
        :return: Encoded URI
        """
        base_url = self.get_context_path()
        path = "/".join(quote(segment) for segment in path_segments)
        return f"{base_url}/{path}"

    def parse_uuid(self, uuid_string: str, error: str) -> UUID:
        """
        Helper to parse an input UUID string format.
        :param uuid_string: UUID string to parse
        :param error: Error to raise if the UUID string is invalid
        :return: Parsed UUID
        :raises HTTPException: If the given UUID string is invalid
        """
        try:
            return UUID(uuid_string)
        except ValueError:
            raise HTTPException(status_code=400, detail=error)

    def get_ehr_uuid(self, ehr_id_string: str) -> UUID:
        """
        Helper to parse a UUID from EHR id string and raises ObjectNotFound if invalid.
        :param ehr_id_string: String representation of the ehrId
        :return: UUID of ehrId
        """
        return self.extract_uuid_from_string_with_error(ehr_id_string, "ehr", "EHR not found, only UUID-type IDs are supported")

    def get_composition_versioned_object_uid_string(self, composition_uid_string: str) -> UUID:
        """
        Helper to parse a UUID from composition versioned object id string and raises ObjectNotFound if invalid.
        :param composition_uid_string: String representation of the composition versioned object
        :return: UUID of composition
        """
        return self.extract_uuid_from_string_with_error(
            composition_uid_string, COMPOSITION, "Composition not found, only UUID-type versionedObjectUids are supported"
        )

    def get_contribution_versioned_object_uid_string(self, contribution_uid_string: str) -> UUID:
        """
        Helper to parse a UUID from contribution versioned object id string and raises ObjectNotFound if invalid.
        :param contribution_uid_string: String representation of the contribution versioned object
        :return: UUID of contribution
        """
        return self.extract_uuid_from_string_with_error(
            contribution_uid_string, CONTRIBUTION, "Contribution not found, only UUID-type versionedObjectUids are supported"
        )

    def extract_uuid_from_string_with_error(self, uuid_string: str, type: str, error: str) -> UUID:
        """
        Extracts UUID from string and raises an error if invalid.
        :param uuid_string: String to convert to UUID
        :param type: Type of object being checked (used for error context)
        :param error: Error message if invalid
        :return: UUID object
        """
        try:
            return UUID(uuid_string)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"{type}: {error}")

    def extract_versioned_object_uid_from_version_uid(self, version_uid: str) -> UUID:
        """
        Extracts the UUID base from a versioned UID.
        :param version_uid: Raw versionUid in format [UUID]::[VERSION]
        :return: UUID part of the versionUid
        """
        if "::" in version_uid:
            return UUID(version_uid.split("::")[0])
        return UUID(version_uid)

    def extract_version_from_version_uid(self, version_uid: str) -> Optional[int]:
        """
        Extract the version from versionUid in format $UUID::$SYSTEM::$VERSION
        :param version_uid: Version UID in the above format
        :return: Integer version number
        :raises HTTPException: If version is zero or negative
        """
        parts = version_uid.split("::")
        if len(parts) > 2:
            version = int(parts[-1])
            if version < 1:
                raise HTTPException(status_code=400, detail="Version can't be zero or negative.")
            return version
        return None

    def resolve_content_type(self, accept_header: str, default_media_type: str = "application/json") -> str:
        """
        Resolves the Content-Type based on the Accept header. Defaults to application/json.
        :param accept_header: Accept header value
        :param default_media_type: Default media type
        :return: Resolved Content-Type
        :raises HTTPException: If the Accept header is invalid
        """
        supported_media_types = ["application/json", "application/xml"]
        if not accept_header:
            return default_media_type

        media_types = [mt.strip() for mt in accept_header.split(",")]
        for media_type in media_types:
            if media_type in supported_media_types:
                return media_type

        raise HTTPException(status_code=400, detail="Invalid Content-Type in request.")

    def decode_version_at_time(self, version_at_time_param: Optional[str]) -> Optional[datetime]:
        """
        Decodes the version_at_time parameter from ISO 8601 format.
        :param version_at_time_param: The version_at_time string to decode
        :return: Decoded datetime or None
        :raises HTTPException: If the input format is invalid
        """
        if version_at_time_param:
            try:
                return datetime.fromisoformat(version_at_time_param.replace(' ', '+')).astimezone(timezone.utc)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Value '{version_at_time_param}' is not valid. Must be in extended ISO 8601 format."
                )
        return None
