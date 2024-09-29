from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from http import HTTPStatus
import uuid

# Assuming appropriate imports for response data and services
# from your_response import AdminUpdateResponseData, AdminDeleteResponseData
# from your_service import EhrService
# from your_http_rest_context import HttpRestContext
# from your_exceptions import ObjectNotFoundException

app = Flask(__name__)
api = Api(app)

class AdminEhrController(Resource):
    
    @app.route('/admin/ehr/<string:ehr_id>', methods=['PUT'])
    def update_ehr(ehr_id):
        """
        Update an EHR specified by ehr_id.
        Returns the number of updated items in the body.
        """
        accept = request.headers.get('Accept')
        ehr_uuid = uuid.UUID(ehr_id)
        
        # Check if EHR with id exists
        if not ehr_service.has_ehr(ehr_uuid):
            raise ObjectNotFoundException("Admin EHR", f"EHR with id {ehr_id} does not exist.")

        HttpRestContext.register(EHR_ID, str(ehr_uuid))
        
        # TODO: Implement the actual update functionality
        
        return jsonify(AdminUpdateResponseData(0)), HTTPStatus.OK

    @app.route('/admin/ehr/<string:ehr_id>', methods=['DELETE'])
    def delete_ehr(ehr_id):
        """
        Delete an EHR specified by ehr_id.
        """
        ehr_uuid = uuid.UUID(ehr_id)

        # Check if EHR with id exists
        if not ehr_service.has_ehr(ehr_uuid):
            raise ObjectNotFoundException("Admin EHR", f"EHR with id {ehr_id} does not exist.")

        HttpRestContext.register(EHR_ID, str(ehr_uuid), REMOVED_PATIENTS, get_patient_numbers(ehr_uuid))
        
        ehr_service.admin_delete_ehr(ehr_uuid)

        return '', HTTPStatus.NO_CONTENT

    @staticmethod
    def get_patient_numbers(*ehrs):
        return {ehr_service.get_subject_ext_ref(str(ehr_id)) for ehr_id in ehrs}

# Example of registering the AdminEhrController
def create_app():
    api.add_resource(AdminEhrController, '/admin/ehr')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
