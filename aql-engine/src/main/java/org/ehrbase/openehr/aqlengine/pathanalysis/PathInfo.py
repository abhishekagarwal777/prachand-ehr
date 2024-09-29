from typing import List, Dict, Set, Tuple, Optional, Union, Iterable
from dataclasses import dataclass, field
from enum import Enum, auto
import itertools

# Enums
class JoinMode(Enum):
    ROOT = auto()
    DATA = auto()
    INTERNAL_SINGLE_CHILD = auto()
    INTERNAL_FORK = auto()

class NodeCategory(Enum):
    STRUCTURE = auto()
    STRUCTURE_INTERMEDIATE = auto()
    RM_TYPE = auto()
    FOUNDATION = auto()
    FOUNDATION_EXTENDED = auto()

@dataclass
class NodeInfo:
    category: NodeCategory
    rm_types: Set[str]
    path_from_root: List[str]
    multiple_valued: bool
    dv_ordered_types: Set[str]

@dataclass
class PathNode:
    attribute: str

@dataclass
class PathCohesionTreeNode:
    paths: List['IdentifiedPath']
    children: List['PathCohesionTreeNode']
    is_root: bool
    # Assuming this method exists
    def get_paths_ending_at_node(self) -> List['IdentifiedPath']:
        pass

@dataclass
class IdentifiedPath:
    path: 'AqlObjectPath'
    root: 'AbstractContainmentExpression'
    root_predicate: Optional[str]
    # Assuming this method exists
    def render(self) -> str:
        pass

@dataclass
class AbstractContainmentExpression:
    type: str

@dataclass
class AqlObjectPath:
    path_nodes: List[PathNode]

    def get_path_nodes(self) -> List[PathNode]:
        return self.path_nodes

