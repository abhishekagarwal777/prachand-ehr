from typing import List, Optional, Stream
import itertools


class RmAttributeAlias:
    @staticmethod
    def get_alias(attribute: str) -> str:
        # This method should return the alias for the given attribute.
        # Implementation needs to be defined based on your requirements.
        return attribute


class StructureIndex:
    CAP_SYMBOL = "~"  # Lexicographically larger than all employed symbols [0-9, A-Z, a-z]
    INDEX_DELIMITER = "."  # Lexicographically smaller than all employed symbols [0-9, A-Z, a-z]

    class Node:
        def __init__(self, attribute: str, idx: Optional[int]):
            self.attribute = attribute
            self.idx = idx

        @classmethod
        def of(cls, attribute: str, idx: Optional[int]) -> 'StructureIndex.Node':
            return cls(attribute, idx)

        def get_attribute(self) -> str:
            return self.attribute

        def get_idx(self) -> Optional[int]:
            return self.idx

        def __eq__(self, other):
            if not isinstance(other, StructureIndex.Node):
                return False
            return (self.idx, self.attribute) == (other.idx, other.attribute)

        def __hash__(self):
            return hash((self.attribute, self.idx))

        def __str__(self) -> str:
            return f"Node('{self.attribute}' {self.idx})"

    def __init__(self, *index: Node):
        self.index = list(index)

    def create_child(self, i: Node) -> 'StructureIndex':
        return StructureIndex(*(self.index + [i]))

    def __eq__(self, other):
        if not isinstance(other, StructureIndex):
            return False
        return self.index == other.index

    def __hash__(self):
        return hash(tuple(self.index))

    @classmethod
    def of(cls, *index: Node) -> 'StructureIndex':
        return cls(*index)

    @classmethod
    def of_single(cls, attribute: str, index: int) -> 'StructureIndex':
        return cls(cls.Node(attribute, index))

    def stream(self) -> Stream[Node]:
        return iter(self.index)

    def length(self) -> int:
        return len(self.index)

    def starts_with(self, prefix: 'StructureIndex') -> bool:
        p_idx = prefix.index
        p_len = len(p_idx)
        if self.length() < p_len:
            return False
        return self.index[:p_len] == p_idx

    def print_index_string(self, cap: bool, with_index: bool) -> str:
        if self.length() == 0:
            return self.CAP_SYMBOL if cap else ""
        else:
            nodes_string = self.index_to_string(with_index)
            return f"{self.INDEX_DELIMITER}{self.CAP_SYMBOL}" if cap else f"{self.INDEX_DELIMITER}{nodes_string}"

    def print_last_attribute(self) -> Optional[str]:
        if len(self.index) == 0:
            return None
        last_node = self.index[-1]
        return self.get_node_string(last_node, False)

    def get_node_string(self, node: Node, with_index: bool) -> str:
        att = RmAttributeAlias.get_alias(node.attribute)
        return f"{att}{node.idx}" if with_index and node.idx is not None else att

    def index_to_string(self, with_index: bool) -> str:
        return self.INDEX_DELIMITER.join(
            self.get_node_string(node, with_index) for node in self.index
        )

    def __str__(self) -> str:
        return str(self.index)
