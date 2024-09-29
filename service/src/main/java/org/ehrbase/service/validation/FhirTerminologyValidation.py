import logging
import requests
from requests.exceptions import RequestException
from typing import List, Optional, Dict, Any, Tuple

class InternalServerException(Exception):
    pass

class ExternalTerminologyValidationException(Exception):
    pass

class ConstraintViolation:
    def __init__(self, message: str):
        self.message = message

class ConstraintViolationException(Exception):
    def __init__(self, violations: List[ConstraintViolation]):
        self.violations = violations

class CodePhrase:
    def __init__(self, terminology_id: str, code_string: str):
        self.terminology_id = TerminologyId(terminology_id)
        self.code_string = code_string

class TerminologyId:
    def __init__(self, value: str):
        self.value = value

class DvCodedText:
    def __init__(self, display: str, code_phrase: CodePhrase):
        self.display = display
        self.code_phrase = code_phrase

class TerminologyParam:
    def __init__(self, service_api: Optional[str] = None, use_value_set: bool = False, use_code_system: bool = False, code_phrase: Optional[CodePhrase] = None):
        self._service_api = service_api
        self._use_value_set = use_value_set
        self._use_code_system = use_code_system
        self._code_phrase = code_phrase

    def get_service_api(self) -> Optional[str]:
        return self._service_api

    def is_use_value_set(self) -> bool:
        return self._use_value_set

    def is_use_code_system(self) -> bool:
        return self._use_code_system

    def get_code_phrase(self) -> Optional[CodePhrase]:
        return self._code_phrase

    def extract_from_parameter(self, extractor) -> Optional[str]:
        # Placeholder for parameter extraction logic
        return None

