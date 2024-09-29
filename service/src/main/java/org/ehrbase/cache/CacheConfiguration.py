from typing import Callable
from cachetools import Cache
from cachetools.cached import cached
from cachetools.keys import hashkey
from dataclasses import dataclass
from functools import wraps

# Placeholder for CacheProvider
class CacheProvider:
    class EhrBaseCache:
        INTROSPECT_CACHE = "introspect_cache"
        TEMPLATE_UUID_ID_CACHE = "template_uuid_id_cache"
        TEMPLATE_ID_UUID_CACHE = "template_id_uuid_cache"
        USER_ID_CACHE = "user_id_cache"
        EXTERNAL_FHIR_TERMINOLOGY_CACHE = "external_fhir_terminology_cache"
        STORED_QUERY_CACHE = "stored_query_cache"

@dataclass
class CacheProperties:
    class CacheConfig:
        expire_after_write: int = None
        expire_after_access: int = None

    user_id_cache_config: CacheConfig = CacheConfig()
    external_fhir_terminology_cache_config: CacheConfig = CacheConfig()

class CacheManager:
    def __init__(self):
        self.caches = {}

    def register_custom_cache(self, name: str, cache: Cache):
        self.caches[name] = cache

    def get_cache(self, name: str) -> Cache:
        return self.caches.get(name)

class CacheConfiguration:
    def __init__(self, cache_properties: CacheProperties):
        self.cache_properties = cache_properties
        self.cache_manager = CacheManager()
        self.configure_caffeine_cache_manager()

    def configure_caffeine_cache_manager(self):
        self.cache_manager.register_custom_cache(
            CacheProvider.EhrBaseCache.INTROSPECT_CACHE,
            Cache()
        )
        self.cache_manager.register_custom_cache(
            CacheProvider.EhrBaseCache.TEMPLATE_UUID_ID_CACHE,
            Cache()
        )
        self.cache_manager.register_custom_cache(
            CacheProvider.EhrBaseCache.TEMPLATE_ID_UUID_CACHE,
            Cache()
        )
        self.cache_manager.register_custom_cache(
            CacheProvider.EhrBaseCache.USER_ID_CACHE,
            self.configure_cache(Cache(), self.cache_properties.user_id_cache_config)
        )
        self.cache_manager.register_custom_cache(
            CacheProvider.EhrBaseCache.EXTERNAL_FHIR_TERMINOLOGY_CACHE,
            self.configure_cache(Cache(), self.cache_properties.external_fhir_terminology_cache_config)
        )
        self.cache_manager.register_custom_cache(
            CacheProvider.EhrBaseCache.STORED_QUERY_CACHE,
            Cache()
        )

    def configure_cache(self, cache: Cache, cache_config: CacheProperties.CacheConfig) -> Cache:
        if cache_config.expire_after_write is not None:
            cache.ttl = cache_config.expire_after_write
        if cache_config.expire_after_access is not None:
            cache.maxsize = cache_config.expire_after_access
        return cache

# Example usage
if __name__ == "__main__":
    cache_props = CacheProperties(
        user_id_cache_config=CacheProperties.CacheConfig(expire_after_write=300, expire_after_access=600),
        external_fhir_terminology_cache_config=CacheProperties.CacheConfig(expire_after_write=300)
    )
    cache_config = CacheConfiguration(cache_props)
