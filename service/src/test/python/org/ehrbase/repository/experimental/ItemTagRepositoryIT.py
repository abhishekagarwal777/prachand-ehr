import uuid
from enum import Enum
from typing import List, Collection, Optional
import pytest

# Enum for Item Tag RM Types
class ItemTagRMType(Enum):
    COMPOSITION = "COMPOSITION"
    EHR_STATUS = "EHR_STATUS"


class ItemTagDto:
    """Data Transfer Object for Item Tag."""
    
    def __init__(self, id: Optional[uuid.UUID], owner_id: uuid.UUID, target: uuid.UUID,
                 target_type: ItemTagRMType, target_path: Optional[str], key: str,
                 value: Optional[str]):
        self.id = id
        self.owner_id = owner_id
        self.target = target
        self.target_type = target_type
        self.target_path = target_path
        self.key = key
        self.value = value


class ObjectNotFoundException(Exception):
    """Exception raised when an object is not found."""
    pass


class ItemTagRepository:
    """Simulated repository for Item Tags."""

    def bulk_store(self, item_tags: List[ItemTagDto]) -> Collection[uuid.UUID]:
        """Simulates storing item tags."""
        # Simulate insertion logic
        return [uuid.uuid4() for _ in item_tags]  # Returns new IDs for each item tag

    def admin_delete_all(self, ehr_id: uuid.UUID):
        """Simulates deleting all item tags for the given EHR."""
        pass  # Implement the deletion logic as needed

    def find_for_owner_and_target(self, ehr_id: uuid.UUID, target: uuid.UUID,
                                   type: ItemTagRMType, ids: Collection[uuid.UUID],
                                   keys: Collection[str]) -> List[ItemTagDto]:
        """Simulates finding item tags for a specific owner and target."""
        return []  # Implement logic to find item tags


@pytest.fixture
def setup_item_tag_repository():
    """Fixture to set up the Item Tag repository for testing."""
    yield ItemTagRepository()


@pytest.fixture
def setup_ehr():
    """Fixture to set up EHR for testing."""
    ehr_id = uuid.uuid4()
    return ehr_id


