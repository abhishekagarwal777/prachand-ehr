from enum import Enum
from typing import Type, Set, Optional, Dict
import inspect
from your_module import RMObject, CareEntry, ContentItem, Entry, Event, Item, ItemStructure, ArchieRMInfoLookup, StructureRmType, StructureRoot  # Import your equivalents

class AncestorStructureRmType(Enum):
    """Describes relevant abstract RM structure types."""
    CONTENT_ITEM = (ContentItem,)
    ENTRY = (Entry,)
    CARE_ENTRY = (CareEntry,)
    EVENT = (Event,)
    ITEM_STRUCTURE = (ItemStructure,)
    ITEM = (Item,)

    def __init__(self, rm_type: Type[RMObject]):
        self.type: Type[RMObject] = rm_type
        self.non_structure_descendants: Set[Type[RMObject]] = self.non_abstract_descendants(rm_type)
        self.descendants: Set[StructureRmType] = self.collect_descendants()
        structure_roots = {descendant.get_structure_root() for descendant in self.descendants}
        self.structure_root: Optional[StructureRoot] = structure_roots.pop() if len(structure_roots) == 1 else None

    @classmethod
    def collect_descendants(cls):
        """Collect non-abstract descendants."""
        descendants_set = set()
        for non_abstract in self.non_structure_descendants:
            descendant = StructureRmType.by_type(non_abstract)
            if descendant is not None:
                descendants_set.add(descendant)
        return descendants_set

    @classmethod
    def non_abstract_descendants(cls, rm_type: Type[RMObject]) -> Set[Type[RMObject]]:
        """Get non-abstract descendant classes of a given RMObject type."""
        return {info.get_java_class() for info in ArchieRMInfoLookup.get_instance().get_type_info(rm_type).get_all_descendant_classes()
                if not inspect.isabstract(info.get_java_class())}

    @classmethod
    def by_type(cls, rm_type: Type[RMObject]) -> Optional['AncestorStructureRmType']:
        """Get an AncestorStructureRmType by RMObject type."""
        return cls._by_type.get(rm_type)

    @classmethod
    def by_type_name(cls, rm_type_name: str) -> Optional['AncestorStructureRmType']:
        """Get an AncestorStructureRmType by RMObject type name."""
        return cls._by_type_name.get(rm_type_name)

    @property
    def get_structure_root(self) -> Optional[StructureRoot]:
        """Get the structure root of this type."""
        return self.structure_root

    @property
    def get_descendants(self) -> Set[StructureRmType]:
        """Get descendants of this type."""
        return self.descendants

    @property
    def get_non_structure_descendants(self) -> Set[Type[RMObject]]:
        """Get non-structure descendants of this type."""
        return self.non_structure_descendants

# Pre-compute maps for lookup
AncestorStructureRmType._by_type: Dict[Type[RMObject], 'AncestorStructureRmType'] = {type_.type: type_ for type_ in AncestorStructureRmType}
AncestorStructureRmType._by_type_name: Dict[str, 'AncestorStructureRmType'] = {ArchieRMInfoLookup.get_instance().get_type_info(type_.type).get_rm_name(): type_ for type_ in AncestorStructureRmType}
