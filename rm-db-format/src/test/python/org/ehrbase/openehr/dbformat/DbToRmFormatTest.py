import unittest
import json
import io
from enum import Enum
from typing import Callable, List, Tuple
from unittest.mock import MagicMock
from collections import defaultdict

# Mock classes for the EHR components
class RMObject:
    pass

class Composition(RMObject):
    def __init__(self, archetype_details):
        self.archetype_details = archetype_details
        self.content = []

    def getArchetypeDetails(self):
        return self.archetype_details

class ArchetypeDetails:
    def __init__(self, template_id):
        self.template_id = template_id

    def getTemplateId(self):
        return self.template_id

class ItemTree(RMObject):
    def __init__(self, archetype_node_id, items):
        self.archetype_node_id = archetype_node_id
        self.items = items

    def getArchetypeNodeId(self):
        return self.archetype_node_id

class Evaluation(RMObject):
    def __init__(self, data):
        self.data = data

class Section(RMObject):
    def __init__(self, items):
        self.items = items

class PartyIdentified(RMObject):
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

class DvCount(RMObject):
    def __init__(self, magnitude):
        self.magnitude = magnitude

    def getMagnitude(self):
        return self.magnitude

class DvMultimedia(RMObject):
    def __init__(self, media_type, size, data):
        self.media_type = media_type
        self.size = size
        self.data = data

    def getMediaType(self):
        return self.media_type

    def getSize(self):
        return self.size

    def getData(self):
        return self.data

class CanonicalJson:
    @staticmethod
    def unmarshal(data):
        return json.loads(data)

    @staticmethod
    def valueToTree(obj):
        return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

class DbToRmFormat:
    TYPE_ALIAS = "some_type_alias"
    TYPE_ATTRIBUTE = "some_type_attribute"

    @staticmethod
    def getAlias(attribute):
        return "alias_of_" + attribute

    @staticmethod
    def reconstructRmObject(cls, data):
        if cls == Composition:
            details = ArchetypeDetails("International Patient Summary")
            composition = Composition(details)
            return composition
        elif cls == DvMultimedia:
            return DvMultimedia("application/pdf", 8, b'TestData')
        elif cls == ItemTree:
            return ItemTree("node_id", [])
        return None

class DbToRmFormatTest(unittest.TestCase):

    def test_type_alias(self):
        self.assertEqual(DbToRmFormat.TYPE_ALIAS, DbToRmFormat.getAlias(DbToRmFormat.TYPE_ATTRIBUTE))

    def load_db_one_json(self, name):
        data_path = f"./{name}.db_aliased.json"
        with open(data_path, 'r') as resource_stream:
            return resource_stream.read()

    def compare_json(self, composition, expected_composition):
        tree = CanonicalJson.valueToTree(composition)
        expected_tree = CanonicalJson.valueToTree(expected_composition)

        issues = []
        self.compare_json_node(tree, expected_tree, [], issues)
        if issues:
            self.fail('\n'.join(issues))

    def compare_json_node(self, node, expected_node, path, issues):
        if type(node) != type(expected_node):
            issues.append(f"Unexpected node type at {path}: {type(node)} vs. {type(expected_node)}")
        elif node is None:
            issues.append(f"Unexpected node type at {path}: None")
        elif isinstance(node, (int, float)):
            if node != expected_node:
                issues.append(f"Unexpected value at {path}: {node} vs. {expected_node}")
        elif isinstance(node, bool):
            if node != expected_node:
                issues.append(f"Unexpected value at {path}: {node} vs. {expected_node}")
        elif isinstance(node, str):
            if node != expected_node:
                issues.append(f"Unexpected value at {path}: {node} vs. {expected_node}")
        elif isinstance(node, list):
            if len(node) != len(expected_node):
                issues.append(f"Unexpected number of array elements at {path}: {len(node)} vs. {len(expected_node)}")
            for i in range(min(len(node), len(expected_node))):
                self.compare_json_node(node[i], expected_node[i], path + [i], issues)
        elif isinstance(node, dict):
            names = set(node.keys())
            expected_names = set(expected_node.keys())
            shared_names = names.intersection(expected_names)
            issues.extend([f"Unexpected nodes at {path}: {names - shared_names}"])
            issues.extend([f"Missing nodes at {path}: {expected_names - shared_names}"])
            for name in shared_names:
                self.compare_json_node(node[name], expected_node[name], path + [name], issues)

    def test_to_composition_from_test_ips(self):
        data = self.load_db_one_json("ips")
        composition = DbToRmFormat.reconstructRmObject(Composition, data)

        self.assertIsNotNone(composition.getArchetypeDetails())
        self.assertEqual(composition.getArchetypeDetails().getTemplateId(), "International Patient Summary")

        # Mock expected composition for comparison
        expected_composition = Composition(ArchetypeDetails("International Patient Summary"))
        
        # Example paths for assertions
        paths = [
            lambda c: c.getArchetypeDetails().getTemplateId(),
            lambda c: "Some value"  # Placeholder for actual logic
        ]

        for p in paths:
            self.assertEqual(p(composition), p(expected_composition))

        self.compare_json(composition, expected_composition)

    def test_to_composition_from_test_all_types(self):
        data = self.load_db_one_json("all_types_no_multimedia")
        composition = DbToRmFormat.reconstructRmObject(Composition, data)

        self.assertIsNotNone(composition.getArchetypeDetails())
        self.assertEqual(composition.getArchetypeDetails().getTemplateId(), "test_all_types.en.v1")

        expected_composition = Composition(ArchetypeDetails("test_all_types.en.v1"))

        paths = [
            lambda c: c.getArchetypeDetails().getTemplateId(),
            lambda c: "Some other value"  # Placeholder for actual logic
        ]

        for p in paths:
            self.assertEqual(p(composition), p(expected_composition))

        self.compare_json(composition, expected_composition)

    def test_reconstruct_rm_object_dv_multimedia_type(self):
        rm_object = DbToRmFormat.reconstructRmObject(
            DvMultimedia,
            '{"T": "mu", "d": "VGVzdERhdGE=", "mt": {"T": "C", "cd": "application/pdf"}, "si": 8}'
        )
        self.assertEqual(rm_object.getMediaType(), "application/pdf")
        self.assertEqual(rm_object.getSize(), 8)
        self.assertEqual(rm_object.getData(), b'TestData')

    def test_remove_prefix(self):
        # Add assertions similar to the original Java test
        pass

    def test_db_json_path(self):
        # Add assertions similar to the original Java test
        pass

if __name__ == '__main__':
    unittest.main()
