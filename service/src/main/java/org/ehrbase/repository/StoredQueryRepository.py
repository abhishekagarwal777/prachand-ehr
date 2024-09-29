from sqlalchemy import select, and_, desc, Table
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Stream

class InternalServerException(Exception):
    pass

class ObjectNotFoundException(Exception):
    pass

class QueryDefinitionResultDto:
    def __init__(self):
        self.saved = None
        self.qualified_name = None
        self.version = None
        self.query_text = None
        self.type = None

class StoredQueryQualifiedName:
    def __init__(self, reverse_domain_name: str, semantic_id: str, semver: str):
        self._reverse_domain_name = reverse_domain_name
        self._semantic_id = semantic_id
        self._semver = semver

    def reverse_domain_name(self):
        return self._reverse_domain_name

    def semantic_id(self):
        return self._semantic_id

    def sem_ver(self):
        return self._semver

class StoredQueryRepository:
    def __init__(self, session: Session, time_provider):
        self.session = session
        self.time_provider = time_provider

    def store(self, stored_query_qualified_name: StoredQueryQualifiedName, source_aql_text: str):
        stored_query_record = self.create_stored_query_record(stored_query_qualified_name, source_aql_text)
        self.session.add(stored_query_record)
        self.session.commit()

    def update(self, stored_query_qualified_name: StoredQueryQualifiedName, source_aql_text: str):
        stored_query_record = self.create_stored_query_record(stored_query_qualified_name, source_aql_text)
        self.session.merge(stored_query_record)
        self.session.commit()

    def retrieve_qualified(self, stored_query_qualified_name: StoredQueryQualifiedName) -> Optional[QueryDefinitionResultDto]:
        stored_query_record = self.retrieve_stored_query_record(stored_query_qualified_name)
        if stored_query_record:
            return self.map_to_query_definition_dto(stored_query_record)
        return None

    def delete(self, stored_query_qualified_name: StoredQueryQualifiedName):
        stored_query = self.retrieve_stored_query_record(stored_query_qualified_name)
        if not stored_query:
            raise ObjectNotFoundException(
                "STORED_QUERY",
                f"No Stored Query with {stored_query_qualified_name.semantic_id()} and {stored_query_qualified_name.sem_ver()}"
            )
        self.session.delete(stored_query)
        self.session.commit()

    def retrieve_qualified_list(self, qualified_query_name: str) -> List[QueryDefinitionResultDto]:
        query = select(StoredQueryRecord).where(self.build_conditions(qualified_query_name))
        result = self.session.execute(query).scalars().all()
        return [self.map_to_query_definition_dto(record) for record in result]

    def map_to_query_definition_dto(self, stored_query_record) -> QueryDefinitionResultDto:
        dto = QueryDefinitionResultDto()
        dto.saved = stored_query_record.creation_date  # Assume datetime object
        dto.qualified_name = f"{stored_query_record.reverse_domain_name}::{stored_query_record.semantic_id}"
        dto.version = stored_query_record.semver
        dto.query_text = stored_query_record.query_text
        dto.type = stored_query_record.type
        return dto

    def build_conditions(self, qualified_query_name: str):
        # Implementation of condition building based on qualified_query_name
        conditions = []
        if qualified_query_name:
            parts = qualified_query_name.split("::")
            if len(parts) > 1:
                conditions.append(StoredQueryRecord.reverse_domain_name == parts[0])
                conditions.append(StoredQueryRecord.semantic_id == parts[1])
            else:
                conditions.append(StoredQueryRecord.semantic_id == qualified_query_name)

        return and_(*conditions)

    def create_stored_query_record(self, stored_query_qualified_name: StoredQueryQualifiedName, source_aql_text: str):
        stored_query_record = StoredQueryRecord()
        stored_query_record.reverse_domain_name = stored_query_qualified_name.reverse_domain_name()
        stored_query_record.semantic_id = stored_query_qualified_name.semantic_id()
        stored_query_record.semver = stored_query_qualified_name.sem_ver()
        stored_query_record.query_text = source_aql_text
        stored_query_record.type = "AQL"
        stored_query_record.creation_date = self.time_provider.get_now()  # Assuming this returns a datetime object
        return stored_query_record

    def retrieve_stored_query_record(self, stored_query_qualified_name: StoredQueryQualifiedName):
        # Fetch stored query record based on the stored_query_qualified_name
        conditions = and_(
            StoredQueryRecord.reverse_domain_name == stored_query_qualified_name.reverse_domain_name(),
            StoredQueryRecord.semantic_id == stored_query_qualified_name.semantic_id(),
            StoredQueryRecord.semver == stored_query_qualified_name.sem_ver()
        )
        result = self.session.execute(select(StoredQueryRecord).where(conditions)).scalars().first()
        return result
