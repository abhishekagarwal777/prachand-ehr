# test_folder_utils.py

import io
import pytest
from json import loads
from ehrbase_sdk.serialisation.jsonencoding import CanonicalJson
from ehrbase_sdk.test_data.folder import FolderTestDataCanonicalJson
from ehrbase_sdk.utils.folder_utils import FolderUtils

# Test class to replace the original FolderUtilsTest
class TestFolderUtils:

    canonical_json = CanonicalJson()

    def test_detects_duplicate_folder_names(self):
        # Simulate reading the JSON data from the stream
        value = io.StringIO(FolderTestDataCanonicalJson.FOLDER_WITH_DUPLICATE_NAMES.get_stream().decode('utf-8')).read()
        
        # Unmarshal the JSON data into a Folder object
        test_folder = self.canonical_json.unmarshal(value, Folder)

        # Assert that the IllegalArgumentException is raised by check_sibling_name_conflicts
        with pytest.raises(IllegalArgumentException):
            FolderUtils.check_sibling_name_conflicts(test_folder)

    def test_accepts_folders_without_conflicts(self):
        # Simulate reading the JSON data from the stream
        value = io.StringIO(FolderTestDataCanonicalJson.FOLDER_WITHOUT_DUPLICATE_NAMES.get_stream().decode('utf-8')).read()

        # Unmarshal the JSON data into a Folder object
        test_folder = self.canonical_json.unmarshal(value, Folder)

        # Assert that no exception is raised when checking for sibling name conflicts
        FolderUtils.check_sibling_name_conflicts(test_folder)

# The CanonicalJson and Folder classes would need to be implemented in the ehrbase_sdk.
# FolderTestDataCanonicalJson and FolderUtils should also have the same functional behavior as the Java equivalents.




def some_function(param):
    if not isinstance(param, expected_type):
        raise ValueError("Invalid argument: expected a specific type.")

def process_data(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid argument: 'data' must be a dictionary.")

    # Process the data...
    return data


# Example usage
try:
    process_data("not a dictionary")  # This will raise an exception
except ValueError as e:
    print(e)  # Output: Invalid argument: 'data' must be a dictionary.
