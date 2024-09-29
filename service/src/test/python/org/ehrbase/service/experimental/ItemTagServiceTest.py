import uuid
from typing import List, Collection
import pytest
from unittest import mock

# Assuming we have the equivalent classes and exceptions defined in Python
from ehrbase.api.dto.experimental import ItemTagDto
from ehrbase.api.exception import ObjectNotFoundException, UnprocessableEntityException, ValidationException
from ehrbase.api.service import EhrService
from ehrbase.service.experimental import ItemTagService, ItemTagServiceImpl
from ehrbase.repository.experimental import ItemTagRepository
from ehrbase.util import UuidGenerator

SAMPLE_EHR_ID = uuid.UUID("90867c82-8498-4536-b2b6-16ea4e62818f")


@pytest.fixture
def mock_item_tag_repository():
    return mock.Mock(spec=ItemTagRepository)


@pytest.fixture
def mock_ehr_service():
    return mock.Mock(spec=EhrService)


@pytest.fixture
def item_tag_service(mock_item_tag_repository, mock_ehr_service):
    return ItemTagServiceImpl(mock_item_tag_repository, mock_ehr_service)


def item_tag_dto(key: str) -> ItemTagDto:
    return ItemTagDto(None, None, None, None, None, key, None)


def test_bulk_upsert_empty_list_nop(item_tag_service):
    ids = item_tag_service.bulk_upsert(
        SAMPLE_EHR_ID, uuid.UUID("6d4622d6-ecbb-456a-981a-59423a374a2e"), ItemTagDto.ItemTagRMType.COMPOSITION, []
    )
    assert len(ids) == 0


@pytest.mark.parametrize("type, target_id", [
    ("EHR_STATUS", "90867c82-8498-4536-b2b6-16ea4e62818f"),
    ("COMPOSITION", "6d4622d6-ecbb-456a-981a-59423a374a2e"),
])
def test_bulk_upsert_ehr_not_exist_error(item_tag_service, type, target_id):
    target = uuid.UUID(target_id)
    target_type = ItemTagDto.ItemTagRMType[type]

    with pytest.raises(ObjectNotFoundException):
        item_tag_service.bulk_upsert(SAMPLE_EHR_ID, target, target_type, [item_tag_dto("some:key")])


def test_bulk_updater_change_of_owner_error(item_tag_service):
    item_tags = [
        ItemTagDto(
            uuid.uuid4(),
            uuid.UUID("1dc42f91-094a-43e7-8c26-3ca6d43b8833"),
            SAMPLE_EHR_ID,
            ItemTagDto.ItemTagRMType.EHR_STATUS,
            None,
            "a:key",
            None
        )
    ]

    with pytest.raises(UnprocessableEntityException) as excinfo:
        item_tag_service.bulk_upsert(SAMPLE_EHR_ID, SAMPLE_EHR_ID, ItemTagDto.ItemTagRMType.EHR_STATUS, item_tags)
    assert "Owner mismatch for ItemTag 'a:key': 1dc42f91-094a-43e7-8c26-3ca6d43b8833 vs. {}".format(SAMPLE_EHR_ID) == str(excinfo.value)


def test_build_update_target_type_mismatch(item_tag_service):
    item_tags = [
        ItemTagDto(
            uuid.uuid4(),
            SAMPLE_EHR_ID,
            uuid.UUID("f5fe8b05-2fe3-4962-a0b7-d443e0b53304"),
            ItemTagDto.ItemTagRMType.COMPOSITION,
            None,
            "some:key",
            None
        )
    ]

    with pytest.raises(ValidationException) as excinfo:
        item_tag_service.bulk_upsert(SAMPLE_EHR_ID, uuid.UUID("f5fe8b05-2fe3-4962-a0b7-d443e0b53304"), ItemTagDto.ItemTagRMType.EHR_STATUS, item_tags)
    assert "target_type does not match EHR_STATUS" == str(excinfo.value)


