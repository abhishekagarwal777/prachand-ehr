from typing import Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class ExceptionFriendlyFunction(Callable[[T], R]):
    def __call__(self, value: T) -> R:
        raise NotImplementedError
