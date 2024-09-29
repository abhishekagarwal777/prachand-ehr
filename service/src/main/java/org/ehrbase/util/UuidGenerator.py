import os
import threading
import uuid

class UuidGenerator:
    UUID_BYTECOUNT = 16
    GENERATORS = threading.local()  # Thread-local storage

    def __init__(self):
        self.number_generator = os.urandom  # Using os.urandom for randomness
        self.data = bytearray(self.UUID_BYTECOUNT * 32)  # Prepare 32 UUIDs
        self.next_uuid = len(self.data)

    @classmethod
    def random_uuid(cls):
        """Generates a random UUID."""
        if not hasattr(cls.GENERATORS, 'instance'):
            cls.GENERATORS.instance = UuidGenerator()
        return cls.GENERATORS.instance.random_uuid_internal()

    def random_uuid_internal(self):
        """Internal method to generate a random UUID."""
        self.ensure_batch_available()
        pos = self.next_uuid
        self.next_uuid += self.UUID_BYTECOUNT
        return self.create_uuid(self.data, pos)

    def ensure_batch_available(self):
        """Ensures there is a batch of UUIDs available."""
        if self.next_uuid >= len(self.data):
            self.prepare_new_batch()

    def prepare_new_batch(self):
        """Prepares a new batch of UUIDs."""
        self.data[:] = self.number_generator(self.UUID_BYTECOUNT * 32)
        self.next_uuid = 0

    @staticmethod
    def create_uuid(data: bytearray, pos: int) -> uuid.UUID:
        """Creates a UUID from byte data."""
        UuidGenerator.engrave_v4_bytes(data, pos)
        msb = int.from_bytes(data[pos:pos + 8], 'big')
        lsb = int.from_bytes(data[pos + 8:pos + 16], 'big')
        return uuid.UUID((msb, lsb))

    @staticmethod
    def engrave_v4_bytes(data: bytearray, offset: int):
        """Sets the version and variant bits for a version 4 UUID."""
        p6 = offset + 6
        data[p6] &= 0x0f  # Clear version
        data[p6] |= 0x40  # Set to version 4
        p8 = offset + 8
        data[p8] &= 0x3f  # Clear variant
        data[p8] |= 0x80  # Set to IETF variant

