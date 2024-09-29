from fastapi import FastAPI
from fastapi.openapi.models import Info, License, ExternalDocumentation
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Configure OpenAPI documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="EHRbase API",
        version="v1",
        description=(
            "EHRbase implements the [official openEHR REST API](https://specifications.openehr.org/releases/ITS-REST/latest/) and "
            "a subset of the [EhrScape API](https://www.ehrscape.com/). "
            "Additionally, EHRbase provides a custom `status` heartbeat endpoint, "
            "an [Admin API](https://ehrbase.readthedocs.io/en/latest/03_development/07_admin/index.html) (if activated) "
            "and a [Status and Metrics API](https://ehrbase.readthedocs.io/en/latest/03_development/08_status_and_metrics/index.html?highlight=status) (if activated) "
            "for monitoring and maintenance. "
            "Please select the definition in the top right. "
            "Note: The openEHR REST API and the EhrScape API are documented in their official documentation, not here. Please refer to their separate documentation."
        ),
        license_info=License(name="Apache 2.0", url="https://github.com/ehrbase/ehrbase/blob/develop/LICENSE.md"),
        external_docs=ExternalDocumentation(
            description="EHRbase Documentation",
            url="https://ehrbase.readthedocs.io/"
        ),
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Define API endpoints and their paths
@app.get("/rest/openehr/**")
def open_ehr_api():
    return {"message": "openEHR API"}

@app.get("/rest/ecis/**")
def ehr_scape_api():
    return {"message": "EhrScape API"}

@app.get("/rest/status")
def status_api():
    return {"message": "EHRbase Status Endpoint"}

@app.get("/rest/admin/**")
def admin_api():
    return {"message": "EHRbase Admin API"}

@app.get("/management/**")
def actuator_api():
    return {"message": "Management API"}

# Conditional Experimental API
from fastapi import Depends
from typing import Optional

def get_path(path: Optional[str] = None):
    return path or "/rest/experimental/tags"

@app.get("/rest/experimental/tags/**", include_in_schema=True)
def experimental_api(path: str = Depends(get_path)):
    return {"message": f"Experimental API at {path}"}
