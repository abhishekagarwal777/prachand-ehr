from typing import Set, List, Dict, Optional, Union
from collections import defaultdict

class StructureRmType:
    @staticmethod
    def by_type_name(type_name: str) -> Optional['StructureRmType']:
        pass

    def is_structure_entry(self) -> bool:
        pass

class FoundationType:
    @staticmethod
    def by_type_name(type_name: str) -> Optional['FoundationType']:
        pass

class StringPrimitive:
    def get_value(self) -> str:
        pass

class AndOperatorPredicate:
    def get_operands(self) -> List['ComparisonOperatorPredicate']:
        pass

class ComparisonOperatorPredicate:
    class PredicateComparisonOperator:
        EQ = 'EQ'
        NEQ = 'NEQ'
        MATCHES = 'MATCHES'

    def get_operator(self) -> str:
        pass

    def get_path(self) -> str:
        pass

    def get_value(self) -> 'StringPrimitive':
        pass

class AqlObjectPathUtil:
    ARCHETYPE_NODE_ID = '/archetype_node_id'

class PathAnalysis:
    @staticmethod
    def resolve_concrete_type_names(type_name: str) -> Set[str]:
        pass

    @staticmethod
    def append_path(node: 'ANode', path: str, types: Set[str]):
        pass

    @staticmethod
    def rm_type_from_archetype(archetype_node_id: str) -> Optional[Set[str]]:
        pass

class ANode:
    class NodeCategory:
        STRUCTURE = 'STRUCTURE'
        STRUCTURE_INTERMEDIATE = 'STRUCTURE_INTERMEDIATE'
        RM_TYPE = 'RM_TYPE'
        FOUNDATION = 'FOUNDATION'
        FOUNDATION_EXTENDED = 'FOUNDATION_EXTENDED'

    def __init__(self, rm_type: Optional[str], parent_predicates: List[AndOperatorPredicate], predicates: List[AndOperatorPredicate]):
        if rm_type is None:
            self.candidate_types = None
        else:
            self.candidate_types = {type_name for type_name in PathAnalysis.resolve_concrete_type_names(rm_type)}

        self.attributes: Dict[str, 'ANode'] = {}
        self.constrain_by_archetype(parent_predicates)
        self.constrain_by_archetype(predicates)
        self.add_predicate_constraints(parent_predicates)
        self.add_predicate_constraints(predicates)

    def get_categories(self) -> Set[NodeCategory]:
        if self.candidate_types is None:
            raise Exception("The candidate types have not been calculated")

        result = set()
        for type_name in self.candidate_types:
            result.add(self.get_category(type_name))
        return result

    @staticmethod
    def get_category(type_name: str) -> NodeCategory:
        structure_type = StructureRmType.by_type_name(type_name)
        if structure_type is not None:
            return NodeCategory.STRUCTURE if structure_type.is_structure_entry() else NodeCategory.STRUCTURE_INTERMEDIATE

        foundation_type = FoundationType.by_type_name(type_name)
        if foundation_type is not None:
            return NodeCategory.FOUNDATION

        return NodeCategory.RM_TYPE

    def get_attribute(self, attribute: str) -> Optional['ANode']:
        return self.attributes.get(attribute)

    def get_candidate_types(self) -> Set[str]:
        return set(self.candidate_types)

    def add_predicate_constraints(self, predicates: List[AndOperatorPredicate]):
        if predicates and len(predicates) == 1:
            operands = predicates[0].get_operands()
            for predicate in operands:
                if predicate.get_operator() not in {ComparisonOperatorPredicate.PredicateComparisonOperator.NEQ, ComparisonOperatorPredicate.PredicateComparisonOperator.MATCHES}:
                    PathAnalysis.append_path(self, predicate.get_path(), PathAnalysis.resolve_concrete_type_names(predicate.get_value().get_value()))

    def constrain_by_archetype(self, predicates: List[AndOperatorPredicate]):
        self.candidate_types = self.constrain_by_archetype(self.candidate_types, predicates)

    @staticmethod
    def constrain_by_archetype(candidate_types: Optional[Set[str]], predicates: List[AndOperatorPredicate]) -> Set[str]:
        if not predicates or (candidate_types and not candidate_types):
            return candidate_types or set()

        if len(predicates) == 1:
            return ANode.constrain_by_archetype(candidate_types, predicates[0])

        constraint_union = set()
        for predicate in predicates:
            candidate_set = candidate_types.copy() if candidate_types else set()
            candidate_set = ANode.constrain_by_archetype(candidate_set, predicate)

            if candidate_set:
                constraint_union.update(candidate_set)

        if candidate_types is None:
            return constraint_union
        else:
            candidate_types.intersection_update(constraint_union)
            return candidate_types

    @staticmethod
    def constrain_by_archetype(candidate_types: Optional[Set[str]], predicates: AndOperatorPredicate) -> Set[str]:
        constrained = candidate_types or set()
        for predicate in predicates.get_operands():
            archetype_node_id = ANode.get_archetype_node_id(predicate)
            if archetype_node_id:
                constrained = ANode.constrain_by_archetype(constrained, archetype_node_id)
        return constrained

    @staticmethod
    def get_archetype_node_id(predicate: ComparisonOperatorPredicate) -> Optional[str]:
        if (predicate.get_operator() == ComparisonOperatorPredicate.PredicateComparisonOperator.EQ and
            predicate.get_path() == AqlObjectPathUtil.ARCHETYPE_NODE_ID and
            isinstance(predicate.get_value(), StringPrimitive)):
            return predicate.get_value().get_value()
        return None

    @staticmethod
    def constrain_by_archetype(candidate_types: Set[str], archetype_node_id: str) -> Set[str]:
        return PathAnalysis.rm_type_from_archetype(archetype_node_id) or candidate_types
