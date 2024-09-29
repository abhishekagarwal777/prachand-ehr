from typing import Dict, Any, Callable, Optional, TypeVar
from dataclasses import dataclass, field
from collections import defaultdict

# Exception definitions
class InternalServerError(Exception):
    pass

RMObjectType = TypeVar('RMObjectType')
OriginalVersionType = TypeVar('OriginalVersionType', bound='OriginalVersion')

@dataclass
class ContributionCreateDto:
    versions: list['OriginalVersion']

@dataclass
class OriginalVersion:
    preceding_version_uid: str  # Placeholder for the actual UID attribute

    def get_preceding_version_uid(self) -> str:
        return self.preceding_version_uid

@dataclass
class ContributionWrapper:
    contribution_create_dto: ContributionCreateDto
    versions_to_dtos: Dict[OriginalVersionType, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize the versions_to_dtos dictionary with the correct size
        self.versions_to_dtos = defaultdict(lambda: None)

    def register_dto_for_version(self, version: OriginalVersionType, dto: Any):
        if version not in self.contribution_create_dto.versions:
            raise InternalServerError(
                f"Cannot register a dto for a [OriginalVersion<{version.get_preceding_version_uid()}>] because it does not exist"
            )
        self.versions_to_dtos[version] = dto

    def for_each_version(self, consumer: Callable[[OriginalVersionType, Optional[Any]], None]):
        for version in self.contribution_create_dto.versions:
            dto = self.versions_to_dtos.get(version)
            consumer(version, dto)
