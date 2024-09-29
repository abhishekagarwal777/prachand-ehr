import json
import unittest
from lxml import etree
from my_module.serializers import StructuredStringJSonSerializer  # Adjust import based on your module structure
from my_module.models import StructuredString, StructuredStringFormat, CompositionResponseData  # Adjust as needed

import sys
import os

sys.path.append(os.path.abspath('path/to/your/module'))

from .models import YourClass

class TestStructuredStringJSonSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = StructuredStringJSonSerializer()

    def test_serialize(self):
        # JSON in JSON
        response_data = CompositionResponseData()
        structured_string = StructuredString('{"test":false}', StructuredStringFormat.JSON)
        response_data.set_composition(structured_string)

        actual = json.dumps(response_data, default=self.serializer.serialize)
        expected = '{"meta": null, "action": null, "composition": {"test": false}, "format": null, "templateId": null, "ehrId": null, "compositionUid": null}'
        self.assertEqual(expected, actual)

        # XML in JSON
        response_data = CompositionResponseData()
        structured_string = StructuredString('<test>Test<test>', StructuredStringFormat.XML)
        response_data.set_composition(structured_string)

        actual = json.dumps(response_data, default=self.serializer.serialize)
        expected = '{"meta": null, "action": null, "composition": "<test>Test<test>", "format": null, "templateId": null, "ehrId": null, "compositionUid": null}'
        self.assertEqual(expected, actual)

        # JSON in XML
        response_data = CompositionResponseData()
        structured_string = StructuredString('{"test":false}', StructuredStringFormat.JSON)
        response_data.set_composition(structured_string)

        xml_result = self.serialize_to_xml(response_data)
        expected_xml = '<CompositionResponseData><meta/><action/><composition>{"test":false}</composition><format/><templateId/><ehrId/><compositionUid/></CompositionResponseData>'
        self.assertEqual(expected_xml, xml_result)

        # XML in XML
        response_data = CompositionResponseData()
        structured_string = StructuredString('<test>Test<test>', StructuredStringFormat.XML)
        response_data.set_composition(structured_string)

        xml_result = self.serialize_to_xml(response_data)
        expected_xml = '<CompositionResponseData><meta/><action/><composition><test>Test<test></composition><format/><templateId/><ehrId/><compositionUid/></CompositionResponseData>'
        self.assertEqual(expected_xml, xml_result)

    def serialize_to_xml(self, response_data):
        root = etree.Element("CompositionResponseData")
        etree.SubElement(root, "meta")
        etree.SubElement(root, "action")
        composition_element = etree.SubElement(root, "composition")
        composition_element.text = json.dumps(response_data.composition.value) if isinstance(response_data.composition.value, dict) else response_data.composition.value
        etree.SubElement(root, "format")
        etree.SubElement(root, "templateId")
        etree.SubElement(root, "ehrId")
        etree.SubElement(root, "compositionUid")

        return etree.tostring(root, pretty_print=True, encoding='unicode')

if __name__ == '__main__':
    unittest.main()
