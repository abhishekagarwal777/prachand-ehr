from typing import Set, Optional
from dataclasses import dataclass
from enum import Enum, auto

# Enums
class PathType(Enum):
    EXTRACTED = auto()
    STRUCTURE = auto()
    ITEM = auto()
    OBJECT = auto()
    PRIMITIVE = auto()

@dataclass
class ContainmentClassExpression:
    # Placeholder for actual implementation
    pass

@dataclass
class AqlObjectPath:
    # Placeholder for actual implementation
    pass

@dataclass
class PathQueryDescriptor:
    root: ContainmentClassExpression
    parent: Optional['PathQueryDescriptor']
    represented_path: AqlObjectPath
    type: PathType
    rm_type: Set[str]

    def __str__(self) -> str:
        return (f"PathQueryDescriptor{{root={self.root}, parent={self.parent}, "
                f"represented_path={self.represented_path}, type={self.type}, "
                f"aliased_rm_type={self.rm_type}}}")

    def get_rm_type(self) -> Set[str]:
        return self.rm_type

# Example usage
if __name__ == "__main__":
    root = ContainmentClassExpression()  # Replace with actual instance
    represented_path = AqlObjectPath()  # Replace with actual instance
    descriptor = PathQueryDescriptor(
        root=root,
        parent=None,  # Or another PathQueryDescriptor instance
        represented_path=represented_path,
        type=PathType.STRUCTURE,  # Or another PathType value
        rm_type={'example_rm_type'}
    )
    print(descriptor)