@pytest.mark.parametrize("type, target_id", [
    ("EHR_STATUS", "1a598f7a-fbc2-4762-9fae-6480390b9bb5"),
    ("COMPOSITION", "9448b3b8-866f-4415-97d2-d5605a553e45"),
])
def test_bulk_upsert(item_tag_service, type, target_id):
    target = uuid.UUID(target_id)
    target_type = ItemTagDto.ItemTagRMType[type]

    mock_ehr_service().check_ehr_exists(SAMPLE_EHR_ID)

    tag_id = uuid.UUID("49532718-9a4f-4c3c-a1ad-86af95a1751c")
    item_tags = [
        item_tag_dto("1:new:key"),
        ItemTagDto(tag_id, None, None, None, None, "2:existing:key", None)
    ]

    fixture_ids = [UuidGenerator.random_uuid(), tag_id]
    mock_item_tag_repository().bulk_store.return_value = fixture_ids

    ids = item_tag_service.bulk_upsert(SAMPLE_EHR_ID, target, target_type, item_tags)
    assert ids == fixture_ids

    mock_item_tag_repository().bulk_store.assert_called_once()
    stored_tags = mock_item_tag_repository().bulk_store.call_args[0][0]
    stored_tags = sorted(stored_tags, key=lambda x: x.key)
    assert len(stored_tags) == 2
    assert stored_tags[0] == ItemTagDto(None, SAMPLE_EHR_ID, target, target_type, None, "1:new:key", None)
    assert stored_tags[1] == ItemTagDto(tag_id, SAMPLE_EHR_ID, target, target_type, None, "2:existing:key", None)


@pytest.mark.parametrize("type, target_id", [
    ("EHR_STATUS", "422f7ddf-5646-4db8-b984-2df23d5021da"),
    ("COMPOSITION", "6d4622d6-ecbb-456a-981a-59423a374a2e"),
])
def test_find_ehr_not_exist_error(item_tag_service, type, target_id):
    target = uuid.UUID(target_id)
    target_type = ItemTagDto.ItemTagRMType[type]

    with pytest.raises(ObjectNotFoundException):
        item_tag_service.find_item_tag(SAMPLE_EHR_ID, target, target_type, [], [])


@pytest.mark.parametrize("type, target_id, key", [
    ("EHR_STATUS", "90867c82-8498-4536-b2b6-16ea4e62818f", "tag::1"),
    ("COMPOSITION", "7eb105ca-d671-4220-9103-d08db0403dc0", "tag::2"),
])
def test_find_item_by_tag(item_tag_service, type, target_id, key):
    target = uuid.UUID(target_id)
    target_type = ItemTagDto.ItemTagRMType[type]

    item_tag = ItemTagDto(uuid.uuid4(), SAMPLE_EHR_ID, target, target_type, None, key, None)
    mock_item_tag_repository().find_for_owner_and_target.return_value = [item_tag]

    result = item_tag_service.find_item_tag(SAMPLE_EHR_ID, target, target_type, [], [key])
    assert len(result) == 1
    assert result[0] == ItemTagDto(item_tag.id, SAMPLE_EHR_ID, target, target_type, None, key, None)


def test_bulk_delete_nop(item_tag_service):
    mock_ehr_service().check_ehr_exists.side_effect = ObjectNotFoundException("test", "test")
    assert not item_tag_service.bulk_delete(SAMPLE_EHR_ID, uuid.uuid4(), ItemTagDto.ItemTagRMType.EHR_STATUS, [])


@pytest.mark.parametrize("type, target_id", [
    ("EHR_STATUS", "422f7ddf-5646-4db8-b984-2df23d5021da"),
    ("COMPOSITION", "6d4622d6-ecbb-456a-981a-59423a374a2e"),
])
def test_bulk_delete_ehr_not_exist_error(item_tag_service, type, target_id):
    target = uuid.UUID(target_id)
    target_type = ItemTagDto.ItemTagRMType[type]

    with pytest.raises(ObjectNotFoundException):
        item_tag_service.bulk_delete(SAMPLE_EHR_ID, target, target_type, [uuid.uuid4()])


