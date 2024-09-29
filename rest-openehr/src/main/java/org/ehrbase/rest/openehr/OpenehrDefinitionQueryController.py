from flask import Flask, request, jsonify, Response, make_response
from flask_restful import Resource, Api
from werkzeug.exceptions import NotAcceptable, BadRequest, UnsupportedMediaType
import json
import logging
from typing import Optional

app = Flask(__name__)
api = Api(app)

class QueryDefinitionListResponseData:
    def __init__(self, stored_queries):
        self.stored_queries = stored_queries

class QueryDefinitionResponseData:
    def __init__(self, stored_query):
        self.stored_query = stored_query

class QueryDefinitionResultDto:
    def __init__(self, qualified_name, version):
        self.qualified_name = qualified_name
        self.version = version

class StoredQueryService:
    def retrieve_stored_queries(self, qualified_query_name: Optional[str]):
        # Logic to retrieve stored queries goes here
        pass

    def retrieve_stored_query(self, qualified_query_name: str, version: Optional[str]):
        # Logic to retrieve a specific stored query goes here
        pass

    def create_stored_query(self, qualified_query_name: str, version: Optional[str], aql: str):
        # Logic to create a stored query goes here
        return QueryDefinitionResultDto(qualified_query_name, version)

class HttpRestContext:
    QUERY_ID = "query_id"
    
    @staticmethod
    def register(key: str, value: str):
        # Logic to register HTTP context information
        pass

logger = logging.getLogger(__name__)

class OpenehrDefinitionQueryController(Resource):
    AQL = "AQL"

    def __init__(self, stored_query_service: StoredQueryService):
        self.stored_query_service = stored_query_service

    def get_stored_query_list(self, qualified_query_name: Optional[str] = None):
        logger.debug(f"getStoredQueryList invoked with the following input: {qualified_query_name}")
        HttpRestContext.register(self.QUERY_ID, qualified_query_name)

        response_data = QueryDefinitionListResponseData(
            self.stored_query_service.retrieve_stored_queries(qualified_query_name)
        )
        return make_response(jsonify(response_data.__dict__), 200)

    def get_stored_query_version(self, qualified_query_name: str, version: Optional[str] = None):
        logger.debug(f"getStoredQueryVersion invoked with the following input: {qualified_query_name}, version: {version}")
        HttpRestContext.register(self.QUERY_ID, qualified_query_name)

        query_definition_response_data = QueryDefinitionResponseData(
            self.stored_query_service.retrieve_stored_query(qualified_query_name, version)
        )
        return make_response(jsonify(query_definition_response_data.__dict__), 200)

    def put_stored_query(self, qualified_query_name: str, version: Optional[str] = None):
        content_type = request.content_type
        accept = request.headers.get('Accept')
        query_payload = request.data.decode('utf-8')

        if self.AQL.lower() not in content_type.lower():
            raise NotAcceptable(f"Query type: {content_type} not supported!")

        aql = None

        if 'application/json' in content_type:
            try:
                json_payload = json.loads(query_payload)
                aql = json_payload.get("q")
            except json.JSONDecodeError:
                raise BadRequest("Invalid content format")

        elif 'text/plain' in content_type:
            aql = query_payload

        else:
            raise UnsupportedMediaType(content_type)

        if not aql:
            raise BadRequest("No AQL query provided")

        HttpRestContext.register(self.QUERY_ID, qualified_query_name)

        stored_query = self.stored_query_service.create_stored_query(qualified_query_name, version, aql)
        return self.get_put_definition_response_entity(content_type, stored_query)

    def get_put_definition_response_entity(self, media_type, stored_query):
        if 'application/json' in media_type:
            return make_response(jsonify(QueryDefinitionResponseData(stored_query).__dict__), 200)
        elif 'text/plain' in media_type:
            response = Response(status=200)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Location'] = f"/definition/query/{stored_query.qualified_name}/{stored_query.version}"
            return response
        else:
            raise BadRequest(f"Unexpected media type: {media_type}")

api.add_resource(OpenehrDefinitionQueryController, '/definition/query/<string:qualified_query_name>', 
                  '/definition/query/<string:qualified_query_name>/<string:version>', 
                  '/definition/query/<string:qualified_query_name>/<string:version>', 
                  endpoint='definition_query')

if __name__ == '__main__':
    app.run(debug=True)
