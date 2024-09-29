class OpenEHRMediaType:
    """
    OpenEHR specific Formats.
    """

    # Format structSDT JSON.
    # For reference: https://specifications.openehr.org/releases/ITS-REST/latest/simplified_data_template.html
    APPLICATION_WT_JSON_VALUE = "application/openehr.wt+json"
    APPLICATION_WT_JSON = "application/openehr.wt+json"  # Representing MediaType as a string

    # Format structSDT JSON structured schema.
    # For reference: https://specifications.openehr.org/releases/ITS-REST/latest/simplified_data_template.html
    APPLICATION_WT_STRUCTURED_SCHEMA_JSON_VALUE = "application/openehr.wt.structured.schema+json"
    APPLICATION_WT_STRUCTURED_SCHEMA_JSON = "application/openehr.wt.structured.schema+json"  # Representing MediaType as a string

    # Format ncSDT extract from Operational Template (OPT).
    # For reference: https://specifications.openehr.org/releases/ITS-REST/latest/simplified_data_template.html
    APPLICATION_WT_FLAT_SCHEMA_JSON_VALUE = "application/openehr.wt.flat.schema+json"
    APPLICATION_WT_FLAT_SCHEMA_JSON = "application/openehr.wt.flat.schema+json"  # Representing MediaType as a string

    @staticmethod
    def get_media_type(value):
        """
        Returns the corresponding media type string for a given value.

        :param value: The media type value to retrieve.
        :return: Corresponding media type string.
        """
        if value == OpenEHRMediaType.APPLICATION_WT_JSON_VALUE:
            return OpenEHRMediaType.APPLICATION_WT_JSON
        elif value == OpenEHRMediaType.APPLICATION_WT_STRUCTURED_SCHEMA_JSON_VALUE:
            return OpenEHRMediaType.APPLICATION_WT_STRUCTURED_SCHEMA_JSON
        elif value == OpenEHRMediaType.APPLICATION_WT_FLAT_SCHEMA_JSON_VALUE:
            return OpenEHRMediaType.APPLICATION_WT_FLAT_SCHEMA_JSON
        else:
            raise ValueError("Unsupported media type value")