@dataclass
class PathInfo:
    cohesion_tree_root: PathCohesionTreeNode
    path_to_query_clause: Dict[IdentifiedPath, Set[str]]

    DV_ORDERED_TYPES: Set[str] = field(default_factory=set)

    def __post_init__(self):
        self.path_attribute_info = self._initialize_path_attribute_info()
        self.node_type_info = self._fill_node_type_info(self.cohesion_tree_root, -1, {})
        
    def _initialize_path_attribute_info(self) -> Dict[IdentifiedPath, Tuple['ANode', Dict['ANode', Dict[str, 'AttInfo']]]]:
        path_attribute_info = {}
        for ip in self.cohesion_tree_root.paths:
            root = ip.root
            analyzed = PathAnalysis.analyze_aql_path_types(
                root.type if isinstance(root, ContainmentClassExpression) else RmConstants.ORIGINAL_VERSION,
                ip.root_predicate,
                root.predicates,
                ip.path,
                None
            )
            if not analyzed.get_candidate_types():
                raise ValueError(f"Path {ip.render()} is not valid")
            path_attribute_info[ip] = (analyzed, PathAnalysis.create_attribute_infos(analyzed))
        return path_attribute_info

    def _fill_node_type_info(self, current_node: PathCohesionTreeNode, level: int, node_type_info: Dict[PathCohesionTreeNode, NodeInfo]) -> Dict[PathCohesionTreeNode, NodeInfo]:
        node_info = self._node_type_info_for_path_at_level(current_node.paths[0], level)
        node_type_info[current_node] = node_info
        for child in current_node.children:
            self._fill_node_type_info(child, level + 1, node_type_info)
        return node_type_info

    def _node_type_info_for_path_at_level(self, ip: IdentifiedPath, level: int) -> NodeInfo:
        a_node, attribute_infos = self.path_attribute_info[ip]
        path_nodes = ip.path.get_path_nodes()
        attribute = None
        att_info = None
        for i in range(level + 1):
            attribute = path_nodes[i].attribute
            att_info = attribute_infos.get(a_node, {}).get(attribute)
            a_node = a_node.get_attribute(attribute)
        
        node_category = reduce(NodeInfo.merge_node_categories, a_node.get_categories(), None)
        if node_category is None:
            raise ValueError("Cannot determine node category")
        
        return NodeInfo(
            category=node_category,
            rm_types=att_info.target_types if att_info else a_node.get_candidate_types(),
            path_from_root=[] if level < 0 else path_nodes[:level + 1],
            multiple_valued=att_info.multiple_valued if att_info else False,
            dv_ordered_types=att_info.target_types.intersection(self.DV_ORDERED_TYPES) if att_info else set()
        )

    @staticmethod
    def merge_node_categories(a: NodeCategory, b: NodeCategory) -> NodeCategory:
        if a == b:
            return a
        
        c0, c1 = (a, b) if a.value < b.value else (b, a)
        
        if c0 in [NodeCategory.STRUCTURE, NodeCategory.STRUCTURE_INTERMEDIATE]:
            raise ValueError(f"Incompatible node types: {a}, {b}")
        if c0 in [NodeCategory.RM_TYPE, NodeCategory.FOUNDATION]:
            return NodeCategory.FOUNDATION_EXTENDED
        raise ValueError(f"Inconsistent node types: {a}, {b}")

    @staticmethod
    def create_path_infos(aql_query: 'AqlQuery', contains_descs: Dict['AbstractContainmentExpression', 'ContainsWrapper']) -> Dict['ContainsWrapper', 'PathInfo']:
        path_cohesion = PathCohesionAnalysis.analyze_path_cohesion(aql_query)
        
        path_to_query_clause = {}
        for path, clause in itertools.chain(
            ((p, 'SELECT') for p in aql_query.select.statements if isinstance(p, IdentifiedPath)),
            ((p, 'WHERE') for p in stream_where_conditions(aql_query.where) if isinstance(p, IdentifiedPath)),
            ((p, 'ORDER_BY') for p in aql_query.order_by.statements if isinstance(p, IdentifiedPath))
        ):
            if path not in path_to_query_clause:
                path_to_query_clause[path] = set()
            path_to_query_clause[path].add(clause)
        
        return {
            contains_descs.get(key): PathInfo(path_cohesion[key], path_to_query_clause)
            for key in contains_descs
            if key in path_cohesion and not (isinstance(key, ContainmentClassExpression) and key.type == RmConstants.EHR)
        }

    def get_node_category(self, node: PathCohesionTreeNode) -> NodeCategory:
        return self.node_type_info.get(node).category
    
    def get_target_types(self, node: PathCohesionTreeNode) -> Set[str]:
        return self.node_type_info.get(node).rm_types

    def get_dv_ordered_types(self, node: PathCohesionTreeNode) -> Set[str]:
        return self.node_type_info.get(node).dv_ordered_types

    def is_used_in_select(self, node: PathCohesionTreeNode) -> bool:
        return any(
            clause == 'SELECT'
            for path in node.get_paths_ending_at_node()
            if (query_clauses := self.path_to_query_clause.get(path)) is not None
            for clause in query_clauses
        )

    def is_used_in_where_or_order_by(self, node: PathCohesionTreeNode) -> bool:
        return any(
            clause in ['WHERE', 'ORDER_BY']
            for path in node.get_paths_ending_at_node()
            if (query_clauses := self.path_to_query_clause.get(path)) is not None
            for clause in query_clauses
        )

    def is_multiple_valued(self, node: PathCohesionTreeNode) -> bool:
        info = self.node_type_info.get(node)
        return not 'BYTE' in info.rm_types and info.multiple_valued

    def get_path_to_node(self, node: PathCohesionTreeNode) -> List[PathNode]:
        return self.node_type_info.get(node).path_from_root

    def join_mode(self, node: PathCohesionTreeNode) -> JoinMode:
        if node.is_root:
            return JoinMode.ROOT
        
        has_data = any(
            self.get_node_category(child) in [NodeCategory.RM_TYPE, NodeCategory.FOUNDATION, NodeCategory.FOUNDATION_EXTENDED]
            for child in node.children
        ) or node.get_paths_ending_at_node()
        
        if has_data:
            return JoinMode.DATA
        
        structure_child_count = sum(
            1 for child in node.children
            if self.get_node_category(child) not in [NodeCategory.RM_TYPE, NodeCategory.FOUNDATION, NodeCategory.FOUNDATION_EXTENDED]
        )
        
        if structure_child_count == 0:
            raise ValueError(f"Internal node without children: {node}")
        if structure_child_count == 1:
            return JoinMode.INTERNAL_SINGLE_CHILD
        return JoinMode.INTERNAL_FORK
