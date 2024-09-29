import pytest
from unittest.mock import Mock, patch
from http import HTTPStatus
from your_module import OpenehrTemplateController, InvalidApiParameterException
from your_module.dto import TemplateMetaDataDto
from your_module.service import CompositionService, TemplateService
from your_module.model import WebTemplate

class TestOpenehrTemplateController:

    CONTEXT_PATH = "https://template.test/ehrbase/rest"
    SAMPLE_OPT = """<?xml version="1.0" encoding="utf-8"?>
<template xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://schemas.openehr.org/v1">
    <test></test>
</template>
"""
    SAMPLE_WEB_TEMPLATE = WebTemplate()
    SAMPLE_ID = "test-template"

    @pytest.fixture
    def setup_controller(self):
        self.mock_template_service = Mock(TemplateService)
        self.mock_composition_service = Mock(CompositionService)
        self.controller = OpenehrTemplateController(self.mock_template_service, self.mock_composition_service)
        self.controller.get_context_path = Mock(return_value=self.CONTEXT_PATH)

    @pytest.mark.parametrize("accept", ["application/json", "application/xml"])
    def test_get_templates_adl1_4(self, setup_controller, accept):
        meta_data_dto = TemplateMetaDataDto()
        meta_data_dto.template_id = self.SAMPLE_ID

        self.mock_template_service.get_all_templates.return_value = [meta_data_dto]

        response = self.controller.get_templates_classic("1.0.3", None, accept)

        assert response.status_code == HTTPStatus.OK
        assert response.headers['Content-Type'] == accept
        assert response.headers['Location'] == f"{self.CONTEXT_PATH}/definition/template/adl1.4"
        assert response.body == [meta_data_dto]

    @pytest.mark.parametrize("prefer", ["", "return=minimal", "return=representation"])
    def test_create_template_adl1_4(self, setup_controller, prefer):
        self.mock_template_service.create.return_value = self.SAMPLE_ID
        self.mock_template_service.find_operational_template.return_value = self.SAMPLE_OPT
        self.mock_template_service.find_template.return_value = self.SAMPLE_WEB_TEMPLATE

        response = self.controller.create_template_classic("1.0.3", None, prefer, self.SAMPLE_OPT)

        assert response.status_code == HTTPStatus.CREATED
        assert response.headers['Content-Type'] == "application/xml"
        assert response.headers['Location'] == f"{self.CONTEXT_PATH}/definition/template/adl1.4/{self.SAMPLE_ID}"

        if prefer == "return=representation":
            assert response.body == self.SAMPLE_OPT
        else:
            assert response.body is None

    def test_create_template_adl1_4_opt_invalid_error(self, setup_controller):
        with pytest.raises(InvalidApiParameterException, match="error: Content is not allowed in prolog."):
            self.controller.create_template_classic("1.0.3", None, None, "not a xml")

    def test_get_template_adl1_4_opt(self, setup_controller):
        self.mock_template_service.find_operational_template.return_value = self.SAMPLE_OPT

        response = self.controller.get_template_classic("1.0.3", None, "application/xml", self.SAMPLE_ID)

        assert response.status_code == HTTPStatus.OK
        assert response.headers['Content-Type'] == "application/xml"
        assert response.headers['Location'] == f"{self.CONTEXT_PATH}/definition/template/adl1.4/{self.SAMPLE_ID}"
        assert response.body == self.SAMPLE_OPT

    @pytest.mark.parametrize("accept", ["application/json", "application/openehr.wt+json"])
    def test_get_template_adl1_4_web_template(self, setup_controller, accept):
        response = self.controller.get_template_classic("1.0.3", None, accept, self.SAMPLE_ID)

        assert response.status_code == HTTPStatus.OK
        assert response.headers['Content-Type'] == accept
        assert response.headers['Location'] == f"{self.CONTEXT_PATH}/definition/template/adl1.4/{self.SAMPLE_ID}"
        assert isinstance(response.body, WebTemplate)
        assert response.body == self.SAMPLE_WEB_TEMPLATE

    @pytest.mark.parametrize("accept", [
        "application/xml",
        "application/json",
        "application/openehr.wt.structured.schema+json",
        "application/openehr.wt.flat.schema+json"
    ])
    def test_get_template_example(self, setup_controller, accept):
        from your_module.composition import Composition
        from your_module.dto import StructuredString, StructuredStringFormat

        composition = Composition()
        structured_string = StructuredString("\"string\"", StructuredStringFormat.JSON)

        self.mock_template_service.build_example.return_value = composition
        self.mock_composition_service.serialize.return_value = structured_string

        response = self.controller.get_template_example(accept, self.SAMPLE_ID, None)

        assert response.status_code == HTTPStatus.OK
        assert response.headers['Content-Type'] == accept
        assert response.headers['Location'] == f"{self.CONTEXT_PATH}/definition/template/adl1.4/{self.SAMPLE_ID}/example"
        assert response.body == "\"string\""

    @pytest.mark.parametrize("accept", ["application/json", "application/openehr.wt+json"])
    def test_get_web_template(self, setup_controller, accept):
        response = self.controller.get_web_template(accept, self.SAMPLE_ID)

        assert response.status_code == HTTPStatus.OK
        assert response.headers['Content-Type'] == accept
        assert response.headers['Location'] == f"{self.CONTEXT_PATH}/definition/template/adl1.4/{self.SAMPLE_ID}/webtemplate"
        assert "Deprecated" in response.headers
        assert "Link" in response.headers
        assert isinstance(response.body, WebTemplate)
        assert response.body == self.SAMPLE_WEB_TEMPLATE

    def test_template_adl2_not_implemented(self, setup_controller):
        assert self.controller.get_templates_new(None, None, None).status_code == HTTPStatus.NOT_IMPLEMENTED
        assert self.controller.create_template_new(None, None, None, None, None, None, None).status_code == HTTPStatus.NOT_IMPLEMENTED
        assert self.controller.get_templates_new(None, None, None).status_code == HTTPStatus.NOT_IMPLEMENTED
