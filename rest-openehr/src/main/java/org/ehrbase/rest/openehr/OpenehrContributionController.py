import uuid
from flask import Flask, request, jsonify, make_response
from flask.views import MethodView
from werkzeug.exceptions import NotAcceptable
from your_package import ContributionService  # Adjust import as necessary
from your_package.dto import ContributionResponseData, ContributionDto  # Adjust import as necessary
from your_package.exceptions import NotAcceptableException  # Adjust import as necessary

app = Flask(__name__)

class OpenehrContributionController(MethodView):

    def __init__(self, contribution_service: ContributionService):
        self.contribution_service = contribution_service

    @app.route('/ehr/<string:ehr_id>/contribution', methods=['POST'])
    def create_contribution(self, ehr_id):
        openehr_version = request.headers.get('openEHR-VERSION')
        openehr_audit_details = request.headers.get('openEHR-AUDIT_DETAILS')
        content_type = request.headers.get('Content-Type')
        accept = request.headers.get('Accept')
        prefer = request.headers.get('Prefer')

        if not self.resolve_content_type(content_type) == 'application/json':
            raise NotAcceptable("Invalid content type, only application/json is supported")

        ehr_uuid = uuid.UUID(ehr_id)
        contribution = request.get_data(as_text=True)

        contribution_id = self.contribution_service.commit_contribution(ehr_uuid, contribution)

        uri = self.create_location_uri('EHR', str(ehr_uuid), 'CONTRIBUTION', str(contribution_id))

        header_list = ['Location', 'ETag']
        do_return_representation = 'return-representation' in prefer

        resp_data = self.build_contribution_response_data(contribution_id, ehr_uuid, accept, uri, header_list, do_return_representation)

        if do_return_representation:
            return make_response(jsonify(resp_data['response_data']), 201, resp_data['headers'])
        else:
            return make_response('', 204, resp_data['headers'])

    @app.route('/ehr/<string:ehr_id>/contribution/<string:contribution_uid>', methods=['GET'])
    def get_contribution(self, ehr_id, contribution_uid):
        openehr_version = request.headers.get('openEHR-VERSION')
        openehr_audit_details = request.headers.get('openEHR-AUDIT_DETAILS')
        accept = request.headers.get('Accept')

        ehr_uuid = uuid.UUID(ehr_id)
        contribution_uuid = uuid.UUID(contribution_uid)

        uri = self.create_location_uri('EHR', str(ehr_uuid), 'CONTRIBUTION', str(contribution_uuid))

        header_list = ['Location', 'ETag', 'Last-Modified']

        resp_data = self.build_contribution_response_data(contribution_uuid, ehr_uuid, accept, uri, header_list, True)

        return make_response(jsonify(resp_data['response_data']), 200, resp_data['headers'])

    def build_contribution_response_data(self, contribution_id, ehr_id, accept, uri, header_list, include_response_data):
        resp_headers = {}
        for header in header_list:
            if header == 'Location':
                resp_headers['Location'] = uri
            elif header == 'ETag':
                resp_headers['ETag'] = f'"{contribution_id}"'
            elif header == 'Last-Modified':
                # Mocked value for demonstration, replace with actual logic
                resp_headers['Last-Modified'] = '123124442'

        response_data = None
        if include_response_data:
            media_type = self.resolve_content_type(accept)
            resp_headers['Content-Type'] = media_type

            contribution = self.contribution_service.get_contribution(ehr_id, contribution_id)

            response_data = ContributionResponseData(
                id=str(contribution_id),
                object_references=[
                    {'key': k, 'value': v} for k, v in contribution.object_references.items()
                ],
                audit_details=contribution.audit_details
            )

        return {'response_data': response_data, 'headers': resp_headers}

    def create_location_uri(self, *args):
        return '/'.join(args)

    def resolve_content_type(self, content_type):
        return content_type

# Initialize the service and add the controller to Flask
contribution_service = ContributionService()  # Adjust initialization as necessary
app.add_url_rule('/ehr/<string:ehr_id>/contribution', view_func=OpenehrContributionController.as_view('contribution', contribution_service))
app.add_url_rule('/ehr/<string:ehr_id>/contribution/<string:contribution_uid>', view_func=OpenehrContributionController.as_view('get_contribution', contribution_service))

if __name__ == '__main__':
    app.run(debug=True)
