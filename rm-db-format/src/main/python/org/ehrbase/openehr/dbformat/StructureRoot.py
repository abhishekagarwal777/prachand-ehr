from enum import Enum

class StructureRoot(Enum):
    EHR = (False,)
    EHR_STATUS = (True,)
    COMPOSITION = (True,)
    FOLDER = (True,)

    def __init__(self, versioned: bool):
        self.versioned = versioned

    def is_versioned(self) -> bool:
        return self.versioned

# Example usage
if __name__ == "__main__":
    for root in StructureRoot:
        print(f"{root.name}: versioned={root.is_versioned()}")
