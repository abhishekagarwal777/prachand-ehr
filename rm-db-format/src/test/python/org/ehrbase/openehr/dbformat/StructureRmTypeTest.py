import pytest
from enum import Enum
from typing import Set, Dict, Optional, Union
import inspect

# Placeholder for actual RM classes
class Locatable:
    pass

class Actor:
    pass

class EhrAccess:
    pass

class RMTypeInfo:
    def __init__(self, rm_name, java_class, attributes):
        self.rm_name = rm_name
        self.java_class = java_class
        self.attributes = attributes

    def get_all_parent_classes(self) -> Set['RMTypeInfo']:
        # Placeholder: Implement logic to return parent classes
        return set()

class ArchieRMInfoLookup:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = ArchieRMInfoLookup()
        return cls._instance

    def get_type_info(self, type_enum):
        # Placeholder: Implement logic to return RMTypeInfo for the given type
        return RMTypeInfo(type_enum.name, type_enum.value, [])

    def get_all_types(self) -> Set[RMTypeInfo]:
        # Placeholder: Return a set of all RMTypeInfo instances
        return set()

class StructureRmType(Enum):
    # Define enum values as per your RM structure
    COMPOSITION = "Composition"
    EHR_STATUS = "EHRStatus"
    FOLDER = "Folder"
    EVENT_CONTEXT = "EventContext"
    FEEDER_AUDIT = "FeederAudit"
    # Add other types as necessary

    def get_parents(self) -> Set['StructureRmType']:
        # Placeholder: Implement logic to return parent types
        return set()

    @staticmethod
    def byTypeName(name: str) -> Optional['StructureRmType']:
        try:
            return StructureRmType[name]
        except KeyError:
            return None

    @property
    def type(self):
        return self.value

    def is_structure_entry(self) -> bool:
        return self in {StructureRmType.EVENT_CONTEXT, StructureRmType.FEEDER_AUDIT} or \
               issubclass(self.type, Locatable)

    def is_distinguishing(self) -> bool:
        # Placeholder: Implement logic to determine if it's distinguishing
        return True  # Example value, replace with actual logic


class TestStructureRmType:

    @pytest.mark.parametrize("type", list(StructureRmType))
    def test_by_type_name(self, type):
        assert StructureRmType.byTypeName(type.name) == type

    @pytest.mark.parametrize("type", list(StructureRmType))
    def test_rm_hierarchy(self, type):
        rm_infos = ArchieRMInfoLookup.getInstance()
        type_info = rm_infos.get_type_info(type)
        own_type_infos = type_info.get_all_parent_classes()
        own_type_infos.add(type_info)

        referencing_types = {t for t in rm_infos.get_all_types() if
                             Actor.__module__ != t.java_class.__module__ and
                             t.java_class != EhrAccess and
                             any(att.type in own_type_infos for att in t.attributes)}

        referencing_types = {t for t in referencing_types if not inspect.isabstract(t.java_class)}

        referencing_structure_rm_types = {
            StructureRmType.byTypeName(t.rm_name)
            for t in referencing_types
            if StructureRmType.byTypeName(t.rm_name) is not None
        }

        assert type.get_parents() == referencing_structure_rm_types

    @pytest.mark.parametrize("type", list(StructureRmType))
    def test_structure_entry(self, type):
        if type in {StructureRmType.EVENT_CONTEXT, StructureRmType.FEEDER_AUDIT}:
            assert type.is_structure_entry()
        else:
            assert type.is_structure_entry() == issubclass(type.type, Locatable)

    def test_distinguishing(self):
        reachable_from: Dict[StructureRmType, Set[StructureRmType]] = {s: {s} | s.get_parents() for s in StructureRmType}

        todo = set(StructureRmType)

        while todo:
            s = todo.pop()
            predecessors = reachable_from[s]

            new_predecessors = {p for predecessor in predecessors for p in reachable_from[predecessor] if p not in predecessors}

            if new_predecessors:
                predecessors.update(new_predecessors)
                todo.update(e for e, preds in reachable_from.items() if preds.contains(s) and e != s)

        roots = {StructureRmType.COMPOSITION, StructureRmType.EHR_STATUS, StructureRmType.FOLDER}

        for s in StructureRmType:
            belongs_to_roots = reachable_from[s].intersection(roots)
            assert s.is_distinguishing() == (len(belongs_to_roots) == 1), f"{s}(distinguishing={s.is_distinguishing()}) is reachable from {belongs_to_roots}"


# To run the tests, execute the following command in the terminal:
# pytest -q --tb=short <name_of_this_file>.py
