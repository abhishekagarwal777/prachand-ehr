from typing import Dict, Set, Optional
from fastapi import Depends
from fastapi_utils.context import context
from pydantic import BaseModel
from fastapi_utils.inferring_router import InferringRouter
from dependency_injector.wiring import inject, Provide

router = InferringRouter()

# This class will hold the audit result map similar to the Java class
class RequestAwareAuditResultMapHolder:
    def __init__(self):
        # Initializes an empty dictionary similar to HashMap in Java
        self.audit_result_map: Dict[str, Set[object]] = {}

    # Method to set the audit result map
    def set_audit_result_map(self, map: Optional[Dict[str, Set[object]]]):
        if map is None:
            # If map is None, assign it directly (similar to the original Java logic)
            self.audit_result_map = map
        else:
            # Otherwise, clear the map and populate it with the new data
            self.audit_result_map.clear()
            self.audit_result_map.update(map)

    # Method to get the audit result map
    def get_audit_result_map(self) -> Dict[str, Set[object]]:
        return self.audit_result_map


# Pydantic model for request body validation
class AuditResultMapRequest(BaseModel):
    audit_map: Dict[str, Set[object]]


# Dependency injection for request-scoped data
def get_audit_result_map_holder() -> RequestAwareAuditResultMapHolder:
    return context.get_request_scope_dependency(RequestAwareAuditResultMapHolder)


# API endpoint to get the current audit result map
@router.get("/audit_map", response_model=Dict[str, Set[object]])
def get_audit_result_map(
    audit_result_map_holder: RequestAwareAuditResultMapHolder = Depends(get_audit_result_map_holder)
):
    return audit_result_map_holder.get_audit_result_map()


# API endpoint to set the audit result map
@router.post("/audit_map")
def set_audit_result_map(
    audit_map_request: AuditResultMapRequest,
    audit_result_map_holder: RequestAwareAuditResultMapHolder = Depends(get_audit_result_map_holder)
):
    audit_result_map_holder.set_audit_result_map(audit_map_request.audit_map)
    return {"message": "Audit result map updated successfully"}
