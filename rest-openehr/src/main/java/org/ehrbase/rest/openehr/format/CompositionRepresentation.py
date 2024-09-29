from enum import Enum
from flask import request
from your_exceptions import InvalidApiParameterException, NotAcceptableException  # Adjust import as needed
from your_media_types import OpenEHRMediaType  # Define your media types here
from your_composition_format import CompositionFormat  # Import your CompositionFormat enum

class CompositionRepresentation(Enum):
    """
    Defines all supported combinations of MediaType with its corresponding CompositionFormat.
    To select an available CompositionRepresentation use the select_from_media_type_with_format function.
    """

    # An XML representation of a composition
    XML = (OpenEHRMediaType.APPLICATION_XML, CompositionFormat.XML)

    # A canonical JSON representation of a composition
    JSON = (OpenEHRMediaType.APPLICATION_JSON, CompositionFormat.JSON)

    # A structured JSON (structSDT) representation of a composition
    JSON_STRUCTURED = (OpenEHRMediaType.APPLICATION_WT_STRUCTURED_SCHEMA_JSON, CompositionFormat.STRUCTURED)

    # A flat JSON (simSDT) representation of a composition
    JSON_FLAT = (OpenEHRMediaType.APPLICATION_WT_FLAT_SCHEMA_JSON, CompositionFormat.FLAT)

    def __init__(self, media_type, composition_format):
        self._media_type = media_type
        self._format = composition_format

    @property
    def format(self):
        return self._format

    @property
    def media_type(self):
        return self._media_type

    @staticmethod
    def select_from_media_type_with_format(media_type, format):
        """
        Selects the supported CompositionRepresentation from the given MediaType in combination with the
        provided CompositionFormat.

        :param media_type: MediaType of the serialized composition
        :param format: CompositionFormat used for serialization and/or deserialization
        :return: CompositionRepresentation of a composition to use
        :raises InvalidApiParameterException: when the given format is not supported.
        :raises NotAcceptableException: when content type or composition format is not supported or invalid input.
        """
        if format is not None:
            CompositionRepresentation.validate_supported_composition_format(format)

        if media_type.is_compatible_with(OpenEHRMediaType.APPLICATION_XML):
            return CompositionRepresentation.select_xml_representation(media_type, format)
        elif media_type.is_compatible_with(OpenEHRMediaType.APPLICATION_WT_FLAT_SCHEMA_JSON):
            return CompositionRepresentation.JSON_FLAT
        elif media_type.is_compatible_with(OpenEHRMediaType.APPLICATION_WT_STRUCTURED_SCHEMA_JSON):
            return CompositionRepresentation.JSON_STRUCTURED
        elif media_type.is_compatible_with(OpenEHRMediaType.APPLICATION_JSON):
            return CompositionRepresentation.select_json_representation(media_type, format)
        else:
            raise NotAcceptableException("Only compositions in XML or JSON are supported at the moment")

    @staticmethod
    def validate_supported_composition_format(format):
        """
        Validates that the provided composition format is supported.

        :param format: CompositionFormat to validate
        :raises InvalidApiParameterException: if the format is not supported.
        """
        if format not in {CompositionFormat.FLAT, CompositionFormat.STRUCTURED, CompositionFormat.XML, CompositionFormat.JSON}:
            raise InvalidApiParameterException(f"Format {format} not supported")

    @staticmethod
    def select_xml_representation(media_type, format):
        """
        Selects the XML representation for the given media type and format.

        :param media_type: MediaType of the request
        :param format: CompositionFormat to check
        :return: Corresponding CompositionRepresentation for XML
        :raises NotAcceptableException: if the format is not XML.
        """
        if format is None or format == CompositionFormat.XML:
            return CompositionRepresentation.XML
        else:
            raise NotAcceptableException(f"Only composition format [XML] is supported at the moment for type [{media_type}]")

    @staticmethod
    def select_json_representation(media_type, format):
        """
        Selects the JSON representation for the given media type and format.

        :param media_type: MediaType of the request
        :param format: CompositionFormat to check
        :return: Corresponding CompositionRepresentation for JSON
        :raises NotAcceptableException: if the format is not supported.
        """
        if format is None:
            return CompositionRepresentation.JSON
        elif format == CompositionFormat.JSON:
            return CompositionRepresentation.JSON
        elif format == CompositionFormat.FLAT:
            return CompositionRepresentation.JSON_FLAT
        elif format == CompositionFormat.STRUCTURED:
            return CompositionRepresentation.JSON_STRUCTURED
        else:
            raise NotAcceptableException(f"Only compositions formats [JSON, FLAT, STRUCTURED] are supported at the moment for [{media_type}]")
