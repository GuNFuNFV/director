
class TreeNode:
    def __init__(self, name):
        self.name = name
        self.value_dict = {}
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def find_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def __str__(self):
        return f"{self.name} ({self.value_dict})"


class Tree:
    def __init__(self, data):
        self.root = TreeNode("root")
        self.build_tree(data, self.root)

    def is_dict(self, data):
        if isinstance(data, dict):
            return True
        return False

    def build_tree(self, data, parent=None):
        for node_name, node_data in data.items():
            if self.is_dict(node_data):
                node = TreeNode(node_name)
                self.build_tree(node_data, node)
                parent.add_child(node)
            else:
                parent.value_dict[node_name] = (node_data)

    def dump_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print(" " * level + str(node))
        for child in node.children:
            self.dump_tree(child, level + 1)


class tree_path():
    def __init__(self):
        self.node_list = []

    def add_node(self, node: TreeNode):
        self.node_list.insert(0, node)

    def __str__(self):
        result = ""
        for node in self.node_list:
            result += node.name + "/"
        return result

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, tree_path):
            return self.__str__() == other.__str__()
        return False