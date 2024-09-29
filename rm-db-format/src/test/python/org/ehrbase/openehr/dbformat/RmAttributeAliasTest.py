import pytest

class RmAttributeAlias:
    # Placeholder for RmAttributeAlias to simulate Java functionality
    VALUES = [
        # Example attributes; this should be replaced with actual values
        'attribute1', 'attribute2', 'attribute3'
    ]
    
    @staticmethod
    def attribute():
        # Simulate fetching attribute names
        return RmAttributeAlias.VALUES

    @staticmethod
    def get_attribute(name):
        # Simulate checking if the attribute exists and return accordingly
        if name in RmAttributeAlias.VALUES:
            raise ValueError(f"Alias name clashes with an existing attribute {name}")
        return name  # Return the attribute if no clash

    @staticmethod
    def rm_to_json_path_parts(path):
        # Mapping of RM paths to JSON path parts
        mapping = {
            "archetype_details/template_id/value": ["ad", "tm", "V"],
            "subject/external_ref/id/value": ["su", "er", "X", "V"],
        }
        return mapping.get(path, [])

class TestRmAttributeAlias:

    def test_check_aliases(self):
        attributes = {RmAttributeAlias.attribute() for _ in RmAttributeAlias.VALUES}

        for a in attributes:
            with pytest.raises(ValueError, match=f"Alias name clashes with an existing attribute {a}"):
                RmAttributeAlias.get_attribute(a)

    def test_rm_to_json_path_parts(self):
        assert RmAttributeAlias.rm_to_json_path_parts("archetype_details/template_id/value") == ["ad", "tm", "V"]
        assert RmAttributeAlias.rm_to_json_path_parts("subject/external_ref/id/value") == ["su", "er", "X", "V"]

# To run the tests, execute the following command in the terminal:
# pytest -q --tb=short <name_of_this_file>.py