@pytest.mark.parametrize("type, target_id", [
    ("EHR_STATUS", "b84b5a08-e6fa-4988-b40a-82f162a8f068"),
    ("COMPOSITION", "f1251117-66e2-49e5-884b-c69641ad36e3"),
])
def test_bulk_delete(item_tag_service, type, target_id):
    target = uuid.UUID(target_id)
    target_type = ItemTagDto.ItemTagRMType[type]

    item_tag_service.bulk_delete(SAMPLE_EHR_ID, target, target_type, [uuid.UUID("247d5155-a4bd-4ad6-ae9a-a8112d1fcd25")])
    mock_item_tag_repository().bulk_delete.assert_called_once_with(SAMPLE_EHR_ID, target, target_type, [uuid.UUID("247d5155-a4bd-4ad6-ae9a-a8112d1fcd25")])


@pytest.mark.parametrize("key", [chr(c) for c in range(32, 127)])  # valid ASCII
def test_valid_tag_key(key):
    assert ItemTagServiceImpl.validate_tag_key(key) is None


@pytest.mark.parametrize("key", [
    None,
    "",
    "tag::key with spaces",
    "tag::key!@#$",
])
def test_invalid_tag_key(key):
    with pytest.raises(ValidationException):
        ItemTagServiceImpl.validate_tag_key(key)


def test_validate_existing_keys():
    existing_keys = ["tag::1", "tag::2"]
    item_tag_service = ItemTagServiceImpl(mock.Mock(), mock.Mock())
    new_keys = ["tag::3", "tag::2"]

    with pytest.raises(ValidationException):
        item_tag_service.validate_existing_keys(existing_keys, new_keys)


















# import uuid
# from typing import List, Collection, Callable, Any
# import pytest
# from unittest import mock

# # Assuming we have the equivalent classes and exceptions defined in Python
# from ehrbase.api.dto.experimental import ItemTagDto
# from ehrbase.api.exception import ObjectNotFoundException, UnprocessableEntityException, ValidationException
# from ehrbase.api.service import EhrService
# from ehrbase.service.experimental import ItemTagService, ItemTagServiceImpl
# from ehrbase.repository.experimental import ItemTagRepository
# from ehrbase.util import UuidGenerator

# SAMPLE_EHR_ID = uuid.UUID("90867c82-8498-4536-b2b6-16ea4e62818f")


# @pytest.fixture
# def mock_item_tag_repository():
#     return mock.Mock(spec=ItemTagRepository)


# @pytest.fixture
# def mock_ehr_service():
#     return mock.Mock(spec=EhrService)


# @pytest.fixture
# def item_tag_service(mock_item_tag_repository, mock_ehr_service):
#     return ItemTagServiceImpl(mock_item_tag_repository, mock_ehr_service)


# def item_tag_dto(key: str) -> ItemTagDto:
#     return ItemTagDto(None, None, None, None, None, key, None)


# def test_bulk_upsert_empty_list_nop(item_tag_service):
#     ids = item_tag_service.bulk_upsert(
#         SAMPLE_EHR_ID, uuid.UUID("6d4622d6-ecbb-456a-981a-59423a374a2e"), ItemTagDto.ItemTagRMType.COMPOSITION, []
#     )
#     assert len(ids) == 0


# @pytest.mark.parametrize("type, target_id", [
#     ("EHR_STATUS", "90867c82-8498-4536-b2b6-16ea4e62818f"),
#     ("COMPOSITION", "6d4622d6-ecbb-456a-981a-59423a374a2e"),
# ])
# def test_bulk_upsert_ehr_not_exist_error(item_tag_service, type, target_id):
#     target = uuid.UUID(target_id)
#     target_type = ItemTagDto.ItemTagRMType[type]

