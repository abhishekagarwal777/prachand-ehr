# Copyright (c) 2024 vitasystems GmbH.
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

from typing import Optional, List
import uuid
from datetime import datetime
from EHR_name.api.exception import (ObjectNotFoundException,
                                              PreconditionFailedException,
                                              StateConflictException)
from EHR_name.api.service import EhrService, SystemService
from EHR_name.repository import EhrFolderRepository
from EHR_name.util import FolderUtils, UuidGenerator
from EHR_name.rm.directory import Folder
from EHR_name.rm.support.identification import ObjectVersionId, HierObjectId
from EHR_name.rm.support.identification import UIDBasedId, UID
from EHR_name.rm.support.identification import VersionTreeId
from EHR_name.logger import get_logger
from EHR_name.api.service import InternalDirectoryService
from spring_security import PreAuthorize
from spring.transaction import Transactional

logger = get_logger(__name__)

class DirectoryServiceImp(InternalDirectoryService):

    EHR_DIRECTORY_FOLDER_IDX = 1

    def __init__(self, system_service: SystemService, ehr_service: EhrService, ehr_folder_repository: EhrFolderRepository):
        self.system_service = system_service
        self.ehr_service = ehr_service
        self.ehr_folder_repository = ehr_folder_repository

    def get(self, ehr_id: uuid.UUID, folder_id: Optional[ObjectVersionId], path: Optional[str]) -> Optional[Folder]:
        root = None
        if folder_id is None:
            # directory
            root = self.ehr_folder_repository.find_head(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX)
        else:
            version_tree_id = folder_id.version_tree_id
            if version_tree_id.is_branch():
                raise Exception(f"Version branching is not supported: {version_tree_id.value}")

            if folder_id.creating_system_id.value != self.system_service.get_system_id():
                return None

            version = int(version_tree_id.value)
            # directory
            root = self.ehr_folder_repository.find_by_version(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX, version)

        if root is None:
            self.ehr_service.check_ehr_exists(ehr_id)
            return None

        if folder_id is not None and folder_id.root != root.uid.root:
            return None

        return self.find_by_path(root, path.split('/')) if path else root

    def get_by_time(self, ehr_id: uuid.UUID, time: datetime, path: Optional[str]) -> Optional[Folder]:
        version_by_time = self.ehr_folder_repository.find_version_by_time(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX, time)

        return (
            version_by_time
            .flat_map(lambda v: self.ehr_folder_repository.find_by_version(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX, extract_version(v)))
            .flat_map(lambda f: self.find_by_path(f, path.split('/')))
            if path else None
        )

    def find_by_path(self, root: Folder, path: List[str]) -> Optional[Folder]:
        if not path:
            return root
        if root.folders is None:
            return None

        for sf in root.folders:
            if sf.name_as_string == path[0]:
                return self.find_by_path(sf, path[1:])
        return None

    def create(self, ehr_id: uuid.UUID, folder: Folder) -> Folder:
        return self.create(ehr_id, folder, None, None)

    def create_with_contribution(self, ehr_id: uuid.UUID, folder: Folder, contribution_id: Optional[uuid.UUID], audit_id: Optional[uuid.UUID]) -> Folder:
        self.ehr_service.check_ehr_exists_and_is_modifiable(ehr_id)
        if self.ehr_folder_repository.has_folder(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX):
            raise StateConflictException(f"EHR with id {ehr_id} already contains a directory.")

        FolderUtils.check_sibling_name_conflicts(folder)

        self.update_uuid(
            folder,
            True,
            UUID(folder.uid.root.value) if folder.uid else UuidGenerator.random_uuid(),
            1
        )

        self.ehr_folder_repository.commit(ehr_id, folder, contribution_id, audit_id, self.EHR_DIRECTORY_FOLDER_IDX)
        return self.get(ehr_id, None, None)

    def update(self, ehr_id: uuid.UUID, folder: Folder, if_matches: ObjectVersionId) -> Folder:
        return self.update(ehr_id, folder, if_matches, None, None)

    def update_with_contribution(self, ehr_id: uuid.UUID, folder: Folder, if_matches: ObjectVersionId, contribution_id: Optional[uuid.UUID], audit_id: Optional[uuid.UUID]) -> Folder:
        self.ehr_service.check_ehr_exists_and_is_modifiable(ehr_id)
        if not self.ehr_folder_repository.has_folder(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX):
            raise PreconditionFailedException(f"EHR with id {ehr_id} does not contain a directory.")

        FolderUtils.check_sibling_name_conflicts(folder)

        version = int(if_matches.version_tree_id.value)

        self.update_uuid(folder, True, UUID(if_matches.object_id.value), version + 1)
        self.ehr_folder_repository.update(ehr_id, folder, contribution_id, audit_id, self.EHR_DIRECTORY_FOLDER_IDX)

        return self.get(ehr_id, None, None)

    def delete(self, ehr_id: uuid.UUID, if_matches: ObjectVersionId) -> None:
        self.delete_with_contribution(ehr_id, if_matches, None, None)

    def delete_with_contribution(self, ehr_id: uuid.UUID, if_matches: ObjectVersionId, contribution_id: Optional[uuid.UUID], audit_id: Optional[uuid.UUID]) -> None:
        self.ehr_service.check_ehr_exists_and_is_modifiable(ehr_id)
        if not self.ehr_folder_repository.has_folder(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX):
            raise PreconditionFailedException(f"EHR with id {ehr_id} does not contain a directory.")

        self.ehr_folder_repository.delete(
            ehr_id,
            UUID(if_matches.object_id.value),
            int(if_matches.version_tree_id.value),
            self.EHR_DIRECTORY_FOLDER_IDX,
            contribution_id,
            audit_id
        )

    def update_uuid(self, folder: Folder, root: bool, root_uuid: UUID, version: int) -> None:
        if folder.uid is None or root:
            if root:
                folder.uid = ObjectVersionId(f"{root_uuid}::{self.system_service.get_system_id()}::{version}")
            else:
                folder.uid = HierObjectId(str(UuidGenerator.random_uuid()))

        if folder.folders:
            for subfolder in folder.folders:
                self.update_uuid(subfolder, False, root_uuid, version)

    @PreAuthorize("hasRole('ADMIN')")
    def admin_delete_folder(self, ehr_id: uuid.UUID, folder_id: uuid.UUID) -> None:
        if not self.ehr_service.has_ehr(ehr_id):
            raise ObjectNotFoundException("Admin Directory", f"EHR with id {ehr_id} does not exist")

        latest = self.ehr_folder_repository.find_head(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX)

        if latest.is_present():
            from_folder = latest.get()
            if UUID(from_folder.uid.root.value) != folder_id:
                raise ValueError("FolderIds do not match")

            self.ehr_folder_repository.admin_delete(ehr_id, self.EHR_DIRECTORY_FOLDER_IDX)
