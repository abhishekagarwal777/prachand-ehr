from flask import Flask, jsonify, request, Response
from flask_restx import Api, Resource
from typing import Optional
import platform

app = Flask(__name__)
api = Api(app, title="EHRbase API", description="Heartbeat, Version info, Status", doc="/swagger")

# Mock class for StatusResponseData to hold status information
class StatusResponseData:
    def __init__(self):
        self.jvm_version = None
        self.os_version = None
        self.postgres_version = None
        self.ehrbase_version = None
        self.open_ehr_sdk_version = None
        self.archie_version = None

    def to_dict(self):
        return {
            "jvmVersion": self.jvm_version,
            "osVersion": self.os_version,
            "postgresVersion": self.postgres_version,
            "ehrbaseVersion": self.ehrbase_version,
            "openEhrSdkVersion": self.open_ehr_sdk_version,
            "archieVersion": self.archie_version,
        }

# Mock service class for StatusService
class StatusService:
    def get_java_vm_information(self):
        return platform.java_ver()[0] or "Java VM version not available"

    def get_operating_system_information(self):
        return platform.platform()

    def get_database_information(self):
        # Placeholder: In real case, this would interact with PostgreSQL or another database
        return "PostgreSQL 13.3"

    def get_ehrbase_version(self):
        # Placeholder: Should return the actual version of EHRbase
        return "EHRbase v1.0.0"

    def get_open_ehr_sdk_version(self):
        # Placeholder: Should return the actual version of the openEHR SDK
        return "openEHR SDK v1.2.3"

    def get_archie_version(self):
        # Placeholder: Should return the actual version of Archie
        return "Archie v1.4.5"


# Flask-RESTx Namespace setup
ns = api.namespace("Status", description="Heartbeat, Version info, Status")

# Controller equivalent to the `StatusController` in Java
@ns.route("/status")
class StatusController(Resource):
    def __init__(self, *args, **kwargs):
        self.status_service = StatusService()  # Equivalent to the injected StatusService
        super().__init__(*args, **kwargs)

    @ns.doc(
        responses={200: "EHRbase is available. Basic information on runtime and build is returned in body."},
        params={"Accept": {"description": "Client desired response data format", "default": "application/json"}}
    )
    def get(self):
        """
        Get status information on running EHRbase server instance
        """
        response_data = StatusResponseData()
        # Java VM version
        response_data.jvm_version = self.status_service.get_java_vm_information()
        # OS Identifier and version
        response_data.os_version = self.status_service.get_operating_system_information()
        # Database server version
        response_data.postgres_version = self.status_service.get_database_information()
        # EHRbase version
        response_data.ehrbase_version = self.status_service.get_ehrbase_version()
        # Client SDK Version
        response_data.open_ehr_sdk_version = self.status_service.get_open_ehr_sdk_version()
        # Archie version
        response_data.archie_version = self.status_service.get_archie_version()

        # Return the response based on the `Accept` header
        accept_header = request.headers.get("Accept", "application/json")
        if accept_header == "application/xml":
            # For XML format, you'd need a custom serializer; here we return a simple string for illustration
            return Response("XML format is not implemented", mimetype="application/xml")
        else:
            # Default to JSON format
            return jsonify(response_data.to_dict())


# Route registration in Flask is handled by Flask-RESTx's `api` object

# Starting the Flask application
if __name__ == "__main__":
    app.run(debug=True)