#     with pytest.raises(ObjectNotFoundException):
#         item_tag_service.bulk_upsert(SAMPLE_EHR_ID, target, target_type, [item_tag_dto("some:key")])


# def test_bulk_updater_change_of_owner_error(item_tag_service):
#     item_tags = [
#         ItemTagDto(
#             uuid.uuid4(),
#             uuid.UUID("1dc42f91-094a-43e7-8c26-3ca6d43b8833"),
#             SAMPLE_EHR_ID,
#             ItemTagDto.ItemTagRMType.EHR_STATUS,
#             None,
#             "a:key",
#             None
#         )
#     ]

#     with pytest.raises(UnprocessableEntityException) as excinfo:
#         item_tag_service.bulk_upsert(SAMPLE_EHR_ID, SAMPLE_EHR_ID, ItemTagDto.ItemTagRMType.EHR_STATUS, item_tags)
#     assert "Owner mismatch for ItemTag 'a:key': 1dc42f91-094a-43e7-8c26-3ca6d43b8833 vs. {}".format(SAMPLE_EHR_ID) == str(excinfo.value)


# def test_build_update_target_type_mismatch(item_tag_service):
#     item_tags = [
#         ItemTagDto(
#             uuid.uuid4(),
#             SAMPLE_EHR_ID,
#             uuid.UUID("f5fe8b05-2fe3-4962-a0b7-d443e0b53304"),
#             ItemTagDto.ItemTagRMType.COMPOSITION,
#             None,
#             "some:key",
#             None
#         )
#     ]

#     with pytest.raises(ValidationException) as excinfo:
#         item_tag_service.bulk_upsert(SAMPLE_EHR_ID, uuid.UUID("f5fe8b05-2fe3-4962-a0b7-d443e0b53304"), ItemTagDto.ItemTagRMType.EHR_STATUS, item_tags)
#     assert "target_type does not match EHR_STATUS" == str(excinfo.value)


# @pytest.mark.parametrize("type, target_id", [
#     ("EHR_STATUS", "1a598f7a-fbc2-4762-9fae-6480390b9bb5"),
#     ("COMPOSITION", "9448b3b8-866f-4415-97d2-d5605a553e45"),
# ])
# def test_bulk_upsert(item_tag_service, type, target_id):
#     target = uuid.UUID(target_id)
#     target_type = ItemTagDto.ItemTagRMType[type]

#     mock_ehr_service().check_ehr_exists(SAMPLE_EHR_ID)

#     tag_id = uuid.UUID("49532718-9a4f-4c3c-a1ad-86af95a1751c")
#     item_tags = [
#         item_tag_dto("1:new:key"),
#         ItemTagDto(tag_id, None, None, None, None, "2:existing:key", None)
#     ]

#     fixture_ids = [UuidGenerator.random_uuid(), tag_id]
#     mock_item_tag_repository().bulk_store.return_value = fixture_ids

#     ids = item_tag_service.bulk_upsert(SAMPLE_EHR_ID, target, target_type, item_tags)
#     assert ids == fixture_ids

#     mock_item_tag_repository().bulk_store.assert_called_once()
#     stored_tags = mock_item_tag_repository().bulk_store.call_args[0][0]
#     stored_tags = sorted(stored_tags, key=lambda x: x.key)
#     assert len(stored_tags) == 2
#     assert stored_tags[0] == ItemTagDto(None, SAMPLE_EHR_ID, target, target_type, None, "1:new:key", None)
#     assert stored_tags[1] == ItemTagDto(tag_id, SAMPLE_EHR_ID, target, target_type, None, "2:existing:key", None)


# @pytest.mark.parametrize("type, target_id", [
#     ("EHR_STATUS", "422f7ddf-5646-4db8-b984-2df23d5021da"),
#     ("COMPOSITION", "6d4622d6-ecbb-456a-981a-59423a374a2e"),
# ])
# def test_find_ehr_not_exist_error(item_tag_service, type, target_id):
#     target = uuid.UUID(target_id)
#     target_type = ItemTagDto.ItemTagRMType[type]

