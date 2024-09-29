from typing import Optional, Callable, TypeVar, Generic, Dict
from uuid import UUID
from jayway.jsonpath import DocumentContext
from my_exceptions import InternalServerException  # Custom exception import (create this module as needed)


# import sys
# sys.path.append('/path/to/your/module')
# from . import my_exceptions
# class MyCustomError(Exception):
#     pass
# from my_exceptions import MyCustomError

# def risky_function():
#     raise MyCustomError("An error occurred!")

# try:
#     risky_function()
# except MyCustomError as e:
#     print(e)



K = TypeVar('K')
V = TypeVar('V')

class EhrBaseCache(Generic[K, V]):
    def __init__(self, name: str, kex_class: type, value_class: type):
        self.name = name
        self.kex_class = kex_class
        self.value_class = value_class

class CacheManager:
    def __init__(self):
        self.caches: Dict[str, 'Cache'] = {}

    def get_cache(self, name: str) -> Optional['Cache']:
        return self.caches.get(name)

class Cache:
    def get(self, key: K, value_loader: Callable[[], V]) -> V:
        # Implement cache retrieval logic
        raise NotImplementedError("Cache retrieval logic not implemented")

    def evict(self, key: K):
        # Implement cache eviction logic
        raise NotImplementedError("Cache eviction logic not implemented")

class CacheProvider:
    INTROSPECT_CACHE = EhrBaseCache[str, 'WebTemplate']("introspectCache", str, 'WebTemplate')
    TEMPLATE_ID_UUID_CACHE = EhrBaseCache[str, UUID]("TemplateIdUuidCache", str, UUID)
    TEMPLATE_UUID_ID_CACHE = EhrBaseCache[UUID, str]("TemplateUuidIdCache", UUID, str)
    USER_ID_CACHE = EhrBaseCache[str, UUID]("userIdCache", str, UUID)
    EXTERNAL_FHIR_TERMINOLOGY_CACHE = EhrBaseCache[str, DocumentContext]("externalFhirTerminologyCache", str, DocumentContext)
    STORED_QUERY_CACHE = EhrBaseCache[str, 'QueryDefinitionResultDto']("StoredQueryCache", str, 'QueryDefinitionResultDto')

    def get(self, cache: EhrBaseCache[K, V], key: K, value_loader: Callable[[], V]) -> V:
        # Implement cache retrieval logic
        raise NotImplementedError("Cache retrieval logic not implemented")

    def evict(self, cache: EhrBaseCache[K, V], key: K):
        # Implement cache eviction logic
        raise NotImplementedError("Cache eviction logic not implemented")

class CacheProviderImp(CacheProvider):
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    def get(self, cache: EhrBaseCache[K, V], key: K, value_loader: Callable[[], V]) -> V:
        cache_instance = self.cache_manager.get_cache(cache.name)
        if cache_instance is None:
            raise self.get_exception(cache)
        return cache_instance.get(key, value_loader)

    def evict(self, cache: EhrBaseCache[K, V], key: K):
        cache_instance = self.cache_manager.get_cache(cache.name)
        if cache_instance is None:
            raise self.get_exception(cache)
        cache_instance.evict(key)

    @staticmethod
    def get_exception(cache: EhrBaseCache) -> InternalServerException:
        return InternalServerException(f"Non existing cache: {cache.name}")

# Example usage
if __name__ == "__main__":
    # Create a cache manager and add a cache instance for testing
    cache_manager = CacheManager()
    cache_manager.caches["introspectCache"] = Cache()  # Placeholder for actual Cache instance
    
    provider = CacheProviderImp(cache_manager)
    print("Cache Provider Imp initialized.")
