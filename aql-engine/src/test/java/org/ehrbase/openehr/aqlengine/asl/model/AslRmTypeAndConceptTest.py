import unittest

class AslRmTypeAndConcept:
    def __init__(self, rm_type: str, concept: str):
        self.rm_type = rm_type
        self.concept = concept

    @staticmethod
    def from_archetype_node_id(node_id: str):
        if node_id.startswith("openEHR-EHR-"):
            parts = node_id[len("openEHR-EHR-"):].split('.', 1)
            if len(parts) == 2:
                return AslRmTypeAndConcept(parts[0], '.' + parts[1])
            return AslRmTypeAndConcept(parts[0], '')
        return AslRmTypeAndConcept(None, node_id)

    @staticmethod
    def to_entity_concept(node_id: str):
        if node_id.startswith("openEHR-EHR-"):
            parts = node_id[len("openEHR-EHR-"):].split('.', 1)
            if len(parts) == 2:
                return '.' + parts[1]
            raise ValueError("Invalid archetype node ID")
        return node_id

    def __eq__(self, other):
        return isinstance(other, AslRmTypeAndConcept) and self.rm_type == other.rm_type and self.concept == other.concept

class TestAslRmTypeAndConcept(unittest.TestCase):
    
    def test_from_archetype_node_id(self):
        self.assertEqual(AslRmTypeAndConcept.from_archetype_node_id("openEHR-EHR-OBSERVATION.symptom_sign_screening.v0"),
                         AslRmTypeAndConcept("OB", ".symptom_sign_screening.v0"))
        self.assertEqual(AslRmTypeAndConcept.from_archetype_node_id("at123"), AslRmTypeAndConcept(None, "at123"))
        self.assertEqual(AslRmTypeAndConcept.from_archetype_node_id("id123"), AslRmTypeAndConcept(None, "id123"))
        with self.assertRaises(ValueError):
            AslRmTypeAndConcept.from_archetype_node_id("openEHR-EHR-OBSERVATION")
        with self.assertRaises(ValueError):
            AslRmTypeAndConcept.from_archetype_node_id("nr123")

    def test_to_entity_concept(self):
        self.assertEqual(AslRmTypeAndConcept.to_entity_concept("openEHR-EHR-OBSERVATION.symptom_sign_screening.v0"),
                         ".symptom_sign_screening.v0")
        self.assertEqual(AslRmTypeAndConcept.to_entity_concept("at123"), "at123")
        self.assertEqual(AslRmTypeAndConcept.to_entity_concept("id123"), "id123")
        with self.assertRaises(ValueError):
            AslRmTypeAndConcept.to_entity_concept("openEHR-EHR-OBSERVATION")
        with self.assertRaises(ValueError):
            AslRmTypeAndConcept.to_entity_concept("nr123")

if __name__ == '__main__':
    unittest.main()
