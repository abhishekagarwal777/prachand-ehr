import logging
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List, BinaryIO
from xml.etree.ElementTree import ParseError

# Placeholder classes for types used in the Java code
class InvalidApiParameterException(Exception):
    pass

class StateConflictException(Exception):
    pass

class WebTemplate:
    pass

class OPERATIONALTEMPLATE:
    def __init__(self, template_id, concept, language, definition, description):
        self.template_id = template_id
        self.concept = concept
        self.language = language
        self.definition = definition
        self.description = description

class CacheProvider:
    INTROSPECT_CACHE = "INTROSPECT_CACHE"
    TEMPLATE_ID_UUID_CACHE = "TEMPLATE_ID_UUID_CACHE"
    TEMPLATE_UUID_ID_CACHE = "TEMPLATE_UUID_ID_CACHE"
    
    def evict(self, cache_name, key):
        pass

    def get(self, cache_name, key, fallback):
        pass

class TemplateUtils:
    @staticmethod
    def get_template_id(template):
        return template.template_id

    @staticmethod
    def is_supported(template):
        return True  # Placeholder, assumes template is supported for this example

    UNSUPPORTED_RM_TYPES = []

class TemplateStorage:
    def store_template(self, template):
        pass
    
    def read_operationaltemplate(self, key):
        return Optional.empty()

    def delete_template(self, template_id):
        return True

    def list_all_operational_templates(self):
        return []

    def find_template_id_by_uuid(self, uuid):
        return Optional.empty()

    def find_uuid_by_template_id(self, template_id):
        return Optional.empty()

class OPTParser:
    def __init__(self, template):
        self.template = template

    def parse(self):
        return WebTemplate()

# Python version of the service
class KnowledgeCacheService(ABC):
    @abstractmethod
    def add_operational_template(self, input_stream: BinaryIO) -> str:
        pass

    @abstractmethod
    def list_all_operational_templates(self) -> List:
        pass

    @abstractmethod
    def retrieve_operational_template(self, key: str) -> Optional[OPERATIONALTEMPLATE]:
        pass

    @abstractmethod
    def delete_operational_template(self, template: OPERATIONALTEMPLATE) -> bool:
        pass

    @abstractmethod
    def find_template_id_by_uuid(self, uuid: UUID) -> Optional[str]:
        pass

    @abstractmethod
    def find_uuid_by_template_id(self, template_id: str) -> Optional[UUID]:
        pass

class IntrospectService(ABC):
    @abstractmethod
    def get_query_opt_metadata(self, template_id: str) -> WebTemplate:
        pass

class KnowledgeCacheServiceImp(KnowledgeCacheService, IntrospectService):

    ELEMENT = "ELEMENT"

    def __init__(self, template_storage: TemplateStorage, cache_provider: CacheProvider, allow_template_overwrite=False):
        self.template_storage = template_storage
        self.cache_provider = cache_provider
        self.allow_template_overwrite = allow_template_overwrite
        self.log = logging.getLogger(__name__)

    def add_operational_template(self, input_stream: BinaryIO) -> str:
        template = self.build_operational_template(input_stream)
        return self._add_operational_template_internal(template, False)

    def build_operational_template(self, content: BinaryIO) -> OPERATIONALTEMPLATE:
        try:
            # Simulate parsing
            return OPERATIONALTEMPLATE("template_id", "concept", "language", "definition", "description")
        except (ParseError, IOError) as e:
            raise InvalidApiParameterException(e)

    def _add_operational_template_internal(self, template: OPERATIONALTEMPLATE, overwrite: bool) -> str:
        self.validate_template(template)

        try:
            template_id = TemplateUtils.get_template_id(template)
        except ValueError:
            raise InvalidApiParameterException("Invalid template input content")

        if not self.allow_template_overwrite and not overwrite and self.retrieve_operational_template(template_id):
            raise StateConflictException(f"Operational template with this template ID already exists: {template_id}")

        self.template_storage.store_template(template)
        
        if self.allow_template_overwrite and not overwrite:
            self.invalidate_cache(template)

        return template_id

    def admin_update_operational_template(self, content: BinaryIO) -> str:
        template = self.build_operational_template(content)
        return self._add_operational_template_internal(template, True)

    def invalidate_cache(self, template: OPERATIONALTEMPLATE) -> None:
        template_id = template.template_id
        uuid = self.find_uuid_by_template_id(template_id).or_else(None)
        self.cache_provider.evict(CacheProvider.INTROSPECT_CACHE, template_id)
        self.cache_provider.evict(CacheProvider.TEMPLATE_ID_UUID_CACHE, template_id)
        self.cache_provider.evict(CacheProvider.TEMPLATE_UUID_ID_CACHE, uuid)

    def list_all_operational_templates(self) -> List:
        return self.template_storage.list_all_operational_templates()

    def retrieve_operational_template(self, key: str) -> Optional[OPERATIONALTEMPLATE]:
        self.log.debug(f"retrieveOperationalTemplate({key})")
        return self.template_storage.read_operationaltemplate(key)

    def retrieve_operational_template_by_uuid(self, uuid: UUID) -> Optional[OPERATIONALTEMPLATE]:
        return self.find_template_id_by_uuid(uuid).flatmap(self.retrieve_operational_template)

    def delete_operational_template(self, template: OPERATIONALTEMPLATE) -> bool:
        deleted = self.template_storage.delete_template(template.template_id)
        if deleted:
            self.invalidate_cache(template)
        return deleted

    def find_template_id_by_uuid(self, uuid: UUID) -> Optional[str]:
        try:
            return self.cache_provider.get(
                CacheProvider.TEMPLATE_UUID_ID_CACHE, uuid, lambda: self.template_storage.find_template_id_by_uuid(uuid).or_else(None)
            )
        except KeyError:
            return None

    def find_uuid_by_template_id(self, template_id: str) -> Optional[UUID]:
        try:
            return self.cache_provider.get(
                CacheProvider.TEMPLATE_ID_UUID_CACHE, template_id, lambda: self.template_storage.find_uuid_by_template_id(template_id).or_else(None)
            )
        except KeyError:
            return None

    def get_query_opt_metadata(self, template_id: str) -> WebTemplate:
        try:
            return self.cache_provider.get(
                CacheProvider.INTROSPECT_CACHE, template_id, lambda: self.build_query_opt_metadata(template_id)
            )
        except KeyError as e:
            raise RuntimeError(e)

    def build_query_opt_metadata(self, template_id: str) -> WebTemplate:
        return self.retrieve_operational_template(template_id).map(self._build_query_opt_metadata).or_else(None)

    def _build_query_opt_metadata(self, operational_template: OPERATIONALTEMPLATE) -> WebTemplate:
        self.log.info(f"Updating WebTemplate cache for template: {operational_template.template_id}")
        try:
            return OPTParser(operational_template).parse()
        except Exception as e:
            raise ValueError(f"Invalid template: {e}")

    def delete_all_operational_templates(self) -> int:
        templates = self.template_storage.list_all_operational_templates()
        if not templates:
            return 0
        return sum(1 for template in templates if self.delete_operational_template(template))

    def validate_template(self, template: OPERATIONALTEMPLATE) -> None:
        if not template:
            raise InvalidApiParameterException("Could not parse input template")
        if not template.concept or not template.language or not template.definition:
            raise ValueError("Supplied template has nil or empty concept/language/definition")
        if not TemplateUtils.is_supported(template):
            raise ValueError(f"The supplied template is not supported (unsupported types: {TemplateUtils.UNSUPPORTED_RM_TYPES})")
