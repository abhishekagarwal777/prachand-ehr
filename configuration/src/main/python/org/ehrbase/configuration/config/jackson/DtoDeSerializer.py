import json
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError, root_validator

T = TypeVar('T', bound=BaseModel)

class DtoDeSerializer:
    def __init__(self, model_cls: Type[T], type_node: str):
        self.model_cls = model_cls
        self.type_node = type_node

    def deserialize(self, json_str: str) -> T:
        data = json.loads(json_str)
        self.validate_type(data)
        return self.model_cls.parse_obj(data)

    def validate_type(self, data: dict) -> None:
        type_node = data.get('_type')
        if type_node is None:
            raise ValueError("Missing [_type] value")
        elif type_node != self.type_node:
            raise ValueError(f"Unexpected [_type] value [{type_node}] not matching [{self.type_node}]")

# Example usage:

class MyDto(BaseModel):
    _type: str
    field1: str
    field2: int

# Instantiate the deserializer with the DTO class and expected type
deserializer = DtoDeSerializer(MyDto, "expected_type")

json_data = '{"_type": "expected_type", "field1": "value", "field2": 123}'
dto_instance = deserializer.deserialize(json_data)
print(dto_instance)
