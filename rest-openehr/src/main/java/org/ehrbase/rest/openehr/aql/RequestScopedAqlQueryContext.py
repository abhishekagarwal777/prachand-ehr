from flask import request
from datetime import datetime
from urllib.parse import urlparse
from your_service import StatusService  # Import your StatusService here
from your_dto import AqlQueryContext, MetaData  # Import your DTOs
from your_headers import EHRbaseHeader  # Define your headers
from your_properties import EhrbaseMetaProperty  # Define your MetaProperty

class RequestScopedAqlQueryContext(AqlQueryContext):
    def __init__(self, status_service: StatusService):
        self.generator_details_enabled = False  # Default value
        self.executed_aql_enabled = True  # Default value
        self.debugging_enabled = False  # Default value
        
        self.status_service = status_service
        self.executed_aql = None
        self.meta_properties = {}

        # Load values from environment or configuration if necessary
        # Example:
        # self.generator_details_enabled = os.getenv("EHRBASE_REST_AQL_RESPONSE_GENERATOR_DETAILS_ENABLED", "false").lower() == "true"
        # Similarly for other flags...

    def create_meta_data(self, location: str) -> MetaData:
        meta_data = MetaData()
        meta_data.created = datetime.now()
        meta_data.schema_version = OPENEHR_REST_API_VERSION
        meta_data.type = MetaData.RESULTSET

        if location:
            parsed_uri = urlparse(location)
            meta_data.href = parsed_uri.geturl()

        if self.generator_details_enabled:
            meta_data.generator = f"EHRBase/{self.status_service.get_ehrbase_version()}"

        meta_data.executed_aql = self.executed_aql

        if self.is_dry_run():
            self.set_meta_property(EhrbaseMetaProperty.DRY_RUN, True)

        for key, value in self.meta_properties.items():
            meta_data.set_additional_property(key, value)

        return meta_data

    def show_executed_aql(self) -> bool:
        return self.executed_aql_enabled

    def is_dry_run(self) -> bool:
        return self.debugging_enabled and self.is_header_true(EHRbaseHeader.AQL_DRY_RUN)

    def show_executed_sql(self) -> bool:
        return self.debugging_enabled and self.is_header_true(EHRbaseHeader.AQL_EXECUTED_SQL)

    def show_query_plan(self) -> bool:
        return self.debugging_enabled and self.is_header_true(EHRbaseHeader.AQL_QUERY_PLAN)

    def is_header_true(self, header: str) -> bool:
        header_value = request.headers.get(header)
        return header_value is not None and header_value.lower() == "true"

    def set_executed_aql(self, executed_aql: str):
        self.executed_aql = executed_aql

    def set_meta_property(self, property: EhrbaseMetaProperty, value: any):
        name = property.property_name
        if value is None:
            self.meta_properties.pop(name, None)
        else:
            self.meta_properties[name] = value
