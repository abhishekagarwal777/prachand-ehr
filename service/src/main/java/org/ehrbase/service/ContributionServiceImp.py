# Copyright (c) 2024 vitasystems GmbH.
#
# This file is part of project EHRbase
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Optional, Tuple, Union
import uuid

from EHR.exceptions import (
    InternalServerException,
    ObjectNotFoundException,
    UnprocessableEntityException,
    ValidationException
)
from EHR.dto import EhrStatusDto
from EHR.services import (
    CompositionService,
    EhrService,
    InternalDirectoryService,
    ValidationService,
    ContributionRepository,
    CompositionRepository,
    EhrFolderRepository,
    EhrRepository
)
from EHR.models import ContributionCreateDto, ContributionDto, AuditDetails, ContributionDataType
from EHR.utils import UuidGenerator

class ContributionServiceImp:
    class SupportedVersionedObject:
        COMPOSITION = "COMPOSITION"
        EHR_STATUS = "EHR_STATUS"
        FOLDER = "FOLDER"

    def __init__(self, composition_service: CompositionService,
                 ehr_service: EhrService,
                 folder_service: InternalDirectoryService,
                 validation_service: ValidationService,
                 contribution_repository: ContributionRepository,
                 composition_repository: CompositionRepository,
                 ehr_folder_repository: EhrFolderRepository,
                 ehr_repository: EhrRepository):
        self.composition_service = composition_service
        self.ehr_service = ehr_service
        self.folder_service = folder_service
        self.validation_service = validation_service
        self.contribution_repository = contribution_repository
        self.composition_repository = composition_repository
        self.ehr_folder_repository = ehr_folder_repository
        self.ehr_repository = ehr_repository

    def get_contribution(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID) -> ContributionDto:
        audit_details = self.retrieve_audit_details(ehr_id, contribution_id)
        object_references = self.retrieve_uuids_of_contribution_objects(ehr_id, contribution_id)
        return ContributionDto(contribution_id, object_references, audit_details)

    def commit_contribution(self, ehr_id: uuid.UUID, content: str) -> uuid.UUID:
        if not self.ehr_service.has_ehr(ehr_id):
            raise ObjectNotFoundException("EHR", f"No EHR found with given ID: {ehr_id}")

        contribution_wrapper = ContributionServiceHelper.unmarshal_contribution(content)
        contribution = contribution_wrapper.get_contribution_create_dto()

        self.validation_service.check(contribution)

        audit_uuid = self.contribution_repository.create_audit(contribution.audit, "CONTRIBUTION")
        contribution_uuid = contribution.uid.value if contribution.uid else UuidGenerator.random_uuid()

        contribution_id = self.contribution_repository.create_contribution(
            ehr_id, contribution_uuid, ContributionDataType.other, audit_uuid
        )

        for version, dto in contribution_wrapper.versions:
            version_rm_object = version.data

            if isinstance(version_rm_object, Composition):
                self.process_composition_version(ehr_id, contribution_id, version, version_rm_object)
            elif isinstance(version_rm_object, Folder):
                self.process_folder_version(ehr_id, contribution_id, version, version_rm_object)
            elif isinstance(version_rm_object, EhrStatus):
                ehr_status_dto = dto if isinstance(dto, EhrStatusDto) else None
                if not ehr_status_dto:
                    raise InternalServerException("Expected DTO to exist for Contribution of EHR_STATUS")
                self.process_ehr_status_version(ehr_id, contribution_id, version, ehr_status_dto)
            elif version_rm_object is None:
                self.process_metadata_version(ehr_id, contribution_id, version)
            else:
                raise ValidationException(f"Invalid version object in contribution: {type(version_rm_object).__name__}")

        return contribution_id

    def process_ehr_status_version(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID, version, ehr_status: EhrStatusDto):
        change_type = ContributionService.ContributionChangeType.from_audit_details(version.commit_audit)

        self.check_contribution_rules(version, change_type)

        audit = self.contribution_repository.create_audit(version.commit_audit, "EHR_STATUS")

        if change_type == "CREATION":
            raise ValidationException("Invalid change type. EHR_STATUS cannot be manually created.")
        elif change_type in {"AMENDMENT", "MODIFICATION"}:
            self.ehr_service.update_status(ehr_id, ehr_status, version.preceding_version_uid, contribution_id, audit)
        elif change_type == "DELETED":
            raise ValidationException("Invalid change type. EHR_STATUS cannot be deleted.")
        else:
            raise ValidationException(f"ChangeType[{change_type}] not Supported.")

    def process_composition_version(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID, version, composition: Composition):
        change_type = ContributionService.ContributionChangeType.from_audit_details(version.commit_audit)

        self.check_contribution_rules(version, change_type)

        audit = self.contribution_repository.create_audit(version.commit_audit, "COMPOSITION")

        if change_type == "CREATION":
            self.composition_service.create(ehr_id, composition, contribution_id, audit)
        elif change_type in {"AMENDMENT", "MODIFICATION"}:
            self.composition_service.update(ehr_id, version.preceding_version_uid, composition, contribution_id, audit)
        elif change_type == "DELETED":
            self.composition_service.delete(ehr_id, version.preceding_version_uid, contribution_id, audit)
        else:
            raise ValidationException(f"ChangeType[{change_type}] not Supported.")

    def process_folder_version(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID, version, folder: Folder):
        change_type = ContributionService.ContributionChangeType.from_audit_details(version.commit_audit)

        self.check_contribution_rules(version, change_type)

        audit = self.contribution_repository.create_audit(version.commit_audit, "EHR_FOLDER")

        if change_type == "CREATION":
            self.folder_service.create(ehr_id, folder, contribution_id, audit)
        elif change_type in {"AMENDMENT", "MODIFICATION"}:
            self.folder_service.update(ehr_id, folder, version.preceding_version_uid, contribution_id, audit)
        elif change_type == "DELETED":
            self.folder_service.delete(ehr_id, version.preceding_version_uid, contribution_id, audit)
        else:
            raise ValidationException(f"ChangeType[{change_type}] not Supported.")

    def check_contribution_rules(self, version, change_type):
        if change_type == "CREATION" and version.preceding_version_uid:
            raise ValidationException("Invalid version. Change type CREATION while preceding_version_uid is set.")
        elif change_type in {"MODIFICATION", "AMENDMENT"} and not version.preceding_version_uid:
            raise ValidationException("Invalid version. Change type %s without preceding_version_uid." % change_type)

    def process_metadata_version(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID, version):
        change_type = ContributionService.ContributionChangeType.from_audit_details(version.commit_audit)

        if change_type != "DELETED":
            raise ValidationException(f"ChangeType[{change_type}] not Supported.")

        object_uid = self.get_versioned_uid_from_version(version)

        if self.composition_service.exists(object_uid):
            audit = self.contribution_repository.create_audit(version.commit_audit, "COMPOSITION")
            self.composition_service.delete(ehr_id, version.preceding_version_uid, contribution_id, audit)
        elif self.is_folder_present(ehr_id, version.preceding_version_uid):
            audit = self.contribution_repository.create_audit(version.commit_audit, "EHR_FOLDER")
            self.folder_service.delete(ehr_id, version.preceding_version_uid, contribution_id, audit)
        else:
            raise ObjectNotFoundException("COMPOSITION|FOLDER", f"Could not find Object[id: {object_uid}]")

    def is_folder_present(self, ehr_id: uuid.UUID, folder_uid):
        return self.folder_service.get(ehr_id, folder_uid, None) is not None

    def get_versioned_uid_from_version(self, version):
        preceding_version_uid = version.preceding_version_uid
        if preceding_version_uid is None:
            raise ValueError("Input invalid. Composition can't be modified without precedingVersionUid.")
        if preceding_version_uid.value.count("::") != 2:
            raise ValueError("Input invalid. Given precedingVersionUid is not a versionUid.")
        versioned_uid = preceding_version_uid.value.split("::")[0]
        return uuid.UUID(versioned_uid)

    def retrieve_uuids_of_contribution_objects(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID) -> Dict[str, str]:
        obj_refs = {}
        for k in sorted(self.composition_repository.find_version_ids_by_contribution(ehr_id, contribution_id)):
            obj_refs[k.value] = ContributionServiceImp.SupportedVersionedObject.COMPOSITION

        for k in sorted(self.ehr_repository.find_version_ids_by_contribution(ehr_id, contribution_id)):
            obj_refs[k.value] = ContributionServiceImp.SupportedVersionedObject.EHR_STATUS

        for f in sorted(self.ehr_folder_repository.find_folder_ids_by_contribution(ehr_id, contribution_id)):
            obj_refs[f.value] = ContributionServiceImp.SupportedVersionedObject.FOLDER

        return obj_refs

    def retrieve_audit_details(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID) -> AuditDetails:
        audit_details = self.contribution_repository.get_audit_details(ehr_id, contribution_id)
        if audit_details is None:
            raise ObjectNotFoundException("CONTRIBUTION", f"No contribution found with ID: {contribution_id}")
        return audit_details
