from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from http import HTTPStatus
import uuid

# Assuming appropriate imports for services and exceptions
# from your_service import EhrService, CompositionService
# from your_exception import ObjectNotFoundException
# from your_response import AdminDeleteResponseData

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)

class AdminCompositionController(Resource):
    def __init__(self, ehr_service, composition_service):
        self.ehr_service = ehr_service
        self.composition_service = composition_service

    @app.route('/admin/ehr/<string:ehr_id>/composition/<string:composition_id>', methods=['DELETE'])
    def delete_composition(ehr_id, composition_id):
        try:
            ehr_uuid = uuid.UUID(ehr_id)

            # Check if EHR exists
            if not self.ehr_service.has_ehr(ehr_uuid):
                raise ObjectNotFoundException(
                    "Admin Composition", f"EHR with id {ehr_id} does not exist."
                )

            composition_uid = uuid.UUID(composition_id)

            self.composition_service.admin_delete(composition_uid)

            # Register the context (this is a placeholder, implement as needed)
            HttpRestContext.register(
                EHR_ID=ehr_uuid,
                COMPOSITION_ID=composition_uid,
                LOCATION=f"/admin/ehr/{ehr_id}/composition/{composition_id}"
            )

            return '', HTTPStatus.NO_CONTENT

        except ObjectNotFoundException as e:
            return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
        except Exception as e:
            return jsonify({"error": "An error occurred."}), HTTPStatus.INTERNAL_SERVER_ERROR

# Example of registering the services and adding the resource to the API
def create_app(ehr_service, composition_service):
    api.add_resource(AdminCompositionController, '/admin/ehr/<string:ehr_id>/composition/<string:composition_id>')
    return app

if __name__ == "__main__":
    # Placeholder for actual service initialization
    ehr_service = EhrService()
    composition_service = CompositionService()
    
    app = create_app(ehr_service, composition_service)
    app.run(debug=True)
