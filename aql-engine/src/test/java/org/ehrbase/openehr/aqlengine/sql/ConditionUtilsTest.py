import pytest
import json

# Assuming ConditionUtils is defined in your_module and contains escape_as_json_string
from your_module import ConditionUtils

def test_escape_as_json_string():
    assert ConditionUtils.escape_as_json_string(None) is None
    assert ConditionUtils.escape_as_json_string(" Test ") == "\" Test \""
    assert ConditionUtils.escape_as_json_string("") == "\"\""
    assert ConditionUtils.escape_as_json_string("\"Test\"") == "\"\\\"Test\\\"\""
    assert ConditionUtils.escape_as_json_string("C:\\temp\\") == "\"C:\\\\temp\\\\\""
    assert ConditionUtils.escape_as_json_string("Cluck Ol' Hen") == "\"Cluck Ol' Hen\""
