import json
import unittest
from assertpy import assert_that


class CompositionCleanupTest(unittest.TestCase):

    COMP = json.dumps({
        "_type": "COMPOSITION",
        "name": {
            "_type": "DV_TEXT",
            "value": "aql-conformance-ehrbase.org.v0"
        },
        "archetype_details": {
            "archetype_id": {
                "value": "openEHR-EHR-COMPOSITION.conformance_composition_.v0"
            },
            "template_id": {
                "value": "aql-conformance-ehrbase.org.v0"
            },
            "rm_version": "1.0.4"
        },
        "language": {
            "_type": "CODE_PHRASE",
            "terminology_id": {
                "_type": "TERMINOLOGY_ID",
                "value": "ISO_639-1"
            },
            "code_string": "en"
        },
        "territory": {
            "_type": "CODE_PHRASE",
            "terminology_id": {
                "_type": "TERMINOLOGY_ID",
                "value": "ISO_3166-1"
            },
            "code_string": "DE"
        },
        "category": {
            "_type": "DV_CODED_TEXT",
            "value": "event",
            "defining_code": {
                "_type": "CODE_PHRASE",
                "terminology_id": {
                    "_type": "TERMINOLOGY_ID",
                    "value": "openehr"
                },
                "code_string": "433"
            }
        },
        "composer": {
            "_type": "PARTY_IDENTIFIED",
            "name": "Max Mustermann"
        },
        "context": {
            "_type": "EVENT_CONTEXT",
            "start_time": {
                "_type": "DV_DATE_TIME",
                "value": "2022-02-03T04:05:06"
            },
            "end_time": {
                "_type": "DV_DATE_TIME",
                "value": "2022-02-03T04:05:06"
            },
            "setting": {
                "_type": "DV_CODED_TEXT",
                "value": "home",
                "defining_code": {
                    "_type": "CODE_PHRASE",
                    "terminology_id": {
                        "_type": "TERMINOLOGY_ID",
                        "value": "openehr"
                    },
                    "code_string": "225"
                }
            },
            "health_care_facility": {
                "_type": "PARTY_IDENTIFIED",
                "name": "DOE, John"
            }
        },
        "content": [
            {
                "_type": "SECTION",
                "name": {
                    "_type": "DV_TEXT",
                    "value": "conformance section"
                },
                "archetype_details": {
                    "archetype_id": {
                        "value": "openEHR-EHR-SECTION.conformance_section.v0"
                    },
                    "rm_version": "1.0.4"
                },
                "items": [
                    {
                        "_type": "OBSERVATION",
                        "name": {
                            "_type": "DV_TEXT",
                            "value": "Conformance Observation"
                        },
                        "archetype_details": {
                            "archetype_id": {
                                "value": "openEHR-EHR-OBSERVATION.conformance_observation.v0"
                            },
                            "rm_version": "1.0.4"
                        },
                        "language": {
                            "_type": "CODE_PHRASE",
                            "terminology_id": {
                                "_type": "TERMINOLOGY_ID",
                                "value": "ISO_639-1"
                            },
                            "code_string": "en"
                        },
                        "encoding": {
                            "_type": "CODE_PHRASE",
                            "terminology_id": {
                                "_type": "TERMINOLOGY_ID",
                                "value": "IANA_character-sets"
                            },
                            "code_string": "UTF-8"
                        },
                        "subject": {
                            "_type": "PARTY_SELF"
                        },
                        "data": {
                            "name": {
                                "_type": "DV_TEXT",
                                "value": "History"
                            },
                            "origin": {
                                "_type": "DV_DATE_TIME",
                                "value": "2022-02-03T04:05:06"
                            },
                            "events": [
                                {
                                    "_type": "INTERVAL_EVENT",
                                    "name": {
                                        "_type": "DV_TEXT",
                                        "value": "Any event"
                                    },
                                    "time": {
                                        "_type": "DV_DATE_TIME",
                                        "value": "2022-02-03T04:05:06"
                                    },
                                    "data": {
                                        "_type": "ITEM_TREE",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Tree"
                                        },
                                        "items": [
                                            {
                                                "_type": "ELEMENT",
                                                "name": {
                                                    "_type": "DV_TEXT",
                                                    "value": "DV_TEXT"
                                                },
                                                "value": {
                                                    "_type": "DV_TEXT",
                                                    "value": "Lorem ipsum"
                                                },
                                                "archetype_node_id": "at0004"
                                            },
                                            {
                                                "_type": "CLUSTER",
                                                "name": {
                                                    "_type": "DV_TEXT",
                                                    "value": "conformance cluster"
                                                },
                                                "archetype_details": {
                                                    "archetype_id": {
                                                        "value": "openEHR-EHR-CLUSTER.conformance_cluster.v0"
                                                    },
                                                    "rm_version": "1.0.4"
                                                },
                                                "items": [
                                                    {
                                                        "_type": "ELEMENT",
                                                        "name": {
                                                            "_type": "DV_TEXT",
                                                            "value": "labresult"
                                                        },
                                                        "value": {
                                                            "_type": "DV_TEXT",
                                                            "value": "Lorem ipsum"
                                                        },
                                                        "archetype_node_id": "at0003"
                                                    },
                                                    {
                                                        "_type": "ELEMENT",
                                                        "name": {
                                                            "_type": "DV_TEXT",
                                                            "value": "comment"
                                                        },
                                                        "value": {
                                                            "_type": "DV_TEXT",
                                                            "value": "Lorem ipsum"
                                                        },
                                                        "archetype_node_id": "at0004"
                                                    },
                                                    {
                                                        "_type": "ELEMENT",
                                                        "name": {
                                                            "_type": "DV_TEXT",
                                                            "value": "ANY"
                                                        },
                                                        "value": {
                                                            "_type": "DV_TEXT",
                                                            "value": "Lorem ipsum"
                                                        },
                                                        "archetype_node_id": "at0005"
                                                    }
                                                ],
                                                "archetype_node_id": "openEHR-EHR-CLUSTER.conformance_cluster.v0"
                                            }
                                        ],
                                        "archetype_node_id": "at0003"
                                    },
                                    "width": {
                                        "_type": "DV_DURATION",
                                        "value": "PT42H"
                                    },
                                    "math_function": {
                                        "_type": "DV_CODED_TEXT",
                                        "value": "minimum",
                                        "defining_code": {
                                            "_type": "CODE_PHRASE",
                                            "terminology_id": {
                                                "_type": "TERMINOLOGY_ID",
                                                "value": "openehr"
                                            },
                                            "code_string": "145"
                                        }
                                    },
                                    "archetype_node_id": "at0002"
                                },
                                {
                                    "_type": "POINT_EVENT",
                                    "name": {
                                        "_type": "DV_TEXT",
                                        "value": "Any event"
                                    },
                                    "time": {
                                        "_type": "DV_DATE_TIME",
                                        "value": "2022-02-03T04:05:06"
                                    },
                                    "data": {
                                        "_type": "ITEM_TREE",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Tree"
                                        },
                                        "items": [
                                            {
                                                "_type": "ELEMENT",
                                                "name": {
                                                    "_type": "DV_TEXT",
                                                    "value": "DV_TEXT"
                                                },
                                                "value": {
                                                    "_type": "DV_TEXT",
                                                    "value": "Lorem ipsum"
                                                },
                                                "archetype_node_id": "at0004"
                                            }
                                        ],
                                        "archetype_node_id": "at0003"
                                    },
                                    "archetype_node_id": "at0002"
                                }
                            ],
                            "archetype_node_id": "at0001"
                        },
                        "archetype_node_id": "openEHR-EHR-OBSERVATION.conformance_observation.v0",
                        "uid": {
                            "_type": "HIER_OBJECT_ID",
                            "value": "893506a7-462b-40b8-9638-0aa3990642d9"
                        }
                    }
                ],
                "archetype_node_id": "openEHR-EHR-SECTION.conformance_section.v0"
            }
        ]
    })


