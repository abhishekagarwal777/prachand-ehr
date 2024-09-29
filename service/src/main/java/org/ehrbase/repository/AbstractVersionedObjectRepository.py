# Copyright (c) 2024 vitasystems GmbH.
# Licensed under the Apache License, Version 2.0 (the "License").

from sqlalchemy import (
    Table, Column, Integer, String, ForeignKey,
    JSON, select, and_, func, insert, delete
)
from sqlalchemy.orm import Session, relationship, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional, List, Callable, TypeVar, Union

Base = declarative_base()

# Define your models based on the Java classes
class Locatable(Base):
    __tablename__ = 'locatable'
    id = Column(UUID, primary_key=True)
    # Add other fields here


class AuditDetails(Base):
    __tablename__ = 'audit_details'
    id = Column(UUID, primary_key=True)
    # Add other fields here


class Contribution(Base):
    __tablename__ = 'contribution'
    id = Column(UUID, primary_key=True)
    # Add other fields here


class VersionHead(Base):
    __tablename__ = 'version_head'
    id = Column(UUID, primary_key=True)
    sys_version = Column(Integer)
    contribution_id = Column(UUID, ForeignKey('contribution.id'))
    ehr_id = Column(UUID)
    # Add other fields here


class VersionHistory(Base):
    __tablename__ = 'version_history'
    id = Column(UUID, primary_key=True)
    sys_version = Column(Integer)
    contribution_id = Column(UUID, ForeignKey('contribution.id'))
    sys_deleted = Column(Integer)
    # Add other fields here


# Type variables for generics
VR = TypeVar('VR', bound=VersionHead)
DR = TypeVar('DR', bound=Locatable)
VH = TypeVar('VH', bound=VersionHistory)
DH = TypeVar('DH', bound=Locatable)
O = TypeVar('O', bound=Locatable)

