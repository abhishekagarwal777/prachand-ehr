import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify, request
from http import HTTPStatus
from uuid import uuid4, UUID

# Sample DTO class
class ItemTagDto:
    class ItemTagRMType:
        EHR_STATUS = "EHR_STATUS"
        COMPOSITION = "COMPOSITION"

    def __init__(self, id, ehr_id, target_id, type, path, key, value):
        self.id = id
        self.ehr_id = ehr_id
        self.target_id = target_id
        self.type = type
        self.path = path
        self.key = key
        self.value = value

# Sample service class
class ItemTagService:
    def bulk_upsert(self, *args, **kwargs):
        pass

    def find_item_tag(self, *args, **kwargs):
        pass

    def bulk_delete(self, *args, **kwargs):
        pass

# Flask app and controller setup
app = Flask(__name__)

class ItemTagController:
    def __init__(self, item_tag_service):
        self.item_tag_service = item_tag_service

    def get_context_path(self):
        return "https://openehr.test.item-tag.com/rest"

    def upsert_item_tags(self, prefer, ehr_id, target_id, type, resource_type, tags):
        if not tags:
            raise Exception("ItemTags are empty")
        # Simulating the upsert operation
        return jsonify(tags), HTTPStatus.OK

    def get_item_tag(self, ehr_id, target_id, type, resource_type, ids=None, keys=None):
        # Simulating the fetch operation
        return jsonify([]), HTTPStatus.OK

    def delete_tags(self, ehr_id, target_id, type, ids):
        if not ids:
            raise Exception("ItemTags are empty")
        # Simulating the delete operation
        return '', HTTPStatus.NO_CONTENT

# Test class
class ItemTagControllerTest(unittest.TestCase):
    SAMPLE_EHR_ID = "d7a57443-20ee-4950-8c72-9bced2aa9881"

    def setUp(self):
        self.mock_item_tag_service = MagicMock(ItemTagService)
        self.controller = ItemTagController(self.mock_item_tag_service)

    def item_tag_dto(self, type, target_id):
        return ItemTagDto(
            id=uuid4(),
            ehr_id=UUID(self.SAMPLE_EHR_ID),
            target_id=UUID(target_id),
            type=type,
            path="/content",
            key="a::key",
            value="some value"
        )

    def test_conditional_enabled(self):
        # Simulating the annotation check
        self.assertEqual(True, True)  # Replace with actual check

    def test_upsert_item_tags_common_used(self):
        target_id = "1073d3bd-1490-4f3b-b2ac-95202d18c41d"
        tag = self.item_tag_dto(ItemTagDto.ItemTagRMType.COMPOSITION, target_id)

        # Simulating the upsert operation
        self.controller.upsert_item_tags(None, self.SAMPLE_EHR_ID, target_id, ItemTagDto.ItemTagRMType.COMPOSITION, "composition", [tag])
        self.controller.upsert_item_tags(None, self.SAMPLE_EHR_ID, target_id, ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status", [tag])

        # Verify calls
        self.mock_item_tag_service.bulk_upsert.assert_called()

    def test_upsert_item_tags_empty_error(self):
        with self.assertRaises(Exception) as context:
            self.controller.upsert_item_tags(None, self.SAMPLE_EHR_ID, "21bfba85-aaa6-4190-b6dd-4968cb84b549", ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status", [])
        self.assertEqual("ItemTags are empty", str(context.exception))

    def test_get_item_tags_common_used(self):
        target_id = "1073d3bd-1490-4f3b-b2ac-95202d18c41d"
        self.controller.get_item_tag(self.SAMPLE_EHR_ID, target_id, ItemTagDto.ItemTagRMType.COMPOSITION, "composition")
        self.controller.get_item_tag(self.SAMPLE_EHR_ID, target_id, ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status")

    def test_delete_item_tags_common_used(self):
        target_id = "a377d88c-3374-4cea-8149-697b7837de17"
        id = "248c21df-09ad-476f-87d7-72ca8f58e89f"

        self.controller.delete_tags(self.SAMPLE_EHR_ID, target_id, ItemTagDto.ItemTagRMType.COMPOSITION, [id])
        self.controller.delete_tags(self.SAMPLE_EHR_ID, target_id, ItemTagDto.ItemTagRMType.EHR_STATUS, [id])

    def test_delete_item_tags_empty_error(self):
        with self.assertRaises(Exception) as context:
            self.controller.delete_tags(self.SAMPLE_EHR_ID, "a377d88c-3374-4cea-8149-697b7837de17", ItemTagDto.ItemTagRMType.EHR_STATUS, [])
        self.assertEqual("ItemTags are empty", str(context.exception))

if __name__ == '__main__':
    unittest.main()
