from typing import Optional

class OrderByDirection:
    ASCENDING = 'ascending'
    DESCENDING = 'descending'

class IdentifiedPath:
    # Placeholder for the IdentifiedPath class
    def __init__(self, path: str):
        self._path = path

    def __str__(self) -> str:
        return self._path

class ContainsWrapper:
    # Assuming ContainsWrapper class is already defined as per previous code
    pass

class OrderByWrapper:
    def __init__(self, identified_path: IdentifiedPath, direction: str, root: ContainsWrapper):
        self._identified_path = identified_path
        self._direction = direction
        self._root = root

    def identified_path(self) -> IdentifiedPath:
        return self._identified_path

    def direction(self) -> str:
        return self._direction

    def root(self) -> ContainsWrapper:
        return self._root

    def __str__(self) -> str:
        return f"OrderByWrapper[identifiedPath={self._identified_path}, direction={self._direction}, root={self._root}]"

# Example of usage
order_by_wrapper = OrderByWrapper(
    identified_path=IdentifiedPath("path/to/element"),
    direction=OrderByDirection.ASCENDING,
    root=ContainsWrapper()
)
print(order_by_wrapper)
