from fastapi import FastAPI, HTTPException, Request, Response, Header
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from urllib.parse import quote
import xml.etree.ElementTree as ET

app = FastAPI()

# Placeholder classes and functions for the services and DTOs
class TemplateService:
    def create(self, template):
        # Simulate template creation and return a template ID
        return "template_id_123"

    def find_operational_template(self, template_id, format):
        # Simulate fetching the operational template
        return "<operational_template>...</operational_template>"

    def get_all_templates(self):
        # Simulate fetching all templates
        return [{"id": "template_id_123", "name": "Template 1"}]

    def find_template(self, template_id):
        # Simulate fetching a template
        return {"id": template_id, "name": "Template 1"}

    def build_example(self, template_id):
        # Simulate building an example composition
        return Composition()

class CompositionService:
    def serialize(self, composition_dto, format):
        # Simulate serialization
        return {"value": "serialized_composition"}

class Composition:
    # Placeholder for Composition class
    pass

class TemplateResponseData(BaseModel):
    # Define fields as per the requirement
    pass

class TemplateMetaDataDto(BaseModel):
    id: str
    name: str

class CompositionDto:
    def __init__(self, composition, template_id, a, b):
        self.composition = composition
        self.template_id = template_id

    # Placeholder for more complex serialization logic

template_service = TemplateService()
composition_service = CompositionService()

@app.post("/api/v1/definition/template/adl1.4", status_code=201, response_class=Response)
async def create_template_classic(
    openehr_version: Optional[str] = Header(None),
    openehr_audit_details: Optional[str] = Header(None),
    prefer: Optional[str] = Header(None),
    request_body: str = None
):
    try:
        # Parse the incoming XML template
        root = ET.fromstring(request_body)
        template_id = template_service.create(root)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    headers = {
        "Location": f"/api/v1/definition/template/adl1.4/{template_id}",
        "ETag": f'"{template_id}"',
        "Last-Modified": "123124442"  # Placeholder for actual last modified timestamp
    }

    if prefer == "return-representation":
        response_template = template_service.find_operational_template(template_id, "XML")
        return Response(content=response_template, media_type="application/xml", headers=headers)
    else:
        return Response(headers=headers)

@app.get("/api/v1/definition/template/adl1.4", response_model=List[TemplateMetaDataDto])
async def get_templates_classic(
    openehr_version: Optional[str] = Header(None),
    openehr_audit_details: Optional[str] = Header(None),
    accept: Optional[str] = Header(None)
):
    templates = template_service.get_all_templates()
    return JSONResponse(content=templates)

@app.get("/api/v1/definition/template/adl1.4/{template_id}", response_model=Optional[dict])
async def get_template_classic(
    openehr_version: Optional[str] = Header(None),
    openehr_audit_details: Optional[str] = Header(None),
    accept: Optional[str] = Header(None),
    template_id: str = None
):
    media_type = "application/xml" if "application/xml" in accept else "application/json"
    operational_template = template_service.find_operational_template(template_id, media_type)

    if media_type == "application/xml":
        return Response(content=operational_template, media_type="application/xml")
    else:
        web_template = template_service.find_template(template_id)
        return JSONResponse(content=web_template)

@app.get("/api/v1/definition/template/adl1.4/{template_id}/example", response_model=str)
async def get_template_example(
    accept: Optional[str] = Header(None),
    template_id: str = None,
    format: Optional[str] = None
):
    composition = template_service.build_example(template_id)
    composition_dto = CompositionDto(composition, template_id, None, None)
    serialized = composition_service.serialize(composition_dto, format)
    return JSONResponse(content=serialized)

@app.get("/api/v1/definition/template/adl1.4/{template_id}/webtemplate", response_model=dict)
async def get_web_template(
    accept: Optional[str] = Header(None),
    template_id: str = None
):
    media_type = "application/json" if "application/json" in accept else "application/json"
    web_template = template_service.find_template(template_id)

    link_prefix = f"{app.root_path}/swagger-ui/index.html?urls.primaryName=1.%20openEHR%20API#"
    headers = {
        "Link": f'<{link_prefix}/template/getWebTemplate>; rel="deprecation"; type="text/html", <{link_prefix}/adl1.4/template/getTemplateClassic>; rel="successor-version"',
        "Deprecated": "Mon, 03 Jun 2024 00:00:00 GMT"
    }

    return JSONResponse(content=web_template, headers=headers)

# ADL 2 endpoints are not implemented
@app.post("/api/v1/definition/template/adl2", status_code=501)
async def create_template_new():
    raise HTTPException(status_code=501, detail="Not Implemented")

@app.get("/api/v1/definition/template/adl2", status_code=501)
async def get_templates_new():
    raise HTTPException(status_code=501, detail="Not Implemented")

@app.get("/api/v1/definition/template/adl2/{template_id}/{version_pattern}", status_code=501)
async def get_template_new():
    raise HTTPException(status_code=501, detail="Not Implemented")
