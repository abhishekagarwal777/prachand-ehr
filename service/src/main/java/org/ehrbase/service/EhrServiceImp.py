from typing import Optional, List, UUID
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Assuming necessary imports for database and validation handling

class StateConflictException(Exception):
    pass

class InternalServerException(Exception):
    pass

class ObjectNotFoundException(Exception):
    pass

class UnprocessableEntityException(Exception):
    pass

class ValidationException(Exception):
    pass

@dataclass
class EhrStatusDto:
    version_id: Optional[str]
    archetype_node_id: str
    name: str
    archetype_details: Optional[str]
    feeder_audit: Optional[str]
    subject: Optional[str]
    is_queryable: bool
    is_modifiable: bool
    other_details: Optional[str]

@dataclass
class EhrResult:
    ehr_id: UUID
    status_version_id: str
    status: EhrStatusDto

@dataclass
class AuditDetails:
    system_id: str
    committer: str
    time_committed: datetime
    change_type: str
    description: str

@dataclass
class RevisionHistoryItem:
    object_version_id: str
    audit_details: List[AuditDetails]

@dataclass
class RevisionHistory:
    items: List[RevisionHistoryItem]

    def add_item(self, item: RevisionHistoryItem):
        self.items.append(item)

class VersionedObject:
    def __init__(self, uid, owner_id, time_created):
        self.uid = uid
        self.owner_id = owner_id
        self.time_created = time_created

