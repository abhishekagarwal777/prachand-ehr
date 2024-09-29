from abc import ABC, abstractmethod
from typing import List, Collection, Optional
import uuid

class ItemTagDto:
    # Placeholder for the ItemTagDto class definition.
    class ItemTagRMType:
        # Placeholder for the ItemTagRMType class definition.
        pass

class ItemTagService(ABC):
    @abstractmethod
    def bulk_upsert(
        self,
        owner_id: uuid.UUID,
        target_id: uuid.UUID,
        target_type: ItemTagDto.ItemTagRMType,
        item_tags_dto: List[ItemTagDto]
    ) -> List[uuid.UUID]:
        """Perform a bulk update/create operation for item tags."""
        pass

    @abstractmethod
    def find_item_tag(
        self,
        owner_id: uuid.UUID,
        target_id: uuid.UUID,
        target_type: ItemTagDto.ItemTagRMType,
        ids: Collection[uuid.UUID],
        keys: Collection[str]
    ) -> List[ItemTagDto]:
        """Perform a bulk get operation for item tags by IDs and/or keys."""
        pass

    @abstractmethod
    def bulk_delete(
        self,
        owner_id: uuid.UUID,
        target_id: uuid.UUID,
        target_type: ItemTagDto.ItemTagRMType,
        ids: Collection[uuid.UUID]
    ):
        """Perform a bulk delete operation for item tags by IDs."""
        pass
