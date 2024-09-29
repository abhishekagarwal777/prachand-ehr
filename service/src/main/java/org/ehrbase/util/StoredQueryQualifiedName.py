from typing import Optional


class SemVer:
    NO_VERSION = None  # Assuming NO_VERSION is defined as None for simplicity.

    def __init__(self, major: Optional[int], minor: Optional[int], patch: Optional[int], suffix: Optional[str]):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.suffix = suffix

    def is_no_version(self) -> bool:
        return self.major is None


class StoredQueryQualifiedName:
    def __init__(self, reverse_domain_name: str, semantic_id: str, sem_ver: SemVer):
        if not reverse_domain_name or not semantic_id:
            raise ValueError("reverse_domain_name and semantic_id cannot be None or empty")
        self.reverse_domain_name = reverse_domain_name
        self.semantic_id = semantic_id
        self.sem_ver = sem_ver

    @classmethod
    def create(cls, qualified_name: str, version: Optional[SemVer]) -> 'StoredQueryQualifiedName':
        """
        Creates a StoredQueryQualifiedName from a qualified name string and an optional version.

        :param qualified_name: A qualified name string in the format 'reverse-domain-name::semantic-id'.
        :param version: An optional SemVer instance representing the version.
        :return: A StoredQueryQualifiedName instance.
        :raises ValueError: If the qualified name is not valid.
        """
        name_parts = qualified_name.split("::")

        if len(name_parts) != 2 or '/' in qualified_name:
            raise ValueError(
                "Qualified name is not valid (https://specifications.openehr.org/releases/SM/latest/openehr_platform.html#_query_service): "
                + qualified_name
            )

        return cls(
            name_parts[0],
            name_parts[1],
            version if version is not None else SemVer.NO_VERSION
        )

    def to_name(self) -> str:
        """
        Returns the name part of the qualified query name.

        :return: Concatenated string of reverseDomainName and semanticId.
        """
        return f"{self.reverse_domain_name}::{self.semantic_id}"

    def to_qualified_name_string(self) -> str:
        """
        Returns the fully qualified query name.

        :return: Concatenated string of reverseDomainName, semanticId, and semVer if not None.
        """
        result = f"{self.reverse_domain_name}::{self.semantic_id}"
        if not self.sem_ver.is_no_version():
            result += f"/{self.sem_ver}"
        return result

    def __str__(self) -> str:
        """
        Uses the to_qualified_name_string method.

        :return: Qualified name from the to_qualified_name_string method.
        """
        return self.to_qualified_name_string()
