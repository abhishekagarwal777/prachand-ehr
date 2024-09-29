from flask import Flask, jsonify
from flask_restful import Api, Resource
from http import HTTPStatus

# Assuming appropriate imports for response data
# from your_response import AdminStatusResponseData

app = Flask(__name__)
api = Api(app)

class AdminController(Resource):
    @app.route('/admin/status', methods=['GET'])
    def get_status():
        """
        Get the status of the Admin API.
        Returns a message indicating the availability of the API and the user's permission status.
        """
        response_data = AdminStatusResponseData(
            "EHRbase Admin API available and you have permission to access it"
        )
        return jsonify(response_data), HTTPStatus.OK

# Example of registering the AdminController
def create_app():
    api.add_resource(AdminController, '/admin')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
