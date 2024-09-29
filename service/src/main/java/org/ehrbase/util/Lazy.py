from typing import Callable, TypeVar, Generic

V = TypeVar('V')

class Lazy(Generic[V]):
    """
    Lazy property value that can be used to cache values with "expensive" calculations during the first time of access.
    Usage:
    ```
    from #your_module# import Lazy

    class MyClass:
        def __init__(self):
            self.lazy_value = Lazy(lambda: "some expensive calculated value")

        def get_value(self):
            return self.lazy_value.get()
    ```
    """

    def __init__(self, supplier: Callable[[], V]):
        self._value = None  # equivalent to private V value = null in Java
        self._supplier = supplier

    def get(self) -> V:
        if self._value is None:
            self._value = self._supplier()
        return self._value

    @staticmethod
    def lazy(supplier: Callable[[], V]) -> 'Lazy[V]':
        return Lazy(supplier)
