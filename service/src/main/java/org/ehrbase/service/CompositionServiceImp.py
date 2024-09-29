# Copyright (c) 2024 vitasystems GmbH.
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

import uuid
from typing import Optional, List
from datetime import datetime

from EHR.api.dto.experimental import ItemTagDto
from EHR.api.exception import (BadGatewayException,
                                              InternalServerException,
                                              InvalidApiParameterException,
                                              ObjectNotFoundException,
                                              PreconditionFailedException,
                                              UnprocessableEntityException,
                                              ValidationException)
from EHR.api.service import CompositionService, EhrService, SystemService, ValidationService
from EHR.openehr.sdk.response.dto.ehrscape import CompositionDto, CompositionFormat, StructuredString, StructuredStringFormat
from EHR.openehr.sdk.serialisation.flatencoding import FlatFormat, FlatJasonProvider
from EHR.openehr.sdk.serialisation.jsonencoding import CanonicalJson
from EHR.openehr.sdk.serialisation.xmlencoding import CanonicalXML
from EHR.openehr.sdk.webtemplate.model import WebTemplate
from EHR.openehr.sdk.webtemplate.templateprovider import TemplateProvider
from EHR.repository import CompositionRepository, ItemTagRepository
from EHR.util import UuidGenerator
from EHR.rm.changecontrol import OriginalVersion
from EHR.rm.composition import Composition
from EHR.rm.ehr import VersionedComposition
from EHR.rm.generic import Attestation, AuditDetails, RevisionHistory, RevisionHistoryItem
from EHR.rm.support.identification import ObjectVersionId, UIDBasedId
from EHR.logger import get_logger

logger = get_logger(__name__)