class EhrServiceImp:
    def __init__(self, validation_service, system_service, ehr_folder_repository,
                 composition_repository, ehr_repository, item_tag_repository):
        self.validation_service = validation_service
        self.ehr_folder_repository = ehr_folder_repository
        self.composition_repository = composition_repository
        self.ehr_repository = ehr_repository
        self.item_tag_repository = item_tag_repository
        self.system_service = system_service

    def create(self, ehr_id: Optional[UUID], status: Optional[EhrStatusDto]) -> EhrResult:
        ehr_id = ehr_id or UUID()  # Random UUID

        if self.has_ehr(ehr_id):
            raise StateConflictException("EHR with this ID already exists")

        if status is None:
            status = EhrStatusDto(
                None,
                "openEHR-EHR-EHR_STATUS.generic.v1",
                "EHR Status",
                None,
                None,
                None,
                True,
                True,
                None
            )
        else:
            self.check(status)
            self.check_ehr_exist_for_party(ehr_id, status)

        status_version_id = self.build_object_version_id(UUID(), 1)
        status = self.ehr_status_dto_with_id(status, status_version_id)

        self.ehr_repository.commit(ehr_id, self.from_dto(status), None, None)

        return EhrResult(ehr_id, status_version_id, status)

    def update_status(self, ehr_id: UUID, status: EhrStatusDto, if_match: str,
                      contribution_id: UUID, audit: UUID) -> EhrResult:
        self.check(status)
        self.ensure_ehr_exist(ehr_id)

        status = self.ehr_status_dto_with_id(status, if_match)
        self.check_ehr_exist_for_party(ehr_id, status)

        comp_id = UUID(if_match.split("::")[0])
        version = int(if_match.split("::")[1])

        status_version_id = self.build_object_version_id(comp_id, version + 1)
        status = self.ehr_status_dto_with_id(status, status_version_id)

        self.ehr_repository.update(ehr_id, self.from_dto(status), contribution_id, audit)

        return EhrResult(ehr_id, status_version_id, status)

    def get_ehr_status(self, ehr_id: UUID) -> EhrResult:
        self.check_ehr_exists(ehr_id)

        head = self.ehr_repository.find_head(ehr_id)

        if not head:
            self.raise_ehr_not_found_exception(ehr_id)

        return EhrResult(ehr_id, head.uid, head)

    def get_ehr_status_at_version(self, ehr_id: UUID, versioned_object_uid: UUID, version: int) -> Optional[EhrStatusDto]:
        self.ensure_ehr_exist(ehr_id)

        return self.ehr_repository.get_original_version_status(ehr_id, versioned_object_uid, version)

    def check_ehr_exist_for_party(self, ehr_id: UUID, status: EhrStatusDto):
        party_ref = status.subject  # Assuming subject returns a PartyRef

        if party_ref:
            subject_id = party_ref.id
            namespace = party_ref.namespace
            ehr_id_opt = self.find_by_subject(subject_id, namespace)
            if ehr_id_opt and ehr_id_opt != ehr_id:
                raise StateConflictException(
                    f"Supplied partyId[{subject_id}] is used by a different EHR in the same partyNamespace[{namespace}]."
                )

    def check(self, status: EhrStatusDto):
        try:
            self.validation_service.check(status)
        except Exception as ex:
            if isinstance(ex, (UnprocessableEntityException, ValidationException)):
                raise ex
            raise InternalServerException(str(ex))

    def find_by_subject(self, subject_id: str, namespace: str) -> Optional[UUID]:
        return self.ehr_repository.find_by_subject(subject_id, namespace)

    def get_ehr_status_version_by_timestamp(self, ehr_id: UUID, timestamp: datetime) -> str:
        self.ensure_ehr_exist(ehr_id)

        return self.ehr_repository.find_version_by_time(ehr_id, timestamp)

    def get_latest_version_uid_of_status(self, ehr_id: UUID) -> str:
        self.ensure_ehr_exist(ehr_id)

        return self.ehr_repository.find_latest_version(ehr_id)

    def get_creation_time(self, ehr_id: UUID) -> datetime:
        self.ensure_ehr_exist(ehr_id)

        return self.ehr_repository.find_ehr_creation_time(ehr_id)

    def has_ehr(self, ehr_id: UUID) -> bool:
        return self.ehr_repository.has_ehr(ehr_id)

    def get_versioned_ehr_status(self, ehr_id: UUID) -> VersionedObject:
        self.ensure_ehr_exist(ehr_id)

        return self.ehr_repository.get_versioned_ehr_status(ehr_id)

    def get_revision_history_of_versioned_ehr_status(self, ehr_uid: UUID) -> RevisionHistory:
        versions = int(self.get_latest_version_uid_of_status(ehr_uid).version)
        versioned_object_uid = self.get_latest_version_uid_of_status(ehr_uid).object_id

        revision_history = RevisionHistory(items=[])
        for i in range(1, versions + 1):
            ehr_status = self.get_ehr_status_at_version(ehr_uid, versioned_object_uid, i)

            if ehr_status:
                revision_history.add_item(self.revision_history_item_from_ehr_status(ehr_status, i))

        if not revision_history.items:
            raise InternalServerException("Problem creating RevisionHistory")

        return revision_history

    def revision_history_item_from_ehr_status(self, ehr_status, version: int) -> RevisionHistoryItem:
        status_id = ehr_status.version_id.split("::")[0]
        object_version_id = f"{status_id}::{self.system_service.get_system_id()}::{version}"

        audit_details_list = [ehr_status.commit_audit]

        if ehr_status.attestations:
            for a in ehr_status.attestations:
                new_audit = AuditDetails(
                    a.system_id,
                    a.committer,
                    a.time_committed,
                    a.change_type,
                    a.description
                )
                audit_details_list.append(new_audit)

        return RevisionHistoryItem(object_version_id, audit_details_list)

    def admin_delete_ehr(self, ehr_id: UUID):
        self.ehr_folder_repository.admin_delete(ehr_id, None)
        self.composition_repository.admin_delete_all(ehr_id)
        self.item_tag_repository.admin_delete_all(ehr_id)
        self.ehr_repository.admin_delete(ehr_id)

    def get_subject_ext_ref(self, ehr_id: str) -> Optional[str]:
        ehr_status = self.get_ehr_status(UUID(ehr_id)).status
        return ehr_status.subject.external_ref.id if ehr_status.subject else None

    def check_ehr_exists(self, ehr_id: UUID):
        if ehr_id is None or not self.has_ehr(ehr_id):
            raise ObjectNotFoundException("EHR", f"EHR with id {ehr_id} not found")

    def check_ehr_exists_and_is_modifiable(self, ehr_id: UUID):
        modifiable = self.ehr_repository.fetch_is_modifiable(ehr_id)

        if modifiable is None:
            raise ObjectNotFoundException("EHR", f"EHR with id {ehr_id} not found")

        if not modifiable:
            raise StateConflictException(f"EHR with id {ehr_id} does not allow modification")

    def ensure_ehr_exist(self, ehr_id: UUID):
        if not self.has_ehr(ehr_id):
            self.raise_ehr_not_found_exception(ehr_id)

    def ehr_status_dto_with_id(self, ehr_status_dto: EhrStatusDto, version_id: str) -> EhrStatusDto:
        return EhrStatusDto(
            version_id,
            ehr_status_dto.archetype_node_id,
            ehr_status_dto.name,
            ehr_status_dto.archetype_details,
            ehr_status_dto.feeder_audit,
            ehr_status_dto.subject,
            ehr_status_dto.is_queryable,
            ehr_status_dto.is_modifiable,
            ehr_status_dto.other_details
        )

    def raise_ehr_not_found_exception(self, ehr_id: UUID):
        raise ObjectNotFoundException("EHR", f"EHR with id {ehr_id} not found")

    def build_object_version_id(self, comp_id: UUID, version: int) -> str:
        return f"{comp_id}::{version}"
