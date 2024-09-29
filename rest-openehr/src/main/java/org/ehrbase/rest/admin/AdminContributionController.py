from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
import uuid

# Assuming appropriate imports for services and exceptions
# from your_service import EhrService, ContributionService
# from your_exception import ObjectNotFoundException
# from your_response import AdminDeleteResponseData, AdminUpdateResponseData

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)

class AdminContributionController(Resource):
    def __init__(self, ehr_service, contribution_service):
        self.ehr_service = ehr_service
        self.contribution_service = contribution_service

    @app.route('/admin/ehr/<string:ehr_id>/contribution/<string:contribution_id>', methods=['PUT'])
    def update_contribution(ehr_id, contribution_id):
        ehr_uuid = uuid.UUID(ehr_id)

        # Check if EHR exists
        if not self.ehr_service.has_ehr(ehr_uuid):
            raise ObjectNotFoundException(
                "Admin Contribution", f"EHR with id {ehr_id} does not exist"
            )

        contribution_uuid = uuid.UUID(contribution_id)

        # TODO: Implement endpoint functionality for updating contribution

        # Contribution existence check will be done in services

        create_rest_context(ehr_uuid, contribution_uuid)

        return jsonify(AdminUpdateResponseData(0)), HTTPStatus.OK

    @app.route('/admin/ehr/<string:ehr_id>/contribution/<string:contribution_id>', methods=['DELETE'])
    def delete_contribution(ehr_id, contribution_id):
        ehr_uuid = uuid.UUID(ehr_id)

        # Check if EHR exists
        if not self.ehr_service.has_ehr(ehr_uuid):
            raise ObjectNotFoundException(
                "Admin Contribution", f"EHR with id {ehr_id} does not exist"
            )

        self.contribution_service.admin_delete(ehr_uuid, uuid.UUID(contribution_id))

        create_rest_context(ehr_uuid, uuid.UUID(contribution_id))

        return '', HTTPStatus.NO_CONTENT

    def create_rest_context(ehr_id, contribution_id):
        HttpRestContext.register(
            EHR_ID=ehr_id,
            LOCATION=f"/admin/ehr/{ehr_id}/contribution/{contribution_id}"
        )

# Example of registering the services and adding the resource to the API
def create_app(ehr_service, contribution_service):
    api.add_resource(AdminContributionController, '/admin/ehr/<string:ehr_id>/contribution/<string:contribution_id>')
    return app

if __name__ == "__main__":
    # Placeholder for actual service initialization
    ehr_service = EhrService()
    contribution_service = ContributionService()
    
    app = create_app(ehr_service, contribution_service)
    app.run(debug=True)
