from abc import ABC, abstractmethod
from typing import Type, Optional
from dataclasses import dataclass, field

class AslExtractedColumn:
    # Define necessary attributes and methods
    pass

@dataclass(frozen=True)
class FieldSource:
    owner: 'AslQuery'
    internal_provider: 'AslQuery'
    provider: 'AslQuery'

    @staticmethod
    def with_owner(owner: 'AslQuery') -> 'FieldSource':
        return FieldSource(owner=owner, internal_provider=owner, provider=owner)

    def with_provider(self, new_provider: 'AslQuery') -> 'FieldSource':
        return FieldSource(owner=self.owner, internal_provider=self.provider, provider=new_provider)

class AslQuery(ABC):
    # Define necessary attributes and methods
    @abstractmethod
    def get_alias(self) -> str:
        pass

@dataclass(frozen=True)
class AslField(ABC):
    type: Type
    field_source: Optional[FieldSource]
    extracted_column: Optional[AslExtractedColumn]

    @abstractmethod
    def with_provider(self, provider: AslQuery) -> 'AslField':
        pass

    @abstractmethod
    def copy_with_owner(self, owner: AslQuery) -> 'AslField':
        pass

    def aliased_name(self, name: str) -> str:
        if self.field_source and self.field_source.owner:
            return f"{self.field_source.owner.get_alias()}_{name}"
        return name

class AslVirtualField(AslField):
    def __init__(self, type: Type, field_source: FieldSource, extracted_column: AslExtractedColumn):
        super().__init__(type=type, field_source=field_source, extracted_column=extracted_column)

    def aliased_name(self, name: str) -> str:
        return super().aliased_name(name)
