# test_sem_ver.py

import pytest
from semver import SemVer, InvalidVersionFormatException
from assertpy import assert_that

# Test class to replace the original SemVerTest
class TestSemVer:

    def test_parse(self):
        # Test parsing an empty string
        ver = SemVer.parse("")
        assert_that(ver).is_equal_to(SemVer.NO_VERSION)

        # Test parsing "Latest"
        ver = SemVer.parse("Latest")
        assert_that(ver).is_equal_to(SemVer.NO_VERSION)

        # Test parsing "1"
        ver = SemVer.parse("1")
        assert_that(ver.major).is_equal_to(1)
        assert_that(ver.minor).is_none()
        assert_that(ver.patch).is_none()
        assert_that(ver.suffix).is_none()

        # Test parsing "1.2"
        ver = SemVer.parse("1.2")
        assert_that(ver.major).is_equal_to(1)
        assert_that(ver.minor).is_equal_to(2)
        assert_that(ver.patch).is_none()
        assert_that(ver.suffix).is_none()

        # Test parsing "1.29.3"
        ver = SemVer.parse("1.29.3")
        assert_that(ver.major).is_equal_to(1)
        assert_that(ver.minor).is_equal_to(29)
        assert_that(ver.patch).is_equal_to(3)
        assert_that(ver.suffix).is_none()

        # Test parsing "1.2.3-SNAPSHOT"
        ver = SemVer.parse("1.2.3-SNAPSHOT")
        assert_that(ver.major).is_equal_to(1)
        assert_that(ver.minor).is_equal_to(2)
        assert_that(ver.patch).is_equal_to(3)
        assert_that(ver.suffix).is_equal_to("SNAPSHOT")

        # Test parsing "1.2.3-THE-SNAPSHOT.1.42"
        ver = SemVer.parse("1.2.3-THE-SNAPSHOT.1.42")
        assert_that(ver.major).is_equal_to(1)
        assert_that(ver.minor).is_equal_to(2)
        assert_that(ver.patch).is_equal_to(3)
        assert_that(ver.suffix).is_equal_to("THE-SNAPSHOT.1.42")

    @pytest.mark.parametrize("param", [
        ".", "1.", "1.2-SNAPSHOT", "1-SNAPSHOT", "-SNAPSHOT", "1.2.3.4",
        "1.2.3-SNAPSHOT.01", "1.0.0-alpha+001", "1.0.0+20130313144700",
        "1.0.0-beta+exp.sha.5114f85", "1.0.0+21AF26D3----117B344092BD"
    ])
    def test_parse_invalid(self, param):
        # Assert that invalid versions raise the InvalidVersionFormatException
        with pytest.raises(InvalidVersionFormatException):
            SemVer.parse(param)

    def test_to_version_string(self):
        # Test converting version to string
        assert_that(SemVer(1, None, None, None).to_version_string()).is_equal_to("1")
        assert_that(SemVer(1, 2, None, None).to_version_string()).is_equal_to("1.2")
        assert_that(SemVer(1, 2, 3, None).to_version_string()).is_equal_to("1.2.3")
        assert_that(SemVer(1, 2, 3, "SNAPSHOT").to_version_string()).is_equal_to("1.2.3-SNAPSHOT")


import semver

# Example of using semver functions
version1 = "1.0.0"
version2 = "2.0.0"

# Compare versions
comparison = semver.compare(version1, version2)
if comparison < 0:
    print(f"{version1} is less than {version2}")
elif comparison > 0:
    print(f"{version1} is greater than {version2}")
else:
    print(f"{version1} is equal to {version2}")

# Parse a version
parsed_version = semver.parse(version1)
print(parsed_version)  # Output: {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None, 'build': None}

import semver

def validate_version(version):
    try:
        # This will raise ValueError if the version format is invalid
        parsed_version = semver.parse(version)
        print(f"Parsed version: {parsed_version}")
    except ValueError as e:
        print(f"Invalid version format: {version}. Error: {e}")

# Example usage
validate_version("1.0.0")  # Valid version
validate_version("invalid.version")  # Invalid version
