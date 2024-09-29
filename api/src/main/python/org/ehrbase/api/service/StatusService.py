from abc import ABC, abstractmethod

class StatusService(ABC):

    @abstractmethod
    def get_operating_system_information(self) -> str:
        """
        Returns information on the current operating system this EHRbase instance is running on.
        """
        pass

    @abstractmethod
    def get_java_vm_information(self) -> str:
        """
        Returns information on the current Java Virtual Machine that is running this EHRbase instance.
        """
        pass

    @abstractmethod
    def get_database_information(self) -> str:
        """
        Returns information on the current connected Database instance version.
        """
        pass

    @abstractmethod
    def get_ehrbase_version(self) -> str:
        """
        Returns current version of EHRbase build that is running.
        """
        pass

    @abstractmethod
    def get_archie_version(self) -> str:
        """
        Returns current version of Archie which has been used to build the running EHRbase instance.
        """
        pass

    @abstractmethod
    def get_open_ehr_sdk_version(self) -> str:
        """
        Returns the current version of ehrbase SDK which has been used to build the running EHRbase instance.
        """
        pass
