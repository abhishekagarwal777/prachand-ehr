import uuid
import io
import csv
import pytest
from unittest import mock
from datetime import datetime, timezone, timedelta
from collections import namedtuple
from typing import Tuple, List

# Mocked classes and enums
class Locatable:
    pass

class Composition(Locatable):
    pass

class TimeProvider:
    def get_now(self):
        pass

class CompositionRepository:
    def __init__(self, context, param1, param2, param3, time_provider):
        self.context = context
        self.time_provider = time_provider

    def to_records(self, ehr_id, version_data_object, contribution_id, audit_id):
        # Mock implementation for conversion to records
        return VersionDataDbRecord()  # Should return a version record

class VersionDataDbRecord:
    def version_record(self):
        return [self]  # Mocking version record

    def data_records(self):
        return [self]  # Mocking data records


@pytest.fixture
def setup_composition_repository():
    """Fixture to set up the Composition repository for testing."""
    time_provider = mock.Mock(spec=TimeProvider)
    yield CompositionRepository(None, None, None, None, time_provider)


class CompositionTestDataCanonicalJson:
    IPS = "ips"
    
    @staticmethod
    def get_stream(name):
        return io.BytesIO(name.encode())  # Mocking data stream


def load_expected_csv(name: str, version: bool) -> str:
    with open(f"{name}{'.version' if version else '.data'}.csv", mode='r', newline='') as infile:
        return infile.read()


def to_csv(version_data_object: Locatable, time_provider: TimeProvider) -> Tuple[str, str]:
    now = datetime(2022, 3, 21, 23, 45, 10, 123456, tzinfo=timezone.utc)
    time_provider.get_now = mock.Mock(return_value=now)

    repo = CompositionRepository(None, None, None, None, time_provider)

    version_data = repo.to_records(uuid.UUID("a6080b1b-da89-4992-b179-279a06ebe0e5"), version_data_object,
                                    uuid.UUID("6c8f92e4-7562-4962-9065-83c6d1e94dfb"),
                                    uuid.UUID("ce70b0d9-99ac-4ca2-a017-d69284dde509"))

    version_csv = to_csv_helper([version_data.version_record()])
    data_csv = to_csv_helper(version_data.data_records())
    return version_csv, data_csv


def to_csv_helper(data_records: List[VersionDataDbRecord]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    
    # Assuming records have a specific structure, this will vary based on your actual implementation
    for record in data_records:
        writer.writerow(record)  # Replace with appropriate record attributes

    return output.getvalue()


def load_locatable(name: str, type_: type) -> Locatable:
    with open(f"{name}.json", mode='r') as infile:
        data = infile.read()
        return to_locatable(data, type_)


def to_locatable(data: str, type_: type) -> Locatable:
    return CanonicalJson().unmarshal(data, type)  # Mocked unmarshal implementation


class TestCompositionRepository:

    @pytest.fixture(autouse=True)
    def setup(self, setup_composition_repository):
        self.composition_repository = setup_composition_repository

    def test_ips_db_format(self):
        composition = get_composition(CompositionTestDataCanonicalJson.IPS)
        expected_version_csv = load_expected_csv("ips", True)
        expected_data_csv = load_expected_csv("ips", False)
        csv = to_csv(composition, self.composition_repository.time_provider)
        assert csv[0] == expected_version_csv.strip()
        assert csv[1] == expected_data_csv.strip()

    def test_conformance_max_db_format(self):
        composition = load_locatable("conformance_ehrbase.de.v0_max", Composition)
        expected_version_csv = load_expected_csv("conformance_ehrbase.de.v0_max", True)
        expected_data_csv = load_expected_csv("conformance_ehrbase.de.v0_max", False)
        csv = to_csv(composition, self.composition_repository.time_provider)
        assert csv[0] == expected_version_csv.strip()
        assert csv[1] == expected_data_csv.strip()

def get_composition(composition_type) -> Composition:
    with CompositionTestDataCanonicalJson.get_stream(composition_type) as stream:
        return to_locatable(stream.getvalue(), Composition)


class CanonicalJson:
    @staticmethod
    def unmarshal(data: str, type_: type) -> Locatable:
        # Mock implementation for unmarshalling
        return type_()  # Should return an instance of the specified type
