import re
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any
from flask import current_app
from EHR.api.definitions import ServerConfig  # Update with the correct import
from EHR.api.dto import EhrStatusDto  # Update with the correct import
from EHR.api.exception import InternalServerException, UnprocessableEntityException, ValidationException  # Update with the correct import
from EHR.api.service import ValidationService  # Update with the correct import
from EHR.openehr.sdk.response.dto import ContributionCreateDto  # Update with the correct import
from EHR.openehr.sdk.terminology.openehr import TerminologyService  # Update with the correct import
from EHR.openehr.sdk.validation import CompositionValidator, ConstraintViolation, ConstraintViolationException  # Update with the correct import
from EHR.openehr.sdk.validation.terminology import ExternalTerminologyValidation, ItemStructureVisitor  # Update with the correct import
from EHR.openehr.sdk.webtemplate.model import WebTemplate  # Update with the correct import

class ValidationServiceImp(ValidationService):
    def __init__(self, knowledge_cache_service, terminology_service: TerminologyService,
                 server_config: ServerConfig, object_provider: ExternalTerminologyValidation,
                 shared_aql_query_cache: bool = True):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.NAMESPACE_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9-_:/&+?]*")

        self.knowledge_cache_service = knowledge_cache_service
        self.terminology_service = terminology_service
        self.composition_validator = ThreadPoolExecutor()

        self.rm_path_query_cache: Dict[str, Any] = {}

        disable_strict_validation = server_config.disable_strict_validation
        if disable_strict_validation:
            self.logger.warning("Disabling strict invariant validation. Caution is advised.")

        if shared_aql_query_cache:
            self.delegator = self.create_a_path_query_cache()
        else:
            self.logger.warning("Shared RMPathQueryCache is disabled.")
            self.delegator = None

        self.composition_validator = self.create_composition_validator(object_provider, disable_strict_validation, self.delegator)

    def create_a_path_query_cache(self):
        return {
            "query": lambda query: self.rm_path_query_cache.setdefault(query, None)
        }

    def create_composition_validator(self, object_provider, disable_strict_validation, delegator):
        validator = CompositionValidator()
        if object_provider is not None:
            object_provider.set_external_terminology_validation(validator)

        validator.run_invariant_checks = not disable_strict_validation
        self.set_shared_a_path_query_cache(validator, delegator)
        return validator

    def set_shared_a_path_query_cache(self, validator, delegator):
        if delegator is None:
            return
        try:
            # This assumes that there's a way to access the queryCache in the original Java class
            query_cache_field = getattr(validator.get_rm_object_validator(), "query_cache", None)
            if query_cache_field:
                query_cache_field = delegator
        except Exception as e:
            raise InternalServerException("Failed to inject shared RMPathQuery cache") from e

    def check(self, composition):
        # Check if this composition is valid for processing
        self.composition_mandatory_property(composition.name, "name")
        self.composition_mandatory_property(composition.archetype_node_id, "archetype_node_id")
        self.composition_mandatory_property(composition.language, "language")
        self.composition_mandatory_property(composition.category, "category")
        self.composition_mandatory_property(composition.composer, "composer")
        self.composition_mandatory_property(composition.archetype_details, "archetype details")
        self.composition_mandatory_property(composition.archetype_details.template_id, "archetype details/template_id")

        template_id = composition.archetype_details.template_id.value
        self.check_template(template_id, composition)

        self.logger.debug("Validated Composition against WebTemplate[%s]", template_id)

    def check_template(self, template_id: str, composition):
        try:
            web_template = self.knowledge_cache_service.get_query_opt_meta_data(template_id)
        except ValueError as e:
            raise UnprocessableEntityException(str(e))

        # Validate the composition based on WebTemplate
        violations = self.composition_validator.validate(composition, web_template)
        if violations:
            raise ConstraintViolationException(violations)

        # Check code phrases against terminologies
        item_structure_visitor = ItemStructureVisitor(self.terminology_service)
        item_structure_visitor.validate(composition)

    @staticmethod
    def composition_mandatory_property(value, attribute):
        if value is None:
            raise ValidationException(f"Composition missing mandatory attribute: {attribute}")

    def check_ehr_status(self, ehr_status: EhrStatusDto):
        rm_object_validator = self.composition_validator.get_rm_object_validator()
        validation_issues = []

        validation_issues.extend(self.require(ehr_status.type, "/subject", "subject", ehr_status.subject))
        validation_issues.extend(self.require(ehr_status.type, "/is_queryable", "is_queryable", ehr_status.is_queryable))
        validation_issues.extend(self.require(ehr_status.type, "/is_modifiable", "is_modifiable", ehr_status.is_modifiable))
        validation_issues.extend(self.validate(rm_object_validator, "/uid", ehr_status.uid))
        validation_issues.extend(self.validate(rm_object_validator, "/name", ehr_status.name))
        validation_issues.extend(self.validate(rm_object_validator, "/subject", ehr_status.subject))
        validation_issues.extend(self.validate(rm_object_validator, "/archetype_details", ehr_status.archetype_details))
        validation_issues.extend(self.validate(rm_object_validator, "/feeder_audit", ehr_status.feeder_audit))
        validation_issues.extend(self.validate(rm_object_validator, "/other_details", ehr_status.other_details))

        validation_issues.extend(self.matches(ehr_status.type, "/subject/external_ref/namespace", "namespace", 
                                               self.NAMESPACE_PATTERN, 
                                               ehr_status.subject.external_ref.namespace if ehr_status.subject else None))

        if validation_issues:
            raise ValidationException("\n".join(str(issue) for issue in validation_issues))

    def check_contribution(self, contribution: ContributionCreateDto):
        rm_object_validator = self.composition_validator.get_rm_object_validator()

        messages = []

        # Validate audit details
        if contribution.audit:
            self.reject(messages, "/audit/time_committed", "time_committed", contribution.audit.time_committed)
            messages.extend(rm_object_validator.validate(contribution.audit))

        if not contribution.versions:
            messages.append("Versions must not be empty")
        else:
            for version in contribution.versions:
                self.reject(messages, "/version/contribution", "contribution", version.contribution)
                messages.extend(rm_object_validator.validate(version))

        if messages:
            raise ValidationException("\n".join(messages))

    @staticmethod
    def validate(rm_object_validator, path, value):
        if value is not None:
            return rm_object_validator.validate(value)
        return []

    @staticmethod
    def require(type, path, attr, value):
        if value is None:
            return [f"Attribute {attr} of class {type} does not match existence 1..1"]
        return []

    @staticmethod
    def matches(type, path, attr, pattern, value):
        matches = bool(value and pattern.match(value))
        if not matches:
            return [f"Invariant {attr} of class {type} does not match pattern [{pattern.pattern}]"]
        return []

    @staticmethod
    def reject(messages, path, attr, must_be_null):
        if must_be_null is not None:
            messages.append(f"Attribute {attr} must not be set")
