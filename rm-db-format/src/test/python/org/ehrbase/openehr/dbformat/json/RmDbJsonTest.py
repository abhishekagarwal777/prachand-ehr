import base64
import unittest
from dataclasses import dataclass
from typing import Any, Dict

from com.fasterxml.jackson.databind import ObjectMapper
from com.nedap.archie.rm.datatypes import CodePhrase
from com.nedap.archie.rm.datavalues.encapsulated import DvMultimedia
from com.nedap.archie.rm.support.identification import TerminologyId

# Mocking RmDbJson class with necessary methods for testing
class RmDbJson:
    MARSHAL_OM = ObjectMapper()

@dataclass
class ByteArrayTest:
    data: bytes

class RmDbJsonTest(unittest.TestCase):

    def test_read_tree_byte_array_base64(self):
        json_string = '{"data":"U2hhbGwgQmUgQmFzZTY0IGVuY29kZWQ="}'
        json_node = RmDbJson.MARSHAL_OM.readTree(json_string)
        self.assertEqual(json_node.get("data").asText(), "U2hhbGwgQmUgQmFzZTY0IGVuY29kZWQ=")
        byte_array_test = RmDbJson.MARSHAL_OM.convertValue(json_node, ByteArrayTest)
        self.assertEqual(byte_array_test.data, "Shall Be Base64 encoded".encode())

    def test_read_tree_byte_array_base64_utf8(self):
        json_string = '{"data":"U29tZUTDpHTDtg=="}'
        json_node = RmDbJson.MARSHAL_OM.readTree(json_string)
        self.assertEqual(json_node.get("data").asText(), "U29tZUTDpHTDtg==")
        byte_array_test = RmDbJson.MARSHAL_OM.convertValue(json_node, ByteArrayTest)
        self.assertEqual(byte_array_test.data, "SomeDätö".encode())

    def test_read_tree_dv_multimedia_type(self):
        json_string = '{"_type":"DV_MULTIMEDIA","data":"VGVzdERhdGE=","media_type":{"_type":"CODE_PHRASE","terminology_id":{"_type":"TERMINOLOGY_ID","value":"IANA_media-type"},"code_string":"application/pdf"},"size":8}'
        json_node = RmDbJson.MARSHAL_OM.readTree(json_string)
        self.assertEqual(json_node.get("data").asText(), "VGVzdERhdGE=")
        dv_multimedia = RmDbJson.MARSHAL_OM.convertValue(json_node, DvMultimedia)
        self.assertEqual(dv_multimedia.getMediaType(), CodePhrase(TerminologyId("IANA_media-type"), "application/pdf"))
        self.assertEqual(dv_multimedia.getSize(), 8)
        self.assertEqual(dv_multimedia.getData(), "TestData".encode())

    def test_value_to_tree_byte_array_base64(self):
        data = "Shall Be Base64 encoded"
        json_node = RmDbJson.MARSHAL_OM.valueToTree(ByteArrayTest(data.encode()))
        self.assertEqual(json_node.get("data").asText(), "U2hhbGwgQmUgQmFzZTY0IGVuY29kZWQ=")
        self.assertEqual(json_node.toString(), '{"data":"U2hhbGwgQmUgQmFzZTY0IGVuY29kZWQ="}')

    def test_value_to_tree_byte_array_base64_utf8(self):
        data = "SomeDätö"
        json_node = RmDbJson.MARSHAL_OM.valueToTree(ByteArrayTest(data.encode()))
        self.assertEqual(json_node.get("data").asText(), "U29tZUTDpHTDtg==")
        self.assertEqual(json_node.toString(), '{"data":"U29tZUTDpHTDtg=="}')

    def test_value_to_tree_dv_multimedia_type(self):
        data = "TestData"
        multimedia = DvMultimedia()
        multimedia.setMediaType(CodePhrase(TerminologyId("IANA_media-type"), "application/pdf"))
        multimedia.setData(data.encode())
        multimedia.setSize(len(data.encode()))

        json_node = RmDbJson.MARSHAL_OM.valueToTree(multimedia)
        self.assertEqual(json_node.get("data").asText(), "VGVzdERhdGE=")
        self.assertEqual(json_node.toString(), '{"_type":"DV_MULTIMEDIA","data":"VGVzdERhdGE=","media_type":{"_type":"CODE_PHRASE","terminology_id":{"_type":"TERMINOLOGY_ID","value":"IANA_media-type"},"code_string":"application/pdf"},"size":8}')

if __name__ == '__main__':
    unittest.main()
