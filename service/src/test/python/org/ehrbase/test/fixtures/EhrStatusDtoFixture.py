# Copyright (c) 2019-2024 vitasystems GmbH.
#
# This file is part of project EHRbase
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from EHR import EhrStatusDto, DvText, PartySelf, UIDBasedId, Archetyped, FeederAudit, ItemStructure  # Adjust import based on your module structure

class EhrStatusDtoFixture:
    NAME = DvText("EHR_STATUS")
    ARCHETYPE_NODE_ID = "openEHR-EHR-EHR_STATUS.generic.v1"
    SUBJECT = PartySelf()

    @staticmethod
    def ehr_status_dto(uid: UIDBasedId = None, name: DvText = None, archetyped: Archetyped = None, 
                       feeder_audit: FeederAudit = None, subject: PartySelf = SUBJECT, 
                       is_queryable: bool = True, is_modifiable: bool = True, 
                       other_details: ItemStructure = None) -> EhrStatusDto:
        return EhrStatusDto(
            uid=uid,
            archetype_node_id=EhrStatusDtoFixture.ARCHETYPE_NODE_ID,
            name=name or EhrStatusDtoFixture.NAME,
            archetype_details=archetyped,
            feeder_audit=feeder_audit,
            subject=subject,
            is_queryable=is_queryable,
            is_modifiable=is_modifiable,
            other_details=other_details
        )

    @staticmethod
    def ehr_status_dto_with_uid(uid: UIDBasedId) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(uid=uid)

    @staticmethod
    def ehr_status_dto_with_name(name: DvText) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(name=name)

    @staticmethod
    def ehr_status_dto_with_archetyped(archetyped: Archetyped) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(archetyped=archetyped)

    @staticmethod
    def ehr_status_dto_with_feeder_audit(feeder_audit: FeederAudit) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(feeder_audit=feeder_audit)

    @staticmethod
    def ehr_status_dto_with_subject(subject: PartySelf) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(subject=subject)

    @staticmethod
    def ehr_status_dto_with_queryable_modifiable(is_queryable: bool, is_modifiable: bool) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(is_queryable=is_queryable, is_modifiable=is_modifiable)

    @staticmethod
    def ehr_status_dto_with_item_structure(item_structure: ItemStructure) -> EhrStatusDto:
        return EhrStatusDtoFixture.ehr_status_dto(other_details=item_structure)

# Example usage:
# uid = UIDBasedId(...)  # Your UIDBasedId instance
# ehr_status = EhrStatusDtoFixture.ehr_status_dto_with_uid(uid)
