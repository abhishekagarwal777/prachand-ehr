from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

class KeyValuePair:
    def __init__(self, id: uuid.UUID, context: str, key: str, value: str):
        self.id = id
        self.context = context
        self.key = key
        self.value = value

    @staticmethod
    def of(plugin_id: str, key: str, value: str) -> 'KeyValuePair':
        return KeyValuePair(uuid.uuid4(), plugin_id, key, value)

    @staticmethod
    def of_with_id(id: uuid.UUID, plugin_id: str, key: str, value: str) -> 'KeyValuePair':
        return KeyValuePair(id, plugin_id, key, value)

    def get_id(self) -> uuid.UUID:
        return self.id

    def get_context(self) -> str:
        return self.context

    def get_key(self) -> str:
        return self.key

    def get_value(self) -> str:
        return self.value

class KeyValuePairRepository(ABC):

    @abstractmethod
    def find_all_by(self, context: str) -> List[KeyValuePair]:
        """Retrieve all key-value pairs associated with a specific context."""
        pass

    @abstractmethod
    def find_by(self, context: str, key: str) -> Optional[KeyValuePair]:
        """Find a key-value pair by its context and key."""
        pass

    @abstractmethod
    def find_by_uuid(self, uid: uuid.UUID) -> Optional[KeyValuePair]:
        """Find a key-value pair by its UUID."""
        pass

    @abstractmethod
    def save(self, kve: KeyValuePair) -> KeyValuePair:
        """Save a key-value pair to the repository."""
        pass

    @abstractmethod
    def delete_by(self, uid: uuid.UUID) -> bool:
        """Delete a key-value pair from the repository using its UUID."""
        pass

# Example concrete implementation
class InMemoryKeyValuePairRepository(KeyValuePairRepository):
    def __init__(self):
        self.store = {}

    def find_all_by(self, context: str) -> List[KeyValuePair]:
        return [v for k, v in self.store.items() if v.get_context() == context]

    def find_by(self, context: str, key: str) -> Optional[KeyValuePair]:
        for k, v in self.store.items():
            if v.get_context() == context and v.get_key() == key:
                return v
        return None

    def find_by_uuid(self, uid: uuid.UUID) -> Optional[KeyValuePair]:
        return self.store.get(uid)

    def save(self, kve: KeyValuePair) -> KeyValuePair:
        self.store[kve.get_id()] = kve
        return kve

    def delete_by(self, uid: uuid.UUID) -> bool:
        if uid in self.store:
            del self.store[uid]
            return True
        return False
