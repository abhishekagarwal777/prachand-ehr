from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session
from cachetools import cached, TTLCache
from aql_query_parser import AqlParseException, AqlQueryParser  # Assume these are the appropriate AQL parsing modules
from custom_exceptions import (
    GeneralRequestProcessingException,
    InvalidApiParameterException,
    InternalServerException,
    ObjectNotFoundException,
    StateConflictException
)  # Custom exceptions
from semver import SemVer, SemVerUtil  # Assuming a semver library that works like Java's SemVer
from stored_query_repository import StoredQueryRepository  # Assuming this class exists for repository access
from functools import lru_cache


class CacheProvider:
    """
    CacheProvider is a placeholder class for handling cache functionality.
    """
    STORED_QUERY_CACHE = "stored_query_cache"

    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=300)  # Example cache

    @cached(cache={})
    def get(self, cache_name, key, func):
        try:
            if key not in self.cache:
                self.cache[key] = func()
            return self.cache[key]
        except Exception as e:
            raise GeneralRequestProcessingException(f"Cache Access Error: {str(e)}")

    def evict(self, cache_name, key):
        if key in self.cache:
            del self.cache[key]


class StoredQueryServiceImp:
    """
    Python equivalent of the StoredQueryServiceImp class in Java.
    Provides stored query management: retrieval, creation, and deletion of stored queries.
    """

    def __init__(self, stored_query_repository: StoredQueryRepository, cache_provider: CacheProvider):
        self.stored_query_repository = stored_query_repository
        self.cache_provider = cache_provider

    def retrieve_stored_queries(self, fully_qualified_name: str):
        name = fully_qualified_name if fully_qualified_name else None
        try:
            return self.stored_query_repository.retrieve_qualified_list(name)
        except DataError as e:
            raise GeneralRequestProcessingException(f"Data Access Error: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Could not retrieve stored query, reason: {str(e)}") from e

    def retrieve_stored_query(self, qualified_name: str, version: str):
        requested_version = self._parse_request_semver(version)
        stored_query_qualified_name = StoredQueryQualifiedName.create(qualified_name, requested_version)
        try:
            return self.cache_provider.get(
                CacheProvider.STORED_QUERY_CACHE,
                stored_query_qualified_name.to_qualified_name_string(),
                lambda: self._retrieve_stored_query_internal(stored_query_qualified_name)
            )
        except KeyError as e:
            raise GeneralRequestProcessingException(f"Cache Access Error: {str(e)}") from e

    def _retrieve_stored_query_internal(self, stored_query_qualified_name):
        try:
            stored_query_access = self.stored_query_repository.retrieve_qualified(stored_query_qualified_name)
            return stored_query_access if stored_query_access else None
        except DataError as e:
            raise GeneralRequestProcessingException(f"Data Access Error: {str(e)}") from e
        except Exception as e:
            raise InternalServerException(str(e)) from e

    def create_stored_query(self, qualified_name: str, version: str, query_string: str):
        requested_version = self._parse_request_semver(version)
        query_qualified_name = StoredQueryQualifiedName.create(qualified_name, requested_version)

        # Validate the query syntax using AQL parser
        try:
            AqlQueryParser.parse(query_string)
        except AqlParseException as e:
            raise ValueError(f"Invalid query, reason: {str(e)}") from e

        # Lookup version in the database
        db_semver = self.stored_query_repository.retrieve_qualified(query_qualified_name).map(
            lambda q: SemVer.parse(q.get_version())
        ) or SemVer.NO_VERSION

        self._check_version_combination(requested_version, db_semver)

        new_version = SemVerUtil.determine_version(requested_version, db_semver)
        new_query_qualified_name = StoredQueryQualifiedName.create(qualified_name, new_version)

        is_update = db_semver.is_pre_release()

        try:
            if is_update:
                self.stored_query_repository.update(new_query_qualified_name, query_string)
            else:
                self.stored_query_repository.store(new_query_qualified_name, query_string)
        except DataError as e:
            raise GeneralRequestProcessingException(f"Data Access Error: {str(e)}") from e
        except VersionConflictException as e:
            raise ValueError(str(e)) from e

        # Clear partially cached versions
        self._evict_partially_cached_versions(qualified_name, new_version)

        return self._retrieve_stored_query_internal(new_query_qualified_name)

    def delete_stored_query(self, qualified_name: str, version: str):
        requested_version = self._parse_request_semver(version)
        if requested_version.is_no_version() or requested_version.is_partial():
            raise InvalidApiParameterException("A qualified version has to be specified")

        stored_query_qualified_name = StoredQueryQualifiedName.create(qualified_name, requested_version)

        try:
            self.stored_query_repository.delete(stored_query_qualified_name)
        except ObjectNotFoundException as e:
            raise e
        except DataError as e:
            raise GeneralRequestProcessingException(f"Data Access Error: {str(e)}") from e
        except Exception as e:
            raise InternalServerException(str(e)) from e
        finally:
            self.cache_provider.evict(CacheProvider.STORED_QUERY_CACHE, stored_query_qualified_name.to_qualified_name_string())

    def _evict_partially_cached_versions(self, qualified_name: str, sem_ver: SemVer):
        version_major = SemVer(sem_ver.major, None, None, None)
        version_major_minor = SemVer(sem_ver.major, sem_ver.minor, None, None)

        self.cache_provider.evict(
            CacheProvider.STORED_QUERY_CACHE,
            StoredQueryQualifiedName.create(qualified_name, version_major).to_qualified_name_string()
        )
        self.cache_provider.evict(
            CacheProvider.STORED_QUERY_CACHE,
            StoredQueryQualifiedName.create(qualified_name, version_major_minor).to_qualified_name_string()
        )

    @staticmethod
    def _parse_request_semver(version: str):
        try:
            return SemVer.parse(version)
        except Exception as e:
            raise InvalidApiParameterException("Incorrect version. Use the SEMVER format.") from e

    @staticmethod
    def _check_version_combination(request_semver: SemVer, db_semver: SemVer):
        if db_semver.is_no_version():
            return
        elif db_semver.is_partial():
            raise IllegalStateException("The database contains stored queries with partial versions")
        elif db_semver.is_pre_release():
            if not request_semver.is_pre_release():
                raise RuntimeError(
                    f"Pre-release {db_semver} was provided when {request_semver} was requested"
                )
        elif db_semver.is_release():
            if request_semver.is_pre_release():
                raise RuntimeError(
                    f"Version {db_semver} was provided when pre-release {request_semver} was requested"
                )
            elif request_semver.is_release():
                raise StateConflictException("Version already exists")


# Example Usage
cache_provider = CacheProvider()
stored_query_repository = StoredQueryRepository()  # Assuming this is the actual repository

stored_query_service = StoredQueryServiceImp(stored_query_repository, cache_provider)

# Example method calls
try:
    stored_queries = stored_query_service.retrieve_stored_queries("some_query_name")
    print(stored_queries)
except Exception as e:
    print(str(e))
