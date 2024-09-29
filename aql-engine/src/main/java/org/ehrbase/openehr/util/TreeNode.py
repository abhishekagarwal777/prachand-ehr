from typing import List, Optional, TypeVar, Generic
from functools import total_ordering

T = TypeVar('T', bound='TreeNode')

@total_ordering
class TreeNode(Generic[T]):
    def __init__(self):
        self.parent: Optional[T] = None
        self.children: List[T] = []

    def get_parent(self) -> Optional[T]:
        return self.parent

    def add_child(self, child: T) -> T:
        if child.parent == self:
            return child

        if child.children:
            ancestor = self.parent
            while ancestor:
                if ancestor == child:
                    raise ValueError("The child is an ancestor of the current node")
                ancestor = ancestor.parent

        child.remove_from_parent()

        child.parent = self
        self.children.append(child)
        return child

    def get_children(self) -> List[T]:
        return list(self.children)  # Returns a shallow copy

    def sort_children(self, key=None, reverse=False):
        self.children.sort(key=key, reverse=reverse)

    def remove_from_parent(self):
        if self.parent:
            self.parent.children.remove(self)
            self.parent = None

    def stream_depth_first(self) -> List[T]:
        result = [self]
        for child in self.children:
            result.extend(child.stream_depth_first())
        return result
