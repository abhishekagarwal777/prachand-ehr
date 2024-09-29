import json
from typing import Any, Dict

class ApiExample:
    """
    API Example objects.
    """

    # Private constructor equivalent in Python
    def __init__(self):
        raise NotImplementedError("This class cannot be instantiated.")

    @staticmethod
    def get_ehr_status_json() -> str:
        """
        Returns a JSON string representing the EHR status example.
        """
        return json.dumps(ApiExample.EHR_STATUS_JSON)

    EHR_STATUS_JSON: str = """
    {
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {
            "value": "EHR status"
        },
        "uid": {
            "_type": "OBJECT_VERSION_ID",
            "value": "9e3eb79b-1caa-4ab9-8cd4-d374b7c42bb4::local.ehrbase.org::1"
        },
        "subject": {
            "_type": "PARTY_SELF"
        },
        "is_queryable": true,
        "is_modifiable": true
    }
    """
