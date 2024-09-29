import re
from typing import Optional


class InvalidVersionFormatException(Exception):
    def __init__(self, sem_ver_str: str):
        super().__init__(f"Invalid version format: {sem_ver_str}")


class SemVer:
    """
    A class representing a Semantic Versioning scheme.
    """

    # Regex pattern for semantic versioning
    SEMVER_REGEX = re.compile(
        r"(?P<major>0|[1-9]\d*)"
        r"(?:\.(?P<minor>0|[1-9]\d*))?"
        r"(?:\.(?P<patch>0|[1-9]\d*))?"
        r"(?:-(?P<suffix>(?:0|[1-9]\d*|[1-9]\d*[-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*))*)*)?"
    )

    NO_VERSION = None  # Represents no version

    def __init__(self, major: Optional[int], minor: Optional[int], patch: Optional[int], suffix: Optional[str]):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.suffix = suffix

    @classmethod
    def parse(cls, sem_ver_str: str) -> 'SemVer':
        if not sem_ver_str or sem_ver_str.strip().lower() == "latest":
            return cls(None, None, None, None)

        matcher = cls.SEMVER_REGEX.fullmatch(sem_ver_str)
        if matcher is None:
            raise InvalidVersionFormatException(sem_ver_str)

        return cls(
            cls.integer_from_group(matcher, 'major'),
            cls.integer_from_group(matcher, 'minor'),
            cls.integer_from_group(matcher, 'patch'),
            matcher.group('suffix')  # optional group, will be None if not found
        )

    def to_version_string(self) -> str:
        if self.is_no_version():
            return ""
        parts = [str(self.major)]
        if self.minor is not None:
            parts.append(str(self.minor))
            if self.patch is not None:
                parts.append(str(self.patch))
                if self.suffix is not None:
                    parts.append(f"-{self.suffix}")
        return '.'.join(parts)

    def is_no_version(self) -> bool:
        return self.major is None

    def is_partial(self) -> bool:
        return self.patch is None

    def is_release(self) -> bool:
        return self.patch is not None and self.suffix is None

    def is_pre_release(self) -> bool:
        return self.suffix is not None

    @staticmethod
    def integer_from_group(matcher: re.Match, group_name: str) -> Optional[int]:
        group_value = matcher.group(group_name)
        return int(group_value) if group_value is not None else None

    def __str__(self) -> str:
        return self.to_version_string()