class AbstractVersionedObjectRepository:
    NOT_MATCH_LATEST_VERSION = "Not match latest version"

    def __init__(self, target_type: str, session: Session, **tables: Table):
        self.target_type = target_type
        self.tables = tables
        self.session = session

    @staticmethod
    def build_object_version_id(versioned_object_id: UUID, sys_version: int) -> str:
        return f"{versioned_object_id},{sys_version}"

    def find_head(self, condition) -> Optional[O]:
        query = select(self.tables['data_head']).where(condition)
        result = self.session.execute(query).fetchone()
        return result

    def find_by_version(self, condition, history_condition, version: int) -> Optional[O]:
        head_query = select(self.tables['data_head']).where(
            condition, self.tables['data_head'].c.sys_version == version)
        history_query = select(self.tables['data_history']).where(
            history_condition, self.tables['data_history'].c.sys_version == version)

        combined_query = head_query.union_all(history_query)
        data_record = self.session.execute(combined_query).fetchone()

        if data_record is None and not self.is_deleted(condition, history_condition, version):
            raise Exception(f"No {self.target_type} with given ID found")

        return data_record

    def is_deleted(self, condition, history_condition, version: int) -> bool:
        return self.find_root_record_by_version(condition, history_condition, version).sys_deleted

    def find_root_record_by_version(self, condition, history_condition, version: int) -> Optional[VH]:
        query = select(self.tables['version_head']).where(
            condition, self.tables['version_head'].c.sys_version == version)
        history_query = select(self.tables['version_history']).where(
            history_condition, self.tables['version_history'].c.sys_version == version)

        combined_query = query.union_all(history_query)
        return self.session.execute(combined_query).fetchone()

    def delete(self, ehr_id: UUID, condition, version: int, contribution_id: Optional[UUID], audit_id: Optional[UUID], notfound_message: str):
        version_heads = self.find_version_head_records(condition)

        if not version_heads:
            raise Exception(f"{self.target_type} not found: {notfound_message}")

        if len(version_heads) > 1:
            raise Exception("The implementation is limited to deleting one entry")

        version_head = version_heads[0]

        if version_head.sys_version != version:
            raise Exception(self.NOT_MATCH_LATEST_VERSION)

        self.copy_head_to_history(version_head)
        self.delete_head(condition, version)

        final_contribution_id = contribution_id or self.create_default_contribution(ehr_id)
        final_audit_id = audit_id or self.create_default_audit()

        version_head.sys_deleted = True
        version_head.sys_version += 1
        version_head.contribution_id = final_contribution_id
        self.session.add(version_head)
        self.session.commit()

    def commit_head(self, ehr_id: UUID, composition: O, contribution_id: Optional[UUID], audit_id: Optional[UUID],
                    change_type: str, add_version_fields: Callable[[VR], None], add_data_fields: Callable[[DR], None]):
        final_contribution_id = contribution_id or self.create_default_contribution(ehr_id)
        final_audit_id = audit_id or self.create_default_audit()

        version_data = self.to_records(ehr_id, composition, final_contribution_id, final_audit_id)

        version_record = version_data.version_record
        add_version_fields(version_record)
        self.session.add(version_record)

        for data_record in version_data.data_records:
            add_data_fields(data_record)
            self.session.add(data_record)

        self.session.commit()

    def update(self, ehr_id: UUID, composition: O, condition, history_condition, 
               contribution_id: Optional[UUID], audit_id: Optional[UUID], 
               add_version_fields: Callable[[VR], None], add_data_fields: Callable[[DR], None], 
               not_found_error_message: str):
        version_heads = self.find_version_head_records(condition)

        if not version_heads:
            latest_history_root = self.find_latest_history_root(history_condition)
            if not latest_history_root:
                raise Exception(f"{self.target_type} not found: {not_found_error_message}")

            if latest_history_root.sys_deleted:
                raise Exception(self.NOT_MATCH_LATEST_VERSION)

            old_version = latest_history_root.sys_version
            now = datetime.utcnow()

        elif len(version_heads) > 1:
            raise Exception(f"{len(version_heads)} versions were returned")

        else:
            old_version = version_heads[0].sys_version
            now = datetime.utcnow()

        if old_version + 1 != self.extract_version(composition.uid):
            raise Exception(self.NOT_MATCH_LATEST_VERSION)

        if latest_history_root:
            latest_history_root.sys_period_upper = now
            self.session.commit()
        else:
            self.copy_head_to_history(version_heads[0])
            self.delete_head(condition, old_version)

        self.commit_head(ehr_id, composition, contribution_id, audit_id, "modification",
                         add_version_fields, add_data_fields)

    # Placeholder methods for unimplemented methods in the original Java code
    def find_version_head_records(self, condition) -> List[VR]:
        query = select(self.tables['version_head']).where(condition)
        return self.session.execute(query).fetchall()

    def create_default_contribution(self, ehr_id: UUID) -> UUID:
        # Implement contribution creation logic
        pass

    def create_default_audit(self) -> UUID:
        # Implement audit creation logic
        pass

    def to_records(self, ehr_id: UUID, version_data_object: O, contribution_id: UUID, audit_id: UUID):
        # Implement logic to convert to records
        pass

    def copy_head_to_history(self, version_head: VR):
        # Implement logic to copy head to history
        pass

    def delete_head(self, condition, version):
        # Implement delete head logic
        pass

    def find_latest_history_root(self, condition) -> Optional[VH]:
        query = select(self.tables['version_history']).where(condition).order_by(
            self.tables['version_history'].c.sys_version.desc()).limit(1)
        return self.session.execute(query).fetchone()

    @staticmethod
    def extract_version(composition_uid: str) -> int:
        return int(composition_uid.split(",")[-1])  # Adjust according to actual UID format

# Define the functions and queries related to locatable data
def build_locatable_data_query(condition, head: bool) -> select:
    version_table = tables.get(True, head)
    data_table = tables.get(False, head)

    vo_id_field = version_table.c.vo_id
    sys_version_field = version_table.c.sys_version
    jsonb_field = func.jsonb_agg(
        data_table.c.entity_idx, data_table.c.data).label("data")

    return (from_joined_version_data(condition, head)
            .where(condition)
            .group_by(vo_id_field, sys_version_field))

def from_joined_version_data(select_query, head: bool) -> select:
    version_table = tables.get(True, head)
    data_table = tables.get(False, head)

    join_condition = version_data_join_condition(
        lambda f: version_table.c[f].eq(data_table.c[f]))

    if not head:
        join_condition = and_(
            join_condition,
            version_table.c.sys_version.eq(data_table.c.sys_version)
        )

    return select(version_table, data_table).join(data_table, join_condition)

def version_data_join_condition(condition: Callable[[str], str]) -> str:
    # Define the join condition logic
    pass
