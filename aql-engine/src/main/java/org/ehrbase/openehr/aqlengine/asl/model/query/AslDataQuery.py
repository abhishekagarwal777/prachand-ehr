from typing import List, Optional

class AslQuery:
    def __init__(self, alias: str, select: List['AslQuery']):
        self.alias = alias
        self.select = select

class AslDataQuery(AslQuery):
    def __init__(self, alias: str, base: Optional[AslQuery], base_provider: AslQuery):
        super().__init__(alias, [])
        self.base = base
        self.base_provider = base_provider

    def get_base(self) -> Optional[AslQuery]:
        return self.base

    def set_base(self, base: 'AslStructureQuery') -> None:
        self.base = base

    def get_base_provider(self) -> AslQuery:
        return self.base_provider
