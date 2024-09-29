from fastapi import APIRouter, Header
from fastapi.responses import Response

router = APIRouter()

class ContributionApiSpecification:
    """
    Specification for the Contribution API.
    """

    @router.post(
        "/contribution",
        summary="Create contribution",
        responses={200: {"description": "Successful creation of contribution"}},
        tags=["CONTRIBUTION"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/ehr.html#contribution-contribution-post"
            }
        }
    )
    async def create_contribution(
        openehr_version: str,
        openehr_audit_details: str,
        content_type: str = Header(...),
        accept: str = Header(...),
        prefer: str = Header(...),
        ehr_id_string: str = Header(...),
        contribution: str = Header(...)
    ) -> Response:
        """
        Create a new contribution.
        """
        pass  # Implement the functionality here

    @router.get(
        "/contribution",
        summary="Get contribution by id",
        responses={200: {"description": "Successful retrieval of contribution"}},
        tags=["CONTRIBUTION"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/ehr.html#contribution-contribution-get"
            }
        }
    )
    async def get_contribution(
        openehr_version: str,
        openehr_audit_details: str,
        accept: str = Header(...),
        ehr_id_string: str = Header(...),
        contribution_uid_string: str = Header(...)
    ) -> Response:
        """
        Get a contribution by its ID.
        """
        pass  # Implement the functionality here
