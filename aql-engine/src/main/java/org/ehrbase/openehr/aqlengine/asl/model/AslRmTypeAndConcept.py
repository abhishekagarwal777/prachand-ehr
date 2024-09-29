from typing import Optional
from dataclasses import dataclass

ARCHETYPE_PREFIX = "openEHR-EHR-"

@dataclass
class AslRmTypeAndConcept:
    aliased_rm_type: Optional[str]
    concept: str

    @staticmethod
    def from_archetype_node_id(archetype_node_id: Optional[str]) -> Optional['AslRmTypeAndConcept']:
        if not archetype_node_id:
            return None

        if archetype_node_id.startswith(ARCHETYPE_PREFIX):
            pos = archetype_node_id.find('.', len(ARCHETYPE_PREFIX))
            if pos < 0:
                raise ValueError(f"Archetype id is not valid: {archetype_node_id}")
            alias = RmTypeAlias.optional_alias(archetype_node_id[len(ARCHETYPE_PREFIX):pos])
            if alias is None:
                raise ValueError(f"Archetype id for unsupported/unknown RM type: {archetype_node_id}")
            concept = archetype_node_id[pos:]
            return AslRmTypeAndConcept(alias, concept)

        elif archetype_node_id.startswith("at") or archetype_node_id.startswith("id"):
            return AslRmTypeAndConcept(None, archetype_node_id)
        else:
            raise ValueError(f"Invalid archetype_node_id: {archetype_node_id}")

    @staticmethod
    def to_entity_concept(archetype_node_id: Optional[str]) -> Optional[str]:
        if not archetype_node_id:
            return None
        return AslRmTypeAndConcept.from_archetype_node_id(archetype_node_id).concept

# Assuming RmTypeAlias is implemented in Python
class RmTypeAlias:
    @staticmethod
    def optional_alias(alias: str) -> Optional[str]:
        # Implement the method to return the alias if it exists
        # This is a placeholder implementation
        return alias if alias in ['supported_alias'] else None
