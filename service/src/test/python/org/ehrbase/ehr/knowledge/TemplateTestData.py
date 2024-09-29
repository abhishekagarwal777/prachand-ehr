import os
from enum import Enum

class TemplateTestData(Enum):
    """Enumeration for template test data files."""

    CLINICAL_CONTENT_VALIDATION = "clinical_content_validation.opt"
    IMMUNISATION_SUMMARY = "IDCR - Immunisation summary.v0.opt"
    NON_UNIQUE_AQL_PATH = "non_unique_aql_paths.opt"
    ANAMNESE = "Anamnese.opt"

    def get_stream(self):
        """Returns a stream of the template test data file."""
        # Get the path to the resource relative to the module
        resource_path = os.path.join("knowledge", self.value)
        
        # Open the file and return the file object
        try:
            return open(resource_path, 'rb')  # Open in binary mode
        except FileNotFoundError:
            raise Exception(f"File {resource_path} not found.")

# Example usage
if __name__ == "__main__":
    for template in TemplateTestData:
        try:
            with template.get_stream() as stream:
                data = stream.read()
                print(f"Loaded {template.name}: {data[:100]}")  # Print first 100 bytes of the content
        except Exception as e:
            print(e)
