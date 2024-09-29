import json
from typing import Any
from dataclasses import dataclass
from abc import ABC
from your_module import OpenEHRBase  # Import your OpenEHRBase equivalent
from your_module import DbToRmFormat  # Import your DbToRmFormat equivalent

class RmDbJson:
    """The RmDbJson class provides functionality for JSON serialization of EHR data."""

    # Static member for ObjectMapper equivalent, initialized once
    MARSHAL_OM = None

    @classmethod
    def initialize(cls):
        """Initialize the MARSHAL_OM with the appropriate configuration."""
        cls.MARSHAL_OM = CanonicalJson.MARSHAL_OM.copy()
        cls.MARSHAL_OM.set_default_typing(OpenEHRBaseTypeResolverBuilder.build())

    def __init__(self):
        raise NotImplementedError("This class is not meant to be instantiated.")

    @dataclass
    class OpenEHRBaseTypeResolverBuilder(ABC):
        """Jackson type resolver builder for OpenEHRBase types."""

        def __init__(self):
            """Constructor to set up the type resolver."""
            self.default_typing = 'NON_FINAL_AND_ENUMS'  # Equivalent to Java's DefaultTyping
            self.subtype_validator = LaissezFaireSubTypeValidator()  # Assuming an equivalent

        def use_for_type(self, t: Any) -> bool:
            """Determine if this resolver can handle the given type."""
            return issubclass(t.__class__, OpenEHRBase)

        @classmethod
        def build(cls):
            """Build and return the type resolver builder."""
            builder = cls()
            builder.init(JsonTypeInfo.Id.NAME, CanonicalJson.CJOpenEHRTypeNaming())
            builder.type_property = DbToRmFormat.TYPE_ATTRIBUTE
            builder.type_id_visibility = True
            builder.inclusion = JsonTypeInfo.As.PROPERTY
            return builder

# Initialize the MARSHAL_OM once
RmDbJson.initialize()
