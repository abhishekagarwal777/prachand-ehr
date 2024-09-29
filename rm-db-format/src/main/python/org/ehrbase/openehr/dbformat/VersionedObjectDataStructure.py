import json
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any, Iterator
from collections import defaultdict

# Assuming these are defined elsewhere based on your Java code
class RMObject:
    pass

class RmDbJson:
    @staticmethod
    def marshal_om(value):
        return json.loads(value)  # Stub for the marshaling function

class StructureNode:
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []
        self.entity_idx = None
        self.structure_rm_type = None
        self.entity_name = None
        self.archetype_node_id = None
        self.json_node = None
        self.content_item = None
        self.parent_num = None
        self.num = None

    def set_entity_idx(self, idx):
        self.entity_idx = idx

    def set_structure_rm_type(self, structure_rm_type):
        self.structure_rm_type = structure_rm_type

    def set_entity_name(self, name):
        self.entity_name = name

    def set_archetype_node_id(self, archetype_node_id):
        self.archetype_node_id = archetype_node_id

    def set_json_node(self, json_node):
        self.json_node = json_node

    def set_content_item(self, content_item):
        self.content_item = content_item

    def get_structure_rm_type(self):
        return self.structure_rm_type

    def get_children(self):
        return self.children

    def add_child(self, child):
        self.children.append(child)

    def get_json_node(self):
        return self.json_node


class StructureRmType(Enum):
    ELEMENT = "element"
    FEEDER_AUDIT = "feeder_audit"

    @staticmethod
    def by_type(rm_object_type):
        # Placeholder for actual mapping
        return None

class OpenEHRDateTimeSerializationUtils:
    @staticmethod
    def to_magnitude(value):
        # Placeholder for actual conversion logic
        return value

class DbToRmFormat:
    TYPE_ATTRIBUTE = "type"

class StructureIndex:
    class Node:
        @staticmethod
        def of(attribute, index):
            return (attribute, index)

class RmAttributeAlias:
    @staticmethod
    def get_alias(key):
        return key  # Placeholder for actual aliasing logic

class RmTypeAlias:
    @staticmethod
    def get_alias(value):
        return value  # Placeholder for actual aliasing logic

MAGNITUDE_FIELD = "_magnitude"

