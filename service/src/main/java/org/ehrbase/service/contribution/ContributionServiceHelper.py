import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from json.decoder import JSONDecodeError

# Exception definitions
class ContributionError(Exception):
    pass

@dataclass
class EhrStatusDto:
    # Attributes should be defined based on the structure of the EhrStatusDto in Java
    pass

@dataclass
class ContributionCreateDto:
    versions: List['OriginalVersion']

@dataclass
class OriginalVersion:
    data: Any  # RMObject equivalent; use an appropriate type based on actual RMObject structure

@dataclass
class ContributionWrapper:
    contribution_create_dto: ContributionCreateDto
    registered_dtos: Dict[OriginalVersion, EhrStatusDto] = field(default_factory=dict)

    def register_dto_for_version(self, original_version: OriginalVersion, ehr_status_dto: EhrStatusDto):
        self.registered_dtos[original_version] = ehr_status_dto

class ContributionServiceHelper:
    @staticmethod
    def unmarshal_contribution(content: str) -> ContributionWrapper:
        try:
            root = json.loads(content)

            # remove "_type" if it exists in the root
            root.pop("_type", None)

            # Convert to DTO
            contribution_create_dto = ContributionCreateDto(versions=[])
            contribution_wrapper = ContributionWrapper(contribution_create_dto)

            # Register additional DTOs for RMObjects
            ContributionServiceHelper.register_dtos(contribution_wrapper, root)

            return contribution_wrapper
        except (KeyError, JSONDecodeError) as e:
            raise ContributionError(f"Error while processing given json input: {str(e)}") from e

    @staticmethod
    def register_dtos(contribution_wrapper: ContributionWrapper, root: Dict[str, Any]):
        raw_versions = root.get("versions", [])
        versions = contribution_wrapper.contribution_create_dto.versions

        for idx in range(len(versions)):
            original_version = versions[idx]
            data = original_version.data

            if isinstance(data, EhrStatus):  # Assuming EhrStatus is defined elsewhere
                if idx < len(raw_versions):
                    node = raw_versions[idx].get("data")
                    if node is not None:
                        node_copy = node.copy()
                        node_copy.pop("_type", None)
                        ehr_status_dto = EhrStatusDto(**node_copy)  # Construct EhrStatusDto from the node
                        contribution_wrapper.register_dto_for_version(original_version, ehr_status_dto)
