from flask import Flask, request, jsonify, Response
from uuid import UUID
from datetime import datetime
from werkzeug.exceptions import NotFound, BadRequest
from marshmallow import Schema, fields, validate

app = Flask(__name__)

# Mock services and exceptions for demonstration purposes
class InternalServerException(Exception):
    pass

class InvalidApiParameterException(Exception):
    pass

class ObjectNotFoundException(Exception):
    pass

class EhrService:
    def has_ehr(self, ehr_id):
        # Implement actual EHR validation logic
        return True

class CompositionService:
    def get_versioned_composition(self, ehr_id, versioned_compo_uid):
        # Implement fetching versioned composition
        return {"uid": versioned_compo_uid, "owner_id": "owner", "time_created": datetime.utcnow()}

    def exists(self, versioned_compo_uid):
        # Implement logic to check existence of composition
        return True

    def retrieve_template_id(self, versioned_compo_uid):
        # Return mock template ID
        return "template_id"

    def get_last_version_number(self, versioned_compo_uid):
        # Return last version number
        return 1

class ContributionService:
    def get_contribution(self, ehr_id, contribution_id):
        # Implement logic to retrieve contribution
        return {"id": contribution_id}

class SystemService:
    def get_system_id(self):
        # Return a mock system ID
        return "system_id"

# DTO classes
class VersionedCompositionDto(Schema):
    uid = fields.UUID(required=True)
    owner_id = fields.String(required=True)
    time_created = fields.String(required=True)

class OriginalVersionResponseData(Schema):
    original_version = fields.Raw(required=True)
    contribution = fields.Raw(required=True)

class RevisionHistoryResponseData(Schema):
    revision_history = fields.Raw(required=True)