class VersionedObjectDataStructure:
    @staticmethod
    def create_data_structure(rm_object: RMObject) -> List[StructureNode]:
        json_node = RmDbJson.marshal_om(rm_object)
        VersionedObjectDataStructure.fill_in_magnitudes(json_node)

        root = VersionedObjectDataStructure.create_structure_dto(
            None, json_node, StructureRmType.by_type(type(rm_object)), None
        )

        roots = [root]
        VersionedObjectDataStructure.handle_sub_structure(root, root.get_json_node(), None, roots)

        # set num and parentNum fields
        num = 0
        root.parent_num = 0
        for r in roots:
            if r.get_structure_rm_type() == StructureRmType.ELEMENT:
                r.num = num
                num += 1
                for c in r.get_children():
                    if c.get_structure_rm_type() == StructureRmType.ELEMENT:
                        c.parent_num = r.num
        return roots

    @staticmethod
    def stream_object_nodes(json_node) -> Iterator:
        if not isinstance(json_node, dict):
            return iter([])

        for key, value in json_node.items():
            yield from VersionedObjectDataStructure.stream_object_nodes(value)
            if isinstance(value, dict):
                yield value

    @staticmethod
    def fill_in_magnitudes(json_node):
        for node in VersionedObjectDataStructure.stream_object_nodes(json_node):
            VersionedObjectDataStructure.add_magnitude_attribute(node.get(DbToRmFormat.TYPE_ATTRIBUTE), node)

    @staticmethod
    def add_magnitude_attribute(type: str, obj):
        try:
            if type == "DV_DATE_TIME":
                obj[MAGNITUDE_FIELD] = OpenEHRDateTimeSerializationUtils.to_magnitude(RmDbJson.marshal_om(obj))
            elif type == "DV_DATE":
                obj[MAGNITUDE_FIELD] = OpenEHRDateTimeSerializationUtils.to_magnitude(RmDbJson.marshal_om(obj))
            elif type == "DV_TIME":
                obj[MAGNITUDE_FIELD] = OpenEHRDateTimeSerializationUtils.to_magnitude(RmDbJson.marshal_om(obj))
            elif type == "DV_DURATION":
                obj[MAGNITUDE_FIELD] = RmDbJson.marshal_om(obj).get('magnitude')
            elif type == "DV_PROPORTION":
                obj[MAGNITUDE_FIELD] = RmDbJson.marshal_om(obj).get('magnitude')
            # No else case needed
        except json.JSONDecodeError as e:
            raise RuntimeError(e)

    @staticmethod
    def handle_sub_structure(current_node: StructureNode, current_json: Any, array_parent_name: Optional[str], roots: List[StructureNode]) -> bool:
        if not isinstance(current_json, (dict, list)):
            return True

        if isinstance(current_json, dict):
            VersionedObjectDataStructure.handle_sub_object(current_node, current_json, roots)
            return True
        elif isinstance(current_json, list):
            has_remaining_children = False
            for i, child in enumerate(current_json):
                remaining_child = VersionedObjectDataStructure.handle_array_element(current_node, current_json, array_parent_name, roots, i)
                if i == 0:
                    has_remaining_children = remaining_child
                elif has_remaining_children != remaining_child:
                    raise ValueError("Structure elements must not be mixed with non-structure elements")
            return has_remaining_children
        else:
            raise RuntimeError(f"Unexpected container type: {type(current_json)}")

    @staticmethod
    def handle_array_element(root: StructureNode, parent_array: List, parent_name: Optional[str], roots: List[StructureNode], child_index: int) -> bool:
        child = parent_array[child_index]
        structure_rm_type = VersionedObjectDataStructure.get_type(child)
        child_root = structure_rm_type and StructureRmType.by_type(structure_rm_type)

        if child_root:
            new_root = VersionedObjectDataStructure.create_structure_dto(root, child, child_root, StructureIndex.Node.of(parent_name, child_index))
            roots.append(new_root)
        VersionedObjectDataStructure.handle_sub_structure(child_root or root, child, None, roots)

        return not (child_root and child_root.is_structure_entry())

    @staticmethod
    def handle_sub_object(root: StructureNode, json_node: dict, roots: List[StructureNode]):
        for attribute, child in json_node.items():
            child_root = VersionedObjectDataStructure.get_type(child)
            if child_root and child_root.is_structure_entry() and not (root.get_structure_rm_type() == StructureRmType.ELEMENT and child_root == StructureRmType.FEEDER_AUDIT):
                del json_node[attribute]
                continue

            new_root = VersionedObjectDataStructure.create_structure_dto(root, child, child_root, StructureIndex.Node.of(attribute, None))
            roots.append(new_root)

            keep_child = VersionedObjectDataStructure.handle_sub_structure(child_root or root, child, attribute, roots)
            if not keep_child:
                del json_node[attribute]

    @staticmethod
    def create_structure_dto(parent: Optional[StructureNode], json_node: Any, structure_rm_type: Optional[StructureRmType], idx: Optional[Tuple[str, int]]) -> StructureNode:
        new_root = StructureNode(parent)
        if parent is None:
            new_root.set_entity_idx(None)
        else:
            new_root.set_entity_idx(parent.entity_idx.create_child(idx))

        new_root.set_structure_rm_type(structure_rm_type)
        
        if isinstance(json_node, dict):
            name = json_node.get("name", {}).get("value")
            if name:
                new_root.set_entity_name(name)
            archetype_node_id = json_node.get("archetype_node_id")
            if archetype_node_id:
                new_root.set_archetype_node_id(archetype_node_id)

        new_root.set_json_node(json_node)

        if parent is None:
            content_item = None
        else:
            content_item = parent if parent.get_archetype_node_id() else parent.get_content_item()
        new_root.set_content_item(content_item)

        return new_root

    @staticmethod
    def get_type(child_node: Any) -> Optional[str]:
        if isinstance(child_node, dict):
            return child_node.get(DbToRmFormat.TYPE_ATTRIBUTE)
        return None

    @staticmethod
    def apply_rm_aliases(json_node: dict) -> dict:
        new_node = {}

        for key, value in json_node.items():
            alias = RmAttributeAlias.get_alias(key)
            if isinstance(value, dict):
                value = VersionedObjectDataStructure.apply_rm_aliases(value)
            elif isinstance(value, list):
                new_array = [VersionedObjectDataStructure.apply_rm_aliases(c) if isinstance(c, dict) else c for c in value]
                value = new_array
            elif isinstance(value, str) and key == DbToRmFormat.TYPE_ATTRIBUTE:
                value = RmTypeAlias.get_alias(value)

            new_node[alias] = value

        return new_node
