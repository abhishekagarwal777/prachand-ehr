import pytest
from your_module import PathAnalysis, AqlObjectPath, ANode

class TestANode:

    def test_node_categories(self):
        # POINT_EVENT with ITEM_SINGLE data with ELEMENT item
        # with DV_SCALE or DV_ORDINAL value (as its value is a number)
        root_node = PathAnalysis.analyze_aql_path_types(
            "POINT_EVENT", None, None, AqlObjectPath.parse("data/item/value[value>=0]/value"), None
        )

        node = root_node
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("data")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("item")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("value")
        assert node.get_categories() == [ANode.NodeCategory.RM_TYPE]
        node = node.attributes.get("value")
        assert node.get_categories() == [ANode.NodeCategory.FOUNDATION]

        # POINT_EVENT with ITEM_STRUCTURE data with ELEMENT or CLUSTER items
        root_node = PathAnalysis.analyze_aql_path_types(
            "POINT_EVENT", None, None, AqlObjectPath.parse("data/items/name[value!='foo']/value"), None
        )

        node = root_node
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("data")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("items")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("name")
        assert node.get_categories() == [ANode.NodeCategory.RM_TYPE]
        node = node.attributes.get("value")
        assert node.get_categories() == [ANode.NodeCategory.FOUNDATION]

        # POINT_EVENT with ITEM_STRUCTURE data with CLUSTER with ELEMENT
        root_node = PathAnalysis.analyze_aql_path_types(
            "POINT_EVENT", None, None, AqlObjectPath.parse("data/items/items/name[value!='foo']/value"), None
        )

        node = root_node
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("data")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("items")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("items")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]

        # ACTION with INSTRUCTION_DETAILS instruction_details with ITEM_STRUCTURE wf_details
        root_node = PathAnalysis.analyze_aql_path_types(
            "CARE_ENTRY", None, None, AqlObjectPath.parse("instruction_details/wf_details"), None
        )

        node = root_node
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("instruction_details")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE_INTERMEDIATE]
        node = node.attributes.get("wf_details")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]

        # Duplicate test with the same path
        root_node = PathAnalysis.analyze_aql_path_types(
            "CARE_ENTRY", None, None, AqlObjectPath.parse("instruction_details/wf_details"), None
        )

        node = root_node
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]
        node = node.attributes.get("instruction_details")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE_INTERMEDIATE]
        node = node.attributes.get("wf_details")
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]


@pytest.fixture
def setup_node():
    return PathAnalysis.analyze_aql_path_types(
        "POINT_EVENT", None, None, AqlObjectPath.parse("data/item/value[value>=0]/value"), None
    )

class TestANode:

    def test_node_categories(self, setup_node):
        node = setup_node
        assert node.get_categories() == [ANode.NodeCategory.STRUCTURE]