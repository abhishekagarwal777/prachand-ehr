import unittest
from unittest.mock import patch
from parameterized import parameterized
from werkzeug.exceptions import NotAcceptable
from enum import Enum

# Mock equivalent classes for CompositionRepresentation and CompositionFormat
class CompositionFormat(Enum):
    FLAT = 'FLAT'
    STRUCTURED = 'STRUCTURED'
    RAW = 'RAW'
    EXPANDED = 'EXPANDED'
    ECISFLAT = 'ECISFLAT'

class CompositionRepresentation:
    XML = 'XML'
    JSON = 'JSON'
    JSON_FLAT = 'JSON_FLAT'
    JSON_STRUCTURED = 'JSON_STRUCTURED'

    @staticmethod
    def select_from_media_type_with_format(media_type, composition_format):
        if media_type == 'application/xml':
            if composition_format in [None, CompositionFormat.FLAT, CompositionFormat.STRUCTURED]:
                raise NotAcceptable(
                    "Only composition format [XML] is supported at the moment for type [application/xml]"
                )
            return CompositionRepresentation.XML
        elif media_type == 'application/json':
            if composition_format == CompositionFormat.FLAT:
                return CompositionRepresentation.JSON_FLAT
            elif composition_format == CompositionFormat.STRUCTURED:
                return CompositionRepresentation.JSON_STRUCTURED
            return CompositionRepresentation.JSON
        elif media_type == 'application/x-www-form-urlencoded':
            raise NotAcceptable("Only compositions in XML or JSON are supported at the moment")
        raise NotAcceptable("Format %s not supported" % composition_format)

class OpenEHRMediaType:
    APPLICATION_WT_FLAT_SCHEMA_JSON = 'application/wt-flat-schema+json'
    APPLICATION_WT_STRUCTURED_SCHEMA_JSON = 'application/wt-structured-schema+json'

# Exception classes to mock InvalidApiParameterException and NotAcceptableException
class InvalidApiParameterException(Exception):
    pass

class NotAcceptableException(Exception):
    pass


class CompositionRepresentationTest(unittest.TestCase):

    def test_accepts_media_type_application_xml(self):
        self.assertEqual(
            CompositionRepresentation.XML,
            CompositionRepresentation.select_from_media_type_with_format('application/xml', None)
        )

    def test_fails_for_media_type_application_xhtml(self):
        with self.assertRaises(NotAcceptableException) as context:
            CompositionRepresentation.select_from_media_type_with_format('application/xhtml+xml', None)
        self.assertEqual(
            "Only compositions in XML or JSON are supported at the moment",
            str(context.exception)
        )

    def test_fails_for_media_type_application_xml_flat(self):
        with self.assertRaises(NotAcceptableException) as context:
            CompositionRepresentation.select_from_media_type_with_format('application/xml', CompositionFormat.FLAT)
        self.assertEqual(
            "Only composition format [XML] is supported at the moment for type [application/xml]",
            str(context.exception)
        )

    def test_fails_for_media_type_application_xml_structured(self):
        with self.assertRaises(NotAcceptableException) as context:
            CompositionRepresentation.select_from_media_type_with_format('application/xml', CompositionFormat.STRUCTURED)
        self.assertEqual(
            "Only composition format [XML] is supported at the moment for type [application/xml]",
            str(context.exception)
        )

    @parameterized.expand([
        (CompositionFormat.RAW,),
        (CompositionFormat.EXPANDED,),
        (CompositionFormat.ECISFLAT,)
    ])
    def test_fails_for_media_type_application_xml_unsupported_formats(self, format):
        with self.assertRaises(InvalidApiParameterException) as context:
            CompositionRepresentation.select_from_media_type_with_format('application/xml', format)
        self.assertEqual(
            "Format %s not supported" % format.name,
            str(context.exception)
        )

    def test_accepts_media_type_application_json(self):
        self.assertEqual(
            CompositionRepresentation.JSON,
            CompositionRepresentation.select_from_media_type_with_format('application/json', None)
        )

    def test_accepts_media_type_application_json_flat(self):
        self.assertEqual(
            CompositionRepresentation.JSON_FLAT,
            CompositionRepresentation.select_from_media_type_with_format('application/json', CompositionFormat.FLAT)
        )

    def test_accepts_media_type_application_json_structured(self):
        self.assertEqual(
            CompositionRepresentation.JSON_STRUCTURED,
            CompositionRepresentation.select_from_media_type_with_format('application/json', CompositionFormat.STRUCTURED)
        )

    def test_fails_for_media_type_application_ndjson(self):
        with self.assertRaises(NotAcceptableException) as context:
            CompositionRepresentation.select_from_media_type_with_format('application/ndjson', None)
        self.assertEqual(
            "Only compositions in XML or JSON are supported at the moment",
            str(context.exception)
        )

    @parameterized.expand([
        (CompositionFormat.RAW,),
        (CompositionFormat.EXPANDED,),
        (CompositionFormat.ECISFLAT,)
    ])
    def test_fails_for_media_type_application_json_unsupported_formats(self, format):
        with self.assertRaises(InvalidApiParameterException) as context:
            CompositionRepresentation.select_from_media_type_with_format('application/json', format)
        self.assertEqual(
            "Format %s not supported" % format.name,
            str(context.exception)
        )

    def test_accepts_media_type_application_wt_flat_json(self):
        self.assertEqual(
            CompositionRepresentation.JSON_FLAT,
            CompositionRepresentation.select_from_media_type_with_format(
                OpenEHRMediaType.APPLICATION_WT_FLAT_SCHEMA_JSON, None
            )
        )

    def test_accepts_media_type_application_wt_structured_json(self):
        self.assertEqual(
            CompositionRepresentation.JSON_STRUCTURED,
            CompositionRepresentation.select_from_media_type_with_format(
                OpenEHRMediaType.APPLICATION_WT_STRUCTURED_SCHEMA_JSON, None
            )
        )

    # Helper method to assert that an exception is raised with the expected message
    def assert_fails_with(self, message, exception_class, func):
        with self.assertRaises(exception_class) as context:
            func()
        self.assertEqual(message, str(context.exception))

if __name__ == "__main__":
    unittest.main()
