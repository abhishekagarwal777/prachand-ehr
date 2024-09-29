from flask import Flask, jsonify
from flask_restful import Api, Resource
from http import HTTPStatus
import uuid

# Assuming appropriate imports for response data and services
# from your_response import AdminDeleteResponseData
# from your_service import DirectoryService
# from your_http_rest_context import HttpRestContext

app = Flask(__name__)
api = Api(app)

class AdminDirectoryController(Resource):
    @app.route('/admin/ehr/<string:ehr_id>/directory/<string:directory_id>', methods=['DELETE'])
    def delete_directory(ehr_id, directory_id):
        """
        Delete a directory specified by ehr_id and directory_id.
        Removes a complete directory tree from the database.
        """
        ehr_uuid = uuid.UUID(ehr_id)
        folder_uid = uuid.UUID(directory_id)

        HttpRestContext.register(
            EHR_ID,
            str(ehr_uuid),
            DIRECTORY_ID,
            str(folder_uid),
            HttpRestContext.LOCATION,
            f"/ehr/{ehr_id}/directory/{folder_uid}"
        )

        # Call the service to delete the directory
        directory_service.admin_delete_folder(ehr_uuid, folder_uid)

        return '', HTTPStatus.NO_CONTENT

# Example of registering the AdminDirectoryController
def create_app():
    api.add_resource(AdminDirectoryController, '/admin/ehr')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
