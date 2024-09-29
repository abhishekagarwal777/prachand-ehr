from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()

# Define database tables as classes
class Ehr(Base):
    __tablename__ = 'ehr'

    id = Column(UUID, primary_key=True)
    creation_date = Column(datetime)

class EhrStatus(Base):
    __tablename__ = 'ehr_status'

class EhrStatusVersion(Base):
    __tablename__ = 'ehr_status_version'

class EhrStatusData(Base):
    __tablename__ = 'ehr_status_data'

class EhrStatusVersionHistory(Base):
    __tablename__ = 'ehr_status_version_history'

class EhrStatusDataHistory(Base):
    __tablename__ = 'ehr_status_data_history'

class EhrRepository:
    NOT_MATCH_LATEST_VERSION = "If-Match version_uid does not match latest version."

    def __init__(self, session: Session):
        self.session = session

    def commit(self, ehr_id: UUID, status: EhrStatus, contribution_id: Optional[UUID], audit_id: Optional[UUID]):
        ehr_record = Ehr(id=ehr_id, creation_date=datetime.now())
        self.session.add(ehr_record)

        # Implementation of commitHead function will be similar to the commit logic in Java
        self.commit_head(ehr_id, status, contribution_id, audit_id)

    def has_ehr(self, ehr_id: UUID) -> bool:
        return self.session.query(Ehr).filter(Ehr.id == ehr_id).count() > 0

    def fetch_is_modifiable(self, ehr_id: UUID) -> Optional[bool]:
        result = self.session.execute(
            select(EhrStatusData).where(EhrStatusData.ehr_id == ehr_id).limit(1)
        ).fetchone()
        return result[0] if result else None

    def find_by_subject(self, subject_id: str, name_space: str) -> Optional[UUID]:
        result = self.session.execute(
            select(EhrStatusData.ehr_id).where(
                and_(
                    EhrStatusData.subject_id == subject_id,
                    EhrStatusData.namespace == name_space
                )
            )
        ).fetchone()
        return result[0] if result else None

    def find_by_version(self, ehr_id: UUID, status_version: UUID, version: int) -> Optional[EhrStatus]:
        result = self.session.execute(
            select(EhrStatus).where(
                and_(
                    EhrStatus.ehr_id == ehr_id,
                    EhrStatus.version == version
                )
            )
        ).fetchone()
        if result and result.uid == status_version:
            return result[0]
        return None

    def find_latest_version(self, ehr_id: UUID) -> Optional[Tuple[UUID, int]]:
        result = self.session.execute(
            select(EhrStatusVersion).where(EhrStatusVersion.ehr_id == ehr_id).limit(1)
        ).fetchone()
        return (result[0], result[1]) if result else None

    def find_head(self, ehr_id: UUID) -> Optional[EhrStatus]:
        return self.session.query(EhrStatus).filter(EhrStatus.ehr_id == ehr_id).first()

    def admin_delete(self, ehr_id: UUID):
        self.session.execute(delete(Ehr).where(Ehr.id == ehr_id))
        self.session.execute(delete(EhrStatus).where(EhrStatus.ehr_id == ehr_id))

    def update(self, ehr_id: UUID, ehr_status: EhrStatus, contribution_id: Optional[UUID], audit_id: Optional[UUID]):
        version_head = self.session.query(EhrStatusVersion).filter(EhrStatusVersion.ehr_id == ehr_id).first()
        if version_head.sys_version + 1 != self.extract_version(ehr_status.uid):
            raise Exception(self.NOT_MATCH_LATEST_VERSION)
        
        self.copy_head_to_history(version_head)
        self.delete_head(ehr_id, version_head.sys_version)
        self.commit_head(ehr_id, ehr_status, contribution_id, audit_id)

    def get_original_version_status(self, ehr_id: UUID, versioned_object_uid: UUID, version: int) -> Optional[EhrStatus]:
        return self.get_original_version(ehr_id, versioned_object_uid, version)

    def find_ehr_creation_time(self, ehr_id: UUID) -> datetime:
        result = self.session.execute(
            select(Ehr.creation_date).where(Ehr.id == ehr_id)
        ).fetchone()
        return result[0] if result else None

    # Helper methods for commit, copy head, and other functionality would go here

    def commit_head(self, ehr_id: UUID, status: EhrStatus, contribution_id: Optional[UUID], audit_id: Optional[UUID]):
        pass  # Placeholder for the actual commit logic

    def extract_version(self, uid: UUID) -> int:
        return int(uid.version)  # Assuming `uid` has a version attribute

    def copy_head_to_history(self, version_head: EhrStatusVersion):
        pass  # Placeholder for copying head to history

    def delete_head(self, ehr_id: UUID, version: int):
        pass  # Placeholder for deleting head logic

    def get_original_version(self, ehr_id: UUID, versioned_object_uid: UUID, version: int) -> Optional[EhrStatus]:
        pass  # Placeholder for getting original version
