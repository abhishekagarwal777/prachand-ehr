import pytest

class TreeNode:
    def __init__(self, id):
        self.id = id
        self.children = []

    def add_child(self, node):
        if node is self:
            raise ValueError("Cannot add node as a child of itself")
        self.children.append(node)
        return node

    @staticmethod
    def root(id):
        return TreeNode(id)

def parse_tree(tree_graph):
    lines = tree_graph.strip().split('\n')
    nodes = {}
    for line in lines:
        depth = len(line) - len(line.lstrip())
        id = int(line.strip())
        if depth == 0:
            node = TreeNode.root(id)
            nodes[id] = node
        else:
            parent_id = int(lines[depth - 1].strip())
            parent_node = nodes[parent_id]
            node = TreeNode(id)
            parent_node.add_child(node)
            nodes[id] = node
    return nodes[0]  # Root node

def render_tree(node, depth=0):
    result = " " * depth + str(node.id) + "\n"
    for child in node.children:
        result += render_tree(child, depth + 2)
    return result

def test_simple_tree():
    root = TreeNode.root(0)
    n1 = root.add_child(TreeNode(1))
    n11 = n1.add_child(TreeNode(11))
    n12 = n1.add_child(TreeNode(12))
    n123 = n12.add_child(TreeNode(123))
    n13 = n1.add_child(TreeNode(13))
    n2 = root.add_child(TreeNode(2))
    n3 = root.add_child(TreeNode(3))
    n3_1 = n3.add_child(TreeNode(31))

    expected = (
        "0\n"
        "  1\n"
        "    11\n"
        "    12\n"
        "      123\n"
        "    13\n"
        "  2\n"
        "  3\n"
        "    31\n"
    )
    assert render_tree(root) == expected

def test_move_child():
    tree = (
        "0\n"
        "  1\n"
        "    11\n"
        "    12\n"
        "      123\n"
        "    13\n"
        "  2\n"
        "  3\n"
        "    31\n"
    )
    root = parse_tree(tree)

    n1 = root.children[0]
    n12 = n1.children[1]
    n3 = root.children[2]

    with pytest.raises(ValueError):
        n12.add_child(root)  # Cannot add root as a child of n12

    n3.add_child(n12)

    expected = (
        "0\n"
        "  1\n"
        "    11\n"
        "    13\n"
        "  2\n"
        "  3\n"
        "    31\n"
        "    12\n"
        "      123\n"
    )
    assert render_tree(root) == expected

def test_create_tree():
    tree = (
        "0\n"
        "  1\n"
        "    11\n"
        "    12\n"
        "      123\n"
        "    13\n"
        "  2\n"
        "  3\n"
        "    31\n"
    )
    assert render_tree(parse_tree(tree)) == tree
