from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from http import HTTPStatus
import logging

# Assuming appropriate imports for services and context
# from your_service import StoredQueryService
# from your_http_rest_context import HttpRestContext

app = Flask(__name__)
api = Api(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AdminQueryController(Resource):
    
    @app.route('/admin/query/<string:qualified_query_name>/<string:version>', methods=['DELETE'])
    def delete_stored_query(qualified_query_name, version):
        """
        Delete a stored query identified by qualified_query_name and version.
        """
        accept = request.headers.get('Accept')
        logger.debug("deleteStoredQuery for the following input: %s , version: %s", qualified_query_name, version)

        HttpRestContext.register(
            HttpRestContext.LOCATION,
            str(from_path("").path_segment("query", qualified_query_name, version))
        )
        
        stored_query_service.delete_stored_query(qualified_query_name, version)
        HttpRestContext.register(QUERY_ID, qualified_query_name)

        return '', HTTPStatus.OK

# Example of registering the AdminQueryController
def create_app():
    api.add_resource(AdminQueryController, '/admin/query')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