# Main controller
class OpenehrVersionedCompositionController:
    def __init__(self):
        self.ehr_service = EhrService()
        self.composition_service = CompositionService()
        self.contribution_service = ContributionService()
        self.system_service = SystemService()

    def retrieve_versioned_composition_by_versioned_object_uid(self, ehr_id_string, versioned_object_uid):
        ehr_id = self.get_ehr_uuid(ehr_id_string)
        versioned_compo_uid = self.get_composition_versioned_object_uid_string(versioned_object_uid)

        self.check_for_valid_ehr_and_composition_parameter(ehr_id, versioned_compo_uid)

        versioned_composition = self.composition_service.get_versioned_composition(ehr_id, versioned_compo_uid)
        versioned_composition_dto = VersionedCompositionDto().load({
            "uid": versioned_composition["uid"],
            "owner_id": versioned_composition["owner_id"],
            "time_created": versioned_composition["time_created"].isoformat()
        })

        audit_location = self.get_location_url(versioned_compo_uid, ehr_id, 0)
        self.create_rest_context(ehr_id, versioned_compo_uid, audit_location)

        return Response(
            response=jsonify(versioned_composition_dto),
            status=200,
            mimetype='application/json'
        )

    def retrieve_versioned_composition_revision_history_by_ehr(self, ehr_id_string, versioned_object_uid):
        ehr_id = self.get_ehr_uuid(ehr_id_string)
        versioned_compo_uid = self.get_composition_versioned_object_uid_string(versioned_object_uid)

        self.check_for_valid_ehr_and_composition_parameter(ehr_id, versioned_compo_uid)

        revision_history = {"history": "mock_revision_history"}  # Mocked for demonstration

        audit_location = self.get_location_url(versioned_compo_uid, ehr_id, 0, "revision_history")
        self.create_rest_context(ehr_id, versioned_compo_uid, audit_location)

        return Response(
            response=jsonify({"revision_history": revision_history}),
            status=200,
            mimetype='application/json'
        )

    def retrieve_version_of_composition_by_version_uid(self, ehr_id_string, versioned_object_uid, version_uid):
        ehr_id = self.get_ehr_uuid(ehr_id_string)
        versioned_compo_uid = self.get_composition_versioned_object_uid_string(versioned_object_uid)

        self.check_for_valid_ehr_and_composition_parameter(ehr_id, versioned_compo_uid)

        # Additional logic for version UID matching (mocked)
        composition_version_id = version_uid.split(':')
        if composition_version_id[0] != versioned_object_uid:
            raise BadRequest("Composition parameters are not matching.")

        # Simulate fetching original version
        original_version = {"composition": "mock_composition", "contribution": "mock_contribution"}

        contribution_id = original_version['contribution']
        contribution_dto = self.contribution_service.get_contribution(ehr_id, contribution_id)

        original_version_response_data = OriginalVersionResponseData().load({
            "original_version": original_version,
            "contribution": contribution_dto
        })

        return Response(
            response=jsonify(original_version_response_data),
            status=200,
            mimetype='application/json'
        )

    def retrieve_version_of_composition_by_time(self, ehr_id_string, versioned_object_uid, version_at_time=None):
        ehr_id = self.get_ehr_uuid(ehr_id_string)
        versioned_compo_uid = self.get_composition_versioned_object_uid_string(versioned_object_uid)

        self.check_for_valid_ehr_and_composition_parameter(ehr_id, versioned_compo_uid)

        # Mocked version retrieval
        version = self.composition_service.get_last_version_number(versioned_compo_uid)

        audit_location = self.get_location_url(versioned_compo_uid, ehr_id, version)
        self.create_rest_context(ehr_id, versioned_compo_uid, audit_location)

        return Response(
            response=jsonify({"version": version}),
            status=200,
            mimetype='application/json'
        )

    def check_for_valid_ehr_and_composition_parameter(self, ehr_id, versioned_compo_uid):
        if not self.ehr_service.has_ehr(ehr_id):
            raise ObjectNotFoundException("No EHR with this ID can be found")
        if not self.composition_service.exists(versioned_compo_uid):
            raise ObjectNotFoundException("No composition with this ID can be found.")

    def create_rest_context(self, ehr_id, versioned_compo_uid, audit_location):
        # Create the REST context as per your application needs
        pass

    def get_location_url(self, versioned_object_uid, ehr_id, version, *path_segments):
        if version == 0:
            version = self.composition_service.get_last_version_number(versioned_object_uid)

        versioned_composition = f"{versioned_object_uid}::{self.system_service.get_system_id()}::{version}"
        url = f"/ehr/{ehr_id}/{versioned_composition}"

        if path_segments:
            url += '/' + '/'.join(path_segments)

        return url

    def get_ehr_uuid(self, ehr_id_string):
        return UUID(ehr_id_string)

    def get_composition_versioned_object_uid_string(self, versioned_object_uid):
        return UUID(versioned_object_uid)

controller = OpenehrVersionedCompositionController()

# Flask routes
@app.route('/ehr/<ehr_id>/versioned_composition/<versioned_object_uid>', methods=['GET'])
def get_versioned_composition(ehr_id, versioned_object_uid):
    return controller.retrieve_versioned_composition_by_versioned_object_uid(ehr_id, versioned_object_uid)

@app.route('/ehr/<ehr_id>/versioned_composition/<versioned_object_uid>/revision_history', methods=['GET'])
def get_revision_history(ehr_id, versioned_object_uid):
    return controller.retrieve_versioned_composition_revision_history_by_ehr(ehr_id, versioned_object_uid)

@app.route('/ehr/<ehr_id>/versioned_composition/<versioned_object_uid>/version/<version_uid>', methods=['GET'])
def get_version_by_uid(ehr_id, versioned_object_uid, version_uid):
    return controller.retrieve_version_of_composition_by_version_uid(ehr_id, versioned_object_uid, version_uid)

@app.route('/ehr/<ehr_id>/versioned_composition/<versioned_object_uid>/version', methods=['GET'])
def get_version_by_time(ehr_id, versioned_object_uid):
    version_at_time = request.args.get('version_at_time')
    return controller.retrieve_version_of_composition_by_time(ehr_id, versioned_object_uid, version_at_time)

if __name__ == '__main__':
    app.run(debug=True)
