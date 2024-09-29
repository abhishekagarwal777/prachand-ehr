# test_uuid_generator.py

import uuid
import pytest
from uuid_generator import UuidGenerator
from assertpy import assert_that
from concurrent.futures import ThreadPoolExecutor


# uuid_generator.py

import uuid

class UuidGenerator:
    @staticmethod
    def random_uuid():
        return uuid.uuid4()




class TestUuidGenerator:

    def test_random_uuid(self):
        # Check that the UUID is not None
        assert UuidGenerator.random_uuid() is not None

        # Check that different UUIDs are generated on subsequent calls
        assert UuidGenerator.random_uuid() != UuidGenerator.random_uuid()

        # Check that 1000 parallel UUID generations result in unique UUIDs
        with ThreadPoolExecutor() as executor:
            uuids = list(executor.map(lambda _: UuidGenerator.random_uuid(), range(1000)))
        assert len(set(uuids)) == 1000

    def test_uuid_version_and_variant(self):
        # Check the UUID version and variant
        for _ in range(1000):
            uuid_val = UuidGenerator.random_uuid()
            assert uuid_val.version == 4
            assert uuid_val.variant == 2

    def test_all_chars_variable(self):
        first_uuid = str(UuidGenerator.random_uuid())

        char_variables = [False] * len(first_uuid)

        for _ in range(1000):
            uuid_str = str(UuidGenerator.random_uuid())
            for j in range(len(char_variables)):
                # Ignore 15th character (index 14) as it is reserved for version
                if not char_variables[j] and (first_uuid[j] != uuid_str[j] or first_uuid[j] == '-' or j == 14):
                    char_variables[j] = True

        assert_that(char_variables).does_not_contain(False)
