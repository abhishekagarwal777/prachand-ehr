import uuid
import json
from typing import Collection, Optional, Callable, Generator
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Exception definitions
class InternalServerException(Exception):
    pass

# Database Record Prototypes
Base = declarative_base()

class ObjectVersionRecordPrototype(Base):
    __tablename__ = 'object_version'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ehr_id = Column(UUID(as_uuid=True))
    vo_id = Column(UUID(as_uuid=True))
    sys_version = Column(String)
    sys_period_lower = Column(DateTime)
    audit_id = Column(UUID(as_uuid=True))
    contribution_id = Column(UUID(as_uuid=True))

class ObjectDataRecordPrototype(Base):
    __tablename__ = 'object_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vo_id = Column(UUID(as_uuid=True))
    num = Column(String)
    citem_num = Column(String)
    parent_num = Column(String)
    num_cap = Column(String)
    rm_entity = Column(String)
    entity_concept = Column(String)
    entity_name = Column(String)
    entity_attribute = Column(String)
    entity_idx = Column(String)
    entity_idx_len = Column(String)
    data = Column(JSON)

class StructureNode:
    # Simulated StructureNode class for the sake of this implementation
    def __init__(self, num, parent_num, num_cap, rm_entity, archetype_node_id, entity_name, entity_idx, json_node):
        self.num = num
        self.parent_num = parent_num
        self.num_cap = num_cap
        self.rm_entity = rm_entity
        self.archetype_node_id = archetype_node_id
        self.entity_name = entity_name
        self.entity_idx = entity_idx
        self.json_node = json_node

    def get_num(self):
        return self.num

    def get_content_item(self):
        return self

    def get_parent_num(self):
        return self.parent_num

    def get_rm_entity(self):
        return self.rm_entity

    def get_archetype_node_id(self):
        return self.archetype_node_id

    def get_entity_name(self):
        return self.entity_name

    def get_entity_idx(self):
        return self.entity_idx

    def get_json_node(self):
        return self.json_node

class AslRmTypeAndConcept:
    @staticmethod
    def to_entity_concept(node_id: str) -> str:
        # Placeholder for the actual conversion logic
        return node_id

class StructureIndex:
    # Placeholder implementation for StructureIndex
    def print_last_attribute(self) -> str:
        return "last_attribute"

    def print_index_string(self, arg1: bool, arg2: bool) -> str:
        return "index_string"

    def length(self) -> int:
        return 1

class VersionedObjectDataStructure:
    @staticmethod
    def create_data_structure(version_data_object) -> Collection[StructureNode]:
        # Placeholder implementation for creating the data structure
        return [StructureNode("1", "0", "1", "Entity", "nodeId", "EntityName", StructureIndex(), json.loads('{}'))]

    @staticmethod
    def apply_rm_aliases(json_node) -> dict:
        # Placeholder implementation for applying RM aliases
        return json_node

# VersionDataDbRecord class
class VersionDataDbRecord:
    def __init__(self, version_record: ObjectVersionRecordPrototype, data_records: Callable[[], Generator[ObjectDataRecordPrototype, None, None]]):
        self.version_record = version_record
        self.data_records = data_records

    @staticmethod
    def to_records(ehr_id: uuid.UUID, version_data_object: 'Locatable', contribution_id: uuid.UUID, audit_id: uuid.UUID, now: datetime, session) -> 'VersionDataDbRecord':
        roots = VersionedObjectDataStructure.create_data_structure(version_data_object)
        vo_id = uuid.UUID(version_data_object.get_uid().get_root().get_value())
        
        version_record = VersionDataDbRecord.build_version_record(
            session, 
            ehr_id, 
            vo_id, 
            VersionedObjectDataStructure.extract_version(version_data_object.get_uid()), 
            contribution_id, 
            audit_id, 
            now
        )
        
        data_records = VersionDataDbRecord.data_records_builder(vo_id, roots, session)
        
        return VersionDataDbRecord(version_record, data_records)

    @staticmethod
    def build_version_record(session, ehr_id: uuid.UUID, vo_id: uuid.UUID, sys_version: int, contribution_id: uuid.UUID, audit_id: uuid.UUID, now: datetime) -> ObjectVersionRecordPrototype:
        object_data_record = ObjectVersionRecordPrototype()

        # system columns
        object_data_record.ehr_id = ehr_id
        object_data_record.vo_id = vo_id
        object_data_record.sys_version = str(sys_version)
        object_data_record.sys_period_lower = now
        object_data_record.audit_id = audit_id
        object_data_record.contribution_id = contribution_id

        session.add(object_data_record)
        session.commit()
        
        return object_data_record

    @staticmethod
    def data_records_builder(vo_id: uuid.UUID, node_list: Collection[StructureNode], session) -> Callable[[], Generator[ObjectDataRecordPrototype, None, None]]:
        def generator() -> Generator[ObjectDataRecordPrototype, None, None]:
            for node in node_list:
                if node.get_rm_entity() == "StructureEntry":  # Simulating StructureEntry check
                    yield VersionDataDbRecord.build_data_record(vo_id, node, session)

        return generator

    @staticmethod
    def build_data_record(vo_id: uuid.UUID, node: StructureNode, session) -> ObjectDataRecordPrototype:
        rec = ObjectDataRecordPrototype()

        rec.num = node.get_num()
        rec.citem_num = node.get_content_item().get_num() if node.get_content_item() else None
        rec.parent_num = node.get_parent_num()
        rec.num_cap = node.get_num_cap()
        rec.rm_entity = node.get_rm_entity()  # Assumed to be an alias
        rec.entity_concept = AslRmTypeAndConcept.to_entity_concept(node.get_archetype_node_id())
        rec.entity_name = node.get_entity_name()
        
        index = node.get_entity_idx()
        rec.entity_attribute = index.print_last_attribute()
        rec.entity_idx = index.print_index_string(False, True)
        rec.entity_idx_len = str(index.length())
        
        rec.data = VersionedObjectDataStructure.apply_rm_aliases(node.get_json_node())

        # system columns
        rec.vo_id = vo_id

        session.add(rec)
        session.commit()
        
        return rec