class CompositionCleanup:
    @staticmethod
    def cleanup(comp_json, param1, param2):
        # This is a placeholder for the actual cleanup logic.
        # You should implement the actual logic as needed.
        return json.loads(comp_json)  # Example return, modify as needed.



    @unittest.expectedFailure
    def test_cleanup(self):
        cleaned = CompositionCleanup.cleanup(self.COMP, False, True)
        assert_that(cleaned).contains(
            "\"template_id\" : \"aql-conformance-ehrbase.org.v0\"",
            "\"items\" : [ \"ELEMENT[at0004,'DV_TEXT']\" ]"
        )
        print(cleaned)

        # The expected cleaned output should be defined here
        expected_output = {
            "_type": "COMPOSITION",
            "name": {
                "_type": "DV_TEXT",
                "value": "Conformance composition"
            },
            "archetype_details": {
                "archetype_id": {
                    "value": "openEHR-EHR-COMPOSITION.conformance_composition.v0"
                },
                "rm_version": "1.0.4"
            },
            "language": {
                "_type": "CODE_PHRASE",
                "terminology_id": {
                    "_type": "TERMINOLOGY_ID",
                    "value": "ISO_639-1"
                },
                "code_string": "en"
            },
            "territory": {
                "_type": "CODE_PHRASE",
                "terminology_id": {
                    "_type": "TERMINOLOGY_ID",
                    "value": "ISO_3166-1"
                },
                "code_string": "US"
            },
            "category": {
                "_type": "DV_CODED_TEXT",
                "value": "event",
                "defining_code": {
                    "_type": "CODE_PHRASE",
                    "terminology_id": {
                        "_type": "TERMINOLOGY_ID",
                        "value": "openehr"
                    },
                    "code_string": "433"
                }
            },
            "composer": {
                "_type": "PARTY_IDENTIFIED",
                "name": "Dr. John Doe"
            },
            "context": {
                "_type": "EVENT_CONTEXT",
                "start_time": {
                    "_type": "DV_DATE_TIME",
                    "value": "2022-02-03T04:05:06"
                },
                "setting": {
                    "_type": "DV_CODED_TEXT",
                    "value": "primary care",
                    "defining_code": {
                        "_type": "CODE_PHRASE",
                        "terminology_id": {
                            "_type": "TERMINOLOGY_ID",
                            "value": "openehr"
                        },
                        "code_string": "238"
                    }
                }
            },
            "content": [
                {
                    "_type": "SECTION",
                    "name": {
                        "_type": "DV_TEXT",
                        "value": "Conformance section"
                    },
                    "archetype_details": {
                        "archetype_id": {
                            "value": "openEHR-EHR-SECTION.conformance_section.v0"
                        },
                        "rm_version": "1.0.4"
                    },
                    "items": [
                        {
                            "_type": "OBSERVATION",
                            "name": {
                                "_type": "DV_TEXT",
                                "value": "Blood pressure"
                            },
                            "archetype_details": {
                                "archetype_id": {
                                    "value": "openEHR-EHR-OBSERVATION.blood_pressure.v2"
                                },
                                "rm_version": "1.0.4"
                            },
                            "language": {
                                "_type": "CODE_PHRASE",
                                "terminology_id": {
                                    "_type": "TERMINOLOGY_ID",
                                    "value": "ISO_639-1"
                                },
                                "code_string": "en"
                            },
                            "encoding": {
                                "_type": "CODE_PHRASE",
                                "terminology_id": {
                                    "_type": "TERMINOLOGY_ID",
                                    "value": "IANA_character-sets"
                                },
                                "code_string": "UTF-8"
                            },
                            "subject": {
                                "_type": "PARTY_SELF"
                            },
                            "data": {
                                "name": {
                                    "_type": "DV_TEXT",
                                    "value": "History"
                                },
                                "origin": {
                                    "_type": "DV_DATE_TIME",
                                    "value": "2022-02-03T04:05:06"
                                },
                                "events": [
                                    {
                                        "_type": "POINT_EVENT",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Any event"
                                        },
                                        "time": {
                                            "_type": "DV_DATE_TIME",
                                            "value": "2022-02-03T04:05:06"
                                        },
                                        "state": {
                                            "_type": "ITEM_TREE",
                                            "name": {
                                                "_type": "DV_TEXT",
                                                "value": "state structure"
                                            },
                                            "items": [
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Position"
                                                    },
                                                    "value": {
                                                        "_type": "DV_CODED_TEXT",
                                                        "value": "Standing",
                                                        "defining_code": {
                                                            "_type": "CODE_PHRASE",
                                                            "terminology_id": {
                                                                "_type": "TERMINOLOGY_ID",
                                                                "value": "local"
                                                            },
                                                            "code_string": "at1000"
                                                        }
                                                    },
                                                    "archetype_node_id": "at0008"
                                                },
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Confounding factors"
                                                    },
                                                    "value": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Lorem ipsum"
                                                    },
                                                    "archetype_node_id": "at1052"
                                                },
                                                {
                                                    "_type": "CLUSTER",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "conformance cluster"
                                                    },
                                                    "archetype_details": {
                                                        "archetype_id": {
                                                            "value": "openEHR-EHR-CLUSTER.conformance_cluster.v0"
                                                        },
                                                        "rm_version": "1.0.4"
                                                    },
                                                    "items": [
                                                        {
                                                            "_type": "ELEMENT",
                                                            "name": {
                                                                "_type": "DV_TEXT",
                                                                "value": "labresult"
                                                            },
                                                            "value": {
                                                                "_type": "DV_TEXT",
                                                                "value": "Lorem ipsum"
                                                            },
                                                            "archetype_node_id": "at0003"
                                                        },
                                                        {
                                                            "_type": "ELEMENT",
                                                            "name": {
                                                                "_type": "DV_TEXT",
                                                                "value": "comment"
                                                            },
                                                            "value": {
                                                                "_type": "DV_TEXT",
                                                                "value": "Lorem ipsum"
                                                            },
                                                            "archetype_node_id": "at0004"
                                                        },
                                                        {
                                                            "_type": "ELEMENT",
                                                            "name": {
                                                                "_type": "DV_TEXT",
                                                                "value": "ANY"
                                                            },
                                                            "value": {
                                                                "_type": "DV_TEXT",
                                                                "value": "Lorem ipsum"
                                                            },
                                                            "archetype_node_id": "at0005"
                                                        }
                                                    ],
                                                    "archetype_node_id": "openEHR-EHR-CLUSTER.conformance_cluster.v0"
                                                },
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Sleep status"
                                                    },
                                                    "value": {
                                                        "_type": "DV_CODED_TEXT",
                                                        "value": "Awake",
                                                        "defining_code": {
                                                            "_type": "CODE_PHRASE",
                                                            "terminology_id": {
                                                                "_type": "TERMINOLOGY_ID",
                                                                "value": "local"
                                                            },
                                                            "code_string": "at1044"
                                                        }
                                                    },
                                                    "archetype_node_id": "at1043"
                                                },
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Tilt"
                                                    },
                                                    "value": {
                                                        "_type": "DV_QUANTITY",
                                                        "units": "deg",
                                                        "magnitude": 0.0
                                                    },
                                                    "archetype_node_id": "at1005"
                                                }
                                            ],
                                            "archetype_node_id": "at0007"
                                        },
                                        "data": {
                                            "_type": "ITEM_TREE",
                                            "name": {
                                                "_type": "DV_TEXT",
                                                "value": "blood pressure"
                                            },
                                            "items": [
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Systolic"
                                                    },
                                                    "value": {
                                                        "_type": "DV_QUANTITY",
                                                        "units": "mm[Hg]",
                                                        "magnitude": 500.0
                                                    },
                                                    "archetype_node_id": "at0004"
                                                },
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Diastolic"
                                                    },
                                                    "value": {
                                                        "_type": "DV_QUANTITY",
                                                        "units": "mm[Hg]",
                                                        "magnitude": 500.0
                                                    },
                                                    "archetype_node_id": "at0005"
                                                },
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "value": "Mean arterial pressure"
                                                    },
                                                    "value": {
                                                        "_type": "DV_QUANTITY",
                                                        "units": "mm[Hg]",
                                                        "magnitude": 500.0
                                                    },
                                                    "archetype_node_id": "at1006"
                                                },
                                                {
                                                    "_type": "ELEMENT",
                                                    "name": {
                                                        "_type": "DV_TEXT",
                                                        "
                                                    }
                                                }
                                        }
                                 
                                   ]   }
                            }
                        }
                }
        })

         @unittest.expectedFailure
        def test_cleanup(self):
        cleaned = CompositionCleanup.cleanup(self.COMP, False, True)
        assert_that(cleaned).contains(
            "\"template_id\" : \"aql-conformance-ehrbase.org.v0\"",
            "\"items\" : [ \"ELEMENT[at0004,'DV_TEXT']\" ]"
        )
        print(cleaned)

if __name__ == '__main__':
    unittest.main()
    