import pytest
from your_module import PathAnalysis, AqlObjectPath, RmConstants, FoundationType, LongPrimitive, StringPrimitive
from your_module.path_analysis import AndOperatorPredicate, ComparisonOperatorPredicate
from your_module.rm_attribute_alias import RmAttributeAlias

def test_composition_types():
    assert PathAnalysis.AttributeInfos.rm_types, "rm_types should not be empty"
    print(PathAnalysis.AttributeInfos.rm_types)

def test_base_types_by_attribute():
    cut = PathAnalysis.AttributeInfos.base_types_by_attribute

    assert cut, "base_types_by_attribute should not be empty"
    assert "other_participations" in cut

    assert cut["other_participations"] == {
        "CARE_ENTRY", "ADMIN_ENTRY", "INSTRUCTION", "OBSERVATION", "ENTRY", "ACTION", "EVALUATION"
    }

def test_analyze_aql_path_invalid():
    with pytest.raises(ValueError, match="non"):
        PathAnalysis.analyze_aql_path_types(
            RmConstants.COMPOSITION,
            None,
            None,
            AqlObjectPath.parse("path/links/non/existent/attributes"),
            None
        )

def test_analyze_aql_path():
    # simple composition
    node = PathAnalysis.analyze_aql_path_types(RmConstants.COMPOSITION, None, None, None, None)
    assert node.candidate_types == {RmConstants.COMPOSITION}
    assert not node.attributes

    # CARE_ENTRY with archetype node id condition
    node = PathAnalysis.analyze_aql_path_types(
        "CARE_ENTRY",
        archetype_node_id_condition("openEHR-EHR-OBSERVATION.my-observation.v3"),
        None,
        None,
        None
    )
    assert node.candidate_types == {RmConstants.OBSERVATION}
    assert "archetype_node_id" in node.attributes

    # CARE_ENTRY with state
    node = PathAnalysis.analyze_aql_path_types("CARE_ENTRY", None, None, AqlObjectPath.parse("state"), None)
    assert node.candidate_types == {RmConstants.OBSERVATION}
    assert "state" in node.attributes

    # CARE_ENTRY with data
    node = PathAnalysis.analyze_aql_path_types("CARE_ENTRY", None, None, AqlObjectPath.parse("data"), None)
    assert node.candidate_types == {RmConstants.OBSERVATION, RmConstants.EVALUATION}
    assert "data" in node.attributes

    # CARE_ENTRY with data and events
    node = PathAnalysis.analyze_aql_path_types(
        "CARE_ENTRY", None, None, AqlObjectPath.parse("data/events/state"), None
    )
    assert node.candidate_types == {RmConstants.OBSERVATION}
    assert "data" in node.attributes

    # ITEM_STRUCTURE with item and value
    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE", None, None, AqlObjectPath.parse("item/value"), None
    )
    assert node.candidate_types == {RmConstants.ITEM_SINGLE}
    assert "item" in node.attributes

    item = node.attributes["item"]
    assert item.candidate_types == {RmConstants.ELEMENT}
    assert "value" in item.attributes
    element_value = item.attributes["value"]
    assert all(v.startswith("DV_") for v in element_value.candidate_types)

    # ITEM_SINGLE with DvCodedText value
    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE",
        None,
        None,
        AqlObjectPath.parse("item/value[defining_code/terminology_id/value='openehr']/value"),
        None
    )
    assert node.candidate_types == {RmConstants.ITEM_SINGLE}
    assert "item" in node.attributes

    item = node.attributes["item"]
    assert item.candidate_types == {RmConstants.ELEMENT}
    assert "value" in item.attributes
    element_value = item.attributes["value"]
    assert all(v.startswith("DV_") for v in element_value.candidate_types)
    assert "value" in element_value.attributes
    value_value = element_value.attributes["value"]
    assert value_value.candidate_types == {FoundationType.STRING.name()}

    # ITEM_SINGLE with type constrained via predicate value
    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE", None, None, AqlObjectPath.parse("item/value[value=10.0]/value"), None
    )
    assert node.candidate_types == {RmConstants.ITEM_SINGLE}
    assert "item" in node.attributes

    item = node.attributes["item"]
    assert item.candidate_types == {RmConstants.ELEMENT}
    assert "value" in item.attributes
    element_value = item.attributes["value"]
    assert element_value.candidate_types == {RmConstants.DV_SCALE, RmConstants.DV_ORDINAL}

    # ITEM_SINGLE with type constrained via value
    candidate_types = PathAnalysis.get_candidate_types(LongPrimitive(10))
    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE", None, None, AqlObjectPath.parse("item/value/value"), candidate_types
    )
    assert node.candidate_types == {RmConstants.ITEM_SINGLE}
    assert "item" in node.attributes

    item = node.attributes["item"]
    assert item.candidate_types == {RmConstants.ELEMENT}
    assert "value" in item.attributes
    element_value = item.attributes["value"]
    assert element_value.candidate_types == {RmConstants.DV_SCALE, RmConstants.DV_ORDINAL}

def archetype_node_id_condition(archetype_node_id):
    if archetype_node_id is None:
        return None
    return [
        AndOperatorPredicate([
            ComparisonOperatorPredicate(
                AqlObjectPathUtil.ARCHETYPE_NODE_ID,
                ComparisonOperatorPredicate.PredicateComparisonOperator.EQ,
                StringPrimitive(archetype_node_id)
            )
        ])
    ]

def test_create_attribute_infos():
    # Test creation of attribute infos with specific conditions
    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE",
        None,
        None,
        AqlObjectPath.parse("item/value/value"),
        PathAnalysis.get_candidate_types(LongPrimitive(10))
    )
    attribute_infos = PathAnalysis.create_attribute_infos(node)
    assert len(attribute_infos) == 3
    assert all(len(info) == 1 for info in attribute_infos.values())

    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE",
        None,
        None,
        AqlObjectPath.parse("item[value/value>3]/value[value < 100]/value"),
        PathAnalysis.get_candidate_types(LongPrimitive(10))
    )
    attribute_infos = PathAnalysis.create_attribute_infos(node)
    assert len(attribute_infos) == 3
    assert all(len(info) == 1 for info in attribute_infos.values())

    node = PathAnalysis.analyze_aql_path_types(
        "ITEM_STRUCTURE",
        None,
        None,
        AqlObjectPath.parse("item[name/value='My Item']/value[value < 100]/value"),
        PathAnalysis.get_candidate_types(LongPrimitive(10))
    )
    attribute_infos = PathAnalysis.create_attribute_infos(node)
    assert len(attribute_infos) == 4
    assert len([item for sublist in attribute_infos.values() for item in sublist.values()]) == 5

def test_rm_attribute_alias():
    rm_attributes = [
        alias.attribute for alias in RmAttributeAlias.VALUES
        if alias.attribute not in {"_magnitude", "details", "folders", "_type", "_index"}
    ]
    rm_attributes.extend(["timeCreated", "ehrId", "ehrStatus", "compositions"])

    attribute_infos_keys = PathAnalysis.AttributeInfos.attribute_infos.keys()
    assert all(attr in attribute_infos_keys for attr in rm_attributes)
    assert all(attr in rm_attributes for attr in attribute_infos_keys)
