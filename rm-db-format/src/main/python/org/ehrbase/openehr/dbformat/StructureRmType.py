from enum import Enum, auto
from typing import Type, Set, Optional, Dict, ClassVar, Tuple, List
from collections import defaultdict

# Placeholder for RMObject base class
class RMObject:
    pass

# Placeholder for specific RMObject subclasses
class Composition(RMObject):
    pass

class Folder(RMObject):
    pass

class EhrStatus(RMObject):
    pass

class EventContext(RMObject):
    pass

class Section(RMObject):
    pass

class GenericEntry(RMObject):
    pass

class AdminEntry(RMObject):
    pass

class Observation(RMObject):
    pass

class Instruction(RMObject):
    pass

class Action(RMObject):
    pass

class Evaluation(RMObject):
    pass

class InstructionDetails(RMObject):
    pass

class Activity(RMObject):
    pass

class History(RMObject):
    pass

class PointEvent(RMObject):
    pass

class IntervalEvent(RMObject):
    pass

class FeederAudit(RMObject):
    pass

class FeederAuditDetails(RMObject):
    pass

class ItemList(RMObject):
    pass

class ItemSingle(RMObject):
    pass

class ItemTable(RMObject):
    pass

class ItemTree(RMObject):
    pass

class Cluster(RMObject):
    pass

class Element(RMObject):
    pass

class StructureRoot:
    COMPOSITION = "COMPOSITION"
    FOLDER = "FOLDER"
    EHR_STATUS = "EHR_STATUS"

