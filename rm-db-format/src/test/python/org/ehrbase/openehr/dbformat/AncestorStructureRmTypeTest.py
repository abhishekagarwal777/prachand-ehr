import unittest
from enum import Enum
from typing import List, Set

class StructureRmType(Enum):
    CLUSTER = "CLUSTER"
    ELEMENT = "ELEMENT"

class AncestorStructureRmType(Enum):
    ENTRY = "ENTRY"
    ITEM = "ITEM"
    CARE_ENTRY = "CARE_ENTRY"

    def getNonStructureDescendants(self) -> Set[str]:
        if self == AncestorStructureRmType.ENTRY:
            return set()
        elif self == AncestorStructureRmType.ITEM:
            return set()

    def getDescendants(self) -> Set[str]:
        if self == AncestorStructureRmType.ENTRY:
            return {AncestorStructureRmType.CARE_ENTRY}
        elif self == AncestorStructureRmType.ITEM:
            return {StructureRmType.CLUSTER, StructureRmType.ELEMENT}

    @classmethod
    def byTypeName(cls, name: str) -> List['AncestorStructureRmType']:
        return [type for type in cls if type.name == name]

class AncestorStructureRmTypeTest(unittest.TestCase):

    def test_entry(self):
        self.assertEqual(AncestorStructureRmType.ENTRY.getNonStructureDescendants(), set())
        self.assertTrue(AncestorStructureRmType.ENTRY.getDescendants().issuperset(AncestorStructureRmType.CARE_ENTRY.getDescendants()))

    def test_item(self):
        self.assertEqual(AncestorStructureRmType.ITEM.getNonStructureDescendants(), set())
        self.assertEqual(AncestorStructureRmType.ITEM.getDescendants(), {StructureRmType.CLUSTER, StructureRmType.ELEMENT})

    def test_by_type_name(self):
        for type in AncestorStructureRmType:
            self.assertIn(type, AncestorStructureRmType.byTypeName(type.name))

if __name__ == '__main__':
    unittest.main()
