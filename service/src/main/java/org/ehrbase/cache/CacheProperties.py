from dataclasses import dataclass
from enum import Enum
from typing import Optional

class TimeUnit(Enum):
    MINUTES = 'minutes'
    SECONDS = 'seconds'
    HOURS = 'hours'

@dataclass
class ExpireTime:
    duration: int = 5
    unit: TimeUnit = TimeUnit.MINUTES

@dataclass
class CacheConfig:
    expire_after_access: Optional[ExpireTime] = None
    expire_after_write: Optional[ExpireTime] = None

@dataclass
class CacheProperties:
    template_init_on_startup: bool = True
    external_fhir_terminology_cache_config: CacheConfig = CacheConfig()
    user_id_cache_config: CacheConfig = CacheConfig()

    def is_template_init_on_startup(self) -> bool:
        return self.template_init_on_startup

    def set_template_init_on_startup(self, template_init_on_startup: bool):
        self.template_init_on_startup = template_init_on_startup

    def get_external_fhir_terminology_cache_config(self) -> CacheConfig:
        return self.external_fhir_terminology_cache_config

    def set_external_fhir_terminology_cache_config(self, config: CacheConfig):
        self.external_fhir_terminology_cache_config = config

    def get_user_id_cache_config(self) -> CacheConfig:
        return self.user_id_cache_config

    def set_user_id_cache_config(self, config: CacheConfig):
        self.user_id_cache_config = config

# Example usage
if __name__ == "__main__":
    cache_properties = CacheProperties(
        template_init_on_startup=True,
        external_fhir_terminology_cache_config=CacheConfig(
            expire_after_access=ExpireTime(duration=10, unit=TimeUnit.MINUTES),
            expire_after_write=ExpireTime(duration=5, unit=TimeUnit.SECONDS)
        ),
        user_id_cache_config=CacheConfig(
            expire_after_access=ExpireTime(duration=15, unit=TimeUnit.MINUTES)
        )
    )

    print("Template Init On Startup:", cache_properties.is_template_init_on_startup())
    print("External FHIR Terminology Cache Config:", cache_properties.get_external_fhir_terminology_cache_config())
    print("User ID Cache Config:", cache_properties.get_user_id_cache_config())
