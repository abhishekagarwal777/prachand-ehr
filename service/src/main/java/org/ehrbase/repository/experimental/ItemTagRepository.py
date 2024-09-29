from typing import List, Collection, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from EHR.dto.experimental import ItemTagDto
from EHR.dto.experimental import ItemTagDto.ItemTagRMType
from EHR.exception import ObjectNotFoundException
from EHR.enums import EhrItemTagTargetType
from EHR.models import EhrItemTag
from EHR.service import TimeProvider
from EHR.util import UuidGenerator


class ItemTagRepository:
    """Repository responsible for ITEM_TAG persistence."""

    def __init__(self, session: Session, time_provider: TimeProvider):
        self.session = session
        self.time_provider = time_provider

    def bulk_store(self, item_tags: List[ItemTagDto]) -> List[UUID]:
        """Stores the given ItemTagDtos by performing an Insert for new tags 
        or Update for existing tags.

        Args:
            item_tags: List of ItemTagDto to store.

        Returns:
            List of stored ItemTagDto IDs.
        """
        if not item_tags:
            return []

        new_tags = [self.new_record_for_tag(tag) for tag in item_tags if tag.id is None]

        existing_tags_by_id = {
            tag.id: tag for tag in item_tags if tag.id is not None
        }

        existing_tags = self.session.query(EhrItemTag).filter(
            EhrItemTag.id.in_(existing_tags_by_id.keys())
        ).all()

        for db_record in existing_tags:
            item_tag = existing_tags_by_id.pop(db_record.id, None)
            if item_tag:
                self.map_item_tag(item_tag, db_record)

        if existing_tags_by_id:
            raise ObjectNotFoundException(
                "ItemTag(s) with ID(s) %s not found" % list(existing_tags_by_id.keys())
            )

        self.bulk_insert(new_tags)
        self.session.bulk_save_objects(existing_tags)
        self.session.commit()

        # retain order of itemTags parameter
        it = iter(new_tags)
        return [
            tag.id if tag.id is not None else next(it).id for tag in item_tags
        ]

    def find_for_owner_and_target(
            self,
            owner_id: UUID,
            target_vo_id: UUID,
            target_type: ItemTagRMType,
            ids: Collection[UUID],
            keys: Collection[str]
    ) -> Collection[ItemTagDto]:
        """Search ItemTagDtos of ownerId for the latest version of the given targetVoId 
        by applying the optional filter for ids, keys.

        Args:
            owner_id: Identifier of owner object, such as EHR.
            target_vo_id: VERSIONED_OBJECT<T> Identifier of target.
            target_type: Type of the target object.
            ids: Identifier ItemTag to search for.
            keys: ItemTag keys to search for.

        Returns:
            Collection of ItemTagDto.
        """
        query = self.session.query(EhrItemTag).filter(
            EhrItemTag.ehr_id == owner_id,
            EhrItemTag.target_type == self.item_target_type_to_db_enum(target_type),
            EhrItemTag.target_vo_id == target_vo_id
        )

        if ids:
            query = query.filter(EhrItemTag.id.in_(ids))
        if keys:
            query = query.filter(EhrItemTag.key.in_(keys))

        return [self.record_as_item_tag(record) for record in query.all()]

    def bulk_delete(
            self,
            owner_id: UUID,
            target_vo_id: UUID,
            target_type: ItemTagRMType,
            ids: Collection[UUID]
    ) -> int:
        """Bulk delete ItemTagDtos with the given ids.

        Args:
            owner_id: Identifier of owner object.
            target_vo_id: VERSIONED_OBJECT<T> Identifier of target.
            target_type: Type of the target object.
            ids: Identifier of ItemTag to delete.

        Returns:
            Number of deleted records.
        """
        if not ids:
            return 0

        result = self.session.query(EhrItemTag).filter(
            EhrItemTag.ehr_id == owner_id,
            EhrItemTag.target_type == self.item_target_type_to_db_enum(target_type),
            EhrItemTag.target_vo_id == target_vo_id,
            EhrItemTag.id.in_(ids)
        ).delete(synchronize_session=False)

        self.session.commit()
        return result

    def admin_delete(self, target_id: UUID, target_type: ItemTagRMType) -> None:
        """Admin delete for a specific target ID.

        Args:
            target_id: Target identifier.
            target_type: Type of the target object.
        """
        self.session.query(EhrItemTag).filter(
            EhrItemTag.target_vo_id == target_id,
            EhrItemTag.target_type == self.item_target_type_to_db_enum(target_type)
        ).delete()

        self.session.commit()

    def admin_delete_all(self, ehr_id: UUID) -> None:
        """Admin delete all ItemTags for a specific EHR ID.

        Args:
            ehr_id: Identifier of EHR.
        """
        self.session.query(EhrItemTag).filter(
            EhrItemTag.ehr_id == ehr_id
        ).delete()

        self.session.commit()

    def bulk_insert(self, records: List[EhrItemTag]) -> None:
        """Bulk insert ItemTag records.

        Args:
            records: List of EhrItemTag records to insert.
        """
        if not records:
            return

        try:
            self.session.bulk_save_objects(records)
            self.session.commit()
        except Exception as e:  # Catch specific exceptions if needed
            details = str(e).split("[(|)]")
            raise ObjectNotFoundException(
                "EHR with id '%s' does not exist" % details[-2]
            )

    def new_record_for_tag(self, item_tag: ItemTagDto) -> EhrItemTag:
        """Create a new record for the ItemTagDto.

        Args:
            item_tag: ItemTagDto to convert.

        Returns:
            New EhrItemTag record.
        """
        item_tag_record = EhrItemTag()
        self.map_item_tag(item_tag, item_tag_record)
        item_tag_record.creation_date = self.time_provider.get_now()
        return item_tag_record

    def map_item_tag(self, item_tag: ItemTagDto, item_tag_record: EhrItemTag) -> None:
        """Map ItemTagDto to EhrItemTag record.

        Args:
            item_tag: ItemTagDto to map.
            item_tag_record: EhrItemTag record to populate.
        """
        item_tag_record.id = item_tag.id or UuidGenerator.random_uuid()
        item_tag_record.ehr_id = item_tag.owner_id
        item_tag_record.target_vo_id = item_tag.target
        item_tag_record.target_type = self.item_target_type_to_db_enum(item_tag.target_type)
        item_tag_record.key = item_tag.key
        item_tag_record.value = item_tag.value
        item_tag_record.target_path = item_tag.target_path
        item_tag_record.sys_period_lower = self.time_provider.get_now()

    @staticmethod
    def record_as_item_tag(db_record: EhrItemTag) -> ItemTagDto:
        """Convert a database record to an ItemTagDto.

        Args:
            db_record: EhrItemTag database record.

        Returns:
            Corresponding ItemTagDto.
        """
        return ItemTagDto(
            id=db_record.id,
            owner_id=db_record.ehr_id,
            target=db_record.target_vo_id,
            target_type=ItemTagRepository.db_enum_to_target_type(db_record.target_type),
            target_path=db_record.target_path,
            key=db_record.key,
            value=db_record.value
        )

    @staticmethod
    def db_enum_to_target_type(db_enum: EhrItemTagTargetType) -> ItemTagRMType:
        """Convert database enum to ItemTagRMType.

        Args:
            db_enum: EhrItemTagTargetType enum.

        Returns:
            Corresponding ItemTagRMType.
        """
        return {
            EhrItemTagTargetType.ehr_status: ItemTagRMType.EHR_STATUS,
            EhrItemTagTargetType.composition: ItemTagRMType.COMPOSITION
        }.get(db_enum)

    @staticmethod
    def item_target_type_to_db_enum(type_: ItemTagRMType) -> EhrItemTagTargetType:
        """Convert ItemTagRMType to database enum.

        Args:
            type_: ItemTagRMType.

        Returns:
            Corresponding EhrItemTagTargetType.
        """
        return {
            ItemTagRMType.EHR_STATUS: EhrItemTagTargetType.ehr_status,
            ItemTagRMType.COMPOSITION: EhrItemTagTargetType.composition
        }.get(type_)
