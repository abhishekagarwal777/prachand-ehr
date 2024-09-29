from typing import List, Optional
from collections import defaultdict
from dataclasses import dataclass, field

class StructureRmType:
    # This class should define the possible structure RM types.
    # The implementation needs to be provided based on the original Java enums.
    def __init__(self, name):
        self.name = name

class StructureIndex:
    @classmethod
    def of(cls):
        return cls()

@dataclass
class StructureNode:
    num: int = -1
    numCap: int = -1
    rmEntity: Optional[str] = None
    archetypeNodeId: Optional[str] = None
    entityName: Optional[str] = None
    entityIdx: StructureIndex = field(default_factory=StructureIndex.of)
    children: List['StructureNode'] = field(default_factory=list)
    jsonNode: Optional[dict] = None  # Assuming ObjectNode is a dictionary in Python
    structureRmType: Optional[StructureRmType] = None
    contentItem: Optional['StructureNode'] = None
    parentNum: int = -1

    def __post_init__(self):
        # If parent is provided, add this node to the parent's children
        if hasattr(self, 'parent') and self.parent:
            self.parent.children.append(self)

    def set_structure_rm_type(self, structureRmType: StructureRmType):
        self.structureRmType = structureRmType
        self.rmEntity = structureRmType.name  # Assuming structureRmType has a name attribute

    def get_num_cap(self) -> int:
        if self.numCap == -1:
            if self.children:
                self.numCap = max(child.get_num_cap() for child in self.children)
            else:
                self.numCap = self.num
        return self.numCap

    def add_child(self, child: 'StructureNode'):
        """Adds a child node to this node."""
        self.children.append(child)
        child.parentNum = self.num

    def remove_child(self, child: 'StructureNode'):
        """Removes a child node from this node."""
        self.children.remove(child)

    def get_child_count(self) -> int:
        """Returns the number of children."""
        return len(self.children)

    def has_children(self) -> bool:
        """Checks if this node has children."""
        return len(self.children) > 0

    def __str__(self) -> str:
        return (f"StructureNode{{num={self.num}, rmEntity='{self.rmEntity}', "
                f"entityConcept='{self.archetypeNodeId}', entityName='{self.entityName}', "
                f"entityIdx={self.entityIdx}, children={self.children}, "
                f"jsonNode={self.jsonNode}, structureRmType={self.structureRmType}}}")

    # Getters and Setters
    def get_content_item(self) -> Optional['StructureNode']:
        return self.contentItem

    def set_content_item(self, contentItem: 'StructureNode'):
        self.contentItem = contentItem

    def get_parent_num(self) -> int:
        return self.parentNum

    def set_parent_num(self, parentNum: int):
        self.parentNum = parentNum

    # Additional methods can be added as needed...
