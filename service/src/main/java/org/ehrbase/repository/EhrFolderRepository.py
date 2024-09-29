import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from models import EhrFolderVersion, EhrFolderData, EhrFolderVersionHistory, EhrFolderDataHistory
from models import Folder
from services import SystemService, TimeProvider
from repositories import ContributionRepository, AbstractVersionedObjectRepository

import sys
sys.path.append('/path/to/your/module')

from . import repositories

class EhrFolderRepository(AbstractVersionedObjectRepository):

    NOT_MATCH_LATEST_VERSION = "If-Match version_uid does not match latest version."

    def __init__(self, 
                 session: Session, 
                 contribution_repository: ContributionRepository,
                 system_service: SystemService,
                 time_provider: TimeProvider):
        super().__init__(EhrFolderVersion, EhrFolderData, EhrFolderVersionHistory, EhrFolderDataHistory, 
                         session, contribution_repository, system_service, time_provider)

    def get_version_data_join_fields(self) -> List[str]:
        return [EhrFolderVersion.ehr_id, EhrFolderVersion.ehr_folders_idx]

    def commit(self, ehr_id: uuid.UUID, folder: Folder, 
               contribution_id: Optional[uuid.UUID], 
               audit_id: Optional[uuid.UUID], 
               ehr_folders_idx: int) -> None:
        self.commit_head(
            ehr_id,
            folder,
            contribution_id,
            audit_id,
            ContributionChangeType.creation,
            lambda r: setattr(r, 'ehr_folders_idx', ehr_folders_idx),
            lambda r: setattr(r, 'ehr_id', ehr_id)
        )

    def update(self, ehr_id: uuid.UUID, folder: Folder, 
               contribution_id: Optional[uuid.UUID], 
               audit_id: Optional[uuid.UUID], 
               ehr_folders_idx: int) -> None:
        self.update(
            ehr_id,
            folder,
            self.single_folder_condition(ehr_id, ehr_folders_idx, self.version_head()),
            self.single_folder_condition(ehr_id, ehr_folders_idx, self.version_history()),
            contribution_id,
            audit_id,
            lambda r: setattr(r, 'ehr_folders_idx', ehr_folders_idx),
            lambda r: setattr(r, 'ehr_id', ehr_id),
            f"No Directory in ehr: {ehr_id}"
        )

    def find_head(self, ehr_id: uuid.UUID, ehr_folders_idx: int) -> Optional[Folder]:
        return self.find_head(self.single_folder_condition(ehr_id, ehr_folders_idx, self.version_head()))

    def delete(self, ehr_id: uuid.UUID, root_folder_id: uuid.UUID, 
               version: int, ehr_folders_idx: int, 
               contribution_id: Optional[uuid.UUID], 
               audit_id: Optional[uuid.UUID]) -> None:
        self.delete(
            ehr_id,
            self.single_folder_condition(ehr_id, ehr_folders_idx, self.version_head())
                .and_(self.version_prototype.vo_id == root_folder_id),
            version,
            contribution_id,
            audit_id,
            f"No folder with {root_folder_id}"
        )

    def find_by_version(self, ehr_id: uuid.UUID, folder_idx: int, version: int) -> Optional[Folder]:
        return self.find_by_version(
            self.single_folder_condition(ehr_id, folder_idx, self.version_head()),
            self.single_folder_condition(ehr_id, folder_idx, self.version_history()),
            version
        )

    def get_locatable_class(self) -> type:
        return Folder

    def single_folder_condition(self, ehr_id: uuid.UUID, folder_idx: int, table) -> 'Condition':
        return and_(
            table.ehr_id == ehr_id,
            table.ehr_folders_idx == folder_idx
        )

    def find_version_by_time(self, ehr_id: uuid.UUID, folder_idx: int, time: datetime) -> Optional[uuid.UUID]:
        return self.find_version_by_time(
            self.single_folder_condition(ehr_id, folder_idx, self.version_head()),
            self.single_folder_condition(ehr_id, folder_idx, self.version_history()),
            time
        )

    def has_folder(self, ehr_id: uuid.UUID, ehr_folder_idx: int) -> bool:
        head_query = select().select_one().from_(self.version_head()).where(
            self.single_folder_condition(ehr_id, ehr_folder_idx, self.version_head())
        )

        history_query = select().select_one().from_(self.version_history()).where(
            self.single_folder_condition(ehr_id, ehr_folder_idx, self.version_history())
        )

        return self.session.execute(head_query.union_all(history_query)).scalar() is not None

    def admin_delete(self, ehr_id: uuid.UUID, ehr_folders_idx: Optional[int]) -> None:
        delete_query = delete(self.version_head()).where(self.version_prototype.ehr_id == ehr_id)
        if ehr_folders_idx is not None:
            delete_query = delete_query.where(EhrFolderVersion.ehr_folders_idx == ehr_folders_idx)
        self.session.execute(delete_query)

        delete_history_query = delete(self.version_history()).where(self.version_history.ehr_id == ehr_id)
        if ehr_folders_idx is not None:
            delete_history_query = delete_history_query.where(EhrFolderVersionHistory.ehr_folders_idx == ehr_folders_idx)
        self.session.execute(delete_history_query)

    def find_for_contribution(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID) -> List[uuid.UUID]:
        return self.find_version_ids_by_contribution(ehr_id, contribution_id)
