import pytest
import re

class AqlParameterReplacement:
    # Placeholder for actual method implementation
    @staticmethod
    def replace_parameters(query, parameters):
        # Simulate replacement logic; actual implementation needed
        for key, value in parameters.items():
            query = re.sub(r'\$' + re.escape(key), str(value), query)
        return query

    # Simulate temporal pattern matching
    TemporalPrimitivePattern = re.compile(r"some_regex_pattern")

def test_temporal_pattern_confirm():
    valid_examples = [
        "2020-12-31", "20201231", "23:59:59", "235959", "23:59:59.9",
        "23:59:59.98", "23:59:59.987", "23:59:59.9876", "23:59:59.98765",
        "23:59:59.987654", "23:59:59.9876543", "23:59:59.98765432",
        "23:59:59.987654321", "235959.987", "23:59:59Z", "235959Z",
        "23:59:59.987Z", "235959.987Z", "23:59:59+12", "235959-12:59",
        "23:59:59.987+12", "235959.987-12:59", "235959.987+1259",
        "235959.987-1259", "2020-12-31T23:59:59", "2020-12-31T23:59:59.9",
        "2020-12-31T23:59:59.98", "2020-12-31T23:59:59.987",
        "2020-12-31T23:59:59.9876", "2020-12-31T23:59:59.98765",
        "2020-12-31T23:59:59.987654", "2020-12-31T23:59:59.9876543",
        "2020-12-31T23:59:59.98765432", "2020-12-31T23:59:59.987654321",
        "2020-12-31T23:59:59Z", "2020-12-31T23:59:59-0200",
        "2020-12-31T23:59:59.013-0200"
    ]
    for example in valid_examples:
        assert AqlParameterReplacement.TemporalPrimitivePattern.match(example) is not None

def test_temporal_pattern_reject():
    invalid_examples = [
        "", "T", "2020-1231", "2020", "2020:12:31", "23-59-59", "23-59",
        "236060", "23:60:59.987", "23:59:59.", "23:59:59.1234567890",
        "23:59:59.987z", "23:59:59+120", "23:59:59.987+2", "23:59:59.987+123",
        "23:59:59.987+12345", "23:59:59.987Z+1234", "2020-12-31T23:59:59.",
        "2020-12-31T23:59:59.9876543210", "2020-12-31t23:59:59.013-0200",
        "2020-12-31T235959", "20201231T23:59:59", "23:59:59T2020-12-31"
    ]
    for example in invalid_examples:
        assert AqlParameterReplacement.TemporalPrimitivePattern.match(example) is None

def test_replace_where_parameters():
    # Simple string replacement
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE d/foo = $bar",
        {"bar": "baz"},
        "SELECT d FROM DUMMY d WHERE d/foo = 'baz'"
    )

    # Data types
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE (d/int = $int AND d/bool = $bool AND d/double = $double AND d/str = $str AND d/date = $date)",
        {"int": 42, "bool": True, "double": 1.0, "str": "foo", "date": "2012-12-31"},
        "SELECT d FROM DUMMY d WHERE (d/int = 42 AND d/bool = true AND d/double = 1.0 AND d/str = 'foo' AND d/date = '2012-12-31')"
    )

    # IdentifiedPath: archetype_node_id
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE d[$ani]/foo[$ani2] = 42",
        {"ani": "at0001", "ani2": "at0002"},
        "SELECT d FROM DUMMY d WHERE d[at0001]/foo[at0002] = 42"
    )

    # IdentifiedPath: nodeConstraint + name
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE d[at0001,$nameConstraint]/foo[at0002,$nameConstraint2] = 42",
        {"nameConstraint": "Results", "nameConstraint2": "Results2"},
        "SELECT d FROM DUMMY d WHERE d[at0001, 'Results']/foo[at0002, 'Results2'] = 42"
    )

    # IdentifiedPath: nodeConstraint + local terminology => interpreted as String
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE d[at0001,$nameConstraint]/foo[at0002,$nameConstraint2] = 42",
        {"nameConstraint": "at0002", "nameConstraint2": "at0003"},
        "SELECT d FROM DUMMY d WHERE d[at0001, 'at0002']/foo[at0002, 'at0003'] = 42"
    )

    # IdentifiedPath: nodeConstraint + TERM_CODE => interpreted as String
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE d[at0001,$nameConstraint]/foo[at0002,$nameConstraint2] = 42",
        {"nameConstraint": "ISO_639-1::en", "nameConstraint2": "ISO_639-1::de"},
        "SELECT d FROM DUMMY d WHERE d[at0001, 'ISO_639-1::en']/foo[at0002, 'ISO_639-1::de'] = 42"
    )

    # IdentifiedPath: standard predicates
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE d[foo=$foo AND bar=$bar]/foo[foo=$foo2 AND bar=$bar2] = 42",
        {"foo": "FOO", "bar": 13, "foo2": "FOO2", "bar2": 31},
        "SELECT d FROM DUMMY d WHERE d[foo='FOO' AND bar=13]/foo[foo='FOO2' AND bar=31] = 42"
    )

    # ignored + duplicate usage
    assert_replace_parameters(
        "SELECT d FROM DUMMY d WHERE (d/f1 = $bar AND d/f2 = $bar AND d/f3 = $baz)",
        {"foo": "bob", "bar": "alice", "baz": "charly"},
        "SELECT d FROM DUMMY d WHERE (d/f1 = 'alice' AND d/f2 = 'alice' AND d/f3 = 'charly')"
    )

    # missing
    with pytest.raises(ValueError, match="Missing parameter.*baz"):
        assert_replace_parameters(
            "SELECT d FROM DUMMY d WHERE (d/f1 = $bar AND d/f2 = $bar AND d/f3 = $baz)",
            {"foo": "bob", "bar": "alice"}
        )

def test_replace_from_parameters():
    # archetype_node_id
    assert_replace_parameters(
        "SELECT d FROM DUMMY d[$ani]", {"ani": "at0001"}, "SELECT d FROM DUMMY d[at0001]"
    )
    with pytest.raises(ValueError):
        assert_replace_parameters(
            "SELECT d FROM DUMMY d[$ani]", {"ani": "invalid-id"}
        )

    # nodeConstraint + name
    assert_replace_parameters(
        "SELECT d FROM DUMMY d[at0001,$nameConstraint]",
        {"nameConstraint": "Results"},
        "SELECT d FROM DUMMY d[at0001, 'Results']"
    )

    # nodeConstraint + local terminology => interpreted as String
    assert_replace_parameters(
        "SELECT d FROM DUMMY d[at0001,$nameConstraint]",
        {"nameConstraint": "at0002"},
        "SELECT d FROM DUMMY d[at0001, 'at0002']"
    )

    # nodeConstraint + TERM_CODE => interpreted as String
    assert_replace_parameters(
        "SELECT d FROM DUMMY d[at0001,$nameConstraint]",
        {"nameConstraint": "ISO_639-1::en"},
        "SELECT d FROM DUMMY d[at0001, 'ISO_639-1::en']"
    )

    # standard predicates
    assert_replace_parameters(
