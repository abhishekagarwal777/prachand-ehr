import pytest
from your_module import PathCohesionAnalysis, AqlQuery, TreeUtils

def assert_tree_matches(root, expected):
    rendered_tree = TreeUtils.render_tree(root)
    assert rendered_tree == expected

def analyze_path_cohesion(aql_str):
    return PathCohesionAnalysis.analyze_path_cohesion(AqlQuery.parse(aql_str))

def by_identifier(map):
    return {e.get_key().get_identifier(): e.get_value() for e in map.items()}

def test_simple_path():
    map = by_identifier(analyze_path_cohesion("SELECT c/uid/value FROM COMPOSITION c"))
    assert "c" in map

    n = map["c"]

    assert_tree_matches(n, """
    COMPOSITION
      uid
        value""")

def test_multi_contains():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT c/uid/value, ev/name/value
        FROM EHR e contains COMPOSITION c CONTAINS ( (OBSERVATION o CONTAINS CLUSTER cl) OR EVALUATION ev )
        WHERE cl/name/value = 'Values'
        ORDER BY ev/name/value
        """))

    assert "c" in map
    assert "ev" in map
    assert "cl" in map

    n = map["c"]
    assert_tree_matches(n, """
    COMPOSITION
      uid
        value""")

    n = map["ev"]
    assert_tree_matches(n, """
    EVALUATION
      name
        value""")

    n = map["cl"]
    assert_tree_matches(n, """
    CLUSTER
      name
        value""")

def test_simple_with_predicates():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
        c/content[at0001]/data/events[at0002, 'Irrelevant']/items[name/value='All Items']/items[openEHR-EHR-CLUSTER.myCluster.v1]/items[openEHR-EHR-ELEMENT.myElement.v1, 'Data']/value
        FROM COMPOSITION c"""))

    assert "c" in map

    n = map["c"]
    assert_tree_matches(n, """
    COMPOSITION
      content[at0001]
        data
          events[at0002]
            items[name/value='All Items']
              items[openEHR-EHR-CLUSTER.myCluster.v1]
                items[openEHR-EHR-ELEMENT.myElement.v1, 'Data']
                  value""")

def test_contains_predicate():
    map = by_identifier(analyze_path_cohesion("SELECT c/uid FROM COMPOSITION c[openEHR-EHR-CLUSTER.myComp.v1]"))
    assert "c" in map

    n = map["c"]
    assert_tree_matches(n, """
    COMPOSITION[openEHR-EHR-CLUSTER.myComp.v1]
      uid""")

def test_ignore_root_predicate():
    map = by_identifier(analyze_path_cohesion("SELECT c[openEHR-EHR-CLUSTER.myComp.v1]/uid FROM COMPOSITION c"))
    assert "c" in map

    n = map["c"]
    assert_tree_matches(n, """
    COMPOSITION
      uid""")

def test_not_merging_root_predicate():
    map = by_identifier(analyze_path_cohesion(
        "SELECT c[name/value='My Comp']/uid FROM COMPOSITION c[openEHR-EHR-CLUSTER.myComp.v1]"))
    assert "c" in map

    n = map["c"]
    assert_tree_matches(n, """
    COMPOSITION[openEHR-EHR-CLUSTER.myComp.v1]
      uid""")

def test_simple_attributes():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items[at0004]/name/value AS SystolicName,
          t/items[at0004]/value/magnitude AS SystolicValue
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items[at0004]
        name
          value
        value
          magnitude""")

def test_simple_node_attributes():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items[at0004]/name/value AS SystolicName,
          t/items[at0004]/value/magnitude AS SystolicValue,
          t/items[at0004]/value/units AS SystolicUnit,
          t/items[at0005]/name/value AS DiastolicName,
          t/items[at0005]/value/magnitude AS DiastolicValue
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items[at0004]
        name
          value
        value
          magnitude
          units
      items[at0005]
        name
          value
        value
          magnitude""")

def test_base_attributes():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items/name/value AS Name,
          t/items/value/magnitude AS Value,
          t/items[at0005]/name/value AS DiastolicName,
          t/items[at0005]/value/magnitude AS DiastolicValue,
          t/items[at0005]/value/units AS DiastolicUnit
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items
        name
          value
        value
          magnitude
          units""")

def test_archetype_attributes():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items[openEHR-EHR-ELEMENT.blood_pressure.v2]/name/value AS Name,
          t/items[openEHR-EHR-ELEMENT.blood_pressure.v2, 'Systolic']/value/magnitude AS SystolicValue,
          t/items[at0005, 'Diastolic']/name/value AS DiastolicName,
          t/items[at0005]/value/magnitude AS DiastolicValue,
          t/items[at0005]/value/units AS DiastolicUnit
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items[at0005]
        name
          value
        value
          magnitude
          units
      items[openEHR-EHR-ELEMENT.blood_pressure.v2]
        name
          value
        value
          magnitude""")

def test_name_attributes():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items[name/value='Systolic']/name/value AS Name,
          t/items[name/value='Systolic']/value/magnitude AS SystolicValue,
          t/items[name/value='Diastolic']/name/value AS DiastolicName,
          t/items[name/value='Diastolic']/value/magnitude AS DiastolicValue,
          t/items[name/value='Diastolic']/value/units AS DiastolicUnit
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items[name/value='Diastolic']
        name
          value
        value
          magnitude
          units
      items[name/value='Systolic']
        name
          value
        value
          magnitude""")

def test_mixed_attributes():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items[openEHR-EHR-ELEMENT.blood_pressure.v2]/name/value AS Name,
          t/items[openEHR-EHR-ELEMENT.blood_pressure.v2, 'Systolic']/value/magnitude AS SystolicValue,
          t/items[name/value='Diastolic']/name/value AS DiastolicName,
          t/items[at0005]/value/magnitude AS DiastolicValue,
          t/items[at0005]/value/units AS DiastolicUnit
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items
        name
          value
        value
          magnitude
          units""")

def test_irrelevant_predicates():
    map = by_identifier(analyze_path_cohesion(
        """
        SELECT
          t/items[archetype_node_id=at0004 and value/magnitude > 3 and name/value='Systolic']/name/value AS SystolicName,
          t/items[at0004]/value/magnitude AS SystolicValue
        FROM OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
        CONTAINS ITEM_TREE t"""))

    n = map["t"]
    assert_tree_matches(n, """
    ITEM_TREE
      items[at0004]
        name
          value
        value
          magnitude""")
