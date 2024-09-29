from fastapi import APIRouter, Query
from fastapi.responses import Response
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

# Define the response data models based on your application's requirements
class TemplateResponseData(BaseModel):
    # Define fields for TemplateResponseData based on your API response
    pass

class TemplateMetaDataDto(BaseModel):
    # Define fields for TemplateMetaDataDto based on your API response
    pass

class WebTemplate(BaseModel):
    # Define fields for WebTemplate based on your API response
    pass

class TemplateApiSpecification:
    """
    OpenAPI specification for openEHR REST API TEMPLATE resource.
    """

    @router.post(
        "/template/adl1.4/upload",
        summary="Upload a template",
        responses={
            200: {
                "description": "Template uploaded successfully.",
                "content": {
                    "application/json": {
                        "schema": {"type": "string"}
                    }
                }
            }
        },
        tags=["ADL 1.4 TEMPLATE"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/definition.html#tag/ADL1.4/operation/definition_template_adl1.4_upload"
            }
        }
    )
    async def create_template_classic(
        openehr_version: str = Query(...),
        openehr_audit_details: str = Query(...),
        prefer: Optional[str] = Query(None),
        template: str = Query(...)
    ) -> str:
        """
        Upload a template.
        """
        pass  # Implement the functionality here

    @router.get(
        "/template/adl1.4/list",
        summary="List templates",
        responses={
            200: {
                "description": "List of templates.",
                "model": List[TemplateMetaDataDto]
            }
        },
        tags=["ADL 1.4 TEMPLATE"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/definition.html#tag/ADL1.4/operation/definition_template_adl1.4_list"
            }
        }
    )
    async def get_templates_classic(
        openehr_version: str = Query(...),
        openehr_audit_details: str = Query(...),
        accept: str = Query(...)
    ) -> List[TemplateMetaDataDto]:
        """
        List templates.
        """
        pass  # Implement the functionality here

    @router.get(
        "/template/adl1.4/get",
        summary="Get template",
        responses={
            200: {
                "description": "Template retrieved successfully.",
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    }
                }
            }
        },
        tags=["ADL 1.4 TEMPLATE"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/definition.html#tag/ADL1.4/operation/definition_template_adl1.4_get"
            }
        }
    )
    async def get_template_classic(
        openehr_version: str = Query(...),
        openehr_audit_details: str = Query(...),
        accept: str = Query(...),
        template_id: str = Query(...)
    ) -> Any:
        """
        Get template.
        """
        pass  # Implement the functionality here

    @router.get(
        "/template/example",
        summary="Get an example composition for the specified template",
        responses={
            200: {
                "description": "Example composition retrieved successfully.",
                "content": {
                    "application/json": {
                        "schema": {"type": "string"}
                    }
                }
            }
        },
        tags=["ADL 1.4 TEMPLATE"]
    )
    async def get_template_example(
        accept: str = Query(...),
        template_id: str = Query(...),
        format: str = Query(..., description="Composition format", enum=["JSON", "XML", "STRUCTURED", "FLAT"])
    ) -> str:
        """
        Get an example composition for the specified template.
        """
        pass  # Implement the functionality here

    @router.post(
        "/template/adl2/upload",
        summary="Upload a template",
        responses={
            200: {
                "description": "Template uploaded successfully.",
                "model": TemplateResponseData
            }
        },
        tags=["ADL 2 TEMPLATE"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/definition.html#tag/ADL2/operation/definition_template_adl2_upload"
            }
        }
    )
    async def create_template_new(
        openehr_version: str = Query(...),
        openehr_audit_details: str = Query(...),
        content_type: str = Query(...),
        accept: str = Query(...),
        prefer: Optional[str] = Query(None),
        version: Optional[str] = Query(None),
        template: str = Query(...)
    ) -> TemplateResponseData:
        """
        Upload a template.
        """
        pass  # Implement the functionality here

    @router.get(
        "/template/adl2/get",
        summary="List templates",
        responses={
            200: {
                "description": "List of templates.",
                "model": TemplateResponseData
            }
        },
        tags=["ADL 2 TEMPLATE"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/definition.html#tag/ADL2/operation/definition_template_adl2_get"
            }
        }
    )
    async def get_templates_new(
        openehr_version: str = Query(...),
        openehr_audit_details: str = Query(...),
        accept: str = Query(...)
    ) -> TemplateResponseData:
        """
        List templates.
        """
        pass  # Implement the functionality here

    @router.get(
        "/template/adl2/get",
        summary="Get template",
        responses={
            200: {
                "description": "Template retrieved successfully.",
                "model": TemplateResponseData
            }
        },
        tags=["ADL 2 TEMPLATE"],
        openapi_extra={
            "externalDocs": {
                "url": "https://specifications.openehr.org/releases/ITS-REST/latest/definitions.html#definitions-stored-query-get-1"
            }
        }
    )
    async def get_template_new(
        openehr_version: str = Query(...),
        openehr_audit_details: str = Query(...),
        accept: str = Query(...),
        template_id: str = Query(...),
        version_pattern: str = Query(...)
    ) -> TemplateResponseData:
        """
        Get template.
        """
        pass  # Implement the functionality here

    @router.get(
        "/template/get",
        summary="Deprecated since 2.2.0 and marked for removal",
        description="Replaced by [/rest/openehr/v1/definition/template/adl1.4/{template_id}](./index.html?urls.primaryName=1.%20openEHR%20API#/ADL%201.4%20TEMPLATE/getTemplateClassic)",
        tags=["TEMPLATE"],
        responses={
            200: {
                "description": "Template retrieved successfully.",
                "model": WebTemplate
            }
        }
    )
    async def get_web_template(
        accept: str = Query(...),
        template_id: str = Query(...)
    ) -> WebTemplate:
        """
        Get a web template.
        """
        pass  # Implement the functionality here