class TestItemTagRepository:
    """Test class for ItemTagRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, setup_item_tag_repository, setup_ehr):
        """Setup and teardown for each test."""
        self.item_tag_repository = setup_item_tag_repository
        self.ehr_id = setup_ehr

    def new_item_tag(self, owner_id: uuid.UUID, target: uuid.UUID,
                     type: ItemTagRMType, key: str) -> ItemTagDto:
        return ItemTagDto(None, owner_id, target, type, None, key, None)

    def bulk_store(self, *item_tags: ItemTagDto) -> Collection[uuid.UUID]:
        return self.item_tag_repository.bulk_store(list(item_tags))

    def test_bulk_store_empty_nop(self):
        ids = self.bulk_store()
        assert len(ids) == 0

    def test_bulk_store_insert_target_not_exist(self):
        ids = self.bulk_store(self.new_item_tag(self.ehr_id, uuid.uuid4(), ItemTagRMType.EHR_STATUS, "insert:comp:not_exist:1"))
        assert len(ids) == 1

    def test_bulk_store_insert_target_exist(self):
        comp_id = uuid.uuid4()  # Simulating existing composition ID
        ids = self.bulk_store(self.new_item_tag(self.ehr_id, comp_id, ItemTagRMType.COMPOSITION, "insert:comp:exist:2"))
        assert len(ids) == 1

    def test_bulk_store_update_target_exist(self):
        comp_id = uuid.uuid4()
        item_tag = self.new_item_tag(self.ehr_id, comp_id, ItemTagRMType.COMPOSITION, "update:comp:not_exist:1")
        insert_ids = self.bulk_store(item_tag)
        assert len(insert_ids) == 1

        tag_id = insert_ids[0]

        item_tag_to_update = ItemTagDto(tag_id, item_tag.owner_id, item_tag.target,
                                         item_tag.target_type, item_tag.target_path,
                                         item_tag.key, "new value")
        update_ids = self.bulk_store(item_tag_to_update)

        assert len(update_ids) == 1
        assert update_ids[0] == tag_id

    def test_bulk_store_insert_ehr_not_exist(self):
        item_tags = [ItemTagDto(None, uuid.UUID("7eb0db46-b72e-4db0-9955-05bb91275951"),
                                uuid.uuid4(), ItemTagRMType.COMPOSITION, None,
                                "update:comp:not_exist:1", None)]
        with pytest.raises(ObjectNotFoundException) as excinfo:
            self.item_tag_repository.bulk_store(item_tags)
        assert str(excinfo.value) == "EHR with id '7eb0db46-b72e-4db0-9955-05bb91275951' does not exist"

    def test_bulk_store_update_item_tag_exist_error(self):
        item_tag = ItemTagDto(uuid.UUID("7eb0db46-b72e-4db0-9955-05bb91275951"),
                               self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION,
                               None, "update:comp:not_exist:1", None)

        with pytest.raises(ObjectNotFoundException) as excinfo:
            self.bulk_store(item_tag)
        assert str(excinfo.value) == "ItemTag(s) with ID(s) [7eb0db46-b72e-4db0-9955-05bb91275951] not found"

    def test_find_for_owner_and_target(self):
        comp_id = uuid.uuid4()
        insert_ids = self.bulk_store(
            self.new_item_tag(self.ehr_id, comp_id, ItemTagRMType.COMPOSITION, "find:composition:tag"),
            self.new_item_tag(self.ehr_id, comp_id, ItemTagRMType.COMPOSITION, "other:composition:tag"),
            self.new_item_tag(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, "find:composition:tag"),
            self.new_item_tag(self.ehr_id, self.ehr_id, ItemTagRMType.EHR_STATUS, "find:ehr_status:tag"),
            self.new_item_tag(self.ehr_id, self.ehr_id, ItemTagRMType.EHR_STATUS, "other:ehr_status:tag")
        )
        assert len(insert_ids) == 5

        assert len(self.item_tag_repository.find_for_owner_and_target(uuid.uuid4(), comp_id, ItemTagRMType.COMPOSITION, [], [])) == 0

        comp_id_match = self.item_tag_repository.find_for_owner_and_target(self.ehr_id, comp_id, ItemTagRMType.COMPOSITION, [], [])
        assert len(comp_id_match) == 2
        assert comp_id_match[0].id == insert_ids[0]
        assert comp_id_match[1].id == insert_ids[1]

        comp_tag_id_match = self.item_tag_repository.find_for_owner_and_target(comp_id, ItemTagRMType.COMPOSITION, [], ["find:composition:tag"])
        assert len(comp_tag_id_match) == 1
        assert comp_tag_id_match[0].id == insert_ids[0]

        comp_tag_id_id_match = self.item_tag_repository.find_for_owner_and_target(comp_id, ItemTagRMType.COMPOSITION, [insert_ids[1]], [])
        assert len(comp_tag_id_id_match) == 1
        assert comp_tag_id_id_match[0].id == insert_ids[1]

        ehr_status_match = self.item_tag_repository.find_for_owner_and_target(self.ehr_id, ItemTagRMType.EHR_STATUS, [], [])
        assert len(ehr_status_match) == 2
        assert ehr_status_match[0].id == insert_ids[3]
        assert ehr_status_match[1].id == insert_ids[4]

    def test_bulk_delete_empty_nop(self):
        assert self.item_tag_repository.bulk_store(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, [])

    def test_bulk_delete_nop(self):
        insert_ids = self.bulk_store(
            self.new_item_tag(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, "some:composition:tag"),
            self.new_item_tag(self.ehr_id, uuid.uuid4(), ItemTagRMType.EHR_STATUS, "some:ehr_status:tag")
        )
        assert len(insert_ids) == 2

        self.item_tag_repository.admin_delete_all(self.ehr_id)

        assert len(self.item_tag_repository.find_for_owner_and_target(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, [], [])) == 0
        assert len(self.item_tag_repository.find_for_owner_and_target(self.ehr_id, self.ehr_id, ItemTagRMType.EHR_STATUS, [], [])) == 0

    @pytest.mark.parametrize("type,id", [
        (ItemTagRMType.EHR_STATUS, "ee77096d-8aae-41ae-8c80-1c14e8e66792"),
        (ItemTagRMType.COMPOSITION, "a8019d32-af8b-49ec-a8b8-9df87acb857c")
    ])
    def test_admin_delete(self, type: ItemTagRMType, id: str):
        target_id = uuid.UUID(id)

        insert_ids = self.bulk_store(
            self.new_item_tag(self.ehr_id, target_id, type, f"some:{type.value.lower()}:tag"),
            self.new_item_tag(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, "some:composition:tag"),
            self.new_item_tag(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, "some:composition:tag")
        )
        assert len(insert_ids) == 3

        self.item_tag_repository.admin_delete_all(target_id)

        assert len(self.item_tag_repository.find_for_owner_and_target(self.ehr_id, target_id, type, [], [])) == 0
        assert len(self.item_tag_repository.find_for_owner_and_target(self.ehr_id, uuid.uuid4(), ItemTagRMType.COMPOSITION, [], [])) == 2

    def test_delete_not_exist(self):
        with pytest.raises(ObjectNotFoundException) as excinfo:
            self.item_tag_repository.admin_delete_all(uuid.uuid4())
        assert str(excinfo.value) == "EHR with id 'uuid.UUID()' does not exist"
