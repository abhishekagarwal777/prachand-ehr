from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from collections import defaultdict

class PathNode(BaseModel):
    attribute: str
    predicates: Optional[List[dict]] = None

    def __init__(self, attribute: str, predicates: Optional[List[dict]] = None):
        super().__init__(attribute=attribute, predicates=predicates or [])

class AttributeType:
    BASE = 'BASE'
    ARCHETYPE = 'ARCHETYPE'
    NODE = 'NODE'
    NAME = 'NAME'

    @staticmethod
    def cleanup_predicates(predicates: List[dict], attribute_type: str) -> List[dict]:
        cleaned = []
        for predicate in predicates:
            if attribute_type == AttributeType.NODE:
                if predicate.get('path') == 'ARCHETYPE_NODE_ID' and predicate.get('value', '').startswith('openEHR-'):
                    continue
            cleaned.append(predicate)
        return sorted(cleaned, key=lambda p: (p.get('path'), p.get('value')))

    @staticmethod
    def get_attribute_type(predicates: List[dict]) -> str:
        for predicate in predicates:
            if predicate.get('path') == 'NAME_VALUE':
                return AttributeType.NAME
            if predicate.get('path') == 'ARCHETYPE_NODE_ID':
                value = predicate.get('value')
                if value and value.startswith('openEHR-'):
                    return AttributeType.ARCHETYPE
                return AttributeType.NODE
        return AttributeType.BASE

class PathCohesionTreeNode(BaseModel):
    attribute: PathNode
    paths: List[dict]
    paths_ending_at_node: List[dict]
    root: bool

    @classmethod
    def root(cls, attribute: PathNode, paths: List[dict]) -> 'PathCohesionTreeNode':
        return cls(attribute=attribute, paths=paths, paths_ending_at_node=paths.copy(), root=True)

    def add_child(self, attribute: PathNode, paths: List[dict]) -> 'PathCohesionTreeNode':
        self.paths_ending_at_node = [path for path in self.paths_ending_at_node if path not in paths]
        child = PathCohesionTreeNode(attribute=attribute, paths=paths, paths_ending_at_node=paths)
        return self._add_child(child)

    def _add_child(self, child: 'PathCohesionTreeNode') -> 'PathCohesionTreeNode':
        return child

def analyze_path_cohesion(query: dict) -> Dict[str, PathCohesionTreeNode]:
    roots = defaultdict(list)

    for path in query.get('paths', []):
        root = path['root']
        roots[root].append(path)

    result = {}
    for root, paths in roots.items():
        root_node = create_root_node(root)
        join_tree = PathCohesionTreeNode.root(root_node, paths)
        fill_join_tree(join_tree, 0)
        result[root] = join_tree

    return result

def create_root_node(root: dict) -> PathNode:
    root_type = root.get('type')
    root_predicates = root.get('predicates', [])
    attribute_type = AttributeType.get_attribute_type(root_predicates)
    cleaned_predicates = AttributeType.cleanup_predicates(root_predicates, attribute_type)
    return PathNode(attribute=root_type, predicates=cleaned_predicates)

def fill_join_tree(node: PathCohesionTreeNode, level: int):
    base_attributes = defaultdict(list)

    for path in node.paths:
        path_nodes = path['path_nodes']
        if len(path_nodes) > level:
            base_attributes[path_nodes[level]['attribute']].append(path)

    for attribute, paths in base_attributes.items():
        attribute_type = AttributeType.get_attribute_type([p['path_nodes'][level] for p in paths])
        if attribute_type == AttributeType.BASE:
            node.add_child(PathNode(attribute), paths)
        else:
            grouped_paths = defaultdict(list)
            for path in paths:
                predicates = AttributeType.cleanup_predicates([path['path_nodes'][level]], attribute_type)
                grouped_paths[tuple(predicates)].append(path)
            for predicates, paths_group in grouped_paths.items():
                node.add_child(PathNode(attribute, predicates), paths_group)

    for child in node.children:
        fill_join_tree(child, level + 1)
