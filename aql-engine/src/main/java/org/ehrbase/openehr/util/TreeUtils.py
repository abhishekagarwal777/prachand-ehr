import re
from typing import Callable, TypeVar, List, Optional, Union
from functools import total_ordering

T = TypeVar('T', bound='TreeNode')

class TreeUtils:
    
    @staticmethod
    def render_tree(root: T, child_order: Optional[Callable[[T, T], int]], node_renderer: Callable[[T], str]) -> str:
        sb = []
        TreeUtils._render_tree_node(root, sb, 0, child_order, node_renderer)
        return ''.join(sb)

    @staticmethod
    def _render_tree_node(node: T, sb: List[str], level: int, child_order: Optional[Callable[[T, T], int]], node_renderer: Callable[[T], str]) -> None:
        if sb:
            sb.append("\n")
        sb.append("  " * level)
        node_str = node_renderer(node)
        if not node_str.strip():
            raise ValueError("Rendered node must not be blank")
        if re.match(r'^\s', node_str):
            raise ValueError("Rendered node must not start with whitespace")
        if re.search(r'\R', node_str):
            raise ValueError("Rendered node must not contain line breaks")
        sb.append(node_str)
        
        children = sorted(node.get_children(), key=child_order) if child_order else node.get_children()
        for child in children:
            TreeUtils._render_tree_node(child, sb, level + 1, child_order, node_renderer)

    @staticmethod
    def parse_tree(tree_graph: str, node_parser: Callable[[str], T]) -> T:
        pattern = re.compile(r'((?:  )*)(.+)')
        lines = tree_graph.splitlines()
        it = (pattern.match(line) for line in lines)
        
        def get_match(m):
            if not m:
                raise ValueError(f"Illegal line: {line}")
            return m.group(1).count('  '), m.group(2)

        it = (get_match(m) for m in it)
        
        root_level, root_data = next(it)
        if root_level != 0:
            raise ValueError(f"Only one root allowed: {root_data}")
        root = node_parser(root_data)

        last_node = root
        last_level = 0

        for level, data in it:
            if level <= 0:
                raise ValueError(f"Only one root allowed: {data}")
            parent_level = level - 1
            if parent_level > last_level:
                raise ValueError(f"Inconsistent level of {data}: {level} >> {last_level}")

            parent = last_node
            for _ in range(last_level, parent_level, -1):
                parent = parent.parent

            last_node = parent.add_child(node_parser(data))
            last_level = level

        return root
