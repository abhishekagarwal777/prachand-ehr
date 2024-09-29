# test_sem_ver_util.py

import pytest
from semver import SemVer, VersionConflictException
from semver_util import SemVerUtil
from assertpy import assert_that

# Test class to replace the original SemVerUtilTest
class TestSemVerUtil:

    def test_determine_version_from_release(self):
        req = SemVer.parse("1.2.3")
        
        # Test for determining version when no prior version exists
        assert_that(SemVerUtil.determine_version(req, SemVer.NO_VERSION)).is_equal_to(SemVer.parse("1.2.3"))

        # Test for version conflict when the same version is passed
        with pytest.raises(VersionConflictException):
            SemVerUtil.determine_version(req, req)

    def test_determine_version_snapshot(self):
        req = SemVer.parse("1.2.3-SNAPSHOT")
        
        # Test for determining version when no prior version exists
        assert_that(SemVerUtil.determine_version(req, SemVer.NO_VERSION)).is_equal_to(SemVer.parse("1.2.3-SNAPSHOT"))

        # Test for determining version when a matching snapshot version exists
        assert_that(SemVerUtil.determine_version(req, SemVer.parse("1.2.3-SNAPSHOT"))).is_equal_to(SemVer.parse("1.2.3-SNAPSHOT"))

    def test_determine_version_auto(self):
        # Test for determining version when both current and prior versions are SemVer.NO_VERSION
        assert_that(SemVerUtil.determine_version(SemVer.NO_VERSION, SemVer.NO_VERSION)).is_equal_to(SemVer.parse("1.0.0"))

        # Test for determining version when prior version is provided
        assert_that(SemVerUtil.determine_version(SemVer.NO_VERSION, SemVer.parse("41.2.3"))).is_equal_to(SemVer.parse("42.0.0"))

    def test_determine_version_from_partial_major(self):
        req = SemVer.parse("42")
        
        # Test for determining version when no prior version exists
        assert_that(SemVerUtil.determine_version(req, SemVer.NO_VERSION)).is_equal_to(SemVer.parse("42.0.0"))

        # Test for determining version when a prior version exists with the same major number
        assert_that(SemVerUtil.determine_version(req, SemVer.parse("42.4.5"))).is_equal_to(SemVer.parse("42.5.0"))

    def test_determine_version_from_partial_minor(self):
        req = SemVer.parse("3.42")
        
        # Test for determining version when no prior version exists
        assert_that(SemVerUtil.determine_version(req, SemVer.NO_VERSION)).is_equal_to(SemVer.parse("3.42.0"))

        # Test for determining version when a prior version exists with the same major and minor numbers
        assert_that(SemVerUtil.determine_version(req, SemVer.parse("3.42.5"))).is_equal_to(SemVer.parse("3.42.6"))
