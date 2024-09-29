from flask import Blueprint, request, jsonify, Response
from flask_restful import Resource
from uuid import UUID
from your_service import ItemTagService  # Import your ItemTagService here
from your_dto import ItemTagDto  # Import your DTOs
from your_exception import UnprocessableEntityException  # Define your custom exception
from your_headers import EHRbaseHeader  # Define your headers
from your_specifications import ItemTagApiSpecification  # Import your specifications

class ItemTagController(Resource, ItemTagApiSpecification):
    def __init__(self, item_tag_service: ItemTagService):
        self.item_tag_service = item_tag_service

    # --- EHR_STATUS ---

    def upsert_ehr_status_item_tags(self, ehr_id: str, versioned_object_uid: str):
        openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
        openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
        prefer = request.headers.get(EHRbaseHeader.PREFER)

        item_tags = request.get_json()

        return self.upsert_item_tags(prefer, ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status", item_tags)

    def get_ehr_status_item_tags(self, ehr_id: str, versioned_object_uid: str):
        openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
        openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
        ids = request.args.getlist('ids')
        keys = request.args.getlist('keys')

        return self.get_item_tag(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status", ids, keys)

    def delete_ehr_status_item_tags(self, ehr_id: str, versioned_object_uid: str):
        openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
        openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
        item_tags_or_uuids = request.get_json()

        return self.delete_tags(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.EHR_STATUS, item_tags_or_uuids)

    # --- COMPOSITION ---

    def upsert_composition_item_tags(self, ehr_id: str, versioned_object_uid: str):
        openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
        openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
        prefer = request.headers.get(EHRbaseHeader.PREFER)

        item_tags = request.get_json()

        return self.upsert_item_tags(prefer, ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.COMPOSITION, "composition", item_tags)

    def get_composition_item_tags(self, ehr_id: str, versioned_object_uid: str):
        openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
        openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
        ids = request.args.getlist('ids')
        keys = request.args.getlist('keys')

        return self.get_item_tag(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.COMPOSITION, "composition", ids, keys)

    def delete_composition_item_tags(self, ehr_id: str, versioned_object_uid: str):
        openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
        openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
        item_tags_or_uuids = request.get_json()

        return self.delete_tags(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.COMPOSITION, item_tags_or_uuids)

    # --- Common Implementation

    def upsert_item_tags(self, prefer: str, ehr_id_string: str, versioned_object_uid: str, item_tag_type: ItemTagDto.ItemTagRMType, location_part: str, item_tags: list):
        # obtain path parameter
        ehr_id = UUID(ehr_id_string)
        composition_uid = self.extract_versioned_object_uid_from_version_uid(versioned_object_uid)

        # sanity check for input
        if not item_tags:
            raise UnprocessableEntityException("ItemTags are empty")

        # perform bulk creation and return based on preferred response type
        tag_ids = self.item_tag_service.bulk_upsert(ehr_id, composition_uid, item_tag_type, item_tags)

        uri = self.create_location_uri("ehr", str(ehr_id), location_part, versioned_object_uid, "item_tag")
        response = Response(status=200)
        response.headers['Location'] = uri

        if prefer == "return-representation":
            tags = self.item_tag_service.find_item_tag(ehr_id, composition_uid, item_tag_type, tag_ids, [])
            response.set_data(jsonify(tags))
        else:
            response.set_data(jsonify(tag_ids))

        return response

    def get_item_tag(self, ehr_id_string: str, versioned_object_uid: str, item_tag_type: ItemTagDto.ItemTagRMType, location_part: str, ids: list, keys: list):
        # obtain path parameter
        ehr_id = UUID(ehr_id_string)
        composition_uid = self.extract_versioned_object_uid_from_version_uid(versioned_object_uid)

        tag_keys = keys or []
        tag_ids = [UUID(i) for i in ids] if ids else []

        item_tags = self.item_tag_service.find_item_tag(ehr_id, composition_uid, item_tag_type, tag_ids, tag_keys)

        uri = self.create_location_uri("ehr", str(ehr_id), location_part, versioned_object_uid, "item_tag")
        response = Response(status=200)
        response.headers['Location'] = uri
        response.set_data(jsonify(item_tags))
        return response

    def delete_tags(self, ehr_id_string: str, versioned_object_uid: str, item_tag_type: ItemTagDto.ItemTagRMType, item_tags_or_uuids: list):
        if not item_tags_or_uuids:
            raise UnprocessableEntityException("ItemTags are empty")

        # obtain path parameter
        ehr_id = UUID(ehr_id_string)
        composition_uid = self.extract_versioned_object_uid_from_version_uid(versioned_object_uid)

        tag_ids = []
        for entry in item_tags_or_uuids:
            if isinstance(entry, str):
                tag_ids.append(UUID(entry))
            elif isinstance(entry, dict):
                id_value = entry.get("id")
                if id_value is None:
                    raise UnprocessableEntityException("Expected ItemTag entry to contain an 'id'")
                tag_ids.append(UUID(str(id_value)))
            else:
                raise UnprocessableEntityException("Expected array entry to be ItemTag or UUID String")

        self.item_tag_service.bulk_delete(ehr_id, composition_uid, item_tag_type, tag_ids)

        return Response(status=204)

    # --- Additional Methods ---

    def create_location_uri(self, resource_type: str, ehr_id: str, location_part: str, versioned_object_uid: str, item_type: str):
        # Construct the URI for the created resource
        return f"/{resource_type}/{ehr_id}/{location_part}/{versioned_object_uid}/{item_type}"

    def get_ehr_uuid(self, ehr_id_string: str) -> UUID:
        # Convert the string EHR ID to a UUID
        return UUID(ehr_id_string)

    def extract_versioned_object_uid_from_version_uid(self, versioned_object_uid: str) -> UUID:
        # This should contain the logic to extract the composition UID from the versioned object UID
        return UUID(versioned_object_uid)  # Adjust as needed for your specific logic






















# from flask import Blueprint, request, jsonify, Response
# from flask_restful import Resource
# from uuid import UUID
# from your_service import ItemTagService  # Import your ItemTagService here
# from your_dto import ItemTagDto  # Import your DTOs
# from your_exception import UnprocessableEntityException  # Define your custom exception
# from your_headers import EHRbaseHeader  # Define your headers
# from your_specifications import ItemTagApiSpecification  # Import your specifications

# class ItemTagController(Resource, ItemTagApiSpecification):
#     def __init__(self, item_tag_service: ItemTagService):
#         self.item_tag_service = item_tag_service

#     # --- EHR_STATUS ---

#     def upsert_ehr_status_item_tags(self, ehr_id: str, versioned_object_uid: str):
#         openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
#         openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
#         prefer = request.headers.get(EHRbaseHeader.PREFER)

#         item_tags = request.get_json()

#         return self.upsert_item_tags(prefer, ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status", item_tags)

#     def get_ehr_status_item_tags(self, ehr_id: str, versioned_object_uid: str):
#         openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
#         openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
#         ids = request.args.getlist('ids')
#         keys = request.args.getlist('keys')

#         return self.get_item_tag(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.EHR_STATUS, "ehr_status", ids, keys)

#     def delete_ehr_status_item_tags(self, ehr_id: str, versioned_object_uid: str):
#         openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
#         openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
#         item_tags_or_uuids = request.get_json()

#         return self.delete_tags(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.EHR_STATUS, item_tags_or_uuids)

#     # --- COMPOSITION ---

#     def upsert_composition_item_tags(self, ehr_id: str, versioned_object_uid: str):
#         openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
#         openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
#         prefer = request.headers.get(EHRbaseHeader.PREFER)

#         item_tags = request.get_json()

#         return self.upsert_item_tags(prefer, ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.COMPOSITION, "composition", item_tags)

#     def get_composition_item_tags(self, ehr_id: str, versioned_object_uid: str):
#         openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
#         openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
#         ids = request.args.getlist('ids')
#         keys = request.args.getlist('keys')

#         return self.get_item_tag(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.COMPOSITION, "composition", ids, keys)

#     def delete_composition_item_tags(self, ehr_id: str, versioned_object_uid: str):
#         openehr_version = request.headers.get(EHRbaseHeader.OPENEHR_VERSION)
#         openehr_audit_details = request.headers.get(EHRbaseHeader.OPENEHR_AUDIT_DETAILS)
#         item_tags_or_uuids = request.get_json()

#         return self.delete_tags(ehr_id, versioned_object_uid, ItemTagDto.ItemTagRMType.COMPOSITION, item_tags_or_uuids)

#     # --- Common Implementation

#     def upsert_item_tags(self, prefer: str, ehr_id_string: str, versioned_object_uid: str, item_tag_type: ItemTagDto.ItemTagRMType, location_part: str, item_tags: list):
#         # obtain path parameter
#         ehr_id = UUID(ehr_id_string)
#         composition_uid = self.extract_versioned_object_uid_from_version_uid(versioned_object_uid)

#         # sanity check for input
#         if not item_tags:
#             raise UnprocessableEntityException("ItemTags are empty")

#         # perform bulk creation and return based on preferred response type
#         tag_ids = self.item_tag_service.bulk_upsert(ehr_id, composition_uid, item_tag_type, item_tags)

#         uri = self.create_location_uri("ehr", str(ehr_id), location_part, versioned_object_uid, "item_tag")
#         response = Response(status=200)
#         response.headers['Location'] = uri

#         if prefer == "return-representation":
#             tags = self.item_tag_service.find_item_tag(ehr_id, composition_uid, item_tag_type, tag_ids, [])
#             response.set_data(jsonify(tags))
#         else:
#             response.set_data(jsonify(tag_ids))

#         return response

#     def get_item_tag(self, ehr_id_string: str, versioned_object_uid: str, item_tag_type: ItemTagDto.ItemTagRMType, location_part: str, ids: list, keys: list):
#         # obtain path parameter
#         ehr_id = UUID(ehr_id_string)
#         composition_uid = self.extract_versioned_object_uid_from_version_uid(versioned_object_uid)

#         tag_keys = keys or []
#         tag_ids = [UUID(i) for i in ids] if ids else []

#         item_tags = self.item_tag_service.find_item_tag(ehr_id, composition_uid, item_tag_type, tag_ids, tag_keys)

#         uri = self.create_location_uri("ehr", str(ehr_id), location_part, versioned_object_uid, "item_tag")
#         response = Response(status=200)
#         response.headers['Location'] = uri
#         response.set_data(jsonify(item_tags))
#         return response

#     def delete_tags(self, ehr_id_string: str, versioned_object_uid: str, item_tag_type: ItemTagDto.ItemTagRMType, item_tags_or_uuids: list):
#         if not item_tags_or_uuids:
#             raise UnprocessableEntityException("ItemTags are empty")

#         # obtain path parameter
#         ehr_id = UUID(ehr_id_string)
#         composition_uid = self.extract_versioned_object_uid_from_version_uid(versioned_object_uid)

#         tag_ids = []
#         for entry in item_tags_or_uuids:
#             if isinstance(entry, str):
#                 tag_ids.append(UUID(entry))
#             elif isinstance(entry, dict):
#                 id_value = entry.get("id")
#                 if id_value is None:
#                     raise UnprocessableEntityException("Expected ItemTag entry to contain an 'id'")
#                 tag_ids.append(UUID(str(id_value)))
#             else:
#                 raise UnprocessableEntityException("Expected array entry to be ItemTag or UUID String")

#         self.item_tag_service.bulk_delete(ehr_id, composition_uid, item_tag_type, tag_ids)

#         return Response(status=204)

#     # Additional methods like `create_location_uri`, `get_ehr_uuid`, `extract_versioned_object_uid_from_version_uid` etc. should also be defined here
