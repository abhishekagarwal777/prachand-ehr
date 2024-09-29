import json
from typing import Union

class StructuredString:
    def __init__(self, value: str, format: str):
        self.value = value
        self.format = format

class StructuredStringJsonSerializer:
    @staticmethod
    def serialize(value: StructuredString, format_type: str) -> str:
        if format_type == 'xml':
            if value.format == 'json':
                return json.dumps(value.value)
            elif value.format == 'xml':
                return value.value  # XML content, not escaped
            else:
                raise ValueError(f"Unexpected format: {value.format}")
        elif format_type == 'json':
            if value.format == 'xml':
                return json.dumps(value.value.replace('"', '\\"'))
            elif value.format == 'json':
                return value.value  # JSON content, raw
            else:
                raise ValueError(f"Unexpected format: {value.format}")
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

# Example usage
structured_string = StructuredString('{"key": "value"}', 'json')
serializer = StructuredStringJsonSerializer()
json_output = serializer.serialize(structured_string, 'json')
print(json_output)
