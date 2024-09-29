from typing import Optional, Callable


class VersionConflictException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class SemVer:
    def __init__(self, major: Optional[int], minor: Optional[int], patch: Optional[int], suffix: Optional[str]):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.suffix = suffix

    def is_no_version(self) -> bool:
        return self.major is None

    def is_partial(self) -> bool:
        return self.patch is None

    def is_pre_release(self) -> bool:
        return self.suffix is not None

    def __str__(self) -> str:
        parts = [str(self.major)]
        if self.minor is not None:
            parts.append(str(self.minor))
            if self.patch is not None:
                parts.append(str(self.patch))
        return '.'.join(parts)


class SemVerUtil:
    @staticmethod
    def determine_version(request_sem_ver: SemVer, db_sem_ver: SemVer) -> SemVer:
        """
        Based on a (potentially partial) version and the latest existing version that matches the pattern,
        the subsequent version is generated.
        Snapshot versions are retained.

        :param request_sem_ver: The requested semantic version.
        :param db_sem_ver: The existing semantic version in the database.
        :return: The determined semantic version.
        :raises VersionConflictException: If a release version already exists.
        """
        if request_sem_ver.is_no_version():
            major = SemVerUtil.increment_or_default(db_sem_ver, lambda sv: sv.major, 1)
            minor = 0
            patch = 0

        elif not request_sem_ver.is_partial():
            if not db_sem_ver.is_no_version() and not request_sem_ver.is_pre_release():
                raise VersionConflictException("Release versions must not be replaced")
            return request_sem_ver

        elif request_sem_ver.minor is None:
            major = request_sem_ver.major
            minor = SemVerUtil.increment_or_default(db_sem_ver, lambda sv: sv.minor, 0)
            patch = 0

        else:  # db_sem_ver.patch is None
            major = request_sem_ver.major
            minor = request_sem_ver.minor
            patch = SemVerUtil.increment_or_default(db_sem_ver, lambda sv: sv.patch, 0)

        return SemVer(major, minor, patch, None)

    @staticmethod
    def increment_or_default(sem_ver: SemVer, func: Callable[[SemVer], Optional[int]], fallback: int) -> int:
        if sem_ver.is_no_version():
            return fallback
        else:
            return func(sem_ver) + 1