class StructureRmType(Enum):
    COMPOSITION = ("CO", StructureRoot.COMPOSITION, Composition, False)
    FOLDER = ("F", StructureRoot.FOLDER, Folder, True)
    EHR_STATUS = ("ES", StructureRoot.EHR_STATUS, EhrStatus, False)

    EVENT_CONTEXT = ("EC", StructureRoot.COMPOSITION, EventContext, True, False, [COMPOSITION])
    SECTION = ("SE", StructureRoot.COMPOSITION, Section, True, True, [COMPOSITION])
    GENERIC_ENTRY = ("GE", StructureRoot.COMPOSITION, GenericEntry, True, False, [COMPOSITION, SECTION])
    ADMIN_ENTRY = ("AE", StructureRoot.COMPOSITION, AdminEntry, True, False, [COMPOSITION, SECTION])
    OBSERVATION = ("OB", StructureRoot.COMPOSITION, Observation, True, False, [COMPOSITION, SECTION])
    INSTRUCTION = ("IN", StructureRoot.COMPOSITION, Instruction, True, False, [COMPOSITION, SECTION])
    ACTION = ("AN", StructureRoot.COMPOSITION, Action, True, False, [COMPOSITION, SECTION])
    EVALUATION = ("EV", StructureRoot.COMPOSITION, Evaluation, True, False, [COMPOSITION, SECTION])
    
    INSTRUCTION_DETAILS = ("ID", StructureRoot.COMPOSITION, InstructionDetails, False, False, [ACTION])
    ACTIVITY = ("AY", StructureRoot.COMPOSITION, Activity, True, False, [INSTRUCTION])
    
    HISTORY = ("HI", StructureRoot.COMPOSITION, History, True, False, [OBSERVATION])
    POINT_EVENT = ("PE", StructureRoot.COMPOSITION, PointEvent, True, False, [HISTORY])
    INTERVAL_EVENT = ("IE", StructureRoot.COMPOSITION, IntervalEvent, True, False, [HISTORY])

    FEEDER_AUDIT = (
        "FA", None, FeederAudit, True, False,
        [COMPOSITION, FOLDER, EHR_STATUS, SECTION, GENERIC_ENTRY,
         ADMIN_ENTRY, OBSERVATION, INSTRUCTION, ACTION, EVALUATION,
         ACTIVITY, HISTORY, POINT_EVENT, INTERVAL_EVENT]
    )
    FEEDER_AUDIT_DETAILS = ("FD", None, FeederAuditDetails, False, False, [FEEDER_AUDIT])
    
    ITEM_LIST = (
        "IL", None, ItemList, True, False,
        [FOLDER, EHR_STATUS, FEEDER_AUDIT_DETAILS, EVENT_CONTEXT,
         ADMIN_ENTRY, OBSERVATION, INSTRUCTION, ACTION, EVALUATION,
         INSTRUCTION_DETAILS, ACTIVITY, HISTORY, POINT_EVENT, INTERVAL_EVENT]
    )
    
    ITEM_SINGLE = (
        "IS", None, ItemSingle, True, False,
        [FOLDER, EHR_STATUS, FEEDER_AUDIT_DETAILS, EVENT_CONTEXT,
         ADMIN_ENTRY, OBSERVATION, INSTRUCTION, ACTION, EVALUATION,
         INSTRUCTION_DETAILS, ACTIVITY, HISTORY, POINT_EVENT, INTERVAL_EVENT]
    )
    
    ITEM_TABLE = (
        "TA", None, ItemTable, True, False,
        [FOLDER, EHR_STATUS, FEEDER_AUDIT_DETAILS, EVENT_CONTEXT,
         ADMIN_ENTRY, OBSERVATION, INSTRUCTION, ACTION, EVALUATION,
         INSTRUCTION_DETAILS, ACTIVITY, HISTORY, POINT_EVENT, INTERVAL_EVENT]
    )
    
    ITEM_TREE = (
        "TR", None, ItemTree, True, False,
        [FOLDER, EHR_STATUS, FEEDER_AUDIT_DETAILS, EVENT_CONTEXT,
         GENERIC_ENTRY, ADMIN_ENTRY, OBSERVATION, INSTRUCTION,
         ACTION, EVALUATION, INSTRUCTION_DETAILS, ACTIVITY, HISTORY,
         POINT_EVENT, INTERVAL_EVENT]
    )
    
    CLUSTER = ("CL", None, Cluster, True, True, [ITEM_TABLE, ITEM_TREE])
    ELEMENT = ("E", None, Element, True, False, [ITEM_LIST, ITEM_SINGLE, ITEM_TREE, CLUSTER])
    
    alias: str
    type: Type[RMObject]
    structure_entry: bool
    structure_root: Optional[StructureRoot]
    is_structure_root: bool
    parent_modifiable: Optional[Set['StructureRmType']]
    parents: Set['StructureRmType']

    BY_TYPE: ClassVar[Dict[Type[RMObject], 'StructureRmType']] = {}
    BY_TYPE_NAME: ClassVar[Dict[str, 'StructureRmType']] = {}
    STRUCTURE_LEAFS: ClassVar[Set['StructureRmType']] = set()

    def __new__(cls, alias: str, structure_root: Optional[StructureRoot], 
                rm_type: Type[RMObject], structure_entry: bool, 
                own_parent: Optional[bool] = None, parents: Optional[List['StructureRmType']] = None):
        obj = object.__new__(cls)
        obj._value_ = alias
        obj.structure_root = structure_root
        obj.type = rm_type
        obj.structure_entry = structure_entry
        obj.is_structure_root = structure_root is not None
        obj.parent_modifiable = set(parents) if parents else set()
        if own_parent:
            obj.parents = {obj} | set(parents) if parents else {obj}
        else:
            obj.parents = set(parents) if parents else set()
        return obj

    @classmethod
    def initialize(cls):
        cls.BY_TYPE = {v.type: v for v in cls}
        cls.BY_TYPE_NAME = {v.type.__name__: v for v in cls}
        cls.FEEDER_AUDIT.parent_modifiable.update({cls.ITEM_LIST, cls.ITEM_SINGLE, cls.ITEM_TABLE, cls.ITEM_TREE, cls.CLUSTER, cls.ELEMENT})
        
        cls.STRUCTURE_LEAFS = set(cls) - {parent for v in cls for parent in v.parents}

    @classmethod
    def get_alias_or_type_name(cls, type_name: str) -> str:
        return cls.by_type_name(type_name).alias if cls.by_type_name(type_name) else type_name

    @classmethod
    def by_type(cls, rm_type: Type[RMObject]) -> Optional['StructureRmType']:
        return cls.BY_TYPE.get(rm_type)

    @classmethod
    def by_type_name(cls, rm_type_name: str) -> Optional['StructureRmType']:
        return cls.BY_TYPE_NAME.get(rm_type_name)

    def get_parents(self) -> Set['StructureRmType']:
        return self.parents

    def is_structure_entry(self) -> bool:
        return self.structure_entry

# Initialize the class mappings after defining the class
StructureRmType.initialize()