class FhirTerminologyValidation:
    SUPPORTS_CODE_SYS_TEMPL = "%s/CodeSystem?url=%s"
    SUPPORTS_VALUE_SET_TEMPL = "%s/ValueSet?url=%s"
    CODE_PHRASE_TEMPL = "code=%s&system=%s"
    EXPAND_VALUE_SET_TEMPL = "%s/ValueSet/$expand?%s"
    ERR_SUPPORTS = "An error occurred while checking if FHIR terminology server supports the referenceSetUri: %s"
    ERR_EXPAND_VALUESET = "Error while expanding ValueSet[%s]"

    def __init__(self, base_url: str, fail_on_error: bool = True):
        self.base_url = base_url
        self.fail_on_error = fail_on_error
        self.logger = logging.getLogger(__name__)

    def extract_url(self, reference_set_uri: str) -> str:
        return reference_set_uri.split("url=")[-1]

    def build_rest_client_call(self, url: str) -> str:
        headers = {'Accept': 'application/fhir+json'}
        return url, headers

    def internal_get(self, uri: str) -> Dict[str, Any]:
        url, headers = self.build_rest_client_call(uri)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if self.fail_on_error:
                raise InternalServerException("could not connect to external Terminology Server") from e
            else:
                self.logger.warning("An error occurred: %s", str(e))
                return {}

    def is_valid_terminology(self, url: Optional[str]) -> bool:
        accepted_fhir_apis = [
            "//fhir.hl7.org",
            "terminology://fhir.hl7.org",
            "//hl7.org/fhir"
        ]
        if not url:
            return False
        return any(url.startswith(api) for api in accepted_fhir_apis)

    def supports(self, param: TerminologyParam) -> bool:
        url_param = param.extract_from_parameter(self.extract_url)
        if not url_param or not self.is_valid_terminology(param.get_service_api()):
            return False

        if param.is_use_value_set():
            url = self.SUPPORTS_VALUE_SET_TEMPL % (self.base_url, url_param)
        elif param.is_use_code_system():
            url = self.SUPPORTS_CODE_SYS_TEMPL % (self.base_url, url_param)
        else:
            return False

        try:
            return self.internal_get(url).get("total", 0) > 0
        except Exception as e:
            if self.fail_on_error:
                raise ExternalTerminologyValidationException(self.ERR_SUPPORTS % url) from e
            self.logger.warning("The following error occurred: %s", str(e))
            return False

    def validate(self, param: TerminologyParam) -> Tuple[bool, Optional[ConstraintViolationException]]:
        url = param.extract_from_parameter(self.extract_url)
        if not url:
            return False, ConstraintViolationException([ConstraintViolation("Missing value-set url")])

        if param.is_use_code_system():
            return self.validate_code(url, param.get_code_phrase())
        elif param.is_use_value_set():
            return self.expand_value_set(url, param.get_code_phrase())
        else:
            raise ValueError("Invalid state")

    def validate_code(self, url: str, code_phrase: CodePhrase) -> Tuple[bool, Optional[ConstraintViolationException]]:
        if url != code_phrase.terminology_id.value:
            violation = ConstraintViolation(f"The terminology {code_phrase.terminology_id.value} must be {url}")
            return False, ConstraintViolationException([violation])

        try:
            context = self.internal_get(f"{self.base_url}/CodeSystem/$validate-code?url={url}&code={code_phrase.code_string}")
        except Exception as e:
            if self.fail_on_error:
                raise ExternalTerminologyValidationException("An error occurred while validating the code in CodeSystem") from e
            self.logger.warning("An error occurred while validating the code in CodeSystem: %s", str(e))
            return False, None

        result = context.get("parameter", [{}])[0].get("valueBoolean", False)
        if not result:
            message = context.get("parameter", [{}])[1].get("valueString", "")
            violation = ConstraintViolation(message)
            return False, ConstraintViolationException([violation])

        return True, None

    def expand_value_set(self, url: str, code_phrase: CodePhrase) -> Tuple[bool, Optional[ConstraintViolationException]]:
        try:
            context = self.internal_get(f"{self.base_url}/ValueSet/$expand?url={url}")
        except Exception as e:
            if self.fail_on_error:
                raise ExternalTerminologyValidationException("An error occurred while expanding the ValueSet") from e
            self.logger.warning("An error occurred while expanding the ValueSet: %s", str(e))
            return False, None

        codings = [
            item for item in context.get("expansion", {}).get("contains", [])
            if item.get("code") == code_phrase.code_string
        ]

        if not codings:
            violation = ConstraintViolation(f"The value {code_phrase.code_string} does not match any option from value set {url}")
            return False, ConstraintViolationException([violation])
        elif len(codings) == 1:
            coding = codings[0]
            system = coding.get("system")
            if system != code_phrase.terminology_id.value:
                violation = ConstraintViolation(f"The terminology {code_phrase.code_string} must be {system}")
                return False, ConstraintViolationException([violation])

        return True, None

    def expand(self, param: TerminologyParam) -> List[DvCodedText]:
        if not param.get_service_api() or not self.is_valid_terminology(param.get_service_api()):
            self.logger.warning("Unsupported service-api: %s", param.get_service_api())
            return []

        url_param = param.extract_from_parameter(lambda p: self.guarantee_prefix("url=", p))
        if not url_param or not self.is_valid_terminology(param.get_service_api()):
            return []

        try:
            json_context = self.internal_get(self.EXPAND_VALUE_SET_TEMPL % (self.base_url, url_param))
            return self.value_set_converter(json_context)
        except Exception as e:
            if self.fail_on_error:
                raise ExternalTerminologyValidationException(self.ERR_EXPAND_VALUESET % str(e)) from e
            self.logger.warning(self.ERR_EXPAND_VALUESET % str(e))
            return []

    def guarantee_prefix(self, prefix: str, string: str) -> Optional[str]:
        if not string:
            return None
        return string if prefix in string else prefix + string

    def value_set_converter(self, ctx: Dict[str, Any]) -> List[DvCodedText]:
        contains = ctx.get("expansion", {}).get("contains", [])
        return [
            DvCodedText(item.get("display"), CodePhrase(item.get("system"), item.get("code")))
            for item in contains
        ]
