from flask import Flask, request, jsonify, Response
from werkzeug.exceptions import BadRequest
from typing import Optional
import uuid

app = Flask(__name__)

# Mocking all the dependencies and services
class TemplateService:
    def build_example(self, template_id):
        return f"Example composition for {template_id}"

    def find_template(self, template_id):
        return f"Template {template_id} content"

class CompositionService:
    def serialize(self, composition, format):
        # Simulating serialization of a composition into different formats
        return StructuredString(f"Serialized {composition} in {format}")

class StructuredString:
    def __init__(self, value):
        self.value = value

class Action:
    RETRIEVE = "RETRIEVE"

class RestHref:
    def set_url(self, url):
        self.url = url

class Meta:
    def set_href(self, href):
        self.href = href

class TemplateResponseData:
    def __init__(self):
        self.action = None
        self.meta = None
        self.web_template = None

    def set_action(self, action):
        self.action = action

    def set_meta(self, meta):
        self.meta = meta

    def set_web_template(self, web_template):
        self.web_template = web_template

# Simulating the filter class from the original code
class Filter:
    def filter(self, template_content):
        return f"Filtered content of {template_content}"

# Now, our main TemplateController class
class TemplateController:

    def __init__(self):
        self.template_service = TemplateService()
        self.composition_service = CompositionService()

    def deprecation_headers(self, old_method, new_method):
        return {
            "Deprecation": f"Method {old_method} is deprecated. Use {new_method} instead."
        }

    def create_location_uri(self, template, template_id):
        return f"/rest/ecis/v1/{template}/{template_id}"

    # Mapping the @GetMapping("/example") endpoint in Python
    def get_template_example(self, template_id, format="FLAT"):
        if format in ["RAW", "EXPANDED", "ECISFLAT"]:
            raise BadRequest(f"Format {format} not supported")

        composition = self.template_service.build_example(template_id)
        composition_dto = f"CompositionDto({composition}, {template_id})"
        serialized = self.composition_service.serialize(composition_dto, format)

        content_type = "application/xml" if format == "XML" else "application/json"

        return Response(
            response=serialized.value,
            status=200,
            content_type=content_type,
            headers=self.deprecation_headers("TEMPLATE/getTemplateExample", "ADL 1.4 TEMPLATE/getTemplateExample")
        )

    # Mapping the @GetMapping("/{templateId}") endpoint in Python
    def get_template(self, template_id):
        template_response_data = TemplateResponseData()
        template_response_data.set_web_template(Filter().filter(self.template_service.find_template(template_id)))
        template_response_data.set_action(Action.RETRIEVE)

        url = RestHref()
        url.set_url(self.create_location_uri("TEMPLATE", template_id))

        meta = Meta()
        meta.set_href(url)
        template_response_data.set_meta(meta)

        return jsonify(template_response_data.__dict__), 200, self.deprecation_headers("TEMPLATE/getTemplate", "TEMPLATE/getWebTemplate")

# Creating an instance of TemplateController
template_controller = TemplateController()

# Flask route to replicate @GetMapping("/{templateId}/example")
@app.route("/rest/ecis/v1/template/<string:template_id>/example", methods=["GET"])
def get_template_example(template_id):
    format = request.args.get("format", "FLAT")
    return template_controller.get_template_example(template_id, format)

# Flask route to replicate @GetMapping("/{templateId}")
@app.route("/rest/ecis/v1/template/<string:template_id>", methods=["GET"])
def get_template(template_id):
    return template_controller.get_template(template_id)

if __name__ == "__main__":
    app.run(debug=True)
