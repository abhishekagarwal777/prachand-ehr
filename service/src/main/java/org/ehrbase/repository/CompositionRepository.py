# Copyright (c) 2024 vitasystems GmbH.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from uuid import UUID
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select, union_all, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import JSON
import asyncio

Base = declarative_base()

@dataclass
class Composition:
    # Define fields according to your requirements
    pass

@dataclass
class VersionedComposition:
    uid: str
    owner_id: str
    time_created: str

class KnowledgeCacheService:
    def find_uuid_by_template_id(self, template_id: str) -> Optional[UUID]:
        # Implement method
        pass

    def find_template_id_by_uuid(self, uuid: UUID) -> Optional[str]:
        # Implement method
        pass

class CompositionRepository:
    def __init__(self, session: AsyncSession, knowledge_cache: KnowledgeCacheService):
        self.session = session
        self.knowledge_cache = knowledge_cache

    async def commit(self, ehr_id: UUID, composition: Composition, contribution_id: Optional[UUID], audit_id: Optional[UUID]):
        template_id = await self._get_template_id(composition)
        root_concept = self._to_entity_concept(composition.archetype_node_id)

        # Implement commit_head logic here

    async def delete(self, ehr_id: UUID, comp_id: UUID, version: int, contribution_id: Optional[UUID], audit_id: Optional[UUID]):
        condition = self.single_composition_in_ehr_condition(ehr_id, comp_id)
        # Implement delete logic here

    async def is_template_used(self, template_id: str) -> bool:
        template_uuid = await self.knowledge_cache.find_uuid_by_template_id(template_id)
        if template_uuid is None:
            return False

        query = select(COMP_VERSION.c.vo_id).where(
            and_(COMP_VERSION.c.template_id == template_uuid, COMP_VERSION.c.sys_version == 1)
        )
        
        union_query = union_all(query, select(COMP_VERSION_HISTORY.c.vo_id).where(
            and_(COMP_VERSION_HISTORY.c.template_id == template_uuid, COMP_VERSION_HISTORY.c.sys_version == 1)
        ))

        result = await self.session.execute(union_query)
        return result.scalars().first() is not None

    async def update(self, ehr_id: UUID, composition: Composition, contribution_id: Optional[UUID], audit_id: Optional[UUID]):
        root_id = self.extract_uid(composition.uid)
        template_id = await self._get_template_id(composition)
        root_concept = self._to_entity_concept(composition.archetype_node_id)

        # Implement update logic here

    async def exists(self, comp_id: UUID) -> bool:
        query = select(1).where(COMP_VERSION.c.vo_id == comp_id)
        union_query = union_all(query, select(1).where(COMP_VERSION_HISTORY.c.vo_id == comp_id))
        result = await self.session.execute(union_query)
        return result.scalars().first() is not None

    async def get_latest_version_number(self, comp_id: UUID) -> Optional[int]:
        query = select(COMP_VERSION.c.sys_version).where(COMP_VERSION.c.vo_id == comp_id)
        union_query = union_all(query, select(COMP_VERSION_HISTORY.c.sys_version).where(COMP_VERSION_HISTORY.c.vo_id == comp_id))
        
        result = await self.session.execute(union_query.order_by(COMP_VERSION.c.sys_version.desc()).limit(1))
        return result.scalar_one_or_none()

    async def is_deleted(self, ehr_id: UUID, comp_id: UUID, version: int) -> bool:
        # Implement is_deleted logic here

    async def find_by_version(self, ehr_id: UUID, comp_id: UUID, version: int) -> Optional[Composition]:
        # Implement find_by_version logic here

    async def find_head(self, ehr_id: UUID, comp_id: UUID) -> Optional[Composition]:
        # Implement find_head logic here

    async def find_template_id(self, comp_id: UUID) -> Optional[str]:
        query = select(COMP_VERSION.c.template_id).where(
            and_(COMP_VERSION.c.vo_id == comp_id, COMP_VERSION.c.sys_version == 1)
        )
        union_query = union_all(query, select(COMP_VERSION_HISTORY.c.template_id).where(
            and_(COMP_VERSION_HISTORY.c.vo_id == comp_id, COMP_VERSION_HISTORY.c.sys_version == 1)
        ))

        result = await self.session.execute(union_query)
        return result.scalar_one_or_none()

    async def admin_delete(self, comp_id: UUID):
        await self.session.execute(COMP_VERSION_HISTORY.delete().where(COMP_VERSION_HISTORY.c.vo_id == comp_id))
        await self.session.execute(COMP_VERSION.delete().where(COMP_VERSION.c.vo_id == comp_id))

    async def admin_delete_all(self, ehr_id: UUID):
        await self.session.execute(COMP_VERSION_HISTORY.delete().where(COMP_VERSION_HISTORY.c.ehr_id == ehr_id))
        await self.session.execute(COMP_VERSION.delete().where(COMP_VERSION.c.ehr_id == ehr_id))

    def single_composition_in_ehr_condition(self, ehr_id: UUID, comp_id: UUID):
        # Implement condition logic
        pass

    async def _get_template_id(self, composition: Composition) -> UUID:
        # Implement method to extract template id
        pass

    def extract_uid(self, uid: str) -> UUID:
        # Implement UID extraction logic
        pass

    def _to_entity_concept(self, archetype_node_id: str) -> str:
        # Implement method to convert archetype_node_id to root concept
        pass

# Define your table models as needed
class COMP_VERSION(Base):
    __tablename__ = 'comp_version'
    vo_id = Column(UUID, primary_key=True)
    # Add other fields as needed

class COMP_VERSION_HISTORY(Base):
    __tablename__ = 'comp_version_history'
    vo_id = Column(UUID, primary_key=True)
    # Add other fields as needed

# Use this function to run your repository methods
async def main():
    async_session = sessionmaker(bind=your_database_engine, class_=AsyncSession)
    async with async_session() as session:
        knowledge_cache = KnowledgeCacheService()
        repository = CompositionRepository(session, knowledge_cache)
        
        # Call your repository methods here

if __name__ == "__main__":
    asyncio.run(main())