class CompositionServiceImp(CompositionService):

    def __init__(self, knowledge_cache_service, validation_service: ValidationService, ehr_service: EhrService,
                 system_service: SystemService, composition_repository: CompositionRepository,
                 item_tag_repository: ItemTagRepository):
        self.validation_service = validation_service
        self.knowledge_cache_service = knowledge_cache_service
        self.ehr_service = ehr_service
        self.composition_repository = composition_repository
        self.item_tag_repository = item_tag_repository
        self.system_service = system_service

    def create(self, ehr_id: uuid.UUID, obj_data: Composition, contribution: Optional[uuid.UUID] = None, audit: Optional[uuid.UUID] = None) -> Optional[uuid.UUID]:
        composition_id = self.create_internal(ehr_id, obj_data, contribution, audit)
        return composition_id

    def create_internal(self, ehr_id: uuid.UUID, composition: Composition, contribution_id: Optional[uuid.UUID], audit: Optional[uuid.UUID]) -> uuid.UUID:
        self.ehr_service.check_ehr_exists_and_is_modifiable(ehr_id)

        try:
            self.validation_service.check(composition)
        except (UnprocessableEntityException, ValidationException, BadGatewayException) as e:
            raise e
        except Exception as e:
            raise InternalServerException(e)

        object_version_id = self.check_or_construct_object_version_id(composition.uid)
        composition.uid = object_version_id
        composition_id = object_version_id.object_id

        self.composition_repository.commit(ehr_id, composition, contribution_id, audit)
        logger.debug(f"Composition created: id={composition_id}")

        return composition_id

    def check_or_construct_object_version_id(self, uid: Optional[UIDBasedId]) -> ObjectVersionId:
        if uid is None:
            return build_object_version_id(UuidGenerator.random_uuid(), 1, self.system_service)

        if isinstance(uid, ObjectVersionId):
            if uid.version_tree_id.value != "1":
                raise PreconditionFailedException(f"Provided Id {uid} has an invalid Version. Expect Version 1")

            if uid.creating_system_id.value != self.system_service.get_system_id():
                raise PreconditionFailedException(f"Mismatch of creating_system_id: {uid.creating_system_id.value} !=: {self.system_service.get_system_id()}")

            if self.composition_repository.exists(uuid.UUID(uid.object_id.value)):
                raise PreconditionFailedException(f"Provided Id {uid} already exists")
            return uid
        else:
            raise PreconditionFailedException(f"Provided Id {uid} is not a ObjectVersionId")

    def update(self, ehr_id: uuid.UUID, target_obj_id: ObjectVersionId, obj_data: Composition, contribution: Optional[uuid.UUID] = None, audit: Optional[uuid.UUID] = None) -> Optional[uuid.UUID]:
        comp_id = self.internal_update(ehr_id, target_obj_id, obj_data, contribution, audit)
        return comp_id

    def internal_update(self, ehr_id: uuid.UUID, composition_id: ObjectVersionId, composition: Composition, contribution_id: Optional[uuid.UUID], audit: Optional[uuid.UUID]) -> uuid.UUID:
        self.ehr_service.check_ehr_exists_and_is_modifiable(ehr_id)

        try:
            self.validation_service.check(composition)
        except Exception as e:
            raise InternalServerException(e)

        comp_id = uuid.UUID(composition_id.object_id.value)
        version = int(composition_id.version_tree_id.value)

        existing_template_id = self.composition_repository.find_template_id(comp_id)
        if not existing_template_id:
            raise ObjectNotFoundException("composition", f"No COMPOSITION with given id: {comp_id}")

        input_template_id = composition.archetype_details.template_id.value
        if existing_template_id != input_template_id:
            if existing_template_id.split(".")[0] != input_template_id.split(".")[0]:
                raise InvalidApiParameterException("Can't update composition to have different template.")
            existing_template_id_version = int(existing_template_id.split(".v")[1])
            input_template_id_version = int(input_template_id.split(".v")[1])
            if input_template_id_version < existing_template_id_version:
                raise InvalidApiParameterException("Can't update composition with wrong template version bump.")

        composition.uid = build_object_version_id(comp_id, version + 1, self.system_service)
        self.composition_repository.update(ehr_id, composition, contribution_id, audit)

        return comp_id

    def delete(self, ehr_id: uuid.UUID, target_obj_id: ObjectVersionId, contribution: Optional[uuid.UUID] = None, audit: Optional[uuid.UUID] = None):
        self.internal_delete(ehr_id, target_obj_id, contribution, audit)

    def internal_delete(self, ehr_id: uuid.UUID, composition_id: ObjectVersionId, contribution_id: Optional[uuid.UUID], audit: Optional[uuid.UUID]):
        self.ehr_service.check_ehr_exists_and_is_modifiable(ehr_id)
        self.composition_repository.delete(ehr_id, uuid.UUID(composition_id.object_id.value), extract_version(composition_id), contribution_id, audit)

    def retrieve(self, ehr_id: uuid.UUID, composition_id: uuid.UUID, version: Optional[int]) -> Optional[Composition]:
        if version is None:
            result = self.composition_repository.find_head(ehr_id, composition_id)
        else:
            result = self.composition_repository.find_by_version(ehr_id, composition_id, version)

        if result is None:
            self.ehr_service.check_ehr_exists(ehr_id)

        return result

    def get_ehr_id_for_composition(self, composition_id: uuid.UUID) -> Optional[uuid.UUID]:
        return self.composition_repository.find_ehr_for_composition(composition_id)

    def serialize(self, composition: CompositionDto, format: CompositionFormat) -> StructuredString:
        if format == CompositionFormat.XML:
            composition_string = StructuredString(
                CanonicalXML().marshal(composition.composition, False), StructuredStringFormat.XML)
        elif format == CompositionFormat.JSON:
            composition_string = StructuredString(
                CanonicalJson().marshal(composition.composition), StructuredStringFormat.JSON)
        elif format in (CompositionFormat.FLAT, CompositionFormat.STRUCTURED):
            provider = FlatJasonProvider(self.create_template_provider())
            composition_string = StructuredString(
                provider.build_flat_json(FlatFormat.SIM_SDT if format == CompositionFormat.FLAT else FlatFormat.STRUCTURED, composition.template_id)
                .marshal(composition.composition), StructuredStringFormat.JSON)
        else:
            raise UnexpectedSwitchCaseException(format)

        return composition_string

    def build_composition(self, content: str, format: CompositionFormat, template_id: str) -> Composition:
        if format == CompositionFormat.XML:
            composition = CanonicalXML().unmarshal(content, Composition)
        elif format == CompositionFormat.JSON:
            composition = CanonicalJson().unmarshal(content, Composition)
        elif format in (CompositionFormat.FLAT, CompositionFormat.STRUCTURED):
            provider = FlatJasonProvider(self.create_template_provider())
            composition = provider.build_flat_json(FlatFormat.SIM_SDT if format == CompositionFormat.FLAT else FlatFormat.STRUCTURED, template_id).unmarshal(content)
        else:
            raise UnexpectedSwitchCaseException(format)

        return composition

    def create_template_provider(self) -> TemplateProvider:
        class TemplateProviderImpl(TemplateProvider):
            def find(self, s: str) -> Optional[OPERATIONALTEMPLATE]:
                return self.knowledge_cache_service.get(s)

        return TemplateProviderImpl()

    def find_all_tags(self) -> List[ItemTagDto]:
        tags = self.item_tag_repository.find_all_tags()
        return tags

    def add_tag(self, tag: ItemTagDto):
        self.item_tag_repository.add_tag(tag)

    def delete_tag(self, tag_id: uuid.UUID):
        self.item_tag_repository.delete_tag(tag_id)
