import platform
import psutil
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from functools import lru_cache

class BuildProperties:
    """
    This class mimics the functionality of Spring's BuildProperties.
    It's a placeholder for project-specific build properties.
    """
    def __init__(self, properties):
        self.properties = properties

    def get_version(self):
        return self.properties.get("version", "unknown")

    def get(self, key):
        return self.properties.get(key, "unknown")


class StatusServiceImp:
    """
    Python equivalent of the StatusServiceImp class in Java.
    Provides system and build information and interacts with the database to retrieve version information.
    """

    def __init__(self, session_factory, build_properties: BuildProperties):
        self.build_properties = build_properties
        self.session_factory = session_factory

    @lru_cache(maxsize=1)
    def get_operating_system_information(self):
        """
        Lazy-loaded system information equivalent to the `OperatingSystemMXBean` in Java.
        """
        return f"{platform.system()} {platform.machine()} {platform.version()}"

    @lru_cache(maxsize=1)
    def get_java_vm_information(self):
        """
        Lazy-loaded JVM information equivalent, replaced by Python runtime information.
        """
        return f"{platform.python_implementation()} {platform.python_version()}"

    @lru_cache(maxsize=1)
    def get_database_information(self):
        """
        Lazy-loaded database version information.
        Uses a raw SQL query to retrieve the database version, similar to the Jooq DSLContext approach.
        """
        with self.session_factory() as session:
            result = session.execute(text("SELECT VERSION()")).fetchone()
            return result[0] if result else "unknown"

    @lru_cache(maxsize=1)
    def get_ehrbase_version(self):
        """
        Lazy-loaded EHRbase version from the build properties.
        """
        return self.build_properties.get_version()

    @lru_cache(maxsize=1)
    def get_archie_version(self):
        """
        Lazy-loaded Archie version from the build properties.
        """
        return self.build_properties.get("archie.version")

    @lru_cache(maxsize=1)
    def get_open_ehr_sdk_version(self):
        """
        Lazy-loaded openEHR SDK version from the build properties.
        """
        return self.build_properties.get("openEHR_SDK.version")


# Example Usage
# Setup for BuildProperties and session factory
properties = {
    "version": "1.0.0",
    "archie.version": "1.2.3",
    "openEHR_SDK.version": "4.5.6"
}
build_properties = BuildProperties(properties)

# Assuming you have a SQLAlchemy session factory
def session_factory():
    engine = create_engine("postgresql://username:password@localhost:5432/mydatabase")
    return Session(engine)

# Creating the StatusServiceImp instance
status_service = StatusServiceImp(session_factory, build_properties)

# Accessing the various system and version information
print(status_service.get_operating_system_information())  # OS info
print(status_service.get_java_vm_information())           # Python runtime info
print(status_service.get_database_information())          # DB version
print(status_service.get_ehrbase_version())               # EHRbase version
print(status_service.get_archie_version())                # Archie version
print(status_service.get_open_ehr_sdk_version())          # openEHR SDK version