#     with pytest.raises(ObjectNotFoundException):
#         item_tag_service.find_item_tag(SAMPLE_EHR_ID, target, target_type, [], [])


# @pytest.mark.parametrize("type, target_id, key", [
#     ("EHR_STATUS", "90867c82-8498-4536-b2b6-16ea4e62818f", "tag::1"),
#     ("COMPOSITION", "7eb105ca-d671-4220-9103-d08db0403dc0", "tag::2"),
# ])
# def test_find_item_by_tag(item_tag_service, type, target_id, key):
#     target = uuid.UUID(target_id)
#     target_type = ItemTagDto.ItemTagRMType[type]

#     item_tag = ItemTagDto(uuid.uuid4(), SAMPLE_EHR_ID, target, target_type, None, key, None)
#     mock_item_tag_repository().find_for_owner_and_target.return_value = [item_tag]

#     result = item_tag_service.find_item_tag(SAMPLE_EHR_ID, target, target_type, [], [key])
#     assert len(result) == 1
#     assert result[0] == ItemTagDto(item_tag.id, SAMPLE_EHR_ID, target, target_type, None, key, None)


# def test_bulk_delete_nop(item_tag_service):
#     mock_ehr_service().check_ehr_exists.side_effect = ObjectNotFoundException("test", "test")
#     assert not item_tag_service.bulk_delete(SAMPLE_EHR_ID, uuid.uuid4(), ItemTagDto.ItemTagRMType.EHR_STATUS, [])


# @pytest.mark.parametrize("type, target_id", [
#     ("EHR_STATUS", "422f7ddf-5646-4db8-b984-2df23d5021da"),
#     ("COMPOSITION", "6d4622d6-ecbb-456a-981a-59423a374a2e"),
# ])
# def test_bulk_delete_ehr_not_exist_error(item_tag_service, type, target_id):
#     target = uuid.UUID(target_id)
#     target_type = ItemTagDto.ItemTagRMType[type]

#     with pytest.raises(ObjectNotFoundException):
#         item_tag_service.bulk_delete(SAMPLE_EHR_ID, target, target_type, [uuid.uuid4()])


# @pytest.mark.parametrize("type, target_id", [
#     ("EHR_STATUS", "b84b5a08-e6fa-4988-b40a-82f162a8f068"),
#     ("COMPOSITION", "f1251117-66e2-49e5-884b-c69641ad36e3"),
# ])
# def test_bulk_delete(item_tag_service, type, target_id):
#     target = uuid.UUID(target_id)
#     target_type = ItemTagDto.ItemTagRMType[type]

#     item_tag_service.bulk_delete(SAMPLE_EHR_ID, target, target_type, [uuid.UUID("247d5155-a4bd-4ad6-ae9a-a8112d1fcd25")])
#     mock_item_tag_repository().bulk_delete.assert_called_once_with(SAMPLE_EHR_ID, target, target_type, [uuid.UUID("247d5155-a4bd-4ad6-ae9a-a8112d1fcd25")])


# @pytest.mark.parametrize("key", [chr(c) for c in range(32, 127)])  # valid ASCII
# def test_valid_tag_key(key):
#     assert ItemTagServiceImpl.validate_tag_key(key) is None


# @pytest.mark.parametrize("key", [
#     None,
#     "",
#     "tag::key with spaces",
#     "tag::key!@#$",
# ])
# def test_invalid_tag_key(key):
#     with pytest.raises(ValidationException):
#         ItemTagServiceImpl.validate_tag_key(key)


# def test_validate_existing_keys():
#     existing_keys = ["tag::1", "tag::2"]
#     item_tag_service = ItemTagServiceImpl(mock.Mock(), mock.Mock())
#     new_keys = ["tag::3", "tag::2"]

#     with pytest.raises(ValidationException):
#         item_tag_service.validate_existing_keys(existing_keys, new_keys)
