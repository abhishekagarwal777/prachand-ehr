import uuid
from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import NotFound, BadRequest
from datetime import datetime

app = Flask(__name__)

# Mock services and models for EHR
class EhrService:
    class EhrResult:
        def __init__(self, status):
            self.status = status

    def create(self, ehr_id, ehr_status):
        # Simulate EHR creation
        return self.EhrResult(uuid.uuid4())

    def findBySubject(self, subject_id, subject_namespace):
        # Simulate finding EHR by subject
        return None  # Replace with actual logic to find EHR

    def getEhrStatus(self, ehr_id):
        return self.EhrResult("active")  # Replace with actual status fetching

    def getCreationTime(self, ehr_id):
        return datetime.now()  # Replace with actual creation time fetching

class SystemService:
    def getSystemId(self):
        return "system-id"  # Replace with actual system ID fetching

ehr_service = EhrService()
system_service = SystemService()

@app.route('/ehr', methods=['POST'])
def create_ehr():
    openehr_version = request.headers.get('openehr_version')
    openehr_audit_details = request.headers.get('openehr_audit_details')
    prefer = request.headers.get('Prefer', 'return-minimal')
    ehr_status = request.get_json()  # Assume JSON body is provided

    ehr_id = ehr_service.create(None, ehr_status).ehrId

    # Initialize response
    response_builder = make_response("", 201)
    response_builder.headers['Location'] = f"/ehr/{ehr_id}"
    response_builder.headers['ETag'] = f'"{ehr_id}"'

    if prefer == 'return-representation':
        ehr_response_data = ehr_response_data(ehr_id)
        return jsonify(ehr_response_data), 201
    else:
        return response_builder

@app.route('/ehr/<string:ehr_id>', methods=['PUT'])
def create_ehr_with_id(ehr_id):
    openehr_version = request.headers.get('openehr_version')
    openehr_audit_details = request.headers.get('openehr_audit_details')
    prefer = request.headers.get('Prefer')
    ehr_status = request.get_json()

    try:
        new_ehr_id = uuid.UUID(ehr_id)  # Validate and parse EHR ID
    except ValueError:
        raise BadRequest("EHR ID format not a UUID")

    ehr_id = ehr_service.create(new_ehr_id, ehr_status).ehrId

    # Initialize response
    response_builder = make_response("", 201)
    response_builder.headers['Location'] = f"/ehr/{ehr_id}"
    response_builder.headers['ETag'] = f'"{ehr_id}"'

    if prefer == 'return-representation':
        ehr_response_data = ehr_response_data(ehr_id)
        return jsonify(ehr_response_data), 201
    else:
        return response_builder

@app.route('/ehr/<string:ehr_id>', methods=['GET'])
def get_ehr_by_id(ehr_id):
    try:
        ehr_id = uuid.UUID(ehr_id)  # Validate and parse EHR ID
    except ValueError:
        raise BadRequest("EHR ID format not a UUID")

    ehr_response_data = ehr_response_data(ehr_id)

    return jsonify(ehr_response_data), 200

@app.route('/ehr', methods=['GET'])
def get_ehr_by_subject():
    subject_id = request.args.get('subject_id')
    subject_namespace = request.args.get('subject_namespace')

    ehr_id = ehr_service.findBySubject(subject_id, subject_namespace)
    if ehr_id is None:
        raise NotFound("No EHR with supplied subject parameters found")

    ehr_response_data = ehr_response_data(ehr_id)
    return jsonify(ehr_response_data), 200

def ehr_response_data(ehr_id):
    ehr_result = ehr_service.getEhrStatus(ehr_id)
    return {
        'system_id': system_service.getSystemId(),
        'ehr_id': str(ehr_id),
        'status': ehr_result.status,
        'creation_time': ehr_service.getCreationTime(ehr_id).isoformat(),
    }

if __name__ == '__main__':
    app.run(debug=True)
