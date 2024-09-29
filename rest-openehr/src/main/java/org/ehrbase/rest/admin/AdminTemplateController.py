from flask import Flask, request, jsonify, Response
from flask_restful import Api, Resource
from http import HTTPStatus
from marshmallow import Schema, fields, validate

# Assuming appropriate imports for services and configurations
# from your_service import TemplateService
# from your_config import AdminApiConfiguration
# from your_response_dto import AdminDeleteResponseData, AdminStatusResponseData

app = Flask(__name__)
api = Api(app)

# Set up your services
template_service = TemplateService()
admin_api_configuration = AdminApiConfiguration()

class AdminTemplateController(Resource):

    @app.route('/admin/template/<string:template_id>', methods=['PUT'])
    def update_template(template_id):
        """
        Update an existing template identified by template_id with new content.
        """
        accept = request.headers.get('Accept', 'application/xml')
        content_type = request.headers.get('Content-Type')
        content = request.get_data(as_text=True)

        updated_template = template_service.admin_update_template(template_id, content)

        headers = {'Content-Type': 'application/xml'}
        return Response(updated_template, status=HTTPStatus.OK, headers=headers)

    @app.route('/admin/template/<string:template_id>', methods=['DELETE'])
    def delete_template(template_id):
        """
        Delete a template identified by template_id.
        """
        deleted = template_service.admin_delete_template(template_id)
        return jsonify(AdminDeleteResponseData(deleted)), HTTPStatus.OK

    @app.route('/admin/template/all', methods=['DELETE'])
    def delete_all_templates():
        """
        Delete all templates if allowed by configuration.
        """
        if not admin_api_configuration.allow_delete_all:
            return jsonify(AdminStatusResponseData("Delete all resources not allowed.")), HTTPStatus.METHOD_NOT_ALLOWED

        deleted = template_service.admin_delete_all_templates()
        return jsonify(AdminDeleteResponseData(deleted)), HTTPStatus.OK

# Example of registering the AdminTemplateController
def create_app():
    api.add_resource(AdminTemplateController, '/admin/template')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
