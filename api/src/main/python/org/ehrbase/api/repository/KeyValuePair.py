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

# Example usage
key_value = KeyValuePair.of('plugin1', 'myKey', 'myValue')
print(f"ID: {key_value.get_id()}, Context: {key_value.get_context()}, Key: {key_value.get_key()}, Value: {key_value.get_value()}")
