from collections import defaultdict, deque
from typing import List, Dict, Set, Optional, Tuple, Union
import re

class AttInfo:
    def __init__(self, multiple_valued: bool, nullable: bool, target_types: Set[str]):
        self.multiple_valued = multiple_valued
        self.nullable = nullable
        self.target_types = target_types

class AttributeInfos:
    rm_types: Set[str] = set()
    base_types_by_attribute: Dict[str, Set[str]] = {}
    typed_attributes: Dict[str, Dict[str, Set[str]]] = {}
    attribute_infos: Dict[str, Dict[str, AttInfo]] = {}

    @classmethod
    def initialize(cls):
        # Simulate the initialization logic
        cls.rm_types = {"EHR", "COMPOSITION", "EHR_STATUS", "ORIGINAL_VERSION"}
        cls.base_types_by_attribute = defaultdict(set)
        cls.typed_attributes = defaultdict(lambda: defaultdict(set))
        cls.attribute_infos = defaultdict(lambda: defaultdict(lambda: AttInfo(False, False, set())))

        cls.add_ehr_attributes()

    @classmethod
    def add_ehr_attributes(cls):
        base_type = "EHR"
        cls.rm_types.add(base_type)

        cls.add_attribute("ehrId", base_type, {"HIER_OBJECT_ID"})
        cls.add_attribute("timeCreated", base_type, {"DV_DATE_TIME"})
        cls.add_attribute("ehrStatus", base_type, {"EHR_STATUS"})
        cls.add_attribute("compositions", base_type, {"COMPOSITION"})

    @classmethod
    def add_attribute(cls, attribute: str, base_type: str, target_types: Set[str]):
        cls.base_types_by_attribute[attribute].add(base_type)
        cls.typed_attributes[attribute][base_type].update(target_types)
        cls.attribute_infos[attribute][base_type] = AttInfo(False, False, target_types)

class PathAnalysis:
    @staticmethod
    def validate_attribute_names_exist(root_node):
        for node in PathAnalysis.iterate_nodes(root_node):
            for att in node.attributes.keys():
                if att not in AttributeInfos.attribute_infos:
                    raise ValueError(f"Unknown attribute: {att}")

    @staticmethod
    def iterate_nodes(root_node):
        stack = deque([root_node])
        while stack:
            node = stack.popleft()
            yield node
            stack.extend(node.attributes.values())

    @staticmethod
    def analyze_aql_path_types(root_type: str, variable_predicates: List, root_predicates: List, path, candidate_types: Set[str]):
        root_node = ANode(root_type, variable_predicates, root_predicates)
        PathAnalysis.append_path(root_node, path, candidate_types)
        PathAnalysis.validate_attribute_names_exist(root_node)

        while PathAnalysis.apply_child_attribute_constraints(root_node):
            pass
        return root_node

    @staticmethod
    def apply_child_attribute_constraints(node):
        if not node.attributes or (node.candidate_types is not None and not node.candidate_types):
            return False
        
        changed = False
        for att_name, child_node in node.attributes.items():
            changed |= PathAnalysis.apply_attribute_constraints(node, att_name, child_node)
            changed |= PathAnalysis.apply_child_attribute_constraints(child_node)
        return changed

    @staticmethod
    def apply_attribute_constraints(parent_node, att_name, child_node):
        type_constellations = AttributeInfos.typed_attributes.get(att_name)
        if type_constellations is None:
            parent_node.candidate_types = set()
            child_node.candidate_types = set()
            return True

        if parent_node.candidate_types is None:
            if child_node.candidate_types is None:
                parent_node.candidate_types = set(type_constellations.keys())
                child_node.candidate_types = set.union(*type_constellations.values())
            else:
                child_constraints = set.union(*type_constellations.values())
                child_node.candidate_types.intersection_update(child_constraints)
                parent_node.candidate_types = {k for k in type_constellations if any(t in child_node.candidate_types for t in type_constellations[k])}
            return True

        changed = parent_node.candidate_types.copy()
        parent_node.candidate_types.intersection_update(type_constellations.keys())
        child_constraints = set.union(*[type_constellations[k] for k in parent_node.candidate_types])
        if child_node.candidate_types is None:
            child_node.candidate_types = child_constraints
            changed = True
        else:
            changed |= child_node.candidate_types.intersection_update(child_constraints)
        return changed

    @staticmethod
    def append_path(root, path, candidate_types):
        if path is None:
            return
        for node in path.get_path_nodes():
            root = PathAnalysis.add_attributes(root, node)
        if candidate_types is not None:
            if root.candidate_types is None:
                root.candidate_types = set(candidate_types)
            else:
                root.candidate_types.intersection_update(candidate_types)

    @staticmethod
    def add_attributes(root, child):
        att_name = child.get_attribute()
        child_node = root.attributes.get(att_name)

        if child_node is None:
            child_node = ANode(None, None, child.get_predicate_or_operands())
            root.attributes[att_name] = child_node
        else:
            child_node.constrain_by_archetype(child.get_predicate_or_operands())
            child_node.add_predicate_constraints(child.get_predicate_or_operands())

        return child_node

class ANode:
    def __init__(self, type_name: str, variable_predicates: List, root_predicates: List):
        self.type_name = type_name
        self.variable_predicates = variable_predicates
        self.root_predicates = root_predicates
        self.attributes = {}
        self.candidate_types = None

    def constrain_by_archetype(self, predicates):
        # Implement logic as needed
        pass

    def add_predicate_constraints(self, predicates):
        # Implement logic as needed
        pass

# Initialize attribute information
AttributeInfos.initialize()
