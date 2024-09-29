import pytest
from your_module import FoundationType, PathAnalysis, RMTypeInfo, RmConstants
from collections import deque

@pytest.mark.parametrize("name", ["STRING", "LONG", "TEMPORAL"])
def test_has_foundation_type(name):
    # Check that the FoundationType contains the expected values
    assert FoundationType[name] is not None

def test_foundation_types_complete():
    # Ensure that FoundationType contains all types needed for Compositions
    remaining_types = deque([PathAnalysis.RM_INFOS.get_type_info(RmConstants.COMPOSITION)])
    seen = {remaining_types[0]}  # Add the first type info
    type_names = set()

    while remaining_types:
        type_info = remaining_types.popleft()
        # Traverse direct descendant classes
        for descendant in type_info.get_direct_descendant_classes():
            if descendant not in seen:
                seen.add(descendant)
                remaining_types.append(descendant)

        # If the current class is not abstract
        if not is_abstract(type_info.get_java_class()):
            for attribute in type_info.get_attributes().values():
                if not attribute.is_computed():
                    type_name = attribute.get_type_name_in_collection()
                    type_info_attr = PathAnalysis.RM_INFOS.get_type_info(type_name)
                    if type_info_attr is None:
                        type_names.add(type_name)

                    if type_info_attr and type_info_attr not in seen:
                        seen.add(type_info_attr)
                        remaining_types.append(type_info_attr)

    # Assert that all FoundationType values are as expected
    foundation_type_names = {ft.name for ft in FoundationType}
    assert foundation_type_names == type_names

def is_abstract(java_class):
    """Helper function to check if the Java class is abstract."""
    # Simulate the Java Modifier.isAbstract() function
    return hasattr(java_class, '__abstractmethods__')
