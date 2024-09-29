from typing import List, Optional
import uuid

class UnprocessableEntityException(Exception):
    """Exception to be raised when an entity cannot be processed."""
    pass


class TemplateMetaData:
    """Placeholder for TemplateMetaData class."""
    pass


class OPERATIONALTEMPLATE:
    """Placeholder for OPERATIONALTEMPLATE class with a templateId attribute."""
    
    def __init__(self, template_id_value: str):
        self.template_id = self.TemplateId(template_id_value)

    class TemplateId:
        def __init__(self, value: str):
            self.value = value

        def get_value(self):
            return self.value


class CompositionRepository:
    """Simulated repository for composition data."""

    def is_template_used(self, template_id: str) -> bool:
        """
        Check if the template is used in any compositions.
        This method should check the actual database or data source for template usage.
        """
        # Placeholder logic for checking if the template is used in compositions
        return False


class TemplateStoreRepository:
    """Simulated repository for template storage."""

    def find_all(self) -> List[TemplateMetaData]:
        """Retrieve a list of all operational templates."""
        # Placeholder logic to return all operational templates
        return []

    def store(self, template: OPERATIONALTEMPLATE):
        """Store a new operational template."""
        # Placeholder logic for storing a template
        pass

    def update(self, template: OPERATIONALTEMPLATE):
        """Update an existing operational template."""
        # Placeholder logic for updating a template
        pass

    def find_by_template_id(self, template_id: str) -> Optional[OPERATIONALTEMPLATE]:
        """Find an operational template by its ID."""
        # Placeholder logic for finding a template by ID
        return None

    def delete(self, template_id: str):
        """Delete an operational template by its ID."""
        # Placeholder logic for deleting a template by ID
        pass

    def find_template_id_by_uuid(self, uuid_value: uuid.UUID) -> Optional[str]:
        """Find a template ID by its UUID."""
        # Placeholder logic for finding a template ID by UUID
        return None

    def find_uuid_by_template_id(self, template_id: str) -> Optional[uuid.UUID]:
        """Find a UUID by its template ID."""
        # Placeholder logic for finding a UUID by template ID
        return None


class TemplateStorage:
    """Interface for template storage services."""

    def list_all_operational_templates(self) -> List[TemplateMetaData]:
        raise NotImplementedError

    def store_template(self, template: OPERATIONALTEMPLATE):
        raise NotImplementedError

    def read_operational_template(self, template_id: str) -> Optional[OPERATIONALTEMPLATE]:
        raise NotImplementedError

    def delete_template(self, template_id: str) -> bool:
        raise NotImplementedError

    def find_template_id_by_uuid(self, uuid_value: uuid.UUID) -> Optional[str]:
        raise NotImplementedError

    def find_uuid_by_template_id(self, template_id: str) -> Optional[uuid.UUID]:
        raise NotImplementedError


class TemplateDBStorageService(TemplateStorage):
    """
    Python equivalent of the TemplateDBStorageService class in Java.
    Implements the TemplateStorage interface for managing operational templates in the database.
    """

    def __init__(self, composition_repository: CompositionRepository, template_store_repository: TemplateStoreRepository):
        self.composition_repository = composition_repository
        self.template_store_repository = template_store_repository

    def list_all_operational_templates(self) -> List[TemplateMetaData]:
        """
        Lists all operational templates.
        """
        return self.template_store_repository.find_all()

    def store_template(self, template: OPERATIONALTEMPLATE):
        """
        Stores a new operational template or updates an existing one.
        """
        template_id = template.template_id.get_value()

        # Check if the template already exists
        if not self.read_operational_template(template_id):
            self.template_store_repository.store(template)
        else:
            self.check_usage(template_id, "update")
            self.template_store_repository.update(template)

    def read_operational_template(self, template_id: str) -> Optional[OPERATIONALTEMPLATE]:
        """
        Reads an operational template by its template ID.
        """
        return self.template_store_repository.find_by_template_id(template_id)

    def check_usage(self, template_id: str, operation: str):
        """
        Checks if a template is being used in compositions and raises an exception if it is.
        """
        if self.composition_repository.is_template_used(template_id):
            raise UnprocessableEntityException(
                f"Cannot {operation} template {template_id} since it is used by at least one composition."
            )

    def delete_template(self, template_id: str) -> bool:
        """
        Deletes an operational template by its ID, checking that it is not in use.
        """
        # Check if the template is in use before deleting
        self.check_usage(template_id, "delete")

        self.template_store_repository.delete(template_id)
        return True

    def find_template_id_by_uuid(self, uuid_value: uuid.UUID) -> Optional[str]:
        """
        Finds a template ID by its UUID.
        """
        return self.template_store_repository.find_template_id_by_uuid(uuid_value)

    def find_uuid_by_template_id(self, template_id: str) -> Optional[uuid.UUID]:
        """
        Finds a UUID by its template ID.
        """
        return self.template_store_repository.find_uuid_by_template_id(template_id)


# Example usage of the TemplateDBStorageService class
if __name__ == "__main__":
    composition_repo = CompositionRepository()
    template_repo = TemplateStoreRepository()

    template_service = TemplateDBStorageService(composition_repo, template_repo)

    # Example to store a template
    example_template = OPERATIONALTEMPLATE("example_template_id")
    template_service.store_template(example_template)

    # Example to list all templates
    templates = template_service.list_all_operational_templates()
    print(f"Stored templates: {templates}")
