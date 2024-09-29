import pytest
from enum import Enum

class StructureRmType(Enum):
    # Placeholder for StructureRmType enum; replace with actual enum values
    TYPE_1 = "TYPE_1"
    TYPE_2 = "TYPE_2"
    TYPE_3 = "TYPE_3"

    def get_alias(self):
        # Placeholder for getting alias; implement according to your logic
        return f"alias_for_{self.name}"

class RmTypeAlias:
    # Placeholder for RmTypeAlias class; populate with actual type values and logic
    values = [
        StructureRmType.TYPE_1,
        StructureRmType.TYPE_2,
        StructureRmType.TYPE_3
    ]

    @staticmethod
    def get_alias(name):
        for type_enum in StructureRmType:
            if type_enum.name == name:
                return type_enum.get_alias()
        raise ValueError(f"No alias found for type: {name}")

    @staticmethod
    def get_rm_type(name):
        for type_enum in StructureRmType:
            if type_enum.get_alias() == name:
                return type_enum
        raise ValueError(f"Alias name clashes with an existing type: {name}")

    @staticmethod
    def types_with_aliases():
        return {type_enum.get_alias() for type_enum in StructureRmType}

class TestRmTypeAlias:

    def test_check_structure_aliases(self):
        for v in StructureRmType:
            assert RmTypeAlias.get_alias(v.name) == v.get_alias()

        types_with_aliases = RmTypeAlias.types_with_aliases()

        for t in types_with_aliases:
            with pytest.raises(ValueError, match=f"Alias name clashes with an existing type: {t}"):
                RmTypeAlias.get_rm_type(t)

# To run the tests, execute the following command in the terminal:
# pytest -q --tb=short <name_of_this_file>.py
