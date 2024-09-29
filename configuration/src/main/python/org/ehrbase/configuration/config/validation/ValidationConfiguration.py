from typing import Dict, Optional, Union, List
import logging
from pydantic import BaseModel
import requests
from requests.exceptions import RequestException
from cachetools import TTLCache
from functools import partial

logger = logging.getLogger(__name__)

class ValidationProperties(BaseModel):
    enabled: bool
    fail_on_error: bool
    provider: Dict[str, 'Provider']

    class Provider(BaseModel):
        type: str
        url: str
        oauth2_client: Optional[str]

class CacheProvider:
    EXTERNAL_FHIR_TERMINOLOGY_CACHE = 'external_fhir_terminology_cache'

    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=3600)

    def get(self, cache_name: str, key: str, fetch_function):
        try:
            if key in self.cache:
                return self.cache[key]
            else:
                value = fetch_function()
                self.cache[key] = value
                return value
        except Exception as e:
            raise ValueRetrievalException(e)

class ValueRetrievalException(Exception):
    def __init__(self, cause):
        super().__init__(str(cause))
        self.cause = cause

class ExternalTerminologyValidation:
    def validate(self, param) -> bool:
        raise NotImplementedError()

class NopExternalTerminologyValidation(ExternalTerminologyValidation):
    def __init__(self, error_message: str):
        self.error_message = error_message

    def validate(self, param) -> bool:
        raise Exception(self.error_message)

class FhirTerminologyValidation(ExternalTerminologyValidation):
    def __init__(self, url: str, fail_on_error: bool, web_client):
        self.url = url
        self.fail_on_error = fail_on_error
        self.web_client = web_client

    def internal_get(self, uri: str) -> dict:
        try:
            response = self.web_client.get(uri)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if self.fail_on_error:
                raise BadGatewayException(str(e)) from e
            else:
                raise InternalServerException(f"Failure during FHIR terminology request: {e}") from e

class BadGatewayException(Exception):
    pass

class InternalServerException(Exception):
    pass

class ValidationConfiguration:
    ERR_MSG = "External terminology validation is disabled, consider enabling it"

    def __init__(self, properties: ValidationProperties, cache_provider: CacheProvider, 
                 authorized_client_manager: Optional[str]):
        self.properties = properties
        self.cache_provider = cache_provider
        self.authorized_client_manager = authorized_client_manager

    def external_terminology_validator(self) -> ExternalTerminologyValidation:
        if not self.properties.enabled:
            logger.warning(self.ERR_MSG)
            return self.nop_terminology_validation()

        providers = self.properties.provider

        if not providers:
            raise ValueError("At least one external terminology provider must be defined "
                             "if 'validation.external-validation.enabled' is set to 'true'")
        elif len(providers) == 1:
            return self.build_external_terminology_validation(
                next(iter(providers.items()))
            )
        else:
            chain = ExternalTerminologyValidationChain()
            for named_provider in providers.items():
                chain.add_external_terminology_validation_support(
                    self.build_external_terminology_validation(named_provider)
                )
            return chain

    def build_external_terminology_validation(self, named_provider) -> ExternalTerminologyValidation:
        name, provider = named_provider
        oauth2_client = provider.oauth2_client

        logger.info(
            f"Initializing '{name}' external terminology provider (type: {provider.type}) at {provider.url} "
            f"{f'secured by oauth2 client \'{oauth2_client}\'' if oauth2_client else ''}"
        )

        web_client = self.build_web_client(oauth2_client)

        if provider.type == 'FHIR':
            return FhirTerminologyValidation(provider.url, self.properties.fail_on_error, web_client)
        else:
            raise ValueError(f"Invalid provider type: {provider.type}")

    def build_web_client(self, client_id: Optional[str]) -> requests.Session:
        session = requests.Session()
        if client_id:
            if not self.authorized_client_manager:
                raise ValueError(
                    f"Attempt to create an oauth2 client with id 'spring.security.oauth2.registration.{client_id}' "
                    "but no clients are registered."
                )
            # Set up OAuth2 client, using a placeholder for actual implementation
            session.headers.update({'Authorization': f'Bearer {client_id}'})
        return session

    @staticmethod
    def nop_terminology_validation() -> ExternalTerminologyValidation:
        return NopExternalTerminologyValidation(ValidationConfiguration.ERR_MSG)

class ExternalTerminologyValidationChain(ExternalTerminologyValidation):
    def __init__(self):
        self.validations = []

    def add_external_terminology_validation_support(self, validation: ExternalTerminologyValidation):
        self.validations.append(validation)

    def validate(self, param) -> bool:
        for validation in self.validations:
            if not validation.validate(param):
                return False
        return True
