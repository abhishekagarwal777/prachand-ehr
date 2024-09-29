from typing import List, Collection, Optional
import uuid

# Exception definitions
class UnprocessableEntityException(Exception):
    pass

class ValidationException(Exception):
    pass

class ItemTagRMType:
    # Placeholder for the ItemTagRMType enumeration or class
    pass

class ItemTagDto:
    def __init__(self, key: str, value: Optional[str], target_path: Optional[str], 
                 owner_id: Optional[uuid.UUID] = None, target: Optional[uuid.UUID] = None, 
                 target_type: Optional[ItemTagRMType] = None):
        self.key = key
        self.value = value
        self.target_path = target_path
        self.owner_id = owner_id
        self.target = target
        self.target_type = target_type

    def set_owner_id(self, owner_id: uuid.UUID):
        self.owner_id = owner_id

    def set_target(self, target: uuid.UUID):
        self.target = target

    def set_target_type(self, target_type: ItemTagRMType):
        self.target_type = target_type

class EhrService:
    def check_ehr_exists(self, owner_id: uuid.UUID):
        # Placeholder for EHR existence check implementation
        pass

class ItemTagRepository:
    def bulk_store(self, item_tags: List[ItemTagDto]) -> List[uuid.UUID]:
        # Placeholder for bulk store implementation
        return [uuid.uuid4() for _ in item_tags]  # Simulate generated UUIDs for each tag

    def find_for_owner_and_target(self, owner_id: uuid.UUID, target_vo_id: uuid.UUID, 
                                  target_type: ItemTagRMType, ids: Collection[uuid.UUID], 
                                  keys: Collection[str]) -> List[ItemTagDto]:
        # Placeholder for finding item tags implementation
        return []

    def bulk_delete(self, owner_id: uuid.UUID, target_vo_id: uuid.UUID, 
                    target_type: ItemTagRMType, ids: Collection[uuid.UUID]):
        # Placeholder for bulk delete implementation
        pass

class ItemTagService:
    # Placeholder for the ItemTagService interface
    pass

class ItemTagServiceImpl(ItemTagService):
    def __init__(self, item_tag_repository: ItemTagRepository, ehr_service: EhrService):
        self.item_tag_repository = item_tag_repository
        self.ehr_service = ehr_service

    def bulk_upsert(self, owner_id: uuid.UUID, target_id: uuid.UUID, 
                    target_type: ItemTagRMType, item_tags: List[ItemTagDto]) -> List[uuid.UUID]:
        if not item_tags:
            return []

        # Sanity check for existing EHR version
        self.ehr_service.check_ehr_exists(owner_id)

        # Validate and collect errors
        for dto in item_tags:
            self.fill_and_validate_dto(dto, owner_id, target_id, target_type)

        return self.item_tag_repository.bulk_store(item_tags)

    def find_item_tag(self, owner_id: uuid.UUID, target_vo_id: uuid.UUID, 
                      target_type: ItemTagRMType, ids: Collection[uuid.UUID], 
                      keys: Collection[str]) -> List[ItemTagDto]:
        # Sanity check for existing EHR version
        self.ehr_service.check_ehr_exists(owner_id)

        return self.item_tag_repository.find_for_owner_and_target(owner_id, target_vo_id, target_type, ids, keys)

    def bulk_delete(self, owner_id: uuid.UUID, target_vo_id: uuid.UUID, 
                    target_type: ItemTagRMType, ids: Collection[uuid.UUID]):
        if not ids:
            return

        # Sanity check for existing EHR version
        self.ehr_service.check_ehr_exists(owner_id)

        self.item_tag_repository.bulk_delete(owner_id, target_vo_id, target_type, ids)

    @staticmethod
    def fill_and_validate_dto(dto: ItemTagDto, owner_id: uuid.UUID, 
                              target_vo_id: uuid.UUID, target_type: ItemTagRMType):
        key = dto.key
        value = dto.value
        target_path = dto.target_path

        # Changing the owner is not supported - we keep the EHR for the tag
        if dto.owner_id is not None and dto.owner_id != owner_id:
            raise UnprocessableEntityException(
                f"Owner mismatch for ItemTag '{key}': {dto.owner_id} vs. {owner_id}")

        # Changing the target is not supported - we keep the EHR for the tag
        if dto.target is not None and dto.target != target_vo_id:
            raise ValidationException(
                f"Target mismatch for ItemTag '{key}': {dto.target} vs. {target_vo_id}")

        # Tag validation
        ItemTagServiceImpl.validate_tag_key(key)
        ItemTagServiceImpl.validate_tag_value(key, value)
        ItemTagServiceImpl.validate_target_path(key, target_path)
        ItemTagServiceImpl.validate_target_type(dto, target_type)

        dto.set_owner_id(owner_id)
        dto.set_target(target_vo_id)
        dto.set_target_type(target_type)

    @staticmethod
    def validate_tag_key(key: str):
        if not key or key.strip() == "":
            raise UnprocessableEntityException("ItemTag key must not be blank")
        if not all(c.isalnum() or c in "-_/" for c in key):
            raise UnprocessableEntityException(
                f"ItemTag key '{key}' contains invalid characters, only alphanumerics, minus, slash, underscore are allowed")

    @staticmethod
    def validate_tag_value(key: str, value: Optional[str]):
        if value is not None and value.strip() == "":
            raise UnprocessableEntityException(f"ItemTag '{key}' value must not be blank")

    @staticmethod
    def validate_target_path(key: str, target_path: Optional[str]):
        if target_path is None:
            return
        if not target_path.startswith("/"):
            raise UnprocessableEntityException(
                f"ItemTag '{key}' target_path '{target_path}' does not start at root")
        if len(target_path) < 2:
            raise UnprocessableEntityException(
                f"ItemTag '{key}' target_path cannot target '/', use null instead")

        # Path validation logic to be implemented
        # This can include parsing the path and validating its structure
        # Placeholder for path validation; needs detailed implementation based on actual rules
        if ' OR ' in target_path:  # Simple check for unsupported OR predicates
            raise UnprocessableEntityException(
                f"ItemTag '{key}' target_path '{target_path}': OR predicates are not supported")

    @staticmethod
    def validate_target_type(item_tag: ItemTagDto, target_type: ItemTagRMType):
        tag_type = item_tag.target_type
        if tag_type is not None and tag_type != target_type:
            raise ValidationException(f"target_type does not match {target_type}")
