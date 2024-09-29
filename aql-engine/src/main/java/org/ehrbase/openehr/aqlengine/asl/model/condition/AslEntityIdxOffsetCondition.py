from typing import TypeVar
from dataclasses import dataclass

# Define placeholder classes for type hints
class AslQuery:
    pass

@dataclass
class AslEntityIdxOffsetCondition:
    left_provider: AslQuery
    left_owner: AslQuery
    right_provider: AslQuery
    right_owner: AslQuery
    offset: int

    def get_offset(self) -> int:
        return self.offset

    def get_left_owner(self) -> AslQuery:
        return self.left_owner

    def get_right_owner(self) -> AslQuery:
        return self.right_owner

    def get_left_provider(self) -> AslQuery:
        return self.left_provider

    def get_right_provider(self) -> AslQuery:
        return self.right_provider

# Example usage
if __name__ == "__main__":
    # Example instantiation assuming actual implementations of AslQuery
    left_provider = AslQuery()  # Placeholder for actual implementation
    left_owner = AslQuery()     # Placeholder for actual implementation
    right_provider = AslQuery() # Placeholder for actual implementation
    right_owner = AslQuery()    # Placeholder for actual implementation
    offset = 10

    condition = AslEntityIdxOffsetCondition(
        left_provider=left_provider,
        left_owner=left_owner,
        right_provider=right_provider,
        right_owner=right_owner,
        offset=offset
    )

    # Print attributes
    print(condition.get_offset())
    print(condition.get_left_provider())
    print(condition.get_right_provider())
    print(condition.get_left_owner())
    print(condition.get_right_owner())
