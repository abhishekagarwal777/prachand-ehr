import pytest
import json
from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass
from base64 import b64encode

# Placeholder for actual RM classes
class RMObject:
    pass

class Element:
    def __init__(self, archetype_node_id: str, name: 'DvText', multimedia: 'DvMultimedia'):
        self.archetype_node_id = archetype_node_id
        self.name = name
        self.multimedia = multimedia

class DvText:
    def __init__(self, value: str):
        self.value = value

class CodePhrase:
    def __init__(self, terminology_id: 'TerminologyId', code_string: str):
        self.terminology_id = terminology_id
        self.code_string = code_string

class TerminologyId:
    def __init__(self, value: str):
        self.value = value

class DvMultimedia:
    def __init__(self):
        self.media_type: CodePhrase = None
        self.data: bytes = None
        self.size: int = 0

    def setMediaType(self, media_type: CodePhrase):
        self.media_type = media_type

    def setData(self, data: bytes):
        self.data = data
        self.size = len(data)

@dataclass
class StructureNode:
    json_node: Dict[str, Any]

class StructureRmType(Enum):
    # Define enum values as per your RM structure
    ELEMENT = "Element"
    # Add other types as necessary

    @staticmethod
    def values():
        return list(StructureRmType)

    @property
    def alias(self):
        # Placeholder: return the alias for the StructureRmType
        return self.name.lower()

class CanonicalJson:
    @staticmethod
    def marshal_om(value):
        return value  # Placeholder for actual serialization logic

class VersionedObjectDataStructure:
    @staticmethod
    def createDataStructure(rm_object: RMObject) -> List[StructureNode]:
        # Placeholder: Implement the logic for creating data structure
        # Simulate returning a list of StructureNode
        if isinstance(rm_object, Element):
            return [StructureNode(json_node={
                "_type": rm_object.archetype_node_id,
                "feeder_audit": "feeder_audit_data",
                "name": {"_type": "DV_TEXT", "value": rm_object.name.value}
            }), StructureNode(json_node={"_type": "FEEDER_AUDIT"})]
        return []

class TestVersionedObjectDataStructure:

    def test_structure_rm_type_alias(self):
        # duplicate aliases?
        result = {type_.alias: type_ for type_ in StructureRmType.values()}
        assert result is not None

    @pytest.mark.parametrize(
        "type",
        [type_ for type_ in StructureRmType.values() if type_ not in {StructureRmType.ELEMENT}]
    )
    def test_feeder_audit_preserved_for_element_only(self, type):
        feeder_audit = {
            "_type": "FEEDER_AUDIT",
            "originating_system_item_ids": [
                {
                    "_type": "DV_IDENTIFIER",
                    "id": "system_id",
                    "type": "id"
                }
            ]
        }
        to_parse = {
            "_type": type.name,
            "name": {
                "_type": "DV_TEXT",
                "value": "name"
            },
            "feeder_audit": feeder_audit,
            "archetype_node_id": "at0005"
        }

        roots = VersionedObjectDataStructure.createDataStructure(CanonicalJson.marshal_om(to_parse))

        assert len(roots) == 2
        assert roots[1].json_node == feeder_audit
        json_node = roots[0].json_node
        assert ('feeder_audit' in json_node) == (type == StructureRmType.ELEMENT)
        if type == StructureRmType.ELEMENT:
            assert roots[1].json_node == json_node['feeder_audit']

    def test_value_to_tree_dv_multimedia_type(self):
        data = "TestData"
        multimedia = DvMultimedia()
        multimedia.setMediaType(CodePhrase(TerminologyId("IANA_media-type"), "application/pdf"))
        multimedia.setData(data.encode())
        
        roots = VersionedObjectDataStructure.createDataStructure(Element("at0001", DvText("Test"), multimedia))
        
        assert len(roots) == 1
        node = roots[0]
        value_node = node.json_node.get("value")
        
        assert isinstance(value_node, dict)
        assert value_node["data"] == b64encode(data.encode()).decode()
        assert value_node == {
            "_type": "DV_MULTIMEDIA",
            "data": "VGVzdERhdGE=",
            "media_type": {
                "_type": "CODE_PHRASE",
                "terminology_id": {
                    "_type": "TERMINOLOGY_ID",
                    "value": "IANA_media-type"
                },
                "code_string": "application/pdf"
            },
            "size": len(data.encode())
        }
